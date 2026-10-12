"""Port of sources/SM_91f5b2e4a2c430a4.pine (24小时量价结合斐波那契回调交叉均线交易策略-24-Hour-Volume-Price-Fibonacci-Retracement-MA-Cross-Trading-Strategy.md).

Pine v5. A daily SMA(14)/SMA(28) crossover system dressed with a running
high/low, four Fibonacci retracement levels and a 20-period volume average:

    startTime = timestamp(year, month, dayofmonth, 0, 0)
    endTime   = timestamp(year, month, dayofmonth, 23, 59)
    var float dayHigh = na
    var float dayLow  = na
    if (time >= startTime and time <= endTime)
        dayHigh := na(dayHigh) ? high : math.max(dayHigh, high)
        dayLow  := na(dayLow)  ? low  : math.min(dayLow, low)
    fibRetrace1..4 = dayLow + (dayHigh - dayLow) * 0.236 / 0.382 / 0.618 / 0.786
    volumeMa = ta.sma(volume, 20)
    longCondition  = ta.crossover(ta.sma(close, 14), ta.sma(close, 28))   -> entry("My Long Entry Id", long)
    shortCondition = ta.crossunder(ta.sma(close, 14), ta.sma(close, 28))  -> entry("My Short Entry Id", short)

Only the two SMA-cross markets orders; the high/low, the Fibonacci levels and
the volume average are `plot()`ed and then never read by any `strategy.*` call,
so they are computed here for completeness but cannot move a trade.

The `/*backtest` header declares `period: 1d` on `Binance` SOL_USDT, so
`timeframe` is "1d". `strategy()` declares no properties at all beyond the title
and `overlay=true`, so every trade property is Pine's documented default:
initial capital 1000000 USD, `default_qty_type` fixed, `default_qty_value` 1,
commission 0%, pyramiding 0.

FIDELITY:

* PROSE vs CODE. The prose describes "24小时价格区间追踪: 系统持续监控并更新每个
  交易日内的最高价和最低价" / "monitors and updates the highest and lowest prices
  within each trading day". The code has NO daily reset: `dayHigh` / `dayLow` are
  never re-seeded at a day boundary, so they are a RUNNING maximum of `high` and
  running minimum of `low` from the first bar the source ever evaluates -- an
  all-time high/low so far, not a 24-hour range. The code wins, and the running
  high/low is what the port reproduces. This also means the four Fibonacci levels
  drift to the extremes of the whole series rather than of the day.
* The session gate is inert on this timeframe. `timestamp(year, month,
  dayofmonth, 0, 0)` is the current bar's own date at 00:00 in the exchange time
  zone, which for a daily bar IS the bar's open time, so
  `time >= startTime and time <= endTime` holds on every bar. It is still
  evaluated bar by bar rather than short-circuited to True, so a frame whose
  bars do not open at midnight would gate exactly as the source does.
* Time zone: `year` / `month` / `dayofmonth` / `timestamp()` are exchange-time
  zone in Pine. The local data is UTC and Binance is UTC, so no offset is
  applied; a source on a non-UTC exchange would need one.
* `volumeMa`, the four `fibRetrace*`, `dayHigh`, `dayLow` and the `bgcolor(...)`
  call are chart output with no trade effect. The prose's claim that volume and
  the Fibonacci levels "validate price action" ("利用成交量和斐波那契水平来验证
  价格走势的有效性") is not in the code: no order condition reads them.
* `ta.sma` is na until `length` bars have elapsed (pine_ta.pine_sma), so the
  crossover pair cannot fire before bar 28.
"""
import pandas as pd
from freqtrade.strategy import IStrategy

import pine_ta as ta
from pine_port_base import PinePortBase

_FIB_RATIOS = (0.236, 0.382, 0.618, 0.786)


class SMVolumeFibonacci_91f5b2(PinePortBase, IStrategy):
    source_id = "SM_91f5b2e4a2c430a4"
    source_file = (
        "24小时量价结合斐波那契回调交叉均线交易策略-24-Hour-Volume-Price-"
        "Fibonacci-Retracement-MA-Cross-Trading-Strategy.md"
    )
    timeframe = "1d"
    can_short = True
    source_defaults: dict = {}
    source_qty_type = "fixed"
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = [
        "PROSE/CODE DISAGREEMENT: the prose calls dayHigh/dayLow a per-day "
        "'24-hour' range, but the code never resets them at a day boundary. They "
        "are a RUNNING max of high / min of low from the first evaluated bar, so "
        "the Fibonacci levels are drawn off the all-time extreme, not the day's. "
        "The code is reproduced as written.",
        "The session gate `time >= startTime and time <= endTime` is inert on a "
        "daily series: `timestamp(year, month, dayofmonth, 0, 0)` equals the "
        "daily bar's own open time. It is evaluated per bar, not assumed true.",
        "`ta.sma` returns na until `length` bars elapse (pine_ta.pine_sma), so no "
        "crossover can fire before bar 28; kept as-is.",
        "dayHigh, dayLow, the four fibRetrace levels, volumeMa and bgcolor are "
        "chart output only -- no strategy.* call reads them, so they place no "
        "orders. The prose's 'volume and Fibonacci validate the price action' is "
        "not present in the code.",
        "Pine's `year`/`month`/`dayofmonth`/`timestamp()` are exchange-time zone; "
        "modelled as UTC (Binance and the local data are UTC).",
        "`strategy()` declares no trade properties, so Pine's documented defaults "
        "apply: fixed qty 1, commission 0%, pyramiding 0, capital 1000000 USD. "
        "The MA lengths (14/28), the volume length (20) and the fib ratios are "
        "literals in the source, not `input()`s, and stay literals here.",
    ]

    def pine_indicators(self, dataframe, params):
        index = pd.DatetimeIndex(dataframe.index)
        # startTime = timestamp(year, month, dayofmonth, 0, 0)
        # endTime   = timestamp(year, month, dayofmonth, 23, 59)
        day_start = index.normalize()
        day_end = day_start + pd.Timedelta(hours=23, minutes=59)
        in_session = (index >= day_start) & (index <= day_end)

        # `var float dayHigh = na` / `dayLow`, updated only inside the session
        # gate and never reset: a running extreme, carried forward on any bar
        # the gate excludes (`where` blanks those bars, `cummax`/`cummin` skip
        # the blanks and leave the previous extreme in place, and stay na until
        # the first bar the gate admits).
        day_high = dataframe["high"].where(in_session).cummax()
        day_low = dataframe["low"].where(in_session).cummin()
        dataframe["day_high"] = day_high
        dataframe["day_low"] = day_low

        span = day_high - day_low
        for number, ratio in enumerate(_FIB_RATIOS, start=1):
            dataframe[f"fib_retrace_{number}"] = day_low + span * ratio

        dataframe["volume_ma"] = ta.pine_sma(dataframe["volume"], 20)

        close = dataframe["close"]
        sma_fast = ta.pine_sma(close, 14)
        sma_slow = ta.pine_sma(close, 28)
        dataframe["sma_14"] = sma_fast
        dataframe["sma_28"] = sma_slow
        dataframe["pine_long_condition"] = ta.pine_crossover(sma_fast, sma_slow)
        dataframe["pine_short_condition"] = ta.pine_crossunder(sma_fast, sma_slow)
        return dataframe

    def pine_context(self, dataframe, params):
        return {
            "long_condition": dataframe["pine_long_condition"].to_numpy(),
            "short_condition": dataframe["pine_short_condition"].to_numpy(),
        }

    def pine_script(self, broker, i, ctx):
        # if (longCondition)
        #     strategy.entry("My Long Entry Id", strategy.long)
        if ctx["long_condition"][i]:
            broker.entry("My Long Entry Id", "long")
        # if (shortCondition)
        #     strategy.entry("My Short Entry Id", strategy.short)
        if ctx["short_condition"][i]:
            broker.entry("My Short Entry Id", "short")
