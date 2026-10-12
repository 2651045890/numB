"""Source-faithful deep-assisted port of 常用移动平均线交叉策略Moving-Average-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_aef579f3(PinePortBase, IStrategy):
    source_file = '常用移动平均线交叉策略Moving-Average-Crossover-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'type': 'WMA', 'length': 28, 'FromDay': 1, 'FromMonth': 1, 'FromYear': 2000}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.1
    source_features = ['strategy.exit', 'strategy.entry', '=>']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'type', 'op': '=', 'expr': 'input(defval = "WMA", title = "MA Type: ", options=["RMA", "SMA", "EMA", "WMA"])', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(28)', 'conditions': []}, {'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'FromDay', 'op': '=', 'expr': 'input(defval = 1, title = "From Day", minval = 1, maxval = 31)', 'conditions': []}, {'mode': '', 'name': 'FromMonth', 'op': '=', 'expr': 'input(defval = 1, title = "From Month", minval = 1, maxval = 12)', 'conditions': []}, {'mode': '', 'name': 'FromYear', 'op': '=', 'expr': 'input(defval = 2000, title = "From Year", minval = 2000)', 'conditions': []}, {'mode': '', 'name': 'start', 'op': '=', 'expr': 'timestamp(FromYear, FromMonth, FromDay, 00, 00) // backtest start window', 'conditions': []}, {'mode': '', 'name': 'finish', 'op': '=', 'expr': 'timestamp(9999, 1, 1, 23, 59) // backtest finish window', 'conditions': []}, {'mode': '', 'name': 'v1', 'op': '=', 'expr': 'sma(src, len) // Simple', 'conditions': []}, {'mode': '', 'name': 'v2', 'op': '=', 'expr': 'ema(src, len) // Exponential', 'conditions': []}, {'mode': '', 'name': 'v5', 'op': '=', 'expr': 'wma(src, len) // Weighted', 'conditions': []}, {'mode': '', 'name': 'v7', 'op': '=', 'expr': 'rma(src, len) // Smoothed', 'conditions': []}, {'mode': '', 'name': 'type', 'op': '=', 'expr': '="EMA"?v2 : type=="WMA"?v5 : type=="RMA"?v7 : v1', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': 'variant(type,source, length)', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'security(syminfo.tickerid, "D", atr(14))', 'conditions': []}, {'mode': '', 'name': 'range', 'op': '=', 'expr': 'valuewhen(cross(close,ma), (atr*2), na)', 'conditions': []}, {'mode': '', 'name': 'ep', 'op': '=', 'expr': 'valuewhen(cross(close,ma), close, na)', 'conditions': []}]
    pine_user_functions = [{'name': 'window', 'args': '', 'body': 'time >= start and time <= finish ? true : false // create function "within window of time"'}, {'name': 'variant', 'args': 'type, src, len', 'body': ''}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long Entry", true, when = crossover(close,ma) and window() , stop = ep )', 'conditions': [], 'statement': 'strategy.entry("Long Entry", true, when = crossover(close,ma) and window() , stop = ep )'}, {'kind': 'exit', 'call': 'strategy.exit("Long Exit", "Long Entry", stop = ep-range)', 'conditions': [], 'statement': 'strategy.exit("Long Exit", "Long Entry", stop = ep-range)'}, {'kind': 'exit', 'call': 'strategy.exit("Long Exit", "Long Entry", when = high > ep+range ,stop = ep[1] )', 'conditions': [], 'statement': 'strategy.exit("Long Exit", "Long Entry", when = high > ep+range ,stop = ep[1] )'}, {'kind': 'entry', 'call': 'strategy.entry("Short Entry", false, when = crossunder(close,ma) and window() , stop = ep )', 'conditions': [], 'statement': 'strategy.entry("Short Entry", false, when = crossunder(close,ma) and window() , stop = ep )'}, {'kind': 'exit', 'call': 'strategy.exit("Short Exit", "Short Entry", stop = ep+range)', 'conditions': [], 'statement': 'strategy.exit("Short Exit", "Short Entry", stop = ep+range)'}, {'kind': 'exit', 'call': 'strategy.exit("Short Exit", "Short Entry", when = low < ep-range ,stop = ep[1] )', 'conditions': [], 'statement': 'strategy.exit("Short Exit", "Short Entry", when = low < ep-range ,stop = ep[1] )'}]
    original_pine = '/*backtest\nstart: 2023-10-03 00:00:00\nend: 2023-11-02 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("MA Cross Strategy", overlay=true,commission_value = 0.1)\n\ntype = input(defval = "WMA", title = "MA Type: ", options=["RMA", "SMA", "EMA", "WMA"])\n\nlength = input(28)\nsource = close\n\n\n\n// === INPUT BACKTEST RANGE ===\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromYear  = input(defval = 2000, title = "From Year", minval = 2000)\n\n// === FUNCTION EXAMPLE ===\nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(9999, 1, 1, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false // create function "within window of time"\n\n\n\nvariant(type, src, len) =>\n    v1 = sma(src, len)                                                  // Simple\n    v2 = ema(src, len)                                                  // Exponential\n    v5 = wma(src, len)                                                  // Weighted\n    v7 = rma(src, len)                                                  // Smoothed\n    type=="EMA"?v2 : type=="WMA"?v5 : type=="RMA"?v7 : v1\nma = variant(type,source, length)\n\n\natr = security(syminfo.tickerid, "D", atr(14))\n\nrange = valuewhen(cross(close,ma), (atr*2), na)\n\nep = valuewhen(cross(close,ma), close, na)\n\nplot(ma,color=ma>ma[1]?color.blue:color.red,transp=0,linewidth=1)\nplot(ep,color=#2196f3,transp=100,trackprice=true, offset=-9999)\nplot(ep+range,color=#2196f3,transp=100,trackprice=true, offset=-9999)\nplot(ep-range,color=#2196f3,transp=100,trackprice=true, offset=-9999)\n\nstrategy.entry("Long Entry", true, when = crossover(close,ma)  and window() , stop  = ep ) \nstrategy.exit("Long Exit", "Long Entry", stop  = ep-range) \nstrategy.exit("Long Exit", "Long Entry", when = high > ep+range ,stop = ep[1] ) \n\nstrategy.entry("Short Entry", false, when = crossunder(close,ma)  and window() , stop  = ep ) \nstrategy.exit("Short Exit", "Short Entry", stop  = ep+range) \nstrategy.exit("Short Exit", "Short Entry", when = low < ep-range ,stop = ep[1] )'

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
