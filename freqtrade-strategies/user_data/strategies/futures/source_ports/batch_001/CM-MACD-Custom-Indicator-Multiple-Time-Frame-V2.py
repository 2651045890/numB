"""Port of sources/SM_ddb06dd9f076f1bc.pine (batch_001/CM-MACD-Custom-Indicator-Multiple-Time-Frame-V2.md).

Pine v5 (`//@version=5`). ChaoZhang's "_CM_MacD_Ult_MTF_V2.1": a MACD whose two
moving averages and whose signal line are each wrapped in
`request.security(syminfo.tickerid, res, ...)`, plus a conversion tool's order
block appended at the end -- the pattern PINE_SEMANTICS.md 1.17 records:

    fast_ma = request.security(tickerid, res, sma_source == "SMA" ? ta.sma(src, 12) : ta.ema(src, 12))
    slow_ma = request.security(tickerid, res, sma_source == "SMA" ? ta.sma(src, 26) : ta.ema(src, 26))
    macd    = fast_ma - slow_ma
    signal  = request.security(tickerid, res, sma_signal == "SMA" ? ta.sma(macd, 5) : ta.ema(macd, 5))
    hist    = macd - signal
    cross_UP_A = (signal[1] >= macd[1] and signal < macd) and macd > 0
    cross_DN_B = (signal[1] <= macd[1] and signal > macd) and macd < 0

    if alert_Long_A and cross_UP_A
        strategy.entry("Enter Long", strategy.long)
    else if alert_Short_B and cross_DN_B
        strategy.entry("Enter Short", strategy.short)

`strategy.entry` does not compile inside `indicator()`, so the trading
behaviour of this source is what the appended block does: enter on the gated
cross, and NEVER exit. No exit call of any kind exists in the file -- there is
not even a commented-out `strategy.exit` line -- so a position is only ever
ended by the opposite entry reversing it.

The two entry gates are BOOL INPUTS (`alert_Long_A`, `alert_Short_B`, both
default `true`), not literals, so they are carried in `source_defaults` and
evaluated in `pine_script` rather than being folded away. With their defaults
the conditions reduce to `cross_UP_A` / `cross_DN_B`, but a source parameter
override flips the corresponding side off, which is what the source does.

`res = input.timeframe("", "Indicator TimeFrame")` defaults to the EMPTY
string, which Pine reads as "the chart's timeframe"; on that default every
`request.security` call is the identity on the chart series and the whole MTF
shell is a no-op, so the port computes the three series directly. See FIDELITY
for what a non-default `res` would mean.

There is no `strategy(...)` call, so the Pine defaults apply: `fixed` /
1 contract, initial capital 1000000, commission 0%, `pyramiding 0`,
`process_orders_on_close=false`.

FIDELITY:

* Converter-appended order block (PINE_SEMANTICS 1.17): the file declares
  `indicator()` and the trailing `if` / `else if` entry pair is what the tool
  added. The port reproduces that block's actual behaviour -- enter on the
  gated cross, never exit.
* NO exit call exists in the source, not even a commented-out one, so
  `source_reproduce_stops` is False and a position is only ever ended by the
  opposite entry reversing it.
* No `? -1 : 0` construct is present anywhere in this file, so the 1.17
  integer-truthiness trap does not apply; `cross_UP_A` / `cross_DN_B` are plain
  bools and are used as bare conditions, exactly as written.
* `request.security` (PINE_SEMANTICS 2.1) is NOT modelled by the shared layer,
  and this port does not resample either. On the source's own default
  (`res = ""` == the chart's timeframe) the call is the identity, so computing
  `fast_ma` / `slow_ma` / `signal` on the chart series reproduces it exactly.
  A NON-DEFAULT `res` is NOT reproduced: the port would still compute on the
  chart frame. `res` is carried in `source_defaults` for provenance only; do
  not read its presence as MTF support.
* `sma_source` / `sma_signal` are string inputs whose source options are
  `"EMA"` (default) and `"SMA"`; the port branches on the parameter value the
  same way the source's ternary does, so an override to `"SMA"` picks
  `pine_sma` for that line.
* `src` is `input.source(close, "Source")`; it is resolved through
  `pine_ta.pine_source` so the source's other options (hl2, hlc3, ...) work if
  overridden, and its default `close` is what the source uses.
* `hist`, the `var bool histA_IsUp` colour-state block, `trend_up` /
  `trend_dn`, `trend_col`, `bgcolor`, `barcolor`, `plot`, `hline` and the four
  `alert()` calls are display/alert-only: none of them reaches an order, and
  none is reproduced. `alert_Long` / `alert_Short` gate only `alert()` calls
  and are therefore not carried.
* `cross_UP` / `cross_DN` (the ungated forms) exist in the source but reach
  only `bgcolor` and `alert()`; the appended block uses the `_A` / `_B` forms.
  Both are computed here because the `_A` / `_B` forms are written as
  expansions of them in the source.
* Pine treats an na comparison as false, so the first bar (whose `signal[1]` /
  `macd[1]` are na) cannot fire a cross; numpy/pandas comparisons against NaN
  are also false, which reproduces it. With the default EMA settings neither
  series is na after bar 0 anyway.
* `pine_ema` seeds with the first observation and does not advance on na -- a
  modelled choice, not a certified one (PINE_SEMANTICS 3.1); TradingView does
  not publish its seeding rule.
* The `/*backtest` header declares `period: 10m` on Futures_Binance BTC_USDT,
  so `timeframe` is "10m"; `basePeriod: 1m` is the FMZ backtester's own fill
  granularity, not the strategy's period.
* No `barstate.isrealtime` branch, no repainting, no `strategy.risk.*` rule.
* Leverage, margin, liquidation, funding and the venue's contract-step
  rounding of order quantities are not modelled.
"""
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase


def _pine_ma(source, length, ma_type):
    """`sma_source == "SMA" ? ta.sma(src, len) : ta.ema(src, len)`."""
    if str(ma_type) == "SMA":
        return ta.pine_sma(source, length)
    return ta.pine_ema(source, length)


class SMCmMacdCustomIndicatorMultipleTimeFrameV2_ddb06d(PinePortBase, IStrategy):
    source_id = "SM_ddb06dd9f076f1bc"
    source_file = "CM-MACD-Custom-Indicator-Multiple-Time-Frame-V2.md"
    timeframe = "10m"
    can_short = True
    source_defaults: dict = {
        # `res = input.timeframe("", "Indicator TimeFrame")` -- "" means the
        # chart's timeframe. Carried for provenance; see FIDELITY.
        "res": "",
        "fast_length": 12,
        "slow_length": 26,
        "src": "close",
        "signal_length": 5,
        "sma_source": "EMA",
        "sma_signal": "EMA",
        # The two entry gates are bool inputs defaulting to true.
        "alert_Long_A": True,
        "alert_Short_B": True,
    }
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_reproduce_stops = False
    source_fidelity_notes = [
        "Converter-appended order block (PINE_SEMANTICS 1.17): the file declares "
        "indicator() and the trailing if / else-if entry pair is what the tool "
        "added. The port reproduces that block's actual behaviour -- enter on "
        "the gated MACD cross, never exit.",
        "NO exit call exists in the source, not even a commented-out "
        "strategy.exit, so source_reproduce_stops is False and a position is "
        "only ever ended by the opposite entry reversing it.",
        "No `? -1 : 0` construct is present, so the 1.17 integer-truthiness "
        "trap does not apply; cross_UP_A / cross_DN_B are plain bools used as "
        "bare conditions, exactly as written. if / else-if order (Enter Long "
        "first) is preserved in pine_script.",
        "request.security (PINE_SEMANTICS 2.1) is not modelled and is not "
        "resampled here. res = input.timeframe(\"\") is the EMPTY string, which "
        "Pine reads as the chart's timeframe, so on the source's own default "
        "all three request.security calls are the identity and computing on "
        "the chart series reproduces them exactly. A NON-DEFAULT res is NOT "
        "reproduced -- res is carried in source_defaults for provenance only.",
        "sma_source / sma_signal are string inputs with options EMA (default) "
        "and SMA; the port branches on the parameter just as the source's "
        "ternary does.",
        "src = input.source(close) is resolved through pine_ta.pine_source so "
        "the source's other options work if overridden; the default is close.",
        "hist, the var bool histA_IsUp/histA_IsDown/histB_* colour-state block, "
        "trend_up/trend_dn, trend_col, bgcolor, barcolor, plot, hline and the "
        "four alert() calls are display/alert-only and are not reproduced. "
        "alert_Long / alert_Short gate only alert() calls and are not carried; "
        "alert_Long_A / alert_Short_B DO gate the entries and are.",
        "cross_UP / cross_DN exist in the source but reach only bgcolor and "
        "alert(); the appended block uses the gated _A / _B forms, both of "
        "which are computed here.",
        "Pine treats an na comparison as false, so bar 0 (signal[1] / macd[1] "
        "na) cannot fire; NaN comparisons are false in numpy/pandas too.",
        "pine_ema seeds with the first observation and does not advance on na "
        "-- a modelled choice (PINE_SEMANTICS 3.1), not a certified one.",
        "/*backtest declares period: 10m on Futures_Binance BTC_USDT; "
        "basePeriod: 1m is the FMZ backtester's fill granularity, not the "
        "strategy's period.",
        "No barstate.isrealtime branch, no repainting, no strategy.risk.* rule.",
        "Leverage, margin, liquidation, funding and the venue's contract-step "
        "rounding of order quantities are not modelled.",
    ]

    def pine_indicators(self, dataframe, params):
        src = ta.pine_source(dataframe, str(params["src"]))
        fast_ma = _pine_ma(src, int(params["fast_length"]), params["sma_source"])
        slow_ma = _pine_ma(src, int(params["slow_length"]), params["sma_source"])

        macd = fast_ma - slow_ma
        signal = _pine_ma(macd, int(params["signal_length"]), params["sma_signal"])
        hist = macd - signal

        # cross_UP = signal[1] >= macd[1] and signal < macd
        cross_up = (signal.shift(1) >= macd.shift(1)) & (signal < macd)
        # cross_DN = signal[1] <= macd[1] and signal > macd
        cross_dn = (signal.shift(1) <= macd.shift(1)) & (signal > macd)
        # cross_UP_A = cross_UP and macd > 0 ; cross_DN_B = cross_DN and macd < 0
        cross_up_a = (cross_up & (macd > 0)).fillna(False)
        cross_dn_b = (cross_dn & (macd < 0)).fillna(False)

        dataframe["pine_macd"] = macd
        dataframe["pine_macd_signal"] = signal
        dataframe["pine_macd_hist"] = hist
        dataframe["pine_cross_up"] = cross_up.fillna(False).to_numpy()
        dataframe["pine_cross_dn"] = cross_dn.fillna(False).to_numpy()
        dataframe["pine_long_condition"] = cross_up_a.to_numpy()
        dataframe["pine_short_condition"] = cross_dn_b.to_numpy()
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "macd": dataframe["pine_macd"].to_numpy(),
            "macd_signal": dataframe["pine_macd_signal"].to_numpy(),
            "cross_up": dataframe["pine_cross_up"].to_numpy(),
            "cross_dn": dataframe["pine_cross_dn"].to_numpy(),
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
            "alert_Long_A": bool(params["alert_Long_A"]),
            "alert_Short_B": bool(params["alert_Short_B"]),
        }

    def pine_script(self, broker, i, ctx):
        # if alert_Long_A and cross_UP_A
        #     strategy.entry("Enter Long", strategy.long)
        # else if alert_Short_B and cross_DN_B
        #     strategy.entry("Enter Short", strategy.short)
        if ctx["alert_Long_A"] and ctx["long_condition"][i]:
            broker.entry("Enter Long", "long")
        elif ctx["alert_Short_B"] and ctx["short_condition"][i]:
            broker.entry("Enter Short", "short")
