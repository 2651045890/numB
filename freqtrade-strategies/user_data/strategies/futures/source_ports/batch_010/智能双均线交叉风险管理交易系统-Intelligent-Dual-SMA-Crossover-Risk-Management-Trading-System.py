"""Source-faithful deep-assisted port of 智能双均线交叉风险管理交易系统-Intelligent-Dual-SMA-Crossover-Risk-Management-Trading-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_788a4ace(PinePortBase, IStrategy):
    source_file = '智能双均线交叉风险管理交易系统-Intelligent-Dual-SMA-Crossover-Risk-Management-Trading-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'shortSMA': 9, 'longSMA': 21, 'riskPercent': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.equity', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'shortSMA', 'op': '=', 'expr': 'input.int(9, title="Short SMA")', 'conditions': []}, {'mode': '', 'name': 'longSMA', 'op': '=', 'expr': 'input.int(21, title="Long SMA")', 'conditions': []}, {'mode': '', 'name': 'riskPercent', 'op': '=', 'expr': 'input.float(1.0, title="Risk Percentage", step=0.1)', 'conditions': []}, {'mode': '', 'name': 'shortSMAValue', 'op': '=', 'expr': 'ta.sma(close, shortSMA)', 'conditions': []}, {'mode': '', 'name': 'longSMAValue', 'op': '=', 'expr': 'ta.sma(close, longSMA)', 'conditions': []}, {'mode': '', 'name': 'bullishSignal', 'op': '=', 'expr': 'ta.crossover(shortSMAValue, longSMAValue)', 'conditions': []}, {'mode': '', 'name': 'bearishSignal', 'op': '=', 'expr': 'ta.crossunder(shortSMAValue, longSMAValue)', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'riskPercent / 100', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': 'stopLossPercent * 2', 'conditions': []}, {'mode': '', 'name': 'riskAmount', 'op': '=', 'expr': 'strategy.equity * riskPercent / 100', 'conditions': []}, {'mode': 'var', 'name': 'buyStopLossPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'buyTakeProfitPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'sellStopLossPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'var', 'name': 'sellTakeProfitPrice', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'buyStopLossPrice', 'op': ':=', 'expr': 'close * (1 - stopLossPercent)', 'conditions': ['(bullishSignal)']}, {'mode': '', 'name': 'buyTakeProfitPrice', 'op': ':=', 'expr': 'close * (1 + takeProfitPercent)', 'conditions': ['(bullishSignal)']}, {'mode': '', 'name': 'sellStopLossPrice', 'op': ':=', 'expr': 'close * (1 + stopLossPercent)', 'conditions': ['(bearishSignal)']}, {'mode': '', 'name': 'sellTakeProfitPrice', 'op': ':=', 'expr': 'close * (1 - takeProfitPercent)', 'conditions': ['(bearishSignal)']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (bullishSignal)'}, {'indent': 0, 'statement': 'if (bearishSignal)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(bullishSignal)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=buyTakeProfitPrice, stop=buyStopLossPrice)', 'conditions': ['(bullishSignal)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=buyTakeProfitPrice, stop=buyStopLossPrice)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['(bearishSignal)'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=sellTakeProfitPrice, stop=sellStopLossPrice)', 'conditions': ['(bearishSignal)'], 'statement': 'strategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=sellTakeProfitPrice, stop=sellStopLossPrice)'}]
    original_pine = '/*backtest\nstart: 2024-06-09 00:00:00\nend: 2025-02-19 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=6\nstrategy("AI Trade Bot with Risk Management", overlay=true)\n\n// Input parameters\nshortSMA = input.int(9, title="Short SMA")\nlongSMA = input.int(21, title="Long SMA")\nriskPercent = input.float(1.0, title="Risk Percentage", step=0.1)\n\n// Calculate SMAs\nshortSMAValue = ta.sma(close, shortSMA)\nlongSMAValue = ta.sma(close, longSMA)\n\n// Bullish and Bearish Signals\nbullishSignal = ta.crossover(shortSMAValue, longSMAValue)\nbearishSignal = ta.crossunder(shortSMAValue, longSMAValue)\n\n// Risk Management\nstopLossPercent = riskPercent / 100\ntakeProfitPercent = stopLossPercent * 2\n\n// Calculate position size based on risk management\nriskAmount = strategy.equity * riskPercent / 100\n\nvar float buyStopLossPrice = na\nvar float buyTakeProfitPrice = na\nvar float sellStopLossPrice = na\nvar float sellTakeProfitPrice = na\n\nif (bullishSignal)\n    buyStopLossPrice := close * (1 - stopLossPercent)\n    buyTakeProfitPrice := close * (1 + takeProfitPercent)\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Buy", limit=buyTakeProfitPrice, stop=buyStopLossPrice)\n\nif (bearishSignal)\n    sellStopLossPrice := close * (1 + stopLossPercent)\n    sellTakeProfitPrice := close * (1 - takeProfitPercent)\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", from_entry="Sell", limit=sellTakeProfitPrice, stop=sellStopLossPrice)\n\n// Plot SMAs on the chart\nplot(shortSMAValue, color=color.blue, title="Short SMA")\nplot(longSMAValue, color=color.red, title="Long SMA")\n\n// Plot Buy/Sell signals on the chart\nplotshape(series=bullishSignal, location=location.belowbar, color=color.green, style=shape.labelup, title="Buy Signal", text="BUY")\nplotshape(series=bearishSignal, location=location.abovebar, color=color.red, style=shape.labeldown, title="Sell Signal", text="SELL")\n\n// Plot Buy Stop Loss and Take Profit levels\nplot(buyStopLossPrice, color=color.red, style=plot.style_linebr, linewidth=2, title="Buy Stop Loss")\nplot(buyTakeProfitPrice, color=color.green, style=plot.style_linebr, linewidth=2, title="Buy Take Profit")\n\n// Plot Sell Stop Loss and Take Profit levels\nplot(sellStopLossPrice, color=color.red, style=plot.style_linebr, linewidth=2, title="Sell Stop Loss")\nplot(sellTakeProfitPrice, color=color.green, style=plot.style_linebr, linewidth=2, title="Sell Take Profit")'

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
