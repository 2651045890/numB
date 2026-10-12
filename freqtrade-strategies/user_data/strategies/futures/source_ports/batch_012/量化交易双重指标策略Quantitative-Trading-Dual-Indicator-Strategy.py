"""batch_012 port of 量化交易双重指标策略Quantitative-Trading-Dual-Indicator-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-07 00:00:00\nend: 2024-01-11 23:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy("Bollinger Bands + RSI, Double Strategy (by SlumdogTrader)", shorttitle="BolBand_RSI_Strat", overlay=true)\n\n// SlumdogTrader\'s Bollinger Bands + RSI Double Strategy - Profit Trailer\n//\n// Version 1.0\n// Script by SlumdogTrader on July Fri 13(!), 2018.\n//\n// This strategy uses a normalise Bollinger Bands + RSI.\n//\n// Bollinger Band triggers\n// SELL - when the price is above the upper band.\n// BUY - when the price is below the lower band.\n//\n// RSI triggers\n// SELL - when the price is above 55.\n// BUY - when the price is below 45.\n//\n// This simple strategy only triggers when\n// both the BB and the RSI\n// indicators, at the same time, are in\n// a overbought or oversold condition.\n//\n// Visit my TradingView work at:\n// https://www.tradingview.com/u/SlumdogTrader/\n//\n// Visit my website at:\n// https://www.slumdogtrader.com\n//\n\n///////////// Bollinger Bands Settings\nBBlength = input(20, minval=1,title="Bollinger Bands SMA Period Length")\nBBmult = input(2.0, minval=0.001, maxval=50,title="Bollinger Bands Standard Deviation")\nprice = input(close, title="Source")\nBBbasis = sma(price, BBlength)\nBBdev = BBmult * stdev(price, BBlength)\nBBupper = BBbasis + BBdev\nBBlower = BBbasis - BBdev\nsource = close\nbuyEntry = crossover(source, BBlower)\nsellEntry = crossunder(source, BBupper)\nplot(BBbasis, color=aqua,title="BBs SMA Basis Line")\np1 = plot(BBupper, color=silver,title="BBs Upper Line")\np2 = plot(BBlower, color=silver,title="BBs Lower Line")\nfill(p1, p2)\n\n///////////// RSI Settings\nRSIlength = input( 16 ,title="RSI Period Length")\nRSIvalue = input( 45 ,title="RSI Value Range")\nRSIoverSold = 0 + RSIvalue\nRSIoverBought = 100 - RSIvalue\nvrsi = rsi(price, RSIlength)\n\n\n///////////// Colour Settings\nswitch1=input(true, title="Enable Bar Color?")\nswitch2=input(true, title="Enable Background Color?")\nTrendColor = RSIoverBought and (price[1] > BBupper and price < BBupper) ? red : RSIoverSold and (price[1] < BBlower and price > BBlower)  ? green : na\nbarcolor(switch1?TrendColor:na)\nbgcolor(switch2?TrendColor:na,transp=50)\n\n\n///////////// RSI + Bollinger Bands Strategy\nif (not na(vrsi))\n\n    if (crossover(vrsi, RSIoverSold) and crossover(source, BBlower))\n        strategy.entry("RSI_BB_L", strategy.long, stop=BBlower,  comment="RSI_BB_L")\n    else\n        strategy.cancel(id="RSI_BB_L")\n\n    if (crossunder(vrsi, RSIoverBought) and crossunder(source, BBupper))\n        strategy.entry("RSI_BB_S", strategy.short, stop=BBupper,  comment="RSI_BB_S")\n    else\n        strategy.cancel(id="RSI_BB_S")\n\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)\n\n'

class SMQuantitativeTradingDualIndicatorStrategy61933b(PinePortBase, IStrategy):
    source_id = "SM_61933baeb4fca9dd"
    source_file = '量化交易双重指标策略Quantitative-Trading-Dual-Indicator-Strategy.md'
    timeframe = '1m'
    can_short = True
    source_defaults = {'BBlength': 20, 'BBmult': 2.0, 'price': 'close', 'RSIlength': 16, 'RSIvalue': 45, 'switch1': True, 'switch2': True}
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
