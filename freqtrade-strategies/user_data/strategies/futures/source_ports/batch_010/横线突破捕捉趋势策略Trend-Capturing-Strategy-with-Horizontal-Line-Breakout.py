"""Source-faithful deep-assisted port of 横线突破捕捉趋势策略Trend-Capturing-Strategy-with-Horizontal-Line-Breakout.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6f68d077(PinePortBase, IStrategy):
    source_file = '横线突破捕捉趋势策略Trend-Capturing-Strategy-with-Horizontal-Line-Breakout.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.opentrades', 'var ', 'array.', 'timeframe.', 'line.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses mutable Pine arrays; mutation order and per-bar persistence are load-bearing.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'yatayc', 'op': '=', 'expr': 'low[1] > close[0]', 'conditions': []}, {'mode': '', 'name': 'cizgilen', 'op': '=', 'expr': 'input.int(20, "Çizgi uzunluğu?", group = "Yatay Çizgi Ayarları")', 'conditions': []}, {'mode': '', 'name': 'numberOfLines', 'op': '=', 'expr': 'input.int(10, "Son Kaç Çizgi?", 0, group = "Yatay Çizgi Ayarları")', 'conditions': []}, {'mode': '', 'name': 'kural22', 'op': '=', 'expr': 'low[1] > close[0]', 'conditions': []}, {'mode': 'var', 'name': 'lastLinePrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'lastLinePrice', 'op': ':=', 'expr': 'line.get_price(array.get(lines, array.size(lines) - 1), bar_index)', 'conditions': ['not na(close) and array.size(lines) > 0']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if yatayc'}, {'indent': 4, 'statement': 'if strategy.opentrades > 0'}, {'indent': 4, 'statement': 'else'}, {'indent': 0, 'statement': 'if not na(close) and array.size(lines) > 0'}, {'indent': 0, 'statement': 'if open < lastLinePrice and close > lastLinePrice'}, {'indent': 4, 'statement': 'if strategy.opentrades > 0'}, {'indent': 4, 'statement': 'else'}]
    pine_orders = [{'kind': 'close', 'call': 'strategy.close("AL", comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")', 'conditions': ['yatayc', 'strategy.opentrades > 0'], 'statement': 'strategy.close("AL", comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")'}, {'kind': 'entry', 'call': 'strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")', 'conditions': ['yatayc', 'ELSE'], 'statement': 'strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")'}, {'kind': 'close', 'call': 'strategy.close("AL", comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")', 'conditions': ['open < lastLinePrice and close > lastLinePrice', 'strategy.opentrades > 0'], 'statement': 'strategy.close("AL", comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")'}, {'kind': 'entry', 'call': 'strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")', 'conditions': ['open < lastLinePrice and close > lastLinePrice', 'ELSE'], 'statement': 'strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")'}]
    original_pine = '/*backtest\nstart: 2023-04-20 00:00:00\nend: 2024-04-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Traderxprox\n\n//@version=5\nstrategy("Alarm Trader_ALL", overlay=true)\n\n// Yatay çizgi oluşum\nyatayc = low[1] > close[0]\n\nif yatayc\n    if strategy.opentrades > 0\n        strategy.close("AL", comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")\n    else\n        strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(low[1], "#.##") + "\\n" + timeframe.period +"\\n Yatay Direnç Oluştu")\n\n\n//YATAY ÇİZGİ\nint cizgilen = input.int(20, "Çizgi uzunluğu?", group = "Yatay Çizgi Ayarları")\nvar array<line> lines = array.new<line>()\nint numberOfLines = input.int(10, "Son Kaç Çizgi?", 0, group = "Yatay Çizgi Ayarları")\nkural22 = low[1] > close[0]\n// if kural22\n//     newLine = line.new(bar_index-2, low[1], bar_index+cizgilen, low[1] ,color=color.red, width=1, style=line.style_solid)\n//     // Push the `newLine` into the `lines` array.\n//     lines.push(newLine)\n//     // Delete the oldest line when the size of the array exceeds the specified `numberOfLines`.\n//     if array.size(lines) > numberOfLines\n//         line.delete(lines.shift())\n    \n// Alarm kırılım için koşul\n\nvar float lastLinePrice = na\nif not na(close) and array.size(lines) > 0 \n    lastLinePrice := line.get_price(array.get(lines, array.size(lines) - 1), bar_index)\nif open < lastLinePrice and close > lastLinePrice\n    if strategy.opentrades > 0\n        strategy.close("AL", comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")\n    else\n        strategy.entry("AL", strategy.long, comment = "Fiyat:" + str.tostring(lastLinePrice, "#.##") + "\\n" + timeframe.period +" \\n Yatay çizgi yukarı kırılımı")'

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
