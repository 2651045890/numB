"""batch_011 port of 趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-03-05 00:00:00\nend: 2025-03-03 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("MY3 ADX+Stokastik", overlay=true, initial_capital=10000, default_qty_type=strategy.percent_of_equity, default_qty_value=10)\n\n// ADX Parametreleri\nadxPeriod    = input.int(14, title="ADX Periyodu", minval=1)\nadxThreshold = input.float(25.0, title="Trend Gücü Eşiği", step=0.1)\n\n// Stokastik Parametreleri\nstochKPeriod    = input.int(14, title="Stokastik %K Periyodu", minval=1)\nstochSmoothK    = input.int(3, title="Stokastik Smooth", minval=1)\nstochDPeriod    = input.int(3, title="Stokastik %D Periyodu", minval=1)\nstochOverbought = input.int(80, title="Aşırı Alım Seviyesi", minval=50)\nstochOversold   = input.int(20, title="Aşırı Satım Seviyesi", maxval=50)\n\n// ADX Hesaplaması (Manuel)\n// Hesaplamada kullanılan temel unsurlar\nupMove   = high - high[1]\ndownMove = low[1] - low\nplusDM  = (upMove > downMove and upMove > 0) ? upMove : 0.0\nminusDM = (downMove > upMove and downMove > 0) ? downMove : 0.0\n\n// True Range hesaplaması\ntr0 = high - low\ntr1 = math.abs(high - close[1])\ntr2 = math.abs(low - close[1])\ntrueRange = math.max(math.max(tr0, tr1), tr2)\n\n// ATR hesaplaması: Wilder\'in Yumuşak Ortalaması\natrValue = ta.rma(trueRange, adxPeriod)\nplusDI   = 100 * ta.rma(plusDM, adxPeriod) / atrValue\nminusDI  = 100 * ta.rma(minusDM, adxPeriod) / atrValue\ndx       = 100 * math.abs(plusDI - minusDI) / (plusDI + minusDI)\nadxValue = ta.rma(dx, adxPeriod)\n\n// Stokastik Hesaplaması\nk = ta.sma(ta.stoch(close, high, low, stochKPeriod), stochSmoothK)\nd = ta.sma(k, stochDPeriod)\n\n// Alım ve Satım Koşulları:\n// Alım: ADX belirlenen eşik üzerinde ve Stokastik, aşırı satım bölgesinde (k < stochOversold) iken %K, %D kesişimi yukarı doğru.\nbuySignal = (adxValue > adxThreshold) and ta.crossover(k, d) and (k < stochOversold)\n// Satım: ADX belirlenen eşik üzerinde ve Stokastik, aşırı alım bölgesinde (k > stochOverbought) iken %K, %D kesişimi aşağı doğru.\nsellSignal = (adxValue > adxThreshold) and ta.crossunder(k, d) and (k > stochOverbought)\n\n// İşlem Emirleri\nif (buySignal)\n    strategy.entry("Long", strategy.long)\nif (sellSignal)\n    strategy.close("Long")\n\n// Göstergelerin Grafik Üzerinde Gösterimi\nplot(adxValue, color=color.blue, title="ADX")\nhline(adxThreshold, color=color.gray, linestyle=hline.style_dotted, title="ADX Eşiği")\nplot(k, color=color.green, title="Stokastik %K")\nplot(d, color=color.orange, title="Stokastik %D")\nhline(stochOverbought, color=color.red, linestyle=hline.style_dotted, title="Aşırı Alım")\nhline(stochOversold, color=color.green, linestyle=hline.style_dotted, title="Aşırı Satım")\n\n// 3Commas için Uyarı Koşulları (Webhook entegrasyonu için kullanılacak)\nalertcondition(buySignal, title="Alım Uyarısı", message="BUY_SIGNAL")\nalertcondition(sellSignal, title="Satım Uyarısı", message="SELL_SIGNAL")\n'

class SMAE4EB12A58520A1E(PinePortBase, IStrategy):
    source_id = "SM_ae4eb12a58520a1e"
    source_file = '趋势确认随机震荡策略ADX与随机指标结合的动态市场识别系统-Trend-Confirmation-Stochastic-Oscillation-Strategy-Dynamic-Market-Identification-System-Combining-ADX-and-Stochastic-Indicators.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'adxPeriod': 14, 'adxThreshold': 25.0, 'stochKPeriod': 14, 'stochSmoothK': 3, 'stochDPeriod': 3, 'stochOverbought': 80, 'stochOversold': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['common_subset']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
