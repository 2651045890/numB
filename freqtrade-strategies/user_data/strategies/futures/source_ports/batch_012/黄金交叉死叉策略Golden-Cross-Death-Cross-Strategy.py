"""batch_012 port of 黄金交叉死叉策略Golden-Cross-Death-Cross-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-10 00:00:00\nend: 2023-10-10 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//strategy("Golden X BF Strategy", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.0)\n\n/////////////// Time Frame ///////////////\ntestStartYear = input(2010, "Backtest Start Year") \ntestStartMonth = input(1, "Backtest Start Month")\ntestStartDay = input(1, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay, 0, 0)\n\ntestStopYear = input(2019, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay, 0, 0)\n\ntestPeriod() =>  true\n\n///////////// MA Params /////////////\nsource1 = input(title="MA Source 1", defval=close)\nmaType1 = input(title="MA Type 1", defval="sma", options=["sma", "ema", "swma", "wma"])\nlength1 = input(title="MA Length 1", defval=50)\n\nsource2 = input(title="MA Source 2", defval=close)\nmaType2 = input(title="MA Type 2", defval="sma", options=["sma", "ema", "swma", "wma"])\nlength2 = input(title="MA Length 2", defval=200)\n\n///////////// Get MA Function /////////////\ngetMAType(maType, sourceType, maLen) => \n    res = sma(close, 1)\n    \n    if maType == "ema"\n        res := ema(sourceType, maLen)\n    if maType == "sma"\n        res := sma(sourceType, maLen)\n    if maType == "swma"\n        res := swma(sourceType)\n    if maType == "wma"\n        res := wma(sourceType, maLen)\n    res\n    \n///////////// MA /////////////\nfastMA = getMAType(maType1, source1, length1)\nslowMA = getMAType(maType2, source2, length2)\n\nlong = crossover(fastMA, slowMA)\nshort = crossunder(fastMA, slowMA)\n\n/////////////// Plotting /////////////// \ncheckColor() => fastMA > slowMA\ncolCheck = checkColor() ? color.lime : color.red\np1 = plot(fastMA, color = colCheck, linewidth=1)\np2 = plot(slowMA, color = colCheck, linewidth=1)\nfill(p1, p2, color = checkColor() ? color.lime : color.red)\nbgcolor(long ? color.lime : short ? color.red : na, transp=20)\n\n/////////////// Execution /////////////// \nif testPeriod()\n    strategy.entry("Long", strategy.long, when=long)\n    strategy.entry("Short", strategy.short, when=short)\n'

class SMGoldenCrossDeathCrossStrategy4f8942(PinePortBase, IStrategy):
    source_id = "SM_4f89427c4d360843"
    source_file = '黄金交叉死叉策略Golden-Cross-Death-Cross-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'testStartYear': 2010, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2019, 'testStopMonth': 12, 'testStopDay': 31, 'source1': 'close', 'maType1': 'sma', 'length1': 50, 'source2': 'close', 'maType2': 'sma', 'length2': 200}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
