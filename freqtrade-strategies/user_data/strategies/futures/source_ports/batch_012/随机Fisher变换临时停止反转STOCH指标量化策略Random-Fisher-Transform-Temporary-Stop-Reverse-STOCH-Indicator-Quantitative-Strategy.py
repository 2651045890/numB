"""batch_012 port of 随机Fisher变换临时停止反转STOCH指标量化策略Random-Fisher-Transform-Temporary-Stop-Reverse-STOCH-Indicator-Quantitative-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-26 00:00:00\nend: 2024-01-01 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("IFT Stochastic + Trailing Stop", overlay=false, pyramiding = 0, calc_on_order_fills = false, commission_type =  strategy.commission.percent, commission_value = 0.0454, default_qty_type = strategy.percent_of_equity, default_qty_value = 100)\n\n//INPUTS\nstochlength=input(19, "STOCH Length")\nwmalength=input(4, title="Smooth")\nul = input(0.64,step=0.01, title="UP line")\ndl = input(-0.62,step=0.01, title="DOWN line")\nuts = input(true, title="Use trailing stop")\ntsi = input(title="trailing stop actiation pips",defval=245)                                                                       \ntso = input(title="trailing stop offset pips",defval=20)\n\n//CALCULATIONS\nv1=0.1*(stoch(close, high, low, stochlength)-50)\nv2=wma(v1, wmalength)\nINVLine=(exp(2*v2)-1)/(exp(2*v2)+1)\n\n//CONDITIONS\nsell = crossunder(INVLine,ul)? 1 : 0\nbuy = crossover(INVLine,dl)? 1 : 0\n\n//PLOTS\nplot(INVLine, color=aqua, linewidth=1, title="STOCH")\nhline(ul, color=red)\nhline(dl, color=green)\nbgcolor(sell==1? red : na, transp=30, title = "sell signal")\nbgcolor(buy==1? lime : na, transp=30, title = "buy signal")\nplotchar(buy==1, title="Buy Signal", char=\'B\', location=location.bottom, color=white, transp=0, offset=0)\nplotchar(sell==1, title="Sell Signal", char=\'S\', location=location.top, color=white, transp=0, offset=0)\n\n//STRATEGY\nstrategy.entry("BUY", strategy.long, when = buy==1)\nstrategy.entry("SELL", strategy.short, when = sell==1)\n\nif  (uts)\n    strategy.entry("BUY", strategy.long, when = buy)\n    strategy.entry("SELL", strategy.short, when = sell)\n    strategy.exit("Close BUY with TS","BUY", trail_points = tsi, trail_offset = tso)\n    strategy.exit("Close SELL with TS","SELL", trail_points = tsi, trail_offset = tso)\n\n'

class SMFisherSTOCHRandomFisherTransformTemporaryStopReverseSTOc3c2e8(PinePortBase, IStrategy):
    source_id = "SM_c3c2e876006e8059"
    source_file = '随机Fisher变换临时停止反转STOCH指标量化策略Random-Fisher-Transform-Temporary-Stop-Reverse-STOCH-Indicator-Quantitative-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'stochlength': 19, 'wmalength': 4, 'ul': 0.64, 'dl': -0.62, 'uts': True, 'tsi': 245, 'tso': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0454
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
