"""Source-faithful deep-assisted port of 布林带跨度交易策略Bollinger-Band-Breakout-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_56630aa0(PinePortBase, IStrategy):
    source_file = '布林带跨度交易策略Bollinger-Band-Breakout-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'leverage': 1, 'TP_Factor': 2, 'invertBuyLogic': False, 'lookbackDistance': 25, 'devMult': 2}
    source_qty_type = 'cash'
    source_qty_value = 1000000.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'var ']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'leverage', 'op': '=', 'expr': 'input.float(1,"Leverage (x)",step=1)', 'conditions': []}, {'mode': '', 'name': 'SL_Factor', 'op': '=', 'expr': '1 - input.float(1,"Risk Capital per Trade (%)", minval=0.1, maxval=100, step=0.05) / 100 / leverage', 'conditions': []}, {'mode': '', 'name': 'TP_Factor', 'op': '=', 'expr': 'input.float(2, step=0.1)', 'conditions': []}, {'mode': '', 'name': 'invertBuyLogic', 'op': '=', 'expr': 'input.bool(false)', 'conditions': []}, {'mode': '', 'name': 'lookbackDistance', 'op': '=', 'expr': 'input.int(25)', 'conditions': []}, {'mode': '', 'name': 'devMult', 'op': '=', 'expr': 'input.float(2,step=0.1)', 'conditions': []}, {'mode': 'var', 'name': 'lastSellHour', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': 'var', 'name': 'disableAdditionalBuysThisDay', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'disableAdditionalBuysThisDay', 'op': ':=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'disableAdditionalBuysThisDay', 'op': ':=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'lastSellHour', 'op': ':=', 'expr': 'time', 'conditions': []}, {'mode': '', 'name': 'source', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(source, lookbackDistance)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'devMult * ta.stdev(source, lookbackDistance)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': 'basis + dev', 'conditions': []}, {'mode': '', 'name': 'lower', 'op': '=', 'expr': 'basis - dev', 'conditions': []}, {'mode': '', 'name': 'isBuy', 'op': '=', 'expr': 'ta.crossunder(source, upper)', 'conditions': []}, {'mode': '', 'name': 'isBuyInverted', 'op': '=', 'expr': 'ta.crossover(source, lower)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(time > lastSellHour + 1000 * 60 * 60 * 6)'}, {'indent': 0, 'statement': 'if(strategy.position_size != strategy.position_size[1])'}, {'indent': 0, 'statement': 'if((invertBuyLogic ? isBuyInverted : isBuy) and not(disableAdditionalBuysThisDay))'}, {'indent': 0, 'statement': 'if(strategy.position_size > 0)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, (strategy.initial_capital / close) * leverage)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, (strategy.initial_capital / close) * leverage)'}, {'kind': 'exit', 'call': 'strategy.exit("SL Long", "Long", stop=strategy.position_avg_price * SL_Factor)', 'conditions': [], 'statement': 'strategy.exit("SL Long", "Long", stop=strategy.position_avg_price * SL_Factor)'}, {'kind': 'close', 'call': 'strategy.close("Long", when=close > strategy.position_avg_price * (1 + (1 - SL_Factor) * TP_Factor), comment="TP Long")', 'conditions': [], 'statement': 'strategy.close("Long", when=close > strategy.position_avg_price * (1 + (1 - SL_Factor) * TP_Factor), comment="TP Long")'}]
    original_pine = '/*backtest\nstart: 2023-11-18 00:00:00\nend: 2023-12-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("I11L OIL Bot",overlay=true, initial_capital=1000000,default_qty_value=1000000,default_qty_type=strategy.cash,commission_type=strategy.commission.percent,commission_value=0.00)\n\nleverage = input.float(1,"Leverage (x)",step=1)\nSL_Factor = 1 - input.float(1,"Risk Capital per Trade (%)", minval=0.1, maxval=100, step=0.05) / 100 / leverage\nTP_Factor = input.float(2, step=0.1)\ninvertBuyLogic = input.bool(false)\n \nlookbackDistance = input.int(25)\ndevMult = input.float(2,step=0.1)\n\nvar lastSellHour = 0\nvar disableAdditionalBuysThisDay = false\n\n\nif(time > lastSellHour + 1000 * 60 * 60 * 6)\n    disableAdditionalBuysThisDay := false\nif(strategy.position_size != strategy.position_size[1])\n    disableAdditionalBuysThisDay := true\n    lastSellHour := time\n\nsource = close\n\n//Trade Logic\nbasis = ta.sma(source, lookbackDistance)\ndev = devMult * ta.stdev(source, lookbackDistance)\nupper = basis + dev\nlower = basis - dev\nisBuy = ta.crossunder(source, upper)\nisBuyInverted = ta.crossover(source, lower)\n\nplot(upper, color=color.white)\nplot(lower, color=color.white)\n\nstrategy.initial_capital = 50000\n\nif((invertBuyLogic ? isBuyInverted : isBuy) and not(disableAdditionalBuysThisDay))\n    strategy.entry("Long", strategy.long, (strategy.initial_capital / close) * leverage)\n\nif(strategy.position_size > 0)\n    strategy.exit("SL Long", "Long", stop=strategy.position_avg_price * SL_Factor)\n    strategy.close("Long",  when=close > strategy.position_avg_price * (1 + (1 - SL_Factor) * TP_Factor), comment="TP Long")'

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
