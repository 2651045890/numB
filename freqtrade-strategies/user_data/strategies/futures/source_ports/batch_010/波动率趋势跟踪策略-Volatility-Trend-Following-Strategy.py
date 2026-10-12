"""Source-faithful deep-assisted port of 波动率趋势跟踪策略-Volatility-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7dc04913(PinePortBase, IStrategy):
    source_file = '波动率趋势跟踪策略-Volatility-Trend-Following-Strategy.md'
    timeframe = '4h'
    can_short = False
    source_defaults = {'Length': 20, 'Dev': 1.0, 'UseFilter': True, 'ATRLength': 14, 'HideLabels': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Length', 'op': '=', 'expr': "input.int(defval=20, title='Length', minval=1) // Length parameter for Bollinger Bands", 'conditions': []}, {'mode': '', 'name': 'Dev', 'op': '=', 'expr': "input.float(defval=1.0, title='Deviation', minval=0.1, step=0.05) // Deviation parameter for Bollinger Bands", 'conditions': []}, {'mode': '', 'name': 'UseFilter', 'op': '=', 'expr': "input(defval=true, title='Use Filter') // Option to use filter", 'conditions': []}, {'mode': '', 'name': 'ATRLength', 'op': '=', 'expr': "input.int(defval=14, title='ATR Length', minval=1) // ATR Length parameter", 'conditions': []}, {'mode': '', 'name': 'HideLabels', 'op': '=', 'expr': "input(defval=false, title='Hide Labels') // Option to hide labels", 'conditions': []}, {'mode': '', 'name': 'UpperBand', 'op': '=', 'expr': 'ta.sma(close, Length) + ta.stdev(close, Length) * Dev', 'conditions': []}, {'mode': '', 'name': 'LowerBand', 'op': '=', 'expr': 'ta.sma(close, Length) - ta.stdev(close, Length) * Dev', 'conditions': []}, {'mode': '', 'name': 'Line', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'Trend', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'atrValue', 'op': '=', 'expr': 'ta.atr(ATRLength)', 'conditions': []}, {'mode': '', 'name': 'Signal', 'op': '=', 'expr': 'close > UpperBand ? 1 : close < LowerBand ? -1 : 0', 'conditions': []}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'low - atrValue', 'conditions': ['Signal == 1', 'UseFilter == true']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'Line[1]', 'conditions': ['Signal == 1', 'UseFilter == true', 'Line < Line[1]']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'low', 'conditions': ['Signal == 1', 'ELSE']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'Line[1]', 'conditions': ['Signal == 1', 'ELSE', 'Line < Line[1]']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'high + atrValue', 'conditions': ['Signal == -1', 'UseFilter == true']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'Line[1]', 'conditions': ['Signal == -1', 'UseFilter == true', 'Line > Line[1]']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'high', 'conditions': ['Signal == -1', 'ELSE']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'Line[1]', 'conditions': ['Signal == -1', 'ELSE', 'Line > Line[1]']}, {'mode': '', 'name': 'Line', 'op': ':=', 'expr': 'Line[1]', 'conditions': ['Signal == 0']}, {'mode': '', 'name': 'Trend', 'op': ':=', 'expr': 'Trend[1]', 'conditions': []}, {'mode': '', 'name': 'Trend', 'op': ':=', 'expr': '1', 'conditions': ['Line > Line[1]']}, {'mode': '', 'name': 'Trend', 'op': ':=', 'expr': '-1', 'conditions': ['Line < Line[1]']}, {'mode': '', 'name': 'BuySignal', 'op': '=', 'expr': 'Trend[1] == -1 and Trend == 1 ? true : false', 'conditions': []}, {'mode': '', 'name': 'SellSignal', 'op': '=', 'expr': 'Trend[1] == 1 and Trend == -1 ? true : false', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if Signal == 1'}, {'indent': 4, 'statement': 'if UseFilter == true'}, {'indent': 8, 'statement': 'if Line < Line[1]'}, {'indent': 4, 'statement': 'else'}, {'indent': 8, 'statement': 'if Line < Line[1]'}, {'indent': 0, 'statement': 'if Signal == -1'}, {'indent': 4, 'statement': 'if UseFilter == true'}, {'indent': 8, 'statement': 'if Line > Line[1]'}, {'indent': 4, 'statement': 'else'}, {'indent': 8, 'statement': 'if Line > Line[1]'}, {'indent': 0, 'statement': 'if Signal == 0'}, {'indent': 0, 'statement': 'if Line > Line[1]'}, {'indent': 0, 'statement': 'if Line < Line[1]'}, {'indent': 0, 'statement': 'if BuySignal'}, {'indent': 0, 'statement': 'if SellSignal'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Buy', strategy.long)", 'conditions': ['BuySignal'], 'statement': "strategy.entry('Buy', strategy.long)"}, {'kind': 'close', 'call': "strategy.close('Buy')", 'conditions': ['SellSignal'], 'statement': "strategy.close('Buy')"}]
    original_pine = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © Julien_Eche\n\n//@version=5\nstrategy(\'Volatility Trend Strategy\', overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=20)\n\n// Input parameters\nLength = input.int(defval=20, title=\'Length\', minval=1) // Length parameter for Bollinger Bands\nDev = input.float(defval=1.0, title=\'Deviation\', minval=0.1, step=0.05) // Deviation parameter for Bollinger Bands\nUseFilter = input(defval=true, title=\'Use Filter\') // Option to use filter\nATRLength = input.int(defval=14, title=\'ATR Length\', minval=1) // ATR Length parameter\nHideLabels = input(defval=false, title=\'Hide Labels\') // Option to hide labels\n\n// Calculation of Bollinger Bands\nUpperBand = ta.sma(close, Length) + ta.stdev(close, Length) * Dev\nLowerBand = ta.sma(close, Length) - ta.stdev(close, Length) * Dev\n\n// Initialization of variables\nLine = 0.0\nTrend = 0.0\n\n// Calculation of Average True Range (ATR)\natrValue = ta.atr(ATRLength)\n\n// Determine signal based on Bollinger Bands\nSignal = close > UpperBand ? 1 : close < LowerBand ? -1 : 0\n\n// Determine trend line based on signal and filter option\nif Signal == 1\n    if UseFilter == true\n        Line := low - atrValue\n        if Line < Line[1]\n            Line := Line[1]\n    else\n        Line := low\n        if Line < Line[1]\n            Line := Line[1]\n        \nif Signal == -1\n    if UseFilter == true\n        Line := high + atrValue\n        if Line > Line[1]\n            Line := Line[1]\n    else\n        Line := high\n        if Line > Line[1]\n            Line := Line[1]\n\nif Signal == 0\n    Line := Line[1]\n\n// Determine trend direction\nTrend := Trend[1]\nif Line > Line[1]\n    Trend := 1\nif Line < Line[1]\n    Trend := -1\n\n// Determine buy and sell signals\nBuySignal = Trend[1] == -1 and Trend == 1 ? true : false\nSellSignal = Trend[1] == 1 and Trend == -1 ? true : false\n\n// Plot trend line\nplot(Line, color=Trend > 0 ? color.new(color.blue, 100) : color.new(color.red, 100), style=plot.style_line, linewidth=2, title=\'Trend Line\')\n\n// Plot buy and sell signals\nplotshape(BuySignal == true and HideLabels == false ? Line - atrValue : na, style=shape.labelup, location=location.absolute, color=color.new(color.blue, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)\nplotshape(SellSignal == true and HideLabels == false ? Line + atrValue : na, style=shape.labeldown, location=location.absolute, color=color.new(color.red, 0), textcolor=color.new(color.white, 0), offset=0, size=size.auto)\n\n// Entry and exit strategy\nif BuySignal\n    strategy.entry(\'Buy\', strategy.long)\nif SellSignal\n    strategy.close(\'Buy\')'

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
