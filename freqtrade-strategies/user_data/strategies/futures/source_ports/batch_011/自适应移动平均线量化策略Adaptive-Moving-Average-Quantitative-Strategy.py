"""batch_011 port of 自适应移动平均线量化策略Adaptive-Moving-Average-Quantitative-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-11-10 00:00:00\nend: 2023-11-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © fondDealer96636\n\n//@version=5\n\nstrategy(\'Automatic Moving Average\', overlay=true, max_bars_back=201, pyramiding=0, currency=currency.USD, default_qty_type=strategy.cash, default_qty_value=10000, initial_capital=10000)\n\n// input\nstart = 20\nlookback = input(20, "Sensitivity", tooltip="Low (High Sensitivity), High (Low Sensitivity).\\n\\nAdjust according to timeframe and asset.")\nsmoothing = input(3, "Smoothing")\nsource = input(close, "Source")\nstartYear = input(2020, "Start year")\nresp = 1\n\nin_date_range = time >= timestamp(syminfo.timezone, startYear, 1, 1, 0, 0)\n\n// global\nvar ix = -1\nvar mal = array.new_int(0)\n\n\n// functions\navg(source, len) =>\n    sum = 0.0\n    for i = 0 to len-1\n        sum += source[i]\n    sum/len\n\nbull = close > open\n\nwick_touch(x) =>\n    bull ? ((close <= x and x <= high) or (low <= x and x <= open)) : ((open <= x and x <= high) or (low <= x and x <= close))\n\nbody_touch(x) =>\n    bull ? (open < x and x < close) : (close < x and x < open)\n\ntouches(t) =>\n    touches = 0\n    for i = 0 to lookback-1\n        touches += t[i] ? 1 : 0\n    touches\n\n\n// local\nix := ix+1\nprev_mal = ix >= 1 ? array.get(mal, ix-1) : start\n\ncma = avg(source, prev_mal)\ncma_p1 = avg(source, prev_mal+1)\ncma_m1 = avg(source, prev_mal-1)\n\nd = touches(wick_touch(cma))\nd_p1 = touches(wick_touch(cma_p1))\nd_m1 = touches(wick_touch(cma_m1))\n\nd_b = touches(body_touch(cma))\nd_p1_b = touches(body_touch(cma_p1))\nd_m1_b = touches(body_touch(cma_m1))\n\nany_body_touch = d_b > 0 or d_p1_b > 0 or d_m1_b > 0\nno_wick_touch = d <= 0 and d_p1 <= 0 and d_m1 <= 0\nwick_maximized = d >= d_p1 and d >= d_m1 ? prev_mal : (d_p1 >= d and d_p1 >= d_m1 ? prev_mal+resp : (d_m1 >= d and d_m1 >= d_p1 ? prev_mal-resp : na))\n\nup = cma > cma[1]\ndown = cma < cma[1]\nagainst_trend = (up and close < cma) or (down and close > cma)\n\nnew_mal = no_wick_touch or against_trend ? prev_mal-resp : (any_body_touch ? prev_mal+resp : wick_maximized)\nnext_mal = na(new_mal) ? prev_mal : new_mal\n\narray.push(mal, next_mal < 2 ? 2 : (next_mal > 200 ? 200 : next_mal))\n\n\n// graph\nscma = ta.ema(cma, smoothing)\n\nuptrend = scma > scma[1]\ndowntrend = scma < scma[1]\n\nplot(scma, "Automatic MA", color=uptrend ? color.green : color.red)\n\nuptrending = close > scma and uptrend\ndowntrending = close < scma and downtrend\n\ndefy = not uptrending and not downtrending\ndefy_cross = defy and body_touch(scma)\n\nbarcolor(uptrending ? color.lime : (downtrending ? color.red : (defy_cross ? color.black : color.white)))\n\n\n// strategy\nchange_to_uptrend = uptrending and downtrend[1]\nchange_to_downtrend = downtrending and uptrend[1]\n\nlong = in_date_range and change_to_uptrend\nshort = in_date_range and change_to_downtrend\n\nif long\n    strategy.entry("Long", strategy.long)\nif short\n    strategy.entry("Short", strategy.short)\n'

class SM8AF8D61FFAD04FF2(PinePortBase, IStrategy):
    source_id = "SM_8af8d61ffad04ff2"
    source_file = '自适应移动平均线量化策略Adaptive-Moving-Average-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'lookback': 20, 'smoothing': 3, 'startYear': 2020}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'array', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
