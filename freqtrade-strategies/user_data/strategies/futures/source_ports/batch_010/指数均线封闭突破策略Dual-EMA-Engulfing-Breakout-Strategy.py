"""Source-faithful deep-assisted port of 指数均线封闭突破策略Dual-EMA-Engulfing-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c877eb51(PinePortBase, IStrategy):
    source_file = '指数均线封闭突破策略Dual-EMA-Engulfing-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'I_start_date': 'timestamp("20 Jan 1990 00:00 +0900"', 'I_finish_date': 'timestamp("20 Dec 2030 00:00 +0900"', 'I_short_ema': 15, 'I_long_ema': 30, 'I_body': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 10000000.0
    source_commission_percent = 0.01
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'I_start_date', 'op': '=', 'expr': 'input (defval = timestamp("20 Jan 1990 00:00 +0900"))', 'conditions': []}, {'mode': '', 'name': 'I_finish_date', 'op': '=', 'expr': 'input(defval = timestamp("20 Dec 2030 00:00 +0900"))', 'conditions': []}, {'mode': '', 'name': 'I_short_ema', 'op': '=', 'expr': 'input.int(defval = 15 , title = "Short EMA", minval = 1 , maxval = 300 , step = 1)', 'conditions': []}, {'mode': '', 'name': 'I_long_ema', 'op': '=', 'expr': 'input.int(defval = 30 , title = "Long EMA", minval = 1 , maxval = 300 , step = 1)', 'conditions': []}, {'mode': '', 'name': 'I_body', 'op': '=', 'expr': 'input.float(defval = 1 , title = "Size of Body", minval = 1 , maxval = 5 , step = 0.1)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'C_uptrend', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'C_downtrend', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'C_ema_short', 'op': '=', 'expr': 'ta.ema(source = close, length = I_short_ema)', 'conditions': []}, {'mode': '', 'name': 'C_ema_long', 'op': '=', 'expr': 'ta.ema(source = close, length = I_long_ema)', 'conditions': []}, {'mode': '', 'name': 'C_uptrend', 'op': ':=', 'expr': 'close > C_ema_short and C_ema_short > C_ema_long', 'conditions': []}, {'mode': '', 'name': 'C_downtrend', 'op': ':=', 'expr': 'close < C_ema_short and C_ema_short < C_ema_long', 'conditions': []}, {'mode': '', 'name': 'C_pre_body', 'op': '=', 'expr': 'math.abs(open[1]-close[1])', 'conditions': []}, {'mode': '', 'name': 'C_pre_body_ratio', 'op': '=', 'expr': '(math.abs(open[1]-close[1])) / (math.abs(high[1]-low[1])) * 100', 'conditions': []}, {'mode': '', 'name': 'C_now_body', 'op': '=', 'expr': 'math.abs(open-close)', 'conditions': []}, {'mode': '', 'name': 'C_now_body_ratio', 'op': '=', 'expr': '(math.abs(open-close)) / (math.abs(high-low)) * 100', 'conditions': []}, {'mode': '', 'name': 'C_bullish_engulfing', 'op': '=', 'expr': '(open[1] > close[1] and open <= close) and (low < low[1] and high > high[1])', 'conditions': []}, {'mode': '', 'name': 'C_bearish_engulfing', 'op': '=', 'expr': '(open[1] < close[1] and open >= close) and (low < low[1] and high > high[1])', 'conditions': []}, {'mode': '', 'name': 'C_avoid_doge', 'op': '=', 'expr': '(C_pre_body_ratio > I_body and C_now_body_ratio > I_body) ? true : false', 'conditions': []}, {'mode': '', 'name': 'C_volume_filter', 'op': '=', 'expr': 'volume > volume[1] * 1.2', 'conditions': []}, {'mode': '', 'name': 'long_signal', 'op': '=', 'expr': 'C_uptrend and C_bullish_engulfing and C_avoid_doge and C_volume_filter', 'conditions': []}, {'mode': '', 'name': 'close_signal', 'op': '=', 'expr': 'C_downtrend or C_bearish_engulfing', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if long_signal and time_cond'}, {'indent': 0, 'statement': 'if close_signal and time_cond'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id = "Long", direction = strategy.long)', 'conditions': ['long_signal and time_cond'], 'statement': 'strategy.entry(id = "Long", direction = strategy.long)'}, {'kind': 'close', 'call': 'strategy.close(id = "Long")', 'conditions': ['close_signal and time_cond'], 'statement': 'strategy.close(id = "Long")'}]
    original_pine = '/*backtest\nstart: 2023-11-06 00:00:00\nend: 2023-12-06 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// @version=5\n// # ========================================================================= #\n// #                   |   STRATEGY  |\n// # ========================================================================= #\nstrategy(\n  title                           = "fpemehd Strategy001",\n  shorttitle                      = "f_001",\n  overlay                         =  true,\n  default_qty_type                =  strategy.percent_of_equity, \n  default_qty_value               =  100, \n  initial_capital                 =  10000000, \n  currency                        =  currency.USD, \n  slippage                        =  0, \n  commission_type                 =  strategy.commission.cash_per_order, \n  commission_value                =  0.01, \n  process_orders_on_close         =  true)\n// # ========================================================================= #\n// #                   |   STRATEGY  |\n// # ========================================================================= #\n\n\n// Inputs\nI_start_date = input (defval = timestamp("20 Jan 1990 00:00 +0900"))\nI_finish_date = input(defval = timestamp("20 Dec 2030 00:00 +0900"))\n\nI_short_ema = input.int(defval = 15 , title = "Short EMA", minval = 1 , maxval = 300 , step = 1)\nI_long_ema = input.int(defval = 30 , title = "Long EMA", minval = 1 , maxval = 300 , step = 1)\n\nI_body = input.float(defval = 1 , title = "Size of Body", minval = 1 , maxval = 5 , step = 0.1)\n\ntime_cond = true\n\n// Calculate Engulfing Candles\nC_uptrend = false\nC_downtrend = false\nC_ema_short = ta.ema(source = close, length = I_short_ema) \nC_ema_long = ta.ema(source = close, length = I_long_ema) \nC_uptrend := close > C_ema_short and C_ema_short > C_ema_long\nC_downtrend := close < C_ema_short and C_ema_short < C_ema_long\n\nC_pre_body = math.abs(open[1]-close[1])\nC_pre_body_ratio = (math.abs(open[1]-close[1])) / (math.abs(high[1]-low[1])) * 100\n\nC_now_body = math.abs(open-close)\nC_now_body_ratio = (math.abs(open-close)) / (math.abs(high-low)) * 100\n\nC_bullish_engulfing = (open[1] > close[1] and open <= close) and (low < low[1] and high > high[1])\nC_bearish_engulfing = (open[1] < close[1] and open >= close) and (low < low[1] and high > high[1])\nC_avoid_doge = (C_pre_body_ratio > I_body and C_now_body_ratio > I_body) ? true : false\nC_volume_filter = volume > volume[1] * 1.2\n\n// Signals\nlong_signal = C_uptrend and C_bullish_engulfing and C_avoid_doge and C_volume_filter\nclose_signal = C_downtrend or C_bearish_engulfing \n\n\nif long_signal and time_cond\n    strategy.entry(id = "Long", direction = strategy.long)\n\nif close_signal and time_cond\n    strategy.close(id = "Long")'

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
