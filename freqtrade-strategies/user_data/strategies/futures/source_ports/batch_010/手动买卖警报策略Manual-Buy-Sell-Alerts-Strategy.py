"""Source-faithful deep-assisted port of 手动买卖警报策略Manual-Buy-Sell-Alerts-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_7ae75843(PinePortBase, IStrategy):
    source_file = '手动买卖警报策略Manual-Buy-Sell-Alerts-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'sTime': 'timestamp("2020-01-01")', 'eTime': 'timestamp("2030-01-01")', 'buy_type': 'stop', 'buy_price': 49000, 'target_price': 51000, 'stop_price': 47000, 'AlertLong': 'Buy message', 'AlertExit': 'Sell message'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 1
    source_initial_capital = 10000.0
    source_commission_percent = 0.1
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.position_size', 'strategy.equity', 'alert']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'title_name', 'op': '=', 'expr': "'Manual Buy & Sell Alerts'", 'conditions': []}, {'mode': '', 'name': 'sTime', 'op': '=', 'expr': 'input(timestamp("2020-01-01"), "Start", group="Period", inline=\'1\')', 'conditions': []}, {'mode': '', 'name': 'eTime', 'op': '=', 'expr': 'input(timestamp("2030-01-01"), "End", group="Period", inline=\'2\')', 'conditions': []}, {'mode': '', 'name': 'inDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'buy_type', 'op': '=', 'expr': "input.string('stop', 'Buy Type', group='Buy&Sell', inline='1', options=['stop', 'limit'])", 'conditions': []}, {'mode': '', 'name': 'buy_price', 'op': '=', 'expr': "input.float(49000, 'Buy Price', group='Buy&Sell', inline='1')", 'conditions': []}, {'mode': '', 'name': 'target_price', 'op': '=', 'expr': "input.float(51000, 'Target Price', group='Buy&Sell', inline='2')", 'conditions': []}, {'mode': '', 'name': 'stop_price', 'op': '=', 'expr': "input.float(47000, 'Stop Price', group='Buy&Sell', inline='2')", 'conditions': []}, {'mode': '', 'name': 'avg_price', 'op': '=', 'expr': 'strategy.position_avg_price', 'conditions': []}, {'mode': '', 'name': 'division', 'op': '=', 'expr': '1', 'conditions': []}, {'mode': '', 'name': 'AlertLong', 'op': '=', 'expr': 'input.string("Buy message", "Buy Alert Message", group=\'Alert set-up\', inline=\'1\')', 'conditions': []}, {'mode': '', 'name': 'AlertExit', 'op': '=', 'expr': 'input.string("Sell message", "Sell Alert Message", group=\'Alert set-up\', inline=\'1\')', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'inDateRange and strategy.position_size == 0', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': "if longCondition and buy_type == 'stop'"}, {'indent': 0, 'statement': "if longCondition and buy_type == 'limit'"}]
    pine_orders = [{'kind': 'exit', 'call': 'strategy.exit("sell", "buy", limit=target_price, stop=stop_price, alert_message=AlertExit)', 'conditions': [], 'statement': 'strategy.exit("sell", "buy", limit=target_price, stop=stop_price, alert_message=AlertExit)'}, {'kind': 'entry', 'call': 'strategy.entry("buy", strategy.long, qty=posSize, stop=buy_price, when=close < buy_price, comment="buy_STOP", alert_message=AlertLong)', 'conditions': ["longCondition and buy_type == 'stop'"], 'statement': 'strategy.entry("buy", strategy.long, qty=posSize, stop=buy_price, when=close < buy_price, comment="buy_STOP", alert_message=AlertLong)'}, {'kind': 'entry', 'call': 'strategy.entry("buy", strategy.long, qty=posSize, limit=buy_price, when=close > buy_price, comment="buy_LIMIT", alert_message=AlertLong)', 'conditions': ["longCondition and buy_type == 'limit'"], 'statement': 'strategy.entry("buy", strategy.long, qty=posSize, limit=buy_price, when=close > buy_price, comment="buy_LIMIT", alert_message=AlertLong)'}]
    original_pine = '/*backtest\nstart: 2024-01-21 00:00:00\nend: 2024-02-20 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © MGTG\n\ntitle_name = \'Manual Buy & Sell Alerts\'\n\n//@version=5\nstrategy(\n title=title_name, overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, \n pyramiding=1, commission_type=strategy.commission.percent, commission_value=0.1)\n\n// Period\nsTime         = input(timestamp("2020-01-01"), "Start", group="Period", inline=\'1\')\neTime         = input(timestamp("2030-01-01"), "End", group="Period", inline=\'2\')\ninDateRange   = true\n\n// Bot Set-up\nbuy_type = input.string(\'stop\', \'Buy Type\', group=\'Buy&Sell\', inline=\'1\', options=[\'stop\', \'limit\'])\nbuy_price = input.float(49000, \'Buy Price\', group=\'Buy&Sell\', inline=\'1\')\n\ntarget_price = input.float(51000, \'Target Price\', group=\'Buy&Sell\', inline=\'2\')\nstop_price = input.float(47000, \'Stop Price\', group=\'Buy&Sell\', inline=\'2\')\navg_price = strategy.position_avg_price\ndivision = 1\n\n// Alert message\nAlertLong=input.string("Buy message", "Buy Alert Message",  group=\'Alert set-up\', inline=\'1\')\nAlertExit=input.string("Sell message", "Sell Alert Message",  group=\'Alert set-up\', inline=\'1\')\n\nplot(buy_price, \'Buy Price\', color=color.new(#009688, 0), style=plot.style_linebr, offset=1)\nplot(target_price, \'Take Profit\', color=color.new(color.orange, 0), style=plot.style_linebr, offset=1)\nplot(stop_price, \'Safety\', color=color.new(color.aqua, 0), style=plot.style_linebr, offset=1)\n\nposSize = \n strategy.equity / close\n\nstrategy.exit("sell", "buy", limit=target_price, stop=stop_price, alert_message=AlertExit)\n\nlongCondition = inDateRange and strategy.position_size == 0\nif longCondition and buy_type == \'stop\'\n    strategy.entry("buy", strategy.long, qty=posSize, stop=buy_price, when=close < buy_price, comment="buy_STOP", alert_message=AlertLong)\n\nif longCondition and buy_type == \'limit\'\n    strategy.entry("buy", strategy.long, qty=posSize, limit=buy_price, when=close > buy_price, comment="buy_LIMIT", alert_message=AlertLong)'

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
