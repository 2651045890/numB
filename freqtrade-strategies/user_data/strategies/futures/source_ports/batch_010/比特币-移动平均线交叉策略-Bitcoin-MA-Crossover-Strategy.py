"""Source-faithful deep-assisted port of 比特币-移动平均线交叉策略-Bitcoin-MA-Crossover-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_337ef958(PinePortBase, IStrategy):
    source_file = '比特币-移动平均线交叉策略-Bitcoin-MA-Crossover-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'usr_risk': 10, 'sma_fast': 20, 'sma_slow': 40, 'rsi_valu': 14}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.order', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'usr_risk', 'op': '=', 'expr': 'input(title="Equity Risk (%)",type=input.integer,minval=1,maxval=100,step=1,defval=10,confirm=false)', 'conditions': []}, {'mode': '', 'name': 'sma_fast', 'op': '=', 'expr': 'input(title="Fast MA (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=20,confirm=false)', 'conditions': []}, {'mode': '', 'name': 'sma_slow', 'op': '=', 'expr': 'input(title="Slow MA (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=40,confirm=false)', 'conditions': []}, {'mode': '', 'name': 'rsi_valu', 'op': '=', 'expr': 'input(title="RSI (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=14,confirm=false)', 'conditions': []}, {'mode': '', 'name': 'shortSMA', 'op': '=', 'expr': 'sma(close, sma_fast)', 'conditions': []}, {'mode': '', 'name': 'longSMA', 'op': '=', 'expr': 'sma(close, sma_slow)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'rsi(close, rsi_valu)', 'conditions': []}, {'mode': '', 'name': 'amount', 'op': '=', 'expr': 'usr_risk / 100 * (strategy.initial_capital + strategy.netprofit)', 'conditions': []}, {'mode': '', 'name': 'units', 'op': '=', 'expr': 'floor(amount / close)', 'conditions': []}, {'mode': '', 'name': 'longEntry', 'op': '=', 'expr': 'crossover(shortSMA, longSMA)', 'conditions': []}, {'mode': '', 'name': 'shortEntry', 'op': '=', 'expr': 'crossunder(shortSMA, longSMA)', 'conditions': []}, {'mode': '', 'name': 'longExit', 'op': '=', 'expr': 'crossunder(shortSMA, longSMA)', 'conditions': []}, {'mode': '', 'name': 'shortExit', 'op': '=', 'expr': 'crossover(shortSMA, longSMA)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longEntry)'}, {'indent': 0, 'statement': 'if(longExit and strategy.position_size > 0)'}, {'indent': 0, 'statement': 'if (shortEntry)'}, {'indent': 0, 'statement': 'if(shortExit and strategy.position_size < 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("long", strategy.long, units, when = rsi > 50)', 'conditions': ['(longEntry)'], 'statement': 'strategy.entry("long", strategy.long, units, when = rsi > 50)'}, {'kind': 'order', 'call': 'strategy.order("exit long", strategy.short, abs(strategy.position_size))', 'conditions': [], 'statement': 'strategy.order("exit long", strategy.short, abs(strategy.position_size))'}, {'kind': 'entry', 'call': 'strategy.entry("short", strategy.short, units, when = rsi < 50)', 'conditions': ['(shortEntry)'], 'statement': 'strategy.entry("short", strategy.short, units, when = rsi < 50)'}, {'kind': 'order', 'call': 'strategy.order("exit short", strategy.long, abs(strategy.position_size))', 'conditions': [], 'statement': 'strategy.order("exit short", strategy.long, abs(strategy.position_size))'}]
    original_pine = '/*backtest\nstart: 2023-11-03 00:00:00\nend: 2023-12-03 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//Trading Strategy Warning - Past performance may not equal future performance\n//Account Size Warning - Performance based upon default 10% risk per trade, of account size $100,000. Adjust before you trade to see your own drawdown.\n//Time Frame - D1 and H4, warning H4 has a lower profit factor (fake-outs, and account drawdown), D1 recommended\n//Trend Following System - Profitability of this system is dependent on a STRONG trend in Bitcoin, into the future\nstrategy("Bitcoin - MA Crossover Strategy", overlay=true)\n\n// User Input\nusr_risk = input(title="Equity Risk (%)",type=input.integer,minval=1,maxval=100,step=1,defval=10,confirm=false)\nsma_fast = input(title="Fast MA (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=20,confirm=false)\nsma_slow = input(title="Slow MA (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=40,confirm=false)\nrsi_valu = input(title="RSI (Period)",type=input.integer,minval=1,maxval=500,step=1,defval=14,confirm=false)\n\n// Create Indicator\'s\nshortSMA = sma(close, sma_fast)\nlongSMA = sma(close, sma_slow)\nrsi = rsi(close, rsi_valu)\nstrategy.initial_capital = 50000\n// Units to buy\namount = usr_risk / 100 * (strategy.initial_capital + strategy.netprofit)\nunits = floor(amount / close)\n\n// Specify entry conditions\nlongEntry = crossover(shortSMA, longSMA)\nshortEntry = crossunder(shortSMA, longSMA)\n\n// Specify exit conditions\nlongExit = crossunder(shortSMA, longSMA)\nshortExit = crossover(shortSMA, longSMA)\n\n// Execute long trade\nif (longEntry)\n    strategy.entry("long", strategy.long, units, when = rsi > 50)\n\n// Exit long trade\nif(longExit and strategy.position_size > 0)    \n    strategy.order("exit long", strategy.short, abs(strategy.position_size))\n\n// Execute short trade\nif (shortEntry)\n    strategy.entry("short", strategy.short, units, when = rsi < 50)\n    \n// Exit short trade\nif(shortExit and strategy.position_size < 0)    \n    strategy.order("exit short", strategy.long, abs(strategy.position_size))\n\n// Plot Moving Average\'s to chart\nplot(shortSMA)\nplot(longSMA, color=color.black)'

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
