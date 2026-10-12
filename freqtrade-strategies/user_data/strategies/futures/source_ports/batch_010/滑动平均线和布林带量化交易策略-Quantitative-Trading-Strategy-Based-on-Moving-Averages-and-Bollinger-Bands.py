"""Source-faithful deep-assisted port of 滑动平均线和布林带量化交易策略-Quantitative-Trading-Strategy-Based-on-Moving-Averages-and-Bollinger-Bands.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_27b20ca7(PinePortBase, IStrategy):
    source_file = '滑动平均线和布林带量化交易策略-Quantitative-Trading-Strategy-Based-on-Moving-Averages-and-Bollinger-Bands.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'n_slow': 50, 'n_fast': 4, 'n_deviation': 30, 'k_deviation_open': 1.2, 'k_deviation_close': 1.6}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'result', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'result', 'op': ':=', 'expr': 'result + price [i] / n', 'conditions': []}, {'mode': '', 'name': 'result', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'sum_weight', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'weight', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'weight', 'op': ':=', 'expr': 'n - 1', 'conditions': []}, {'mode': '', 'name': 'result', 'op': ':=', 'expr': 'result + price [i]*weight', 'conditions': []}, {'mode': '', 'name': 'sum_weight', 'op': ':=', 'expr': 'sum_weight + weight', 'conditions': []}, {'mode': '', 'name': 'result', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'alpha', 'op': '=', 'expr': '2/(n + 1)', 'conditions': []}, {'mode': '', 'name': 'prevResult', 'op': '=', 'expr': 'price', 'conditions': []}, {'mode': '', 'name': 'prevResult', 'op': ':=', 'expr': 'result[1]', 'conditions': ['(na(result[1]) == false)']}, {'mode': '', 'name': 'result', 'op': ':=', 'expr': 'alpha * price + (1 - alpha) * prevResult', 'conditions': []}, {'mode': '', 'name': 'n_slow', 'op': '=', 'expr': 'input.int(50, "Период медленной скользящей средней", step=5)', 'conditions': []}, {'mode': '', 'name': 'n_fast', 'op': '=', 'expr': 'input.int(4, "Период быстрой скользящей средней")', 'conditions': []}, {'mode': '', 'name': 'n_deviation', 'op': '=', 'expr': 'input.int(30, "Период среднеквадратического отклонения", step=5)', 'conditions': []}, {'mode': '', 'name': 'k_deviation_open', 'op': '=', 'expr': 'input.float(1.2, "Коэффициент ширины коридора покупки", step=0.1)', 'conditions': []}, {'mode': '', 'name': 'k_deviation_close', 'op': '=', 'expr': 'input.float(1.6, "Коэффициент ширины коридора продажи", step=0.1)', 'conditions': []}, {'mode': '', 'name': 'sma', 'op': '=', 'expr': 'sma(close, n_slow)', 'conditions': []}, {'mode': '', 'name': 'bollinger_open', 'op': '=', 'expr': 'k_deviation_open * ta.stdev(close, n_deviation)', 'conditions': []}, {'mode': '', 'name': 'open_short_line', 'op': '=', 'expr': 'sma + bollinger_open', 'conditions': []}, {'mode': '', 'name': 'open_long_line', 'op': '=', 'expr': 'sma - bollinger_open', 'conditions': []}, {'mode': '', 'name': 'bollinger_close', 'op': '=', 'expr': 'k_deviation_close * ta.stdev(close, n_deviation)', 'conditions': []}, {'mode': '', 'name': 'close_short_line', 'op': '=', 'expr': 'sma + bollinger_close', 'conditions': []}, {'mode': '', 'name': 'close_long_line', 'op': '=', 'expr': 'sma - bollinger_close', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ema(close, n_fast)', 'conditions': []}]
    pine_user_functions = [{'name': 'sma', 'args': 'price, n', 'body': ''}, {'name': 'wma', 'args': 'price, n', 'body': ''}, {'name': 'ema', 'args': 'price, n', 'body': ''}]
    pine_controls = [{'indent': 4, 'statement': 'for i = 0 to n - 1'}, {'indent': 4, 'statement': 'for i = 0 to n - 1'}, {'indent': 4, 'statement': 'if (na(result[1]) == false)'}, {'indent': 0, 'statement': 'if(ema[1] >= open_short_line[1] and ema < open_short_line)'}, {'indent': 0, 'statement': 'if(ema[1] <= open_long_line[1] and ema > open_long_line)'}, {'indent': 0, 'statement': 'if (high >= close_short_line)'}, {'indent': 0, 'statement': 'if (low <= close_long_line)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("short", strategy.short)', 'conditions': [], 'statement': 'strategy.entry("short", strategy.short)'}, {'kind': 'entry', 'call': 'strategy.entry("long", strategy.long)', 'conditions': [], 'statement': 'strategy.entry("long", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("long")', 'conditions': ['(high >= close_short_line)'], 'statement': 'strategy.close("long")'}, {'kind': 'close', 'call': 'strategy.close("short")', 'conditions': ['(low <= close_long_line)'], 'statement': 'strategy.close("short")'}]
    original_pine = '/*backtest\nstart: 2024-03-01 00:00:00\nend: 2024-03-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy ("Marina Parfenova School Project Bot", overlay = true)\n\nsma(price, n) =>\n    result = 0.0\n    for i = 0 to n - 1\n        result := result + price [i] / n    \n    result\n\nwma(price, n) =>\n    result = 0.0\n    sum_weight = 0.0\n    weight = 0.0\n    for i = 0 to n - 1\n        weight := n - 1\n        result := result + price [i]*weight\n        sum_weight := sum_weight + weight\n    result/sum_weight\n\nema(price, n) =>\n    result = 0.0\n    alpha = 2/(n + 1)\n    prevResult = price \n    if (na(result[1]) == false)\n        prevResult := result[1]\n    result := alpha * price + (1 - alpha) * prevResult\n\n/// Настройки\nn_slow = input.int(50, "Период медленной скользящей средней", step=5)\nn_fast = input.int(4, "Период быстрой скользящей средней")\nn_deviation = input.int(30, "Период среднеквадратического отклонения", step=5)\nk_deviation_open = input.float(1.2, "Коэффициент ширины коридора покупки", step=0.1)\nk_deviation_close = input.float(1.6, "Коэффициент ширины коридора продажи", step=0.1)\n\n// ----- Линии индикаторов -----\n\n// Медленная скользящая \nsma = sma(close, n_slow)\nplot(sma, color=#d3d3d3)\n\n// Линии Боллинджера, обозначающие коридор цены\nbollinger_open = k_deviation_open * ta.stdev(close, n_deviation)\nopen_short_line = sma + bollinger_open\nplot(open_short_line, color=#ec8383)\nopen_long_line = sma - bollinger_open\nplot(open_long_line, color=#6dd86d)\n\nbollinger_close = k_deviation_close * ta.stdev(close, n_deviation)\nclose_short_line = sma + bollinger_close\nplot(close_short_line, color=#e3e3e3)\nclose_long_line = sma - bollinger_close\nplot(close_long_line, color=#e3e3e3)\n\n// Быстрая скользящая\nema = ema(close, n_fast)\nplot(ema, color = color.aqua, linewidth = 2)\n\n// ----- Сигналы для запуска стратегии -----\n\n// если ema пересекает линию open_short сверху вниз - сигнал на создание ордера в short\nif(ema[1] >= open_short_line[1] and ema < open_short_line)\n    strategy.entry("short", strategy.short)\n\n// если ema пересекает линию open_long снизу вверх - сигнал на создание ордера в long\nif(ema[1] <= open_long_line[1] and ema > open_long_line)\n    strategy.entry("long", strategy.long)\n\n// если свеча пересекает верхнюю линию коридора продажи - закрываем все long-ордера \nif (high >= close_short_line)\n    strategy.close("long")\n\n// если свеча пересекает нижнюю линию коридора продажи - закрываем все short-ордера\nif (low <= close_long_line)\n    strategy.close("short")'

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
