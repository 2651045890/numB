"""Source-faithful deep-assisted port of 平滑型Heikin-Ashi结合SMA交叉趋势跟踪策略-Smoothed-Heikin-Ashi-with-SMA-Crossover-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_1de75cd6(PinePortBase, IStrategy):
    source_file = '平滑型Heikin-Ashi结合SMA交叉趋势跟踪策略-Smoothed-Heikin-Ashi-with-SMA-Crossover-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'s1': 11, 's2': 44, 'noPositionThreshold': 0.001, 'smoothLength': 6}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'var ', 'for ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 's1', 'op': '=', 'expr': 'input.int(11, title="Short SMA Period")', 'conditions': []}, {'mode': '', 'name': 's2', 'op': '=', 'expr': 'input.int(44, title="Long SMA Period")', 'conditions': []}, {'mode': '', 'name': 'noPositionThreshold', 'op': '=', 'expr': 'input.float(0.001, title="No Position Threshold", step=0.0001)', 'conditions': []}, {'mode': '', 'name': 'haClose', 'op': '=', 'expr': '(open + high + low + close) / 4', 'conditions': []}, {'mode': 'var', 'name': 'haOpen', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'haOpen', 'op': ':=', 'expr': 'na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2', 'conditions': []}, {'mode': '', 'name': 'haHigh', 'op': '=', 'expr': 'math.max(high, math.max(haOpen, haClose))', 'conditions': []}, {'mode': '', 'name': 'haLow', 'op': '=', 'expr': 'math.min(low, math.min(haOpen, haClose))', 'conditions': []}, {'mode': '', 'name': 'smoothLength', 'op': '=', 'expr': 'input.int(6, title="Smoothing Length")', 'conditions': []}, {'mode': '', 'name': 'smoothedHaClose', 'op': '=', 'expr': 'ta.ema(haClose, smoothLength)', 'conditions': []}, {'mode': '', 'name': 'smoothedHaOpen', 'op': '=', 'expr': 'ta.ema(haOpen, smoothLength)', 'conditions': []}, {'mode': '', 'name': 'smoothedHaHigh', 'op': '=', 'expr': 'ta.ema(haHigh, smoothLength)', 'conditions': []}, {'mode': '', 'name': 'smoothedHaLow', 'op': '=', 'expr': 'ta.ema(haLow, smoothLength)', 'conditions': []}, {'mode': '', 'name': 'smaShort', 'op': '=', 'expr': 'ta.sma(close, s1)', 'conditions': []}, {'mode': '', 'name': 'smaLong', 'op': '=', 'expr': 'ta.sma(close, s2)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'ta.crossover(smoothedHaClose, smaLong)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'ta.crossunder(smoothedHaClose, smaLong)', 'conditions': []}, {'mode': '', 'name': 'noPositionCondition', 'op': '=', 'expr': 'math.abs(smoothedHaClose - smaLong) < noPositionThreshold', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}, {'indent': 0, 'statement': 'if (noPositionCondition and strategy.position_size != 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close_all', 'call': 'strategy.close_all("No Position")', 'conditions': ['(noPositionCondition and strategy.position_size != 0)'], 'statement': 'strategy.close_all("No Position")'}]
    original_pine = '/*backtest\nstart: 2024-10-01 00:00:00\nend: 2024-10-31 23:59:59\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Smoothed Heikin Ashi with SMA Strategy", overlay=true)\n\n// Input parameters for SMAs\ns1 = input.int(11, title="Short SMA Period")\ns2 = input.int(44, title="Long SMA Period")\nnoPositionThreshold = input.float(0.001, title="No Position Threshold", step=0.0001)\n\n// Calculate the original Heikin-Ashi values\nhaClose = (open + high + low + close) / 4\nvar float haOpen = na\nhaOpen := na(haOpen[1]) ? (open + close) / 2 : (haOpen[1] + haClose[1]) / 2\nhaHigh = math.max(high, math.max(haOpen, haClose))\nhaLow = math.min(low, math.min(haOpen, haClose))\n\n// Smoothing using exponential moving averages\nsmoothLength = input.int(6, title="Smoothing Length")\nsmoothedHaClose = ta.ema(haClose, smoothLength)\nsmoothedHaOpen = ta.ema(haOpen, smoothLength)\nsmoothedHaHigh = ta.ema(haHigh, smoothLength)\nsmoothedHaLow = ta.ema(haLow, smoothLength)\n\n// Calculate SMAs\nsmaShort = ta.sma(close, s1)\nsmaLong = ta.sma(close, s2)\n\n// Plotting the smoothed Heikin-Ashi values\nplotcandle(smoothedHaOpen, smoothedHaHigh, smoothedHaLow, smoothedHaClose, color=(smoothedHaClose >= smoothedHaOpen ? color.green : color.red), title="Smoothed Heikin Ashi")\nplot(smaShort, color=color.blue, title="SMA Short")\nplot(smaLong, color=color.red, title="SMA Long")\n\n// Generate buy/sell signals based on SHA crossing 44 SMA\nlongCondition = ta.crossover(smoothedHaClose, smaLong)\nshortCondition = ta.crossunder(smoothedHaClose, smaLong)\nnoPositionCondition = math.abs(smoothedHaClose - smaLong) < noPositionThreshold\n\n// Strategy logic\nif (longCondition)\n    strategy.entry("Long", strategy.long)\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\nif (noPositionCondition and strategy.position_size != 0)\n    strategy.close_all("No Position")\n\n// Plot buy/sell signals\nplotshape(series=longCondition, location=location.belowbar, color=color.green, style=shape.labelup, text="BUY", size=size.small)\nplotshape(series=shortCondition, location=location.abovebar, color=color.red, style=shape.labeldown, text="SELL", size=size.small)\nplotshape(series=noPositionCondition and strategy.position_size != 0, location=location.belowbar, color=color.yellow, style=shape.labeldown, text="EXIT", size=size.small)'

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
