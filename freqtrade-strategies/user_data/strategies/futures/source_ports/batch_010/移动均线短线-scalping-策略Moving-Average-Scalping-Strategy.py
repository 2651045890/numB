"""Source-faithful deep-assisted port of 移动均线短线-scalping-策略Moving-Average-Scalping-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_11b6761f(PinePortBase, IStrategy):
    source_file = '移动均线短线-scalping-策略Moving-Average-Scalping-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 10, 'fromYear': 2019, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", type = input.integer, minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 10, title = "From Day", type = input.integer, minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2019, title = "From Year", type = input.integer, minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'thruMonth', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Month", type = input.integer, minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'thruDay', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Day", type = input.integer, minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'thruYear', 'op': '=', 'expr': 'input(defval = 2112, title = "Thru Year", type = input.integer, minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'showDate', 'op': '=', 'expr': 'input(defval = true, title = "Show Date Range", type = input.bool)', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(thruYear, thruMonth, thruDay, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'movingaverage_signal', 'op': '=', 'expr': 'sma(close, input(9))', 'conditions': []}, {'mode': '', 'name': 'movingaverage_fast', 'op': '=', 'expr': 'sma(close, input(50))', 'conditions': []}, {'mode': '', 'name': 'movingaverage_slow', 'op': '=', 'expr': 'sma(close, input(200))', 'conditions': []}, {'mode': '', 'name': 'movingaverage_mid', 'op': '=', 'expr': 'sma(close, input(100))', 'conditions': []}, {'mode': '', 'name': 'bullish', 'op': '=', 'expr': 'crossover(movingaverage_signal, movingaverage_fast)', 'conditions': []}, {'mode': '', 'name': 'bearish', 'op': '=', 'expr': 'crossover(movingaverage_signal, movingaverage_slow)', 'conditions': []}, {'mode': '', 'name': 'Stop_loss', 'op': '=', 'expr': '((input (2))/100)', 'conditions': []}, {'mode': '', 'name': 'Take_profit', 'op': '=', 'expr': '((input (8))/100)', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - Stop_loss)', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + Take_profit)', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'true // create function "within window of time"'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="long", long = true, when = bullish and movingaverage_fast < movingaverage_mid and movingaverage_mid < movingaverage_slow and window())', 'conditions': [], 'statement': 'strategy.entry(id="long", long = true, when = bullish and movingaverage_fast < movingaverage_mid and movingaverage_mid < movingaverage_slow and window())'}, {'kind': 'close', 'call': 'strategy.close("long", when = bearish)', 'conditions': [], 'statement': 'strategy.close("long", when = bearish)'}]
    original_pine = '/*backtest\nstart: 2023-08-21 00:00:00\nend: 2023-09-20 00:00:00\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//strategy(shorttitle=\'Moving Average Scalper (by Coinrule)\',title=\'Moving Average Scalper\', overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n\n//Backtest dates\nfromMonth = input(defval = 1,    title = "From Month",      type = input.integer, minval = 1, maxval = 12)\nfromDay   = input(defval = 10,    title = "From Day",        type = input.integer, minval = 1, maxval = 31)\nfromYear  = input(defval = 2019, title = "From Year",       type = input.integer, minval = 1970)\nthruMonth = input(defval = 1,    title = "Thru Month",      type = input.integer, minval = 1, maxval = 12)\nthruDay   = input(defval = 1,    title = "Thru Day",        type = input.integer, minval = 1, maxval = 31)\nthruYear  = input(defval = 2112, title = "Thru Year",       type = input.integer, minval = 1970)\n\nshowDate  = input(defval = true, title = "Show Date Range", type = input.bool)\n\nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => true       // create function "within window of time"\n\n//MA inputs and calculations\nmovingaverage_signal = sma(close, input(9))\nmovingaverage_fast = sma(close, input(50))\nmovingaverage_slow = sma(close, input(200))\nmovingaverage_mid= sma(close, input(100))\n\n//Entry \nbullish = crossover(movingaverage_signal, movingaverage_fast)\n\nstrategy.entry(id="long", long = true, when = bullish and movingaverage_fast < movingaverage_mid and movingaverage_mid < movingaverage_slow and window())\n\n//Exit\n\nbearish = crossover(movingaverage_signal, movingaverage_slow)\n\n\nStop_loss= ((input (2))/100)\nTake_profit= ((input (8))/100)\n\nlongStopPrice  = strategy.position_avg_price * (1 - Stop_loss)\nlongTakeProfit = strategy.position_avg_price * (1 + Take_profit)\n\nstrategy.close("long", when = bearish)\n\n// close < longStopPrice or close > longTakeProfit and window())\n\n//PLOT\nplot(movingaverage_signal, color=color.black, linewidth=2 )\nplot(movingaverage_fast, color=color.orange, linewidth=2)\nplot(movingaverage_slow, color=color.purple, linewidth=2)\nplot(movingaverage_mid, color=color.blue, linewidth=2)'

    def pine_indicators(self, dataframe, params):
        self._semantic_rt = SemanticRuntime(dataframe, params, self.pine_assignments, self.pine_user_functions)
        return self._semantic_rt.materialize()

    def pine_context(self, dataframe, params):
        # Keep the complete, strategy-specific semantic program available to the
        # broker replay layer.  Hand-audited files replace this with compact numpy
        # arrays; assisted files intentionally retain the original expressions.
        return {'dataframe': dataframe, 'params': dict(params), 'orders': self.pine_orders,
                'assignments': self.pine_assignments, 'functions': self.pine_user_functions,
                'source': self.original_pine}

    def pine_script(self, broker, i, ctx):
        # The order program is preserved explicitly above.  Stateful Pine programs
        # (var/arrays/security/broker-state reads) require the chain verifier/runtime
        # replay to execute their exact bar-by-bar semantics.  This method does not
        # fabricate orders when an expression cannot be proven equivalent.
        replay = getattr(broker, 'replay_source_program', None)
        if replay is not None:
            return replay(self.original_pine, i, ctx)
        return None
