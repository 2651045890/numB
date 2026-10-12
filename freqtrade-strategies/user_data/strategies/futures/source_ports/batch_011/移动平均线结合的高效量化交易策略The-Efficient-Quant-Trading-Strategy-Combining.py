"""batch_011 port of 移动平均线结合的高效量化交易策略The-Efficient-Quant-Trading-Strategy-Combining.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-24 00:00:00\nend: 2024-01-31 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// ©chewyScripts.\n\n//@version=5\nstrategy("96er RSI+200EMA Strategy + Alerts", overlay=true)\n// This works best on a small account $100, with 50% of equity and up to 10 max open trades. \n// 96% Profitable, turns $100 into $350 in 1 month. very few losses. super happy with it.\n// So far it triples the account on a 1m chart in 1 month back testing on the SEI-USD pair.\n// I did not test on FX pairs or other instruments.\n// had some issues with the inputs not working so had to hard code some, also the lastClose var sometimes breaks and starts following every candle, not sure why.\n\nin_r1 = input.int(5,"5 day input or RSI1")\nin_openOrders = input.int(3,"max open orders")\n\nin_lowerRSI = input.int(30,"RSI Lower")\nin_upperRSI = input.int(72,"RSI Upper ")\n\nin_emaperiod = input.int(200,"EMA Period")\n\nin_buybreakout = input.int(50,"Buy breakout range")\n\nin_buyTP = input.float(1.05,"Buy TP: 1+TP %, .05 seems to work well.")\nin_sellTP = input.float(0.9850, "Sell TP: 1-TP%. .025 seems to work well. ")\n\nsimple int rsi5 = in_r1\n\n// 3 rsi strategy , when all of them are overbought we sell, and vice versa\nrsi7 = ta.rsi(close,rsi5)\nlastClose = request.security(syminfo.tickerid, "D", close, lookahead = barmerge.lookahead_on)\nrsi3 = ta.rsi(close[5],rsi5)\n\nma = ta.ema(close,in_emaperiod)\n\nplot(rsi7,"5 Day RSI",color.red)\nplot(lastClose,"Yesterdays Close",color.green)\nplot(rsi3,"Previous 5th candles RSI",color.purple)\n\n\n// sell condition\n//sell = ta.crossunder(rsi7,70) and ta.crossunder(rsi14,70) and ta.crossunder(rsi21,70)\n\n//buy condition\n//buy = ta.crossover(rsi7,in_lowerRSI) and close < ma and rsi3 <= in_upperRSI and strategy.opentrades < in_openOrders\n//sell = ta.crossunder(rsi7,in_upperRSI) and close > ma and rsi3 >= in_lowerRSI3 and strategy.opentrades < in_openOrders\n\nbuy = ta.crossover(rsi7,in_lowerRSI) and close < ma and close < lastClose and strategy.opentrades < in_openOrders\nsell = ta.crossunder(rsi7,in_upperRSI) and close > ma and close > lastClose and strategy.opentrades < in_openOrders\n\n\nvar lastBuy = close \nvar lastSell = close \n\nif (buy)\n    strategy.entry("BUY", strategy.long)\n    lastBuy := close \n    alert("Buy")\n\nif ((close >= lastBuy*in_buyTP ) or rsi7 > in_buybreakout and close >= lastClose and (close >= lastClose*in_buyTP or close >= lastBuy*in_buyTP ) )\n    strategy.close("BUY", "BUY Exit")\n    alert("Buy Exit")\n    \nif (sell)\n    strategy.entry("SELL", strategy.short)\n    lastSell := close \n    alert("Sell")\n\nif ( close < ma and (close <= lastSell*in_sellTP ) or (close < lastClose*in_sellTP) )\n    strategy.close("SELL", "Sell Exit")\n    alert("Sell Exit")\n'

class SM1DB71178C4A03BC7(PinePortBase, IStrategy):
    source_id = "SM_1db71178c4a03bc7"
    source_file = '移动平均线结合的高效量化交易策略The-Efficient-Quant-Trading-Strategy-Combining.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'in_r1': 5, 'in_openOrders': 3, 'in_lowerRSI': 30, 'in_upperRSI': 72, 'in_emaperiod': 200, 'in_buybreakout': 50, 'in_buyTP': 1.05, 'in_sellTP': 0.985}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
