"""Source-faithful deep-assisted port of 底部猎人策略Bottom-Hunter-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_8da922ac(PinePortBase, IStrategy):
    source_file = '底部猎人策略Bottom-Hunter-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fastLength': 12, 'slowLength': 26, 'signalSmoothing': 9, 'rsiLength': 14, 'length': 20, 'src': 'close', 'mult': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input.int(12, "Fast Length")', 'conditions': []}, {'mode': '', 'name': 'slowLength', 'op': '=', 'expr': 'input.int(26, "Slow Length")', 'conditions': []}, {'mode': '', 'name': 'signalSmoothing', 'op': '=', 'expr': 'input.int(9, "Signal Smoothing")', 'conditions': []}, {'mode': '', 'name': 'ema99', 'op': '=', 'expr': 'ta.ema(close, 99)', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input.int(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(20, "BB Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, "Source")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input.float(2.0, "BB StdDev")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(src, length)', 'conditions': []}, {'mode': '', 'name': 'priceLow', 'op': '=', 'expr': 'ta.lowest(low[1], 60)', 'conditions': []}, {'mode': '', 'name': 'macdLow', 'op': '=', 'expr': 'ta.lowest(macdLine[1], 60)', 'conditions': []}, {'mode': '', 'name': 'divergence', 'op': '=', 'expr': 'low < priceLow and macdLine > macdLow', 'conditions': []}, {'mode': '', 'name': 'allHighsBelowEma99', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'allHighsBelowEma99', 'op': ':=', 'expr': 'false', 'conditions': ['high[i] > ema99']}, {'mode': '', 'name': 'rsiBelow', 'op': '=', 'expr': 'rsi < 31.1', 'conditions': []}, {'mode': '', 'name': 'priceDifference', 'op': '=', 'expr': '(high - low) / low * 100', 'conditions': []}, {'mode': '', 'name': 'buySignal1', 'op': '=', 'expr': 'divergence and allHighsBelowEma99 and rsiBelow', 'conditions': []}, {'mode': '', 'name': 'buySignal2', 'op': '=', 'expr': 'high < ema99 and priceDifference >= 3 and close < open and high < basis', 'conditions': []}, {'mode': '', 'name': 'buySignal3', 'op': '=', 'expr': 'buySignal1 or buySignal2', 'conditions': []}, {'mode': 'var', 'name': 'buyPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'buyPrice', 'op': ':=', 'expr': 'close // 存储买入时的价格', 'conditions': ['buySignal3']}, {'mode': '', 'name': 'longTakeProfit', 'op': '=', 'expr': 'buyPrice * 1.1 // 止盈设为买入价格的1.2倍', 'conditions': []}, {'mode': '', 'name': 'longStopLoss', 'op': '=', 'expr': 'buyPrice * 0.98// 止损设为买入价格的0.99倍', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'for i = 0 to 14'}, {'indent': 4, 'statement': 'if high[i] > ema99'}, {'indent': 0, 'statement': 'if buySignal3'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buySignal3'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit", "Buy", limit=longTakeProfit, stop=longStopLoss)', 'conditions': [], 'statement': 'strategy.exit("Exit", "Buy", limit=longTakeProfit, stop=longStopLoss)'}]
    original_pine = '/*backtest\nstart: 2023-01-30 00:00:00\nend: 2024-02-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("MACD Divergence Strategy", shorttitle="Strategy: MACD Dive", overlay=true)\n\n// MACD设置\nfastLength = input.int(12, "Fast Length")\nslowLength = input.int(26, "Slow Length")\nsignalSmoothing = input.int(9, "Signal Smoothing")\n\n[macdLine, signalLine, _] = ta.macd(close, fastLength, slowLength, signalSmoothing)\n\n// 计算99日EMA均线\nema99 = ta.ema(close, 99)\n\n// 计算RSI\nrsiLength = input.int(14, title="RSI Length")\nrsi = ta.rsi(close, rsiLength)\n\n// 计算布林带中轨\nlength = input.int(20, "BB Length")\nsrc = input(close, "Source")\nmult = input.float(2.0, "BB StdDev")\nbasis = ta.sma(src, length)\n\n// 买入筛选条件\npriceLow = ta.lowest(low[1], 60)\nmacdLow = ta.lowest(macdLine[1], 60)\ndivergence = low < priceLow and macdLine > macdLow\n\nallHighsBelowEma99 = true\nfor i = 0 to 14\n    if high[i] > ema99\n        allHighsBelowEma99 := false\n\nrsiBelow = rsi < 31.1\npriceDifference = (high - low) / low * 100\n\nbuySignal1 = divergence and allHighsBelowEma99 and rsiBelow\nbuySignal2 = high < ema99 and priceDifference >= 3 and close < open and high < basis \nbuySignal3 = buySignal1 or buySignal2\n\n// 定义一个变量来存储买入时的价格\nvar float buyPrice = na\n\n// 买入逻辑\nif buySignal3\n    buyPrice := close // 存储买入时的价格\n    strategy.entry("Buy", strategy.long)\n\n// 止盈和止损条件\nlongTakeProfit = buyPrice * 1.1 // 止盈设为买入价格的1.2倍\nlongStopLoss = buyPrice * 0.98// 止损设为买入价格的0.99倍\n\n// 应用止盈和止损\nstrategy.exit("Exit", "Buy", limit=longTakeProfit, stop=longStopLoss)\n// 绘制买入信号\nplotshape(series=buySignal3, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.triangleup, size=size.small)'

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
