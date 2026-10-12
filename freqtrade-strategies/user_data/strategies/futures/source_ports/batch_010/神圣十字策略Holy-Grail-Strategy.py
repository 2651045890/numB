"""Source-faithful deep-assisted port of 神圣十字策略Holy-Grail-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_456debab(PinePortBase, IStrategy):
    source_file = '神圣十字策略Holy-Grail-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'testStartYear': 2018, 'testStartMonth': 4, 'testStartDay': 15, 'testStopYear': 2018, 'testStopMonth': 5, 'testStopDay': 30, 'testPeriodBackground': True, 'len3': 14, 'lensig3': 14, 'target': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'switch', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'testStartYear', 'op': '=', 'expr': 'input(2018, "Backtest Start Year")', 'conditions': []}, {'mode': '', 'name': 'testStartMonth', 'op': '=', 'expr': 'input(4, "Backtest Start Month")', 'conditions': []}, {'mode': '', 'name': 'testStartDay', 'op': '=', 'expr': 'input(15, "Backtest Start Day")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStart', 'op': '=', 'expr': 'timestamp(testStartYear,testStartMonth,testStartDay,0,0)', 'conditions': []}, {'mode': '', 'name': 'testStopYear', 'op': '=', 'expr': 'input(2018, "Backtest Stop Year")', 'conditions': []}, {'mode': '', 'name': 'testStopMonth', 'op': '=', 'expr': 'input(5, "Backtest Stop Month")', 'conditions': []}, {'mode': '', 'name': 'testStopDay', 'op': '=', 'expr': 'input(30, "Backtest Stop Day")', 'conditions': []}, {'mode': '', 'name': 'testPeriodStop', 'op': '=', 'expr': 'timestamp(testStopYear,testStopMonth,testStopDay,0,0)', 'conditions': []}, {'mode': '', 'name': 'testPeriodBackground', 'op': '=', 'expr': 'input(title="Color Background?", type=bool, defval=true)', 'conditions': []}, {'mode': '', 'name': 'testPeriodBackgroundColor', 'op': '=', 'expr': 'testPeriodBackground and (time >= testPeriodStart) and (time <= testPeriodStop) ? #00FF00 : na', 'conditions': []}, {'mode': '', 'name': 'myema', 'op': '=', 'expr': 'ema(close, 20)', 'conditions': []}, {'mode': '', 'name': 'len3', 'op': '=', 'expr': 'input(14, minval=1, title="DI Length") /////////////////////', 'conditions': []}, {'mode': '', 'name': 'lensig3', 'op': '=', 'expr': 'input(14, title="ADX Smoothing", minval=1, maxval=50) ////////////////////', 'conditions': []}, {'mode': '', 'name': 'up3', 'op': '=', 'expr': 'change(high) ///////////////////', 'conditions': []}, {'mode': '', 'name': 'down3', 'op': '=', 'expr': '-change(low) //////////////////', 'conditions': []}, {'mode': '', 'name': 'plusDM3', 'op': '=', 'expr': 'na(up3) ? na : (up3 > down3 and up3 > 0 ? up3 : 0) /////////////////', 'conditions': []}, {'mode': '', 'name': 'minusDM3', 'op': '=', 'expr': 'na(down3) ? na : (down3 > up3 and down3 > 0 ? down3 : 0) ////////////////', 'conditions': []}, {'mode': '', 'name': 'trur3', 'op': '=', 'expr': 'rma(tr, len3) ///////////////', 'conditions': []}, {'mode': '', 'name': 'plus3', 'op': '=', 'expr': 'fixnan(100 * rma(plusDM3, len3) / trur3) //////////////', 'conditions': []}, {'mode': '', 'name': 'minus3', 'op': '=', 'expr': 'fixnan(100 * rma(minusDM3, len3) / trur3) /////////////', 'conditions': []}, {'mode': '', 'name': 'sum3', 'op': '=', 'expr': 'plus3 + minus3 ////////////', 'conditions': []}, {'mode': '', 'name': 'adx3', 'op': '=', 'expr': '100 * rma(abs(plus3 - minus3) / (sum3 == 0 ? 1 : sum3), lensig3) ///////////', 'conditions': []}, {'mode': '', 'name': 'target', 'op': '=', 'expr': 'input(30, title=" ADX Target Line") ///////', 'conditions': []}]
    pine_user_functions = [{'name': 'testPeriod', 'args': '', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (adx3 <= target) and crossover(close, myema)'}, {'indent': 0, 'statement': 'if (adx3 >= target) and crossunder(close, myema)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("HolyGrail", strategy.long, comment="Long")', 'conditions': ['(adx3 <= target) and crossover(close, myema)'], 'statement': 'strategy.entry("HolyGrail", strategy.long, comment="Long")'}, {'kind': 'entry', 'call': 'strategy.entry("HolyGrail", strategy.short, comment="Short")', 'conditions': ['(adx3 >= target) and crossunder(close, myema)'], 'statement': 'strategy.entry("HolyGrail", strategy.short, comment="Short")'}]
    original_pine = '/*backtest\nstart: 2022-11-24 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("LAT Holy Grail v3", overlay=true)\n\n/////////////TEST TIME ////////////////////////\ntestStartYear = input(2018, "Backtest Start Year")\ntestStartMonth = input(4, "Backtest Start Month")\ntestStartDay = input(15, "Backtest Start Day")\ntestPeriodStart = timestamp(testStartYear,testStartMonth,testStartDay,0,0)\n\ntestStopYear = input(2018, "Backtest Stop Year")\ntestStopMonth = input(5, "Backtest Stop Month")\ntestStopDay = input(30, "Backtest Stop Day")\ntestPeriodStop = timestamp(testStopYear,testStopMonth,testStopDay,0,0)\n\n// A switch to control background coloring of the test period\ntestPeriodBackground = input(title="Color Background?", type=bool, defval=true)\ntestPeriodBackgroundColor = testPeriodBackground and (time >= testPeriodStart) and (time <= testPeriodStop) ? #00FF00 : na\nbgcolor(testPeriodBackgroundColor, transp=97)\n\ntestPeriod() =>\n    time >= testPeriodStart and time <= testPeriodStop ? true : false\n//////////////////////////////////////////////////////////////////////\n\nmyema= ema(close, 20)\nplot(myema, color=green, title="eMA", linewidth=3)\n\n\n\n//longCondition = (crossover(close, myema)) //and adx3 < target\n//if (longCondition)\n    //strategy.entry("My Long Entry Id", strategy.long)\n\n//shortCondition = (crossunder(close, myema)) //and adx3 > target\n//if (shortCondition)\n    //strategy.entry("My Short Entry Id", strategy.short)\n    \n    //////////////////////////////////////////////////////////\n    ///////////////////////////////////////   DMI  ///////////////////////////////////////////////\nlen3 = input(14, minval=1, title="DI Length")                           /////////////////////\nlensig3 = input(14, title="ADX Smoothing", minval=1, maxval=50)         ////////////////////\nup3 = change(high)                                                      ///////////////////\ndown3 = -change(low)                                                    //////////////////\nplusDM3 = na(up3) ? na : (up3 > down3 and up3 > 0 ? up3 : 0)            /////////////////\nminusDM3 = na(down3) ? na : (down3 > up3 and down3 > 0 ? down3 : 0)     ////////////////\ntrur3 = rma(tr, len3)                                                   ///////////////\nplus3 = fixnan(100 * rma(plusDM3, len3) / trur3)                        //////////////\nminus3 = fixnan(100 * rma(minusDM3, len3) / trur3)                      /////////////\nsum3 = plus3 + minus3                                                   ////////////\nadx3 = 100 * rma(abs(plus3 - minus3) / (sum3 == 0 ? 1 : sum3), lensig3) ///////////\n//plot(plus3, color=green, style=circles, linewidth=2, title="+DI")     //////////\n//plot(minus3, color=red, style=circles, linewidth=2, title="-DI")      /////////\nplot(adx3, color=aqua, style=line, linewidth=3, title="ADX")            ////////\ntarget = input(30, title=" ADX Target Line")                            ///////\nplot(target, color=yellow, title="ADX Target Line")                     //////\n/////////////////////////////////////////////////////////////////////////////////////////////////\n                                                                                        \nplot(hl2)\n\n\n///////////////////////////////////////////////  eMA SIGNAL LINE   ///////////////////////////////////////\n\n//////////////////////////////////////////////////////////////////////////////////////////////////////////\n\n//////////////////////////////////////// HOLY GRAIL STRATEGY ///////////////////////////////////////////////////////////////////\n\nif (adx3 <= target) and crossover(close, myema)\n    strategy.entry("HolyGrail", strategy.long, comment="Long")\n \nif (adx3 >= target) and crossunder(close, myema)\n    strategy.entry("HolyGrail", strategy.short, comment="Short")'

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
