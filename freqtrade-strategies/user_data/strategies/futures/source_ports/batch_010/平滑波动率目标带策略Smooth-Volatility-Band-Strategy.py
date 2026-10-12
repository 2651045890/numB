"""Source-faithful deep-assisted port of 平滑波动率目标带策略Smooth-Volatility-Band-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_18e4c353(PinePortBase, IStrategy):
    source_file = '平滑波动率目标带策略Smooth-Volatility-Band-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'src': 'close', 'per': 100, 'mult': 3.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', '=>', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(defval=close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'per', 'op': '=', 'expr': 'input(defval=100, minval=1, title="Sampling Period")', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': 'input(defval=3.0, minval=0.1, title="Range Multiplier")', 'conditions': []}, {'mode': '', 'name': 'wper', 'op': '=', 'expr': '(t * 2) - 1', 'conditions': []}, {'mode': '', 'name': 'avrng', 'op': '=', 'expr': 'ema(abs(x - x[1]), t)', 'conditions': []}, {'mode': '', 'name': 'smoothrng', 'op': '=', 'expr': 'ema(avrng, wper) * m', 'conditions': []}, {'mode': '', 'name': 'smrng', 'op': '=', 'expr': 'smoothrng(src, per, mult)', 'conditions': []}, {'mode': '', 'name': 'rngfilt', 'op': '=', 'expr': 'x', 'conditions': []}, {'mode': '', 'name': 'rngfilt', 'op': ':=', 'expr': 'x > nz(rngfilt[1]) ? ((x - r) < nz(rngfilt[1]) ? nz(rngfilt[1]) : (x - r)) : ((x + r) > nz(rngfilt[1]) ? nz(rngfilt[1]) : (x + r))', 'conditions': []}, {'mode': '', 'name': 'filt', 'op': '=', 'expr': 'rngfilt(src, smrng)', 'conditions': []}, {'mode': '', 'name': 'upward', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'upward', 'op': ':=', 'expr': 'filt > filt[1] ? nz(upward[1]) + 1 : filt < filt[1] ? 0 : nz(upward[1])', 'conditions': []}, {'mode': '', 'name': 'downward', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'downward', 'op': ':=', 'expr': 'filt < filt[1] ? nz(downward[1]) + 1 : filt > filt[1] ? 0 : nz(downward[1])', 'conditions': []}, {'mode': '', 'name': 'hband', 'op': '=', 'expr': 'filt + smrng', 'conditions': []}, {'mode': '', 'name': 'lband', 'op': '=', 'expr': 'filt - smrng', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': '(src > filt) and (src > src[1]) and (upward > 0)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': '(src < filt) and (src < src[1]) and (downward > 0)', 'conditions': []}, {'mode': '', 'name': 'hbandplot', 'op': '=', 'expr': 'plot(hband, color=color.aqua, transp=100, title="High Target")', 'conditions': []}, {'mode': '', 'name': 'lbandplot', 'op': '=', 'expr': 'plot(lband, color=color.fuchsia, transp=100, title="Low Target")', 'conditions': []}]
    pine_user_functions = [{'name': 'smoothrng', 'args': 'x, t, m', 'body': ''}, {'name': 'rngfilt', 'args': 'x, r', 'body': ''}]
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = longCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = longCondition)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, when = shortCondition)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, when = shortCondition)'}]
    original_pine = '/*backtest\nstart: 2023-01-22 00:00:00\nend: 2024-01-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("1SmSm1 Strategy", shorttitle="1SmSm1", overlay=true)\n\n// Source\nsrc = input(defval=close, title="Source")\n\n// Sampling Period\nper = input(defval=100, minval=1, title="Sampling Period")\n\n// Range Multiplier\nmult = input(defval=3.0, minval=0.1, title="Range Multiplier")\n\n// Smooth Average Range\nsmoothrng(x, t, m) =>\n    wper = (t * 2) - 1\n    avrng = ema(abs(x - x[1]), t)\n    smoothrng = ema(avrng, wper) * m\n    smoothrng\n\nsmrng = smoothrng(src, per, mult)\n\n// Range Filter\nrngfilt(x, r) =>\n    rngfilt = x\n    rngfilt := x > nz(rngfilt[1]) ? ((x - r) < nz(rngfilt[1]) ? nz(rngfilt[1]) : (x - r)) : ((x + r) > nz(rngfilt[1]) ? nz(rngfilt[1]) : (x + r))\n    rngfilt\n\nfilt = rngfilt(src, smrng)\n\n// Filter Direction\nupward = 0.0\nupward := filt > filt[1] ? nz(upward[1]) + 1 : filt < filt[1] ? 0 : nz(upward[1])\n\ndownward = 0.0\ndownward := filt < filt[1] ? nz(downward[1]) + 1 : filt > filt[1] ? 0 : nz(downward[1])\n\n// Target Bands\nhband = filt + smrng\nlband = filt - smrng\n\n// Breakouts\nlongCondition = (src > filt) and (src > src[1]) and (upward > 0)\nshortCondition = (src < filt) and (src < src[1]) and (downward > 0)\n\nstrategy.entry("Buy", strategy.long, when = longCondition)\nstrategy.entry("Sell", strategy.short, when = shortCondition)\n\n// Plotting\nplot(filt, color=upward > 0 ? color.lime : downward > 0 ? color.red : color.orange, linewidth=3, title="Range Filter")\nhbandplot = plot(hband, color=color.aqua, transp=100, title="High Target")\nlbandplot = plot(lband, color=color.fuchsia, transp=100, title="Low Target")\n\n// Fills\nfill(hbandplot, lbandplot, color=color.aqua, title="Target Range")\n\n// Bar Color\nbarcolor(longCondition ? color.green : shortCondition ? color.red : na)\n\n// Alerts\nalertcondition(longCondition, title="Buy Alert", message="BUY")\nalertcondition(shortCondition, title="Sell Alert", message="SELL")'

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
