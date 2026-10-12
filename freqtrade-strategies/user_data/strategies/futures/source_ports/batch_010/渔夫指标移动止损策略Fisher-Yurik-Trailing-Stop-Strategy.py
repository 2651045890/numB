"""Source-faithful deep-assisted port of 渔夫指标移动止损策略Fisher-Yurik-Trailing-Stop-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_081e50f5(PinePortBase, IStrategy):
    source_file = '渔夫指标移动止损策略Fisher-Yurik-Trailing-Stop-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'from_month': 1, 'from_day': 1, 'from_year': 2021, 'to_month': 1, 'to_day': 1, 'to_year': 9999, 'period': 2, 'cost': 1.05, 'dusus': 1.02}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'from_month', 'op': '=', 'expr': 'input(defval = 1, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'from_day', 'op': '=', 'expr': 'input(defval = 1, title = "From Day")', 'conditions': []}, {'mode': '', 'name': 'from_year', 'op': '=', 'expr': 'input(defval = 2021, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'to_month', 'op': '=', 'expr': 'input(defval = 1, title = "To Month")', 'conditions': []}, {'mode': '', 'name': 'to_day', 'op': '=', 'expr': 'input(defval = 1, title = "To Day")', 'conditions': []}, {'mode': '', 'name': 'to_year', 'op': '=', 'expr': 'input(defval = 9999, title = "To Year")', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(from_year, from_month, from_day, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(to_year, to_month, to_day, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'window', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'period', 'op': '=', 'expr': "input(2, title='Period')", 'conditions': []}, {'mode': '', 'name': 'cost', 'op': '=', 'expr': "input.float(1.05, title='profit level ', step=0.01)", 'conditions': []}, {'mode': '', 'name': 'dusus', 'op': '=', 'expr': "input.float(1.02, title='after the signal', step=0.01)", 'conditions': []}, {'mode': 'var', 'name': 'Value', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'Fish', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'ExtBuffer1', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'ExtBuffer2', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': '(high + low) / 2', 'conditions': []}, {'mode': '', 'name': 'MaxH', 'op': '=', 'expr': 'ta.highest(high, period)', 'conditions': []}, {'mode': '', 'name': 'MinL', 'op': '=', 'expr': 'ta.lowest(low, period)', 'conditions': []}, {'mode': '', 'name': 'Value', 'op': ':=', 'expr': '0.33 * 2 * ((price - MinL) / (MaxH - MinL) - 0.5) + 0.67 * nz(Value[1])', 'conditions': []}, {'mode': '', 'name': 'Value', 'op': ':=', 'expr': 'math.max(math.min(Value, 0.999), -0.999)', 'conditions': []}, {'mode': '', 'name': 'Fish', 'op': ':=', 'expr': '0.5 * math.log((1 + Value) / (1 - Value)) + 0.5 * nz(Fish[1])', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'Fish >= 0', 'conditions': []}, {'mode': '', 'name': 'ExtBuffer1', 'op': ':=', 'expr': 'up ? Fish : na', 'conditions': []}, {'mode': '', 'name': 'ExtBuffer2', 'op': ':=', 'expr': 'up ? na : Fish', 'conditions': []}, {'mode': 'var', 'name': 'entryPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'stopPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'entryPrice', 'op': ':=', 'expr': 'close*dusus', 'conditions': ['(ExtBuffer1 > ExtBuffer1[1])']}, {'mode': '', 'name': 'stopPrice', 'op': ':=', 'expr': 'close * cost', 'conditions': ['(ExtBuffer1 > ExtBuffer1[1])']}, {'mode': '', 'name': 'entryPrice', 'op': ':=', 'expr': 'close', 'conditions': ['(ExtBuffer2 < ExtBuffer2[1])']}, {'mode': '', 'name': 'stopPrice', 'op': ':=', 'expr': 'close * cost', 'conditions': ['(ExtBuffer2 < ExtBuffer2[1])']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (ExtBuffer1 > ExtBuffer1[1])'}, {'indent': 0, 'statement': 'if (ExtBuffer2 < ExtBuffer2[1])'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=ExtBuffer1 > ExtBuffer1[1] and window)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=ExtBuffer1 > ExtBuffer1[1] and window)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Trailing Stop", from_entry="Buy", when=(close >= entryPrice * cost) or (close < stopPrice), trail_offset=0.08, trail_price=entryPrice * cost)', 'conditions': [], 'statement': 'strategy.exit("Take Profit/Trailing Stop", from_entry="Buy", when=(close >= entryPrice * cost) or (close < stopPrice), trail_offset=0.08, trail_price=entryPrice * cost)'}]
    original_pine = '/*backtest\nstart: 2023-01-26 00:00:00\nend: 2024-02-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Fisher_Yurik Strategy with Trailing Stop", shorttitle="FY Strategy", overlay=true)\n\n// Date Ranges \nfrom_month = input(defval = 1, title = "From Month")\nfrom_day   = input(defval = 1, title = "From Day")\nfrom_year  = input(defval = 2021, title = "From Year")\nto_month   = input(defval = 1, title = "To Month")\nto_day     = input(defval = 1, title = "To Day")\nto_year    = input(defval = 9999, title = "To Year")\nstart  = timestamp(from_year, from_month, from_day, 00, 00)  // backtest start window\nfinish = timestamp(to_year, to_month, to_day, 23, 59)        // backtest finish window\nwindow = true\nperiod = input(2, title=\'Period\')\ncost = input.float(1.05, title=\'profit level \', step=0.01)\ndusus = input.float(1.02, title=\'after the signal\', step=0.01)\n\nvar float Value = na\nvar float Fish = na\nvar float ExtBuffer1 = na\nvar float ExtBuffer2 = na\n\nprice = (high + low) / 2\nMaxH = ta.highest(high, period)\nMinL = ta.lowest(low, period)\n\nValue := 0.33 * 2 * ((price - MinL) / (MaxH - MinL) - 0.5) + 0.67 * nz(Value[1])\nValue := math.max(math.min(Value, 0.999), -0.999)\nFish := 0.5 * math.log((1 + Value) / (1 - Value)) + 0.5 * nz(Fish[1])\n\nup = Fish >= 0\n\nExtBuffer1 := up ? Fish : na\nExtBuffer2 := up ? na : Fish\n\nvar float entryPrice = na\nvar float stopPrice = na\n \nif (ExtBuffer1 > ExtBuffer1[1])\n    entryPrice := close*dusus\n    stopPrice := close * cost \n \nif (ExtBuffer2 < ExtBuffer2[1])\n    entryPrice := close\n    stopPrice := close * cost\n\n// Sadece seçilen test döneminde işlem yapma koşulu eklenmiştir\nstrategy.entry("Buy", strategy.long, when=ExtBuffer1 > ExtBuffer1[1] and window)\nstrategy.exit("Take Profit/Trailing Stop", from_entry="Buy", when=(close >= entryPrice * cost) or (close < stopPrice), trail_offset=0.08, trail_price=entryPrice * cost)'

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
