"""batch_011 port of 趋势ATR横向突破策略Honey-Trend-ATR-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-01 00:00:00\nend: 2023-11-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(title="Strategy - Bobo PATR Swing", overlay=true, default_qty_type = strategy.fixed, default_qty_value = 1, initial_capital = 10000)\n\n// === STRATEGY RELATED INPUTS AND LOGIC ===\nPivottimeFrame = input(title="Pivot Timeframe",  defval="D")\nATRSDtimeFrame = input(title="ATR Band Timeframe (Lower timeframe = wider bands)",  defval="D")\nlen = input(title="ATR lookback (Lower = bands more responsive to recent price action)",  defval=13)\nmyatr = atr(len)\ndailyatr = request.security(syminfo.tickerid, ATRSDtimeFrame, myatr[1])\natrdiv = input(title="ATR divisor (Lower = wider bands)", type=float, defval=2)\npivot0 = (high[1] + low[1]  + close[1]) / 3\npivot = request.security(syminfo.tickerid, PivottimeFrame, pivot0)\nupperband1 = (dailyatr / atrdiv) + pivot\nlowerband1 = pivot - (dailyatr / atrdiv)\nmiddleband = pivot\n\n// == TREND CALC ===\ni1=input(2, "Momentum Period", minval=1) //Keep at 2 usually\ni2=input(20, "Slow Period", minval=1)\ni3=input(5, "Fast Period", minval=1)\ni4=input(3, "Smoothing Period", minval=1)\ni5=input(4, "Signal Period", minval=1)\ni6=input(50, "Extreme Value", minval=1)\nhiDif = high - high[1]\nloDif = low[1] - low\nuDM = hiDif > loDif and hiDif > 0 ? hiDif : 0\ndDM =  loDif > hiDif and loDif > 0 ? loDif : 0\nATR = rma(tr(true), i1)\nDIu = 100 * rma(uDM, i1) / ATR\nDId = 100 * rma(dDM, i1) / ATR\nHLM2 =  DIu - DId\nDTI = (100 * ema(ema(ema(HLM2, i2), i3), i4)) /  ema(ema(ema(abs(HLM2), i2), i3), i4)\nsignal = ema(DTI, i5)\n\n\n// === RISK MANAGEMENT INPUTS ===\ninpTakeProfit   = input(defval = 0, title = "Take Profit (In Market MinTick Value)", minval = 0)\ninpStopLoss     = input(defval = 100, title = "Stop Loss (In Market MinTick Value)", minval = 0)\n\n// === RISK MANAGEMENT VALUE PREP ===\n// if an input is less than 1, assuming not wanted so we assign \'na\' value to disable it.\nuseTakeProfit   = inpTakeProfit  >= 1 ? inpTakeProfit  : na\nuseStopLoss     = inpStopLoss    >= 1 ? inpStopLoss    : na\n\n// === STRATEGY - LONG POSITION EXECUTION ===\nenterLong = (((low<=lowerband1) and (close >lowerband1)) or ((open <= lowerband1) and (close > lowerband1))) and (strategy.opentrades <1) and (atr(3) > atr(50)) and (signal>signal[3])\nexitLong = (high > middleband)\nstrategy.entry(id = "Long", long = true, when = enterLong) \nstrategy.close(id = "Long", when = exitLong)\n\n// === STRATEGY - SHORT POSITION EXECUTION ===\nenterShort = (((high>=upperband1) and (close < upperband1)) or ((open >= upperband1) and (close < upperband1))) and (strategy.opentrades <1) and (atr(3) > atr(50)) and (signal<signal[3])\nexitShort = (low < middleband)\nstrategy.entry(id = "Short", long = false, when = enterShort)\nstrategy.close(id = "Short", when = exitShort)\n\n// === STRATEGY RISK MANAGEMENT EXECUTION ===\nstrategy.exit("Exit Long", from_entry = "Long", profit = useTakeProfit, loss = useStopLoss)\nstrategy.exit("Exit Short", from_entry = "Short", profit = useTakeProfit, loss = useStopLoss)\n\n// === CHART OVERLAY ===\nplot(upperband1, color=#C10C00, linewidth=3)\nplot(lowerband1, color=#23E019, linewidth=3)\nplot(middleband, color=#00E2E2, linewidth=3)\n//plot(strategy.equity, title="equity", color=red, linewidth=2, style=areabr)'

class SME24530E122669DCA(PinePortBase, IStrategy):
    source_id = "SM_e24530e122669dca"
    source_file = '趋势ATR横向突破策略Honey-Trend-ATR-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'PivottimeFrame': 'D', 'ATRSDtimeFrame': 'D', 'len': 13, 'atrdiv': 2, 'i1': 2, 'i2': 20, 'i3': 5, 'i4': 3, 'i5': 4, 'i6': 50, 'inpTakeProfit': 0, 'inpStopLoss': 100}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'broker_state', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
