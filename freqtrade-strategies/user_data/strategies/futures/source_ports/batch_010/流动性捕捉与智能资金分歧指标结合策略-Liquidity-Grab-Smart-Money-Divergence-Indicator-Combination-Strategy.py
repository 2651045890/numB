"""Source-faithful deep-assisted port of 流动性捕捉与智能资金分歧指标结合策略-Liquidity-Grab-Smart-Money-Divergence-Indicator-Combination-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_5fc85030(PinePortBase, IStrategy):
    source_file = '流动性捕捉与智能资金分歧指标结合策略-Liquidity-Grab-Smart-Money-Divergence-Indicator-Combination-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'length': 14, 'lookback': 5, 'maLength': 50, 'atrLength': 14, 'atrMultiplier': 1.5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'for ']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(14, "RSI Length")', 'conditions': []}, {'mode': '', 'name': 'lookback', 'op': '=', 'expr': 'input(5, "Lookback Bars")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'maLength', 'op': '=', 'expr': 'input(50, "MA Length")', 'conditions': []}, {'mode': '', 'name': 'atrLength', 'op': '=', 'expr': 'input(14, "ATR Length")', 'conditions': []}, {'mode': '', 'name': 'atrMultiplier', 'op': '=', 'expr': 'input(1.5, "ATR Multiplier")', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'ta.rsi(src, length)', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': 'ta.sma(close, maLength)', 'conditions': []}, {'mode': '', 'name': 'trendUp', 'op': '=', 'expr': 'close > ma', 'conditions': []}, {'mode': '', 'name': 'trendDown', 'op': '=', 'expr': 'close < ma', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'ta.atr(atrLength)', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'atr * atrMultiplier', 'conditions': []}, {'mode': '', 'name': 'sweepHigh', 'op': '=', 'expr': 'ta.highest(high, lookback) == high and close < high[1]', 'conditions': []}, {'mode': '', 'name': 'sweepLow', 'op': '=', 'expr': 'ta.lowest(low, lookback) == low and close > low[1]', 'conditions': []}, {'mode': '', 'name': 'bullishDivergence', 'op': '=', 'expr': 'sweepLow and (rsiValue > ta.lowest(rsiValue, lookback))', 'conditions': []}, {'mode': '', 'name': 'bearishDivergence', 'op': '=', 'expr': 'sweepHigh and (rsiValue < ta.highest(rsiValue, lookback))', 'conditions': []}, {'mode': '', 'name': 'buySignal', 'op': '=', 'expr': 'bullishDivergence and trendUp', 'conditions': []}, {'mode': '', 'name': 'sellSignal', 'op': '=', 'expr': 'bearishDivergence and trendDown', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if buySignal'}, {'indent': 0, 'statement': 'if sellSignal'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['buySignal'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Sell", from_entry="Buy", stop=close - sl, limit=close + sl * 2)', 'conditions': ['buySignal'], 'statement': 'strategy.exit("Sell", from_entry="Buy", stop=close - sl, limit=close + sl * 2)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short)', 'conditions': ['sellSignal'], 'statement': 'strategy.entry("Sell", strategy.short)'}, {'kind': 'exit', 'call': 'strategy.exit("Buy", from_entry="Sell", stop=close + sl, limit=close - sl * 2)', 'conditions': ['sellSignal'], 'statement': 'strategy.exit("Buy", from_entry="Sell", stop=close + sl, limit=close - sl * 2)'}]
    original_pine = '/*backtest\nstart: 2024-03-25 00:00:00\nend: 2025-03-24 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("Liquidity Grab + Smart Money Divergence Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=1)\n\n// Input settings\nlength = input(14, "RSI Length")\nlookback = input(5, "Lookback Bars")\nsrc = close\nmaLength = input(50, "MA Length")\natrLength = input(14, "ATR Length")\natrMultiplier = input(1.5, "ATR Multiplier")\n\n// RSI Calculation\nrsiValue = ta.rsi(src, length)\n\n// Moving Average Trend Filter\nma = ta.sma(close, maLength)\ntrendUp = close > ma\ntrendDown = close < ma\n\n// ATR for dynamic stop-loss and take-profit\natr = ta.atr(atrLength)\nsl = atr * atrMultiplier\n\n// Detect liquidity grab (sweep of recent high/low)\nsweepHigh = ta.highest(high, lookback) == high and close < high[1]\nsweepLow = ta.lowest(low, lookback) == low and close > low[1]\n\n// Detect Smart Money Divergence\nbullishDivergence = sweepLow and (rsiValue > ta.lowest(rsiValue, lookback))\nbearishDivergence = sweepHigh and (rsiValue < ta.highest(rsiValue, lookback))\n\n// Trade signals with trend confirmation\nbuySignal = bullishDivergence and trendUp\nsellSignal = bearishDivergence and trendDown\n\n// Execute trades with stop-loss and take-profit\nif buySignal\n    strategy.entry("Buy", strategy.long)\n    strategy.exit("Sell", from_entry="Buy", stop=close - sl, limit=close + sl * 2)\nif sellSignal\n    strategy.entry("Sell", strategy.short)\n    strategy.exit("Buy", from_entry="Sell", stop=close + sl, limit=close - sl * 2)\n\n// Plot signals on chart\nplotshape(buySignal, location=location.belowbar, color=color.green, style=shape.labelup, size=size.small, title="Buy Signal")\nplotshape(sellSignal, location=location.abovebar, color=color.red, style=shape.labeldown, size=size.small, title="Sell Signal")\nplot(ma, title="50 MA", color=color.blue)'

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
