"""Source-faithful deep-assisted port of 日线高低点结合多时框EMA趋势量化交易策略-Multi-Timeframe-EMA-Trend-Strategy-with-Daily-High-Low-Breakout-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2290f057(PinePortBase, IStrategy):
    source_file = '日线高低点结合多时框EMA趋势量化交易策略-Multi-Timeframe-EMA-Trend-Strategy-with-Daily-High-Low-Breakout-System.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'len': 24, 'src': 'close', 'length': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_commission_percent = 0.1
    source_features = ['request.security', 'strategy.entry', 'strategy.close', '=>', 'barstate.']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses barmerge.lookahead_on; source can intentionally expose/repaint future HTF values. Preserve when parity-testing, disable for live-safe testing only as a separate variant.']
    pine_assignments = [{'mode': '', 'name': 'len', 'op': '=', 'expr': "input.int(24, minval=1, title='Length MA', group='Optimization parameters')", 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': "input.source(close, title='Source MA', group='Optimization parameters')", 'conditions': []}, {'mode': '', 'name': 'out', 'op': '=', 'expr': 'ta.ema(src, len)', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': "input.int(20, minval=1, title='CMF Length', group='Optimization parameters')", 'conditions': []}, {'mode': '', 'name': 'ad', 'op': '=', 'expr': 'close == high and close == low or high == low ? 0 : (2 * close - low - high) / (high - low) * volume', 'conditions': []}, {'mode': '', 'name': 'mf', 'op': '=', 'expr': 'math.sum(ad, length) / math.sum(volume, length)', 'conditions': []}, {'mode': '', 'name': 'pricehigh', 'op': '=', 'expr': "f_secureSecurity(syminfo.tickerid, 'D', high)", 'conditions': []}, {'mode': '', 'name': 'pricelow', 'op': '=', 'expr': "f_secureSecurity(syminfo.tickerid, 'D', low)", 'conditions': []}, {'mode': '', 'name': 'short', 'op': '=', 'expr': 'ta.crossunder(low, pricelow) and close < out and mf < 0', 'conditions': []}, {'mode': '', 'name': 'long', 'op': '=', 'expr': 'ta.crossover(high, pricehigh) and close > out and mf > 0', 'conditions': []}, {'mode': '', 'name': 'ema_200', 'op': '=', 'expr': 'ta.ema(close, 200)', 'conditions': []}, {'mode': '', 'name': 'ema_200_1h', 'op': '=', 'expr': 'request.security(syminfo.tickerid, "60", ta.ema(close, 200))', 'conditions': []}]
    pine_user_functions = [{'name': 'f_secureSecurity', 'args': '_symbol, _res, _src', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if short and barstate.isconfirmed'}, {'indent': 0, 'statement': 'if long and barstate.isconfirmed'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('short', strategy.short, stop=pricelow[1])", 'conditions': ['short and barstate.isconfirmed'], 'statement': "strategy.entry('short', strategy.short, stop=pricelow[1])"}, {'kind': 'close', 'call': "strategy.close('short', when=close > out)", 'conditions': ['short and barstate.isconfirmed'], 'statement': "strategy.close('short', when=close > out)"}, {'kind': 'entry', 'call': "strategy.entry('long', strategy.long, stop=pricehigh[1])", 'conditions': ['long and barstate.isconfirmed'], 'statement': "strategy.entry('long', strategy.long, stop=pricehigh[1])"}, {'kind': 'close', 'call': "strategy.close('long', when=close < out)", 'conditions': ['long and barstate.isconfirmed'], 'statement': "strategy.close('long', when=close < out)"}]
    original_pine = '/*backtest\nstart: 2024-10-28 00:00:00\nend: 2024-11-27 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title=\'The security Daily HIGH/LOW strategy\', overlay=true, initial_capital=10000, calc_on_every_tick=true, \n         default_qty_type=strategy.percent_of_equity, default_qty_value=100, \n         commission_type=strategy.commission.percent, commission_value=0.1)\n\n// General Inputs\nlen = input.int(24, minval=1, title=\'Length MA\', group=\'Optimization parameters\')\nsrc = input.source(close, title=\'Source MA\', group=\'Optimization parameters\')\nout = ta.ema(src, len)\n\nlength = input.int(20, minval=1, title=\'CMF Length\', group=\'Optimization parameters\')\nad = close == high and close == low or high == low ? 0 : (2 * close - low - high) / (high - low) * volume\nmf = math.sum(ad, length) / math.sum(volume, length)\n\n// Function to get daily high and low\nf_secureSecurity(_symbol, _res, _src) =>\n    request.security(_symbol, _res, _src[1], lookahead=barmerge.lookahead_on)\n\npricehigh = f_secureSecurity(syminfo.tickerid, \'D\', high)\npricelow = f_secureSecurity(syminfo.tickerid, \'D\', low)\n\n// Plotting previous daily high and low\nplot(pricehigh, title=\'Previous Daily High\', style=plot.style_linebr, linewidth=2, color=color.new(color.white, 0))\nplot(pricelow, title=\'Previous Daily Low\', style=plot.style_linebr, linewidth=2, color=color.new(color.white, 0))\n\n// Entry Conditions\nshort = ta.crossunder(low, pricelow) and close < out and mf < 0\nlong = ta.crossover(high, pricehigh) and close > out and mf > 0\n\nif short and barstate.isconfirmed\n    strategy.entry(\'short\', strategy.short, stop=pricelow[1])\n    strategy.close(\'short\', when=close > out)\n\nif long and barstate.isconfirmed\n    strategy.entry(\'long\', strategy.long, stop=pricehigh[1])\n    strategy.close(\'long\', when=close < out)\n\n// 200 EMA on 1-hour timeframe\nema_200 = ta.ema(close, 200)\nema_200_1h = request.security(syminfo.tickerid, "60", ta.ema(close, 200))\n\nplot(ema_200_1h, color=color.purple, title="200 EMA (1H)")\nplot(ema_200, color=color.white, title="200 EMA")'

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
