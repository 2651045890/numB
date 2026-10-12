"""Source-faithful deep-assisted port of 快慢EMA交叉intraday交易策略Fast-and-Slow-EMA-Cross-Intraday-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_038aa55e(PinePortBase, IStrategy):
    source_file = '快慢EMA交叉intraday交易策略Fast-and-Slow-EMA-Cross-Intraday-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 110, 'slowLength': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.equity']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input(110)', 'conditions': []}, {'mode': '', 'name': 'slowLength', 'op': '=', 'expr': 'input(40)', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'emafast', 'op': '=', 'expr': 'ema(price, fastLength)', 'conditions': []}, {'mode': '', 'name': 'emaslow', 'op': '=', 'expr': 'ema(price, slowLength)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (crossover(emafast, emaslow))'}, {'indent': 0, 'statement': 'if (crossunder(emafast, emaslow))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("EMA2CrossLE", strategy.long, comment="long")', 'conditions': ['(crossover(emafast, emaslow))'], 'statement': 'strategy.entry("EMA2CrossLE", strategy.long, comment="long")'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", from_entry = "EMA2CrossLE", loss = 500, comment= "Rshort")', 'conditions': ['(crossover(emafast, emaslow))'], 'statement': 'strategy.exit("Exit Long", from_entry = "EMA2CrossLE", loss = 500, comment= "Rshort")'}, {'kind': 'entry', 'call': 'strategy.entry("EMA2CrossSE", strategy.short, comment="short")', 'conditions': ['(crossunder(emafast, emaslow))'], 'statement': 'strategy.entry("EMA2CrossSE", strategy.short, comment="short")'}, {'kind': 'exit', 'call': 'strategy.exit("Exit short", from_entry = "EMA2CrossSE", loss = 500, comment= "RLong")', 'conditions': ['(crossunder(emafast, emaslow))'], 'statement': 'strategy.exit("Exit short", from_entry = "EMA2CrossSE", loss = 500, comment= "RLong")'}]
    original_pine = '/*backtest\nstart: 2023-08-12 00:00:00\nend: 2023-09-11 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Eli Strategy", overlay=true)\nfastLength = input(110)\nslowLength = input(40)\nprice = close\n\nemafast = ema(price, fastLength)\nemaslow = ema(price, slowLength)\n\n\nif (crossover(emafast, emaslow))\n    strategy.entry("EMA2CrossLE", strategy.long, comment="long")\n    strategy.exit("Exit Long", from_entry = "EMA2CrossLE", loss = 500, comment= "Rshort")\n\nif (crossunder(emafast, emaslow))\n    strategy.entry("EMA2CrossSE", strategy.short, comment="short")\n    strategy.exit("Exit short", from_entry = "EMA2CrossSE", loss = 500, comment= "RLong")\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
