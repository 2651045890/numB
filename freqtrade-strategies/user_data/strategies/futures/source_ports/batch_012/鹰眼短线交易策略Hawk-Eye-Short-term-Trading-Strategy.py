"""batch_012 port of 鹰眼短线交易策略Hawk-Eye-Short-term-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-15 00:00:00\nend: 2023-09-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("Hawk 1H Strategy", overlay=true)\n\nfastLength = input(21)\nslowlength = input(55)\nMACDLength = input(8)\nsmallEMA = ema(close, fastLength)\nlargeEMA = ema(close, slowlength)\nMACD = smallEMA - largeEMA\naMACD = ema(MACD, MACDLength)\ndelta = MACD - aMACD\n\nsmoothK = input(5, minval=1)\nsmoothD = input(5, minval=1)\nlengthRSI = input(8, minval=1)\nlengthStoch = input(21, minval=1)\nsrc = input(close, title="RSI Source")\nvFast = stoch(close, high, low, 8)\nvSlow = sma(vFast, 5)\nrsi1 = rsi(src, lengthRSI)\nk = sma(stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)\nd = sma(k, smoothD)\n\nfiftyVWMA = vwma(close, 55)\ntwohunVWMA = vwma(close,144)\n\n\nif (MACD > MACD[1]) and (MACD[1] > MACD[2]) and (fiftyVWMA < twohunVWMA)\n    if (vFast > vSlow) and (k < 30) //and (vSlow < 40)\n        strategy.entry("MacdLE", strategy.long, comment=\'Buy\')\n        \nif (MACD < MACD[1]) and (MACD[1] < MACD[2]) and (fiftyVWMA > twohunVWMA)\n    if (vFast < vSlow) and (k > 70)//and (vSlow > 60)//and (rsi1 > 60)\n        strategy.entry("MacdSE", strategy.short, comment=\'Sell\')\n\n\n    \n\n\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)\n'

class SMHawkEyeShorttermTradingStrategydccea1(PinePortBase, IStrategy):
    source_id = "SM_dccea1196834f718"
    source_file = '鹰眼短线交易策略Hawk-Eye-Short-term-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'fastLength': 21, 'slowlength': 55, 'MACDLength': 8, 'smoothK': 5, 'smoothD': 5, 'lengthRSI': 8, 'lengthStoch': 21, 'src': 'close'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
