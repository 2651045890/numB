"""batch_012 port of 高低突破回测策略High-Low-Breaker-Backtest-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-25 00:00:00\nend: 2023-11-26 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("High/Low Breaker Backtest 1.0", overlay=true, initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, max_bars_back=700)\n\n// Strategy Settings\ntakeProfitPercentageLong = input(.1, title=\'Take Profit Percentage Long\', type=float)/100\nstopLossPercentageLong = input(0.15, title=\'Stop Loss Percentage Long\', type=float)/100\ntakeProfitPercentageShort = input(.1, title=\'Take Profit Percentage Short\', type=float)/100\nstopLossPercentageShort = input(0.15, title=\'Stop Loss Percentage Short\', type=float)/100\n\n\ncandlesBack = input(title="Number of candles back",  defval=50)\nuseHighAndLows =  input(true, title="Use high and lows (uncheck to use close)", defval=true)\nlastBarsBackMinimum =  input(title="Number of candles back to ignore for last high/low",  defval=30)\nshowHighsAndLows = input(true, title="Show high/low lines", defval=true)\n\ngetIndexOfLowestInSeries(series, period) => \n    index = 0\n    current = series\n    for i = 1 to period\n        if series[i] <= current\n            index := i\n            current := series[i]\n    index\n\ngetIndexOfHighestInSeries(series, period) => \n    index = 0\n    current = series\n    for i = 1 to period\n        if series[i] >= current\n            index := i\n            current := series[i]\n    index\n\nindexOfHighestInRange = getIndexOfHighestInSeries(useHighAndLows ? high : close, candlesBack)\nindexOfLowestInRange = getIndexOfLowestInSeries(useHighAndLows ? low : close, candlesBack)\n\nmax = useHighAndLows ? high[indexOfHighestInRange] : close[indexOfHighestInRange]\nmin = useHighAndLows ? low[indexOfLowestInRange] : close[indexOfLowestInRange]\n\nbarsSinceLastHigh = indexOfHighestInRange\nbarsSinceLastLow = indexOfLowestInRange\n\nisNewHigh = (useHighAndLows ? high > max[1] : close > max[1]) and (barsSinceLastHigh[1] + 1 > lastBarsBackMinimum)\nisNewLow = (useHighAndLows ? low < min[1] : close < min[1]) and (barsSinceLastLow[1] + 1 > lastBarsBackMinimum)\n\nalertcondition(condition=isNewHigh, title="New High", message="Last High Broken")\nalertcondition(condition=isNewLow, title="New Low", message="Last Low Broken")\n\nif high > max \n    max := high\n    barsSinceLastHigh := 0\n\nif low < min\n    min := low\n    barsSinceLastLow := 0 \n\nplot( showHighsAndLows ? max : na, color=red, style=line, title="High", linewidth=3)\nplot( showHighsAndLows ? min : na, color=green, style=line, title="Low", linewidth=3)\n\n// Strategy Entry/Exit Logic\ngoLong =isNewHigh\nlongStopLevel = strategy.position_avg_price * (1 - stopLossPercentageLong)\nlongTakeProfitLevel = strategy.position_avg_price * (1 + takeProfitPercentageLong)\n\ngoShort = isNewLow\nshortStopLevel = strategy.position_avg_price * (1 + stopLossPercentageShort)\nshortTakeProfitLevel = strategy.position_avg_price * (1 - takeProfitPercentageShort)\n\nstrategy.entry("Long", strategy.long, when=goLong)\nstrategy.exit("Long Exit", "Long", stop=longStopLevel, limit=longTakeProfitLevel)\n\nstrategy.entry("Short", strategy.short, when=goShort)\nstrategy.exit("Short Exit", "Short", stop=shortStopLevel, limit=shortTakeProfitLevel)\n        \nplot(goShort ? shortStopLevel : na, color=yellow, style=linebr, linewidth=2)\nplot(goShort ? shortTakeProfitLevel : na, color=blue, style=linebr, linewidth=2)\nplot(goLong ? longStopLevel : na, color=yellow, style=linebr, linewidth=2)\nplot(goLong ? longTakeProfitLevel : na, color=blue, style=linebr, linewidth=2)\n\n'

class SMHighLowBreakerBacktestStrategyf5ff86(PinePortBase, IStrategy):
    source_id = "SM_f5ff862ce3ecb154"
    source_file = '高低突破回测策略High-Low-Breaker-Backtest-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'candlesBack': 50, 'useHighAndLows': True, 'lastBarsBackMinimum': 30, 'showHighsAndLows': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
