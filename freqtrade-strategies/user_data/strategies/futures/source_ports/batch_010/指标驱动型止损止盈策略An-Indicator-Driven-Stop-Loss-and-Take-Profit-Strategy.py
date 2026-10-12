"""Source-faithful deep-assisted port of 指标驱动型止损止盈策略An-Indicator-Driven-Stop-Loss-and-Take-Profit-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7d76dfc3(PinePortBase, IStrategy):
    source_file = '指标驱动型止损止盈策略An-Indicator-Driven-Stop-Loss-and-Take-Profit-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lo': -5.0, 'tp': 5.0, 'sl': 2.0, 'disp_panels': True, 'info_label_off': 20, 'info_label_size': 'size.large'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.cancel', 'strategy.position_size', 'for ', 'label.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'lo', 'op': '=', 'expr': 'input(-5.0, title = "Long-line, %")', 'conditions': []}, {'mode': '', 'name': 'tp', 'op': '=', 'expr': 'input(5.0, title = "Take-profit")', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'input(2.0, title = "Stop-loss")', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': 'sma(ohlc4, 3)', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'ma + ((ma / 100) * lo)', 'conditions': []}, {'mode': '', 'name': 'avg', 'op': '=', 'expr': 'strategy.position_avg_price', 'conditions': []}, {'mode': '', 'name': 'take', 'op': '=', 'expr': 'avg != 0 ? avg + ((avg / 100) * tp) : long + ((long / 100) * tp)', 'conditions': []}, {'mode': '', 'name': 'stop', 'op': '=', 'expr': 'avg != 0 ? avg - ((avg / 100) * sl) : long - ((long / 100) * sl)', 'conditions': []}, {'mode': '', 'name': 'takelinecolor', 'op': '=', 'expr': 'avg == avg[1] and avg != 0 ? color.lime : na', 'conditions': []}, {'mode': '', 'name': 'stoplinecolor', 'op': '=', 'expr': 'avg == avg[1] and avg != 0 ? color.red : na', 'conditions': []}, {'mode': '', 'name': 'disp_panels', 'op': '=', 'expr': 'input(true, title="Display info panels?")', 'conditions': []}, {'mode': '', 'name': 'h', 'op': '=', 'expr': 'high', 'conditions': []}, {'mode': '', 'name': 'info_label_off', 'op': '=', 'expr': 'input(20, title="Info panel offset")', 'conditions': []}, {'mode': '', 'name': 'info_label_size', 'op': '=', 'expr': 'input(size.large, options=[size.tiny, size.small, size.normal, size.large, size.huge], title="Info panel label size")', 'conditions': []}, {'mode': '', 'name': 'info_panel_x', 'op': '=', 'expr': 'timenow + round(change(time)*info_label_off)', 'conditions': []}, {'mode': '', 'name': 'info_panel_y', 'op': '=', 'expr': 'h', 'conditions': []}, {'mode': '', 'name': 'info_title', 'op': '=', 'expr': '"-=-=-=-=- Info Panel -=-=-=-=-"', 'conditions': []}, {'mode': '', 'name': 'info_div', 'op': '=', 'expr': '"\\n\\n------------------------------"', 'conditions': []}, {'mode': '', 'name': 'a', 'op': '=', 'expr': '"\\n\\ Long : " + tostring(long)', 'conditions': []}, {'mode': '', 'name': 'b', 'op': '=', 'expr': '"\\n\\ Stop loss : " + tostring(stop)', 'conditions': []}, {'mode': '', 'name': 'c', 'op': '=', 'expr': '"\\n\\ TP : " + tostring(take)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if ma > 0'}, {'indent': 0, 'statement': 'if strategy.position_size == 0'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, limit = long)', 'conditions': ['ma > 0'], 'statement': 'strategy.entry("Long", strategy.long, limit = long)'}, {'kind': 'entry', 'call': 'strategy.entry("Take", strategy.short, 0, limit = avg + ((avg / 100) * tp))', 'conditions': ['ma > 0'], 'statement': 'strategy.entry("Take", strategy.short, 0, limit = avg + ((avg / 100) * tp))'}, {'kind': 'entry', 'call': 'strategy.entry("Stop", strategy.short, 0, stop = avg - ((avg / 100) * sl))', 'conditions': ['ma > 0'], 'statement': 'strategy.entry("Stop", strategy.short, 0, stop = avg - ((avg / 100) * sl))'}, {'kind': 'cancel', 'call': 'strategy.cancel("Take")', 'conditions': ['strategy.position_size == 0'], 'statement': 'strategy.cancel("Take")'}, {'kind': 'cancel', 'call': 'strategy.cancel("Stop")', 'conditions': ['strategy.position_size == 0'], 'statement': 'strategy.cancel("Stop")'}]
    original_pine = '/*backtest\nstart: 2023-01-01 00:00:00\nend: 2023-11-09 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("example for panel signals", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n//https://www.tradingview.com/script/m2a04xmb-noro-s-shiftma-tp-sl-strategy/\n//Settings\nlo = input(-5.0, title = "Long-line, %")\ntp = input(5.0, title = "Take-profit")\nsl = input(2.0, title = "Stop-loss")\n\n//SMA\nma = sma(ohlc4, 3)\nlong = ma + ((ma / 100) * lo)\n\n//Orders\navg = strategy.position_avg_price\nif ma > 0\n    strategy.entry("Long", strategy.long, limit = long)\n    strategy.entry("Take", strategy.short, 0, limit = avg + ((avg / 100) * tp))\n    strategy.entry("Stop", strategy.short, 0, stop = avg - ((avg / 100) * sl))\n    \n//Cancel order\nif strategy.position_size == 0\n    strategy.cancel("Take")\n    strategy.cancel("Stop")\n\n//Lines\nplot(long, offset = 1, color = color.black, transp = 0)\ntake = avg != 0 ? avg + ((avg / 100) * tp) : long + ((long / 100) * tp)\nstop = avg != 0 ? avg - ((avg / 100) * sl) : long - ((long / 100) * sl)\ntakelinecolor = avg == avg[1] and avg != 0 ? color.lime : na\nstoplinecolor = avg == avg[1] and avg != 0 ? color.red : na\nplot(take, offset = 1, color = takelinecolor, linewidth = 3, transp = 0)\nplot(stop, offset = 1, color = stoplinecolor, linewidth = 3, transp = 0)\n//\ndisp_panels = input(true, title="Display info panels?")\nh=high\ninfo_label_off = input(20, title="Info panel offset")\ninfo_label_size = input(size.large, options=[size.tiny, size.small, size.normal, size.large, size.huge], title="Info panel label size")\ninfo_panel_x = timenow + round(change(time)*info_label_off)\ninfo_panel_y = h\n\ninfo_title= "-=-=-=-=- Info Panel -=-=-=-=-"\ninfo_div = "\\n\\n------------------------------"\na = "\\n\\ Long : " + tostring(long)\nb = "\\n\\ Stop loss : " + tostring(stop)\nc = "\\n\\ TP : " + tostring(take)\n// info_text = a+c+b\n// info_panel = disp_panels ? label.new(x=info_panel_x, y=info_panel_y, text=info_text, xloc=xloc.bar_time, yloc=yloc.price, color=color.yellow, style=label.style_labelup, textcolor=color.black, size=info_label_size) : na\n// label.delete(info_panel[1])'

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
