"""Source-faithful deep-assisted port of 改进型多指标动量交易策略-Enhanced-Multi-Indicator-Momentum-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_39a27e1c(PinePortBase, IStrategy):
    source_file = '改进型多指标动量交易策略-Enhanced-Multi-Indicator-Momentum-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'volumePeriod': 3, 'atrPeriod': 14, 'atrMultiplierSL': 1.5, 'atrMultiplierTP': 2.5, 'emaPeriod': 200}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ', 'label.']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'volumePeriod', 'op': '=', 'expr': 'input.int(3, "Volume Period", minval=2, maxval=5)', 'conditions': []}, {'mode': '', 'name': 'atrPeriod', 'op': '=', 'expr': 'input.int(14, "ATR Period")', 'conditions': []}, {'mode': '', 'name': 'atrMultiplierSL', 'op': '=', 'expr': 'input.float(1.5, "ATR Multiplier for Stop Loss")', 'conditions': []}, {'mode': '', 'name': 'atrMultiplierTP', 'op': '=', 'expr': 'input.float(2.5, "ATR Multiplier for Take Profit")', 'conditions': []}, {'mode': '', 'name': 'emaPeriod', 'op': '=', 'expr': 'input.int(200, "EMA Period")', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'ta.atr(atrPeriod)', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.ema(close, emaPeriod)', 'conditions': []}, {'mode': '', 'name': 'volumeUp', 'op': '=', 'expr': 'close > open', 'conditions': []}, {'mode': '', 'name': 'volumeDown', 'op': '=', 'expr': 'close < open', 'conditions': []}, {'mode': '', 'name': 'consecutiveUpVolume', 'op': '=', 'expr': 'volumeUp and volumeUp[1] and volumeUp[2]', 'conditions': []}, {'mode': '', 'name': 'consecutiveDownVolume', 'op': '=', 'expr': 'volumeDown and volumeDown[1] and volumeDown[2]', 'conditions': []}, {'mode': '', 'name': 'volumeRatio', 'op': '=', 'expr': 'volume / ta.sma(volume, volumePeriod)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'consecutiveUpVolume and volumeRatio > 1.5 and close > ema', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'consecutiveDownVolume and volumeRatio > 1.5 and close < ema', 'conditions': []}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'low - atr * atrMultiplierSL', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'high + atr * atrMultiplierTP', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'labelText', 'op': '=', 'expr': '"多：" + str.tostring(close, "#.##") + " 倍率:" + str.tostring(volumeRatio, "#.##") + " \\n止盈:" + str.tostring(takeProfit, "#.##") + " \\n止損:" + str.tostring(stopLoss, "#.##")', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'high + atr * atrMultiplierSL', 'conditions': ['(shortCondition)']}, {'mode': '', 'name': 'takeProfit', 'op': '=', 'expr': 'low - atr * atrMultiplierTP', 'conditions': ['(shortCondition)']}, {'mode': '', 'name': 'labelText', 'op': '=', 'expr': '"空：" + str.tostring(close, "#.##") + " 倍率:" + str.tostring(volumeRatio, "#.##") + " \\n止盈:" + str.tostring(takeProfit, "#.##") + " \\n止損:" + str.tostring(stopLoss, "#.##")', 'conditions': ['(shortCondition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", "Long", stop=stopLoss, limit=takeProfit)', 'conditions': ['(longCondition)'], 'statement': 'strategy.exit("Exit Long", "Long", stop=stopLoss, limit=takeProfit)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Short", "Short", stop=stopLoss, limit=takeProfit)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.exit("Exit Short", "Short", stop=stopLoss, limit=takeProfit)'}]
    original_pine = '/*backtest\nstart: 2023-07-20 00:00:00\nend: 2024-07-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Improved Volume Based Strategy", overlay=true)\n\n// 參數\nvolumePeriod = input.int(3, "Volume Period", minval=2, maxval=5)\natrPeriod = input.int(14, "ATR Period")\natrMultiplierSL = input.float(1.5, "ATR Multiplier for Stop Loss")\natrMultiplierTP = input.float(2.5, "ATR Multiplier for Take Profit")\nemaPeriod = input.int(200, "EMA Period")\n\n// 指標計算\natr = ta.atr(atrPeriod)\nema = ta.ema(close, emaPeriod)\n\n// 判斷成交量方向\nvolumeUp = close > open\nvolumeDown = close < open\n\n// 檢查連續K線的成交量方向\nconsecutiveUpVolume = volumeUp and volumeUp[1] and volumeUp[2]\nconsecutiveDownVolume = volumeDown and volumeDown[1] and volumeDown[2]\n\n// 計算成交量倍率\nvolumeRatio = volume / ta.sma(volume, volumePeriod)\n\n// 入場條件\nlongCondition = consecutiveUpVolume and volumeRatio > 1.5 and close > ema\nshortCondition = consecutiveDownVolume and volumeRatio > 1.5 and close < ema\n\n// 執行策略\nif (longCondition)\n    stopLoss = low - atr * atrMultiplierSL\n    takeProfit = high + atr * atrMultiplierTP\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", "Long", stop=stopLoss, limit=takeProfit)\n    labelText = "多：" + str.tostring(close, "#.##") + " 倍率:" + str.tostring(volumeRatio, "#.##") + " \\n止盈:" + str.tostring(takeProfit, "#.##") + " \\n止損:" + str.tostring(stopLoss, "#.##")\n    label.new(bar_index, low - atr * 2, text=labelText, color=color.green, textcolor=color.white, style=label.style_label_up)\n\nif (shortCondition)\n    stopLoss = high + atr * atrMultiplierSL\n    takeProfit = low - atr * atrMultiplierTP\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", "Short", stop=stopLoss, limit=takeProfit)\n    labelText = "空：" + str.tostring(close, "#.##") + " 倍率:" + str.tostring(volumeRatio, "#.##") + " \\n止盈:" + str.tostring(takeProfit, "#.##") + " \\n止損:" + str.tostring(stopLoss, "#.##")\n    label.new(bar_index, high + atr * 2, text=labelText, color=color.red, textcolor=color.white, style=label.style_label_down)\n\n// 繪製指標\nplot(ema, color=color.blue, title="EMA")'

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
