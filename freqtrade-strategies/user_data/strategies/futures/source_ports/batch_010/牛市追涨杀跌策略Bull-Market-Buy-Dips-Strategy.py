"""Source-faithful deep-assisted port of 牛市追涨杀跌策略Bull-Market-Buy-Dips-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_fcaef6c4(PinePortBase, IStrategy):
    source_file = '牛市追涨杀跌策略Bull-Market-Buy-Dips-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'fromMonth': 1, 'fromDay': 10, 'fromYear': 2020, 'thruMonth': 1, 'thruDay': 1, 'thruYear': 2112, 'showDate': True, 'lengthRSI': 14, 'inSignal': 9, 'inlong1': 50, 'inlong2': 200, 'RSI_buy_signal': 35}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 30.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'fromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month")', 'conditions': []}, {'mode': '', 'name': 'fromDay', 'op': '=', 'expr': 'input(defval = 10, title = "From Day")', 'conditions': []}, {'mode': '', 'name': 'fromYear', 'op': '=', 'expr': 'input(defval = 2020, title = "From Year")', 'conditions': []}, {'mode': '', 'name': 'thruMonth', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Month")', 'conditions': []}, {'mode': '', 'name': 'thruDay', 'op': '=', 'expr': 'input(defval = 1, title = "Thru Day")', 'conditions': []}, {'mode': '', 'name': 'thruYear', 'op': '=', 'expr': 'input(defval = 2112, title = "Thru Year")', 'conditions': []}, {'mode': '', 'name': 'showDate', 'op': '=', 'expr': 'input(defval = true, title = "Show Date Range")', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(fromYear, fromMonth, fromDay, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(thruYear, thruMonth, thruDay, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'lengthRSI', 'op': '=', 'expr': "input(14, title = 'RSI period', minval=1)", 'conditions': []}, {'mode': '', 'name': 'RSI', 'op': '=', 'expr': 'rsi(close, lengthRSI)', 'conditions': []}, {'mode': '', 'name': 'inSignal', 'op': '=', 'expr': "input(9, title='MAfast')", 'conditions': []}, {'mode': '', 'name': 'inlong1', 'op': '=', 'expr': "input(50, title='MAslow')", 'conditions': []}, {'mode': '', 'name': 'inlong2', 'op': '=', 'expr': "input(200, title='MAslow')", 'conditions': []}, {'mode': '', 'name': 'MAfast', 'op': '=', 'expr': 'sma(close, inSignal)', 'conditions': []}, {'mode': '', 'name': 'MAslow', 'op': '=', 'expr': 'sma(close, inlong1)', 'conditions': []}, {'mode': '', 'name': 'MAlong', 'op': '=', 'expr': 'sma(close, inlong2)', 'conditions': []}, {'mode': '', 'name': 'RSI_buy_signal', 'op': '=', 'expr': "input(35, title='RSI Buy Signal')", 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'time >= start and time <= finish ? true : false // create function "within window of time"'}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="long", long = true, when = RSI < RSI_buy_signal and MAlong < MAslow and window())', 'conditions': [], 'statement': 'strategy.entry(id="long", long = true, when = RSI < RSI_buy_signal and MAlong < MAslow and window())'}, {'kind': 'close', 'call': 'strategy.close("long", when = close > MAfast and MAfast > MAslow and window())', 'conditions': [], 'statement': 'strategy.close("long", when = close > MAfast and MAfast > MAslow and window())'}]
    original_pine = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(shorttitle=\'Buy The Dips in Bull Market\',title=\'Buy The Dips in Bull Market (by Coinrule)\', overlay=true, initial_capital = 1000, default_qty_type = strategy.percent_of_equity, default_qty_type = strategy.percent_of_equity, default_qty_value = 30, commission_type=strategy.commission.percent, commission_value=0.1)\n    \n//Backtest dates\nfromMonth = input(defval = 1,  title = "From Month")     \nfromDay   = input(defval = 10,    title = "From Day")       \nfromYear  = input(defval = 2020, title = "From Year")       \nthruMonth = input(defval = 1,    title = "Thru Month")     \nthruDay   = input(defval = 1,    title = "Thru Day")     \nthruYear  = input(defval = 2112, title = "Thru Year")       \n    \nshowDate  = input(defval = true, title = "Show Date Range")\n    \nstart     = timestamp(fromYear, fromMonth, fromDay, 00, 00)        // backtest start window\nfinish    = timestamp(thruYear, thruMonth, thruDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false       // create function "within window of time"\n    \n    \n// RSI inputs and calculations\nlengthRSI = input(14, title = \'RSI period\', minval=1)\nRSI = rsi(close, lengthRSI)\n\n//MA inputs and calculations\ninSignal=input(9, title=\'MAfast\')\ninlong1=input(50, title=\'MAslow\')\ninlong2=input(200, title=\'MAslow\')\n\n\nMAfast= sma(close, inSignal)\nMAslow= sma(close, inlong1)\nMAlong= sma(close, inlong2)\n\n\nRSI_buy_signal= input(35, title=\'RSI Buy Signal\')\n\n    \n//Entry\n    \n    \nstrategy.entry(id="long", long = true, when = RSI < RSI_buy_signal and MAlong < MAslow and window()) \n    \n//Exit\n    \n    \nstrategy.close("long", when = close > MAfast and MAfast > MAslow and window())\n\n\nplot(MAslow, color=color.orange, linewidth=1)\nplot(MAfast, color=color.purple, linewidth=1)\nplot(MAlong, color=color.blue, linewidth=2)'

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
