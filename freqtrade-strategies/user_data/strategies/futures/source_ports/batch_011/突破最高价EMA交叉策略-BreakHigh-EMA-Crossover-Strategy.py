"""batch_011 port of 突破最高价EMA交叉策略-BreakHigh-EMA-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-01 00:00:00\nend: 2024-02-29 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// @version = 5\nstrategy(title="BreakHigh Strategy", overlay=true)\nPeriod = input.int(34, "Number of previous bars(34,52 Recommend)")\nshowbg = input(defval = false,title = "Show BackGround Color")\nshowema = input(defval = true ,title = "Show Line")\nMarkBuySig = input(defval = true ,title = "Show Buy/Sell Signal")\n\nRisk_Per_Trade = input(2.5, \'% of Risk Per Trade\') / 100  // Risk% Per Trade Switch\nSLDAY = input(title=\'Lowest price of the previous number of bars\', defval=9)\nBuysig = input(defval=true, title=\'Start Strategy\')\nUseSl = input(defval=false, title=\'Use Stoploss Price\')\nCompound = input(defval = false ,title =  "Compound Profit")\nxtf = input.timeframe(title=\'** Fix chart to which time frame ? **)\', defval=\'D\')\n\n\n//BUY\nfloat buyLine = na\nbuyLine := ta.highest(high,Period)[1] \nplot(showema ? buyLine : na, linewidth=1, style=plot.style_linebr, color=color.new(color.green, 0))\n\n//SELL\noutput = ta.ema(close, Period)\nshow = request.security(syminfo.tickerid, xtf, output)\nFastL = plot(showema ? show : na, color=color.new(color.white, 0), linewidth=2, title=\'Slow EMA\')\n\n//Buy-Sell Signal\nGreen = close > buyLine   // Buy\nRed = close < show // Sell\n\nbuycond = Green and Green[1] == 0\nsellcond = Red and Red[1] == 0\n\nbullish = ta.barssince(buycond) < ta.barssince(sellcond)\nbearish = ta.barssince(sellcond) < ta.barssince(buycond)\n\nbuy = bearish[1] and buycond\nsell = bullish[1] and sellcond\n\nplotshape(MarkBuySig ? buy : na, style=shape.labelup, text=\'Buy Next Bar\', textcolor=color.new(color.black, 0), location=location.belowbar, color=color.new(color.green, 0))\nplotshape(MarkBuySig ? sell : na, style=shape.labeldown, text=\'Sell Next Bar\', textcolor=color.new(color.black, 0), location=location.abovebar, color=color.new(color.red, 0))\nbgcolor(showbg ? bullish ? color.new(color.green,90) : color.new(color.red,90) : na )\n\n\n// === BACKTEST RANGE === //\nuse_date_range = input(true)\nFromYear = input.int(defval=2012, title=\'From Year\', minval=1950)\nFromMonth = input.int(defval=1, title=\'From Month\', minval=1)\nFromDay = input.int(defval=1, title=\'From Day\', minval=1)\nToYear = input.int(defval=9999, title=\'To Year\', minval=1950)\nToMonth = input.int(defval=1, title=\'To Month\', minval=1)\nToDay = input.int(defval=1, title=\'To Day\', minval=1)\nin_date_range = use_date_range ? time > timestamp(FromYear, FromMonth, FromDay, 00, 00) and time < timestamp(ToYear, ToMonth, ToDay, 23, 59) : true\n\n//****************************************************************************//\n\n//////////////////////////////////////////////\n//    define strategy entry / exit          //\n//////////////////////////////////////////////\n\n//****************************************************************************//\n// LONG CONDITIONS\n\nSelect_Long_Condition_1 = close > buyLine // Buy when Have Signal\nOpen_Long_Condition = Select_Long_Condition_1 and strategy.opentrades == 0\n\n//****************************************************************************//\n// STOP LOSS Price\n\nfloat longSL = na\nlongSL := Open_Long_Condition ? ta.lowest(low, SLDAY)[1] : longSL[1]  \n\n\n//****************************************************************************//\n// Cal StopLoss\n\nLong_Entry_Price = close\nDiff_OPEN_to_SL = math.abs(Long_Entry_Price - longSL)\n\n// Exit CONDITIONS\n\nExit_Long_Condition = close < show // Sell when Have Signal\n\n//****************************************************************************//\n// POSITION SIZE CAP\n\nstrategy.initial_capital = 50000\n\nfloat portSize = Compound ? strategy.netprofit + strategy.initial_capital : strategy.initial_capital\nfloat LossAmoutUnit = portSize * Risk_Per_Trade //50\nfloat PercentSL = ( Diff_OPEN_to_SL / Long_Entry_Price ) * 100\nfloat PositionSize = LossAmoutUnit / Diff_OPEN_to_SL\n\n\n//****************************************************************************//\n// ENTRY/EXIT\n\nif Buysig\n    if Open_Long_Condition and in_date_range \n        strategy.entry(\'LONG\', strategy.long, qty=PositionSize)\n\n\nif Exit_Long_Condition and in_date_range\n    strategy.close(\'LONG\')\nif close < longSL and UseSl\n    strategy.close(\'LONG\')\n\n//****************************************************************************//\n// PLOT STOP LOSS\n\nlongPlotSL = strategy.opentrades > 0 and strategy.position_size > 0 ? longSL : na\n// label.new(bar_index, high, text=str.tostring(longPlotSL),color=color.white, textcolor=color.black)\nplot(longPlotSL, title="", linewidth=2, style=plot.style_linebr, color=color.new(color.red, 0))\n\n\n\n//****************************************************************************//\n\n'

class SMCF28E2998FCD4089(PinePortBase, IStrategy):
    source_id = "SM_cf28e2998fcd4089"
    source_file = '突破最高价EMA交叉策略-BreakHigh-EMA-Crossover-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'Period': 34, 'showbg': False, 'showema': True, 'MarkBuySig': True, 'Risk_Per_Trade': 2.5, 'SLDAY': 9, 'Buysig': True, 'UseSl': False, 'Compound': False, 'xtf': 'D', 'use_date_range': True, 'FromYear': 2012, 'FromMonth': 1, 'FromDay': 1, 'ToYear': 9999, 'ToMonth': 1, 'ToDay': 1}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'broker_state', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
