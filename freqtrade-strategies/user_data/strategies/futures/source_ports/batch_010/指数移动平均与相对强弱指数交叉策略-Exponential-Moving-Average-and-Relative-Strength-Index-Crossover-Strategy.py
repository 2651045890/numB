"""Source-faithful deep-assisted port of 指数移动平均与相对强弱指数交叉策略-Exponential-Moving-Average-and-Relative-Strength-Index-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_f941cd48(PinePortBase, IStrategy):
    source_file = '指数移动平均与相对强弱指数交叉策略-Exponential-Moving-Average-and-Relative-Strength-Index-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'emaLength': 68, 'rsiLength': 13, 'buyOffset': 2, 'sellOffset': 2, 'stopLossPoints': 20, 'buyRSIProfitLevel': 70, 'sellRSIProfitLevel': 28}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'for ']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'emaLength', 'op': '=', 'expr': 'input.int(68, title="EMA Length")', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input.int(13, title="RSI Period")', 'conditions': []}, {'mode': '', 'name': 'buyOffset', 'op': '=', 'expr': 'input.float(2, title="Buy Offset (above EMA)")', 'conditions': []}, {'mode': '', 'name': 'sellOffset', 'op': '=', 'expr': 'input.float(2, title="Sell Offset (below EMA)")', 'conditions': []}, {'mode': '', 'name': 'stopLossPoints', 'op': '=', 'expr': 'input.float(20, title="Stop Loss (points)")', 'conditions': []}, {'mode': '', 'name': 'buyRSIProfitLevel', 'op': '=', 'expr': 'input.int(70, title="Buy RSI Profit Level")', 'conditions': []}, {'mode': '', 'name': 'sellRSIProfitLevel', 'op': '=', 'expr': 'input.int(28, title="Sell RSI Profit Level")', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.ema(close, emaLength)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'buyPrice', 'op': '=', 'expr': 'ema + buyOffset', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'ta.crossover(close, buyPrice)', 'conditions': []}, {'mode': '', 'name': 'sellPrice', 'op': '=', 'expr': 'ema - sellOffset', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'ta.crossunder(close, sellPrice)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buyCondition'}, {'indent': 0, 'statement': 'if strategy.position_size > 0'}, {'indent': 4, 'statement': 'if close <= strategy.position_avg_price - stopLossPoints'}, {'indent': 4, 'statement': 'if rsi >= buyRSIProfitLevel'}, {'indent': 0, 'statement': 'if sellCondition'}, {'indent': 0, 'statement': 'if strategy.position_size < 0'}, {'indent': 4, 'statement': 'if close >= strategy.position_avg_price + stopLossPoints'}, {'indent': 4, 'statement': 'if rsi <= sellRSIProfitLevel'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buyCondition'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Buy", comment="Stop Loss")', 'conditions': ['strategy.position_size > 0', 'close <= strategy.position_avg_price - stopLossPoints'], 'statement': 'strategy.close("Buy", comment="Stop Loss")'}, {'kind': 'close', 'call': 'strategy.close("Buy", comment="Profit Target")', 'conditions': ['strategy.position_size > 0', 'rsi >= buyRSIProfitLevel'], 'statement': 'strategy.close("Buy", comment="Profit Target")'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['sellCondition'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Sell", comment="Stop Loss")', 'conditions': ['strategy.position_size < 0', 'close >= strategy.position_avg_price + stopLossPoints'], 'statement': 'strategy.close("Sell", comment="Stop Loss")'}, {'kind': 'close', 'call': 'strategy.close("Sell", comment="Profit Target")', 'conditions': ['strategy.position_size < 0', 'rsi <= sellRSIProfitLevel'], 'statement': 'strategy.close("Sell", comment="Profit Target")'}]
    original_pine = '/*backtest\nstart: 2024-02-21 00:00:00\nend: 2024-10-05 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA & RSI Custom Strategy", overlay=true)\n\n// Input Parameters\nemaLength = input.int(68, title="EMA Length")\nrsiLength = input.int(13, title="RSI Period")\nbuyOffset = input.float(2, title="Buy Offset (above EMA)")\nsellOffset = input.float(2, title="Sell Offset (below EMA)")\nstopLossPoints = input.float(20, title="Stop Loss (points)")\nbuyRSIProfitLevel = input.int(70, title="Buy RSI Profit Level")\nsellRSIProfitLevel = input.int(28, title="Sell RSI Profit Level")\n\n// EMA and RSI Calculations\nema = ta.ema(close, emaLength)\nrsi = ta.rsi(close, rsiLength)\n\n// Buy Condition\nbuyPrice = ema + buyOffset\nbuyCondition = ta.crossover(close, buyPrice)\nif buyCondition\n    strategy.entry("Buy", strategy.long)\n\n// Stop Loss and Profit for Buy\nif strategy.position_size > 0\n    if close <= strategy.position_avg_price - stopLossPoints\n        strategy.close("Buy", comment="Stop Loss")\n    if rsi >= buyRSIProfitLevel\n        strategy.close("Buy", comment="Profit Target")\n\n// Sell Condition\nsellPrice = ema - sellOffset\nsellCondition = ta.crossunder(close, sellPrice)\nif sellCondition\n    strategy.entry("Sell", strategy.short)\n\n// Stop Loss and Profit for Sell\nif strategy.position_size < 0\n    if close >= strategy.position_avg_price + stopLossPoints\n        strategy.close("Sell", comment="Stop Loss")\n    if rsi <= sellRSIProfitLevel\n        strategy.close("Sell", comment="Profit Target")\n\n// Plot EMA\nplot(ema, color=color.blue, title="EMA 68")'

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
