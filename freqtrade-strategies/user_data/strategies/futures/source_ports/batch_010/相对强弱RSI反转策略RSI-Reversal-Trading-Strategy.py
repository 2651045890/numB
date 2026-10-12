"""Source-faithful deep-assisted port of 相对强弱RSI反转策略RSI-Reversal-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_242a228d(PinePortBase, IStrategy):
    source_file = '相对强弱RSI反转策略RSI-Reversal-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'len': 2, 'src': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.cancel', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': 'var', 'name': 'lots', 'op': '=', 'expr': '0.1', 'conditions': []}, {'mode': 'var', 'name': 'fixed_commission', 'op': '=', 'expr': '10 // BTC commission value USD per position size two sides', 'conditions': []}, {'mode': 'var', 'name': 'money', 'op': '=', 'expr': '0.3333 //BTC position size', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input(2, minval=1, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, "RSI Source", type = input.source)', 'conditions': []}, {'mode': '', 'name': 'upRsi', 'op': '=', 'expr': 'rma(max(change(src), 0), len)', 'conditions': []}, {'mode': '', 'name': 'downRsi', 'op': '=', 'expr': 'rma(-min(change(src), 0), len)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'downRsi == 0 ? 100 : upRsi == 0 ? 0 : 100 - (100 / (1 + upRsi / downRsi))', 'conditions': []}, {'mode': 'var', 'name': 'buyColor', 'op': '=', 'expr': 'color.blue', 'conditions': []}, {'mode': 'var', 'name': 'sellColor', 'op': '=', 'expr': 'color.red', 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'rsi >= 90', 'conditions': []}, {'mode': 'var', 'name': 'shortsl', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'short_ts_points', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'shortsl', 'op': ':=', 'expr': 'high', 'conditions': ['short']}, {'mode': '', 'name': 'short_ts_points', 'op': ':=', 'expr': '200', 'conditions': ['short']}, {'mode': '', 'name': 'short_ts_points', 'op': ':=', 'expr': '100', 'conditions': ['rsi <= 30']}, {'mode': '', 'name': 'short_ts_points', 'op': ':=', 'expr': '80', 'conditions': ['rsi <= 20']}, {'mode': 'var', 'name': 'barsPassedSh', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'barsPassedSh', 'op': ':=', 'expr': 'barssince(short)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if short'}, {'indent': 0, 'statement': 'if rsi <= 30'}, {'indent': 0, 'statement': 'else if rsi <= 20'}, {'indent': 0, 'statement': 'if short'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("short", long = strategy.short, qty = money, stop = low)', 'conditions': ['short'], 'statement': 'strategy.entry("short", long = strategy.short, qty = money, stop = low)'}, {'kind': 'exit', 'call': 'strategy.exit("slSh", from_entry="short", stop = shortsl, trail_points = short_ts_points, trail_offset =20 )', 'conditions': [], 'statement': 'strategy.exit("slSh", from_entry="short", stop = shortsl, trail_points = short_ts_points, trail_offset =20 )'}, {'kind': 'cancel_all', 'call': 'strategy.cancel_all(barsPassedSh > 3 and not short)', 'conditions': [], 'statement': 'strategy.cancel_all(barsPassedSh > 3 and not short)'}]
    original_pine = '/*backtest\nstart: 2023-11-06 00:00:00\nend: 2023-11-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// Copyright (c) 2021-present, RicMos\n//study("RSI2 Sell Strategy, overlay=true)\n\n//------------------------------------------USER VARIABLE DEFINITIONS --------------------------------------\nvar float lots = 0.1\n//var float fixed_commission = 0.6 // forex pairs commission  value USD per position size two sides\nvar float fixed_commission = 10 // BTC commission value USD per position size two sides\n//var float money = 10000 //forex pairs position size\nvar float money = 0.3333 //BTC position size\n\n\n\nstrategy(title="RSI2 Sell Strategy", commission_type=strategy.commission.cash_per_order, calc_on_every_tick =true, commission_value = fixed_commission/2, overlay=true, default_qty_value= lots*100000, initial_capital=1000, currency = "USD", calc_on_order_fills = false)\nlen = input(2, minval=1, title="RSI Length")\nsrc = input(close, "RSI Source", type = input.source)\nupRsi = rma(max(change(src), 0), len)\ndownRsi = rma(-min(change(src), 0), len)\nrsi = downRsi == 0 ? 100 : upRsi == 0 ? 0 : 100 - (100 / (1 + upRsi / downRsi))\nvar color buyColor = color.blue\nvar color sellColor = color.red\n\n\nplotshape(rsi <= 10 ? low : na, title="Arrow Up", style=shape.triangleup, location=location.belowbar, size=size.tiny, color=buyColor)\nplotshape(rsi >= 90 ? high : na, title="Arrow Down", style=shape.triangledown, location=location.abovebar, size=size.tiny, color=sellColor)\n\n\n// long = rsi <= 10 \n// var float longsl = 0\n// var int long_ts_points = 0\n\n// if long\n//     longsl:= low\n//     long_ts_points := 200\n    \n// if rsi >= 70\n//     long_ts_points := 100\n// else if rsi >= 80\n//     long_ts_points := 80\n\n\n// plot (longsl)\n// var int barsPassed = 0\n// barsPassed := barssince(long)\n// if long\n//     strategy.entry("long", long = strategy.long, qty = 10000, stop = high)\n// strategy.exit("slLo", from_entry="long", stop = longsl-0.0002, trail_points = long_ts_points )\n// //strategy.close("long", when = rsi[1]>=50 and rsi < 50 , comment = "rsi under 50" )\n// strategy.cancel_all(barsPassed > 3  and not long)\n\n\nshort = rsi >= 90 \nvar float shortsl = 0\nvar int short_ts_points = 0\n//var bool stClose = 0\n\nif short\n    shortsl:= high\n    short_ts_points := 200\n    \nif rsi <= 30\n    short_ts_points := 100\n    //stClose :=1\nelse if rsi <= 20\n    short_ts_points := 80 \n//else\n    //stClose := 0\n\nplot (shortsl)\nvar int barsPassedSh = 0\nbarsPassedSh := barssince(short)\nif short\n    strategy.entry("short", long = strategy.short, qty = money, stop = low)\nstrategy.exit("slSh", from_entry="short", stop = shortsl, trail_points = short_ts_points, trail_offset =20 )\n//strategy.close("short", comment="rsi<30", when = stClose)\n\n\n//strategy.close("long", when = rsi[1]>=50 and rsi < 50 , comment = "rsi under 50" )\nstrategy.cancel_all(barsPassedSh > 3  and not short)'

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
