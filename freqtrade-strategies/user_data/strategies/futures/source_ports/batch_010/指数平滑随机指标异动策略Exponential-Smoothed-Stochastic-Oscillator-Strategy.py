"""Source-faithful deep-assisted port of 指数平滑随机指标异动策略Exponential-Smoothed-Stochastic-Oscillator-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_28934230(PinePortBase, IStrategy):
    source_file = '指数平滑随机指标异动策略Exponential-Smoothed-Stochastic-Oscillator-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'len': 14, 'ex': 2, 'bot': 20, 'top': 80}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'len', 'op': '=', 'expr': 'input.int(14, "length")', 'conditions': []}, {'mode': '', 'name': 'ex', 'op': '=', 'expr': 'input.int(2, title="exp", minval=1, maxval=10)', 'conditions': []}, {'mode': '', 'name': 'exp', 'op': '=', 'expr': 'ex<10? (ex)/(10-ex) : 99', 'conditions': []}, {'mode': '', 'name': 's', 'op': '=', 'expr': '100 * (close - ta.lowest(low, len)) / (ta.highest(high, len) - ta.lowest(low, len))', 'conditions': []}, {'mode': '', 'name': 'ks', 'op': '=', 'expr': 's>50? math.pow(math.abs(s-50),exp)/math.pow(50,exp-1)+50 :', 'conditions': []}, {'mode': '', 'name': 'bot', 'op': '=', 'expr': 'input.int(20)', 'conditions': []}, {'mode': '', 'name': 'top', 'op': '=', 'expr': 'input.int(80)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(ks, bot) and bar_index>0', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(ks, top) and bar_index>0', 'conditions': []}, {'mode': '', 'name': 'h1', 'op': '=', 'expr': 'hline(top)', 'conditions': []}, {'mode': '', 'name': 'h2', 'op': '=', 'expr': 'hline(bot)', 'conditions': []}, {'mode': '', 'name': 'h3', 'op': '=', 'expr': 'hline(100)', 'conditions': []}, {'mode': '', 'name': 'h4', 'op': '=', 'expr': 'hline(0)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-01-11 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © faytterro\n\n//@version=5\nstrategy("Exponential Stochastic Strategy", overlay=false, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\nlen=input.int(14, "length") \nex=input.int(2, title="exp", minval=1, maxval=10)\nexp= ex<10? (ex)/(10-ex) : 99\ns=100 * (close - ta.lowest(low, len)) / (ta.highest(high, len) - ta.lowest(low, len))\nks=s>50? math.pow(math.abs(s-50),exp)/math.pow(50,exp-1)+50 :\n -math.pow(math.abs(s-50),exp)/math.pow(50,exp-1)+50\nplot(ks, color= color.white)\nbot=input.int(20)\ntop=input.int(80)\nlongCondition = ta.crossover(ks, bot) and bar_index>0\nif (longCondition)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nshortCondition = ta.crossunder(ks, top) and bar_index>0\nif (shortCondition)\n    strategy.entry("My Short Entry Id", strategy.short)\n//    strategy.close("My Long Entry Id")\nalertcondition(longCondition, title = "buy")\nalertcondition(shortCondition, title = "sell")\nh1=hline(top)\nh2=hline(bot)\nh3=hline(100)\nh4=hline(0)\nfill(h1,h3, color= color.rgb(255,0,0,200-top*2))\nfill(h2,h4, color= color.rgb(0,255,0,bot*2))'

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
