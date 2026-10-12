"""batch_012 port of 量化交易中的支撑阻力云形态指标Quant-Trading-Support-and-Resistance-Cloud-Indicator.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-10 00:00:00\nend: 2024-01-17 00:00:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("[IND] rang3r", overlay=true)\nentP = input(50, "Entry Period: ")\nexP = input(25, "Exit period: ")\nsensitivity = input(0.9999, "Sensitivity")\nperiodHigh = 0.0\nperiodLow = 0.0\nepH = 0.0\nepL = 0.0\n\n    \n//Entry Trades\nfor i = 1 to (entP+1)\n    if i == 1 \n        periodHigh:=high[i]\n    else\n        if periodHigh < high[i]\n            periodHigh:=high[i]\n    \n\nfor i = 1 to (entP+1)\n    if i == 1 \n        periodLow:=low[i]\n    else\n        if periodLow > low[i]\n            periodLow:=low[i]\n                \ns = high[1] > periodHigh*sensitivity and open > close //and (close[1] > open[1] ? open[1] : close[1]) > close\nl = low[1] < periodLow*(1/sensitivity) and close > open //and (close[1] > open[1] ? close[1] : open[1]) < close\n\nstrategy.entry("long", strategy.long, when=s)\nstrategy.entry("short", strategy.short, when=l)\n\nbgcolor(l ? green : na)\nbgcolor(s ? red : na)\n\nperiodCenter = (periodHigh+periodLow)/2\nperiod0618 = (periodLow)+(periodHigh-periodLow)*0.618\nperiod0382 = (periodLow)+(periodHigh-periodLow)*0.382\n\ncloud1 = plot(period0382, color=#494949)\ncloud2 = plot(period0618, color=#494949)\n\nfill(cloud1, cloud2, color=#d8d8d8)\n\nplot(periodHigh, color=#d81751)\nplot(periodLow, color=#0daa20)\n//plot(periodCenter, color=#494949)\n\nbc = close > period0618 ? white : (close < period0382 ? black : na)\n\nbarcolor(bc)\n'

class SMQuantTradingSupportandResistanceCloudIndicator0852f2(PinePortBase, IStrategy):
    source_id = "SM_0852f2d71871e9d7"
    source_file = '量化交易中的支撑阻力云形态指标Quant-Trading-Support-and-Resistance-Cloud-Indicator.md'
    timeframe = '15m'
    can_short = True
    source_defaults = {'entP': 50, 'exP': 25, 'sensitivity': 0.9999}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Loop/switch logic is present and requires per-strategy semantic verification against TradingView/FMZ before treating results as parity-certified.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
