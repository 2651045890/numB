"""batch_011 port of 移动平均线双轨带牛熊策略CBMA-Bollinger-Bands-Breaker-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-29 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy(title="CBMA Bollinger Bands Strategy directed [ChuckBanger]", shorttitle="CBMA BB CB", \n   overlay=true )\n\n\nlength = input(title="Length", type=input.integer, defval=12, minval=1)\nregular = input(title="Regular BB Or CBMA?", type=input.bool, defval=false)\nsrc = input(title="Source", type=input.source, defval=close)\nmult = input(title="Multipler", type=input.float, defval=2.3, minval=.001, maxval=50, step=.1)\nemaLen = input(title="EMA Length", type=input.integer, defval=11, minval=1)\nemaGL = input(title="EMA Gain Limit", type=input.integer, defval=50, minval=1)\nhighlight = input(title="Highlight On/Off", type=input.bool, defval=true)\n\ndirection = input(0, title = "Strategy Direction", type=input.integer, minval=-1, maxval=1)\n\nstrategy.risk.allow_entry_in(direction == 0 ? strategy.direction.all : (direction < 0 ? strategy.direction.short : strategy.direction.long))\n\n//strategy.risk.max_drawdown(50, strategy.percent_of_equity)\n\ncalc_hma(src, length) =>\n    hullma = wma(2*wma(src, length/2)-wma(src, length), round(sqrt(length)))\n    hullma\n\ncalc_cbma(price, length, emaLength, emaGainLimit) =>\n    alpha = 2 / (emaLength + 1)\n    ema = ema(price, emaLength)\n    int leastError = 1000000\n    \n    float ec = 0\n    float bestGain = 0\n    \n    for i = emaGainLimit to emaGainLimit\n        gain = i / 10\n        ec := alpha * ( ema + gain * (price - nz(ec[1])) ) + (1 - alpha) * nz(ec[1])\n        error = price - ec\n        if (abs(error) < leastError)\n            leastError = abs(error)\n            bestGain = gain\n    \n    ec := alpha * ( ema + bestGain * (price - nz(ec[1])) ) + (1 - alpha) * nz(ec[1])\n    hull = calc_hma(price, length)\n    \n    cbma = (ec + hull) / 2\n    cbma\n\ncbma = calc_cbma(src, length, emaLen, emaGL)\nbasis = regular ? sma(src, length) : cbma\ndev = mult * stdev(src, length)\nupper = basis + dev\nlower = basis - dev\ncbmaColor = fixnan(highlight and not regular ? cbma > high ? color.purple : cbma < low ? color.aqua : na : color.red)\nplot(basis, color=cbmaColor)\np1 = plot(upper, color=color.blue)\np2 = plot(lower, color=color.blue)\nfill(p1, p2)\n\nif (crossover(src, lower))\n    strategy.entry("CBMA_BBandLE", strategy.long, stop=lower, oca_name="BollingerBands", comment="CBMA_BBandLE")\nelse\n    strategy.cancel(id="CBMA_BBandLE")\n\nif (crossunder(src, upper))\n    strategy.entry("CBMA_BBandSE", strategy.short, stop=upper, oca_name="BollingerBands", comment="CBMA_BBandSE")\nelse\n    strategy.cancel(id="CBMA_BBandSE")\n'

class SME46185B169F065D0(PinePortBase, IStrategy):
    source_id = "SM_e46185b169f065d0"
    source_file = '移动平均线双轨带牛熊策略CBMA-Bollinger-Bands-Breaker-Strategy.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'length': 12, 'regular': False, 'mult': 2.3, 'emaLen': 11, 'emaGL': 50, 'highlight': True, 'direction': 0}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'loop', 'entry_price_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
