"""Source-faithful deep-assisted port of 牛市强劲趋势跟踪策略Bull-Trend-Riding-Strategy-Based-on-Stochastic-RSI-with-Special-Rules-for-Heavy-Bullish-Bias.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f2b93f06(PinePortBase, IStrategy):
    source_file = '牛市强劲趋势跟踪策略Bull-Trend-Riding-Strategy-Based-on-Stochastic-RSI-with-Special-Rules-for-Heavy-Bullish-Bias.md'
    timeframe = '3h'
    can_short = False
    source_defaults = {'filter_ema_len': 6, 'ema_donchian_len': 30, 'smoothK': 7, 'smoothD': 4, 'lengthRSI': 14, 'lengthStoch': 14, 'src': 'close', 'lowerband': 35}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'filter_ema_len', 'op': '=', 'expr': 'input(6)', 'conditions': []}, {'mode': '', 'name': 'ema_donchian_len', 'op': '=', 'expr': 'input(30)', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.highest(ta.ema(high,filter_ema_len),ema_donchian_len)', 'conditions': []}, {'mode': '', 'name': 'smoothK', 'op': '=', 'expr': 'input.int(7, "K", minval=1)', 'conditions': []}, {'mode': '', 'name': 'smoothD', 'op': '=', 'expr': 'input.int(4, "D", minval=1)', 'conditions': []}, {'mode': '', 'name': 'lengthRSI', 'op': '=', 'expr': 'input.int(14, "RSI Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'lengthStoch', 'op': '=', 'expr': 'input.int(14, "Stochastic Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="RSI Source")', 'conditions': []}, {'mode': '', 'name': 'rsi1', 'op': '=', 'expr': 'ta.rsi(src, lengthRSI)', 'conditions': []}, {'mode': '', 'name': 'k', 'op': '=', 'expr': 'math.min(100, math.max(0,ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)))', 'conditions': []}, {'mode': '', 'name': 'd', 'op': '=', 'expr': 'math.max(math.min(ta.sma(k, smoothD),80),35)', 'conditions': []}, {'mode': '', 'name': 'h0', 'op': '=', 'expr': 'hline(80, "Upper Band", color=#787B86)', 'conditions': []}, {'mode': '', 'name': 'lowerband', 'op': '=', 'expr': 'input(35)', 'conditions': []}, {'mode': '', 'name': 'h11', 'op': '=', 'expr': 'hline(lowerband, "Lower Band", color=#787B86)', 'conditions': []}, {'mode': '', 'name': 'ematrend', 'op': '=', 'expr': 'close>ema ? 1 : 0', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'k>lowerband and ematrend==1', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(k,lowerband)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Up", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Up", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Up", shortCondition)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.close("Up", shortCondition)'}]
    original_pine = '/*backtest\nstart: 2023-09-16 00:00:00\nend: 2023-10-16 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © SnarkyPuppy\n\n//@version=5\nstrategy("Filtered Stoch", overlay=false, default_qty_value = 100, default_qty_type=strategy.percent_of_equity)\n\n/////high filter...upper donchian channel of ema... or highest ema for a given amount of candles\n\nfilter_ema_len= input(6)\nema_donchian_len = input(30)\n\nema=ta.highest(ta.ema(high,filter_ema_len),ema_donchian_len)\n\n////////////////////////basic stoch rsi with max val 100 and min val 0.. entry above lowerband preset 35\n\nsmoothK = input.int(7, "K", minval=1)\nsmoothD = input.int(4, "D", minval=1)\nlengthRSI = input.int(14, "RSI Length", minval=1)\nlengthStoch = input.int(14, "Stochastic Length", minval=1)\nsrc = input(close, title="RSI Source")\nrsi1 = ta.rsi(src, lengthRSI)\nk = math.min(100, math.max(0,ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)))\nd = math.max(math.min(ta.sma(k, smoothD),80),35)\nplot(k, "K", color=#2962FF)\nplot(d, "D", color=#FF6D00)\nh0 = hline(80, "Upper Band", color=#787B86)\nhline(50, "Middle Band", color=color.new(#787B86, 50))\nlowerband=input(35)\nh11 = hline(lowerband, "Lower Band", color=#787B86)\nfill(h0, h11, color=color.rgb(33, 150, 243, 90), title="Background")\n\nematrend= close>ema ? 1 : 0\n\nbgcolor(ematrend==1?color.rgb(76, 175, 79, 80):na)\n\nlongCondition = k>lowerband and ematrend==1\nif (longCondition)\n    strategy.entry("Up", strategy.long)\n\nshortCondition =  ta.crossunder(k,lowerband)\nif (shortCondition)\n    strategy.close("Up", shortCondition)'

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
