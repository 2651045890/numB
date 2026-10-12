"""Source-faithful deep-assisted port of 渦轮指标结合RSI的股票多头交易策略Vortex-and-RSI-Stock-Long-only-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_2a66b700(PinePortBase, IStrategy):
    source_file = '渦轮指标结合RSI的股票多头交易策略Vortex-and-RSI-Stock-Long-only-Trading-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'n': 14, 'm': 14, 'stop_loss': 7, 'Target_profit': 16}
    source_qty_type = 'cash'
    source_qty_value = 20000.0
    source_pyramiding = 0
    source_initial_capital = 20000.0
    source_commission_percent = 0.25
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'n', 'op': '=', 'expr': 'input(title="vortex period",type=input.integer, defval = 14)', 'conditions': []}, {'mode': '', 'name': 'm', 'op': '=', 'expr': 'input(title = "RSI period", type=input.integer, defval = 14)', 'conditions': []}, {'mode': '', 'name': 'VMP', 'op': '=', 'expr': 'sum( abs( high - low[1]), n )', 'conditions': []}, {'mode': '', 'name': 'VMM', 'op': '=', 'expr': 'sum( abs( low - high[1]), n )', 'conditions': []}, {'mode': '', 'name': 'STR', 'op': '=', 'expr': 'sum( atr(1), n )', 'conditions': []}, {'mode': '', 'name': 'VIP', 'op': '=', 'expr': 'VMP / STR', 'conditions': []}, {'mode': '', 'name': 'VIM', 'op': '=', 'expr': 'VMM / STR', 'conditions': []}, {'mode': '', 'name': 'totalprice', 'op': '=', 'expr': '(high + low+close + open)/4', 'conditions': []}, {'mode': '', 'name': 'myrsi', 'op': '=', 'expr': 'rsi(m, totalprice)', 'conditions': []}, {'mode': '', 'name': 'entryl', 'op': '=', 'expr': 'crossover(VIP, VIM) and close >= high[1]', 'conditions': []}, {'mode': '', 'name': 'exit1', 'op': '=', 'expr': 'crossover(VIM, VIP) and close <= low[1]', 'conditions': []}, {'mode': '', 'name': 'exit2', 'op': '=', 'expr': 'crossunder(myrsi, 70)', 'conditions': []}, {'mode': '', 'name': 'stop_loss', 'op': '=', 'expr': 'input(7, "Stop loss %", minval = 1, step = 1)', 'conditions': []}, {'mode': '', 'name': 'sl', 'op': '=', 'expr': '-1*stop_loss/100*strategy.initial_capital', 'conditions': []}, {'mode': '', 'name': 'close_Stop', 'op': '=', 'expr': 'strategy.openprofit < sl', 'conditions': []}, {'mode': '', 'name': 'Target_profit', 'op': '=', 'expr': 'input(16, "Target Profit %", minval = 1, step = 1)', 'conditions': []}, {'mode': '', 'name': 'tp', 'op': '=', 'expr': 'Target_profit/100*strategy.initial_capital', 'conditions': []}, {'mode': '', 'name': 'close_Target', 'op': '=', 'expr': 'strategy.openprofit > tp', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", true, when=entryl, comment = "Go!")', 'conditions': [], 'statement': 'strategy.entry("Long", true, when=entryl, comment = "Go!")'}, {'kind': 'close', 'call': 'strategy.close("Long", when=exit1, comment = "Vortex down")', 'conditions': [], 'statement': 'strategy.close("Long", when=exit1, comment = "Vortex down")'}, {'kind': 'close', 'call': 'strategy.close("Long", when=exit2, comment = "RSI down")', 'conditions': [], 'statement': 'strategy.close("Long", when=exit2, comment = "RSI down")'}, {'kind': 'close', 'call': 'strategy.close("Long", when = close_Stop)', 'conditions': [], 'statement': 'strategy.close("Long", when = close_Stop)'}, {'kind': 'close', 'call': 'strategy.close("Long", when = close_Target)', 'conditions': [], 'statement': 'strategy.close("Long", when = close_Target)'}]
    original_pine = '/*backtest\nstart: 2023-08-19 00:00:00\nend: 2023-09-18 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n////////////////////////////////////////////////////////////\n//  Copyright by Sauciusfinance \n////////////////////////////////////////////////////////////\nstrategy(title="Vortex and RSI ts 2020",calc_on_order_fills=true,calc_on_every_tick =true, initial_capital=20000,commission_value=.25,overlay = true,default_qty_type = strategy.cash, default_qty_value = 20000)\n//inputs////////////////////////\nn = input(title="vortex period",type=input.integer, defval = 14)\nm = input(title = "RSI period", type=input.integer, defval = 14)\n// CALCULATIONS *** ///////\nVMP = sum( abs( high - low[1]), n )\nVMM = sum( abs( low - high[1]), n )\nSTR = sum( atr(1), n )\nVIP = VMP / STR\nVIM = VMM / STR\n// bring the lines in the panel below, add another panel with RSI\nplot(VIP, title="VI +", color=#311B92)\nplot(VIM, title="VI -", color=#FF006E)\n\n// RSI on total price, always\ntotalprice = (high + low+close + open)/4\nmyrsi = rsi(m, totalprice)\nstrategy.initial_capital = 50000\n//// TRADING SYSTEM CODE //// \nentryl = crossover(VIP, VIM) and close >= high[1] \nstrategy.entry("Long", true, when=entryl, comment = "Go!")\nexit1 = crossover(VIM, VIP) and close <= low[1]\nstrategy.close("Long", when=exit1, comment = "Vortex down")\nexit2 = crossunder(myrsi, 70)\nstrategy.close("Long", when=exit2, comment = "RSI down")\n//money management\nstop_loss=input(7, "Stop loss %", minval = 1, step = 1)\nsl = -1*stop_loss/100*strategy.initial_capital\nclose_Stop = strategy.openprofit < sl\nstrategy.close("Long", when = close_Stop)\nTarget_profit=input(16, "Target Profit %", minval = 1, step = 1)\ntp = Target_profit/100*strategy.initial_capital\nclose_Target = strategy.openprofit > tp\nstrategy.close("Long", when = close_Target)'

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
