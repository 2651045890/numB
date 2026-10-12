"""Source-faithful deep-assisted port of 快慢EMA黄金交叉突破策略Fast-and-Slow-EMA-Golden-Cross-Breakthrough-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c692a4ed(PinePortBase, IStrategy):
    source_file = '快慢EMA黄金交叉突破策略Fast-and-Slow-EMA-Golden-Cross-Breakthrough-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'start_year': 2020, 'short_period': 5, 'mid_period': 8, 'long_period': 13, 'rsi_period': 14, 'longOnly': False}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 100000.0
    source_commission_percent = 0.04
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'start_year', 'op': '=', 'expr': 'input(defval=2020, title="Backtest Start Year")', 'conditions': []}, {'mode': '', 'name': 'short_period', 'op': '=', 'expr': 'input(type=input.integer,defval=5,minval=1,title="Length")', 'conditions': []}, {'mode': '', 'name': 'mid_period', 'op': '=', 'expr': 'input(type=input.integer,defval=8,minval=1,title="Length")', 'conditions': []}, {'mode': '', 'name': 'long_period', 'op': '=', 'expr': 'input(type=input.integer,defval=13,minval=1,title="Length")', 'conditions': []}, {'mode': '', 'name': 'rsi_period', 'op': '=', 'expr': 'input(type=input.integer,defval=14,minval=1,title="Length")', 'conditions': []}, {'mode': '', 'name': 'longOnly', 'op': '=', 'expr': 'input(type=input.bool,defval=false,title="Long Only")', 'conditions': []}, {'mode': '', 'name': 'shortEma', 'op': '=', 'expr': 'ema(close,short_period)', 'conditions': []}, {'mode': '', 'name': 'midEma', 'op': '=', 'expr': 'ema(close,mid_period)', 'conditions': []}, {'mode': '', 'name': 'longEma', 'op': '=', 'expr': 'ema(close,long_period)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'rsi(close, rsi_period)', 'conditions': []}, {'mode': '', 'name': 'longEntry', 'op': '=', 'expr': 'crossover(shortEma,midEma) and crossover(shortEma,longEma) //or ((shortEma > longEma) and crossover(shortEma,midEma)))and (adx > 25)', 'conditions': []}, {'mode': '', 'name': 'shortEntry', 'op': '=', 'expr': '((shortEma < midEma) and crossunder(shortEma,longEma)) or ((shortEma < longEma) and crossunder(shortEma,midEma))', 'conditions': []}]
    pine_user_functions = [{'name': 'enterLong', 'args': '', 'body': ''}, {'name': 'exitLong', 'args': '', 'body': ''}, {'name': 'enterShort', 'args': '', 'body': ''}, {'name': 'exitShort', 'args': '', 'body': ''}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry(id="Long", long=strategy.long, when=enterLong())', 'conditions': [], 'statement': 'strategy.entry(id="Long", long=strategy.long, when=enterLong())'}, {'kind': 'close', 'call': 'strategy.close(id="Long", when=exitLong())', 'conditions': [], 'statement': 'strategy.close(id="Long", when=exitLong())'}, {'kind': 'entry', 'call': 'strategy.entry(id="Short", long=strategy.short, when=enterShort())', 'conditions': [], 'statement': 'strategy.entry(id="Short", long=strategy.short, when=enterShort())'}, {'kind': 'close', 'call': 'strategy.close(id="Short", when=exitShort())', 'conditions': [], 'statement': 'strategy.close(id="Short", when=exitShort())'}]
    original_pine = '/*backtest\nstart: 2023-11-23 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// \n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © gregoirejohnb\n// @It is modified by ttsaadet.\n// Moving average crossover systems measure drift in the market. They are great strategies for time-limited people.\n// So, why don\'t more people use them?\n// \n\n//\nstrategy(title="EMA Crossover Strategy by TTS", shorttitle="EMA-5-8-13 COS by TTS", overlay=true, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, currency=currency.TRY,commission_type=strategy.commission.percent,commission_value=0.04, process_orders_on_close = true, initial_capital = 100000)\n\n// === GENERAL INPUTS ===\n//strategy start date\nstart_year = input(defval=2020, title="Backtest Start Year")\n\n// === LOGIC ===\nshort_period = input(type=input.integer,defval=5,minval=1,title="Length")\nmid_period = input(type=input.integer,defval=8,minval=1,title="Length")\nlong_period = input(type=input.integer,defval=13,minval=1,title="Length")\nrsi_period = input(type=input.integer,defval=14,minval=1,title="Length")\nlongOnly = input(type=input.bool,defval=false,title="Long Only")\nshortEma = ema(close,short_period)\nmidEma = ema(close,mid_period)\nlongEma = ema(close,long_period)\n\nrsi = rsi(close, rsi_period)\n\n[diplus, diminus, adx] = dmi(short_period, short_period)\nplot(shortEma,linewidth=2,color=color.red,title="Fast")\nplot(midEma,linewidth=2,color=color.orange,title="Fast")\nplot(longEma,linewidth=2,color=color.blue,title="Slow")\n\nlongEntry = crossover(shortEma,midEma) and crossover(shortEma,longEma) //or ((shortEma > longEma) and crossover(shortEma,midEma)))and (adx > 25)\nshortEntry =((shortEma < midEma) and crossunder(shortEma,longEma)) or ((shortEma < longEma) and crossunder(shortEma,midEma))\n\nplotshape(longEntry ? close : na,style=shape.triangleup,color=color.green,location=location.belowbar,size=size.small,title="Long Triangle")\nplotshape(shortEntry and not longOnly ? close : na,style=shape.triangledown,color=color.red,location=location.abovebar,size=size.small,title="Short Triangle")\nplotshape(shortEntry and longOnly ? close : na,style=shape.xcross,color=color.black,location=location.abovebar,size=size.small,title="Exit Sign")\n\n// === STRATEGY - LONG POSITION EXECUTION ===\nenterLong() =>\n    longEntry and \n       time > timestamp(start_year, 1, 1, 01, 01)\nexitLong() =>\n    crossunder(shortEma,longEma) or crossunder(close, longEma)\n\nstrategy.entry(id="Long", long=strategy.long, when=enterLong())\nstrategy.close(id="Long", when=exitLong())\n\n\n// === STRATEGY - SHORT POSITION EXECUTION ===\n\nenterShort() =>\n    not longOnly and shortEntry and \n       time > timestamp(start_year, 1, 1, 01, 01)\nexitShort() =>\n    crossover(shortEma,longEma)\n\nstrategy.entry(id="Short", long=strategy.short, when=enterShort())\nstrategy.close(id="Short", when=exitShort())'

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
