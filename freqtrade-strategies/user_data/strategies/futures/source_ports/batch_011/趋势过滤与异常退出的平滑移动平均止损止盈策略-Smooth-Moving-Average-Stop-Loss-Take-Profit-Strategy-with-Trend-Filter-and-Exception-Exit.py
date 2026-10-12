"""batch_011 port of 趋势过滤与异常退出的平滑移动平均止损止盈策略-Smooth-Moving-Average-Stop-Loss-Take-Profit-Strategy-with-Trend-Filter-and-Exception-Exit.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-05-01 00:00:00\nend: 2024-05-31 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Strategia Stop Loss & Take Profit z Filtrem Trendu i Wyjątkiem", shorttitle="Smooth MA SL & TP with Exception", overlay=true)\n\n// Parametry\ntp_multiplier = input.float(1.5, title="Mnożnik Take Profit")\nsl_percent = input.float(5, title="Procent Stop Loss")\nwait_bars = input.int(3, title="Liczba Oczekiwanych Świec")\nsma_period = input.int(200, title="Okres SMA")\nrsi_period = input.int(14, title="Okres RSI")\nvol_ma_period = input.int(20, title="Okres Średniej Wolumenu")\ntr_ma_period = input.int(20, title="Okres Średniej Rzeczywistego Zakresu")\n\n// Obliczenie Gładkiej Średniej Kroczącej\nsma = ta.sma(close, sma_period)\n\n// Obliczenie RSI\nrsi = ta.rsi(close, rsi_period)\n\n// Filtr Trendu\nuptrend = close > sma\ndowntrend = close < sma\n\n// Warunek konsolidacji: Niski wolumen i niska zmienność\nniski_wolumen = volume < ta.sma(volume, vol_ma_period)\nniska_zmienosc = ta.tr(true) < ta.sma(ta.tr(true), tr_ma_period)\n\n// Warunek Wejścia (Long): Cena poniżej SMA 200 i filtr trendu w strefie czerwonej\nwarunek_wejscia = close < sma and niski_wolumen and niska_zmienosc and not uptrend\n\n// Warunek Wyjścia ze strategii\nwarunek_wyjscia = downtrend and close > sma and ta.crossover(close, sma)\n\n// Ustalanie Stop Loss i Take Profit\nvar float stop_loss = na\nvar float take_profit = na\n\nvar int indeks_wejscia = na\n\nif (warunek_wejscia)\n    stop_loss := close * (1 - sl_percent / 100)\n    take_profit := close * (1 + tp_multiplier)\n    indeks_wejscia := bar_index\n\n// Handel\nif (warunek_wejscia)\n    strategy.entry("Long", strategy.long)\n\n// Warunek Wyjścia: RSI w strefie wykupienia lub Stop Loss/Take Profit\nif (strategy.opentrades != 0)\n    if (rsi > 70)\n        strategy.exit("Take Profit/Stop Loss", "Long", limit=take_profit)\n    else if (bar_index - indeks_wejscia == wait_bars)\n        strategy.exit("Take Profit/Stop Loss", "Long", stop=stop_loss, limit=take_profit)\n\n// Wyjątek: Warunek Wyjścia z Longów na podstawie zmiany trendu\nif (warunek_wyjscia)\n    strategy.close("Long")\n\n// Rysowanie RSI\nrsi_plot = plot(rsi, title="RSI", color=color.blue)\n\n// Rysowanie Gładkiej Średniej Kroczącej\nsma_plot = plot(sma, color=color.gray, title="Smooth MA", linewidth=2)\n\n// Rysowanie Filtru Trendu\nfill(sma_plot, rsi_plot, color=downtrend ? color.new(color.red, 90) : na)\n'

class SM1762609328D26A41(PinePortBase, IStrategy):
    source_id = "SM_1762609328d26a41"
    source_file = '趋势过滤与异常退出的平滑移动平均止损止盈策略-Smooth-Moving-Average-Stop-Loss-Take-Profit-Strategy-with-Trend-Filter-and-Exception-Exit.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'tp_multiplier': 1.5, 'sl_percent': 5, 'wait_bars': 3, 'sma_period': 200, 'rsi_period': 14, 'vol_ma_period': 20, 'tr_ma_period': 20}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['broker_state', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
