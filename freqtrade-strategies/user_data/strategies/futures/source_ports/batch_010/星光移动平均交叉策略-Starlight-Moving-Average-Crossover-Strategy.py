"""Source-faithful deep-assisted port of 星光移动平均交叉策略-Starlight-Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_25ece5ac(PinePortBase, IStrategy):
    source_file = '星光移动平均交叉策略-Starlight-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'shortLength': 20, 'longLength': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'shortLength', 'op': '=', 'expr': 'input.int(20, title="Short Moving Average Length")', 'conditions': []}, {'mode': '', 'name': 'longLength', 'op': '=', 'expr': 'input.int(50, title="Long Moving Average Length")', 'conditions': []}, {'mode': '', 'name': 'shortMA', 'op': '=', 'expr': 'ta.sma(close, shortLength)', 'conditions': []}, {'mode': '', 'name': 'longMA', 'op': '=', 'expr': 'ta.sma(close, longLength)', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'ta.crossover(shortMA, longMA)', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'ta.crossunder(shortMA, longMA)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buySignal)'}, {'indent': 0, 'statement': 'if (sellSignal)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buySignal)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy")', 'conditions': ['(sellSignal)'], 'statement': 'strategy.close("Buy")'}]
    original_pine = '/*backtest\nstart: 2023-05-28 00:00:00\nend: 2024-06-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Starlight Strategy", overlay=true)\n\n// Define the inputs for the moving averages\nshortLength = input.int(20, title="Short Moving Average Length")\nlongLength = input.int(50, title="Long Moving Average Length")\n\n// Calculate the moving averages\nshortMA = ta.sma(close, shortLength)\nlongMA = ta.sma(close, longLength)\n\n// Calculate MACD\n[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)\n\n// Plot the moving averages\nplot(shortMA, color=color.orange, title="Short Moving Average")\nplot(longMA, color=color.green, title="Long Moving Average")\n\n// Plot MACD on a separate chart\nhline(0, "Zero Line", color=color.gray)\nplot(macdLine, color=color.red, title="MACD Line")\nplot(signalLine, color=color.purple, title="Signal Line")\n\n// Generate buy and sell signals\nbuySignal = ta.crossover(shortMA, longMA)\nsellSignal = ta.crossunder(shortMA, longMA)\n\n// Plot buy and sell signals\nplotshape(series=buySignal, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="BUY")\nplotshape(series=sellSignal, title="Sell Signal", location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL")\n\n// Strategy execution\nif (buySignal)\n    strategy.entry("Buy", strategy.long)\nif (sellSignal)\n    strategy.close("Buy")'

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
