"""Source-faithful deep-assisted port of 成交量加权平均价与相对强弱指数交叉策略-VWAP-and-RSI-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_72ecb790(PinePortBase, IStrategy):
    source_file = '成交量加权平均价与相对强弱指数交叉策略-VWAP-and-RSI-Crossover-Strategy.md'
    timeframe = '2d'
    can_short = True
    source_defaults = {'cumulativePeriod': 20, 'rsiPeriod': 20, 'rsiOverbought': 70, 'rsiOversold': 30, 'tradeQty': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ', 'alert']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'cumulativePeriod', 'op': '=', 'expr': 'input(20, "Rolling Period for VWAP", minval=1)', 'conditions': []}, {'mode': '', 'name': 'rsiPeriod', 'op': '=', 'expr': 'input(20, "RSI Period", minval=1)', 'conditions': []}, {'mode': '', 'name': 'rsiOverbought', 'op': '=', 'expr': 'input(70, "RSI Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'rsiOversold', 'op': '=', 'expr': 'input(30, "RSI Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'tradeQty', 'op': '=', 'expr': 'input(1, "Trade Quantity", minval=0.01) // Cantidad de la operación', 'conditions': []}, {'mode': '', 'name': 'typicalPrice', 'op': '=', 'expr': '(high + low + close) / 3', 'conditions': []}, {'mode': '', 'name': 'typicalPriceVolume', 'op': '=', 'expr': 'typicalPrice * volume', 'conditions': []}, {'mode': '', 'name': 'cumulativeTypicalPriceVolume', 'op': '=', 'expr': 'sum(typicalPriceVolume, cumulativePeriod)', 'conditions': []}, {'mode': '', 'name': 'cumulativeVolume', 'op': '=', 'expr': 'sum(volume, cumulativePeriod)', 'conditions': []}, {'mode': '', 'name': 'vwapValue', 'op': '=', 'expr': 'cumulativeTypicalPriceVolume / cumulativeVolume', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'rsi(close, rsiPeriod)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'crossover(close, vwapValue) and rsiValue > rsiOversold', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'crossunder(close, vwapValue) and rsiValue < rsiOverbought', 'conditions': []}, {'mode': '', 'name': 'exitLongCondition', 'op': '=', 'expr': 'crossunder(close, vwapValue) or rsiValue > rsiOverbought // Salir de long cuando el precio cruce debajo del VWAP o el RSI sea alto', 'conditions': []}, {'mode': '', 'name': 'exitShortCondition', 'op': '=', 'expr': 'crossover(close, vwapValue) or rsiValue < rsiOversold // Salir de short cuando el precio cruce por encima del VWAP o el RSI sea bajo', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (shortCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, qty=tradeQty)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long", strategy.long, qty=tradeQty)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty=tradeQty)', 'conditions': ['(shortCondition)'], 'statement': 'strategy.entry("Short", strategy.short, qty=tradeQty)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", "Long", when=exitLongCondition)', 'conditions': [], 'statement': 'strategy.exit("Exit Long", "Long", when=exitLongCondition)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Short", "Short", when=exitShortCondition)', 'conditions': [], 'statement': 'strategy.exit("Exit Short", "Short", when=exitShortCondition)'}]
    original_pine = '/*backtest\nstart: 2023-05-05 00:00:00\nend: 2024-05-10 00:00:00\nperiod: 2d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("VWAP and RSI Strategy with Alerts", overlay=true)\n\n// Inputs\ncumulativePeriod = input(20, "Rolling Period for VWAP", minval=1)\nrsiPeriod = input(20, "RSI Period", minval=1)\nrsiOverbought = input(70, "RSI Overbought Level")\nrsiOversold = input(30, "RSI Oversold Level")\ntradeQty = input(1, "Trade Quantity", minval=0.01)  // Cantidad de la operación\n\n// VWAP Calculation\ntypicalPrice = (high + low + close) / 3\ntypicalPriceVolume = typicalPrice * volume\ncumulativeTypicalPriceVolume = sum(typicalPriceVolume, cumulativePeriod)\ncumulativeVolume = sum(volume, cumulativePeriod)\nvwapValue = cumulativeTypicalPriceVolume / cumulativeVolume\nplot(vwapValue, color=color.blue, title="VWAP")\n\n// RSI Calculation\nrsiValue = rsi(close, rsiPeriod)\nhline(rsiOverbought, "Overbought", color=color.red)\nhline(rsiOversold, "Oversold", color=color.green)\n\n// Entry Conditions\nlongCondition = crossover(close, vwapValue) and rsiValue > rsiOversold\nshortCondition = crossunder(close, vwapValue) and rsiValue < rsiOverbought\n\n// Strategy Execution for Entries\nif (longCondition)\n    strategy.entry("Long", strategy.long, qty=tradeQty)\nif (shortCondition)\n    strategy.entry("Short", strategy.short, qty=tradeQty)\n\n// Conditions for Exiting\nexitLongCondition = crossunder(close, vwapValue) or rsiValue > rsiOverbought  // Salir de long cuando el precio cruce debajo del VWAP o el RSI sea alto\nexitShortCondition = crossover(close, vwapValue) or rsiValue < rsiOversold  // Salir de short cuando el precio cruce por encima del VWAP o el RSI sea bajo\n\n// Strategy Execution for Exits\nstrategy.exit("Exit Long", "Long", when=exitLongCondition)\nstrategy.exit("Exit Short", "Short", when=exitShortCondition)\n\n// Alert Conditions\nalertcondition(longCondition, title="Enter Long", message="ENTER-LONG_BINANCE-FUTURES_BTCUSDT_WunderTrading-1_1M_1354a524d74bc295")\nalertcondition(exitLongCondition, title="Exit Long", message="EXIT-LONG_BINANCE-FUTURES_BTCUSDT_WunderTrading-1_1M_1354a524d74bc295")\nalertcondition(shortCondition, title="Enter Short", message="ENTER-SHORT_BINANCE-FUTURES_BTCUSDT_WunderTrading-1_1M_1354a524d74bc295")\nalertcondition(exitShortCondition, title="Exit Short", message="EXIT-SHORT_BINANCE-FUTURES_BTCUSDT_WunderTrading-1_1M_1354a524d74bc295")'

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
