"""Source-faithful deep-assisted port of 拉里威廉姆斯三周期动态均线交易策略-Larry-Williams-Three-Period-Dynamic-Moving-Average-Trading-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_cab35184(PinePortBase, IStrategy):
    source_file = '拉里威廉姆斯三周期动态均线交易策略-Larry-Williams-Three-Period-Dynamic-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'emaPeriodHighs': 3, 'emaPeriodLows': 3, 'startYear': 2020, 'startMonth': 1, 'startDay': 1, 'endYear': 2020, 'endMonth': 12, 'endDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'strategy.position_size', 'barstate.']
    source_fidelity_notes = ['Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'emaPeriodHighs', 'op': '=', 'expr': 'input.int(title="Highs Period", defval=3, minval=1, maxval=9999)', 'conditions': []}, {'mode': '', 'name': 'emaPeriodLows', 'op': '=', 'expr': 'input.int(title="Lows Period", defval=3, minval=1, maxval=9999)', 'conditions': []}, {'mode': '', 'name': 'startYear', 'op': '=', 'expr': 'input.int(title="Start Year", defval=2020)', 'conditions': []}, {'mode': '', 'name': 'startMonth', 'op': '=', 'expr': 'input.int(title="Start Month", defval=1, minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'startDay', 'op': '=', 'expr': 'input.int(title="Start Day", defval=1, minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'endYear', 'op': '=', 'expr': 'input.int(title="End Year", defval=2020)', 'conditions': []}, {'mode': '', 'name': 'endMonth', 'op': '=', 'expr': 'input.int(title="End Month", defval=12, minval=1, maxval=12)', 'conditions': []}, {'mode': '', 'name': 'endDay', 'op': '=', 'expr': 'input.int(title="End Day", defval=31, minval=1, maxval=31)', 'conditions': []}, {'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'timestamp(startYear, startMonth, startDay, 00, 00)', 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': 'timestamp(endYear, endMonth, endDay, 23, 59)', 'conditions': []}, {'mode': '', 'name': 'emaH', 'op': '=', 'expr': 'ta.ema(high, emaPeriodHighs)', 'conditions': []}, {'mode': '', 'name': 'emaL', 'op': '=', 'expr': 'ta.ema(low, emaPeriodLows)', 'conditions': []}, {'mode': '', 'name': 'inDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'checkThreeConsecutiveCandles', 'op': '=', 'expr': '(close[0] > close[1] and close[1] > close[2] and close[2] > close[3]) or (close[0] < close[1] and close[1] < close[2] and close[2] < close[3])', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(close < emaL and inDateRange and checkThreeConsecutiveCandles and barstate.isconfirmed)'}, {'indent': 0, 'statement': 'if(close > emaH and inDateRange and checkThreeConsecutiveCandles and barstate.isconfirmed)'}, {'indent': 0, 'statement': 'if(strategy.position_size > 0 and na(time_close[0]))'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, comment="Long", when=strategy.position_size == 0)', 'conditions': [], 'statement': 'strategy.entry("Long", strategy.long, comment="Long", when=strategy.position_size == 0)'}, {'kind': 'close', 'call': 'strategy.close("Long", comment="Close Long")', 'conditions': [], 'statement': 'strategy.close("Long", comment="Close Long")'}, {'kind': 'close', 'call': 'strategy.close("Long", comment="Close Long")', 'conditions': [], 'statement': 'strategy.close("Long", comment="Close Long")'}]
    original_pine = '/*backtest\nstart: 2023-05-05 00:00:00\nend: 2024-05-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Larry Williams 3 Periodos Editável de MarcosJr", overlay=true, process_orders_on_close=true)\n\n// Parametrização do período do EMA\nemaPeriodHighs = input.int(title="Highs Period", defval=3, minval=1, maxval=9999)\nemaPeriodLows = input.int(title="Lows Period", defval=3, minval=1, maxval=9999)\n\n// Parametrização da data de início e fim do período a ser coletado\nstartYear = input.int(title="Start Year", defval=2020)\nstartMonth = input.int(title="Start Month", defval=1, minval=1, maxval=12)\nstartDay = input.int(title="Start Day", defval=1, minval=1, maxval=31)\n\nendYear = input.int(title="End Year", defval=2020)\nendMonth = input.int(title="End Month", defval=12, minval=1, maxval=12)\nendDay = input.int(title="End Day", defval=31, minval=1, maxval=31)\n\n// Convertendo data de início e fim para timestamp\nstartDate = timestamp(startYear, startMonth, startDay, 00, 00)\nendDate = timestamp(endYear, endMonth, endDay, 23, 59)\n\n// EMA\nemaH = ta.ema(high, emaPeriodHighs)\nemaL = ta.ema(low, emaPeriodLows)\n\n// PLOT:\n// Desenha as linhas EMA no gráfico\nplot(emaH, color=color.green, linewidth=2)\nplot(emaL, color=color.red, linewidth=2)\n\n// Condições\ninDateRange = true\n\n// Verifica se houve mais de três candles consecutivos do mesmo sentido\ncheckThreeConsecutiveCandles = (close[0] > close[1] and close[1] > close[2] and close[2] > close[3]) or (close[0] < close[1] and close[1] < close[2] and close[2] < close[3])\n\nif(close < emaL and inDateRange and checkThreeConsecutiveCandles and barstate.isconfirmed)\n    strategy.entry("Long", strategy.long, comment="Long", when=strategy.position_size == 0)\nif(close > emaH and inDateRange and checkThreeConsecutiveCandles and barstate.isconfirmed)\n    strategy.close("Long", comment="Close Long")\n\n// Fechar a operação no fechamento do pregão\nif(strategy.position_size > 0 and na(time_close[0]))\n    strategy.close("Long", comment="Close Long")'

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
