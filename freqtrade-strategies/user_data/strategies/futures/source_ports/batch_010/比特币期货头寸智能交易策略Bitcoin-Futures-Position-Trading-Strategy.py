"""Source-faithful deep-assisted port of 比特币期货头寸智能交易策略Bitcoin-Futures-Position-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a03d8f1d(PinePortBase, IStrategy):
    source_file = '比特币期货头寸智能交易策略Bitcoin-Futures-Position-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'StartDate': 'timestamp("01 Jan 2021")', 'EndDate': 'timestamp("01 Jan 2024")', 'symbolInput': 'BTC_USDT:swap', 'length': 7, 'overSold': 75, 'overBought': 30, 'longLossPerc': 25, 'shortLossPerc': 25}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10.0
    source_pyramiding = 2
    source_initial_capital = 1000.0
    source_commission_percent = 0.05
    source_features = ['request.security', 'strategy.exit', 'strategy.entry', 'strategy.position_size']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'StartDate', 'op': '=', 'expr': 'input(timestamp("01 Jan 2021"), title="Start Date")', 'conditions': []}, {'mode': '', 'name': 'EndDate', 'op': '=', 'expr': 'input(timestamp("01 Jan 2024"), title="Start Date")', 'conditions': []}, {'mode': '', 'name': 'inDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'symbolInput', 'op': '=', 'expr': 'input(title="Bitfinex Short Symbol", defval="BTC_USDT:swap")', 'conditions': []}, {'mode': '', 'name': 'Shorts', 'op': '=', 'expr': 'request.security(symbolInput, "", open)', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input(title="Length", defval=7, group="RSI Settings" )', 'conditions': []}, {'mode': '', 'name': 'overSold', 'op': '=', 'expr': 'input(title="High Shorts Threshold", defval=75, group="RSI Settings" )', 'conditions': []}, {'mode': '', 'name': 'overBought', 'op': '=', 'expr': 'input(title="Low Shorts Threshold", defval=30, group="RSI Settings" )', 'conditions': []}, {'mode': '', 'name': 'vrsi', 'op': '=', 'expr': 'ta.rsi(Shorts, length)', 'conditions': []}, {'mode': '', 'name': 'RSIunder', 'op': '=', 'expr': 'ta.crossover(vrsi, overSold)', 'conditions': []}, {'mode': '', 'name': 'RSIover', 'op': '=', 'expr': 'ta.crossunder(vrsi, overBought)', 'conditions': []}, {'mode': '', 'name': 'longLossPerc', 'op': '=', 'expr': 'input.float(title="Long Stop Loss (%)", defval=25, group="Stop Loss Settings") * 0.01', 'conditions': []}, {'mode': '', 'name': 'shortLossPerc', 'op': '=', 'expr': 'input.float(title="Short Stop Loss (%)", defval=25, group="Stop Loss Settings") * 0.01', 'conditions': []}, {'mode': '', 'name': 'longStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - longLossPerc)', 'conditions': []}, {'mode': '', 'name': 'shortStopPrice', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + shortLossPerc)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (not na(vrsi))'}, {'indent': 1, 'statement': 'if (inDateRange and RSIover)'}, {'indent': 1, 'statement': 'if (inDateRange and RSIunder)'}, {'indent': 0, 'statement': 'if (strategy.position_size > 0)'}, {'indent': 0, 'statement': 'if (strategy.position_size < 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("LONG", strategy.long, comment="LONG")', 'conditions': ['(not na(vrsi))', '(inDateRange and RSIover)'], 'statement': 'strategy.entry("LONG", strategy.long, comment="LONG")'}, {'kind': 'entry', 'call': 'strategy.entry("SHORT", strategy.short, comment="SHORT")', 'conditions': ['(not na(vrsi))', '(inDateRange and RSIunder)'], 'statement': 'strategy.entry("SHORT", strategy.short, comment="SHORT")'}, {'kind': 'exit', 'call': 'strategy.exit(id="LONG STOP", stop=longStopPrice)', 'conditions': ['(strategy.position_size > 0)'], 'statement': 'strategy.exit(id="LONG STOP", stop=longStopPrice)'}, {'kind': 'exit', 'call': 'strategy.exit(id="SHORT STOP", stop=shortStopPrice)', 'conditions': ['(strategy.position_size < 0)'], 'statement': 'strategy.exit(id="SHORT STOP", stop=shortStopPrice)'}]
    original_pine = '/*backtest\nstart: 2023-12-26 00:00:00\nend: 2024-01-25 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bitfinex Shorts Strat", \n     overlay=true,\n     default_qty_type=strategy.percent_of_equity,\n     default_qty_value=10, precision=2, initial_capital=1000,\n     pyramiding=2,\n     commission_value=0.05)\n\n//Backtest date range\nStartDate = input(timestamp("01 Jan 2021"), title="Start Date")\nEndDate = input(timestamp("01 Jan 2024"), title="Start Date")\ninDateRange = true\n\nsymbolInput = input(title="Bitfinex Short Symbol", defval="BTC_USDT:swap")\nShorts = request.security(symbolInput, "", open)\n\n// RSI Input Settings\nlength = input(title="Length", defval=7, group="RSI Settings" )\noverSold = input(title="High Shorts Threshold", defval=75, group="RSI Settings" )\noverBought = input(title="Low Shorts Threshold", defval=30, group="RSI Settings" )\n\n// Calculating RSI\nvrsi = ta.rsi(Shorts, length)\nRSIunder = ta.crossover(vrsi, overSold)\nRSIover = ta.crossunder(vrsi, overBought)\n\n// Stop Loss Input Settings\nlongLossPerc = input.float(title="Long Stop Loss (%)", defval=25, group="Stop Loss Settings") * 0.01\nshortLossPerc = input.float(title="Short Stop Loss (%)", defval=25, group="Stop Loss Settings") * 0.01\n\n// Calculating Stop Loss\nlongStopPrice  = strategy.position_avg_price * (1 - longLossPerc)\nshortStopPrice = strategy.position_avg_price * (1 + shortLossPerc)\n\n// Strategy Entry\nif (not na(vrsi))\n\tif (inDateRange and RSIover)\n\t\tstrategy.entry("LONG", strategy.long, comment="LONG")\n\tif (inDateRange and RSIunder)\n\t\tstrategy.entry("SHORT", strategy.short, comment="SHORT")\n\n// Submit exit orders based on calculated stop loss price\nif (strategy.position_size > 0)\n    strategy.exit(id="LONG STOP", stop=longStopPrice)\nif (strategy.position_size < 0)\n    strategy.exit(id="SHORT STOP", stop=shortStopPrice)'

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
