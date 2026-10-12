"""batch_012 port of 量化黄金交叉策略Quantitative-Golden-Cross-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-14 00:00:00\nend: 2023-11-15 03:00:00\nperiod: 1m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy(title="@DankCoins - Customized Net Volume")\nsrc = input(defval = close, title = "VA Source")\nnv = change(src) > 0 ? volume : change(src) < 0 ? -volume : 0*volume\n\n\n\n// Inputs //\nVHigh = input(defval = 50, title = "VHigh Amount")\nVLow = input(defval = -50, title = "VLow Amount")\n\n\n// === INPUT BACKTEST RANGE ===\nFromMonth = input(defval = 1, title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1, title = "From Day", minval = 1, maxval = 31)\nFromYear  = input(defval = 2018, title = "From Year", minval = 2012)\nToMonth   = input(defval = 1, title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1, title = "To Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999, title = "To Year", minval = 2012)\n\nMAV1 = sma(volume, 3)\nMAV2 = -sma(volume, 3)\n\nenterShort = crossunder(nv, MAV1)\nexitShort = crossunder(nv, MAV2)\nenterLong = crossover(nv, MAV2)\nexitLong = crossover(nv, MAV1)\n\n// Time Function \nstart     = timestamp(FromYear, FromMonth, FromDay, 00, 00)  // backtest start window\nfinish    = timestamp(ToYear, ToMonth, ToDay, 23, 59)        // backtest finish window\nwindow()  => time >= start and time <= finish ? true : false // create function "within window of time"\n\n\nstrategy.entry(id="Long Entry", long=true, when=enterLong and window())\nstrategy.entry(id="Short Entry", long=false, when=enterShort and window())\nstrategy.exit("Exit Long", from_entry = "Long Entry",  when=exitLong and window())\nstrategy.exit("Exit Short", from_entry = "Short Entry",  when=exitShort and window())\n\n\n// Plot\nplot(nv, color=blue, title="NV")\nplot(VHigh, color=red)\nplot(VLow, color=red)\nplot(MAV1, color=green)\nplot(MAV2, color=green)\n'

class SMQuantitativeGoldenCrossStrategy89160e(PinePortBase, IStrategy):
    source_id = "SM_89160e810e78db67"
    source_file = '量化黄金交叉策略Quantitative-Golden-Cross-Strategy.md'
    timeframe = '1m'
    can_short = False
    source_defaults = {'src': 'close', 'VHigh': 50, 'VLow': -50, 'FromMonth': 1, 'FromDay': 1, 'FromYear': 2018, 'ToMonth': 1, 'ToDay': 1, 'ToYear': 9999}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
