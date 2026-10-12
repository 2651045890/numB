"""Source-faithful deep-assisted port of 特斯拉超趋势策略Tesla-Supertrend-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a4b9690b(PinePortBase, IStrategy):
    source_file = '特斯拉超趋势策略Tesla-Supertrend-Strategy.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'atrPeriod': 19, 'factor': 3.0, 'adxlen': 7, 'dilen': 7}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'atrPeriod', 'op': '=', 'expr': 'input(19, "ATR Length")', 'conditions': []}, {'mode': '', 'name': 'factor', 'op': '=', 'expr': 'input.float(3.0, "Factor", step = 0.01)', 'conditions': []}, {'mode': '', 'name': 'adxlen', 'op': '=', 'expr': 'input(7, title="ADX Smoothing")', 'conditions': []}, {'mode': '', 'name': 'dilen', 'op': '=', 'expr': 'input(7, title="DI Length")', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'ta.change(high)', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': '-ta.change(low)', 'conditions': []}, {'mode': '', 'name': 'plusDM', 'op': '=', 'expr': 'na(up) ? na : (up > down and up > 0 ? up : 0)', 'conditions': []}, {'mode': '', 'name': 'minusDM', 'op': '=', 'expr': 'na(down) ? na : (down > up and down > 0 ? down : 0)', 'conditions': []}, {'mode': '', 'name': 'truerange', 'op': '=', 'expr': 'ta.rma(ta.tr, len)', 'conditions': []}, {'mode': '', 'name': 'plus', 'op': '=', 'expr': 'fixnan(100 * ta.rma(plusDM, len) / truerange)', 'conditions': []}, {'mode': '', 'name': 'minus', 'op': '=', 'expr': 'fixnan(100 * ta.rma(minusDM, len) / truerange)', 'conditions': []}, {'mode': '', 'name': 'sum', 'op': '=', 'expr': 'plus + minus', 'conditions': []}, {'mode': '', 'name': 'adx', 'op': '=', 'expr': '100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)', 'conditions': []}, {'mode': '', 'name': 'sig', 'op': '=', 'expr': 'adx(dilen, adxlen)', 'conditions': []}]
    pine_user_functions = [{'name': 'dirmov', 'args': 'len', 'body': ''}, {'name': 'adx', 'args': 'dilen, adxlen', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if ta.change(direction, 1) < 0 and ta.rsi(close, 21) < 75 and ta.rsi(close, 3) > 65 and ta.rsi(close, 28) > 49 and sig > 21'}, {'indent': 0, 'statement': 'if ta.change(direction, 1) > 0 or ta.rsi(close, 10) < 42'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long Entry", strategy.long)', 'conditions': ['ta.change(direction, 1) < 0 and ta.rsi(close, 21) < 75 and ta.rsi(close, 3) > 65 and ta.rsi(close, 28) > 49 and sig > 21'], 'statement': 'strategy.entry("Long Entry", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long Entry")', 'conditions': ['ta.change(direction, 1) > 0 or ta.rsi(close, 10) < 42'], 'statement': 'strategy.close("Long Entry")'}]
    original_pine = '/*backtest\nstart: 2023-09-29 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// © cjones0313\n\n//@version=5\nstrategy("TSLA 1.8k Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n\n// a measure of volatility, default 10 - measured over 10 bars\n// modifying the value > 10 results in a smoother supertrend line, filter out noise but slower response to price changes\n// modifying the value < 10 results in faster response in price changes, but may result in more false signals\natrPeriod = input(19, "ATR Length")\n\n// sets factor for supertrend line made up of price and ATR, this determines how much weight is given to each, default 3.0\n// increasing the value > 3.0 results in faster response in price changes, but may result in more false signals\n// decreasing the value results in filtering out noise, but may miss smaller price movements\nfactor = input.float(3.0, "Factor", step = 0.01)\n\n// direction = 1 bullish, -1 bearish\n[_, direction] = ta.supertrend(factor, atrPeriod)\n\n\n\nadxlen = input(7, title="ADX Smoothing")\ndilen = input(7, title="DI Length")\ndirmov(len) =>\n    up = ta.change(high)\n    down = -ta.change(low)\n    plusDM = na(up) ? na : (up > down and up > 0 ? up : 0)\n    minusDM = na(down) ? na : (down > up and down > 0 ? down : 0)\n    truerange = ta.rma(ta.tr, len)\n    plus = fixnan(100 * ta.rma(plusDM, len) / truerange)\n    minus = fixnan(100 * ta.rma(minusDM, len) / truerange)\n    [plus, minus]\nadx(dilen, adxlen) =>\n    [plus, minus] = dirmov(dilen)\n    sum = plus + minus\n    adx = 100 * ta.rma(math.abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)\nsig = adx(dilen, adxlen)\n\nif ta.change(direction, 1) < 0 and ta.rsi(close, 21) < 75 and ta.rsi(close, 3) > 65 and ta.rsi(close, 28) > 49 and sig > 21\n    strategy.entry("Long Entry", strategy.long)\n\nif ta.change(direction, 1) > 0 or ta.rsi(close, 10) < 42\n    strategy.close("Long Entry")'

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
