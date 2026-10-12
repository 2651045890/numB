"""Source-faithful deep-assisted port of 月度抛物线突破策略Monthly-Parabolic-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7fc423d5(PinePortBase, IStrategy):
    source_file = '月度抛物线突破策略Monthly-Parabolic-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'rsiPeriod', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'delta', 'op': '=', 'expr': 'close - close[1]', 'conditions': []}, {'mode': '', 'name': 'gain', 'op': '=', 'expr': 'iff(delta > 0, delta, 0)', 'conditions': []}, {'mode': '', 'name': 'loss', 'op': '=', 'expr': 'iff(delta < 0, -delta, 0)', 'conditions': []}, {'mode': '', 'name': 'avgGain', 'op': '=', 'expr': 'sma(gain, rsiPeriod)', 'conditions': []}, {'mode': '', 'name': 'avgLoss', 'op': '=', 'expr': 'sma(loss, rsiPeriod)', 'conditions': []}, {'mode': '', 'name': 'rs', 'op': '=', 'expr': 'avgGain / avgLoss', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': '100 - (100 / (1 + rs))', 'conditions': []}, {'mode': '', 'name': 'emaShort1', 'op': '=', 'expr': 'ema(close, 4)', 'conditions': []}, {'mode': '', 'name': 'emaLong1', 'op': '=', 'expr': 'ema(close, 9)', 'conditions': []}, {'mode': '', 'name': 'macd1', 'op': '=', 'expr': 'emaShort1 - emaLong1', 'conditions': []}, {'mode': '', 'name': 'emaShort2', 'op': '=', 'expr': 'ema(close, 12)', 'conditions': []}, {'mode': '', 'name': 'emaLong2', 'op': '=', 'expr': 'ema(close, 26)', 'conditions': []}, {'mode': '', 'name': 'macd2', 'op': '=', 'expr': 'emaShort2 - emaLong2', 'conditions': []}, {'mode': '', 'name': 'highestRsi', 'op': '=', 'expr': 'highest(rsiValue, 36)', 'conditions': []}, {'mode': '', 'name': 'highestMacd1', 'op': '=', 'expr': 'highest(macd1, 36)', 'conditions': []}, {'mode': '', 'name': 'highestMacd2', 'op': '=', 'expr': 'highest(macd2, 36)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': '(rsiValue >= highestRsi) and (macd1 >= highestMacd1 or macd2 >= highestMacd2)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (buyCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(buyCondition)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell", "Buy", bar_index[30])', 'conditions': [], 'statement': 'strategy.exit("Sell", "Buy", bar_index[30])'}]
    original_pine = '/*backtest\nstart: 2022-11-24 00:00:00\nend: 2023-11-30 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Stringent Strategy for Backtesting", overlay=true)\n\n// Initialize RSI variables\nrsiPeriod = 14\n\n// Manually calculate RSI\ndelta = close - close[1]\ngain = iff(delta > 0, delta, 0)\nloss = iff(delta < 0, -delta, 0)\n\navgGain = sma(gain, rsiPeriod)\navgLoss = sma(loss, rsiPeriod)\n\nrs = avgGain / avgLoss\nrsiValue = 100 - (100 / (1 + rs))\n\n// Manually calculate MACD1 and MACD2\nemaShort1 = ema(close, 4)\nemaLong1 = ema(close, 9)\nmacd1 = emaShort1 - emaLong1\n\nemaShort2 = ema(close, 12)\nemaLong2 = ema(close, 26)\nmacd2 = emaShort2 - emaLong2\n\n// Find the highest values in the last 3 years (36 months)\nhighestRsi = highest(rsiValue, 36)\nhighestMacd1 = highest(macd1, 36)\nhighestMacd2 = highest(macd2, 36)\n\n// Define buy signal conditions\nbuyCondition = (rsiValue >= highestRsi) and (macd1 >= highestMacd1 or macd2 >= highestMacd2)\n\n// Plot the buy signal on the chart\nplotshape(series=buyCondition, title="Buy Signal", location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\n\n// Backtesting: Entry and Exit\nif (buyCondition)\n    strategy.entry("Buy", strategy.long)\n\n// Exit condition (Example: Exit after 30 bars)\nstrategy.exit("Sell", "Buy", bar_index[30])'

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
