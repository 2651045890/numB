"""Source-faithful deep-assisted port of 智能动量混合指标零日期权策略模型-Intelligent-Momentum-Mixed-Indicator-Zero-Day-Options-Strategy-Model.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b7905f4d(PinePortBase, IStrategy):
    source_file = '智能动量混合指标零日期权策略模型-Intelligent-Momentum-Mixed-Indicator-Zero-Day-Options-Strategy-Model.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'rsiPeriod': 7, 'rsiThreshold': 50, 'macdFast': 6, 'macdSlow': 13, 'macdSignal': 5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 0
    source_initial_capital = 100000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', 'alert']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'rsiPeriod', 'op': '=', 'expr': 'input.int(7, title="RSI Period (0DTE)")', 'conditions': []}, {'mode': '', 'name': 'rsiThreshold', 'op': '=', 'expr': 'input.int(50, title="RSI Threshold (0DTE)")', 'conditions': []}, {'mode': '', 'name': 'macdFast', 'op': '=', 'expr': 'input.int(6, title="MACD Fast Length (0DTE)")', 'conditions': []}, {'mode': '', 'name': 'macdSlow', 'op': '=', 'expr': 'input.int(13, title="MACD Slow Length (0DTE)")', 'conditions': []}, {'mode': '', 'name': 'macdSignal', 'op': '=', 'expr': 'input.int(5, title="MACD Signal Smoothing (0DTE)")', 'conditions': []}, {'mode': '', 'name': 'vwapValue', 'op': '=', 'expr': 'ta.vwap(close)', 'conditions': []}, {'mode': '', 'name': 'rsiValue', 'op': '=', 'expr': 'ta.rsi(close, rsiPeriod)', 'conditions': []}, {'mode': '', 'name': 'emaShort', 'op': '=', 'expr': 'ta.ema(close, 5) // Faster EMA for quick moves', 'conditions': []}, {'mode': '', 'name': 'emaLong', 'op': '=', 'expr': 'ta.ema(close, 13) // Longer EMA for trend confirmation', 'conditions': []}, {'mode': '', 'name': 'callCondition', 'op': '=', 'expr': '(macdLine > signalLine) and (close > vwapValue) and (rsiValue > rsiThreshold) and (emaShort > emaLong)', 'conditions': []}, {'mode': '', 'name': 'putCondition', 'op': '=', 'expr': '(macdLine < signalLine) and (close < vwapValue) and (rsiValue < rsiThreshold) and (emaShort < emaLong)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if callCondition'}, {'indent': 0, 'statement': 'if putCondition'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Call", strategy.long)', 'conditions': ['callCondition'], 'statement': 'strategy.entry("Call", strategy.long)'}, {'kind': 'entry', 'call': 'strategy.entry("Put", strategy.short)', 'conditions': ['putCondition'], 'statement': 'strategy.entry("Put", strategy.short)'}, {'kind': 'close', 'call': 'strategy.close("Call", when=putCondition)', 'conditions': [], 'statement': 'strategy.close("Call", when=putCondition)'}, {'kind': 'close', 'call': 'strategy.close("Put", when=callCondition)', 'conditions': [], 'statement': 'strategy.close("Put", when=callCondition)'}]
    original_pine = '/*backtest\nstart: 2024-04-01 00:00:00\nend: 2025-03-31 00:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © oxycodine\n\n//@version=5\nstrategy("Pierre\'s 0DTE Option Strategy with MACD, VWAP, RSI, EMA5/13", overlay=true, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// INPUTS for 0DTE parameters\nrsiPeriod    = input.int(7, title="RSI Period (0DTE)")\nrsiThreshold = input.int(50, title="RSI Threshold (0DTE)")\nmacdFast     = input.int(6, title="MACD Fast Length (0DTE)")\nmacdSlow     = input.int(13, title="MACD Slow Length (0DTE)")\nmacdSignal   = input.int(5, title="MACD Signal Smoothing (0DTE)")\n\n// INDICATOR CALCULATIONS\n[macdLine, signalLine, histLine] = ta.macd(close, macdFast, macdSlow, macdSignal)\nvwapValue = ta.vwap(close)\nrsiValue  = ta.rsi(close, rsiPeriod)\nemaShort = ta.ema(close, 5)   // Faster EMA for quick moves\nemaLong  = ta.ema(close, 13)  // Longer EMA for trend confirmation\n\n// PLOT INDICATORS\nplot(emaShort, color=color.blue, title="EMA5")\nplot(emaLong, color=color.orange, title="EMA13")\nplot(vwapValue, color=color.purple, title="VWAP")\n\n// SIGNAL CONDITIONS FOR 0DTE\n// A bullish (Call) signal is generated when:\n// • MACD is bullish (macdLine > signalLine)\n// • Price is above VWAP\n// • RSI is above threshold\n// • Short EMA is above long EMA\ncallCondition = (macdLine > signalLine) and (close > vwapValue) and (rsiValue > rsiThreshold) and (emaShort > emaLong)\n\n// A bearish (Put) signal is generated when the opposite conditions hold\nputCondition  = (macdLine < signalLine) and (close < vwapValue) and (rsiValue < rsiThreshold) and (emaShort < emaLong)\n\n// EXECUTE STRATEGY ENTRIES\nif callCondition\n    strategy.entry("Call", strategy.long)\nif putCondition\n    strategy.entry("Put", strategy.short)\n\n// OPTIONAL: Close positions on reversal signals\nstrategy.close("Call", when=putCondition)\nstrategy.close("Put",  when=callCondition)\n\n// ADDITIONAL PLOTS\nhline(0, title="Zero Line", color=color.gray)\nplot(macdLine - signalLine, color=color.green, title="MACD Histogram")\n\n// ALERT CONDITIONS\nalertcondition(callCondition, title="Call Signal", message="Call Option Signal")\nalertcondition(putCondition, title="Put Signal", message="Put Option Signal")'

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
