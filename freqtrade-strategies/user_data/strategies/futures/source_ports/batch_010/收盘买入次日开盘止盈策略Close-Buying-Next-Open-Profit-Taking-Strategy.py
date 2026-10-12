"""Source-faithful deep-assisted port of 收盘买入次日开盘止盈策略Close-Buying-Next-Open-Profit-Taking-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_36b7ab81(PinePortBase, IStrategy):
    source_file = '收盘买入次日开盘止盈策略Close-Buying-Next-Open-Profit-Taking-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'MarketFilterLen': 200, 'StopLossPerc': 0.95}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.opentrades', 'timeframe.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'MarketFilterLen', 'op': '=', 'expr': 'input(200)', 'conditions': []}, {'mode': '', 'name': 'StopLossPerc', 'op': '=', 'expr': 'input(.95, step=0.01)', 'conditions': []}, {'mode': '', 'name': 'buyTime', 'op': '=', 'expr': 'time(timeframe.period, "1429-1500")', 'conditions': []}, {'mode': '', 'name': 'sellTime', 'op': '=', 'expr': 'time(timeframe.period, "0925-0935")', 'conditions': []}, {'mode': '', 'name': 'F1', 'op': '=', 'expr': 'close > sma(security(syminfo.tickerid, "D", close[2]), MarketFilterLen) // HIGH OF OLD DATA -- SO NO REPAINTING', 'conditions': []}, {'mode': '', 'name': 'enter', 'op': '=', 'expr': 'buyTime and F1', 'conditions': []}, {'mode': '', 'name': 'exit', 'op': '=', 'expr': 'sellTime', 'conditions': []}, {'mode': '', 'name': 'StopLossLine', 'op': '=', 'expr': 'strategy.position_avg_price * StopLossPerc', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if close > strategy.position_avg_price'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("L", true, when=enter)', 'conditions': [], 'statement': 'strategy.entry("L", true, when=enter)'}, {'kind': 'exit', 'call': 'strategy.exit("StopLoss", stop=StopLossLine )', 'conditions': [], 'statement': 'strategy.exit("StopLoss", stop=StopLossLine )'}, {'kind': 'close', 'call': 'strategy.close("L", when=exit)', 'conditions': ['close > strategy.position_avg_price'], 'statement': 'strategy.close("L", when=exit)'}]
    original_pine = '/*backtest\nstart: 2022-12-27 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//  @version=4\n//  © HermanBrummer\n//  This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\nstrategy("M8 BUY @ END OF DAY", "", 1)\n\n///         BUYS AT THE END OF THE DAY\n///         SELLS THE NEXT MORNING IF PRICE IS HIGHER THEN THE ENTRY PRICE\n///         IF PRICE IS NOT HIGHER THEN IT WILL KEEP THE POSITION AND WAIT FOR EITHER A STOP OUT OR FOR PRICE TO BE HIGHER THAN THE ENTRY\n///         USES A 5% STOP LOSS ON THE REDLINE  -- SETTABLE IN SETTINGS\n///         USES A 200 DAY MARKET FILTER        -- SETTABLE IN SETTINGS -- IMPORTS DATA FROM HIGHER TIMEFRAME, BUT USES CLOSE[2] << SO THIS IS FIXED, NON-REPAITING DATA\n\n\nMarketFilterLen = input(200)\nStopLossPerc    = input(.95, step=0.01)\n\nbuyTime         = time(timeframe.period, "1429-1500")\nsellTime        = time(timeframe.period, "0925-0935")\n\nF1              = close > sma(security(syminfo.tickerid, "D", close[2]), MarketFilterLen) // HIGH OF OLD DATA -- SO NO REPAINTING\n\nenter           = buyTime and F1\nexit            = sellTime\n\n\nStopLossLine    = strategy.position_avg_price * StopLossPerc\n\nplot(StopLossLine, "StopLossLine", color.new(#FF0000, 50))\n\nstrategy.entry("L", true, when=enter)\nstrategy.exit("StopLoss", stop=StopLossLine )\nif  close > strategy.position_avg_price\n    strategy.close("L", when=exit)\n\nbarcolor(strategy.opentrades != 0 ? color.new(color.yellow, 0) : na )'

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
