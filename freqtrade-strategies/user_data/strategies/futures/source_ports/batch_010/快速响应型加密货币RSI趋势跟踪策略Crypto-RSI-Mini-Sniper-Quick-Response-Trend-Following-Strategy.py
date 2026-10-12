"""Source-faithful deep-assisted port of 快速响应型加密货币RSI趋势跟踪策略Crypto-RSI-Mini-Sniper-Quick-Response-Trend-Following-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_093f7b90(PinePortBase, IStrategy):
    source_file = '快速响应型加密货币RSI趋势跟踪策略Crypto-RSI-Mini-Sniper-Quick-Response-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsiLength': 14, 'oversoldLevel': 35, 'overboughtLevel': 65, 'tp_1': 5.0, 'sl': 2.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': 'input(14, title="RSI Length")', 'conditions': []}, {'mode': '', 'name': 'oversoldLevel', 'op': '=', 'expr': 'input(35, title="Oversold Level")', 'conditions': []}, {'mode': '', 'name': 'overboughtLevel', 'op': '=', 'expr': 'input(65, title="Overbought Level")', 'conditions': []}, {'mode': '', 'name': 'sma400', 'op': '=', 'expr': 'ta.sma(close, 400)', 'conditions': []}, {'mode': '', 'name': 'tp_1', 'op': '=', 'expr': 'input.float(5.0, title="Take Profit 1 (%)")', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': 'input.float(2.0, title="Stop Loss (%)")', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'ta.rsi(close, rsiLength)', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'rsi < oversoldLevel and close > sma400', 'conditions': []}, {'mode': '', 'name': 'longExitCondition', 'op': '=', 'expr': 'rsi > 80 and close > sma400', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - sl / 100)', 'conditions': []}, {'mode': '', 'name': 'longTargetPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + tp_1 / 100)', 'conditions': []}, {'mode': '', 'name': 'shortCondition', 'op': '=', 'expr': 'rsi > overboughtLevel and close < sma400', 'conditions': []}, {'mode': '', 'name': 'shortExitCondition', 'op': '=', 'expr': 'rsi < 20 and close < sma400', 'conditions': []}, {'mode': '', 'name': 'shortStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + sl / 100)', 'conditions': []}, {'mode': '', 'name': 'shortTargetPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - tp_1 / 100)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, when=longCondition)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, when=longCondition)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=longExitCondition)', 'conditions': [], 'statement': 'strategy.close("Long", when=longExitCondition)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Long", "Long", stop=longStopPrice, limit=longTargetPrice)', 'conditions': [], 'statement': 'strategy.exit("Exit Long", "Long", stop=longStopPrice, limit=longTargetPrice)'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, when=shortCondition)', 'conditions': [], 'statement': 'strategy.entry("Short", strategy.short, when=shortCondition)'}, {'kind': 'close', 'call': 'strategy.close("Short", when=shortExitCondition)', 'conditions': [], 'statement': 'strategy.close("Short", when=shortExitCondition)'}, {'kind': 'exit', 'call': 'strategy.exit("Exit Short", "Short", stop=shortStopPrice, limit=shortTargetPrice)', 'conditions': [], 'statement': 'strategy.exit("Exit Short", "Short", stop=shortStopPrice, limit=shortTargetPrice)'}]
    original_pine = '/*backtest\nstart: 2023-12-23 00:00:00\nend: 2024-01-22 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Wielkieef\n\n\n//@version=5\nstrategy("Crypto RSI mini-Sniper [5min]", shorttitle="RSI Strategy", overlay=true)\n\n// Inputs\nrsiLength = input(14, title="RSI Length")\noversoldLevel = input(35, title="Oversold Level")\noverboughtLevel = input(65, title="Overbought Level")\nsma400 = ta.sma(close, 400)\ntp_1 = input.float(5.0, title="Take Profit 1 (%)") \nsl = input.float(2.0, title="Stop Loss (%)") \n\n// Longs Logic\nrsi = ta.rsi(close, rsiLength)\nlongCondition = rsi < oversoldLevel and close > sma400  \nlongExitCondition = rsi > 80 and close > sma400  \nlongStopPrice = strategy.position_avg_price * (1 - sl / 100)\nlongTargetPrice = strategy.position_avg_price * (1 + tp_1 / 100)\n\n// \nstrategy.entry("Long", strategy.long, when=longCondition)\nstrategy.close("Long", when=longExitCondition)\nstrategy.exit("Exit Long", "Long", stop=longStopPrice, limit=longTargetPrice)\n\n// Shorts Logic\nshortCondition = rsi > overboughtLevel and close < sma400  \nshortExitCondition = rsi < 20  and close < sma400\nshortStopPrice = strategy.position_avg_price * (1 + sl / 100)\nshortTargetPrice = strategy.position_avg_price * (1 - tp_1 / 100)\n\n// \nstrategy.entry("Short", strategy.short, when=shortCondition)\nstrategy.close("Short", when=shortExitCondition)\nstrategy.exit("Exit Short", "Short", stop=shortStopPrice, limit=shortTargetPrice)\n\n//by wielkieef'

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
