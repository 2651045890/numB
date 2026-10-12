"""Source-faithful deep-assisted port of 收益捕捉策略在趋势反转市的应用Scalping-Strategy-in-Trend-Reversal-Market.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f9abf2bd(PinePortBase, IStrategy):
    source_file = '收益捕捉策略在趋势反转市的应用Scalping-Strategy-in-Trend-Reversal-Market.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'x_src': 'hl2', 'x_len_a': 5, 'x_len_b': 60, 'x_k_b': 13, 'x_changk': 15, 'x_rsi_ct': 35.0, 'x_rsi_ft': 50.0, 'x_exit_if_reason_over': False}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'x_src', 'op': '=', 'expr': 'input( hl2 , title="Source" )', 'conditions': []}, {'mode': '', 'name': 'x_len_a', 'op': '=', 'expr': 'input( 5 , title="short term trend" , minval=1 )', 'conditions': []}, {'mode': '', 'name': 'x_len_b', 'op': '=', 'expr': 'input( 60 , title="long term trend" , minval=1 )', 'conditions': []}, {'mode': '', 'name': 'x_k_b', 'op': '=', 'expr': 'input( 13 , title="smooth long term trend" , minval=1 )', 'conditions': []}, {'mode': '', 'name': 'x_changk', 'op': '=', 'expr': 'input( 15 , title="clear short term pullback appears recently" , minval=1 )', 'conditions': []}, {'mode': '', 'name': 'x_rsi_ct', 'op': '=', 'expr': 'input( 35.0 , title="threshold of short term pullback clear" , minval=0.0 , maxval=100.0 )', 'conditions': []}, {'mode': '', 'name': 'x_rsi_ft', 'op': '=', 'expr': 'input( 50.0 , title="threshold of short term pullback end" , minval=0.0 , maxval=100.0 )', 'conditions': []}, {'mode': '', 'name': 'x_exit_if_reason_over', 'op': '=', 'expr': 'input(false)', 'conditions': []}, {'mode': '', 'name': 'y_stoch', 'op': '=', 'expr': 'stoch( x_src , high , low , x_len_b )', 'conditions': []}, {'mode': '', 'name': 'y_k', 'op': '=', 'expr': 'sma( y_stoch , x_k_b )', 'conditions': []}, {'mode': '', 'name': 'y_rsi', 'op': '=', 'expr': 'rsi( x_src , x_len_a )', 'conditions': []}, {'mode': '', 'name': 'y_upper', 'op': '=', 'expr': 'min( y_k-50 , y_rsi-x_rsi_ft , x_changk>1?x_rsi_ct-lowest(y_rsi,x_changk):50 )', 'conditions': []}, {'mode': '', 'name': 'y_lower', 'op': '=', 'expr': 'max( y_k-50 , y_rsi-x_rsi_ft , x_changk>1?100-x_rsi_ct-highest(y_rsi,x_changk):-50 )', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ( y_upper>0 )'}, {'indent': 0, 'statement': 'else if ( x_exit_if_reason_over and strategy.position_size>0 )'}, {'indent': 0, 'statement': 'if ( y_lower<0 )'}, {'indent': 0, 'statement': 'else if ( x_exit_if_reason_over and strategy.position_size<0 )'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("LE", strategy.long)', 'conditions': ['( y_upper>0 )'], 'statement': 'strategy.entry("LE", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("LE", comment="x" )', 'conditions': ['( x_exit_if_reason_over and strategy.position_size>0 )'], 'statement': 'strategy.close("LE", comment="x" )'}, {'kind': 'entry', 'call': 'strategy.entry("SE", strategy.short)', 'conditions': ['( y_lower<0 )'], 'statement': 'strategy.entry("SE", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("SE", comment="x" )', 'conditions': ['( x_exit_if_reason_over and strategy.position_size<0 )'], 'statement': 'strategy.close("SE", comment="x" )'}]
    original_pine = '/*backtest\nstart: 2023-01-17 00:00:00\nend: 2024-01-23 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("scalping against trapped countertrend", overlay=false , precision=5 )\n\nx_src = input( hl2 , title="Source" )\nx_len_a = input( 5 , title="short term trend" , minval=1 )\nx_len_b = input( 60 , title="long term trend" , minval=1 )\nx_k_b = input( 13 , title="smooth long term trend" , minval=1 )\nx_changk = input( 15 , title="clear short term pullback appears recently" , minval=1 )\nx_rsi_ct = input( 35.0 , title="threshold of short term pullback clear" , minval=0.0 , maxval=100.0 )\nx_rsi_ft = input( 50.0 , title="threshold of short term pullback end" , minval=0.0 , maxval=100.0 )\nx_exit_if_reason_over = input(false)\n\ny_stoch = stoch( x_src , high , low , x_len_b )\ny_k = sma( y_stoch , x_k_b )\ny_rsi = rsi( x_src , x_len_a )\n\ny_upper = min( y_k-50 , y_rsi-x_rsi_ft , x_changk>1?x_rsi_ct-lowest(y_rsi,x_changk):50 )\nif ( y_upper>0 )\n    strategy.entry("LE", strategy.long)\nelse if ( x_exit_if_reason_over and strategy.position_size>0 )\n    strategy.close("LE", comment="x" )\ny_lower = max( y_k-50 , y_rsi-x_rsi_ft , x_changk>1?100-x_rsi_ct-highest(y_rsi,x_changk):-50 )\nif ( y_lower<0 )\n    strategy.entry("SE", strategy.short)\nelse if ( x_exit_if_reason_over and strategy.position_size<0 )\n    strategy.close("SE", comment="x" )\n\nplot( y_stoch , color=#ff3333 )\nplot( y_k , color=#6666ff )\nplot( y_rsi , color=#cccc00 )\nhline(50)'

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
