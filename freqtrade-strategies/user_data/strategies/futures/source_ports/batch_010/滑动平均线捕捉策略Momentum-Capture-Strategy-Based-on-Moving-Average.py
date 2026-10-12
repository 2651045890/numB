"""Source-faithful deep-assisted port of 滑动平均线捕捉策略Momentum-Capture-Strategy-Based-on-Moving-Average.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7192d20c(PinePortBase, IStrategy):
    source_file = '滑动平均线捕捉策略Momentum-Capture-Strategy-Based-on-Moving-Average.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'res1': 'D', 'test': 0, 'sloma': 20, 'Length': 5, 'xPrice': 'hlc3', 'Fastend': 2.5, 'Slowend': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1000.0
    source_pyramiding = 0
    source_initial_capital = 100000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'timeframe.']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.']
    pine_assignments = [{'mode': '', 'name': 'res1', 'op': '=', 'expr': "input.timeframe(title='Heikin Ashi EMA Time Frame', defval='D')", 'conditions': []}, {'mode': '', 'name': 'test', 'op': '=', 'expr': "input(0, 'Heikin Ashi EMA Shift')", 'conditions': []}, {'mode': '', 'name': 'sloma', 'op': '=', 'expr': "input(20, 'Slow EMA Period')", 'conditions': []}, {'mode': '', 'name': 'nAMA', 'op': '=', 'expr': 'hlc3', 'conditions': []}, {'mode': '', 'name': 'Length', 'op': '=', 'expr': 'input.int(5, minval=1)', 'conditions': []}, {'mode': '', 'name': 'xPrice', 'op': '=', 'expr': 'input(hlc3)', 'conditions': []}, {'mode': '', 'name': 'xvnoise', 'op': '=', 'expr': 'math.abs(xPrice - xPrice[1])', 'conditions': []}, {'mode': '', 'name': 'Fastend', 'op': '=', 'expr': 'input.float(2.5, step=.5)', 'conditions': []}, {'mode': '', 'name': 'Slowend', 'op': '=', 'expr': 'input(20)', 'conditions': []}, {'mode': '', 'name': 'nfastend', 'op': '=', 'expr': '2 / (Fastend + 1)', 'conditions': []}, {'mode': '', 'name': 'nslowend', 'op': '=', 'expr': '2 / (Slowend + 1)', 'conditions': []}, {'mode': '', 'name': 'nsignal', 'op': '=', 'expr': 'math.abs(xPrice - xPrice[Length])', 'conditions': []}, {'mode': '', 'name': 'nnoise', 'op': '=', 'expr': 'math.sum(xvnoise, Length)', 'conditions': []}, {'mode': '', 'name': 'nefratio', 'op': '=', 'expr': 'nnoise != 0 ? nsignal / nnoise : 0', 'conditions': []}, {'mode': '', 'name': 'nsmooth', 'op': '=', 'expr': 'math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)', 'conditions': []}, {'mode': '', 'name': 'nAMAn', 'op': '=', 'expr': 'nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))', 'conditions': []}, {'mode': '', 'name': 'ha_t', 'op': '=', 'expr': 'ticker.heikinashi(syminfo.tickerid)', 'conditions': []}, {'mode': '', 'name': 'ha_close', 'op': '=', 'expr': 'request.security(ha_t, timeframe.period, nAMAn)', 'conditions': []}, {'mode': '', 'name': 'mha_close', 'op': '=', 'expr': 'request.security(ha_t, res1, hlc3)', 'conditions': []}, {'mode': '', 'name': 'fma', 'op': '=', 'expr': 'ta.ema(mha_close[test], 1)', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'ta.ema(ha_close, sloma)', 'conditions': []}, {'mode': '', 'name': 'golong', 'op': '=', 'expr': 'ta.crossover(fma, sma)', 'conditions': []}, {'mode': '', 'name': 'goshort', 'op': '=', 'expr': 'ta.crossunder(fma, sma)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Buy', strategy.long, when=golong)", 'conditions': [], 'statement': "strategy.entry('Buy', strategy.long, when=golong)"}, {'kind': 'entry', 'call': "strategy.entry('Sell', strategy.short,when=goshort)", 'conditions': [], 'statement': "strategy.entry('Sell', strategy.short,when=goshort)"}]
    original_pine = '/*backtest\nstart: 2022-10-25 00:00:00\nend: 2023-10-31 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n//Heikin/Kaufman by Gustavo v5\n// strategy(\'Heikin Ashi EMA v5 no repaint \', shorttitle=\'Heikin Ashi EMA v5 no repaint\', overlay=true, max_bars_back=500, default_qty_value=1000, initial_capital=100000, currency=currency.EUR)\n\n\n// Settings - H/K\nres1 = input.timeframe(title=\'Heikin Ashi EMA Time Frame\', defval=\'D\')\ntest = input(0, \'Heikin Ashi EMA Shift\')\nsloma = input(20, \'Slow EMA Period\')\nnAMA = hlc3\n\n//Kaufman MA\nLength = input.int(5, minval=1)\nxPrice = input(hlc3)\nxvnoise = math.abs(xPrice - xPrice[1])\nFastend = input.float(2.5, step=.5)\nSlowend = input(20)\nnfastend = 2 / (Fastend + 1)\nnslowend = 2 / (Slowend + 1)\nnsignal = math.abs(xPrice - xPrice[Length])\nnnoise = math.sum(xvnoise, Length)\nnefratio = nnoise != 0 ? nsignal / nnoise : 0\nnsmooth = math.pow(nefratio * (nfastend - nslowend) + nslowend, 2)\nnAMAn = nz(nAMA[1]) + nsmooth * (xPrice - nz(nAMA[1]))\n\n//Heikin Ashi Open/Close Price\nha_t = ticker.heikinashi(syminfo.tickerid)\nha_close = request.security(ha_t, timeframe.period, nAMAn)\nmha_close = request.security(ha_t, res1, hlc3)\n\n//Moving Average\nfma = ta.ema(mha_close[test], 1)\nsma = ta.ema(ha_close, sloma)\nplot(fma, title=\'MA\', color=color.new(color.black, 0), linewidth=2, style=plot.style_line)\nplot(sma, title=\'SMA\', color=color.new(color.red, 0), linewidth=2, style=plot.style_line)\n\n//Strategy\ngolong = ta.crossover(fma, sma)\ngoshort = ta.crossunder(fma, sma)\n\nstrategy.entry(\'Buy\', strategy.long, when=golong)\nstrategy.entry(\'Sell\', strategy.short,when=goshort)'

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
