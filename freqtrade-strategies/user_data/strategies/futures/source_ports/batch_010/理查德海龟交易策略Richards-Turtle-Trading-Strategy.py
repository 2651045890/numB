"""Source-faithful deep-assisted port of 理查德海龟交易策略Richards-Turtle-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_02695f71(PinePortBase, IStrategy):
    source_file = '理查德海龟交易策略Richards-Turtle-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'variable_for_stoploss': 4, 'lenght': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.']
    pine_assignments = [{'mode': '', 'name': 'variable_for_stoploss', 'op': '=', 'expr': 'input(4,title="stop loss var")', 'conditions': []}, {'mode': '', 'name': 'lenght', 'op': '=', 'expr': 'input(20,title="lenght")', 'conditions': []}, {'mode': '', 'name': '_20_day_highest', 'op': '=', 'expr': 'highest(nz(close[1]), lenght)', 'conditions': []}, {'mode': '', 'name': '_20_day_lowest', 'op': '=', 'expr': 'lowest(nz(close[1]), lenght)', 'conditions': []}, {'mode': '', 'name': '_10_day_low', 'op': '=', 'expr': 'lowest(nz(close[1]), lenght/2)', 'conditions': []}, {'mode': '', 'name': '_10_day_high', 'op': '=', 'expr': 'highest(nz(close[1]), lenght/2)', 'conditions': []}, {'mode': '', 'name': 'atr20', 'op': '=', 'expr': 'atr(20)', 'conditions': []}, {'mode': '', 'name': 'ema_atr20', 'op': '=', 'expr': 'ema(atr20,20)', 'conditions': []}, {'mode': 'var', 'name': 'traded', 'op': '=', 'expr': '"false"', 'conditions': []}, {'mode': 'var', 'name': 'buy_sell', 'op': '=', 'expr': '"none"', 'conditions': []}, {'mode': 'var', 'name': 'buyExit', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'sellExit', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'var', 'name': 'stoploss', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'buyCon', 'op': '=', 'expr': 'close > _20_day_highest and traded == "false"', 'conditions': []}, {'mode': '', 'name': 'traded', 'op': ':=', 'expr': '"true"', 'conditions': ['(buyCon)']}, {'mode': '', 'name': 'buy_sell', 'op': ':=', 'expr': '"buy"', 'conditions': ['(buyCon)']}, {'mode': '', 'name': 'stoploss', 'op': ':=', 'expr': 'round(close - variable_for_stoploss * ema_atr20)', 'conditions': ['(buyCon)']}, {'mode': '', 'name': 'sellCon', 'op': '=', 'expr': 'close < _20_day_lowest and traded == "false"', 'conditions': []}, {'mode': '', 'name': 'traded', 'op': ':=', 'expr': '"true"', 'conditions': ['(sellCon)']}, {'mode': '', 'name': 'buy_sell', 'op': ':=', 'expr': '"sell"', 'conditions': ['(sellCon)']}, {'mode': '', 'name': 'stoploss', 'op': ':=', 'expr': 'round(close - variable_for_stoploss * ema_atr20)', 'conditions': ['(sellCon)']}, {'mode': '', 'name': 'buyExit', 'op': ':=', 'expr': 'true', 'conditions': ['traded == "true"', 'buy_sell == "buy" and ((close<stoploss)or(close<_10_day_low))']}, {'mode': '', 'name': 'traded', 'op': ':=', 'expr': '"false"', 'conditions': ['traded == "true"', 'buy_sell == "buy" and ((close<stoploss)or(close<_10_day_low))']}, {'mode': '', 'name': 'sellExit', 'op': ':=', 'expr': 'true', 'conditions': ['traded == "true"', 'buy_sell == "sell" and ((close>stoploss)or(close>_10_day_high))']}, {'mode': '', 'name': 'traded', 'op': ':=', 'expr': '"false"', 'conditions': ['traded == "true"', 'buy_sell == "sell" and ((close>stoploss)or(close>_10_day_high))']}, {'mode': '', 'name': 'buyExit', 'op': ':=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'sellExit', 'op': ':=', 'expr': 'false', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCon)'}, {'indent': 0, 'statement': 'if (sellCon)'}, {'indent': 0, 'statement': 'if traded == "true"'}, {'indent': 4, 'statement': 'if buy_sell == "buy" and ((close<stoploss)or(close<_10_day_low))'}, {'indent': 4, 'statement': 'if buy_sell == "sell" and ((close>stoploss)or(close>_10_day_high))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long, when = buyCon)', 'conditions': ['(buyCon)'], 'statement': 'strategy.entry("long", strategy.long, when = buyCon)'}, {'kind': 'entry', 'call': 'strategy.entry("short", strategy.short)', 'conditions': ['(sellCon)'], 'statement': 'strategy.entry("short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("long")', 'conditions': ['traded == "true"', 'buy_sell == "buy" and ((close<stoploss)or(close<_10_day_low))'], 'statement': 'strategy.close("long")'}, {'kind': 'close', 'call': 'strategy.close("short")', 'conditions': ['traded == "true"', 'buy_sell == "sell" and ((close>stoploss)or(close>_10_day_high))'], 'statement': 'strategy.close("short")'}]
    original_pine = '/*backtest\nstart: 2023-02-05 00:00:00\nend: 2024-02-05 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © melodyera0822\n\n//@version=4\nstrategy("Richard Strategy", overlay=true)\n\n// User input\nvariable_for_stoploss = input(4,title="stop loss var")\nlenght = input(20,title="lenght")\n\n// high_low\n_20_day_highest = highest(nz(close[1]), lenght)\n_20_day_lowest = lowest(nz(close[1]), lenght)\n\n_10_day_low = lowest(nz(close[1]), lenght/2)\n_10_day_high = highest(nz(close[1]), lenght/2)\n\n//indicators\natr20 = atr(20)\nema_atr20 = ema(atr20,20)\n\n//vars\nvar traded = "false"\nvar buy_sell = "none"\nvar buyExit = false\nvar sellExit = false\nvar stoploss = 0\n\nbuyCon = close > _20_day_highest and traded == "false"\nplotshape(buyCon,style = shape.triangleup,location = location.belowbar, color = color.green )\nif (buyCon)\n    strategy.entry("long", strategy.long, when = buyCon)\n    traded := "true"\n    buy_sell := "buy"\n    stoploss := round(close - variable_for_stoploss * ema_atr20)\n    \nsellCon = close < _20_day_lowest and  traded == "false"\nplotshape(sellCon,style = shape.triangledown, color = color.red )\nif (sellCon)\n    strategy.entry("short", strategy.short)\n    traded := "true"\n    buy_sell := "sell"\n    stoploss := round(close - variable_for_stoploss * ema_atr20)\n\nif traded == "true"\n    if buy_sell == "buy" and ((close<stoploss)or(close<_10_day_low))\n        strategy.close("long")\n        buyExit := true\n        traded := "false"\n        \n    if buy_sell == "sell" and ((close>stoploss)or(close>_10_day_high))\n        strategy.close("short")\n        sellExit := true\n        traded := "false"\n        \nplotshape(buyExit,style = shape.triangleup,location = location.belowbar, color = color.yellow )\nbuyExit := false\nplotshape(sellExit,style = shape.triangledown, color = color.yellow )\nsellExit := false'

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
