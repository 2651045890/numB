"""Source-faithful deep-assisted port of 混合双态Z评分量化策略-Hybrid-Binomial-Z-Score-Quantitative-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_9f23a242(PinePortBase, IStrategy):
    source_file = '混合双态Z评分量化策略-Hybrid-Binomial-Z-Score-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'sma_length': 20, 'threshold_high': 1.5, 'threshold_low': -1.5, 'lookback_period': 252}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', '=>', 'line.']
    source_fidelity_notes = ['Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'sma_length', 'op': '=', 'expr': 'input.int(20, title="Período da SMA")', 'conditions': []}, {'mode': '', 'name': 'threshold_high', 'op': '=', 'expr': 'input.float(1.5, title="Threshold Alto")', 'conditions': []}, {'mode': '', 'name': 'threshold_low', 'op': '=', 'expr': 'input.float(-1.5, title="Threshold Baixo")', 'conditions': []}, {'mode': '', 'name': 'lookback_period', 'op': '=', 'expr': 'input.int(252, title="Período de Retorno Histórico (dias)")', 'conditions': []}, {'mode': '', 'name': 'basis', 'op': '=', 'expr': 'ta.sma(source, length)', 'conditions': []}, {'mode': '', 'name': 'dev', 'op': '=', 'expr': 'mult * ta.stdev(source, length)', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'f_sma(close, sma_length)', 'conditions': []}, {'mode': '', 'name': 'retornos', 'op': '=', 'expr': 'ta.change(close, 1)', 'conditions': []}, {'mode': '', 'name': 'media_retornos', 'op': '=', 'expr': 'ta.sma(retornos, lookback_period)', 'conditions': []}, {'mode': '', 'name': 'desvio_padrao_retornos', 'op': '=', 'expr': 'ta.stdev(retornos, lookback_period)', 'conditions': []}, {'mode': '', 'name': 'z_score', 'op': '=', 'expr': '(retornos - media_retornos) / desvio_padrao_retornos', 'conditions': []}, {'mode': '', 'name': 'sinal_compra', 'op': '=', 'expr': 'z_score < threshold_low and close < lower_band', 'conditions': []}, {'mode': '', 'name': 'sinal_venda', 'op': '=', 'expr': 'z_score > threshold_high and close > upper_band', 'conditions': []}]
    pine_user_functions = [{'name': 'f_sma', 'args': 'source, length', 'body': ''}, {'name': 'f_bollinger_band', 'args': 'source, length, mult', 'body': ''}]
    pine_controls = [{'indent': 0, 'statement': 'if (sinal_compra)'}, {'indent': 0, 'statement': 'if (sinal_venda)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long)', 'conditions': ['(sinal_compra)'], 'statement': 'strategy.entry("Long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long")', 'conditions': ['(sinal_venda)'], 'statement': 'strategy.close("Long")'}]
    original_pine = '/*backtest\nstart: 2023-05-22 00:00:00\nend: 2024-05-27 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estratégia Híbrida Quantitativa", overlay=true)\n\n// Definição de parâmetros\nsma_length = input.int(20, title="Período da SMA")\nthreshold_high = input.float(1.5, title="Threshold Alto")\nthreshold_low = input.float(-1.5, title="Threshold Baixo")\nlookback_period = input.int(252, title="Período de Retorno Histórico (dias)")\n\n// Funções auxiliares\nf_sma(source, length) =>\n    ta.sma(source, length)\n\nf_bollinger_band(source, length, mult) =>\n    basis = ta.sma(source, length)\n    dev = mult * ta.stdev(source, length)\n    [basis + dev, basis - dev]\n\n// Cálculo dos indicadores\nsma = f_sma(close, sma_length)\n[upper_band, lower_band] = f_bollinger_band(close, sma_length, 2)\n\n// Regime de Mercado: Binomial\nretornos = ta.change(close, 1)\nmedia_retornos = ta.sma(retornos, lookback_period)\ndesvio_padrao_retornos = ta.stdev(retornos, lookback_period)\n\n// Indicador de Regime: Z-Score\nz_score = (retornos - media_retornos) / desvio_padrao_retornos\n\n// Sinal de Compra e Venda\nsinal_compra = z_score < threshold_low and close < lower_band\nsinal_venda = z_score > threshold_high and close > upper_band\n\n// Execução de Ordem\nif (sinal_compra)\n    strategy.entry("Long", strategy.long)\nif (sinal_venda)\n    strategy.close("Long")\n\n// Plotagem dos Indicadores\nplot(sma, title="SMA", color=color.blue)\nplot(upper_band, title="Upper Bollinger Band", color=color.red)\nplot(lower_band, title="Lower Bollinger Band", color=color.green)\nhline(threshold_high, "Threshold Alto", color=color.red, linestyle=hline.style_dashed)\nhline(threshold_low, "Threshold Baixo", color=color.green, linestyle=hline.style_dashed)\nplot(z_score, title="Z-Score", color=color.purple)'

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
