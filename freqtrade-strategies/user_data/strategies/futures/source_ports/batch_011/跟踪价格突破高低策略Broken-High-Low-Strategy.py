"""batch_011 port of 跟踪价格突破高低策略Broken-High-Low-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-15 00:00:00\nend: 2023-12-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Broken High/Low Strategy", overlay=true, initial_capital = 5000, default_qty_value = 25, pyramiding = 10, default_qty_type= strategy.percent_of_equity)\n\nuseEMAForStop = input.bool(false, \'Use trail stop EMA\', group = \'Exit strategy\')\ntrailStopMALength = input(8, \'Trail stop EMA length\', group = \'Exit strategy\')\n\nfastMALength = input(5 , \'Fast MA length\', group = \'Trend strength\')\nfastEMAEnabled = input.bool(false, \'Fast EMA enabled (default is SMA)\', group = \'Trend strength\')\n\nslowMALength = input(10, \'Slow MA length\', group = \'Trend strength\')\nslowEMAEnabled = input.bool(false, \'Slow EMA enabled (default is SMA)\', group = \'Trend strength\')\n\nignoreSlowMA = input.bool(false, \'Use fast MA for trend ignoring slow MA\', group = \'Trend strength\')\n\nuseOpposingBarAsExit = input.bool(false, \'Using opposing bar as exit\', group = \'Exit strategy\')\nsecondEntryEnabled = input.bool(false, \'Second bar that eliminates opposing bar for entry\', group = \'Trend strength\')\n\nlongsEnabled = input.bool(true, \'Enable longs\', group = \'Trade settings\')\nshortsEnabled = input.bool(true, \'Enable shorts\', group = \'Trade settings\')\n\nfastMA = fastEMAEnabled ? ta.ema(close, fastMALength) : ta.sma(close, fastMALength)\nslowMA = slowEMAEnabled ? ta.ema(close, slowMALength) : ta.sma(close, slowMALength)\n\nFromMonth=input.int(defval=1,title="FromMonth",minval=1,maxval=12, group = \'Time filters\')\nFromDay=input.int(defval=1,title="FromDay",minval=1,maxval=31, group = \'Time filters\')\nFromYear=input.int(defval=1990,title="FromYear",minval=1900, group = \'Time filters\')\nToMonth=input.int(defval=1,title="ToMonth",minval=1,maxval=12, group = \'Time filters\')\nToDay=input.int(defval=1,title="ToDay",minval=1,maxval=31, group = \'Time filters\')\nToYear=input.int(defval=9999,title="ToYear",minval=2017, group = \'Time filters\')\nstart=timestamp(FromYear,FromMonth,FromDay,00,00)\nfinish=timestamp(ToYear,ToMonth,ToDay,23,59)\nwindow()=>time>=start and time<=finish?true:false\nafterStartDate = time >= start and time<=finish?true:false\ncloseTradesEOD = input.bool(false, \'Close trades end of day\', group = \'Time filters\')\n\ntrailStopMA = ta.ema(close, trailStopMALength)\n\nisGreenCandle = close > open\nisRedCandle = close < open\nisBrokenHigh = close > open[1]\nisPriorCandleRed = close[1] < open[1]\nisPriorPriorCandleRed = close[2] < open[2]\nisPriorPriorCandleGreen = close[2] > open[2]\nisPriorCandleGreen = close[1] > open[1]\nisBrokenLow = close < open[1]\n\nisPriorRedCandleBroken = isGreenCandle and isPriorCandleRed and isBrokenHigh\nisPriorGreenCandleBroken = isRedCandle and isPriorCandleGreen and isBrokenLow\n\nisPriorPriorRedCandleBroken = secondEntryEnabled and not isPriorRedCandleBroken and isGreenCandle and isPriorPriorCandleRed ? close > open[2] : false\nisPriorPriorGreenCandleBroken = secondEntryEnabled and not isPriorGreenCandleBroken and isRedCandle and isPriorPriorCandleGreen ? close < open[2] : false\n\nlongOpenCondition = (isPriorRedCandleBroken or isPriorPriorRedCandleBroken) and afterStartDate and (ignoreSlowMA ? close > fastMA : fastMA > slowMA) and longsEnabled\nlongCloseCondition = useOpposingBarAsExit ? isRedCandle : ta.crossunder(close, fastMA)\nlongCloseCondition := useEMAForStop ? ta.crossunder(close, trailStopMA) : longCloseCondition\n\nshortOpenCondition = (isPriorGreenCandleBroken or isPriorPriorGreenCandleBroken) and afterStartDate and (ignoreSlowMA ? close < fastMA : fastMA < slowMA) and shortsEnabled\nshortCloseCondition = useOpposingBarAsExit ? isGreenCandle : ta.crossover(close, fastMA)\nshortCloseCondition := useEMAForStop ? ta.crossover(close, trailStopMA) : shortCloseCondition\n\nif (longOpenCondition)\n    strategy.entry("Long Entry", strategy.long)\n\nif (longCloseCondition)\n    strategy.close(\'Long Entry\', \'Long Exit\')\n\nif (shortOpenCondition)\n    strategy.entry("Short Entry", strategy.long)\n\nif (shortCloseCondition)\n    strategy.close(\'Short Entry\', \'Short Exit\')\n\nif (closeTradesEOD and hour >= 14 and minute >= 30)\n    strategy.close_all("EOD")\n\nplot(useEMAForStop ? trailStopMA : na, linewidth = 2, color = color.red)\nplot(fastMA)\nplot(ignoreSlowMA ? na : slowMA, linewidth = 4)'

class SM412D0D9877341CE6(PinePortBase, IStrategy):
    source_id = "SM_412d0d9877341ce6"
    source_file = '跟踪价格突破高低策略Broken-High-Low-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'useEMAForStop': False, 'trailStopMALength': 8, 'fastMALength': 5, 'fastEMAEnabled': False, 'slowMALength': 10, 'slowEMAEnabled': False, 'ignoreSlowMA': False, 'useOpposingBarAsExit': False, 'secondEntryEnabled': False, 'longsEnabled': True, 'shortsEnabled': True, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 1990, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999, 'closeTradesEOD': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 25
    source_commission_percent = 0
    source_pyramiding = 10
    source_initial_capital = 5000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
