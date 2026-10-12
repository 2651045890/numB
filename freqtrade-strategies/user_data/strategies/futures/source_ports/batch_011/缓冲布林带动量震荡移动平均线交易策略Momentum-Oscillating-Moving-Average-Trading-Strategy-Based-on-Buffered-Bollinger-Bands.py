"""batch_011 port of 缓冲布林带动量震荡移动平均线交易策略Momentum-Oscillating-Moving-Average-Trading-Strategy-Based-on-Buffered-Bollinger-Bands.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-29 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//                               Hull Cloud v2 by SEASIDE420\nstrategy("Hull Moving Average Cloud v2", shorttitle="hull_cloud_v2", overlay=true, commission_type=strategy.commission.percent, commission_value=0.075, default_qty_type=strategy.percent_of_equity, max_bars_back=200, default_qty_value=100, calc_on_order_fills= true, calc_on_every_tick=true, pyramiding=0)\nhullperiod=input(title="HullMA Period",defval=210, minval=1)\nWidth=input(title="Cloud Width",defval=200, minval=2)\nprice=input(ohlc4,title="Price data")\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12) \nFromDay = input(defval = 1, title = "From Day", minval = 1, maxval = 31) \nFromYear = input(defval = 2017, title = "From Year", minval = 2017) \nToMonth = input(defval = 1, title = "To Month", minval = 1, maxval = 12) \nToDay = input(defval = 1, title = "To Day", minval = 1, maxval = 31) \nToYear = input(defval = 9999, title = "To Year", minval = 2017)\nstart = timestamp(FromYear, FromMonth, FromDay, 00, 00) \nfinish = timestamp(ToYear, ToMonth, ToDay, 23, 59) \nwindow() => true\nn2ma=2*wma(price,round(hullperiod/2))\nnma=wma(price,hullperiod)\ndiff=n2ma-nma\nsqn=round(sqrt(hullperiod))\nn2ma1=2*wma(price[1],round(hullperiod/2))\nnma1=wma(price[1],hullperiod)\ndiff1=n2ma1-nma1\nn1=wma(diff,sqn)\nn2=wma(diff1,sqn)\nHull_Line=n1-n1[1]/n2[1]\nHull_retracted=if(n1>n2)\n    Hull_retracted=Hull_Line-Width\nelse\n    Hull_retracted=Hull_Line+Width\nc1=(Hull_retracted*n1)/price[1] \nc2=(Hull_retracted*n2)/price[1]\nc4=c1>c2?green:red\nc2p=plot(c2, color=black, linewidth=1)\nc3p=plot(price, color=black, linewidth=1)\nfill(c3p, c2p, color=c4, transp=75)\nplot(cross(c1, c2) ? c1 : na, style = circles,color=c4, linewidth = 4) \nif (price<c2)\n    strategy.close("BUY", when=window())\nif (price>c2)                       \n    strategy.close("SELL", when=window())\nif (price[1]>c2 and price[1]>c1)             \n    strategy.entry("BUY",strategy.long, when=window())\nif (price[1]<c1 and price[1]<c2)            \n    strategy.entry("SELL",strategy.short, when=window())//           /L\'-, \n//                               ,\'-.      `   ````                 /  L \'-, \n//     .                    _,--dMMMM\\        `   ` ` \'`..         /       \'-, \n//     :             _,--,  )MMMMMMMMM),.      `     ,<>          /_      \'-,\' \n//     ;     ___,--. \\MM(    `-\'   )M//MM\\          ,\',.;      .-\'* ;     .\' \n//     |     \\MMMMMM) \\MM\\       ,dM//MMM/     ___ < ,; `.      )`--\'    / \n//     |      \\MM()M   MMM)__   /MM(/MP\'  ___, \\  \\ `  `. `.   /__,    ,\' \n//     |       MMMM/   MMMMMM( /MMMMP\'__, \\     | /      `. `-,_\\     / \n//     |       MM     /MMM---\' `--\'_ \\     |-\'  |/         `./ .\\----.___ \n//     |      /MM\'   `--\' __,-  \\""   |-\'  |_,               `.__) . .F. )-. \n//     |     `--\'       \\   \\    |-\'  |_,     _,-/            J . . . J-\'-. `-., \n//     |         __  \\`. |   |   |         \\    / _           |. . . . \\   `-.  F \n//     |   ___  /  \\  | `|   \'      __  \\   |  /-\'            F . . . . \\     \'` \n//     |   \\  \\ \\  /  |        __  /  \\  |  |,-\'        __,- J . . . . . \\ \n//     |    | /  |/     __,-  \\  ) \\  /  |_,-     __,--\'     |. .__.----,\' \n//     |    |/    ___     \\    |\'.  |/      __,--\'           `.-;;;;;;;;;\\ \n//     |     ___  \\  \\     |   |  `   __,--\'                  /;;;;;;;;;;;;. \n//     |     \\  \\  |-\'\\    \'    __,--\'                       /;;;;;;;;;;;;;;\\ \n// \\   |      | /  |      __,--\'                             `--;;/     \\;-\'\\ \n//  \\  |      |/    __,--\'                                   /  /         \\  \\ \n//   \\ |      __,--\'                                        /  /           \\  \\ \n//    \\|__,--\'                                          _,-;M-K,           ,;-;\\ \n//                                                     <;;;;;;;;           \'-;;;; \n//                                                                                  :D'

class SM89E03B60C9C6B63A(PinePortBase, IStrategy):
    source_id = "SM_89e03b60c9c6b63a"
    source_file = '缓冲布林带动量震荡移动平均线交易策略Momentum-Oscillating-Moving-Average-Trading-Strategy-Based-on-Buffered-Bollinger-Bands.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'hullperiod': 210, 'Width': 200, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2017, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.075
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
