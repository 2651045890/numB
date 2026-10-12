"""Source-faithful deep-assisted port of 比特币和黄金双跳空策略Bitcoin-and-Gold-Double-Gap-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_0a4a7551(PinePortBase, IStrategy):
    source_file = '比特币和黄金双跳空策略Bitcoin-and-Gold-Double-Gap-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'fastLength': 5, 'slowLength': 13, 'bollingerLength': 20, 'bollingerMultiplier': 2, 'stopLossMultiplier': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input(5, title="Fast EMA Length")', 'conditions': []}, {'mode': '', 'name': 'slowLength', 'op': '=', 'expr': 'input(13, title="Slow EMA Length")', 'conditions': []}, {'mode': '', 'name': 'bollingerLength', 'op': '=', 'expr': 'input(20, title="Bollinger Band Length")', 'conditions': []}, {'mode': '', 'name': 'bollingerMultiplier', 'op': '=', 'expr': 'input(2, title="Bollinger Band Multiplier")', 'conditions': []}, {'mode': '', 'name': 'stopLossMultiplier', 'op': '=', 'expr': 'input(1, title="Stop Loss Multiplier")', 'conditions': []}, {'mode': '', 'name': 'fastEMA', 'op': '=', 'expr': 'ta.ema(close, fastLength)', 'conditions': []}, {'mode': '', 'name': 'slowEMA', 'op': '=', 'expr': 'ta.ema(close, slowLength)', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(close, bollingerLength)', 'conditions': []}, {'mode': '', 'name': 'upperBand', 'op': '=', 'expr': 'basis + bollingerMultiplier * ta.stdev(close, bollingerLength)', 'conditions': []}, {'mode': '', 'name': 'lowerBand', 'op': '=', 'expr': 'basis - bollingerMultiplier * ta.stdev(close, bollingerLength)', 'conditions': []}, {'mode': '', 'name': 'buyCondition', 'op': '=', 'expr': 'ta.crossover(fastEMA, slowEMA) and (close <= upperBand or close <= basis)', 'conditions': []}, {'mode': '', 'name': 'sellCondition', 'op': '=', 'expr': 'ta.crossunder(fastEMA, slowEMA) and (close >= lowerBand or close >= basis)', 'conditions': []}, {'mode': '', 'name': 'stopLossLevel', 'op': '=', 'expr': 'ta.lowest(low, 2)[1] - stopLossMultiplier * ta.atr(14)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when = buyCondition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when = buyCondition)'}, {'kind': 'exit', 'call': 'strategy.exit("Stop Loss/Close", from_entry="Buy", loss=stopLossLevel)', 'conditions': [], 'statement': 'strategy.exit("Stop Loss/Close", from_entry="Buy", loss=stopLossLevel)'}, {'kind': 'close', 'call': 'strategy.close("Sell", when = sellCondition)', 'conditions': [], 'statement': 'strategy.close("Sell", when = sellCondition)'}]
    original_pine = '/*backtest\nstart: 2023-01-16 00:00:00\nend: 2024-01-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © singhak8757\n\n//@version=5\nstrategy("Bitcoin and Gold 5min Scalping Strategy2.0", overlay=true)\n\n\n// Input parameters\nfastLength = input(5, title="Fast EMA Length")\nslowLength = input(13, title="Slow EMA Length")\nbollingerLength = input(20, title="Bollinger Band Length")\nbollingerMultiplier = input(2, title="Bollinger Band Multiplier")\nstopLossMultiplier = input(1, title="Stop Loss Multiplier")\n\n// Calculate EMAs\nfastEMA = ta.ema(close, fastLength)\nslowEMA = ta.ema(close, slowLength)\n\n// Calculate Bollinger Bands\nbasis = ta.sma(close, bollingerLength)\nupperBand = basis + bollingerMultiplier * ta.stdev(close, bollingerLength)\nlowerBand = basis - bollingerMultiplier * ta.stdev(close, bollingerLength)\n\n// Buy condition\nbuyCondition = ta.crossover(fastEMA, slowEMA) and (close <= upperBand or close <= basis)\n\n// Sell condition\nsellCondition = ta.crossunder(fastEMA, slowEMA) and (close >= lowerBand or close >= basis)\n\n// Calculate stop loss level\nstopLossLevel = ta.lowest(low, 2)[1] - stopLossMultiplier * ta.atr(14)\n\n// Plot EMAs\nplot(fastEMA, color=color.rgb(0, 156, 21), title="Fast EMA")\nplot(slowEMA, color=color.rgb(255, 0, 0), title="Slow EMA")\n\n// Plot Bollinger Bands\nplot(upperBand, color=color.new(#000000, 0), title="Upper Bollinger Band")\nplot(lowerBand, color=color.new(#1b007e, 0), title="Lower Bollinger Band")\n\n// Plot Buy and Sell signals\nplotshape(series=buyCondition, title="Buy Signal", color=color.green, style=shape.labelup, location=location.belowbar)\nplotshape(series=sellCondition, title="Sell Signal", color=color.red, style=shape.labeldown, location=location.abovebar)\n\n// Plot Stop Loss level\nplot(stopLossLevel, color=color.orange, title="Stop Loss Level")\n\n// Strategy logic\nstrategy.entry("Buy", strategy.long, when = buyCondition)\nstrategy.exit("Stop Loss/Close", from_entry="Buy", loss=stopLossLevel)\nstrategy.close("Sell", when = sellCondition)'

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
