"""Port of sources/SM_fc696ed3ce4f57f8.pine (batch_001/MACD-5合1多指标趋势追踪策略Multi-timeframe-MACD-Trend-Following-Strategy.md).

Pine v4. One MACD and five independent long-only strategy blocks, each behind
its own on/off input. Only block #1 is enabled by default.

    macd_Fast = MACD_Line == "SMA" ? sma(macd_Source, 12) : ema(macd_Source, 12)
    macd_Slow = MACD_Line == "SMA" ? sma(macd_Source, 26) : ema(macd_Source, 26)
    MACD      = macd_Fast - macd_Slow
    Signal    = SignalLine == "SMA" ? sma(MACD, 9) : ema(MACD, 9)
    macd_crsovr = crossover(MACD, Signal)
    macd_crsndr = crossunder(MACD, Signal)

    #1  crsovr -> entry("BUY", long)          crsndr -> close("BUY")
    #2  crsovr and MACD < MACD_OB_LVL and Signal < MACD_OB_LVL -> entry
        crsndr                                               -> close("BUY")
    #3  crsovr and (close/close[1..3] vs MA_signal|dema|tema) -> entry
        crsndr and (the same, with the first term kept as `>`) -> close("BUY")
    #4  crsovr and (close/close[1..3] vs MA_zone_srcHi|dema2|tema2) -> entry
        crsndr and (the same, all `<`)                        -> close_all()
    #5  crsovr and RSI > 50 and RSI < 70 -> entry   crsndr and (P5) -> close("BUY")

Every order call in the file is reproduced, in source order, including the
`if (not inDateRange) strategy.close_all()` at the end. `inDateRange` is the
literal `true` (line 112) -- the `Start Time` / `End Time` inputs declared next
to it are never referenced by any condition, so that branch never fires.

`strategy("MACD [5-in-1]")` declares only a title, so Pine's documented
defaults apply: `fixed` / 1 unit, commission 0%, `pyramiding = 0`,
`initial_capital = 1000000`, `process_orders_on_close = false`.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own bar grid.
There is no short entry anywhere, so `can_short` is False.

FIDELITY:

* The md calls this a "Multi-timeframe MACD" strategy and says the MACD death
  cross is a short signal. Neither is in the source: there is no
  `request.security` (no second timeframe is read) and there is no
  `strategy.short` call -- a crossunder only ever CLOSES the long. The source is
  authoritative; both prose divergences are recorded, not applied.
* Block #3's sell condition reproduces the source's own asymmetry literally: its
  first term is `close > MA_signal` (not `<`), while every other term is `<`.
  Copying the line as written is the faithful choice; "fixing" it would change
  when block #3 closes.
* `matype_zone` / `matype_signal` return `na` for any type outside
  EMA/SMA/RMA/WMA/VWMA. `MA_signal_type` and `MA_zone_type` list DEMA and TEMA
  among their options, so selecting either makes the corresponding average `na`
  -- a source quirk, reproduced rather than repaired (dema/tema are computed
  separately and separately gated on exactly those two strings).
* `MA_zone_srcLO = matype_signal(low, ...)` is computed in the source and never
  used; it is not reproduced because it feeds no order call.
* `MACD_rsi_Ex` (the RSI 70 crossunder over 7 bars) is computed in the source
  and never used by any order call; likewise `MACD_rsi_EnSell`, `histogram`,
  the colour inputs and every `plot*`/`fill`/`hline`. Display or dead, and not
  reproduced.
* `quick`/`Signal` use only the binary EMA-vs-SMA choice the source wrote, not
  the wider `matype_zone`; the port follows the source's own expressions.
* `ema` seeding is a modelled choice (first non-na seed), see
  PINE_SEMANTICS.md §3.1.
* No stop/limit/trail exit exists, so `source_reproduce_stops` is False.
* Leverage, margin, liquidation, funding and contract-step rounding are not
  modelled (§二.4, §1.6).
"""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _matype(source, length, kind, volume):
    """matype_zone()/matype_signal(): the five named averages, else na."""
    if kind == "EMA":
        return ta.pine_ema(source, length)
    if kind == "SMA":
        return ta.pine_sma(source, length)
    if kind == "RMA":
        return ta.pine_rma(source, length)
    if kind == "WMA":
        return ta.pine_wma(source, length)
    if kind == "VWMA":
        weighted = source.copy()
        weighted.attrs["volume"] = volume
        return ta.pine_vwma(weighted, length)
    # `na` -- matype_zone's final else branch (DEMA / TEMA / anything else).
    return pd.Series(np.nan, index=source.index, dtype=float)


class SMMacd5In1TrendFollowing_fc696e(PinePortBase, IStrategy):
    source_id = "SM_fc696ed3ce4f57f8"
    source_file = (
        "MACD-5合1多指标趋势追踪策略Multi-timeframe-MACD-Trend-Following-Strategy.md"
    )
    timeframe = "1d"
    can_short = False
    # Every input() in the source, defaults verbatim. `startTime` / `endTime`
    # are declared (lines 109-110) but never referenced: `inDateRange` is the
    # literal `true`, so they are carried here for completeness only.
    source_defaults: dict = {
        "macd_FastLength": 12,
        "macd_SlowLength": 26,
        "macd_signalLen": 9,
        "macd_Source": "close",
        "MACD_Line": "EMA",
        "SignalLine": "EMA",
        "MACD_crs_signal": True,
        "MACD_OB": False,
        "MACD_OB_LVL": 0.0,
        "MACD_close": False,
        "MA_signal_len": 21,
        "MA_signal_type": "EMA",
        "MACD_ZONE": False,
        "MA_zone_len": 21,
        "MA_zone_type": "EMA",
        "MACD_wid_rsiOB": False,
        "rsilen": 14,
        "rsi_ent_value": 50,
        "rsi_ob_value": 70,
        "startTime": "2021-01-01T00:00:00+00:00",
        "endTime": "2022-01-01T00:00:00+00:00",
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source is single-timeframe: no request.security and no second "
        "period is read. The md's name/description ('Multi-timeframe MACD') is "
        "not supported by the code; recorded, not applied.",
        "No strategy.short call exists: a MACD crossunder only closes the long "
        "in every one of the five blocks. The md's 'death cross is a short "
        "signal' is not in the source.",
        "Block #3's sell line keeps the source's asymmetry: its first term is "
        "`close > MA_signal` while every other term is `<`.",
        "matype_zone/matype_signal return na for DEMA/TEMA even though both are "
        "listed among the inputs' options; reproduced as written.",
        "MA_zone_srcLO, MACD_rsi_Ex, MACD_rsi_EnSell, histogram, the colour "
        "inputs, plot/fill/hline/plotshape are computed or drawn but feed no "
        "order call; not reproduced.",
        "`inDateRange` is the literal true; the Start Time / End Time inputs "
        "are declared but never used by any condition. The trailing "
        "`if (not inDateRange) strategy.close_all()` therefore never fires "
        "(PINE_SEMANTICS.md §二.8 -- input.time does not crop the data).",
        "strategy() declares only a title: Pine defaults fixed / 1 unit, "
        "commission 0%, pyramiding 0, initial capital 1000000, "
        "process_orders_on_close=false.",
        "ema seeding is a modelled choice (first non-na seed), §3.1.",
        "No stop/limit/trail exit exists, so source_reproduce_stops is False.",
        "Leverage, margin, liquidation, funding and contract-step rounding are "
        "not modelled (§二.4, §1.6).",
    ]

    # `inDateRange = true` -- a literal in the source, not an input.
    IN_DATE_RANGE = True

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        volume = dataframe["volume"]
        macd_source = ta.pine_source(dataframe, params["macd_Source"])
        fast_len = int(params["macd_FastLength"])
        slow_len = int(params["macd_SlowLength"])
        signal_len = int(params["macd_signalLen"])
        macd_line_kind = params["MACD_Line"]
        signal_kind = params["SignalLine"]

        # macd_Fast = MACD_Line == "SMA" ? sma(...) : ema(...)  (same for slow)
        macd_fast = (
            ta.pine_sma(macd_source, fast_len)
            if macd_line_kind == "SMA"
            else ta.pine_ema(macd_source, fast_len)
        )
        macd_slow = (
            ta.pine_sma(macd_source, slow_len)
            if macd_line_kind == "SMA"
            else ta.pine_ema(macd_source, slow_len)
        )
        macd = macd_fast - macd_slow
        # Signal = SignalLine == "SMA" ? sma(MACD, n) : ema(MACD, n)
        signal = (
            ta.pine_sma(macd, signal_len)
            if signal_kind == "SMA"
            else ta.pine_ema(macd, signal_len)
        )
        macd_crsovr = ta.pine_crossover(macd, signal)
        macd_crsndr = ta.pine_crossunder(macd, signal)

        # Stgy #2: MACD + OverBought
        ob_level = float(params["MACD_OB_LVL"])
        only_trade_when = (macd < ob_level) & (signal < ob_level)
        macd_ob_buy = macd_crsovr & only_trade_when
        macd_ob_sell = macd_crsndr

        # Stgy #3: MACD + Close. MA_signal via matype_zone; dema/tema are na
        # unless the corresponding type string is selected.
        ma_signal_len = int(params["MA_signal_len"])
        ma_signal_type = params["MA_signal_type"]
        ma_signal = _matype(close, ma_signal_len, ma_signal_type, volume)
        dema = _dema(close, ma_signal_len) if ma_signal_type == "DEMA" else _na(close)
        tema = _tema(close, ma_signal_len) if ma_signal_type == "TEMA" else _na(close)

        def _any_above(closes, series):
            """close/k > series/k for k in 0..3, exactly as the source wrote."""
            out = pd.Series(False, index=close.index)
            for lag in (0, 1, 2, 3):
                out = out | (closes.shift(lag) > series.shift(lag))
            return out

        def _any_below(closes, series):
            out = pd.Series(False, index=close.index)
            for lag in (0, 1, 2, 3):
                out = out | (closes.shift(lag) < series.shift(lag))
            return out

        macd_close_buy = macd_crsovr & (
            _any_above(close, ma_signal) | _any_above(close, dema) | _any_above(close, tema)
        )
        # NB: the first term of the sell line is `>` in the source, not `<`.
        macd_close_sell = macd_crsndr & (
            ((close > ma_signal)
             | (close.shift(1) < ma_signal.shift(1))
             | (close.shift(2) < ma_signal.shift(2))
             | (close.shift(3) < ma_signal.shift(3)))
            | _any_below(close, dema)
            | _any_below(close, tema)
        )

        # Stgy #4: MACD + MA-ZONE. Only the `high`-sourced average is used by
        # the conditions; MA_zone_srcLO is dead in the source.
        ma_zone_len = int(params["MA_zone_len"])
        ma_zone_type = params["MA_zone_type"]
        ma_zone_src_hi = _matype(dataframe["high"], ma_zone_len, ma_zone_type, volume)
        dema2 = _dema(close, ma_zone_len) if ma_zone_type == "DEMA" else _na(close)
        tema2 = _tema(close, ma_zone_len) if ma_zone_type == "TEMA" else _na(close)
        macd_zone_buy = macd_crsovr & (
            _any_above(close, ma_zone_src_hi) | _any_above(close, dema2) | _any_above(close, tema2)
        )
        macd_zone_sell = macd_crsndr & (
            _any_below(close, ma_zone_src_hi) | _any_below(close, dema2) | _any_below(close, tema2)
        )

        # Stgy #5: MACD + RSI-OB
        rsi = ta.pine_rsi(close, int(params["rsilen"]))
        macd_rsi_en_buy = (rsi > float(params["rsi_ent_value"])) & (
            rsi < float(params["rsi_ob_value"])
        )

        dataframe["pine_macd"] = macd
        dataframe["pine_macd_signal"] = signal
        dataframe["pine_macd_crsovr"] = macd_crsovr
        dataframe["pine_macd_crsndr"] = macd_crsndr
        dataframe["pine_p1"] = bool(params["MACD_crs_signal"])
        dataframe["pine_p2"] = bool(params["MACD_OB"])
        dataframe["pine_p3"] = bool(params["MACD_close"])
        dataframe["pine_p4"] = bool(params["MACD_ZONE"])
        dataframe["pine_p5"] = bool(params["MACD_wid_rsiOB"])
        dataframe["pine_ob_buy"] = macd_ob_buy
        dataframe["pine_ob_sell"] = macd_ob_sell
        dataframe["pine_close_buy"] = macd_close_buy
        dataframe["pine_close_sell"] = macd_close_sell
        dataframe["pine_zone_buy"] = macd_zone_buy
        dataframe["pine_zone_sell"] = macd_zone_sell
        dataframe["pine_rsi_en_buy"] = macd_rsi_en_buy
        return dataframe

    def pine_context(self, dataframe, params):
        columns = {
            "crsovr": "pine_macd_crsovr",
            "crsndr": "pine_macd_crsndr",
            "ob_buy": "pine_ob_buy",
            "ob_sell": "pine_ob_sell",
            "close_buy": "pine_close_buy",
            "close_sell": "pine_close_sell",
            "zone_buy": "pine_zone_buy",
            "zone_sell": "pine_zone_sell",
            "rsi_en_buy": "pine_rsi_en_buy",
        }
        ctx = {name: dataframe[column].to_numpy() for name, column in columns.items()}
        for gate in ("p1", "p2", "p3", "p4", "p5"):
            ctx[gate] = dataframe[f"pine_{gate}"].to_numpy()
        return ctx

    def pine_script(self, broker, i, ctx):
        # --- Stgy #1: MACD CrossOver (enabled by default) -------------------
        if ctx["crsovr"][i] and ctx["p1"][i] and self.IN_DATE_RANGE:
            broker.entry("BUY", "long")
        if ctx["crsndr"][i] and ctx["p1"][i] and self.IN_DATE_RANGE:
            broker.close("BUY")
        # --- Stgy #2: MACD + OverBought ------------------------------------
        if ctx["ob_buy"][i] and ctx["p2"][i] and self.IN_DATE_RANGE:
            broker.entry("BUY", "long")
        if ctx["ob_sell"][i] and ctx["p2"][i] and self.IN_DATE_RANGE:
            broker.close("BUY")
        # --- Stgy #3: MACD + Close -----------------------------------------
        if ctx["close_buy"][i] and ctx["p3"][i] and self.IN_DATE_RANGE:
            broker.entry("BUY", "long")
        if ctx["close_sell"][i] and ctx["p3"][i] and self.IN_DATE_RANGE:
            broker.close("BUY")
        # --- Stgy #4: MACD + MA-ZONE (closes with close_all) ---------------
        if ctx["zone_buy"][i] and ctx["p4"][i] and self.IN_DATE_RANGE:
            broker.entry("BUY", "long")
        if ctx["zone_sell"][i] and ctx["p4"][i] and self.IN_DATE_RANGE:
            broker.close_all()
        # --- Stgy #5: MACD + RSI-OB ----------------------------------------
        if ctx["crsovr"][i] and ctx["rsi_en_buy"][i] and ctx["p5"][i] and self.IN_DATE_RANGE:
            broker.entry("BUY", "long")
        if ctx["crsndr"][i] and ctx["p5"][i] and self.IN_DATE_RANGE:
            broker.close("BUY")
        # --- trailing guard: if (not inDateRange) strategy.close_all() -----
        # inDateRange is the literal `true`, so this branch is dead in the
        # source and can never fire here either.
        if not self.IN_DATE_RANGE:
            broker.close_all()


def _na(reference):
    """Pine's bare `na` in a series position (an all-na series)."""
    return pd.Series(np.nan, index=reference.index, dtype=float)


def _dema(source, length):
    """dema = 2 * ema - ema(ema, length)."""
    first = ta.pine_ema(source, length)
    return 2.0 * first - ta.pine_ema(first, length)


def _tema(source, length):
    """tema = 3 * (ema - ema(ema, n)) + ema(ema(ema, n), n)."""
    first = ta.pine_ema(source, length)
    second = ta.pine_ema(first, length)
    return 3.0 * (first - second) + ta.pine_ema(second, length)
