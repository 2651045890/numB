"""Source-faithful deep-assisted port of 相对量指标策略The-Relative-Volume-Indicator-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_910f4268(PinePortBase, IStrategy):
    source_file = '相对量指标策略The-Relative-Volume-Indicator-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'RSIlength': 14, 'RSItop': 70, 'RSIbottom': 35, 'RVOLlen': 14, 'RVOLthreshold': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'RSIlength', 'op': '=', 'expr': 'input(14, title="RSI Period")', 'conditions': []}, {'mode': '', 'name': 'RSItop', 'op': '=', 'expr': 'input(70, title="RSI buy", minval= 69, maxval=100)', 'conditions': []}, {'mode': '', 'name': 'RSIbottom', 'op': '=', 'expr': 'input(35, title="RSI short", minval= 0, maxval=35)', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'rsi(price, RSIlength)', 'conditions': []}, {'mode': '', 'name': 'RSIco', 'op': '=', 'expr': 'crossover(vrsi, RSItop)', 'conditions': []}, {'mode': '', 'name': 'RSIcu', 'op': '=', 'expr': 'crossunder(vrsi, RSIbottom)', 'conditions': []}, {'mode': '', 'name': 'band1', 'op': '=', 'expr': 'hline(70, "Upper Band", color=#C0C0C0)', 'conditions': []}, {'mode': '', 'name': 'bandm', 'op': '=', 'expr': 'hline(50, "Middle Band", color=color.new(#C0C0C0, 50))', 'conditions': []}, {'mode': '', 'name': 'band0', 'op': '=', 'expr': 'hline(30, "Lower Band", color=#C0C0C0)', 'conditions': []}, {'mode': '', 'name': 'RVOLlen', 'op': '=', 'expr': 'input(14, minval=1, title="RV Period")', 'conditions': []}, {'mode': '', 'name': 'av', 'op': '=', 'expr': 'sma(volume, RVOLlen)', 'conditions': []}, {'mode': '', 'name': 'RVOL', 'op': '=', 'expr': 'volume / av', 'conditions': []}, {'mode': '', 'name': 'RVOLthreshold', 'op': '=', 'expr': 'input(1.5,title="RV Threshold", minval=0.5, maxval=10)', 'conditions': []}, {'mode': '', 'name': 'LongCondition', 'op': '=', 'expr': 'RSIco and RVOL > RVOLthreshold', 'conditions': []}, {'mode': '', 'name': 'CloseLong', 'op': '=', 'expr': 'vrsi < 69', 'conditions': []}, {'mode': '', 'name': 'ShortCondition', 'op': '=', 'expr': 'RSIcu and RVOL > RVOLthreshold', 'conditions': []}, {'mode': '', 'name': 'CloseShort', 'op': '=', 'expr': 'vrsi > 35', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (LongCondition)'}, {'indent': 0, 'statement': 'if (ShortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(LongCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long", when = CloseLong)', 'conditions': [], 'statement': 'strategy.close("Long", when = CloseLong)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(ShortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Short", when = CloseShort)', 'conditions': [], 'statement': 'strategy.close("Short", when = CloseShort)'}]
    original_pine = '/*backtest\nstart: 2022-12-13 00:00:00\nend: 2023-12-19 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © gary_trades\n//This script is a basic concept to catch breakout moves utilising a spike in relative volume when the RSI is high (for longs) or when the RSI is low (for shorts).\n//Drawdown is typically low as it exits out of the trade once the RSI returns back to "normal levels".\n\n//@version=4\nstrategy(title="Relative Volume & RSI Pop", shorttitle="VOL & RSI Pop", overlay=false, precision=2, margin_long=100, margin_short=100)\n\n//RSI\nRSIlength = input(14, title="RSI Period")\nRSItop = input(70, title="RSI buy", minval= 69, maxval=100)\nRSIbottom = input(35, title="RSI short", minval= 0, maxval=35)\nprice = close\nvrsi = rsi(price, RSIlength)\nRSIco = crossover(vrsi, RSItop)\nRSIcu = crossunder(vrsi, RSIbottom)\nplot(vrsi, "RSI", color=color.purple)\nband1 = hline(70, "Upper Band", color=#C0C0C0)\nbandm = hline(50, "Middle Band", color=color.new(#C0C0C0, 50))\nband0 = hline(30, "Lower Band", color=#C0C0C0)\nfill(band1, band0, color=color.purple, transp=90, title="Background")\n\n//RELATIVE VOLUME\nRVOLlen = input(14, minval=1, title="RV Period")\nav = sma(volume, RVOLlen)\nRVOL = volume / av\nRVOLthreshold = input(1.5,title="RV Threshold", minval=0.5, maxval=10)\n\n//TRADE TRIGGERS\nLongCondition = RSIco and RVOL > RVOLthreshold\nCloseLong = vrsi < 69\n\nShortCondition = RSIcu and RVOL > RVOLthreshold\nCloseShort = vrsi > 35\n\nif (LongCondition)\n    strategy.entry("Long", strategy.long)\n    \nstrategy.close("Long", when = CloseLong)    \n\nif (ShortCondition)\n    strategy.entry("Short", strategy.short)\n    \nstrategy.close("Short", when = CloseShort)'

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
