"""batch_012 port of 阻力与支撑带动的拉里金叉RSI策略RSIndex-and-Moving-Average-Combination-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-04 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n//Created by ChrisMoody\n//Based on Larry Connors RSI-2 Strategy - Lower RSI\nstrategy(title="_CM_RSI_2_Strat_Low", shorttitle="_CM_RSI_2_Strategy_Lower", overlay=false)\nsrc = close, \n\n//RSI CODE\nup = rma(max(change(src), 0), 2)                \ndown = rma(-min(change(src), 0), 2)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\n//Criteria for Moving Avg rules\nma1 = sma(close,1)\nma2 = sma(close,2)\nma3 = sma(close,3)\nma4 = sma(close,4)\nma5 = sma(close,5)\nma6 = sma(close,6)\nma7 = sma(close,7)\nma8 = sma(close,8)\nma9 = sma(close,9)\nma200= sma(close, 120)\n\n//Rule for RSI Color\ncol = close > ma200 and close < ma5 and rsi < 10 ? lime : close < ma200 and close > ma5 and rsi > 90 ? red : silver\n\nplot(rsi, title="RSI", style=line, linewidth=4,color=col)\nplot(100, title="Upper Line 100",style=line, linewidth=3, color=aqua)\nplot(0, title="Lower Line 0",style=line, linewidth=3, color=aqua)\n\nband1 = plot(90, title="Upper Line 90",style=line, linewidth=3, color=aqua)\nband0 = plot(10, title="Lower Line 10",style=line, linewidth=3, color=aqua)\nfill(band1, band0, color=silver, transp=90)\n\n///////////// RSI + Bollinger Bands Strategy\n\n\nif (close > ma200 and rsi < 10 and rsi >1)\n    strategy.entry("RSI_2_L", strategy.long, comment="Bullish")\nif (close < ma200 and rsi > 90 and rsi <98)\n    strategy.entry("RSI_2_S", strategy.short, comment="Bearish")\n\n\nstrategy.close("RSI_2_L", when = close > ma5 and ma1 < ma3)\nstrategy.close("RSI_2_S", when = close < ma5 and ma1 > ma2)\n\n'

class SMRSIRSIndexandMovingAverageCombinationStrategy1fbc07(PinePortBase, IStrategy):
    source_id = "SM_1fbc07892a8c78d7"
    source_file = '阻力与支撑带动的拉里金叉RSI策略RSIndex-and-Moving-Average-Combination-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {}
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
