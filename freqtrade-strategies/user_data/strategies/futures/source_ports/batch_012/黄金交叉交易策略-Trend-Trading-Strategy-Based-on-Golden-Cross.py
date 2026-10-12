"""batch_012 port of 黄金交叉交易策略-Trend-Trading-Strategy-Based-on-Golden-Cross.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-15 00:00:00\nend: 2023-11-22 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nstrategy(title = " Strategy PyramiCover",\n         shorttitle = "S-PC",\n         overlay = true,\n         precision = 8,\n         calc_on_order_fills = true,\n         calc_on_every_tick = true,\n         backtest_fill_limits_assumption = 0,\n         default_qty_type = strategy.fixed,\n         default_qty_value = 2,\n         initial_capital = 10000,\n         pyramiding=50,\n         currency = currency.USD,\n         linktoseries = true)\n\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nbackTestSectionFrom = input(title = "═══════════════ From ═══════════════", defval = true, type = input.bool)\n\nFromMonth         = input(defval = 1, title = "Month", minval = 1)\nFromDay           = input(defval = 1, title = "Day", minval = 1)\nFromYear          = input(defval = 2014, title = "Year", minval = 2014)\n\nbackTestSectionTo = input(title = "════════════════ To ════════════════", defval = true, type = input.bool)\nToMonth           = input(defval = 31, title = "Month", minval = 1)\nToDay             = input(defval = 12, title = "Day", minval = 1)\nToYear            = input(defval = 9999, title = "Year", minval = 2014)\n\nbackTestPeriod() => (time > timestamp(FromYear, FromMonth, FromDay, 00, 00)) and (time < timestamp(ToYear, ToMonth, ToDay, 23, 59))\n\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nper = input(14,title="? Length")\n//\nup = 0.0\nnup= 0.0\nlowl = 0.0\nnin = 0.0\n//\nsrl=wma(close,8)\nsrr = sma(close,8)\nsr = 2*srl - srr\n//\nsrsl=wma(close,20)\nsrsr= sma(close,20)\nsrsignal = 2*srsl - srsr\n//\nif sr>srsignal\n    up := highest(sr,round(150))\n    nup :=highest(srsignal,round(20))\nelse\n    up := highest(srsignal,round(150))\n    nup := highest(sr,round(20))\n//\nif sr<srsignal\n    lowl := lowest(sr,round(150))\n    nin := lowest(srsignal,round(20))\nelse\n    lowl := lowest(sr,round(150))\n    nin := lowest(srsignal,round(20))\n//reg alexgrover\nf_reg(src,length)=>\n    x = bar_index\n    y = src\n    x_ = sma(x, length)\n    y_ = sma(y, length)\n    mx = stdev(x, length)\n    my = stdev(y, length)\n    c = correlation(x, y, length)\n    slope = c * (my / mx)\n    inter = y_ - slope * x_\n    reg = x * slope + inter\n    reg\n//\nup_=f_reg(up,per)\nlowl_=f_reg(lowl,per)\nnup_=f_reg(nup,per)\nnin_=f_reg(nin,per)\n//\nplot(sr, title=\'SR\', color=color.green, linewidth=2, style=plot.style_line,transp=0)\nplot(srsignal, title=\'SR-Signal\', color=color.red, linewidth=2, style=plot.style_line,transp=0)\nplot(up_, title=\'Upper limit\', color=color.blue, linewidth=3, style=plot.style_line,transp=0)\nplot(lowl_, title=\'Lower limit\', color=color.blue, linewidth=3, style=plot.style_line,transp=0)\na=plot(nup_, title=\'Neuronal Upper\', color=color.gray, linewidth=1, style=plot.style_line,transp=0)\nb=plot(nin_, title=\'Neuronal Lower\', color=color.gray, linewidth=1, style=plot.style_line,transp=0)\nfill(a, b, color=color.gray)\nplotshape(crossunder(sr,nup_)? sr+atr(20):na, title="Sell", text="?", location=location.absolute, style=shape.labeldown, size=size.tiny, color=color.red, textcolor=color.black,transp=0)\nplotshape(crossover(sr,nin_)? sr-atr(20):na, title="Buy", text="?", location=location.absolute, style=shape.labelup, size=size.tiny, color=color.green, textcolor=color.black,transp=0)\n\n//\n// ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ //\n\nif backTestPeriod()\n\n    strategy.entry("Buy", true, 1, when = crossover(sr,nin_)) \n    strategy.entry("Short", false, 1, when = crossunder(sr,nup_))\n'

class SMTrendTradingStrategyBasedonGoldenCrossa98e56(PinePortBase, IStrategy):
    source_id = "SM_a98e5635860517d6"
    source_file = '黄金交叉交易策略-Trend-Trading-Strategy-Based-on-Golden-Cross.md'
    timeframe = '30m'
    can_short = False
    source_defaults = {'backTestSectionFrom': True, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2014, 'backTestSectionTo': True, 'ToMonth': 31, 'ToDay': 12, 'ToYear': 9999, 'per': 14}
    source_qty_type = 'fixed'
    source_qty_value = 2
    source_commission_percent = 0.0
    source_pyramiding = 50
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
