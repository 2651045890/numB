"""batch_011 port of 超级Z量化趋势策略Super-Z-Quantitative-Trend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-20 00:00:00\nend: 2023-11-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n//Original script\n//https://www.tradingview.com/script/wYknDlLx-super-Z/\n\n//@version=4\nstrategy("Super Z strategy - Thanks to Rafael Zioni", shorttitle="Super Z strategy",overlay=true )\nsrc5 = input(close)\n    \ntf = input(1440)\nlen5 = timeframe.isintraday and timeframe.multiplier >= 1 ? \n   tf / timeframe.multiplier * 7 : \n   timeframe.isintraday and timeframe.multiplier < 60 ? \n   60 / timeframe.multiplier * 24 * 7 : 7\n\nma = ema(src5*volume, len5) / ema(volume, len5)\n\n\n//script taken from https://www.tradingview.com/script/kChCRRZI-Hull-Moving-Average/\n\nsrc1 = ma\n\np(src1, len5) =>\n    n = 0.0\n    s = 0.0\n    for i = 0 to len5 - 1\n        w = (len5 - i) * len5\n        n := n + w\n        s := s + src5[i] * w\n    s / n\n\nhm = 2.0 * p(src1, floor(len5 / 2)) - p(src1, len5)\nvhma = p(hm, floor(sqrt(len5)))\nlineColor = vhma > vhma[1] ? color.lime : color.red\nplot(vhma, title="VHMA", color=lineColor ,linewidth=3)\nhColor = true,vis = true\nhu = hColor ? (vhma > vhma[2] ? #00ff00 : #ff0000) : #ff9800\n\nvl = vhma[0]\nll = vhma[1]\nm1 = plot(vl, color=hu, linewidth=1, transp=60)\nm2 = plot(vis ? ll : na,  color=hu, linewidth=2, transp=80)\n\nfill(m1, m2,  color=hu, transp=70)\n//\n\nb = timeframe.isintraday and timeframe.multiplier >= 1 ? \n   60 / timeframe.multiplier * 7 : \n   timeframe.isintraday and timeframe.multiplier < 60 ? \n   60 / timeframe.multiplier * 24 * 7 : 7\n\n\n\n//\nres5 = input("D", type=input.resolution)\n\no = security(syminfo.tickerid, res5, open, barmerge.gaps_off, barmerge.lookahead_on)\nc = security(syminfo.tickerid, res5, close, barmerge.gaps_off, barmerge.lookahead_on)\nhz = security(syminfo.tickerid, res5, high, barmerge.gaps_off, barmerge.lookahead_on)\nl = security(syminfo.tickerid, res5, low, barmerge.gaps_off, barmerge.lookahead_on)\n\n\n\ncol = c >= o ? color.lime : color.red\n\nppo = plot(b ? o >= c ? hz : l : o, color=col, title="Open", style=plot.style_stepline, transp=100)\nppc = plot(b ? o <= c ? hz : l : c, color=col, title="Close", style=plot.style_stepline, transp=100)\n\nplot(b and hz > c ? hz : na, color=col, title="High", style=plot.style_circles, linewidth=2,transp=60)\nplot(b and l < c ? l : na, color=col, title="Low", style=plot.style_circles,linewidth=2, transp=60)\n\nfill(ppo, ppc, col)\n\n//\n// INPUTS //\nst_mult   = input(1,   title = \'SuperTrend Multiplier\', minval = 0, maxval = 100, step = 0.01)\nst_period = input(50, title = \'SuperTrend Period\',     minval = 1)\n\n// CALCULATIONS //\nup_lev =l - (st_mult * atr(st_period))\ndn_lev = hz + (st_mult * atr(st_period))\n\nup_trend   = 0.0\nup_trend   := c[1] > up_trend[1]   ? max(up_lev, up_trend[1])   : up_lev\n\ndown_trend = 0.0\ndown_trend := c[1] < down_trend[1] ? min(dn_lev, down_trend[1]) : dn_lev\n\n// Calculate trend var\ntrend = 0\ntrend := c > down_trend[1] ? 1: c < up_trend[1] ? -1 : nz(trend[1], 1)\n\n// Calculate SuperTrend Line\nst_line = trend ==1 ? up_trend : down_trend\n\n// Plotting\n//plot(st_line[1], color = trend == 1 ? color.green : color.red , style = plot.style_cross, linewidth = 2, title = "SuperTrend")\nbuy=crossover( c, st_line)\nsell=crossunder(c, st_line)\nsignal=input(false)\n\n/////////////// Plotting /////////////// \nplotshape(signal and buy, style=shape.triangleup, size=size.normal, location=location.belowbar, color=color.lime)\nplotshape(signal and sell, style=shape.triangledown, size=size.normal, location=location.abovebar, color=color.red)\n\n\nif (buy)\n    strategy.entry("My Long Entry Id", strategy.long)\n\nif (sell)\n    strategy.entry("My Short Entry Id", strategy.short)'

class SM5EE5E1C1CEE1785B(PinePortBase, IStrategy):
    source_id = "SM_5ee5e1c1cee1785b"
    source_file = '超级Z量化趋势策略Super-Z-Quantitative-Trend-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'tf': 1440, 'res5': 'D', 'st_mult': 1, 'st_period': 50, 'signal': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func', 'loop', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
