"""Port of sources/SM_26fd6cc6bb461933.pine (batch_001/MA-HYBRID-BY-RAJ.md).

Pine v4. The file declares a `study("MA HYBRID", overlay=true)` -- an NNFX
indicator with a Baseline, an SSL1, an SSL2 and an SSL3/exit line -- and the
conversion station appended:

    if buy_atr
        strategy.entry("Enter Long", strategy.long)
    else if sell_atr
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` cannot compile inside `study()`, so the "original strategy" IS
the indicator plus that block, and its trading behaviour is exactly what the
block does: enter on the condition, NEVER exit. There is no `strategy()`
declaration and no `strategy.close` / `strategy.exit` in the file, so every
`strategy()` property is Pine's documented default (fixed / 1 contract,
initial capital 1000000, 0% commission, pyramiding 0,
process_orders_on_close=false) and `source_reproduce_stops` is False.

The block's two conditions, reproduced literally (the expressions below are the
source's own, however unusual `lower_half < sslDown2` reads):

    atr_slen   = ma_function(tr(true), 14)      // smoothing = "WMA" -> wma(tr,14)
    upper_band = atr_slen * mult + close        // mult = 1
    lower_band = close - atr_slen * mult
    sslDown2   = Hlv2 < 0 ? maHigh : maLow
    upper_half = atr_slen * atr_crit + close    // atr_crit = 0.9
    lower_half = close - atr_slen * atr_crit
    buy_inatr  = lower_half < sslDown2
    sell_inatr = upper_half > sslDown2
    sell_cont  = close < BBMC and close < sslDown2
    buy_cont   = close > BBMC and close > sslDown2
    sell_atr   = sell_inatr and sell_cont
    buy_atr    = buy_inatr  and buy_cont

with, on the default inputs (maType="HMA", len=60, SSL2Type="JMA", len2=5):

    BBMC        = HMA(close, 60)
    maHigh/maLow = JMA(high, 5) / JMA(low, 5)
    Hlv2        = close > maHigh ? 1 : close < maLow ? -1 : Hlv2[1]

The `if / else if` order matters only for the single-bar case where both hold,
and it is kept exactly as written.

Only the SSL2 chain feeds the order block; the Baseline's Keltner channel
(Keltma / upperk / lowerk), SSL1 (sslDown) and the EXIT line (sslExit,
base_cross_Long/Short, codiff) feed `plot` / `plotshape` / a commented-out
`plotarrow` and the commented-out `alertcondition`s, so they are display-only and
are not computed. They have no state that any computed series reads.
"""
import math

import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_int(value: float) -> int:
    """Pine's implicit float -> int cast: round to nearest, halfway away from zero.

    The source writes `len / 2` and `round(sqrt(len))` where `ta.wma` wants an
    int. `pine_int(60 / 2) == 30` and `pine_int(sqrt(60)) == 8`; this port's two
    lengths are both exact, so no rounding ambiguity arises on the defaults.
    """
    return int(math.floor(value + 0.5)) if value >= 0 else -int(math.floor(-value + 0.5))


def _hma(source, length):
    # ta.wma(2 * ta.wma(src, len / 2) - ta.wma(src, len), round(sqrt(len)))
    inner = 2.0 * ta.pine_wma(source, _pine_int(length / 2.0)) - ta.pine_wma(
        source, int(length)
    )
    return ta.pine_wma(inner, _pine_int(math.sqrt(length)))


def _jma(source, length, phase, power):
    """Jurik MA, as the source writes it (everget's 2018 translation).

    Every recursion variable is declared `x = 0.0` and then immediately
    reassigned with `:=`, so the declaration's value is never observable and
    `nz(x[1])` on the first bar supplies 0 -- modelled by starting each running
    value at 0.0.

    `beta` here is the function-local `beta = 0.45 * (len - 1) / (0.45 * (len -
    1) + 2)`; it SHADOWS the global `beta` input (defval 0.8), which the
    dispatcher never sees. The local value is the one used.
    """
    values = source.to_numpy(dtype=float)
    n = len(values)
    phase_ratio = 0.5 if phase < -100 else (2.5 if phase > 100 else phase / 100.0 + 1.5)
    beta = 0.45 * (int(length) - 1) / (0.45 * (int(length) - 1) + 2.0)
    alpha = beta ** power
    out = np.empty(n, dtype=float)
    e0 = e1 = e2 = jma = 0.0
    for t in range(n):
        value = values[t]
        e0 = (1.0 - alpha) * value + alpha * e0
        e1 = (value - e0) * (1.0 - beta) + beta * e1
        e2 = (e0 + phase_ratio * e1 - jma) * (1.0 - alpha) ** 2 + alpha ** 2 * e2
        jma = e2 + jma
        out[t] = jma
    return pd.Series(out, index=source.index, dtype=float)


def _ma(kind, source, length, params):
    """The source's `ma(type, src, len)` dispatcher.

    Only the two types the entry path actually reaches on the default inputs
    are implemented: HMA (maType / SSL3Type) and JMA (SSL2Type). Any other
    option in the inputs' option lists is NOT implemented and raises loudly,
    rather than being silently substituted with an approximation.
    """
    if kind == "HMA":
        return _hma(source, length)
    if kind == "JMA":
        return _jma(source, length, int(params["jurik_phase"]), int(params["jurik_power"]))
    raise NotImplementedError(
        f"MA-HYBRID port implements only the HMA and JMA variants the default "
        f"inputs select; maType/SSL2Type={kind!r} is not implemented"
    )


def _ma_function(source, atrlen, smoothing):
    """The source's `ma_function`: RMA / SMA / EMA / WMA on the ATR source."""
    if smoothing == "RMA":
        return ta.pine_rma(source, atrlen)
    if smoothing == "SMA":
        return ta.pine_sma(source, atrlen)
    if smoothing == "EMA":
        return ta.pine_ema(source, atrlen)
    return ta.pine_wma(source, atrlen)


class SMMaHybridByRaj_26fd6c(PinePortBase, IStrategy):
    source_id = "SM_26fd6cc6bb461933"
    source_file = "MA-HYBRID-BY-RAJ.md"
    timeframe = "30m"
    can_short = True
    source_defaults: dict = {
        "atrlen": 14,
        "mult": 1,
        "smoothing": "WMA",
        "maType": "HMA",
        "len": 60,
        "SSL2Type": "JMA",
        "len2": 5,
        "SSL3Type": "HMA",
        "len3": 15,
        "src": "close",
        "jurik_phase": 3,
        "jurik_power": 1,
        "useTrueRange": True,
        "multy": 0.2,
        "atr_crit": 0.9,
    }
    # No `strategy()` call exists in the source, so Pine's documented defaults
    # apply: fixed / 1 contract, 1000000 initial capital, 0% commission,
    # pyramiding 0, process_orders_on_close = false.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_mintick = 0.1
    source_fidelity_notes = [
        "The source is a `study()`, not a `strategy()`: the order block appended "
        "by the conversion station (`if buy_atr ... else if sell_atr ...`) is "
        "the whole trading behaviour. No `strategy()` declaration exists, so "
        "fixed/1, 1000000 capital, 0% commission and pyramiding 0 are Pine's "
        "documented defaults rather than declarations.",
        "NO exit exists in the source; the only `alertcondition`s that mention "
        "exits are commented out, and even those are alerts, not orders. A "
        "position is closed only by the opposite entry reversing it, so "
        "source_reproduce_stops is False.",
        "Only the SSL2 chain reaches the order block. The Baseline Keltner "
        "channel (Keltma/upperk/lowerk), SSL1 (sslDown) and the EXIT line "
        "(ExitHigh/ExitLow -> sslExit -> base_cross_Long/Short -> codiff) feed "
        "`plot`/`plotshape`, a commented-out `plotarrow` and commented-out "
        "`alertcondition`s only; they are display-only and are not computed. "
        "None of them carries state another computed series reads.",
        "Consistent with that, `SSL3Type` / `len3` (HMA / 15) are declared as "
        "defaults because the source declares them, but no series used by the "
        "order block depends on them.",
        "`src` (the Source input, defval close) and `mult` (the ATR multiplier) "
        "are likewise declared but not read by the entry path: `src` feeds only "
        "`Keltma` and `mult` only `upper_band` / `lower_band`, which reach the "
        "Baseline/Keltner plots and the `candlesize_violation` plotshape. The "
        "conditions the order block tests use the literal `close`, exactly as "
        "the source writes them, so overriding `src` would change no trade.",
        "Only the HMA and JMA variants of the source's `ma(type, src, len)` "
        "dispatcher are implemented -- those are what the default inputs "
        "select. Selecting any other documented option (SMA / EMA / DEMA / "
        "TEMA / LSMA / WMA / MF / VAMA / TMA / Kijun v2 / EDSMA / McGinley) "
        "raises NotImplementedError instead of being approximated.",
        "MODELLING CHOICE (parity risk): Pine v4's `/` is modelled as float "
        "division, matching the precedent already in this repository "
        "(batch_001/HMA优化多周期...py and batch_001/JMA指标交叉RSI....py). It "
        "matters twice here: `len / 2` (=30.0) feeds `ta.wma`, which needs an "
        "int -- cast with round-half-away-from-zero, and 60/2 and 30 are exact, "
        "so no ambiguity arises on the defaults; and `jurik_phase / 100 + 1.5` "
        "gives phaseRatio 1.53 at jurik_phase=3. Under integer division those "
        "would be 30 and 1.5. Unverified against the original platform.",
        "`beta` inside the JMA branch shadows the global `beta` input "
        "(defval 0.8); the function-local `0.45 * (len - 1) / (0.45 * (len - "
        "1) + 2)` is the one that takes effect, and the global input is "
        "therefore declared but unused.",
        "MODELLING CHOICE: `tr(true)` is Pine's handle_na=true true range, so "
        "the first bar is high-low -- pine_ta.pine_tr(dataframe, "
        "handle_na=True). PINE_SEMANTICS.md 3.7 records the opposite default "
        "(handle_na=false -> na on the first bar) as a known boundary "
        "difference; `tr(true)` is the explicit form and is what is used here.",
        "MODELLING CHOICE: `Hlv2 = int(na)` starts the SSL2 state as na. While "
        "it is na, `close > maHigh` / `close < maLow` has not yet decided a "
        "side and `Hlv2 := Hlv2[1]` keeps na; `Hlv2 < 0 ? maHigh : maLow` then "
        "takes the else branch, i.e. maLow. numpy `NaN < 0` is False and picks "
        "the same branch, so no special-casing is added.",
        "Pine's `and` propagates na (na and X is na unless X is false, in which "
        "case false); `if na` is false. numpy maps every na comparison to "
        "False, so `buy_atr` / `sell_atr` are False rather than na -- the same "
        "outcome (no entry) either way.",
        "Display-only statements are not reproduced: the `show_Baseline` / "
        "`show_SSL1` / `show_atr` toggles, every `plot` / `plotshape` / "
        "`fill` and `color_bar` / `color_ssl1` / `atr_fill`.",
        "The `/*backtest` header declares `period: 30m` on Futures_Binance "
        "BTC_USDT, so `timeframe` is \"30m\"; its `basePeriod: 15m` is the "
        "extractor's own bar granularity, not the strategy's period.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding are not modelled (PINE_SEMANTICS.md section 2).",
    ]

    def pine_indicators(self, dataframe, params):
        close = dataframe["close"]
        high = dataframe["high"]
        low = dataframe["low"]

        # atr_slen = ma_function(tr(true), atrlen) with smoothing = "WMA"
        atr_slen = _ma_function(
            ta.pine_tr(dataframe, handle_na=True), int(params["atrlen"]), params["smoothing"]
        )

        # BBMC = ma(maType, close, len)
        bbmc = _ma(params["maType"], close, int(params["len"]), params)

        # maHigh / maLow = ma(SSL2Type, high|low, len2)
        ma_high = _ma(params["SSL2Type"], high, int(params["len2"]), params)
        ma_low = _ma(params["SSL2Type"], low, int(params["len2"]), params)

        # Hlv2 := close > maHigh ? 1 : close < maLow ? -1 : Hlv2[1]
        close_values = close.to_numpy(dtype=float)
        high_values = ma_high.to_numpy(dtype=float)
        low_values = ma_low.to_numpy(dtype=float)
        hlv2 = np.full(len(dataframe), np.nan, dtype=float)
        previous = np.nan
        for t in range(len(dataframe)):
            if close_values[t] > high_values[t]:
                current = 1.0
            elif close_values[t] < low_values[t]:
                current = -1.0
            else:
                current = previous
            hlv2[t] = current
            previous = current
        hlv2 = pd.Series(hlv2, index=dataframe.index, dtype=float)
        # sslDown2 = Hlv2 < 0 ? maHigh : maLow   (na -> else branch, as in Pine)
        ssl_down2 = ma_high.where(hlv2 < 0, ma_low)

        atr_crit = float(params["atr_crit"])
        upper_half = atr_slen * atr_crit + close
        lower_half = close - atr_slen * atr_crit

        buy_inatr = lower_half < ssl_down2
        sell_inatr = upper_half > ssl_down2
        sell_cont = (close < bbmc) & (close < ssl_down2)
        buy_cont = (close > bbmc) & (close > ssl_down2)
        sell_atr = (sell_inatr & sell_cont).fillna(False)
        buy_atr = (buy_inatr & buy_cont).fillna(False)

        dataframe["pine_atr_slen"] = atr_slen
        dataframe["pine_bbmc"] = bbmc
        dataframe["pine_ssl2"] = ssl_down2
        dataframe["pine_buy_atr"] = buy_atr.astype(bool)
        dataframe["pine_sell_atr"] = sell_atr.astype(bool)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "buy_atr": dataframe["pine_buy_atr"].to_numpy(dtype=bool),
            "sell_atr": dataframe["pine_sell_atr"].to_numpy(dtype=bool),
        }

    def pine_script(self, broker, i, ctx):
        # if buy_atr
        #     strategy.entry("Enter Long", strategy.long)
        # else if sell_atr
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_atr"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_atr"][i]:
            broker.entry("Enter Short", "short")
