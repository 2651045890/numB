"""batch_012 port of 黄金交叉多头趋势跟踪策略Golden-Cross-Uptrend-Tracking-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-26 00:00:00\nend: 2024-01-02 00:00:00\nperiod: 30m\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// @version=4\n//\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// www.tradingview.com/u/TradeFab/\n// www.tradefab.com\n// ___  __        __   __  __       __\n//  |  |__)  /\\  |  \\ |__ |__  /\\  |__)\n//  |  |  \\ /~~\\ |__/ |__ |   /~~\\ |__)\n//\n// DISCLAIMER: Futures, stocks and options trading involves substantial risk of loss \n// and is not suitable for every investor. You are responsible for all the risks and \n// financial resources you use and for the chosen trading system.\n// Past performance is not indicative for future results. In making an investment decision,\n// traders must rely on their own examination of the entity making the trading decisions!\n//\n// TradeFab\'s Golden Cross Strategy.\n// The strategy goes long when the faster SMA 50 (the simple moving average of the last 50 bars) crosses\n// above the SMA 200. Orders are closed when the SMA 50 crosses below SMA 200. The strategy does not short.\n//\nVERSION = "1.2"\n// 1.2 FB 2020-02-09 converted to Pine version 4\n// 1.1 FB 2017-01-15 added short trading\n// 1.0 FB 2017-01-13 basic version using SMAs\n//\nstrategy(\n   title        = "TFs Golden Cross " + VERSION, \n   shorttitle   = "TFs Golden Cross " + VERSION, \n   overlay      = true\n   )\n\n\n///////////////////////////////////////////////////////////\n// === INPUTS ===\n///////////////////////////////////////////////////////////\ninFastSmaPeriod     = input(title="Fast SMA Period", type=input.integer, defval=50, minval=1)\ninSlowSmaPeriod     = input(title="Slow SMA Period", type=input.integer, defval=200, minval=1)\n\n// backtest period\ntestStartYear       = input(title="Backtest Start Year",    type=input.integer, defval=2019, minval=2000)\ntestStartMonth      = input(title="Backtest Start Month",   type=input.integer, defval=1, minval=1, maxval=12)\ntestStartDay        = input(title="Backtest Start Day",     type=input.integer, defval=1, minval=1, maxval=31)\ntestStopYear        = input(title="Backtest Stop Year",     type=input.integer, defval=2099, minval=2000)\ntestStopMonth       = input(title="Backtest Stop Month",    type=input.integer, defval=12, minval=1, maxval=12)\ntestStopDay         = input(title="Backtest Stop Day",      type=input.integer, defval=31, minval=1, maxval=31)\n\n\n///////////////////////////////////////////////////////////\n// === LOGIC ===\n///////////////////////////////////////////////////////////\nsmaFast = sma(close, inFastSmaPeriod)\nsmaSlow = sma(close, inSlowSmaPeriod)\n\nbullishCross = crossover (smaFast, smaSlow)\nbearishCross = crossunder(smaFast, smaSlow)\n\n// detect valid backtest period\nisTestPeriod() => true\n\n\n///////////////////////////////////////////////////////////\n// === POSITION EXECUTION ===\n///////////////////////////////////////////////////////////\nstrategy.entry("long",  strategy.long,  when=bullishCross)\nstrategy.entry("short", strategy.short, when=bearishCross)\n\n\n///////////////////////////////////////////////////////////\n// === PLOTTING ===\n///////////////////////////////////////////////////////////\n// background color\nnopColor = color.new(color.gray, 50)\nbgcolor(not isTestPeriod() ? nopColor : na)\n\nbartrendcolor = \n   close > smaFast and \n   close > smaSlow and \n   change(smaSlow) > 0 \n       ? color.green \n       : close < smaFast and \n         close < smaSlow and \n         change(smaSlow) < 0 \n             ? color.red \n             : color.blue\nbarcolor(bartrendcolor)\nplot(smaFast, color=change(smaFast) > 0 ? color.green : color.red, linewidth=2)\nplot(smaSlow, color=change(smaSlow) > 0 ? color.green : color.red, linewidth=2)\n\n// label\nposColor = color.new(color.green, 75)\nnegColor = color.new(color.red, 75)\ndftColor = color.new(color.blue, 75)\nposProfit= (strategy.position_size != 0) ? (close * 100 / strategy.position_avg_price - 100) : 0.0\nposDir   = (strategy.position_size  > 0) ? "long" : strategy.position_size < 0 ? "short" : "flat"\nposCol   = (posProfit > 0) ? posColor : (posProfit < 0) ? negColor : dftColor\n\nvar label lb = na\nlabel.delete(lb)\nlb := label.new(bar_index, max(high, highest(5)[1]),\n   color=posCol,\n   text="Pos: "+ posDir +\n      "\\nPnL: "+tostring(posProfit, "#.##")+"%" +\n      "\\nClose: "+tostring(close, "#.##"))\n  \n'

class SMGoldenCrossUptrendTrackingStrategyaa3ddc(PinePortBase, IStrategy):
    source_id = "SM_aa3ddcf8d6c9aa19"
    source_file = '黄金交叉多头趋势跟踪策略Golden-Cross-Uptrend-Tracking-Strategy.md'
    timeframe = '30m'
    can_short = True
    source_defaults = {'inFastSmaPeriod': 50, 'inSlowSmaPeriod': 200, 'testStartYear': 2019, 'testStartMonth': 1, 'testStartDay': 1, 'testStopYear': 2099, 'testStopMonth': 12, 'testStopDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
