"""Source-faithful deep-assisted port of 确认型均线交叉动量策略-Confirmed-SMA-Crossover-Momentum-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_147a4c36(PinePortBase, IStrategy):
    source_file = '确认型均线交叉动量策略-Confirmed-SMA-Crossover-Momentum-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'shortSmaLength': 10, 'longSmaLength': 30, 'stopLossPercent': 1.0, 'takeProfitPercent': 10.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'shortSmaLength', 'op': '=', 'expr': 'input.int(10, title="Short SMA Length")', 'conditions': []}, {'mode': '', 'name': 'longSmaLength', 'op': '=', 'expr': 'input.int(30, title="Long SMA Length")', 'conditions': []}, {'mode': '', 'name': 'stopLossPercent', 'op': '=', 'expr': 'input.float(1.0, title="Stop Loss (%)", step=0.1) / 100', 'conditions': []}, {'mode': '', 'name': 'takeProfitPercent', 'op': '=', 'expr': 'input.float(10.0, title="Take Profit (%)", step=0.1) / 100', 'conditions': []}, {'mode': '', 'name': 'shortSma', 'op': '=', 'expr': 'ta.sma(close, shortSmaLength)', 'conditions': []}, {'mode': '', 'name': 'longSma', 'op': '=', 'expr': 'ta.sma(close, longSmaLength)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'ta.crossover(shortSma[1], longSma[1]) and shortSma > longSma', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'ta.crossunder(shortSma[1], longSma[1]) and longSma > shortSma', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}, {'indent': 0, 'statement': 'if (sellCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Long", strategy.long, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))', 'conditions': ['(sellCondition)'], 'statement': 'strategy.entry("Short", strategy.short, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))'}]
    original_pine = '/*backtest\nstart: 2023-07-20 00:00:00\nend: 2024-07-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SMA Crossover Strategy with Confirmation", overlay=true)\n\n// Input settings\nshortSmaLength = input.int(10, title="Short SMA Length")\nlongSmaLength = input.int(30, title="Long SMA Length")\nstopLossPercent = input.float(1.0, title="Stop Loss (%)", step=0.1) / 100\ntakeProfitPercent = input.float(10.0, title="Take Profit (%)", step=0.1) / 100\n\n// Calculations\nshortSma = ta.sma(close, shortSmaLength)\nlongSma = ta.sma(close, longSmaLength)\n\n// Buy signal: Short SMA crosses above Long SMA and holds for one bar\nbuyCondition = ta.crossover(shortSma[1], longSma[1]) and shortSma > longSma\n\n// Sell signal: Long SMA crosses above Short SMA and holds for one bar\nsellCondition = ta.crossunder(shortSma[1], longSma[1]) and longSma > shortSma\n\n// Execute strategy orders\nif (buyCondition)\n    strategy.entry("Long", strategy.long, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))\n\nif (sellCondition)\n    strategy.entry("Short", strategy.short, stop=close * (1 - stopLossPercent), limit=close * (1 + takeProfitPercent))\n\n// Plotting\nplot(shortSma, title="Short SMA", color=color.blue)\nplot(longSma, title="Long SMA", color=color.red)\n\n// Signal markers on price chart\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sellCondition, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")'

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
