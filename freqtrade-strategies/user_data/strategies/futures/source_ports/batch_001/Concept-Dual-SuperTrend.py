"""Port of sources/SM_3c7949e58c476dd3.pine (batch_001/Concept-Dual-SuperTrend.md).

Pine v5. Two SuperTrends of the same source (hl2) and the same ATR period (10)
but different ATR multipliers -- "fast" 2 and "slow" 3 -- are computed; the
order block appended at the end of the file trades the SLOW one only:

    if buySignal2
        strategy.entry("Enter Long", strategy.long)
    else if sellSignal2
        strategy.entry("Enter Short", strategy.short)

with

    atr2  = ta.atr(10)                          # changeATR is true by default
    dnA2  = nz(dn2[1], dn2); dn2 := close[1] < dnA2 ? min(dn2, dnA2) : dn2
    upA2  = nz(up2[1], up2); up2 := close[1] > upA2 ? max(up2, upA2) : up2
    trend2 = -1 if it was -1 and close > dnA2 else 1 if it was 1 and close < upA2
    buySignal2  = trend2 == 1  and trend2[1] == -1
    sellSignal2 = trend2 == -1 and trend2[1] == 1

Both entries are plain market orders with no qty/stop/limit argument and there is
no exit call anywhere in the file, so a position is only ever left by the
opposite entry (which the engine models as a single reverse fill), and a
position still open at the end of the window stays open.

The file declares `indicator(...)`, not `strategy(...)` (see PINE_SEMANTICS.md
1.17: the host appended this block mechanically), so no strategy() properties
exist and Pine's documented defaults are what the source_* attributes record:
fixed 1-unit sizing, 0% commission, pyramiding 0, initial capital 1000000 USD.

FIDELITY:

* The trend/band recursion is a sequential ratchet (`nz(x[1], x)` then `:=`), so
  it is computed with an explicit bar-by-bar loop rather than vectorised; `na`
  comparisons are false, as Pine treats them, which is what keeps the trend at
  +1 through the ATR warmup instead of flipping.
* `ta.tr` (the source's `atrA` branch, and the input of `ta.sma(ta.tr, periods)`)
  is `na` on the first bar in Pine -- there is no previous close. pine_ta.pine_tr
  returns `high - low` there instead (PINE_SEMANTICS.md 3.7), so bar 0 is masked
  to na here. It only bites the `changeATR = false` branch, which is not the
  default; `ta.atr` itself is unaffected because it is defined with
  `handle_na = true`.
* The fast SuperTrend, its plots/fills/labels and the `showlabels` /
  `transp_*` / `highlighting*` inputs are display-only: they place no order. The
  fast series is still computed so the formulas are on the record, but nothing
  reads it.
* `timeframe = ''` in the `indicator()` call is the chart timeframe, not a
  request for another one; `/*backtest`'s `period: 1m` is the timeframe.
* No exit call exists, so `source_reproduce_stops` is False.
"""
import numpy as np
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _supertrend(dataframe, src, multiplier, periods, change_atr):
    """Pine's SuperTrend band pair plus its trend variable, one bar at a time.

    Returns `(upA, dnA, trend)`: the ATR bands the trend test reads (which are
    the PREVIOUS bar's band level when there is one) and the trend itself.

        atrA = ta.sma(ta.tr, periods)
        atr  = changeATR ? ta.atr(periods) : atrA
        up   = src - multiplier * atr
        upA  = nz(up[1], up);  up := close[1] > upA ? max(up, upA) : up
        dn   = src + multiplier * atr
        dnA  = nz(dn[1], dn);  dn := close[1] < dnA ? min(dn, dnA) : dn
        trend    := nz(trend[1], trend)
        trend    := trend == -1 and close > dnA ? 1
                  : trend == 1 and close < upA ? -1 : trend
    """
    close = dataframe["close"].to_numpy(dtype=float)
    src = np.asarray(src, dtype=float)
    # `ta.tr`: na on the first bar, because there is no previous close.
    true_range = ta.pine_tr(dataframe, handle_na=False)
    true_range.iloc[0] = np.nan
    atr = (
        ta.pine_atr(dataframe, periods).to_numpy(dtype=float)
        if change_atr
        else ta.pine_sma(true_range, periods).to_numpy(dtype=float)
    )

    count = len(close)
    up = np.full(count, np.nan)
    dn = np.full(count, np.nan)
    up_a = np.full(count, np.nan)
    dn_a = np.full(count, np.nan)
    trend = np.full(count, np.nan)
    previous_trend = np.nan
    for i in range(count):
        raw_up = src[i] - multiplier * atr[i]
        raw_dn = src[i] + multiplier * atr[i]
        # nz(x[1], x): the previous bar's band, or this bar's raw band.
        up_a[i] = up[i - 1] if i > 0 and np.isfinite(up[i - 1]) else raw_up
        dn_a[i] = dn[i - 1] if i > 0 and np.isfinite(dn[i - 1]) else raw_dn
        previous_close = close[i - 1] if i > 0 else np.nan
        # close[1] > upA / close[1] < dnA are FALSE when either side is na.
        up[i] = max(raw_up, up_a[i]) if _is_true(previous_close, up_a[i], ">") else raw_up
        dn[i] = min(raw_dn, dn_a[i]) if _is_true(previous_close, dn_a[i], "<") else raw_dn

        current = previous_trend if np.isfinite(previous_trend) else 1.0
        if current == -1 and _is_true(close[i], dn_a[i], ">"):
            current = 1.0
        elif current == 1 and _is_true(close[i], up_a[i], "<"):
            current = -1.0
        trend[i] = current
        previous_trend = current
    return up_a, dn_a, trend


def _is_true(left, right, operator):
    """A Pine comparison: false whenever either side is na."""
    if not (np.isfinite(left) and np.isfinite(right)):
        return False
    return left > right if operator == ">" else left < right


def _signal(trend, direction):
    """`trend == d and trend[1] == -d`, false across the na history."""
    previous = np.concatenate([[np.nan], trend[:-1]])
    return (trend == direction) & (previous == -direction)


class SMConceptDualSuperTrend_3c7949(PinePortBase, IStrategy):
    source_id = "SM_3c7949e58c476dd3"
    source_file = "Concept-Dual-SuperTrend.md"
    timeframe = "1m"
    can_short = True
    source_defaults = {
        "src": "hl2",           # input(hl2, title='Source')
        "multiplier": 2.0,      # input.float(2, title='ATR Multiplier (Fast)')
        "multiplier2": 3.0,     # input.float(3, title='ATR Multiplier (Slow)')
        "periods": 10,          # input(10, title='ATR Period (Fast)')
        "periods2": 10,         # input(10, title='ATR Period (Slow)')
        "transp_st": 70.0,      # input.float(70, title='Line Transparency')
        "transp_hl": 90.0,      # input.float(90, title='Shading Transparency')
        "changeATR": True,      # input(true, title='Change ATR Calculation Method?')
        "highlighting": True,   # input(true, title='Show Shading? (Fast)')
        "highlighting2": True,  # input(true, title='Show Shading? (Slow)')
        "showlabels": True,     # input(true, title='Show Buy/Sell Labels?')
    }
    # indicator(...) declares no strategy() properties at all, so Pine's
    # documented defaults apply: fixed 1 unit, 0% commission, pyramiding 0,
    # initial capital 1000000 USD.
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "The source declares `indicator(...)`, not `strategy(...)`: Pine v5 will "
        "not compile strategy.entry inside an indicator, so the original "
        "behaviour is the indicator plus the order block appended at the end of "
        "the file (PINE_SEMANTICS.md 1.17). That block trades the SLOW SuperTrend "
        "(buySignal2 / sellSignal2) only; the fast one plots and nothing else.",
        "No exit call exists -- no strategy.close, no strategy.exit, no stop or "
        "limit -- so a position is only left by the opposite entry, which the "
        "engine models as one reverse fill. source_reproduce_stops is False and "
        "a position open at the end of the window stays open.",
        "The `else if` in the source is reproduced as `elif`, so the short entry "
        "is only evaluated on bars where the long signal is false -- the source's "
        "written order is the engine's fill priority order.",
        "The band/trend recursion is a sequential ratchet and is computed with an "
        "explicit loop; na comparisons are false, Pine's rule, which keeps "
        "trend2 at +1 across the ATR warmup rather than flipping it.",
        "ta.tr is na on the first bar in Pine (no previous close) while "
        "pine_ta.pine_tr returns high - low there (PINE_SEMANTICS.md 3.7); bar 0 "
        "is therefore masked to na so the ta.sma(ta.tr, periods) branch matches "
        "Pine. ta.atr itself is unaffected (it uses handle_na = true).",
        "Only the DEFAULT branch of `changeATR ? ta.atr : atrA` is active "
        "(changeATR defaults to true); both branches are still implemented so a "
        "parameter override keeps the source's meaning.",
        "The `src` input defaults to hl2 and is resolved through "
        "pine_ta.pine_source, so a different source name still works.",
        "The fast SuperTrend, plot/fill/plotshape, and the transp_*/highlighting*/"
        "showlabels inputs are display-only and place no order; the fast series "
        "is computed for the record but nothing reads it.",
        "`timeframe = ''` in indicator() means the chart timeframe, so it is not "
        "a request for a second timeframe; the port's timeframe comes from the "
        "/*backtest header's `period: 1m`.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, params["src"])
        change_atr = bool(params["changeATR"])

        # Calculations (Fast) -- computed, plotted, never traded.
        up_a, dn_a, trend = _supertrend(
            dataframe, src, float(params["multiplier"]), int(params["periods"]),
            change_atr,
        )
        dataframe["pine_upA"] = up_a
        dataframe["pine_dnA"] = dn_a
        dataframe["pine_trend"] = trend
        dataframe["pine_buy_signal"] = _signal(trend, 1)

        # Calculations (Slow) -- this is the pair the order block trades.
        up_a2, dn_a2, trend2 = _supertrend(
            dataframe, src, float(params["multiplier2"]), int(params["periods2"]),
            change_atr,
        )
        dataframe["pine_upA2"] = up_a2
        dataframe["pine_dnA2"] = dn_a2
        dataframe["pine_trend2"] = trend2
        dataframe["pine_buy_signal2"] = _signal(trend2, 1)
        dataframe["pine_sell_signal2"] = _signal(trend2, -1)
        return dataframe

    def pine_context(self, dataframe, params):
        del params
        return {
            "buy_signal2": dataframe["pine_buy_signal2"].to_numpy(),
            "sell_signal2": dataframe["pine_sell_signal2"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if buySignal2
        #     strategy.entry("Enter Long", strategy.long)
        # else if sellSignal2
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["buy_signal2"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["sell_signal2"][i]:
            broker.entry("Enter Short", "short")
