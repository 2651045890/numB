"""Source-faithful deep-assisted port of 相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_42e19d9c(PinePortBase, IStrategy):
    source_file = '相对强弱指标RSI超买超卖量化交易策略-Relative-Strength-Index-RSI-Overbought-Oversold-Quantitative-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'pc_id': '', 'pc_risk': 0.1, 'pc_prefix': ''}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 5.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ', 'alert']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'pc_id', 'op': '=', 'expr': "input.string(title='License ID', defval='', group='MT4/5 Settings', tooltip='This is your license ID')", 'conditions': []}, {'mode': '', 'name': 'pc_risk', 'op': '=', 'expr': "input.float(title='Lots', defval=0.1, step=0.1, minval=0, group='MT4/5 Settings', tooltip='Lot Size')", 'conditions': []}, {'mode': '', 'name': 'pc_prefix', 'op': '=', 'expr': "input.string(title='MetaTrader Symbol', defval='', group='MT4/5 Settings', tooltip='This is your broker\\'s MetaTrader symbol')", 'conditions': []}, {'mode': 'var', 'name': 'symbol', 'op': '=', 'expr': 'pc_prefix', 'conditions': []}, {'mode': '', 'name': 'longa', 'op': '=', 'expr': "pc_id + ',buy,' + symbol + ',risk=' + str.tostring(pc_risk, '#.##')", 'conditions': []}, {'mode': '', 'name': 'shorta', 'op': '=', 'expr': "pc_id + ',sell,' + symbol + ',risk=' + str.tostring(pc_risk, '#.##')", 'conditions': []}, {'mode': '', 'name': 'longa_close', 'op': '=', 'expr': "pc_id + ',closelong,' + symbol + ''", 'conditions': []}, {'mode': '', 'name': 'shorta_close', 'op': '=', 'expr': "pc_id + ',closeshort,' + symbol + ''", 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'rsiSource', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(rsiSource, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'longEntry', 'op': '=', 'expr': 'ta.crossover(rsi, 30) // Buy when RSI crosses above 30', 'conditions': []}, {'mode': '', 'name': 'shortEntry', 'op': '=', 'expr': 'ta.crossunder(rsi, 70) // Sell when RSI crosses below 70', 'conditions': []}, {'mode': '', 'name': 'longExit', 'op': '=', 'expr': 'ta.crossover(rsi, 70) // Close long when RSI hits 70', 'conditions': []}, {'mode': '', 'name': 'shortExit', 'op': '=', 'expr': 'ta.crossunder(rsi, 30) // Close short when RSI hits 30', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longEntry)'}, {'indent': 0, 'statement': 'if (longExit)'}, {'indent': 0, 'statement': 'if (shortEntry)'}, {'indent': 0, 'statement': 'if (shortExit)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("BUY", strategy.long)', 'conditions': ['(longEntry)'], 'statement': 'strategy.entry("BUY", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("BUY")', 'conditions': ['(longExit)'], 'statement': 'strategy.close("BUY")'}, {'kind': 'entry', 'call': 'strategy.entry("SELL", strategy.short)', 'conditions': ['(shortEntry)'], 'statement': 'strategy.entry("SELL", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("SELL")', 'conditions': ['(shortExit)'], 'statement': 'strategy.close("SELL")'}]
    original_pine = '/*backtest\nstart: 2024-03-25 00:00:00\nend: 2025-03-24 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n// Risk Settings\npc_id = input.string(title=\'License ID\', defval=\'\', group=\'MT4/5 Settings\', tooltip=\'This is your license ID\')\npc_risk = input.float(title=\'Lots\', defval=0.1, step=0.1, minval=0, group=\'MT4/5 Settings\', tooltip=\'Lot Size\')\npc_prefix = input.string(title=\'MetaTrader Symbol\', defval=\'\', group=\'MT4/5 Settings\', tooltip=\'This is your broker\\\'s MetaTrader symbol\')\n\n// Symbol Information\nvar symbol = pc_prefix\n\n// Alerts for MetaTrader Integration\nlonga = pc_id + \',buy,\' + symbol + \',risk=\' + str.tostring(pc_risk, \'#.##\')\nshorta = pc_id + \',sell,\' + symbol + \',risk=\' + str.tostring(pc_risk, \'#.##\')\nlonga_close = pc_id + \',closelong,\' + symbol + \'\'\nshorta_close = pc_id + \',closeshort,\' + symbol + \'\'\n//@version=6\nstrategy("RSI Overbought/Oversold Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=5)\n\n// ? RSI Settings\nrsiLength = 14\nrsiSource = close\nrsi = ta.rsi(rsiSource, rsiLength)\n\n// ? Entry Conditions\nlongEntry = ta.crossover(rsi, 30)   // Buy when RSI crosses above 30\nshortEntry = ta.crossunder(rsi, 70) // Sell when RSI crosses below 70\n\n// ? Exit Conditions\nlongExit = ta.crossover(rsi, 70)  // Close long when RSI hits 70\nshortExit = ta.crossunder(rsi, 30) // Close short when RSI hits 30\n\n// ✅ Execute Trades\nif (longEntry)\n    strategy.entry("BUY", strategy.long)\nif (longExit)\n    strategy.close("BUY")\n\nif (shortEntry)\n    strategy.entry("SELL", strategy.short)\nif (shortExit)\n    strategy.close("SELL")\n\n// ? Visuals for Better Clarity\nplot(rsi, title="RSI", color=color.blue, linewidth=2)\nhline(70, "Overbought", color=color.red)\nhline(30, "Oversold", color=color.green)\n\n// ? Alerts for Entry/Exit\nalertcondition(longEntry, title="BUY Signal", message="RSI crossed above 30 - Buy!")\nalertcondition(longExit, title="SELL Exit", message="RSI reached 70 - Close Buy!")\nalertcondition(shortEntry, title="SELL Signal", message="RSI crossed below 70 - Sell!")\nalertcondition(shortExit, title="BUY Exit", message="RSI reached 30 - Close Sell!")'

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
