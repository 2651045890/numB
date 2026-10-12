"""batch_011 port of 结合MACDRSI和FIB的量化比特币交易策略Quant-Bitcoin-Trading-Strategy-Combining-MACD-RSI-and-FIB.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-18 00:00:00\nend: 2023-12-25 00:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © onurenginogutcu\n\n//@version=4\nstrategy("STRATEGY R18-F-BTC", overlay=true, margin_long=100, margin_short=100)\n\n///////////default girişler 1 saatlik btc grafiği için geçerli olmak üzere - stop loss\'lar %2.5 - long\'da %7.6 , short\'ta %8.1\n\nsym = input(title="Symbol", type=input.symbol, defval="BINANCE:BTCUSDT") /////////btc\'yi indikatör olarak alıyoruz\n\nlsl = input(title="Long Stop Loss (%)",\n     minval=0.0, step=0.1, defval=2.5) * 0.01\n     \nssl = input(title="Short Stop Loss (%)",\n     minval=0.0, step=0.1, defval=2.5) * 0.01\n     \nlongtp = input(title="Long Take Profit (%)",\n     minval=0.0, step=0.1, defval=7.6) * 0.01\n     \nshorttp = input(title="Short Take Profit (%)",\n     minval=0.0, step=0.1, defval=7.5) * 0.01\n     \ncapperc = input(title="Capital Percentage to Invest (%)",\n     minval=0.0, maxval=100, step=0.1, defval=90) * 0.01\n     \nchoice = input(title="Reverse ?", type=input.bool, defval=false)\n\nsymClose = security(sym, "", close)\nsymHigh = security(sym, "", high)\nsymLow = security(sym, "", low)\n\ni = ema (symClose , 15) - ema (symClose , 30) ///////// ema close 15 ve 30 inanılmaz iyi sonuç verdi (macd standartı 12 26)\nr = ema (i , 9)\n\nsapust = highest (i , 100) * 0.729 //////////0.729 altın oran oldu 09.01.2022\nsapalt = lowest (i , 100) * 0.729  //////////0.729 altın oran oldu 09.01.2022\n\n///////////highx = highest (close , 365) * 0.72 fibo belki dahiledilebilir\n///////////lowx = lowest (close , 365) * 1.272 fibo belki dahil edilebilir\nsimRSI = rsi (symClose , 50 ) /////// RSI DAHİL EDİLDİ "50 MUMLUK RSI EN İYİ SONUCU VERİYOR"\n\n\n//////////////fibonacci seviyesi eklenmesi amacı ile koyuldu fakat en iyi sonuç %50 seviyesinin altı ve üstü (low ve high 38 barlık) en iyi sonuç verdi\nfibvar = 38\nfibtop = lowest (symLow , fibvar) + ((highest (symHigh , fibvar) - lowest (symLow , fibvar)) * 0.50)\nfibbottom = lowest (symLow , fibvar) + ((highest (symHigh , fibvar) - lowest (symLow , fibvar)) * 0.50)\n\n///////////////////////////////////////////////////////////// INDICATOR CONDITIONS\n\nlongCondition = crossover(i, r) and i < sapalt and symClose < sma (symClose , 50) and simRSI < sma (simRSI , 50) and symClose < fibbottom\nshortCondition = crossunder(i, r) and i > sapust and symClose > sma (symClose , 50) and simRSI > sma (simRSI , 50)  and symClose > fibtop\n\n////////////////////////////////////////////////////////////////\n\n///////////////////////////////////////////STRATEGY ENTRIES AND STOP LOSSES /////stratejilerde kalan capital için strategy.equity kullan (bunun üzerinden işlem yap)\n\n\nif (choice == false and longCondition)\n    strategy.entry("Long", strategy.long , qty = capperc * strategy.equity / close ,   when = strategy.position_size == 0)\n   \n\nif (choice == false and shortCondition)\n    strategy.entry("Short" , strategy.short , qty = capperc * strategy.equity / close ,  when = strategy.position_size == 0)\n\nif (choice == true and longCondition)\n    strategy.entry("Short" , strategy.short , qty = capperc * strategy.equity / close ,  when = strategy.position_size == 0)\n\nif (choice == true and shortCondition)\n    strategy.entry("Long", strategy.long , qty = capperc * strategy.equity / close ,   when = strategy.position_size == 0)\n    \n\nif (strategy.position_size > 0)\n    strategy.exit("Exit Long", "Long", stop=strategy.position_avg_price*(1 - lsl) , limit=strategy.position_avg_price*(1 + longtp))\n\nif (strategy.position_size < 0)\n    strategy.exit("Exit Short", "Short", stop=strategy.position_avg_price*(1 + ssl) , limit=strategy.position_avg_price*(1 - shorttp))\n\n\n////////////////////////vertical colouring signals\nbgcolor(color=longCondition ? color.new (color.green , 70) : na)\nbgcolor(color=shortCondition ? color.new (color.red , 70) : na)\n\n\n'

class SMEC5EB03583E918B6(PinePortBase, IStrategy):
    source_id = "SM_ec5eb03583e918b6"
    source_file = '结合MACDRSI和FIB的量化比特币交易策略Quant-Bitcoin-Trading-Strategy-Combining-MACD-RSI-and-FIB.md'
    timeframe = '10m'
    can_short = True
    source_defaults = {'sym': 'BINANCE:BTCUSDT', 'lsl': 2.5, 'ssl': 2.5, 'longtp': 7.6, 'shorttp': 7.5, 'capperc': 90, 'choice': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
