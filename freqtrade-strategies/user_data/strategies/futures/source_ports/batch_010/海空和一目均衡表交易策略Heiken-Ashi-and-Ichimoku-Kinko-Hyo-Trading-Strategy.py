"""Source-faithful deep-assisted port of 海空和一目均衡表交易策略Heiken-Ashi-and-Ichimoku-Kinko-Hyo-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_06098e17(PinePortBase, IStrategy):
    source_file = '海空和一目均衡表交易策略Heiken-Ashi-and-Ichimoku-Kinko-Hyo-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'TenkanSenPeriods': 9, 'KijunSenPeriods': 24, 'SenkouSpanBPeriods': 51, 'displacement': 24}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', '=>', 'timeframe.']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'hahigh', 'op': '=', 'expr': 'security(heikinashi(syminfo.tickerid), timeframe.period, high)', 'conditions': []}, {'mode': '', 'name': 'halow', 'op': '=', 'expr': 'security(heikinashi(syminfo.tickerid), timeframe.period, low)', 'conditions': []}, {'mode': '', 'name': 'TenkanSenPeriods', 'op': '=', 'expr': 'input(9, minval=1, title="Tenkan Sen Periods")', 'conditions': []}, {'mode': '', 'name': 'KijunSenPeriods', 'op': '=', 'expr': 'input(24, minval=1, title="Kijun Sen Periods")', 'conditions': []}, {'mode': '', 'name': 'SenkouSpanBPeriods', 'op': '=', 'expr': 'input(51, minval=1, title="Senkou Span B Periods")', 'conditions': []}, {'mode': '', 'name': 'displacement', 'op': '=', 'expr': 'input(24, minval=1, title="Displacement")', 'conditions': []}, {'mode': '', 'name': 'TenkanSen', 'op': '=', 'expr': 'donchian(TenkanSenPeriods)', 'conditions': []}, {'mode': '', 'name': 'KijunSen', 'op': '=', 'expr': 'donchian(KijunSenPeriods)', 'conditions': []}, {'mode': '', 'name': 'SenkouSpanA', 'op': '=', 'expr': 'avg(TenkanSen, KijunSen)', 'conditions': []}, {'mode': '', 'name': 'SenkouSpanB', 'op': '=', 'expr': 'donchian(SenkouSpanBPeriods)', 'conditions': []}, {'mode': '', 'name': 'SenkouSpanH', 'op': '=', 'expr': 'max(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])', 'conditions': []}, {'mode': '', 'name': 'SenkouSpanL', 'op': '=', 'expr': 'min(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])', 'conditions': []}, {'mode': '', 'name': 'ChikouSpan', 'op': '=', 'expr': 'close[displacement-1]', 'conditions': []}, {'mode': '', 'name': 'sa', 'op': '=', 'expr': 'plot (SenkouSpanA, offset = displacement, color=green, title="Senkou Span A", linewidth = 2)', 'conditions': []}, {'mode': '', 'name': 'sb', 'op': '=', 'expr': 'plot (SenkouSpanB, offset = displacement, color=red, title="Senkou Span B", linewidth = 3)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'hahigh > max(hahigh[1],hahigh[2]) and close>ChikouSpan and close>SenkouSpanH and (TenkanSen>=KijunSen or close>KijunSen)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'halow < min(halow[1],halow[2]) and close<ChikouSpan and close<SenkouSpanL and (TenkanSen<=KijunSen or close<KijunSen)', 'conditions': []}, {'mode': '', 'name': 'closelong', 'op': '=', 'expr': 'halow < min(halow[1],halow[2]) and (TenkanSen<KijunSen or close<TenkanSen or close<KijunSen or close<SenkouSpanH or close<ChikouSpan)', 'conditions': []}, {'mode': '', 'name': 'closeshort', 'op': '=', 'expr': 'hahigh > max(hahigh[1],hahigh[2]) and (TenkanSen>KijunSen or close>TenkanSen or close>KijunSen or close>SenkouSpanL or close>ChikouSpan)', 'conditions': []}]
    pine_user_functions = [{'name': 'donchian', 'args': 'len', 'body': 'avg(lowest(len), highest(len))'}]
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (closelong)'}, {'indent': 0, 'statement': 'if (closeshort)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long",strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long",strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short",strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short",strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(closelong)'], 'statement': 'strategy.close("Long")'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(closeshort)'], 'statement': 'strategy.close("Short")'}]
    original_pine = '/*backtest\nstart: 2023-08-18 00:00:00\nend: 2023-09-17 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n\nstrategy("Heiken Ashi + Ichimoku Kinko Hyo Strategy", shorttitle="HaI", overlay=true, default_qty_type=strategy.percent_of_equity, max_bars_back=1000, default_qty_value=100, calc_on_order_fills= true, calc_on_every_tick=true, pyramiding=0)\n\nhahigh = security(heikinashi(syminfo.tickerid), timeframe.period, high)\nhalow = security(heikinashi(syminfo.tickerid), timeframe.period, low)\n\nTenkanSenPeriods = input(9, minval=1, title="Tenkan Sen Periods")\nKijunSenPeriods = input(24, minval=1, title="Kijun Sen Periods")\nSenkouSpanBPeriods = input(51, minval=1, title="Senkou Span B Periods")\ndisplacement = input(24, minval=1, title="Displacement")\ndonchian(len) => avg(lowest(len), highest(len))\nTenkanSen = donchian(TenkanSenPeriods)\nKijunSen = donchian(KijunSenPeriods)\nSenkouSpanA = avg(TenkanSen, KijunSen)\nSenkouSpanB = donchian(SenkouSpanBPeriods)\nSenkouSpanH = max(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])\nSenkouSpanL = min(SenkouSpanA[displacement - 1], SenkouSpanB[displacement - 1])\nChikouSpan = close[displacement-1]\n\nplot(TenkanSen, color=blue, title="Tenkan Sen", linewidth = 2)\nplot(KijunSen, color=maroon, title="Kijun Sen", linewidth = 3)\nplot(close, offset = -displacement, color=orange, title="Chikou Span", linewidth = 2)\nsa=plot (SenkouSpanA, offset = displacement, color=green,  title="Senkou Span A", linewidth = 2)\nsb=plot (SenkouSpanB, offset = displacement, color=red,  title="Senkou Span B", linewidth = 3)\nfill(sa, sb, color = SenkouSpanA > SenkouSpanB ? green : red)\n\nlongCondition = hahigh > max(hahigh[1],hahigh[2]) and close>ChikouSpan and close>SenkouSpanH and (TenkanSen>=KijunSen or close>KijunSen)\nif (longCondition)\n    strategy.entry("Long",strategy.long)\n\nshortCondition = halow < min(halow[1],halow[2]) and close<ChikouSpan and close<SenkouSpanL and (TenkanSen<=KijunSen or close<KijunSen)\nif (shortCondition)\n    strategy.entry("Short",strategy.short)\n\ncloselong = halow < min(halow[1],halow[2]) and (TenkanSen<KijunSen or close<TenkanSen or close<KijunSen or close<SenkouSpanH or close<ChikouSpan)\nif (closelong)\n    strategy.close("Long")\n\ncloseshort = hahigh > max(hahigh[1],hahigh[2]) and (TenkanSen>KijunSen or close>TenkanSen or close>KijunSen or close>SenkouSpanL or close>ChikouSpan)\nif (closeshort)\n    strategy.close("Short")'

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
