"""batch_012 port of 逐级铺垫的均线兼顾策略Level-by-Level-Build-Up-Moving-Average-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-09-19 00:00:00\nend: 2023-09-25 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("Renko Level Strategy 2", shorttitle="RLS2", overlay=true, pyramiding=2, currency=currency.USD, default_qty_value=50, initial_capital=2000, default_qty_type=strategy.percent_of_equity) \n\nTF = input(title=\'TimeFrame\', type=input.resolution, defval="D")\nATRlength = input(title="ATR length", type=input.integer, defval=14, minval=2, maxval=100)\n\nHIGH = security(syminfo.tickerid, TF, high)\nLOW = security(syminfo.tickerid, TF, low)\nCLOSE = security(syminfo.tickerid, TF, close)\nATR = security(syminfo.tickerid, TF, atr(ATRlength))\n\nfloat RENKO = na\ncolor COLOR = na\nint BUY = na\nint SELL = na\nbool UP = na\nbool DN = na\n\nRENKO := na(RENKO[1]) ? close : RENKO[1]\nCOLOR := na(COLOR[1]) ? color.white : COLOR[1]\nBUY := na(BUY[1]) ? 0 : BUY[1]\nSELL := na(SELL[1]) ? 0 : SELL[1]\nUP := false\nDN := false\n\nif(close > RENKO[1]+ATR[1])\n    UP := true\n    RENKO := close\n    COLOR := color.lime\n    SELL := 0\n    BUY := BUY+1\n\nif(close < RENKO[1]-ATR[1])\n    DN := true\n    RENKO := close\n    COLOR := color.red\n    BUY := 0\n    SELL := SELL+1\n    \n\nif(BUY[1]==1 and BUY==2)\n    strategy.entry("long", strategy.long)//, limit = RENKODN)\n\nif(DN)\n    strategy.cancel_all()\n    strategy.close_all(comment = "close")\n\n\nplot(RENKO, style=plot.style_line, linewidth=2, color=COLOR)\n'

class SMLevelbyLevelBuildUpMovingAverageStrategye6ad82(PinePortBase, IStrategy):
    source_id = "SM_e6ad82a710a2b9ce"
    source_file = '逐级铺垫的均线兼顾策略Level-by-Level-Build-Up-Moving-Average-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'TF': 'D', 'ATRlength': 14}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 50
    source_commission_percent = 0.0
    source_pyramiding = 2
    source_initial_capital = 2000
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
