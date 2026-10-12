"""Source-faithful deep-assisted port of 皮特波浪交易系统策略Pete-Wave-Trading-System-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_57ff918c(PinePortBase, IStrategy):
    source_file = '皮特波浪交易系统策略Pete-Wave-Trading-System-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'fastLength': 9, 'slowLength': 22, 'atrLength': 14, 'atrFilter': 0.5, 'trailingStop': 1.5, 'pullbackThreshold': 0.5, 'minCandleBody': 0.5, 'breakoutConfirmation': True}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'alert']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'fastLength', 'op': '=', 'expr': 'input(9, title="Fast MA Length")', 'conditions': []}, {'mode': '', 'name': 'slowLength', 'op': '=', 'expr': 'input(22, title="Slow MA Length")', 'conditions': []}, {'mode': '', 'name': 'atrLength', 'op': '=', 'expr': 'input(14, title="ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atrFilter', 'op': '=', 'expr': 'input(0.5, title="ATR Filter")', 'conditions': []}, {'mode': '', 'name': 'trailingStop', 'op': '=', 'expr': 'input(1.5, title="Trailing Stop Percentage")', 'conditions': []}, {'mode': '', 'name': 'pullbackThreshold', 'op': '=', 'expr': 'input(0.5, title="Pullback Threshold")', 'conditions': []}, {'mode': '', 'name': 'minCandleBody', 'op': '=', 'expr': 'input(0.5, title="Minimum Candle Body Percentage")', 'conditions': []}, {'mode': '', 'name': 'breakoutConfirmation', 'op': '=', 'expr': 'input(true, title="Use Breakout Confirmation")', 'conditions': []}, {'mode': '', 'name': 'price', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'mafast', 'op': '=', 'expr': 'ta.sma(price, fastLength)', 'conditions': []}, {'mode': '', 'name': 'maslow', 'op': '=', 'expr': 'ta.sma(price, slowLength)', 'conditions': []}, {'mode': '', 'name': 'atrValue', 'op': '=', 'expr': 'ta.atr(atrLength)', 'conditions': []}, {'mode': '', 'name': 'long_entry', 'op': '=', 'expr': 'ta.crossover(mafast, maslow) and atrValue > atrFilter', 'conditions': []}, {'mode': '', 'name': 'short_entry', 'op': '=', 'expr': 'ta.crossunder(mafast, maslow) and atrValue > atrFilter', 'conditions': []}, {'mode': '', 'name': 'pullbackLong', 'op': '=', 'expr': 'ta.crossover(price, mafast) and ta.change(price) <= -pullbackThreshold', 'conditions': []}, {'mode': '', 'name': 'pullbackShort', 'op': '=', 'expr': 'ta.crossunder(price, mafast) and ta.change(price) >= pullbackThreshold', 'conditions': []}, {'mode': '', 'name': 'long_entry', 'op': ':=', 'expr': 'long_entry and (pullbackLong or not ta.crossover(price, mafast))', 'conditions': []}, {'mode': '', 'name': 'short_entry', 'op': ':=', 'expr': 'short_entry and (pullbackShort or not ta.crossunder(price, mafast))', 'conditions': []}, {'mode': '', 'name': 'validLongEntry', 'op': '=', 'expr': 'long_entry and ta.change(price) > 0 and ta.change(price) >= minCandleBody', 'conditions': []}, {'mode': '', 'name': 'validShortEntry', 'op': '=', 'expr': 'short_entry and ta.change(price) < 0 and ta.change(price) <= -minCandleBody', 'conditions': []}, {'mode': '', 'name': 'breakoutLong', 'op': '=', 'expr': 'breakoutConfirmation ? (close > ta.highest(high, fastLength)[1]) : true', 'conditions': []}, {'mode': '', 'name': 'breakoutShort', 'op': '=', 'expr': 'breakoutConfirmation ? (close < ta.lowest(low, fastLength)[1]) : true', 'conditions': []}, {'mode': '', 'name': 'long_entry', 'op': ':=', 'expr': 'validLongEntry and breakoutLong', 'conditions': []}, {'mode': '', 'name': 'short_entry', 'op': ':=', 'expr': 'validShortEntry and breakoutShort', 'conditions': []}, {'mode': '', 'name': 'long_stop', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - trailingStop / 100)', 'conditions': []}, {'mode': '', 'name': 'short_stop', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + trailingStop / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_entry)'}, {'indent': 0, 'statement': 'if (short_entry)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(long_entry)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Short")', 'conditions': ['(long_entry)'], 'statement': 'strategy.close("Short")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short)', 'conditions': ['(short_entry)'], 'statement': 'strategy.entry("Short", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(short_entry)'], 'statement': 'strategy.close("Long")'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", "Long", stop = long_stop)', 'conditions': [], 'statement': 'strategy.exit("Exit Long", "Long", stop = long_stop)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Short", "Short", stop = short_stop)', 'conditions': [], 'statement': 'strategy.exit("Exit Short", "Short", stop = short_stop)'}]
    original_pine = '/*backtest\nstart: 2023-12-01 00:00:00\nend: 2023-12-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("9:22 5 MIN 15 MIN BANKNIFTY", overlay=true)\n\nfastLength = input(9, title="Fast MA Length")\nslowLength = input(22, title="Slow MA Length")\natrLength = input(14, title="ATR Length")\natrFilter = input(0.5, title="ATR Filter")\ntrailingStop = input(1.5, title="Trailing Stop Percentage")\npullbackThreshold = input(0.5, title="Pullback Threshold")\nminCandleBody = input(0.5, title="Minimum Candle Body Percentage")\nbreakoutConfirmation = input(true, title="Use Breakout Confirmation")\n\nprice = close\nmafast = ta.sma(price, fastLength)\nmaslow = ta.sma(price, slowLength)\n\natrValue = ta.atr(atrLength)\n\nlong_entry = ta.crossover(mafast, maslow) and atrValue > atrFilter\nshort_entry = ta.crossunder(mafast, maslow) and atrValue > atrFilter\n\n// Pullback Filter\npullbackLong = ta.crossover(price, mafast) and ta.change(price) <= -pullbackThreshold\npullbackShort = ta.crossunder(price, mafast) and ta.change(price) >= pullbackThreshold\n\n// Include pullback condition only if a valid entry signal is present\nlong_entry := long_entry and (pullbackLong or not ta.crossover(price, mafast))\nshort_entry := short_entry and (pullbackShort or not ta.crossunder(price, mafast))\n\n// Filter based on candle body size\nvalidLongEntry = long_entry and ta.change(price) > 0 and ta.change(price) >= minCandleBody\nvalidShortEntry = short_entry and ta.change(price) < 0 and ta.change(price) <= -minCandleBody\n\n// Breakout confirmation filter\nbreakoutLong = breakoutConfirmation ? (close > ta.highest(high, fastLength)[1]) : true\nbreakoutShort = breakoutConfirmation ? (close < ta.lowest(low, fastLength)[1]) : true\n\nlong_entry := validLongEntry and breakoutLong\nshort_entry := validShortEntry and breakoutShort\n\nif (long_entry)\n    strategy.entry("Long", strategy.long)\n    strategy.close("Short")\n    alert("Long trade iniated")\n    \nif (short_entry)\n    strategy.entry("Short", strategy.short)\n    strategy.close("Long")\n    alert("Short trade initated")\n\n// Trailing Stop-Loss\nlong_stop = strategy.position_avg_price * (1 - trailingStop / 100)\nshort_stop = strategy.position_avg_price * (1 + trailingStop / 100)\nstrategy.exit("Exit Long", "Long", stop = long_stop)\nstrategy.exit("Exit Short", "Short", stop = short_stop)\n\nplot(mafast, color=color.green, linewidth=2, title="Fast MA")\nplot(maslow, color=color.red, linewidth=2, title="Slow MA")'

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
