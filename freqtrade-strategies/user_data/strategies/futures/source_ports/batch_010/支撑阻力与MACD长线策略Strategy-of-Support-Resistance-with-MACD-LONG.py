"""Source-faithful deep-assisted port of 支撑阻力与MACD长线策略Strategy-of-Support-Resistance-with-MACD-LONG.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_64f3c28c(PinePortBase, IStrategy):
    source_file = '支撑阻力与MACD长线策略Strategy-of-Support-Resistance-with-MACD-LONG.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'supportLevel': 100, 'resistanceLevel': 100, 'stopLossLevel': 5, 'takeProfitLevel': 7.5}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'var ', 'barstate.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'supportLevel', 'op': '=', 'expr': 'input(100, title="Support Level Strength", minval=1)', 'conditions': []}, {'mode': '', 'name': 'resistanceLevel', 'op': '=', 'expr': 'input(100, title="Resistance Level Strength", minval=1)', 'conditions': []}, {'mode': 'var', 'name': 'supportPrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': 'var', 'name': 'resistancePrice', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'supportPrice', 'op': ':=', 'expr': 'low', 'conditions': ['low <= supportPrice or barstate.islast']}, {'mode': '', 'name': 'resistancePrice', 'op': ':=', 'expr': 'high', 'conditions': ['high >= resistancePrice or barstate.islast']}, {'mode': '', 'name': 'macdHistogram', 'op': '=', 'expr': 'macdLine - signalLine', 'conditions': []}, {'mode': '', 'name': 'bullishSetup', 'op': '=', 'expr': 'crossover(macdLine, signalLine) and macdHistogram > 0 and close > supportPrice', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'input(5, title="Stop Loss Level (%)", minval=0.1, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'takeProfitLevel', 'op': '=', 'expr': 'input(7.5, title="Take Profit Level (%)", minval=0.1, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'stopLossPrice', 'op': '=', 'expr': 'close * (1 - stopLossLevel / 100)', 'conditions': ['bullishSetup']}, {'mode': '', 'name': 'takeProfitPrice', 'op': '=', 'expr': 'close * (1 + takeProfitLevel / 100)', 'conditions': ['bullishSetup']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if low <= supportPrice or barstate.islast'}, {'indent': 0, 'statement': 'if high >= resistancePrice or barstate.islast'}, {'indent': 0, 'statement': 'if bullishSetup'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['bullishSetup'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit", "Long", stop=stopLossPrice, limit=takeProfitPrice)', 'conditions': ['bullishSetup'], 'statement': 'strategy.exit("Exit", "Long", stop=stopLossPrice, limit=takeProfitPrice)'}]
    original_pine = '/*backtest\nstart: 2022-10-23 00:00:00\nend: 2023-10-29 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Price Action - Support & Resistance + MACD Strategy", overlay=true)\n\n// Price Action - Support & Resistance\nsupportLevel = input(100, title="Support Level Strength", minval=1)\nresistanceLevel = input(100, title="Resistance Level Strength", minval=1)\n\nvar supportPrice = 0.0\nvar resistancePrice = 0.0\n\nif low <= supportPrice or barstate.islast\n    supportPrice := low\nif high >= resistancePrice or barstate.islast\n    resistancePrice := high\n\nplot(supportPrice, color=color.green, linewidth=1, title="Support")\nplot(resistancePrice, color=color.red, linewidth=1, title="Resistance")\n\n// MACD Indicator\n[macdLine, signalLine, _] = macd(close, 26, 100, 9)\nmacdHistogram = macdLine - signalLine\n\n// Bullish Trade Setup\nbullishSetup = crossover(macdLine, signalLine) and macdHistogram > 0 and close > supportPrice\nplotshape(bullishSetup, color=color.green, title="Bullish Setup", style=shape.triangleup, location=location.belowbar)\n\n// Stop Loss and Take Profit Levels\nstopLossLevel = input(5, title="Stop Loss Level (%)", minval=0.1, step=0.1)\ntakeProfitLevel = input(7.5, title="Take Profit Level (%)", minval=0.1, step=0.1)\n\n// Execute Long Trades\nif bullishSetup\n    stopLossPrice = close * (1 - stopLossLevel / 100)\n    takeProfitPrice = close * (1 + takeProfitLevel / 100)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit", "Long", stop=stopLossPrice, limit=takeProfitPrice)'

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
