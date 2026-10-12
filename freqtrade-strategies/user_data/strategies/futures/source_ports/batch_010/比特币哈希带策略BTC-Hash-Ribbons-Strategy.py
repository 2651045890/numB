"""Source-faithful deep-assisted port of 比特币哈希带策略BTC-Hash-Ribbons-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c4623080(PinePortBase, IStrategy):
    source_file = '比特币哈希带策略BTC-Hash-Ribbons-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'enableDirection': 0, 'smoothingS': 'SMA', 'SmoothLengthS': 30, 'smoothingL': 'SMA', 'SmoothLengthL': 60}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'switch', '=>']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.']
    pine_assignments = [{'mode': '', 'name': 'enableDirection', 'op': '=', 'expr': 'input(0, title="Both(0), Long(1), Short(-1)", group="Direction")', 'conditions': []}, {'mode': '', 'name': 'smoothingS', 'op': '=', 'expr': 'input.string(title="Smoothing short MA", defval="SMA", options=["SMA", "RMA", "EMA", "WMA"], group="Hashrate Settings")', 'conditions': []}, {'mode': '', 'name': 'SmoothLengthS', 'op': '=', 'expr': 'input(30, \'Short MA length\', group="Hashrate Settings")', 'conditions': []}, {'mode': '', 'name': 'smoothingL', 'op': '=', 'expr': 'input.string(title="Smoothing long MA", defval="SMA", options=["SMA", "RMA", "EMA", "WMA"], group="Hashrate Settings")', 'conditions': []}, {'mode': '', 'name': 'SmoothLengthL', 'op': '=', 'expr': 'input(60, \'Long MA length\', group="Hashrate Settings")', 'conditions': []}, {'mode': '', 'name': 'HashRate', 'op': '=', 'expr': 'request.security("INTOTHEBLOCK:BTC_HASHRATE", "D", close)', 'conditions': []}, {'mode': '', 'name': 'SignalLine', 'op': '=', 'expr': 'ma_functionS(HashRate, SmoothLengthS)', 'conditions': []}, {'mode': '', 'name': 'LongLine', 'op': '=', 'expr': 'ma_functionL(HashRate, SmoothLengthL)', 'conditions': []}, {'mode': '', 'name': 'LongCondition', 'op': '=', 'expr': 'ta.crossover(SignalLine, LongLine)', 'conditions': []}, {'mode': '', 'name': 'ShortCondition', 'op': '=', 'expr': 'ta.crossunder(SignalLine, LongLine)', 'conditions': []}]
    pine_user_functions = [{'name': 'ma_functionS', 'args': 'source, length', 'body': ''}, {'name': 'ma_functionL', 'args': 'source, length', 'body': ''}]
    pine_controls = [{'indent': 1, 'statement': 'switch smoothingS'}, {'indent': 1, 'statement': 'switch smoothingL'}, {'indent': 0, 'statement': 'if LongCondition and (enableDirection == 1 or enableDirection == 0)'}, {'indent': 0, 'statement': 'if LongCondition and (enableDirection == -1)'}, {'indent': 0, 'statement': 'if ShortCondition and (enableDirection == -1 or enableDirection == 0)'}, {'indent': 0, 'statement': 'if ShortCondition and (enableDirection == 1)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['LongCondition and (enableDirection == 1 or enableDirection == 0)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['LongCondition and (enableDirection == -1)'], 'statement': 'strategy.close("Short")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['ShortCondition and (enableDirection == -1 or enableDirection == 0)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['ShortCondition and (enableDirection == 1)'], 'statement': 'strategy.close("Long")'}]
    original_pine = '/*backtest\nstart: 2023-01-05 00:00:00\nend: 2024-01-11 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Powerscooter\n// Since IntoTheBlock only provides daily hashrate data, this chart might look chunky on lower timeframes, even with smoothing.\n\n//@version=5\nstrategy("BTC Hashrate ribbons", overlay = true)\nenableDirection = input(0, title="Both(0), Long(1), Short(-1)", group="Direction")\nsmoothingS = input.string(title="Smoothing short MA", defval="SMA", options=["SMA", "RMA", "EMA", "WMA"], group="Hashrate Settings")\nSmoothLengthS = input(30, \'Short MA length\', group="Hashrate Settings")\nsmoothingL = input.string(title="Smoothing long MA", defval="SMA", options=["SMA", "RMA", "EMA", "WMA"], group="Hashrate Settings")\nSmoothLengthL = input(60, \'Long MA length\', group="Hashrate Settings")\nma_functionS(source, length) =>\n\tswitch smoothingS\n\t\t"RMA" => ta.rma(source, length)\n\t\t"SMA" => ta.sma(source, length)\n\t\t"EMA" => ta.ema(source, length)\n\t\t=> ta.wma(source, length)\nma_functionL(source, length) =>\n\tswitch smoothingL\n\t\t"RMA" => ta.rma(source, length)\n\t\t"SMA" => ta.sma(source, length)\n\t\t"EMA" => ta.ema(source, length)\n\t\t=> ta.wma(source, length)\n\nHashRate = request.security("INTOTHEBLOCK:BTC_HASHRATE", "D", close)\n\nSignalLine = ma_functionS(HashRate, SmoothLengthS)\nLongLine = ma_functionL(HashRate, SmoothLengthL)\n\nplot(ma_functionS(HashRate, SmoothLengthS), "Short MA", color=color.yellow)\nplot(ma_functionL(HashRate, SmoothLengthL), "Long MA", color=color.blue)\n\nLongCondition = ta.crossover(SignalLine, LongLine)\nShortCondition = ta.crossunder(SignalLine, LongLine)\n\n//Long Entry Condition\nif LongCondition and (enableDirection == 1 or enableDirection == 0)\n    strategy.entry("Long", strategy.long)\nif LongCondition and (enableDirection == -1)\n    strategy.close("Short")\n\n//Short Entry condition\nif ShortCondition and (enableDirection == -1 or enableDirection == 0)\n    strategy.entry("Short", strategy.short)\nif ShortCondition and (enableDirection == 1)\n    strategy.close("Long")'

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
