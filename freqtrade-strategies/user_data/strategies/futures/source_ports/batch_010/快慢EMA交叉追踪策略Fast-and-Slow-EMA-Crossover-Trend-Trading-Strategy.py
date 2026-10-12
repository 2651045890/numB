"""Source-faithful deep-assisted port of 快慢EMA交叉追踪策略Fast-and-Slow-EMA-Crossover-Trend-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_dd30097e(PinePortBase, IStrategy):
    source_file = '快慢EMA交叉追踪策略Fast-and-Slow-EMA-Crossover-Trend-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'maFastSource': 'close', 'maFastLength': 13, 'maSlowSource': 'close', 'maSlowLength': 48}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1000.0
    source_pyramiding = 3
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'maFastSource', 'op': '=', 'expr': 'input(defval = close, title = "Fast MA Source")', 'conditions': []}, {'mode': '', 'name': 'maFastLength', 'op': '=', 'expr': 'input(defval = 13, title = "Fast MA Period", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'maSlowSource', 'op': '=', 'expr': 'input(defval = close, title = "Slow MA Source")', 'conditions': []}, {'mode': '', 'name': 'maSlowLength', 'op': '=', 'expr': 'input(defval = 48, title = "Slow MA Period", minval = 1)', 'conditions': []}, {'mode': '', 'name': 'fastMA', 'op': '=', 'expr': 'ema(maFastSource, maFastLength)', 'conditions': []}, {'mode': '', 'name': 'slowMA', 'op': '=', 'expr': 'ema(maSlowSource, maSlowLength)', 'conditions': []}]
    pine_user_functions = [{'name': 'goLong', 'args': '', 'body': 'crossover(fastMA, slowMA)'}, {'name': 'killLong', 'args': '', 'body': 'crossunder(close, fastMA)'}, {'name': 'goShort', 'args': '', 'body': 'crossunder (fastMA, slowMA)'}, {'name': 'killShort', 'args': '', 'body': 'crossover(fastMA, slowMA)'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = goLong())', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = goLong())'}, {'kind': 'close', 'call': 'strategy.close("Buy", when = killLong())', 'conditions': [], 'statement': 'strategy.close("Buy", when = killLong())'}]
    original_pine = '/*backtest\nstart: 2022-09-05 00:00:00\nend: 2023-09-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\n// strategy("EMA Strategy 13 48", shorttitle = "EMA Strategy 13 48", overlay=true, pyramiding = 3,default_qty_type = strategy.percent_of_equity, default_qty_value = 1000)\n\n\n// === Inputs ===\n// short ma\nmaFastSource   = input(defval = close, title = "Fast MA Source")\nmaFastLength   = input(defval = 13, title = "Fast MA Period", minval = 1)\n\n// long ma\nmaSlowSource   = input(defval = close, title = "Slow MA Source")\nmaSlowLength   = input(defval = 48, title = "Slow MA Period", minval = 1)\n\n\n// === Vars and Series ===\nfastMA = ema(maFastSource, maFastLength)\nslowMA = ema(maSlowSource, maSlowLength)\n\nplot(fastMA, color=blue)\nplot(slowMA, color=purple)\n\ngoLong() => crossover(fastMA, slowMA)\nkillLong() => crossunder(close, fastMA)\nstrategy.entry("Buy", strategy.long, when = goLong())\nstrategy.close("Buy", when = killLong())\n\n// Shorting if using\ngoShort() => crossunder (fastMA, slowMA)\nkillShort() => crossover(fastMA, slowMA)\n//strategy.entry("Sell", strategy.short, when = goShort())\n//strategy.close("Sell", when = killShort())'

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
