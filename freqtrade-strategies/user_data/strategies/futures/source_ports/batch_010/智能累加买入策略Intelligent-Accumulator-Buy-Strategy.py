"""Source-faithful deep-assisted port of 智能累加买入策略Intelligent-Accumulator-Buy-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_ea15dc87(PinePortBase, IStrategy):
    source_file = '智能累加买入策略Intelligent-Accumulator-Buy-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'addWhileInProfit': False, 'extLong': False, 'entry': 'close', 'minProfit': 0.0, 'exitPxcandle': 100.0, 'extShort': False, 'exit': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.opentrades', 'while ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'maxEntries', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'maxEntries', 'op': ':=', 'expr': 'maxEntries[1]', 'conditions': ['not na(maxEntries[1])']}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, 7)', 'conditions': []}, {'mode': '', 'name': 'rsima', 'op': '=', 'expr': 'ta.sma(rsi, 14)', 'conditions': []}, {'mode': '', 'name': 'bbstd', 'op': '=', 'expr': 'ta.stdev(rsi, 14)', 'conditions': []}, {'mode': '', 'name': 'intEntry', 'op': '=', 'expr': 'rsi < rsima - bbstd', 'conditions': []}, {'mode': '', 'name': 'intExit', 'op': '=', 'expr': 'rsi > rsima + bbstd', 'conditions': []}, {'mode': '', 'name': 'maxEntries', 'op': ':=', 'expr': 'math.max(strategy.opentrades, maxEntries)', 'conditions': []}, {'mode': '', 'name': 'addWhileInProfit', 'op': '=', 'expr': 'input.bool(false, "Add while in profit")', 'conditions': []}, {'mode': '', 'name': 'extLong', 'op': '=', 'expr': 'input.bool(false, "", inline = "long")', 'conditions': []}, {'mode': '', 'name': 'entry', 'op': '=', 'expr': 'input.source(close,"entry", inline = "long") == 1', 'conditions': []}, {'mode': '', 'name': 'entry', 'op': ':=', 'expr': 'intEntry', 'conditions': ['not extLong']}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'entry and (strategy.opentrades == 0 or (not addWhileInProfit or close < strategy.position_avg_price))', 'conditions': []}, {'mode': '', 'name': 'minProfit', 'op': '=', 'expr': 'input.float(0.0, "Required profit % to exit")', 'conditions': []}, {'mode': '', 'name': 'exitPxcandle', 'op': '=', 'expr': 'input.float(100.0,"% exit per candle")', 'conditions': []}, {'mode': '', 'name': 'extShort', 'op': '=', 'expr': 'input.bool(false, "", inline = "exit")', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'input.source(close,"exit", inline = "exit") == 1', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': ':=', 'expr': 'intExit', 'conditions': ['not extShort']}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'exit', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if not na(maxEntries[1])'}, {'indent': 0, 'statement': 'if not extLong'}, {'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if not extShort'}, {'indent': 0, 'statement': 'if (shortCondition and strategy.opentrades > 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("long", qty_percent = exitPxcandle)', 'conditions': ['(shortCondition and strategy.opentrades > 0)'], 'statement': 'strategy.close("long", qty_percent = exitPxcandle)'}]
    original_pine = '/*backtest\nstart: 2023-02-19 00:00:00\nend: 2024-02-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © TheTradingParrot\n\n//@version=5\nstrategy("TTP Intelligent Accumulator", overlay=true)\n\nmaxEntries = 0.0\n\nif not na(maxEntries[1])\n    maxEntries := maxEntries[1]\n\nrsi = ta.rsi(close, 7)\nrsima = ta.sma(rsi, 14)\nbbstd = ta.stdev(rsi, 14)\n\n// plot(rsi)\n// plot(rsima)\n// plot(rsima - bbstd)\n// plot(rsima + bbstd)\n\nintEntry = rsi < rsima - bbstd\nintExit = rsi > rsima + bbstd\n\nmaxEntries := math.max(strategy.opentrades, maxEntries)\nplot(maxEntries, "maxEntries")\n\naddWhileInProfit = input.bool(false, "Add while in profit")\n\nextLong = input.bool(false, "", inline = "long")\nentry = input.source(close,"entry", inline = "long") == 1\n\nif not extLong\n    entry := intEntry\nlongCondition = entry and (strategy.opentrades == 0 or (not addWhileInProfit or close < strategy.position_avg_price))\n\n\nif (longCondition)\n    strategy.entry("long", strategy.long)\n\nminProfit = input.float(0.0, "Required profit % to exit")\nexitPxcandle = input.float(100.0,"% exit per candle")\n\nextShort = input.bool(false, "", inline = "exit")\n\nexit = input.source(close,"exit", inline = "exit") == 1\nif not extShort\n    exit := intExit\n\nshortCondition = exit\nif (shortCondition and strategy.opentrades > 0)\n    strategy.close("long", qty_percent = exitPxcandle)\n\nplot(strategy.position_avg_price, "Avg")'

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
