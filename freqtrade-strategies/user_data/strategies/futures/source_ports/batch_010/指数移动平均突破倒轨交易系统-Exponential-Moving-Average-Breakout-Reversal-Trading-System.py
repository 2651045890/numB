"""Source-faithful deep-assisted port of 指数移动平均突破倒轨交易系统-Exponential-Moving-Average-Breakout-Reversal-Trading-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_4a76ed2d(PinePortBase, IStrategy):
    source_file = '指数移动平均突破倒轨交易系统-Exponential-Moving-Average-Breakout-Reversal-Trading-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'varip', 'alert']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'emaLength', 'op': '=', 'expr': '5', 'conditions': []}, {'mode': '', 'name': 'emaValue', 'op': '=', 'expr': 'ta.ema(close, emaLength)', 'conditions': []}, {'mode': '', 'name': 'capital', 'op': '=', 'expr': '1000', 'conditions': []}, {'mode': '', 'name': 'riskPerTrade', 'op': '=', 'expr': '2 // Fixed risk per trade in dollars', 'conditions': []}, {'mode': '', 'name': 'candleTouchesEMA', 'op': '=', 'expr': 'low <= emaValue', 'conditions': []}, {'mode': 'varip', 'name': 'validAlertLow', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'varip', 'name': 'validAlertHigh', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'varip', 'name': 'isAlertActive', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'varip', 'name': 'positionSize', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': 'varip', 'name': 'capitalUsed', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'validAlertLow', 'op': ':=', 'expr': 'low', 'conditions': ['alertCandle']}, {'mode': '', 'name': 'validAlertHigh', 'op': ':=', 'expr': 'high', 'conditions': ['alertCandle']}, {'mode': '', 'name': 'isAlertActive', 'op': ':=', 'expr': 'true', 'conditions': ['alertCandle']}, {'mode': '', 'name': 'positionSize', 'op': ':=', 'expr': 'riskPerTrade / alertCandleRange // Shares or contracts', 'conditions': ['isAlertActive']}, {'mode': '', 'name': 'capitalUsed', 'op': ':=', 'expr': 'positionSize * validAlertLow // Capital used in dollars', 'conditions': ['isAlertActive']}, {'mode': '', 'name': 'shortTrigger', 'op': '=', 'expr': 'isAlertActive and low < validAlertLow', 'conditions': []}, {'mode': '', 'name': 'shortEntry', 'op': '=', 'expr': 'validAlertLow', 'conditions': ['shortTrigger']}, {'mode': '', 'name': 'stopLoss', 'op': '=', 'expr': 'validAlertHigh', 'conditions': ['shortTrigger']}, {'mode': '', 'name': 'target', 'op': '=', 'expr': 'shortEntry - (stopLoss - shortEntry)', 'conditions': ['shortTrigger']}, {'mode': '', 'name': 'isAlertActive', 'op': ':=', 'expr': 'false // Disable alert after trade execution', 'conditions': ['shortTrigger']}, {'mode': '', 'name': 'validAlertLow', 'op': ':=', 'expr': 'low', 'conditions': ['not shortTrigger and not candleTouchesEMA[0]']}, {'mode': '', 'name': 'validAlertHigh', 'op': ':=', 'expr': 'high', 'conditions': ['not shortTrigger and not candleTouchesEMA[0]']}, {'mode': '', 'name': 'isAlertActive', 'op': ':=', 'expr': 'true', 'conditions': ['not shortTrigger and not candleTouchesEMA[0]']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if alertCandle'}, {'indent': 0, 'statement': 'if isAlertActive'}, {'indent': 0, 'statement': 'if shortTrigger'}, {'indent': 0, 'statement': 'if not shortTrigger and not candleTouchesEMA[0]'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, qty=positionSize, stop=shortEntry)', 'conditions': ['shortTrigger'], 'statement': 'strategy.entry("Short", strategy.short, qty=positionSize, stop=shortEntry)'}, {'kind': 'exit', 'call': 'strategy.exit("Take Profit", from_entry="Short", limit=target, stop=stopLoss)', 'conditions': ['shortTrigger'], 'statement': 'strategy.exit("Take Profit", from_entry="Short", limit=target, stop=stopLoss)'}]
    original_pine = '/*backtest\nstart: 2024-03-03 00:00:00\nend: 2025-03-01 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n//@version=5\nstrategy("EMA 5 Alert Candle Short", overlay=true)\n\n// Define EMA\nemaLength = 5\nemaValue = ta.ema(close, emaLength)\n\n// Risk Management Parameters\ncapital = 1000\nriskPerTrade = 2  // Fixed risk per trade in dollars\n\n// Check if previous candles touched EMA, but the current candle is far above EMA\ncandleTouchesEMA = low <= emaValue\nalertCandle = not candleTouchesEMA[0] and candleTouchesEMA[1] and candleTouchesEMA[2] and candleTouchesEMA[3]\n\n// Persistent Variables to Store Alert Levels\nvarip float validAlertLow = na\nvarip float validAlertHigh = na\nvarip bool isAlertActive = false\nvarip float positionSize = na\nvarip float capitalUsed = na\n\n// When an alert candle is identified, store its high and low\nif alertCandle\n    validAlertLow := low\n    validAlertHigh := high\n    isAlertActive := true\n\n// Calculate Position Sizing\nif isAlertActive\n    alertCandleRange = validAlertHigh - validAlertLow\n    positionSize := riskPerTrade / alertCandleRange  // Shares or contracts\n    capitalUsed := positionSize * validAlertLow      // Capital used in dollars\n\n// Check if the next candle breaks the alert candle low (entry condition)\nshortTrigger = isAlertActive and low < validAlertLow\nif shortTrigger\n    shortEntry = validAlertLow\n    stopLoss = validAlertHigh\n    target = shortEntry - (stopLoss - shortEntry)\n    isAlertActive := false  // Disable alert after trade execution\n\n    // Execute trade\n    strategy.entry("Short", strategy.short, qty=positionSize, stop=shortEntry)\n    strategy.exit("Take Profit", from_entry="Short", limit=target, stop=stopLoss)\n\n// Reset alert candle if next candle does not break low but also does not touch 5EMA\nif not shortTrigger and not candleTouchesEMA[0]\n    validAlertLow := low\n    validAlertHigh := high\n    isAlertActive := true\n\n// Plot EMA\nplot(emaValue, title="EMA 5", color=color.blue, linewidth=2)\n\n// Mark alert candle\nplotshape(alertCandle, location=location.abovebar, color=color.red, style=shape.labeldown, title="Alert Candle")'

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
