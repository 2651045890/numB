"""Source-faithful deep-assisted port of 布林带高频量化策略结合过高低点突破的多空策略-Bollinger-Bands-High-Frequency-Quantitative-Strategy-Combined-with-High-Low-Breakout-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_90ad1159(PinePortBase, IStrategy):
    source_file = '布林带高频量化策略结合过高低点突破的多空策略-Bollinger-Bands-High-Frequency-Quantitative-Strategy-Combined-with-High-Low-Breakout-System.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'bbLength': 20, 'stdDev': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ', 'line.']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'bbLength', 'op': '=', 'expr': 'input(20, title="Bollinger Bands Length")', 'conditions': []}, {'mode': '', 'name': 'stdDev', 'op': '=', 'expr': 'input(2.0, title="Bollinger Bands Std Dev")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(close, bbLength)', 'conditions': []}, {'mode': '', 'name': 'deviation', 'op': '=', 'expr': 'stdDev * ta.stdev(close, bbLength)', 'conditions': []}, {'mode': '', 'name': 'upperBB', 'op': '=', 'expr': 'basis + deviation', 'conditions': []}, {'mode': '', 'name': 'lowerBB', 'op': '=', 'expr': 'basis - deviation', 'conditions': []}, {'mode': '', 'name': 'prevHigh', 'op': '=', 'expr': 'high[1] // Previous candle high', 'conditions': []}, {'mode': '', 'name': 'prevLow', 'op': '=', 'expr': 'low[1] // Previous candle low', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'ta.crossover(high, prevHigh) and (prevHigh < lowerBB[1])', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'ta.crossunder(low, prevLow) and (prevLow > upperBB[1])', 'conditions': []}, {'mode': '', 'name': 'stopLossPrice', 'op': '=', 'expr': 'prevLow', 'conditions': ['(buyCondition)']}, {'mode': '', 'name': 'targetPrice', 'op': '=', 'expr': 'prevHigh + (prevHigh - stopLossPrice) // 1:1 RR target', 'conditions': ['(buyCondition)']}, {'mode': '', 'name': 'stopLossPriceSell', 'op': '=', 'expr': 'prevHigh', 'conditions': ['(sellCondition)']}, {'mode': '', 'name': 'targetPriceSell', 'op': '=', 'expr': 'prevLow - (stopLossPriceSell - prevLow) // 1:1 RR target', 'conditions': ['(sellCondition)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell", "Buy", limit=targetPrice, stop=stopLossPrice)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.exit("Sell", "Buy", limit=targetPrice, stop=stopLossPrice)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(sellCondition)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Cover", "Sell", limit=targetPriceSell, stop=stopLossPriceSell)', 'conditions': ['(sellCondition)'], 'statement': 'strategy.exit("Cover", "Sell", limit=targetPriceSell, stop=stopLossPriceSell)'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-12-03 00:00:00\nperiod: 2d\nbasePeriod: 2d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bollinger Band Scalping", overlay=true)\n\n// Input for Bollinger Bands length and standard deviation\nbbLength = input(20, title="Bollinger Bands Length")\nstdDev = input(2.0, title="Bollinger Bands Std Dev")\n\n// Calculate and plot the Bollinger Bands\nbasis = ta.sma(close, bbLength)\ndeviation = stdDev * ta.stdev(close, bbLength)\nupperBB = basis + deviation\nlowerBB = basis - deviation\n\n// Get previous candle\'s values\nprevHigh = high[1]   // Previous candle high\nprevLow = low[1]     // Previous candle low\n\n// Buy Signal Condition: Current high crossed above previous high and previous high is below the lower Bollinger Band\nbuyCondition = ta.crossover(high, prevHigh) and (prevHigh < lowerBB[1])\n\n// Sell Signal Condition: Current low crossed below previous low and previous low is above the upper Bollinger Band\nsellCondition = ta.crossunder(low, prevLow) and (prevLow > upperBB[1])\n\n// Entry and exit for Buy signals\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n    // Calculate target and stop loss\n    stopLossPrice = prevLow\n    targetPrice = prevHigh + (prevHigh - stopLossPrice)  // 1:1 RR target\n\n    // Set stop loss and target orders\n    strategy.exit("Sell", "Buy", limit=targetPrice, stop=stopLossPrice)\n\n    // // Plot entry line\n    // line.new(x1=bar_index, y1=prevHigh, x2=bar_index + 12, y2=prevHigh, color=color.green, width=2, style=line.style_solid)\n    // // Plot stop loss line\n    // line.new(x1=bar_index, y1=stopLossPrice, x2=bar_index + 12, y2=stopLossPrice, color=color.red, width=1, style=line.style_dashed)\n    // // Plot target line\n    // line.new(x1=bar_index, y1=targetPrice, x2=bar_index + 12, y2=targetPrice, color=color.blue, width=2, style=line.style_solid)\n\n// Entry and exit for Sell signals\nif (sellCondition)\n    strategy.entry("Sell", strategy.short)\n    // Calculate target and stop loss\n    stopLossPriceSell = prevHigh\n    targetPriceSell = prevLow - (stopLossPriceSell - prevLow)  // 1:1 RR target\n\n    // Set stop loss and target orders\n    strategy.exit("Cover", "Sell", limit=targetPriceSell, stop=stopLossPriceSell)\n\n    // // Plot entry line\n    // line.new(x1=bar_index, y1=prevLow, x2=bar_index + 12, y2=prevLow, color=color.red, width=2, style=line.style_solid)\n    // // Plot stop loss line\n    // line.new(x1=bar_index, y1=stopLossPriceSell, x2=bar_index + 12, y2=stopLossPriceSell, color=color.green, width=1, style=line.style_dashed)\n    // // Plot target line\n    // line.new(x1=bar_index, y1=targetPriceSell, x2=bar_index + 12, y2=targetPriceSell, color=color.blue, width=2, style=line.style_solid)\n\n// Plotting Bollinger Bands with 70% transparency\nplot(upperBB, color=color.red, title="Upper Bollinger Band", transp=70)\nplot(lowerBB, color=color.green, title="Lower Bollinger Band", transp=70)\nplot(basis, color=color.blue, title="Middle Band", transp=70)'

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
