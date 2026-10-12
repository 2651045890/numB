"""Source-faithful deep-assisted port of 短线动量反转策略Momentum-Reversal-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6e9c35d4(PinePortBase, IStrategy):
    source_file = '短线动量反转策略Momentum-Reversal-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'x': 5, 'percentChangePos': 0.4, 'percentChangeNeg': -0.4}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'for ', '=>', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'x', 'op': '=', 'expr': "input(5, title = 'x candles difference', minval = 1)", 'conditions': []}, {'mode': '', 'name': 'trueChange1', 'op': '=', 'expr': '(close - close[x]) / close[x] * 100', 'conditions': []}, {'mode': '', 'name': 'percentChangePos', 'op': '=', 'expr': 'input(0.4, title="Percent Change")', 'conditions': []}, {'mode': '', 'name': 'trueChange2', 'op': '=', 'expr': '(close - close[x]) / close[x] * 100', 'conditions': []}, {'mode': '', 'name': 'percentChangeNeg', 'op': '=', 'expr': 'input(-0.4, title="Percent Change")', 'conditions': []}, {'mode': '', 'name': 'col', 'op': '=', 'expr': 'percentChangePos < trueChange1 ? color.lime : percentChangeNeg > trueChange2 ? color.red : color.white', 'conditions': []}, {'mode': '', 'name': 'condColor', 'op': '=', 'expr': 'percentChangePos < trueChange1 ? color.new(color.lime,50) : percentChangeNeg > trueChange2 ? color.new(color.red,50) : na', 'conditions': []}, {'mode': '', 'name': 'buy', 'op': '=', 'expr': 'percentChangePos < trueChange1', 'conditions': []}, {'mode': '', 'name': 'sell', 'op': '=', 'expr': 'percentChangeNeg > trueChange2', 'conditions': []}]
    pine_user_functions = [{'name': 'UpColor', 'args': '', 'body': 'percentChangePos < trueChange1'}, {'name': 'DownColor', 'args': '', 'body': 'percentChangeNeg > trueChange2'}]
    pine_controls = [{'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'else'}, {'indent': 0, 'statement': 'if (buy)'}, {'indent': 0, 'statement': 'if (sell)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("My Long Entry Id", strategy.long)', 'conditions': ['(buy)'], 'statement': 'strategy.entry("My Long Entry Id", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("My Short Entry Id", strategy.short)', 'conditions': ['(sell)'], 'statement': 'strategy.entry("My Short Entry Id", strategy.short)'}]
    original_pine = '/*backtest\nstart: 2023-10-13 00:00:00\nend: 2023-11-12 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// created by Oliver\nstrategy("Percentage Change strategy w/BG color", overlay=true, scale=scale.none, precision=2)\n\nx = input(5, title = \'x candles difference\', minval = 1)\ntrueChange1 = (close - close[x]) / close[x] * 100\npercentChangePos = input(0.4, title="Percent Change")\n\n//if (percentChange > trueChange) then Signal  \n\nplotChar1 = if percentChangePos > trueChange1\n    false\nelse\n    true\n\nplotchar(series=plotChar1, char=\'?\', color=color.green, location=location.top, size = size.tiny )\n\ntrueChange2 = (close - close[x]) / close[x] * 100\npercentChangeNeg = input(-0.4, title="Percent Change")\n\nplotChar2 = if percentChangeNeg < trueChange2\n    false\nelse\n    true\nplotchar(series=plotChar2, char=\'?\', color=color.red, location=location.top, size = size.tiny)\n\n//------------------------------------------------------------------------\nUpColor() => percentChangePos < trueChange1\nDownColor() => percentChangeNeg > trueChange2\n\n//Up = percentChangePos < trueChange1\n//Down = percentChangeNeg > trueChange2\n\n\ncol = percentChangePos < trueChange1 ? color.lime : percentChangeNeg > trueChange2 ? color.red : color.white\n//--------\ncondColor = percentChangePos < trueChange1 ? color.new(color.lime,50) : percentChangeNeg > trueChange2 ? color.new(color.red,50) : na\n//c_lineColor = condUp ? color.new(color.green, 97) : condDn ? color.new(color.maroon, 97) : na\n//barcolor(Up ? color.blue : Down ? color.yellow : color.gray, transp=70)\n\n//Background Highlights\n//bgcolor(condColor, transp=70)\n\n\n//---------\n\nbarcolor(UpColor() ? color.lime: DownColor() ? color.red : na)\nbgcolor(UpColor() ? color.lime: DownColor() ? color.red : na)\n\n//------------------------------------------------------------------------\n\nbuy = percentChangePos < trueChange1\nsell = percentChangeNeg > trueChange2\n\n\n//------------------------------------------------------------------------\n/////////////// Alerts /////////////// \nalertcondition(buy, title=\'buy\', message=\'Buy\')\nalertcondition(sell, title=\'sell\', message=\'Sell\')\n\n//-------------------------------------------------\n\nif (buy)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nif (sell)\n    strategy.entry("My Short Entry Id", strategy.short)\n\n\n/////////////////// Plotting //////////////////////// \nplotshape(buy, title="buy", text="Buy", color=color.green, style=shape.labelup, location=location.belowbar, size=size.small, textcolor=color.white, transp=0)  //plot for buy icon\nplotshape(sell, title="sell", text="Sell", color=color.red, style=shape.labeldown, location=location.abovebar, size=size.small, textcolor=color.white, transp=0)'

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
