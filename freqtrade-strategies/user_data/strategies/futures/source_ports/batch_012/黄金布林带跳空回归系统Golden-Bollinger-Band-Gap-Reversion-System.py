"""batch_012 port of 黄金布林带跳空回归系统Golden-Bollinger-Band-Gap-Reversion-System.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-01 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 2h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © exlux99\n\n//@version=4\nstrategy("Bollinger Bands, RSI and ADX Trading System", overlay=true)\n\n\ntimeinrange(res, sess) => time(res, sess) != 0\n\n\ntimer = color.red\n\n\n//bgcolor(timeinrange(timeframe.period, "0300-0600") or timeinrange(timeframe.period, "0900-1300") or timeinrange(timeframe.period, "2030-2300") ? timer : na, transp=70)\n\n\n//RSI\nlength = input( 20 )\noverSold = input( 35 )\noverBought = input( 65 )\nprice = close\nvrsi = rsi(price, length)\nco = crossover(vrsi, overSold)\ncu = crossunder(vrsi, overBought)\n//if (not na(vrsi))\n\n\n//BB\nlengthB = input(60, minval=1)\nsrc = input(close, title="Source")\nmult = input(2.0, minval=0.001, maxval=50, title="StdDev")\nbasis = sma(src, lengthB)\ndev = mult * stdev(src, lengthB)\nupper = basis + dev\nlower = basis - dev\n\n\n//adx\nadxlen = input(14, title="ADX Smoothing")\ndilen = input(14, title="DI Length")\ndirmov(len) =>\n\tup = change(high)\n\tdown = -change(low)\n\tplusDM = na(up) ? na : (up > down and up > 0 ? up : 0)\n\tminusDM = na(down) ? na : (down > up and down > 0 ? down : 0)\n\ttruerange = rma(tr, len)\n\tplus = fixnan(100 * rma(plusDM, len) / truerange)\n\tminus = fixnan(100 * rma(minusDM, len) / truerange)\n\t[plus, minus]\nadx(dilen, adxlen) =>\n\t[plus, minus] = dirmov(dilen)\n\tsum = plus + minus\n\tadx = 100 * rma(abs(plus - minus) / (sum == 0 ? 1 : sum), adxlen)\nsig = adx(dilen, adxlen)\n\nlongEntry = close < upper and crossover(vrsi,overSold) and sig < 32 //and (timeinrange(timeframe.period, "0301-0600") or timeinrange(timeframe.period, "0901-1300") or timeinrange(timeframe.period, "2031-2300"))\n\nshortEntry = close > upper and crossunder(vrsi,overBought) and sig < 32 //and (timeinrange(timeframe.period, "0301-0600") or timeinrange(timeframe.period, "0901-1300") or timeinrange(timeframe.period, "2031-2300"))\n\n\ntp=input(90, step=10)\nsl=input(90, step=10)\n\nstrategy.entry("long",1,when=longEntry)\nstrategy.exit("X_long", "long", profit=tp,  loss=sl )\nstrategy.close("long",when=crossunder(close,basis))\n\nstrategy.entry(\'short\',0,when=shortEntry)\nstrategy.exit("x_short", "short",profit=tp, loss=sl)\nstrategy.close("short",when=crossover(close,basis))\n\n\n\n\n\n\n'

class SMGoldenBollingerBandGapReversionSystem095bfa(PinePortBase, IStrategy):
    source_id = "SM_095bfa7335fe3827"
    source_file = '黄金布林带跳空回归系统Golden-Bollinger-Band-Gap-Reversion-System.md'
    timeframe = '2h'
    can_short = False
    source_defaults = {'length': 20, 'overSold': 35, 'overBought': 65, 'lengthB': 60, 'src': 'close', 'mult': 2.0, 'adxlen': 14, 'dilen': 14, 'tp': 90, 'sl': 90}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
