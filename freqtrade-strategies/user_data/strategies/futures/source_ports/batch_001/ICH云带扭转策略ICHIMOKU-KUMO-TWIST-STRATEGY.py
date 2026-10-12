"""Port of sources/SM_d53eefafda6ad8c5.pine (batch_001/ICH云带扭转策略ICHIMOKU-KUMO-TWIST-STRATEGY.md).

Pine v3 (`//@version=3`). An Ichimoku "kumo twist": the two leading spans are
compared directly -- there is no displacement in the SIGNAL, only in the plots
-- and the twist of leadLine1 across leadLine2 is traded:

    dropn(src, n) => na(src[n]) ? na : src
    lows = dropn(low, dropCandles) ; highs = dropn(high, dropCandles)
    lowsp  = logScaling ? log(lows)  : lows
    highsp = logScaling ? log(highs) : highs

    xlowest_(src, len) =>            // progressive min, stops at the first na
        x = src
        for i = 1 to len - 1
            v = src[i]
            if na(v)
                break
            x := min(x, v)
        x
    xlowest(src, len) => na(src[len]) ? xlowest_(src, len) : lowest(src, len)
    xhighest is the mirror image

    donchian(len) => avg(xlowest(lowsp, len), xhighest(highsp, len))
    conversionLine = donchian(conversionPeriods)        // 20
    baseLine       = donchian(basePeriods)              // 60
    leadLine1      = avg(conversionLine, baseLine)
    leadLine2      = donchian(laggingSpan2Periods)      // 120

    golong  = crossover(leadLine1, leadLine2)
    goshort = crossunder(leadLine1, leadLine2)

    strategy.entry("Buy",  strategy.long,  when=golong,  stop=(stoploss ? high + syminfo.mintick : na))
    strategy.entry("Sell", strategy.short, when=goshort, stop=(stoploss ? low  - syminfo.mintick : na))

THE TWO ENTRIES ARE RESTING STOP ENTRIES, not market orders. `stop = high +
mintick` sits ABOVE the signal bar's high, so the buy is a stop-buy breakout:
it rests from the next bar and fills when a later bar's high reaches the level.
`stop = low - mintick` is the same on the sell side. That is the framework
boundary PINE_SEMANTICS.md section 2.11 records: the projection can only fire
`enter_long` / `enter_short` on the bar the order was PLACED, and Freqtrade has
no resting entry order, so the framework fills at the next bar's open while the
engine may fill several bars later, or never. A divergence in entry bar and
price is therefore expected here and is reported by the chain verifier rather
than hidden.

With `stoploss = false` the source passes `stop=na`, which on the original
platform places no stop and degrades the call to a market order; the port
guards identically rather than handing nan to the engine.

The preset cascade is reproduced verbatim. Its default is "Crypto Doubled",
so conversion/base/lagging-span-2 are 20/60/120 -- NOT the 9/26/52 the md's
prose describes (see FIDELITY).

`strategy()` declares only `title` / `shorttitle` / `overlay`, so Pine's
documented defaults apply and are what this port carries:
`default_qty_type=fixed`, one unit per order, `commission_value=0`,
`pyramiding=0`, `process_orders_on_close=false`, initial capital 1000000.

The `/*backtest` header declares `period: 1d` on Futures_Binance BTC_USDT, so
`timeframe` is "1d"; its `basePeriod: 1h` is the FMZ backtester's own filling
granularity for those daily bars, not the strategy's period.

FIDELITY:

* The md's prose says the lines are the standard Ichimoku 9/26/52 midpoints
  ("转换线计算过去9根K线...基准线计算过去26根...导线2为过去52根"). The source's
  `presets` input defaults to "Crypto Doubled", i.e. 20/60/120 with a
  displacement of 30. The source is the authority (iron rule 2); the prose
  discrepancy is recorded here and the code is not changed.
* `displacement` (30/30/26/26) is used ONLY by the `plot(..., offset=...)`
  calls that draw the cloud. The signal compares `leadLine1` and `leadLine2`
  with no displacement and no `[displacement]` shift, so the port does not
  displace either. Reproducing the offset would be inventing a future
  reference the source never makes.
* `dropn(low, dropCandles)` returns na on the first `dropCandles` bars only
  because `low[n]` is na there; the port reproduces that with `shift(n)`.
  dropCandles is 1 by default, so `lows` / `highs` are na on bar 0 alone.
* `xlowest` / `xhighest` are hand-written progressive scans, NOT `lowest` /
  `highest`: while `src[len]` is still na the source falls back to a min/max
  that walks back only as far as the data goes and stops at the first na, so
  the warm-up values are a growing-window extreme rather than na. The port
  implements the loop literally instead of calling
  `pine_ta.pine_lowest` / `pine_ta.pine_highest`, which return na until the
  window is full (iron rule 3: the formula is checked, not the name).
* `logScaling` is an input, so both branches are implemented; with the default
  "Linear" the log branch is inert. `log` is Pine's natural log.
* `avg(a, b)` is Pine's `(a + b) / 2`.
* `crossover` / `crossunder` return false when either operand is na, which is
  the v3 comparison rule and what pine_ta.pine_crossover provides.
* `plot` / `fill` / `hline` and the title are display-only and are not
  reproduced.
* There is no `strategy.exit` / `strategy.close` / `strategy.cancel` anywhere
  in the source: a position is only ever closed by the opposite entry
  reversing it, so `source_reproduce_stops` is False and a position open at
  the end of the window stays open.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding are not modelled; the framework and the engine can differ by a
  rounded quantity (measured separately by the chain verifier).
"""
import numpy as np
import pandas as pd

from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

# The four (conversion, base, lagging-span-2, displacement) tuples the source's
# if/else cascade returns. Anything that is not one of the three named presets
# falls through to the last `else`, i.e. the "Standard Singled" row.
_PRESETS = {
    "Crypto Doubled": (20, 60, 120, 30),
    "Crypto Singled": (10, 30, 60, 30),
    "Standard Doubled": (18, 52, 104, 26),
    "Standard Singled": (9, 26, 52, 26),
}


def _drop_n(src: pd.Series, n: int) -> pd.Series:
    """`dropn(src, n) => na(src[n]) ? na : src` -- na on the first `n` bars."""
    n = int(n)
    if n <= 0:
        return src.astype(float)
    return src.astype(float).where(src.shift(n).notna())


def _xextreme_progressive(values: np.ndarray, length: int, want_max: bool) -> np.ndarray:
    """The source's `xlowest_` / `xhighest_` loop, literally.

    Starts from the current bar's value and walks back up to `length - 1` bars,
    stopping at the first na or at the start of the series.
    """
    out = np.full(len(values), np.nan)
    for i in range(len(values)):
        x = values[i]
        if not np.isfinite(x):
            continue
        for j in range(1, int(length)):
            k = i - j
            if k < 0:
                break
            v = values[k]
            if not np.isfinite(v):
                break
            x = max(x, v) if want_max else min(x, v)
        out[i] = x
    return out


def _xextreme(src: pd.Series, length: int, want_max: bool) -> pd.Series:
    """`xlowest(src, len)` / `xhighest(src, len)`.

    While `src[len]` is na (the series is too short, or the value there is na)
    the source uses its own progressive scan; afterwards it uses the built-in
    `lowest` / `highest`, which is a full-window rolling extreme that returns
    na until `length` bars have elapsed.
    """
    length = int(length)
    values = src.to_numpy(dtype=float)
    progressive = _xextreme_progressive(values, length, want_max)
    rolling = (
        ta.pine_highest(src, length) if want_max else ta.pine_lowest(src, length)
    ).to_numpy(dtype=float)
    too_short = src.shift(length).isna().to_numpy()
    return pd.Series(np.where(too_short, progressive, rolling), index=src.index)


def _donchian(lowsp: pd.Series, highsp: pd.Series, length: int) -> pd.Series:
    """`donchian(len) => avg(xlowest(lowsp, len), xhighest(highsp, len))`."""
    lowest = _xextreme(lowsp, length, want_max=False)
    highest = _xextreme(highsp, length, want_max=True)
    return ta.pine_avg(lowest, highest)


class SMIchKumoTwist_d53eef(PinePortBase, IStrategy):
    source_id = "SM_d53eefafda6ad8c5"
    source_file = "ICH云带扭转策略ICHIMOKU-KUMO-TWIST-STRATEGY.md"
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {
        "scaling": "Linear",
        "presets": "Crypto Doubled",
        "dropCandles": 1,
        "showClouds": False,
        "stoploss": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    # No strategy.exit / close / cancel in the source: the only way out of a
    # position is the opposite entry reversing it.
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Both entries are resting STOP entries (`stop = high + mintick` / "
        "`low - mintick`), which Freqtrade cannot be handed. The projection "
        "fires on the placement bar and the framework fills at the next open, "
        "while the engine fills when a later bar actually reaches the level, or "
        "never. PINE_SEMANTICS.md section 2.11; an entry-bar/price divergence is "
        "the expected outcome, not a port defect.",
        "The md's prose describes the standard Ichimoku 9/26/52 midpoints; the "
        "source's `presets` input defaults to \"Crypto Doubled\" = 20/60/120. "
        "The source is reproduced, the prose discrepancy is recorded.",
        "`displacement` (30) is used only by plot(offset=...) to draw the cloud. "
        "The signal compares leadLine1 and leadLine2 with no displacement and no "
        "history shift, so the port does not displace either.",
        "xlowest/xhighest are the source's own progressive scans while "
        "src[len] is na (they walk back only as far as the data goes and stop at "
        "the first na); the built-in lowest/highest is used after that. "
        "pine_lowest / pine_highest would have returned na through the warm-up "
        "instead, so the loop is implemented literally rather than by name.",
        "The preset if/else cascade falls through to the last else for any "
        "string that is not one of the first three presets; the port mirrors "
        "that fallback.",
        "logScaling is an input, so both branches are implemented (natural log "
        "of the dropped lows/highs); with the default Linear the branch is "
        "inert. The source's exp() calls exist only to restore the scale of the "
        "plotted cloud, which is not reproduced.",
        "dropCandles=1 by default makes lows/highs na on bar 0 alone, which is "
        "what the port's shift(1) reproduces.",
        "There is no exit call in the source; source_reproduce_stops is False "
        "and a position open at the end of the window stays open.",
        "A na stop places no order on the original platform (the `stoploss` "
        "input set to false); the port guards identically instead of passing nan "
        "to the engine.",
        "plot / fill / hline, the title and the overlay flag are display-only "
        "and are not reproduced.",
        "Leverage, margin, liquidation, funding and venue contract-step "
        "rounding are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        presets = str(params["presets"])
        conversion_periods, base_periods, lagging2_periods, _displacement = _PRESETS.get(
            presets, _PRESETS["Standard Singled"]
        )
        drop_candles = int(params["dropCandles"])
        log_scaling = str(params["scaling"]) == "Log"
        want_stop = bool(params["stoploss"])
        mintick = float(self.source_mintick)

        lows = _drop_n(dataframe["low"], drop_candles)
        highs = _drop_n(dataframe["high"], drop_candles)
        lowsp = np.log(lows) if log_scaling else lows
        highsp = np.log(highs) if log_scaling else highs

        conversion_line = _donchian(lowsp, highsp, conversion_periods)
        base_line = _donchian(lowsp, highsp, base_periods)
        lead_line1 = ta.pine_avg(conversion_line, base_line)
        lead_line2 = _donchian(lowsp, highsp, lagging2_periods)

        golong = ta.pine_crossover(lead_line1, lead_line2)
        goshort = ta.pine_crossunder(lead_line1, lead_line2)

        dataframe["pine_conversion_line"] = conversion_line
        dataframe["pine_base_line"] = base_line
        dataframe["pine_lead1"] = lead_line1
        dataframe["pine_lead2"] = lead_line2
        dataframe["pine_golong"] = golong
        dataframe["pine_goshort"] = goshort
        # strategy.entry(..., stop=(stoploss ? high + syminfo.mintick : na))
        if want_stop:
            dataframe["pine_buy_stop"] = dataframe["high"] + mintick
            dataframe["pine_sell_stop"] = dataframe["low"] - mintick
        else:
            dataframe["pine_buy_stop"] = np.nan
            dataframe["pine_sell_stop"] = np.nan
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "golong": dataframe["pine_golong"].to_numpy(),
            "goshort": dataframe["pine_goshort"].to_numpy(),
            "buy_stop": dataframe["pine_buy_stop"].to_numpy(dtype=float),
            "sell_stop": dataframe["pine_sell_stop"].to_numpy(dtype=float),
        }

    def pine_script(self, broker, i, ctx):
        # strategy.entry("Buy", strategy.long, when=golong, stop=(stoploss ? high+syminfo.mintick : na))
        if ctx["golong"][i]:
            stop = ctx["buy_stop"][i]
            if np.isfinite(stop):
                broker.entry("Buy", "long", stop=float(stop))
            else:
                broker.entry("Buy", "long")
        # strategy.entry("Sell", strategy.short, when=goshort, stop=(stoploss ? low-syminfo.mintick : na))
        if ctx["goshort"][i]:
            stop = ctx["sell_stop"][i]
            if np.isfinite(stop):
                broker.entry("Sell", "short", stop=float(stop))
            else:
                broker.entry("Sell", "short")
