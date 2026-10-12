"""batch_012 port of 金叉死叉均线交易策略Golden-Cross-Death-Cross-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-23 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("XAU M15", overlay=true)\n\n// Define input parameters\nlong_length = input.int(64, title="Long MA Length")\nshort_length = input.int(1, title="Short MA Length")\ntrend_length = input.int(200, title="Trend MA Length")\n\n// Calculate moving averages\nlong_ma = ta.sma(close, long_length)\nshort_ma = ta.sma(close, short_length)\ntrend_ma = ta.sma(close, trend_length)\n\n// Plot moving averages on chart\nplot(long_ma, color=color.blue, title="Long MA")\nplot(short_ma, color=color.red, title="Short MA")\nplot(trend_ma, color=color.green, title="Trend MA")\n\n// Entry conditions\nenterLong = ta.crossover(long_ma, short_ma) and long_ma > trend_ma and short_ma > trend_ma\nenterShort = ta.crossunder(long_ma, short_ma) and long_ma < trend_ma and short_ma < trend_ma\n\nif (enterLong)\n    strategy.entry("Long", strategy.long)\n\nif (enterShort)\n    strategy.entry("Short", strategy.short)\n\n// Exit conditions\nexitLong = ta.crossunder(long_ma, short_ma)\nexitShort = ta.crossover(long_ma, short_ma)\n\nif (exitLong)\n    strategy.close("Long")\n\nif (exitShort)\n    strategy.close("Short")\n\n// Set stop loss and take profit levels\nlong_stop_loss_percentage = input(1, title="Long Stop Loss (%)") / 100\nlong_take_profit_percentage = input(3, title="Long Take Profit (%)") / 100\n\nshort_stop_loss_percentage = input(1, title="Short Stop Loss (%)") / 100\nshort_take_profit_percentage = input(3, title="Short Take Profit (%)") / 100\n\nstrategy.exit("Take Profit/Stop Loss", "Long", stop=close * (1 - long_stop_loss_percentage), limit=close * (1 + long_take_profit_percentage))\nstrategy.exit("Take Profit/Stop Loss", "Short", stop=close * (1 + short_stop_loss_percentage), limit=close * (1 - short_take_profit_percentage))\n\nplotshape(series=enterLong, title="Buy Entry", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.tiny)\nplotshape(series=enterShort, title="Sell Entry", location=location.abovebar, color=color.red, style=shape.triangledown, size=size.tiny)\n\n'

class SMGoldenCrossDeathCrossMovingAverageTradingStrategy56a048(PinePortBase, IStrategy):
    source_id = "SM_56a04834b3535912"
    source_file = '金叉死叉均线交易策略Golden-Cross-Death-Cross-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'long_length': 64, 'short_length': 1, 'trend_length': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
