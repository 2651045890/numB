"""batch_011 port of 超越云层的策略Beyond-The-Clouds-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-03 00:00:00\nend: 2023-11-02 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Noro\n//2018\n\n//@version=2\nstrategy("Noro\'s SuperTrend Strategy v2.0 Limit", shorttitle = "STL str", overlay = true, default_qty_type = strategy.percent_of_equity, default_qty_value = 100, pyramiding = 0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\ncapital = input(100, defval = 100, minval = 1, maxval = 10000, title = "Lot, %")\ncloud = input(25, defval = 25, minval = 5, maxval = 50, title = "cloud, % of ATR")\nFactor = input(title = "Super Trend", defval = 3, minval = 1, maxval = 100)\nATR = input(title = "ATR", defval = 7, minval = 1,maxval = 100)\ncentr = input(true, defval = true, title = "need center of ATR?")\nborder = input(false, defval = false, title = "need border?")\nfromyear = input(1900, defval = 1900, minval = 1900, maxval = 2100, title = "From Year")\ntoyear = input(2100, defval = 2100, minval = 1900, maxval = 2100, title = "To Year")\nfrommonth = input(01, defval = 01, minval = 01, maxval = 12, title = "From Month")\ntomonth = input(12, defval = 12, minval = 01, maxval = 12, title = "To Month")\nfromday = input(01, defval = 01, minval = 01, maxval = 31, title = "From day")\ntoday = input(31, defval = 31, minval = 01, maxval = 31, title = "To day")\n\n//Super Trend ATR 1\nsrc = close\nUp=hl2-(Factor*atr(ATR))\nDn=hl2+(Factor*atr(ATR))\nTUp=close[1]>TUp[1]? max(Up,TUp[1]) : Up\nTDown=close[1]<TDown[1]? min(Dn,TDown[1]) : Dn\nTrend = close > TDown[1] ? 1: close< TUp[1]? -1: nz(Trend[1],1)\nTsl1 = Trend==1? TUp: TDown\nTsl2 = Trend==1? TDown: TUp\nlimit = (Tsl1 - Tsl2) / 100 * cloud\nupcloud = Tsl1 - limit\ndncloud = Tsl2 + limit\n\n//Cloud\nlinecolor = Trend == 1 ? green : red\ncentercolor = centr == true ? blue : na\ncloudcolor = Trend == 1 ? green : red\ncline = (Tsl1 + Tsl2) / 2\nP1 = plot(Tsl1, color = border == false ? na : linecolor , style = line , linewidth = 1,title = "SuperTrend ATR-1")\nP2 = plot(Tsl2, color = border == false ? na : linecolor , style = line , linewidth = 1,title = "SuperTrend ATR-2")\nP3 = plot(cline, color = centercolor , style = line , linewidth = 1,title = "SuperTrend Center")\nP4 = plot(upcloud, color = border == false ? na : linecolor , style = line , linewidth = 1,title = "SuperTrend Center+1")\nP5 = plot(dncloud, color = border == false ? na : linecolor , style = line , linewidth = 1,title = "SuperTrend Center-1")\nfill(P1, P4, color = linecolor == red ? red : lime, transp = 50)\nfill(P2, P5, color = linecolor == red ? red : lime, transp = 50)\n\n//Signals\nup = 0.0\ndn = 0.0\nup := Trend != 1 ? 0 : Trend == 1 and close < open ? close : up[1]\ndn := Trend != -1 ? close * 1000 : Trend == -1 and close > open ? close : dn[1]\n\n//Trading\nsize = strategy.position_size\nlot = 0.0\nlot := size != size[1] ? strategy.equity / close * capital / 100 : lot[1]\nif true\n    strategy.entry("Long", strategy.long, needlong ? lot : 0, limit = up, when = (Trend == 1 and time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n    strategy.entry("Short", strategy.short, needshort ? lot : 0, limit = dn, when = (Trend == -1 and time > timestamp(fromyear, frommonth, fromday, 00, 00) and time < timestamp(toyear, tomonth, today, 23, 59)))\n\nif time > timestamp(toyear, tomonth, today, 23, 59)\n    strategy.close_all()'

class SM0DD00F8B1E5232E0(PinePortBase, IStrategy):
    source_id = "SM_0dd00f8b1e5232e0"
    source_file = '超越云层的策略Beyond-The-Clouds-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'capital': 100, 'cloud': 25, 'Factor': 3, 'ATR': 7, 'centr': True, 'border': False, 'fromyear': 1900, 'toyear': 2100, 'tomonth': 12, 'today': 31}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
