"""Source-faithful deep-assisted port of 慢速RSI超买超卖策略Slow-RSI-OB-OS-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c3d9d4b9(PinePortBase, IStrategy):
    source_file = '慢速RSI超买超卖策略Slow-RSI-OB-OS-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'price': 'ohlc4', 'len': 500, 'smoother': 250, 'OB': 52, 'OS': 48}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'price', 'op': '=', 'expr': 'input(ohlc4, title="Price Source")', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(500, minval=1, step=5, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'smoother', 'op': '=', 'expr': 'input(250, minval=1, step=5, title="RSI SMA")', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'rma(max(change(price), 0), len)', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': 'rma(-min(change(price), 0), len)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))', 'conditions': []}, {'mode': '', 'name': 'EmaRSI', 'op': '=', 'expr': 'ema(rsi,smoother)', 'conditions': []}, {'mode': '', 'name': 'OB', 'op': '=', 'expr': 'input(52, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'OS', 'op': '=', 'expr': 'input(48, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'change(EmaRSI) > 0 and EmaRSI <= 50 and crossover(EmaRSI, OS)', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'change(EmaRSI) < 0 and EmaRSI >= 50 and crossunder(EmaRSI, OB)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)'}]
    original_pine = '/*backtest\nstart: 2023-12-20 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n// Wilder was a very influential man when it comes to TA. However, I\'m one to always try to think outside the box. \n// While Wilder recommended that the RSI be used only with a 14 bar lookback period, I on the other hand think there is a lot to learn from RSI if one simply slows down the lookback period \n// Same applies for MACD.\n// Every market has its dynmaics. So don\'t narrow your mind by thinking my source code input levels are the only levels that work.\n// Since the long lookback period weakens the plot volatility, again, one must think outside the box when trying to guage overbought and oversold levels. \n\n// Good luck and don\'t bash me if some off-the-wall FA spurned divergence causes you to lose money.\n// And NO this doesn\'t repaint and I won\'t answer those who ask. \n//@version=4\n\nstrategy("SLOW RSI OB/OS Strategy", overlay=false)\nprice = input(ohlc4, title="Price Source")\nlen = input(500, minval=1, step=5,  title="RSI Length")\nsmoother = input(250, minval=1, step=5, title="RSI SMA")\nup = rma(max(change(price), 0), len)\ndown = rma(-min(change(price), 0), len)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\nEmaRSI = ema(rsi,smoother)\nplot(EmaRSI, title="EmaRSI", style=line, linewidth=1, color=yellow)\n\n\nOB = input(52, step=0.1)\nOS = input(48, step=0.1)\nhline(OB, linewidth=1, color=red)\nhline(OS,linewidth=1, color=green)\nhline(50,linewidth=1, color=gray)\n\n\nlong = change(EmaRSI) > 0 and EmaRSI <= 50 and crossover(EmaRSI, OS)\nshort = change(EmaRSI) < 0 and EmaRSI >= 50 and crossunder(EmaRSI, OB)\n\n\nstrategy.entry("Long", strategy.long, when=long) //_signal or long) //or closeshort_signal)\nstrategy.entry("Short", strategy.short, when=short) //_signal or short) // or closelong_signal)\n\n// If you want to try to play with exits you can activate these!\n\n//closelong = crossunder(EmaRSI, 0) //or crossunder(EmaRSI, OS)\n//closeshort = crossover(EmaRSI, 0) //or crossover(EmaRSI, OB)\n\n//strategy.close("Long", when=closelong)\n//strategy.close("Short", when=closeshort)'

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
