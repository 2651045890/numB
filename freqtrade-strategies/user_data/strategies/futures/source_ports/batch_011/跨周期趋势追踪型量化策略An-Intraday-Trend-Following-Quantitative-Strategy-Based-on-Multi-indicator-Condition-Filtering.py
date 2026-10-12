"""batch_011 port of 跨周期趋势追踪型量化策略An-Intraday-Trend-Following-Quantitative-Strategy-Based-on-Multi-indicator-Condition-Filtering.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-14 00:00:00\nend: 2023-12-14 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("psar+ adx + cmf + rsi Strategy", overlay=true,initial_capital = 1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent , commission_value=0.1 )\n\nstart = input(1.02)\nincrement = input(1.02)\nmaximum = input(1.2)\nvar bool uptrend = na\nvar float EP = na\nvar float SAR = na\nvar float AF = start\nvar float nextBarSAR = na\nif bar_index > 0\n\tfirstTrendBar = false\n\tSAR := nextBarSAR\n\tif bar_index == 1\n\t\tfloat prevSAR = na\n\t\tfloat prevEP = na\n\t\tlowPrev = low[1]\n\t\thighPrev = high[1]\n\t\tcloseCur = close\n\t\tclosePrev = close[1]\n\t\tif closeCur > closePrev\n\t\t\tuptrend := true\n\t\t\tEP := high\n\t\t\tprevSAR := lowPrev\n\t\t\tprevEP := high\n\t\telse\n\t\t\tuptrend := false\n\t\t\tEP := low\n\t\t\tprevSAR := highPrev\n\t\t\tprevEP := low\n\t\tfirstTrendBar := true\n\t\tSAR := prevSAR + start * (prevEP - prevSAR)\n\tif uptrend\n\t\tif SAR > low\n\t\t\tfirstTrendBar := true\n\t\t\tuptrend := false\n\t\t\tSAR := max(EP, high)\n\t\t\tEP := low\n\t\t\tAF := start\n\telse\n\t\tif SAR < high\n\t\t\tfirstTrendBar := true\n\t\t\tuptrend := true\n\t\t\tSAR := min(EP, low)\n\t\t\tEP := high\n\t\t\tAF := start\n\tif not firstTrendBar\n\t\tif uptrend\n\t\t\tif high > EP\n\t\t\t\tEP := high\n\t\t\t\tAF := min(AF + increment, maximum)\n\t\telse\n\t\t\tif low < EP\n\t\t\t\tEP := low\n\t\t\t\tAF := min(AF + increment, maximum)\n\tif uptrend\n\t\tSAR := min(SAR, low[1])\n\t\tif bar_index > 1\n\t\t\tSAR := min(SAR, low[2])\n\telse\n\t\tSAR := max(SAR, high[1])\n\t\tif bar_index > 1\n\t\t\tSAR := max(SAR, high[2])\n\tnextBarSAR := SAR + AF * (EP - SAR)\n\n//rsi strat\nlength = input( 50 )\nmiddle_RSI=input(49)\nprice = close\nvrsi = rsi(price, length)\n\n//cmf\nlengthCMF = input(20, minval=1)\nad = close==high and close==low or high==low ? 0 : ((2*close-low-high)/(high-low))*volume\nmf = sum(ad, lengthCMF) / sum(volume, lengthCMF)\n\n//ADX\nadxlen = input(14, title="ADX Smoothing")\ndilen = input(14, title="DI Length")\ndirmov(len) =>\n\tup = change(high)\n\tdown = -change(low)\n\tplusDM = na(up) ? na : (up > down and up > 0 ? up : 0)\n\tminusDM = na(down) ? na : (down > up and down > 0 ? down : 0)\n\ttruerange = rma(tr, len)\n\tplus = fixnan(100 * rma(plusDM, len) / truerange)\n\tminus = fixnan(100 * rma(minusDM, len) / truerange)\n\t[plus, minus]\nadx(dilen, adxlen) =>\n\t[plus, minus] = dirmov(dilen)\n\tsum = plus + minus\n\tadx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)\nsig = adx(dilen, adxlen)\nema_length=input(10)\nema_sig= ema(sig,ema_length)\n\n\nlong = not uptrend  and vrsi > middle_RSI and sig > ema_sig   and mf>0 \nshort= uptrend   and vrsi < middle_RSI and sig<ema_sig and mf<0\n\nstrategy.entry("long",1,when=long)\nstrategy.close(\'long\',when=short)'

class SM1B467E640831BB42(PinePortBase, IStrategy):
    source_id = "SM_1b467e640831bb42"
    source_file = '跨周期趋势追踪型量化策略An-Intraday-Trend-Following-Quantitative-Strategy-Based-on-Multi-indicator-Condition-Filtering.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'start': 1.02, 'increment': 1.02, 'maximum': 1.2, 'length': 50, 'middle_RSI': 49, 'lengthCMF': 20, 'adxlen': 14, 'dilen': 14, 'ema_length': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.1
    source_pyramiding = 0
    source_initial_capital = 1000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'tuple', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
