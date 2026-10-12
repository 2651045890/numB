"""Source-faithful deep-assisted port of 时空优化多时间框架MACD策略Time-and-Space-Optimized-Multi-Timeframe-MACD-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_354aef79(PinePortBase, IStrategy):
    source_file = '时空优化多时间框架MACD策略Time-and-Space-Optimized-Multi-Timeframe-MACD-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'srca': 'close', 'fromDay': 1, 'fromMonth': 1, 'fromYear': 2000, 'toDay': 31, 'toMonth': 12, 'toYear': 2021, 'tp': 0.0003, 'sl': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', '=>', 'timeframe.', 'alert']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fast_length', 'op': '=', 'expr': '12', 'conditions': []}, {'mode': '', 'name': 'slow_length', 'op': '=', 'expr': '26', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'signal_length', 'op': '=', 'expr': '9', 'conditions': []}, {'mode': '', 'name': 'sma_source', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'sma_signal', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'fast_ma', 'op': '=', 'expr': 'sma_source ? sma(src, fast_length) : ema(src, fast_length)', 'conditions': []}, {'mode': '', 'name': 'slow_ma', 'op': '=', 'expr': 'sma_source ? sma(src, slow_length) : ema(src, slow_length)', 'conditions': []}, {'mode': '', 'name': 'macd', 'op': '=', 'expr': 'fast_ma - slow_ma', 'conditions': []}, {'mode': '', 'name': 'signal', 'op': '=', 'expr': 'sma_signal ? sma(macd, signal_length) : ema(macd, signal_length)', 'conditions': []}, {'mode': '', 'name': 'hist', 'op': '=', 'expr': 'macd - signal', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': '10', 'conditions': []}, {'mode': '', 'name': 'srca', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'out', 'op': '=', 'expr': 'hma(srca, len)', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2000, title = "From Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'toDay', 'op': '=', 'expr': 'input(defval = 31, title = "To Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'toMonth', 'op': '=', 'expr': 'input(defval = 12, title = "To Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'toYear', 'op': '=', 'expr': 'input(defval = 2021, title = "To Year", minval = 1970)', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'finishDate', 'op': '=', 'expr': 'timestamp(toYear, toMonth, toDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'myspecifictradingtimes', 'op': '=', 'expr': "'0900-0915'", 'conditions': []}, {'mode': '', 'name': 'exittime', 'op': '=', 'expr': "'2100-2115'", 'conditions': []}, {'mode': '', 'name': 'optionmacd', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'entrytime', 'op': '=', 'expr': 'time(timeframe.period, myspecifictradingtimes) != 0', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'time(timeframe.period, exittime) != 0', 'conditions': []}, {'mode': '', 'name': 'tp', 'op': '=', 'expr': 'input(0.0003, title="tp")', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'input(1.0 , title="sl")', 'conditions': []}]
    pine_user_functions = [{'name': 'timeinrange', 'args': 'res, sess', 'body': 'time(res, sess) != 0'}]
    pine_controls = [{'indent': 0, 'statement': 'if(time_cond and optionmacd )'}, {'indent': 4, 'statement': 'if(close > open and close[1] > open[1] and close[2] > open[2] and entrytime and crossover(hist,0))'}, {'indent': 4, 'statement': 'if(close< open and close[1] < open[1] and close[2] < open[2] and entrytime and crossunder(hist,0))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long",1)', 'conditions': [], 'statement': 'strategy.entry("long",1)'}, {'kind': 'entry', 'call': 'strategy.entry("short",0)', 'conditions': [], 'statement': 'strategy.entry("short",0)'}, {'kind': 'exit', 'call': 'strategy.exit("closelong", "long" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closelong")', 'conditions': [], 'statement': 'strategy.exit("closelong", "long" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closelong")'}, {'kind': 'exit', 'call': 'strategy.exit("closeshort", "short" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closeshort")', 'conditions': [], 'statement': 'strategy.exit("closeshort", "short" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closeshort")'}]
    original_pine = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\nstrategy("Very high win rate strategy", overlay=true)\n\n\n//\n\nfast_length =12\nslow_length= 26\nsrc = close\nsignal_length = 9\nsma_source = false\nsma_signal = false\n\n// Calculating\nfast_ma = sma_source ? sma(src, fast_length) : ema(src, fast_length)\nslow_ma = sma_source ? sma(src, slow_length) : ema(src, slow_length)\nmacd = fast_ma - slow_ma\nsignal = sma_signal ? sma(macd, signal_length) : ema(macd, signal_length)\nhist = macd - signal\n\n//ma\n\nlen=10\nsrca = input(close, title="Source")\nout = hma(srca, len)\n\nfromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nfromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nfromYear = input(defval = 2000, title = "From Year", minval = 1970)\n //monday and session \n// To Date Inputs\ntoDay = input(defval = 31, title = "To Day", minval = 1, maxval = 31)\ntoMonth = input(defval = 12, title = "To Month", minval = 1, maxval = 12)\ntoYear = input(defval = 2021, title = "To Year", minval = 1970)\n\nstartDate = timestamp(fromYear, fromMonth, fromDay, 00, 00)\nfinishDate = timestamp(toYear, toMonth, toDay, 00, 00)\ntime_cond = true\n\n\ntimeinrange(res, sess) => time(res, sess) != 0\n\n// = input(\'0900-0915\', type=input.session, title="My Defined Hours")\nmyspecifictradingtimes = \'0900-0915\'\nexittime = \'2100-2115\'\n\noptionmacd=true\n\n\nentrytime = time(timeframe.period, myspecifictradingtimes) != 0\nexit = time(timeframe.period, exittime) != 0     \n\nif(time_cond and optionmacd )\n    if(close > open and close[1] > open[1] and close[2] > open[2] and entrytime  and crossover(hist,0))\n        strategy.entry("long",1)\n    if(close< open and close[1] < open[1] and close[2] < open[2] and entrytime and crossunder(hist,0))\n        strategy.entry("short",0)      \n\n\ntp = input(0.0003, title="tp")\n//tp = 0.0003\nsl = input(1.0 , title="sl")\n//sl = 1.0\nstrategy.exit("closelong", "long" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closelong")\nstrategy.exit("closeshort", "short" , profit = close * tp / syminfo.mintick, loss = close * sl / syminfo.mintick, alert_message = "closeshort")'

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
