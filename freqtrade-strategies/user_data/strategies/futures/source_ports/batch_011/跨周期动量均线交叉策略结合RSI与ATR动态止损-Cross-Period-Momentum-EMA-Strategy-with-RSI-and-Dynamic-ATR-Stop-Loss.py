"""batch_011 port of 跨周期动量均线交叉策略结合RSI与ATR动态止损-Cross-Period-Momentum-EMA-Strategy-with-RSI-and-Dynamic-ATR-Stop-Loss.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-10 00:00:00\nend: 2025-02-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Day Trading EMA/RSI Strategy", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=200)\n\n// Ulazni parametri\nfastEmaPeriod   = input.int(9, "Fast EMA Period", minval=1)\nslowEmaPeriod   = input.int(21, "Slow EMA Period", minval=1)\nrsiPeriod       = input.int(14, "RSI Period", minval=1)\nrsiOversold     = input.int(30, "RSI Oversold Level")\nrsiOverbought   = input.int(70, "RSI Overbought Level")\natrPeriod       = input.int(14, "ATR Period", minval=1)\natrMultiplier   = input.float(1.5, "ATR Multiplier za Stop Loss", step=0.1)\ntakeProfitFactor= input.float(2.0, "Take Profit Factor", step=0.1)\n\n// Izračun indikatora\nfastEMA = ta.ema(close, fastEmaPeriod)\nslowEMA = ta.ema(close, slowEmaPeriod)\nrsiValue = ta.rsi(close, rsiPeriod)\natrValue = ta.atr(atrPeriod)\n\n// Definicija trenda: ako je fastEMA iznad slowEMA, smatramo da je trend uzlazan, inače silazni.\ntrendUp   = fastEMA > slowEMA\ntrendDown = fastEMA < slowEMA\n\n// Uvjeti za ulaz:\n// Ulaz u long poziciju: crossover fastEMA i slowEMA, uz filtriranje da RSI nije prekupovan (manje od rsiOverbought)\nlongCondition  = ta.crossover(fastEMA, slowEMA) and (rsiValue < rsiOverbought)\n// Ulaz u short poziciju: crossunder fastEMA i slowEMA, uz filtriranje da RSI nije preprodavan (više od rsiOversold)\nshortCondition = ta.crossunder(fastEMA, slowEMA) and (rsiValue > rsiOversold)\n\n// Definicija dinamičnih stop-loss razina (ATR-based)\nstopLossLong  = close - (atrMultiplier * atrValue)\nstopLossShort = close + (atrMultiplier * atrValue)\n\n// Izvršenje naloga\nif (longCondition)\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Exit Long", "Long", stop=stopLossLong, limit=close + (takeProfitFactor * atrValue))\n\nif (shortCondition)\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Exit Short", "Short", stop=stopLossShort, limit=close - (takeProfitFactor * atrValue))\n\n// Plotanje indikatora za preglednost\nplot(fastEMA, title="Fast EMA", color=color.green)\nplot(slowEMA, title="Slow EMA", color=color.red)\n'

class SM0852071FC076BC42(PinePortBase, IStrategy):
    source_id = "SM_0852071fc076bc42"
    source_file = '跨周期动量均线交叉策略结合RSI与ATR动态止损-Cross-Period-Momentum-EMA-Strategy-with-RSI-and-Dynamic-ATR-Stop-Loss.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastEmaPeriod': 9, 'slowEmaPeriod': 21, 'rsiPeriod': 14, 'rsiOversold': 30, 'rsiOverbought': 70, 'atrPeriod': 14, 'atrMultiplier': 1.5, 'takeProfitFactor': 2.0}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 200
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
