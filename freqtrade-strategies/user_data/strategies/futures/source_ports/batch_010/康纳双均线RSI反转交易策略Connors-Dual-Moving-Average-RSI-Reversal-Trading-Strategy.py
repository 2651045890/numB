"""Source-faithful deep-assisted port of 康纳双均线RSI反转交易策略Connors-Dual-Moving-Average-RSI-Reversal-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_064c698f(PinePortBase, IStrategy):
    source_file = '康纳双均线RSI反转交易策略Connors-Dual-Moving-Average-RSI-Reversal-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsiLength': 2, 'maLength': 200, 'exitMaLength': 5, 'overboughtThreshold': 95, 'oversoldThreshold': 5, 'stopLossPercentage': 3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input(2, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'maLength', 'op': '=', 'expr': 'input(200, title="MA Length")', 'conditions': []}, {'mode': '', 'name': 'exitMaLength', 'op': '=', 'expr': 'input(5, title="Exit MA Length")', 'conditions': []}, {'mode': '', 'name': 'overboughtThreshold', 'op': '=', 'expr': 'input(95, title="Overbought Threshold")', 'conditions': []}, {'mode': '', 'name': 'oversoldThreshold', 'op': '=', 'expr': 'input(5, title="Oversold Threshold")', 'conditions': []}, {'mode': '', 'name': 'stopLossPercentage', 'op': '=', 'expr': 'input(3, title="Stop Loss Percentage")', 'conditions': []}, {'mode': '', 'name': 'rsi2', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'ma200', 'op': '=', 'expr': 'ta.sma(close, maLength)', 'conditions': []}, {'mode': '', 'name': 'ma5_exit', 'op': '=', 'expr': 'ta.sma(close, exitMaLength)', 'conditions': []}, {'mode': '', 'name': 'positiveTrend', 'op': '=', 'expr': 'close > ma200', 'conditions': []}, {'mode': '', 'name': 'negativeTrend', 'op': '=', 'expr': 'close < ma200', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'rsi2 < oversoldThreshold and positiveTrend', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'rsi2 > overboughtThreshold and negativeTrend', 'conditions': []}, {'mode': '', 'name': 'exitLongCondition', 'op': '=', 'expr': 'close > ma5_exit', 'conditions': []}, {'mode': '', 'name': 'exitShortCondition', 'op': '=', 'expr': 'close < ma5_exit', 'conditions': []}, {'mode': '', 'name': 'stopLossLevelLong', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - stopLossPercentage / 100)', 'conditions': []}, {'mode': '', 'name': 'stopLossLevelShort', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + stopLossPercentage / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}, {'indent': 0, 'statement': 'if (exitLongCondition or close >= stopLossLevelLong)'}, {'indent': 0, 'statement': 'if (exitShortCondition or close <= stopLossLevelShort)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sellCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(exitLongCondition or close >= stopLossLevelLong)'], 'statement': 'strategy.close("Buy")'}, {'kind': 'close', 'call': 'strategy.close("Sell")', 'conditions': ['(exitShortCondition or close <= stopLossLevelShort)'], 'statement': 'strategy.close("Sell")'}]
    original_pine = '/*backtest\nstart: 2023-10-21 00:00:00\nend: 2023-11-16 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Connors RSI-MA Strategy", overlay=true)\n\n// Strategy parameters\nrsiLength = input(2, title="RSI Length")\nmaLength = input(200, title="MA Length")\nexitMaLength = input(5, title="Exit MA Length")\noverboughtThreshold = input(95, title="Overbought Threshold")\noversoldThreshold = input(5, title="Oversold Threshold")\nstopLossPercentage = input(3, title="Stop Loss Percentage")\n\n// 2-period RSI\nrsi2 = ta.rsi(close, rsiLength)\n\n// 200-period MA\nma200 = ta.sma(close, maLength)\n\n// 5-period MA for exit signals\nma5_exit = ta.sma(close, exitMaLength)\n\n// Positive trend condition\npositiveTrend = close > ma200\n\n// Negative trend condition\nnegativeTrend = close < ma200\n\n// Buy and sell conditions\nbuyCondition = rsi2 < oversoldThreshold and positiveTrend\nsellCondition = rsi2 > overboughtThreshold and negativeTrend\n\n// Exit conditions\nexitLongCondition = close > ma5_exit\nexitShortCondition = close < ma5_exit\n\n// Stop Loss\nstopLossLevelLong = strategy.position_avg_price * (1 - stopLossPercentage / 100)\nstopLossLevelShort = strategy.position_avg_price * (1 + stopLossPercentage / 100)\n\n// Strategy logic\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n\nif (exitLongCondition or close >= stopLossLevelLong)\n    strategy.close("Buy")\n\nif (exitShortCondition or close <= stopLossLevelShort)\n    strategy.close("Sell")\n\n// Plotting\nplot(ma200, title="200 MA", color=color.blue)\nplot(ma5_exit, title="Exit MA", color=color.red)\n\n// Plot stop loss levels\nplotshape(series=stopLossLevelLong, title="Long Stop Loss", color=color.green, style=shape.triangledown, size=size.small)\nplotshape(series=stopLossLevelShort, title="Short Stop Loss", color=color.red, style=shape.triangleup, size=size.small)'

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
