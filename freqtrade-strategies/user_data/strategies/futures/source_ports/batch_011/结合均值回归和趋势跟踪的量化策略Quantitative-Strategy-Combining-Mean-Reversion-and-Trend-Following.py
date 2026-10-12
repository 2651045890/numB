"""batch_011 port of 结合均值回归和趋势跟踪的量化策略Quantitative-Strategy-Combining-Mean-Reversion-and-Trend-Following.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-07 00:00:00\nend: 2023-04-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © I11L\n\n//@version=5\nstrategy("Mean Reversion and Trendfollowing", overlay=true, pyramiding=1, default_qty_value=100000, initial_capital=100000, default_qty_type=strategy.cash, process_orders_on_close=false, calc_on_every_tick=false)\n\n// Input for the starting date\nstart_date = input(timestamp("1 Feb 2000 12:00"), title="Starting Date")\nenableMeanReversion = input.bool(true)\nenableTrendfollowing = input.bool(true)\ntrendPositionFactor = input.float(1)\nmeanReversionPositionFactor = input.float(0.5)\n\n// Convert the input string to a timestamp\nstart_ts = timestamp(year(start_date), month(start_date), dayofmonth(start_date), 0, 0)\n\n// Check if the current bar\'s time is greater than or equal to the start timestamp\nstart_condition = time >= start_ts\n\nvar tradeOrigin = ""\n\nsma200 = ta.sma(close,200)\nrsi2 = ta.rsi(close,2)\n\nisMeanReversionMode = close < sma200 or not(enableTrendfollowing)\nisTrendfollowingMode = close > sma200 or not(enableMeanReversion)\n\nisRsiBuy = rsi2 < 20 and enableMeanReversion\nisRsiClose = rsi2 > 80 and enableMeanReversion\n\nisSmaBuy = close > sma200 and enableTrendfollowing\nisSmaClose = close < sma200 * 0.95 and enableTrendfollowing\n\nisBuy = (isMeanReversionMode and isRsiBuy) or (isTrendfollowingMode and isSmaBuy)\n\npositionSizeFactor = isSmaBuy ? trendPositionFactor : meanReversionPositionFactor\n\n// Only execute the strategy after the starting date\nif (start_condition)\n    if (isBuy and strategy.opentrades == 0)\n        tradeOrigin := isSmaBuy ? "SMA" : "RSI"\n        strategy.entry("My Long Entry Id", strategy.long, qty=(strategy.equity / close) * positionSizeFactor, comment=str.tostring(positionSizeFactor))\n    isClose = tradeOrigin == "SMA" ? isSmaClose : isRsiClose\n    if (isClose)\n        strategy.exit("Exit", limit = close)\n\nplot(sma200)\nplot(sma200 * 0.95, color=color.orange)'

class SM87E3EC3785BCA8DF(PinePortBase, IStrategy):
    source_id = "SM_87e3ec3785bca8df"
    source_file = '结合均值回归和趋势跟踪的量化策略Quantitative-Strategy-Combining-Mean-Reversion-and-Trend-Following.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'enableMeanReversion': True, 'enableTrendfollowing': True, 'trendPositionFactor': 1, 'meanReversionPositionFactor': 0.5}
    source_qty_type = 'cash'
    source_qty_value = 100000
    source_commission_percent = 0
    source_pyramiding = 1
    source_initial_capital = 100000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
