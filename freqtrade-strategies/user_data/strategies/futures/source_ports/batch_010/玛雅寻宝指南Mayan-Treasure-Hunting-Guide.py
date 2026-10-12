"""Source-faithful deep-assisted port of 玛雅寻宝指南Mayan-Treasure-Hunting-Guide.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_16476b64(PinePortBase, IStrategy):
    source_file = '玛雅寻宝指南Mayan-Treasure-Hunting-Guide.md'
    timeframe = '4h'
    can_short = True
    source_defaults = {'length': 20, 'src': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(20, minval=1, title="Length")', 'conditions': []}, {'mode': '', 'name': 'src', 'op': '=', 'expr': 'input(close, title="Source")', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.ema(src, length)', 'conditions': []}, {'mode': '', 'name': 'last8h', 'op': '=', 'expr': 'ta.highest(close, 8)', 'conditions': []}, {'mode': '', 'name': 'lastl8', 'op': '=', 'expr': 'ta.lowest(close, 8)', 'conditions': []}, {'mode': '', 'name': 'buy_condition', 'op': '=', 'expr': 'ta.cross(close, ema) == 1 and close[1] < close', 'conditions': []}, {'mode': '', 'name': 'sell_condition', 'op': '=', 'expr': 'ta.cross(close, ema) == 1 and close[1] > close', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=buy_condition)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=buy_condition)'}, {'kind': 'entry', 'call': 'strategy.entry("Sell", strategy.short, when=sell_condition)', 'conditions': [], 'statement': 'strategy.entry("Sell", strategy.short, when=sell_condition)'}]
    original_pine = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 23:59:59\nperiod: 4h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © alex-aftc\n\n\n//@version=5\nstrategy("Megalodon", shorttitle="Megalodon", overlay=true)\n\n// Parámetros de la EMA\nlength = input.int(20, minval=1, title="Length")\nsrc = input(close, title="Source")\n\n// Calcular la EMA\nema = ta.ema(src, length)\n\n// Plot de la EMA\nplot(ema, title="EMA", color=color.blue)\n\n// Encontrar los puntos más altos y más bajos\nlast8h = ta.highest(close, 8)\nlastl8 = ta.lowest(close, 8)\n\n// Plot de los puntos más altos y más bajos\nplot(last8h, color=color.red, linewidth=2)\nplot(lastl8, color=color.green, linewidth=2)\n\n// Condiciones de compra y venta\nbuy_condition = ta.cross(close, ema) == 1 and close[1] < close\nsell_condition = ta.cross(close, ema) == 1 and close[1] > close\n\n// Estrategia de trading\nstrategy.entry("Buy", strategy.long, when=buy_condition)\nstrategy.entry("Sell", strategy.short, when=sell_condition)'

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
