"""batch_012 port of 连续阳线短期反转策略Consecutive-Candlestick-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-07 00:00:00\nend: 2023-10-07 00:00:00\nperiod: 3d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//This is part of a series of strategies developed automatically by a online software. I cannot share the site url, which is not related to me in any way, because it is against the TV reules.\n//\n//This strategy was optimized for GBPUSD, timeframe 1D, fixed lots 0.1, initial balance 1000€\n//LOGIC:\n//- LONG ENTRY when previous candle is bear\n//- LONG EXIT: RVI > signal line\n//- SHORT ENTRY when previous candle is bull\n//- SHORT EXIT: RVI <  signal line\n//\n//NOTE: I considered the open of actual candle instead of close otherwise there will be a back shift of 1 candle in pine script\n//\n//Take profit = no\n//Stop loss = no\n\n// strategy("Expert studio strategy 1 - GBPUSD", overlay=false, precision=6, initial_capital=1000,calc_on_every_tick=true, pyramiding=0, default_qty_type=strategy.fixed, default_qty_value=10000, currency=currency.EUR)\n\n//INPUTS\nsrc = input(close, "source")\nmin_body_height = input(42, "Minimum body height", type=input.float)\n//bars_back=input(2, "Consecutive bars of same color")\nrvi_period = input(55, "RVI period")\n\n//CALCULATIONS_____________________________\n//candle color\nbody_height = abs(open - close) / syminfo.mintick\nbody_color = open > close ? color.red : color.green\n\n//da migliorare for i=0 to bars_back-1\n\n//RVI -------- thanks to hecate\np = rvi_period\n\nCO = close - open\nHL = high - low\n\nvalue1 = (CO + 2 * CO[1] + 2 * CO[2] + CO[3]) / 6\nvalue2 = (HL + 2 * HL[1] + 2 * HL[2] + HL[3]) / 6\n\nnum = sum(value1, p)\ndenom = sum(value2, p)\n\nRVI = denom != 0 ? num / denom : 0\n\nRVIsig = (RVI + 2 * RVI[1] + 2 * RVI[2] + RVI[3]) / 6\n\nplot(RVI, color=color.green, style=plot.style_line, linewidth=1)\nplot(RVIsig, color=color.red, style=plot.style_line, linewidth=1)\n\n//----------------------------------\n\nlongCondition = body_height[1] >= min_body_height and body_color[1] == color.red and \n   body_height[0] >= min_body_height and body_color[0] == color.red and \n   RVIsig > RVI\nexitLong = RVI > RVIsig\n\nshortCondition = body_height[1] >= min_body_height and body_color[1] == color.green and \n   body_height[0] >= min_body_height and body_color[0] == color.green and \n   RVIsig < RVI\nexitShort = RVI < RVIsig\n\nif longCondition and strategy.opentrades == 0\n    strategy.entry("Long", strategy.long)\n\nstrategy.close("Long", when=exitLong)\n\nif shortCondition and strategy.opentrades == 0\n    strategy.entry("Short", strategy.short)\n\nstrategy.close("Short", when=exitShort)\n\n// === Backtesting Dates === thanks to Trost\n\ntestPeriodSwitch = input(false, "Custom Backtesting Dates")\ntestStartYear = input(2011, "Backtest Start Year")\ntestStartMonth = input(10, "Backtest Start Month")\ntestStartDay = input(7, "Backtest Start Day")\ntestStartHour = input(0, "Backtest Start Hour")\ntestPeriodStart = timestamp(testStartYear, testStartMonth, testStartDay, testStartHour, 0)\ntestStopYear = input(2018, "Backtest Stop Year")\ntestStopMonth = input(12, "Backtest Stop Month")\ntestStopDay = input(31, "Backtest Stop Day")\ntestStopHour = input(23, "Backtest Stop Hour")\ntestPeriodStop = timestamp(testStopYear, testStopMonth, testStopDay, testStopHour, 0)\ntestPeriod() =>\n    time >= testPeriodStart and time <= testPeriodStop ? true : false\ntestPeriod_1 = testPeriod()\nisPeriod = testPeriodSwitch == true ? testPeriod_1 : true\n// === /END\n\nif not isPeriod\n    strategy.cancel_all()\n    strategy.close_all()\n\n\n\n\n'

class SMConsecutiveCandlestickReversalStrategyf536d7(PinePortBase, IStrategy):
    source_id = "SM_f536d74fbea03a30"
    source_file = '连续阳线短期反转策略Consecutive-Candlestick-Reversal-Strategy.md'
    timeframe = '3d'
    can_short = True
    source_defaults = {'src': 'close', 'min_body_height': 42, 'rvi_period': 55, 'testPeriodSwitch': False, 'testStartYear': 2011, 'testStartMonth': 10, 'testStartDay': 7, 'testStartHour': 0, 'testStopYear': 2018, 'testStopMonth': 12, 'testStopDay': 31, 'testStopHour': 23}
    source_qty_type = 'fixed'
    source_qty_value = 10000
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000
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
