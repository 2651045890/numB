"""batch_011 port of 趋势追踪移动平均RSI策略Trend-Tracking-Moving-Average-RSI-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-16 00:00:00\nend: 2023-11-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © mattehalen\n\n// INPUT per TIMEFRAME\n// 5min     = Legnth = 9, Source = ohlc4,MaxLoss = 1000 TrendMA = 200, ShortMA = 4, LongMA = 10\n// 30min    = Legnth = 7, Source = ohlc4,MaxLoss = 1000 TrendMA = 200, ShortMA = 10, LongMA = 20\n\nstrategy("Mathias & Christer Timeframe RSI", shorttitle="M&C_RSI",overlay=true, process_orders_on_close = true, default_qty_type =  strategy.percent_of_equity, default_qty_value = 100)\nlen = input(9, title="Length", type=input.integer)\nsrc = input(ohlc4, title="Source", type=input.source)\n//show4h = input(true, title="show 4h", type=input.bool)\nmaxLoss = input(3000)\n\nrsiCurrent = rsi(src, len)\n//rsi4h = security(syminfo.ticker, "240", rsi(src, len))\nrsi4h   = rsi(src, len)\n\n//--------------------------------------------------\n//MA\ntrendMAInput = input(200, title="trendMA", type=input.integer)\nshortMAInput = input(30, title="shortMA", type=input.integer)\nlongMAInput = input(50, title="longMA", type=input.integer)\n\ntrendMA = ema(close,trendMAInput)\nshortMA = ema(close,shortMAInput)\nlongMA  = ema(close,longMAInput)\nplot(trendMA, color=color.black, linewidth=5)\nplot(shortMA, color=color.red, linewidth=2)\nplot(longMA, color=color.green, linewidth=2)\nbgcolor(crossunder(shortMA,longMA) ? color.black : na, transp=10)\n\n//--------------------------------------------------\n//RSI\nBuySignalBarssince = barssince(rsi4h[1]<rsi4h[0] and rsi4h[1]<20)\nBuySignal       = (rsi4h[1]<rsi4h[0] and rsi4h[1]<20 and BuySignalBarssince[1]>10)\nBuySignalOut   = crossunder(longMA[1],shortMA[1])\nbgcolor(BuySignal ? color.green : na, transp=70)\nbgcolor(BuySignalOut ? color.green : na, transp=10)\n\n\n\nSellSignalBarssince = barssince(rsi4h[1]>rsi4h[0] and rsi4h[1]>80)\nSellSignal      = (rsi4h[1]>rsi4h[0] and rsi4h[1]>80 and SellSignalBarssince[1]>10)\nSellSignalOut   = crossunder(shortMA[1],longMA[1])\nbgcolor(SellSignal ? color.red : na, transp=70)\nbgcolor(SellSignalOut ? color.red : na, transp=10)\n\n\nif BuySignal\n    strategy.close("short", comment = "Exit short")\n    strategy.entry("long", true)\n    strategy.exit("Max Loss", "long", loss = maxLoss)\n\nif BuySignalOut\n    strategy.close("long", comment = "Exit Long")\nif SellSignal\n    // Enter trade and issue exit order on max loss.\n    strategy.close("long", comment = "Exit Long")\n    strategy.entry("short", false)\n    strategy.exit("Max Loss", "short", loss = maxLoss)\nif SellSignalOut\n    // Force trade exit.\n    strategy.close("short", comment = "Exit short")\n    \n//--------------------------------------------------\n//ATR\nMyAtr = atr(10)\nAtrFactor = 10\nmySLBuy  = close[BuySignalBarssince]\nmySLSell = close[SellSignalBarssince]\n\nplotchar(BuySignal, "BuySignal", "⬆", location.belowbar, color.lime,size =size.huge )\nplotchar(BuySignalOut, "BuySignalOut", "█", location.belowbar, color.lime,size =size.small)\nplotchar(SellSignal, "SellSignal", "⬇", location.abovebar ,color.red,size =size.huge)\nplotchar(SellSignalOut, "SellSignalOut", "█", location.abovebar, color.red,size =size.small)\n\n\n'

class SMF0BB5138ECB956DF(PinePortBase, IStrategy):
    source_id = "SM_f0bb5138ecb956df"
    source_file = '趋势追踪移动平均RSI策略Trend-Tracking-Moving-Average-RSI-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'len': 9, 'maxLoss': 3000, 'trendMAInput': 200, 'shortMAInput': 30, 'longMAInput': 50}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
