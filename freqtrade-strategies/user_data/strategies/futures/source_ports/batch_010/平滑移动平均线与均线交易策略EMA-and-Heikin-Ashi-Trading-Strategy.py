"""Source-faithful deep-assisted port of 平滑移动平均线与均线交易策略EMA-and-Heikin-Ashi-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_de2533f7(PinePortBase, IStrategy):
    source_file = '平滑移动平均线与均线交易策略EMA-and-Heikin-Ashi-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'price': 'close', 'MA1_Length': 15, 'MA2_Length': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.equity', '=>', 'timeframe.']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'price', 'op': '=', 'expr': 'input(close)', 'conditions': []}, {'mode': '', 'name': 'MA1_Length', 'op': '=', 'expr': 'input(15)', 'conditions': []}, {'mode': '', 'name': 'MA2_Length', 'op': '=', 'expr': 'input(50)', 'conditions': []}, {'mode': '', 'name': 'haclose', 'op': '=', 'expr': 'request.security(heikinashi(syminfo.tickerid), timeframe.period, close)', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(2018, 01, 01, 20, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'MA1', 'op': '=', 'expr': 'ema(price, MA1_Length)', 'conditions': []}, {'mode': '', 'name': 'MA2', 'op': '=', 'expr': 'ema(price, MA2_Length)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'haclose > MA1 and haclose > MA2 and MA1 > MA2 and window()', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'haclose < MA1 and haclose < MA2 and MA1 < MA2 and window()', 'conditions': []}, {'mode': '', 'name': 'MA2_color', 'op': '=', 'expr': 'long?lime:short?red:blue', 'conditions': []}, {'mode': '', 'name': 'EMA1', 'op': '=', 'expr': 'plot(MA1, title="EMA 1", style=linebr, linewidth=1, color=MA2_color)', 'conditions': []}, {'mode': '', 'name': 'EMA2', 'op': '=', 'expr': 'plot(MA2, title="EMA 2", style=linebr, linewidth=3, color=MA2_color)', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'time >= start ? true : false // create function "within window of time"'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=long)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=short)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=short)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=haclose < MA1)', 'conditions': [], 'statement': 'strategy.close("Long", when=haclose < MA1)'}, {'kind': 'close', 'call': 'strategy.close("Short", when=haclose > MA1)', 'conditions': [], 'statement': 'strategy.close("Short", when=haclose > MA1)'}]
    original_pine = '/*backtest\nstart: 2023-10-09 00:00:00\nend: 2023-10-12 02:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("EMA & Heikin Ashi", shorttitle="EMA & Heikin Ashi", overlay=true, initial_capital=1)\n\n\n// squaa\'s Strategy\n//\n// Idea by Thw on March 10, 2018.\n//\n//\n// The strategy should be used with high leverages,\n// never stop running,\n// and is always long or short.\n\n// Input\nprice = input(close)\nMA1_Length = input(15)\nMA2_Length = input(50)\n\n\nhaclose = request.security(heikinashi(syminfo.tickerid), timeframe.period, close)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(2018, 01, 01, 20, 00)  // backtest start window\nwindow()  => time >= start ? true : false // create function "within window of time"\n\n\n// Calculation\nMA1 = ema(price, MA1_Length)\nMA2 = ema(price, MA2_Length)\n\n// Strategy\nlong = haclose > MA1 and haclose > MA2 and MA1 > MA2 and window()\nshort = haclose < MA1 and haclose < MA2 and MA1 < MA2 and window()\n\n// MA trend output color\nMA2_color = long?lime:short?red:blue\n\nstrategy.entry("Long", strategy.long, when=long)\nstrategy.entry("Short", strategy.short, when=short)\nstrategy.close("Long", when=haclose < MA1)\nstrategy.close("Short", when=haclose > MA1)\n\n\n// MA output\nEMA1 = plot(MA1, title="EMA 1", style=linebr, linewidth=1, color=MA2_color)\nEMA2 = plot(MA2, title="EMA 2", style=linebr, linewidth=3, color=MA2_color)\nfill(EMA1, EMA2, color=silver, transp=50)\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

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
