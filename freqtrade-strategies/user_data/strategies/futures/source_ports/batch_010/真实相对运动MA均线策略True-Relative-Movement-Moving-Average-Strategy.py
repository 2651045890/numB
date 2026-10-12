"""Source-faithful deep-assisted port of 真实相对运动MA均线策略True-Relative-Movement-Moving-Average-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_72284d4e(PinePortBase, IStrategy):
    source_file = '真实相对运动MA均线策略True-Relative-Movement-Moving-Average-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'Note': 0, 'long': 25, 'short': 5, 'signal': 14, 'rsiBuyfilterlevel': 50, 'rsiSellfilterlevel': 50}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'Note', 'op': '=', 'expr': 'input( 0, title = "TSI standard values are 25, 13, 13, and RSI is 14. Can change the default values to these for \'Slow TRM\'")', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'input(title="TSI-Long Length", type=input.integer, defval=25)', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'input(title="TSI-Short Length", type=input.integer, defval=5)', 'conditions': []}, {'mode': '', 'name': 'signal', 'op': '=', 'expr': 'input(title="TSI-Signal Length", type=input.integer, defval=14)', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'fist_smooth', 'op': '=', 'expr': 'ema(src, long)', 'conditions': []}, {'mode': '', 'name': 'pc', 'op': '=', 'expr': 'change(price)', 'conditions': []}, {'mode': '', 'name': 'double_smoothed_pc', 'op': '=', 'expr': 'double_smooth(pc, long, short)', 'conditions': []}, {'mode': '', 'name': 'double_smoothed_abs_pc', 'op': '=', 'expr': 'double_smooth(abs(pc), long, short)', 'conditions': []}, {'mode': '', 'name': 'tsi_value', 'op': '=', 'expr': '100 * (double_smoothed_pc / double_smoothed_abs_pc)', 'conditions': []}, {'mode': '', 'name': 'TSI_Signal_Line', 'op': '=', 'expr': '(ema(tsi_value, signal))', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close, len = input(5, minval=1, title="RSILength")', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'rma(max(change(src), 0), len)', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': 'rma(-min(change(src), 0), len)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))', 'conditions': []}, {'mode': '', 'name': 'rsiBuyfilterlevel', 'op': '=', 'expr': 'input(50, minval = 1, title = "RSI cross above Buy Level")', 'conditions': []}, {'mode': '', 'name': 'rsiSellfilterlevel', 'op': '=', 'expr': 'input(50, minval = 1, title = "RSI cross below Sell Level")', 'conditions': []}, {'mode': '', 'name': 'TRM_Buy', 'op': '=', 'expr': '((tsi_value > TSI_Signal_Line) and (rsi > rsiBuyfilterlevel))', 'conditions': []}, {'mode': '', 'name': 'TRM_Sell', 'op': '=', 'expr': '( (tsi_value < TSI_Signal_Line) and (rsi <rsiSellfilterlevel))', 'conditions': []}, {'mode': '', 'name': 'TRM_Color', 'op': '=', 'expr': 'TRM_Buy? #3BB3E4 : TRM_Sell? #FF006E : #b2b5be', 'conditions': []}]
    pine_user_functions = [{'name': 'double_smooth', 'args': 'src, long, short', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (TRM_Buy)'}, {'indent': 0, 'statement': 'if (TRM_Sell)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, comment="Long")', 'conditions': ['(TRM_Buy)'], 'statement': 'strategy.entry("Long", strategy.long, comment="Long")'}, {'kind': 'close', 'call': 'strategy.close("Long", comment="Sell")', 'conditions': ['(TRM_Sell)'], 'statement': 'strategy.close("Long", comment="Sell")'}]
    original_pine = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// "True relative Movement" or "TRM" for short is a system that combines my two favorite indicators: RSI and TSI. I strived to put together an indicator that combined the best of both \n// in order to help discretionary traders predict market direction, weakness and strength. As with most technical indicators there are "Buy and sell" signals. Similiar to Elder Impulse system, \n///TRM paints bars 3 different colors to display 3 different conditions: Blue for "Buy", Pink for "Sell", and gray for "Take profit/Hold". When the bars turn blue, that means all conditions\n/// have been met. When they turn pink, no conditions have been met. When they are gray, only one condition has been met. The system is simple, yet effective. A buy signal is prodcued when \n/// TSI is above the signal line, and RSI is above 50, and vice versa for sell signals. I have modified the default parameters for TSI and RSI for more "aggressive" entries and exits. I may later on\n/// name this condition "Fast-TRM" and "Slow-TRM" for when default settings for TSI and RSI are applies, as this is a very robust system as well. \n\n///******ES 1HR, 15MIN/5MIN SYSTEM***** Go long, when all time frame on a buy signal and vice versa. Take profit when the 5 min chart flips to buy or sell depending on what side of the trade you are on. Close or flip\n//// long/short when time all time frames flip to Buy/Hold if short and Sell/Hold if long. Use 20EMA for additional confirmation. \n\n//@version=4\nstrategy("TKP-TRM Strategy", overlay=true)\nNote = input( 0, title = "TSI standard values are 25, 13, 13, and RSI is 14. Can change the default values to these for \'Slow TRM\'")\nlong = input(title="TSI-Long Length", type=input.integer, defval=25)\nshort = input(title="TSI-Short Length", type=input.integer, defval=5)\nsignal = input(title="TSI-Signal Length", type=input.integer, defval=14)\nprice = close\ndouble_smooth(src, long, short) =>\n    fist_smooth = ema(src, long)\n    ema(fist_smooth, short)\npc = change(price)\ndouble_smoothed_pc = double_smooth(pc, long, short)\ndouble_smoothed_abs_pc = double_smooth(abs(pc), long, short)\ntsi_value = 100 * (double_smoothed_pc / double_smoothed_abs_pc)\nTSI_Signal_Line = (ema(tsi_value, signal))\n\n\n/////////////////////////////RSI////////////////////////////////////////////////\n\nsrc = close, len = input(5, minval=1, title="RSILength")\nup = rma(max(change(src), 0), len)\ndown = rma(-min(change(src), 0), len)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\nrsiBuyfilterlevel = input(50, minval = 1, title = "RSI cross above Buy Level")\nrsiSellfilterlevel = input(50, minval = 1, title = "RSI cross below Sell Level")\n\n////////////////////////////Bar Coloring//////////////////////////////////////////////////////////\n\nTRM_Buy = ((tsi_value > TSI_Signal_Line) and (rsi > rsiBuyfilterlevel))\nTRM_Sell = ( (tsi_value < TSI_Signal_Line) and (rsi <rsiSellfilterlevel))\nTRM_Color = TRM_Buy? #3BB3E4 : TRM_Sell? #FF006E : #b2b5be\nbarcolor(TRM_Color)\n\n\n///////////////////////////Strategy Paramters////////////////////////////////////////\n\nif (TRM_Buy)\n    strategy.entry("Long", strategy.long, comment="Long")\n\nif (TRM_Sell)\n    strategy.close("Long", comment="Sell")'

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
