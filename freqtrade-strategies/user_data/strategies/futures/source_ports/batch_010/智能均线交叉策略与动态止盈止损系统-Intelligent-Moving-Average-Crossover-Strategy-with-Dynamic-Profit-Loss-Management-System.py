"""Source-faithful deep-assisted port of 智能均线交叉策略与动态止盈止损系统-Intelligent-Moving-Average-Crossover-Strategy-with-Dynamic-Profit-Loss-Management-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_bcce8376(PinePortBase, IStrategy):
    source_file = '智能均线交叉策略与动态止盈止损系统-Intelligent-Moving-Average-Crossover-Strategy-with-Dynamic-Profit-Loss-Management-System.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'periodo_ma7': 7, 'periodo_ma40': 40, 'stop_loss_pct': 1, 'take_profit_pct': 2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry', 'strategy.close', 'strategy.position_size']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'periodo_ma7', 'op': '=', 'expr': 'input.int(7, title="Período da Média Móvel 7", minval=1)', 'conditions': []}, {'mode': '', 'name': 'periodo_ma40', 'op': '=', 'expr': 'input.int(40, title="Período da Média Móvel 40", minval=1)', 'conditions': []}, {'mode': '', 'name': 'ma7', 'op': '=', 'expr': 'ta.sma(close, periodo_ma7)', 'conditions': []}, {'mode': '', 'name': 'ma40', 'op': '=', 'expr': 'ta.sma(close, periodo_ma40)', 'conditions': []}, {'mode': '', 'name': 'stop_loss_pct', 'op': '=', 'expr': 'input.float(1, title="Stop Loss (%)", minval=0.1) / 100', 'conditions': []}, {'mode': '', 'name': 'take_profit_pct', 'op': '=', 'expr': 'input.float(2, title="Take Profit (%)", minval=0.1) / 100', 'conditions': []}, {'mode': '', 'name': 'compra', 'op': '=', 'expr': 'ta.crossover(ma7, ma40)', 'conditions': []}, {'mode': '', 'name': 'venda', 'op': '=', 'expr': 'ta.crossunder(ma7, ma40)', 'conditions': []}, {'mode': '', 'name': 'stop_loss_price', 'op': '=', 'expr': 'strategy.position_avg_price * (1 - stop_loss_pct)', 'conditions': []}, {'mode': '', 'name': 'take_profit_price', 'op': '=', 'expr': 'strategy.position_avg_price * (1 + take_profit_pct)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (compra and strategy.position_size == 0)'}, {'indent': 0, 'statement': 'if (venda)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Compra", strategy.long)', 'conditions': ['(compra and strategy.position_size == 0)'], 'statement': 'strategy.entry("Compra", strategy.long)'}, {'kind': 'exit', 'call': 'strategy.exit("Saída", from_entry="Compra", stop=stop_loss_price, limit=take_profit_price)', 'conditions': [], 'statement': 'strategy.exit("Saída", from_entry="Compra", stop=stop_loss_price, limit=take_profit_price)'}, {'kind': 'close', 'call': 'strategy.close("Compra")', 'conditions': ['(venda)'], 'statement': 'strategy.close("Compra")'}]
    original_pine = '/*backtest\nstart: 2024-12-10 00:00:00\nend: 2025-01-08 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Cruzamento de Médias Móveis (Configuração Interativa)", overlay=true)\n\n// Permite que o usuário defina os períodos das médias móveis na interface\nperiodo_ma7 = input.int(7, title="Período da Média Móvel 7", minval=1)\nperiodo_ma40 = input.int(40, title="Período da Média Móvel 40", minval=1)\n\n// Definindo as médias móveis com os períodos configuráveis\nma7 = ta.sma(close, periodo_ma7)\nma40 = ta.sma(close, periodo_ma40)\n\n// Parâmetros de stop loss e take profit\nstop_loss_pct = input.float(1, title="Stop Loss (%)", minval=0.1) / 100\ntake_profit_pct = input.float(2, title="Take Profit (%)", minval=0.1) / 100\n\n// Condições para compra e venda\ncompra = ta.crossover(ma7, ma40)\nvenda = ta.crossunder(ma7, ma40)\n\n// Impede novas entradas enquanto já houver uma posição aberta\nif (compra and strategy.position_size == 0)\n    strategy.entry("Compra", strategy.long)\n\n// Cálculo do preço de stop loss e take profit\nstop_loss_price = strategy.position_avg_price * (1 - stop_loss_pct)\ntake_profit_price = strategy.position_avg_price * (1 + take_profit_pct)\n\n// Estratégia de saída com stop loss e take profit\nstrategy.exit("Saída", from_entry="Compra", stop=stop_loss_price, limit=take_profit_price)\n\n// Sinal de venda (fechamento da posição)\nif (venda)\n    strategy.close("Compra")\n\n// Plotando as médias móveis no gráfico\nplot(ma7, color=color.blue, title="Média Móvel 7")\nplot(ma40, color=color.red, title="Média Móvel 40")\n\n// Plotando o Stop Loss e Take Profit no gráfico\nplot(stop_loss_price, color=color.red, style=plot.style_line, linewidth=2, title="Stop Loss")\nplot(take_profit_price, color=color.green, style=plot.style_line, linewidth=2, title="Take Profit")'

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
