"""Source-faithful deep-assisted port of 振荡平衡策略Oscillation-Balance-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6c2657fb(PinePortBase, IStrategy):
    source_file = '振荡平衡策略Oscillation-Balance-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'BoP', 'op': '=', 'expr': '(close - open) / (high - low)', 'conditions': []}, {'mode': '', 'name': 'p1', 'op': '=', 'expr': 'plot(ema(BoP,18),color=color.purple)', 'conditions': []}, {'mode': '', 'name': 'p2', 'op': '=', 'expr': 'plot(ema(BoP,12),color=color.blue)', 'conditions': []}, {'mode': '', 'name': 'p3', 'op': '=', 'expr': 'plot(ema(BoP,9),color=color.green)', 'conditions': []}, {'mode': '', 'name': 'p4', 'op': '=', 'expr': 'plot(ema(BoP,6),color=color.yellow)', 'conditions': []}, {'mode': '', 'name': 'p5', 'op': '=', 'expr': 'plot(ema(BoP,3),color=color.orange)', 'conditions': []}, {'mode': '', 'name': 'p6', 'op': '=', 'expr': 'plot(BoP, color=color.red)', 'conditions': []}, {'mode': '', 'name': 'sumEMA', 'op': '=', 'expr': '(avg(BoP,ema(BoP,3),ema(BoP,6),ema(BoP,9),ema(BoP,12),ema(BoP,18)))', 'conditions': []}, {'mode': '', 'name': 'projected', 'op': '=', 'expr': 'sumEMA + (sumEMA - sumEMA[2])', 'conditions': []}, {'mode': '', 'name': 'p7', 'op': '=', 'expr': 'plot(projected, linewidth=2, color=color.white)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long",true,1,when=crossover(projected,0))', 'conditions': [], 'statement': 'strategy.entry("Long",true,1,when=crossover(projected,0))'}, {'kind': 'entry', 'call': 'strategy.entry("Short",false,0,when=crossunder(projected,0))', 'conditions': [], 'statement': 'strategy.entry("Short",false,0,when=crossunder(projected,0))'}]
    original_pine = '/*backtest\nstart: 2022-10-13 00:00:00\nend: 2023-10-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="Balance of Power", format=format.price, precision=2)\n\nBoP = (close - open) / (high - low)\np1 = plot(ema(BoP,18),color=color.purple)\np2 = plot(ema(BoP,12),color=color.blue)\np3 = plot(ema(BoP,9),color=color.green)\np4 = plot(ema(BoP,6),color=color.yellow)\np5 = plot(ema(BoP,3),color=color.orange)\np6 = plot(BoP, color=color.red)\n\n\nsumEMA = (avg(BoP,ema(BoP,3),ema(BoP,6),ema(BoP,9),ema(BoP,12),ema(BoP,18)))\nplot(sumEMA,color=color.gray)\n\nfill(p1,p2,color.purple)\nfill(p2,p3,color.blue)\nfill(p3,p4,color.green)\nfill(p4,p5,color.yellow)\nfill(p5,p6,color.orange)\n\n\n\n\nprojected = sumEMA + (sumEMA - sumEMA[2])\np7 = plot(projected, linewidth=2, color=color.white)\nfill(p6,p7,color.red)\n\n//strategy.exit("exitx","Exit",when=cross(projected,0))\n\nstrategy.entry("Long",true,1,when=crossover(projected,0))\nstrategy.entry("Short",false,0,when=crossunder(projected,0))'

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
