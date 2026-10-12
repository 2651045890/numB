"""Source-faithful deep-assisted port of 最高最低中心回看策略Highest-Lowest-Center-Lookback-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_9e7d1c49(PinePortBase, IStrategy):
    source_file = '最高最低中心回看策略Highest-Lowest-Center-Lookback-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'lookback_length': 200, 'smoother_length': 5, 'atr_length': 10, 'atr_multiplier': 1.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'lookback_length', 'op': '=', 'expr': 'input(200, type=input.integer, minval=1, title="Lookback Length")', 'conditions': []}, {'mode': '', 'name': 'smoother_length', 'op': '=', 'expr': 'input(5, type=input.integer, minval=1, title="Smoother Length")', 'conditions': []}, {'mode': '', 'name': 'atr_length', 'op': '=', 'expr': 'input(10, type=input.integer, minval=1, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atr_multiplier', 'op': '=', 'expr': 'input(1.5, type=input.float, minval=0.5, title="ATR Multiplier")', 'conditions': []}, {'mode': '', 'name': 'vola', 'op': '=', 'expr': 'atr(atr_length) * atr_multiplier', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'sma(close, 3)', 'conditions': []}, {'mode': '', 'name': 'l', 'op': '=', 'expr': 'ema(lowest(low, lookback_length), smoother_length)', 'conditions': []}, {'mode': '', 'name': 'h', 'op': '=', 'expr': 'ema(highest(high, lookback_length), smoother_length)', 'conditions': []}, {'mode': '', 'name': 'center', 'op': '=', 'expr': '(h + l) * 0.5', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'center + vola', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'center - vola', 'conditions': []}, {'mode': '', 'name': 'trend', 'op': '=', 'expr': 'price > upper ? true : (price < lower ? false : na)', 'conditions': []}, {'mode': '', 'name': 'bull_cross', 'op': '=', 'expr': 'crossover(price, upper)', 'conditions': []}, {'mode': '', 'name': 'bear_cross', 'op': '=', 'expr': 'crossunder(price, lower)', 'conditions': []}, {'mode': '', 'name': 'pc', 'op': '=', 'expr': 'plot(center, title="Center", color=color.black, transp=25, linewidth=2)', 'conditions': []}, {'mode': '', 'name': 'pu', 'op': '=', 'expr': 'plot(upper, title="Upper", color=color.green, transp=75, linewidth=2)', 'conditions': []}, {'mode': '', 'name': 'pl', 'op': '=', 'expr': 'plot(lower, title="Lower", color=color.red, transp=75, linewidth=2)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=bull_cross)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=bull_cross)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when=bear_cross)', 'conditions': [], 'statement': 'strategy.close("Buy", when=bear_cross)'}]
    original_pine = '/*backtest\nstart: 2023-11-27 00:00:00\nend: 2023-12-27 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Highest/Lowest Center Lookback Strategy", overlay=true)\n\nlookback_length = input(200, type=input.integer, minval=1, title="Lookback Length")\nsmoother_length = input(5, type=input.integer, minval=1, title="Smoother Length")\natr_length = input(10, type=input.integer, minval=1, title="ATR Length")\natr_multiplier = input(1.5, type=input.float, minval=0.5, title="ATR Multiplier")\n\nvola = atr(atr_length) * atr_multiplier\nprice = sma(close, 3)\n\nl = ema(lowest(low, lookback_length), smoother_length)\nh = ema(highest(high, lookback_length), smoother_length)\ncenter = (h + l) * 0.5\nupper = center + vola\nlower = center - vola\ntrend = price > upper ? true : (price < lower ? false : na)\n\nbull_cross = crossover(price, upper)\nbear_cross = crossunder(price, lower)\n\nstrategy.entry("Buy", strategy.long, when=bull_cross)\nstrategy.close("Buy", when=bear_cross)\n\nplot(h, title="High", color=color.red, transp=75, linewidth=2)\nplot(l, title="Low", color=color.green, transp=75, linewidth=2)\n\npc = plot(center, title="Center", color=color.black, transp=25, linewidth=2)\npu = plot(upper, title="Upper", color=color.green, transp=75, linewidth=2)\npl = plot(lower, title="Lower", color=color.red, transp=75, linewidth=2)\n\nfill(pu, pc, color=color.green, transp=85)\nfill(pl, pc, color=color.red, transp=85)\n\nbgcolor(trend == true ? color.green : (trend == false ? color.red : color.gray), transp=85)'

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
