"""Source-faithful deep-assisted port of 波林格带动态止盈策略-Dynamic-Take-Profit-Bollinger-Bands-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7b8b5102(PinePortBase, IStrategy):
    source_file = '波林格带动态止盈策略-Dynamic-Take-Profit-Bollinger-Bands-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'length': 14, 'mult': 2.0, 'showBands': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ', 'barstate.', 'table.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(14, "Length")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input.float(2.0, "Multiplier")', 'conditions': []}, {'mode': '', 'name': 'showBands', 'op': '=', 'expr': 'input.bool(true, "Show Bands")', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercentage', 'op': '=', 'expr': '1.0', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(close, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(close, length)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(close[1], lower[1]) and close[1] < open[1]', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(close[1], upper[1]) and close[1] > open[1]', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'shortTakeProfit', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'longTakeProfit', 'op': ':=', 'expr': 'close * (1 + takeProfitPercentage / 100)', 'conditions': ['longCondition']}, {'mode': '', 'name': 'shortTakeProfit', 'op': ':=', 'expr': 'close * (1 - takeProfitPercentage / 100)', 'conditions': ['shortCondition']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if longCondition'}, {'indent': 0, 'statement': 'if shortCondition'}, {'indent': 0, 'statement': 'if longCondition'}, {'indent': 0, 'statement': 'if shortCondition'}, {'indent': 0, 'statement': 'if barstate.islast'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['longCondition'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", from_entry="Buy", limit=longTakeProfit)', 'conditions': ['longCondition'], 'statement': 'strategy.exit("Take Profit", from_entry="Buy", limit=longTakeProfit)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['shortCondition'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", from_entry="Sell", limit=shortTakeProfit)', 'conditions': ['shortCondition'], 'statement': 'strategy.exit("Take Profit", from_entry="Sell", limit=shortTakeProfit)'}]
    original_pine = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2024-04-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Future Price Prediction", overlay=true)\n\n// Ayarlar\nlength = input.int(14, "Length")\nmult = input.float(2.0, "Multiplier")\nshowBands = input.bool(true, "Show Bands")\ntakeProfitPercentage = 1.0\n\n// Ortalama ve Standart Sapma Hesaplamaları\nbasis = ta.sma(close, length)\ndev = mult * ta.stdev(close, length)\n\n// Üst ve Alt Bantlar\nupper = basis + dev\nlower = basis - dev\n\n// Grafikte Gösterim\nplot(basis, color=color.blue, linewidth=2, title="Basis")\nplot(showBands ? upper : na, color=color.red, linewidth=1, title="Upper Band")\nplot(showBands ? lower : na, color=color.green, linewidth=1, title="Lower Band")\n\n// Al-Sat Sinyalleri\nlongCondition = ta.crossover(close[1], lower[1]) and close[1] < open[1]\nshortCondition = ta.crossunder(close[1], upper[1]) and close[1] > open[1]\n\n// Kar al seviyeleri\nfloat longTakeProfit = na\nfloat shortTakeProfit = na\n\nif longCondition\n    longTakeProfit := close * (1 + takeProfitPercentage / 100)\nif shortCondition\n    shortTakeProfit := close * (1 - takeProfitPercentage / 100)\n\n// Strateji Giriş ve Çıkış\nif longCondition\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit", from_entry="Buy", limit=longTakeProfit)\n\nif shortCondition\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Take Profit", from_entry="Sell", limit=shortTakeProfit)\n\n// Al-Sat Sinyalleri Grafikte Gösterim\nplotshape(series=longCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=shortCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Bilgi Tablosu\nvar table data = table.new(position.bottom_right, 2, 2, frame_color=color.black, frame_width=1)\nif barstate.islast\n    table.cell(data, 0, 0, "Current Price", text_color=color.white)\n    table.cell(data, 1, 0, str.tostring(close))\n    table.cell(data, 0, 1, "Predicted Basis", text_color=color.white)\n    table.cell(data, 1, 1, str.tostring(basis))'

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
