"""Source-faithful deep-assisted port of 月末动量突破200日均线策略End-of-Month-Breakout-on-200-Day-Moving-Average-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_496a408f(PinePortBase, IStrategy):
    source_file = '月末动量突破200日均线策略End-of-Month-Breakout-on-200-Day-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'from_day': 1, 'from_month': 1, 'from_year': 2018, 'to_day': 1, 'to_month': 1, 'to_year': 9999}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'dma200', 'op': '=', 'expr': 'ta.sma(close, 200)', 'conditions': []}, {'mode': '', 'name': 'from_day', 'op': '=', 'expr': 'input.int(defval=1, title="From Day", minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'from_month', 'op': '=', 'expr': 'input.int(defval=1, title="From Month", minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'from_year', 'op': '=', 'expr': 'input.int(defval=2018, title="From Year", minval=1900)', 'conditions': []}, {'mode': '', 'name': 'to_day', 'op': '=', 'expr': 'input.int(defval=1, title="To Day", minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'to_month', 'op': '=', 'expr': 'input.int(defval=1, title="To Month", minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'to_year', 'op': '=', 'expr': 'input.int(defval=9999, title="To Year", minval=1900)', 'conditions': []}, {'mode': '', 'name': 'time_cond', 'op': '=', 'expr': 'time > timestamp(from_year, from_month, from_day, 00, 00) and', 'conditions': []}, {'mode': '', 'name': 'xLong', 'op': '=', 'expr': 'dayofmonth(time) == 30 and (close > dma200) ? true : na', 'conditions': []}, {'mode': '', 'name': 'xSell', 'op': '=', 'expr': 'dayofmonth(time) == 30 and (close < dma200) ? true : na', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (xLong == true) and time_cond'}, {'indent': 0, 'statement': 'if (xSell == true) and time_cond'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': ['(xLong == true) and time_cond'], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("long")', 'conditions': ['(xSell == true) and time_cond'], 'statement': 'strategy.close("long")'}]
    original_pine = '/*backtest\nstart: 2022-12-01 00:00:00\nend: 2023-12-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © muscleriot\n//200 dma\n//2000-2016 backtested \n//1 signal per month only at end of month\n//If > 200DMA enter long\n//If < 200DMA goto cash\n//results: 318% drawdown 17% vs 125% with 55% drawdown for buy and hold\n//@version=5\nstrategy("200DMA last DOM - ajh", overlay =true,default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n// Use 100% of  equity always\n\ndma200 = ta.sma(close, 200)\nplot(dma200, color=color.red, linewidth = 2)\n//e =dayofmonth(time)\n// backtesting date range\nfrom_day = input.int(defval=1, title="From Day", minval=1, maxval=31)\nfrom_month = input.int(defval=1, title="From Month", minval=1, maxval=12)\nfrom_year = input.int(defval=2018, title="From Year", minval=1900)\n\nto_day = input.int(defval=1, title="To Day", minval=1, maxval=31)\nto_month = input.int(defval=1, title="To Month", minval=1, maxval=12)\nto_year = input.int(defval=9999, title="To Year", minval=1900)\n\ntime_cond = time > timestamp(from_year, from_month, from_day, 00, 00) and \n   time < timestamp(to_year, to_month, to_day, 23, 59)\n\n\n\nxLong = dayofmonth(time) == 30 and (close > dma200) ? true : na\nxSell = dayofmonth(time) == 30 and (close < dma200) ? true : na\nplotchar(xLong, "long","L", color=color.green)    \nplotchar(xSell, "Sell","S", color=color.red)    \nif (xLong == true) and time_cond\n    strategy.entry("long", strategy.long)\nif (xSell == true) and time_cond\n    strategy.close("long")'

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
