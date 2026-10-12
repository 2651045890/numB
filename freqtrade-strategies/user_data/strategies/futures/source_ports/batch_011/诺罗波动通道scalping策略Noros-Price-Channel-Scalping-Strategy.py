"""batch_011 port of 诺罗波动通道scalping策略Noros-Price-Channel-Scalping-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-10 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n\n//@version=2\nstrategy("Noro\'s Bands Scalper Strategy v1.0", shorttitle = "Scalper str 1.0", overlay=true, default_qty_type = strategy.percent_of_equity, default_qty_value=100.0, pyramiding=0)\n\n//Settings\nneedlong = input(true, defval = true, title = "Long")\nneedshort = input(true, defval = true, title = "Short")\nlen = input(20, defval = 20, minval = 2, maxval = 200, title = "Period")\nneedbb = input(true, defval = true, title = "Show Bands")\nneedbg = input(true, defval = true, title = "Show Background")\nsrc = close\n\n//PriceChannel\nlasthigh = highest(src, len)\nlastlow = lowest(src, len)\ncenter = (lasthigh + lastlow) / 2\n\n//Distance\ndist = abs(src - center)\ndistsma = sma(dist, len)\nhd = center + distsma\nld = center - distsma\nhd2 = center + distsma * 2\nld2 = center - distsma * 2\n\n//Trend\ntrend = close < ld and high < hd ? -1 : close > hd and low > ld ? 1 : trend[1]\n\n//Lines\ncolo = needbb == false ? na : black\nplot(hd, color = colo, linewidth = 1, transp = 0, title = "High band")\nplot(center, color = colo, linewidth = 1, transp = 0, title = "center")\nplot(ld, color = colo, linewidth = 1, transp = 0, title = "Low band")\n\n//Background\ncol = needbg == false ? na : trend == 1 ? lime : red\nbgcolor(col, transp = 80)\n\n//Signals\nbar = close > open ? 1 : close < open ? -1 : 0\nup7 = trend == 1 and bar == -1 and bar[1] == -1 ? 1 : 0\ndn7 = trend == 1 and bar == 1 and bar[1] == 1 and close > strategy.position_avg_price ? 1 : 0\nup8 = trend == -1 and bar == -1 and bar[1] == -1 and close < strategy.position_avg_price ? 1 : 0\ndn8 = trend == -1 and bar == 1 and bar[1] == 1 ? 1 : 0\n\nif up7 == 1 or up8 == 1\n    strategy.entry("Long", strategy.long, needlong == false ? 0 : trend == -1 ? 0 : na)\n\nif dn7 == 1 or dn8 == 1\n    strategy.entry("Short", strategy.short, needshort == false ? 0 : trend == 1 ? 0 : na)'

class SM8535DF71A1795897(PinePortBase, IStrategy):
    source_id = "SM_8535df71a1795897"
    source_file = '诺罗波动通道scalping策略Noros-Price-Channel-Scalping-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'needlong': True, 'needshort': True, 'len': 20, 'needbb': True, 'needbg': True}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
