"""Source-faithful deep-assisted port of 海龟突破EMA交叉策略Turtle-Breakout-EMA-Cross-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_9c675411(PinePortBase, IStrategy):
    source_file = '海龟突破EMA交叉策略Turtle-Breakout-EMA-Cross-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'length1': 10, 'length2': 20, 'lotSize': 1, 'takeProfitLevel': 600, 'stopLossLevel': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length1', 'op': '=', 'expr': 'input.int(10, title="Length EMA Short", minval=1)', 'conditions': []}, {'mode': '', 'name': 'length2', 'op': '=', 'expr': 'input.int(20, title="Length EMA Long", minval=1)', 'conditions': []}, {'mode': '', 'name': 'lotSize', 'op': '=', 'expr': 'input.int(1, title="Lot Size", minval=1)', 'conditions': []}, {'mode': '', 'name': 'takeProfitLevel', 'op': '=', 'expr': 'input.int(600, title="Take Profit Level", minval=1)', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'input.int(200, title="Stop Loss Level", minval=1)', 'conditions': []}, {'mode': '', 'name': 'ema1', 'op': '=', 'expr': 'ta.ema(close, length1)', 'conditions': []}, {'mode': '', 'name': 'ema2', 'op': '=', 'expr': 'ta.ema(close, length2)', 'conditions': []}, {'mode': 'var', 'name': 'lastCrossTime', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'lastCrossTime', 'op': ':=', 'expr': 'timenow', 'conditions': ['ta.crossover(ema1, ema2)']}, {'mode': '', 'name': 'lastCrossTime', 'op': ':=', 'expr': 'timenow', 'conditions': ['ta.crossunder(ema1, ema2)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ta.crossover(ema1, ema2)'}, {'indent': 4, 'statement': 'if na(lastCrossTime)'}, {'indent': 0, 'statement': 'if ta.crossunder(ema1, ema2)'}, {'indent': 4, 'statement': 'if na(lastCrossTime)'}]
    pine_orders = [{'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['ta.crossover(ema1, ema2)', 'na(lastCrossTime)'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': "strategy.entry('Buy Order', strategy.long, qty=lotSize)", 'conditions': ['ta.crossover(ema1, ema2)'], 'statement': "strategy.entry('Buy Order', strategy.long, qty=lotSize)"}, {'kind': 'exit', 'call': "strategy.exit('Exit Buy', 'Buy Order', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)", 'conditions': ['ta.crossover(ema1, ema2)'], 'statement': "strategy.exit('Exit Buy', 'Buy Order', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)"}, {'kind': 'close_all', 'call': 'strategy.close_all()', 'conditions': ['ta.crossunder(ema1, ema2)', 'na(lastCrossTime)'], 'statement': 'strategy.close_all()'}, {'kind': 'entry', 'call': "strategy.entry('Sell Order', strategy.short, qty=lotSize)", 'conditions': ['ta.crossunder(ema1, ema2)'], 'statement': "strategy.entry('Sell Order', strategy.short, qty=lotSize)"}, {'kind': 'exit', 'call': "strategy.exit('Exit Sell', 'Sell Order', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)", 'conditions': ['ta.crossunder(ema1, ema2)'], 'statement': "strategy.exit('Exit Sell', 'Sell Order', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)"}]
    original_pine = '/*backtest\nstart: 2023-10-30 00:00:00\nend: 2023-11-06 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'XXXquang\', overlay=true)\n\n// Sử dụng hàm input.int() và input.float() để tạo các trường nhập liệu với giới hạn giá trị\nlength1 = input.int(10, title="Length EMA Short", minval=1)\nlength2 = input.int(20, title="Length EMA Long", minval=1)\nlotSize = input.int(1, title="Lot Size", minval=1)\n\ntakeProfitLevel = input.int(600, title="Take Profit Level", minval=1)\nstopLossLevel = input.int(200, title="Stop Loss Level", minval=1)\n\nema1 = ta.ema(close, length1)\nema2 = ta.ema(close, length2)\n\nvar float lastCrossTime = na\n\nif ta.crossover(ema1, ema2)\n    if na(lastCrossTime)\n        strategy.close_all()\n    strategy.entry(\'Buy Order\', strategy.long, qty=lotSize)\n    strategy.exit(\'Exit Buy\', \'Buy Order\', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)\n    lastCrossTime := timenow\n\nif ta.crossunder(ema1, ema2)\n    if na(lastCrossTime)\n        strategy.close_all()\n    strategy.entry(\'Sell Order\', strategy.short, qty=lotSize)\n    strategy.exit(\'Exit Sell\', \'Sell Order\', profit=takeProfitLevel / syminfo.pointvalue, loss=stopLossLevel / syminfo.pointvalue)\n    lastCrossTime := timenow\n\nplot(ema1, title=\'EMA Short\', color=color.new(color.blue, 0), linewidth=2)\nplot(ema2, title=\'EMA Long\', color=color.new(color.red, 0), linewidth=2)'

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
