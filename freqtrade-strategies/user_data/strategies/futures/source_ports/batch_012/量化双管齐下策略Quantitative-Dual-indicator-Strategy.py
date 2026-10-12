"""batch_012 port of 量化双管齐下策略Quantitative-Dual-indicator-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-22 00:00:00\nend: 2023-12-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\n////////////////////////////////////////////////////////////\n//  Copyright by HPotter v1.0 12/07/2022\n// This is combo strategies for get a cumulative signal.  \n//\n// First strategy\n// This indicator plots 2/20 exponential moving average. For the Mov \n// Avg X 2/20 Indicator, the EMA bar will be painted when the Alert criteria is met.\n//\n// Second strategy\n//  Bull Power Indicator\n//  To get more information please see "Bull And Bear Balance Indicator" \n//  by Vadim Gimelfarb. \n//\n// WARNING:\n// - For purpose educate only\n// - This script to change bars colors.\n////////////////////////////////////////////////////////////\nEMA20(Length) =>\n    pos = 0.0\n    xPrice = close\n    xXA = ta.ema(xPrice, Length)\n    nHH = math.max(high, high[1])\n    nLL = math.min(low, low[1])\n    nXS = nLL > xXA or nHH < xXA ? nLL : nHH\n    iff_1 = nXS < close[1] ? 1 : nz(pos[1], 0)\n    pos := nXS > close[1] ? -1 : iff_1\n    pos\n\n\nBP(SellLevel) =>\n    pos = 0.0\n    value = close < open ?  \n             close[1] < open ?  math.max(high - close[1], close - low): math.max(high - open, close - low):\n              close > open ? \n               close[1] > open ?  high - low : math.max(open - close[1], high - low) : \n                 high - close > close - low ? \n                  close[1] < open ? math.max(high - close[1], close - low) : high - open : \n                   high - close < close - low ? \n                     close[1] > open ?  high - low : math.max(open - close, high - low) : \n                      close[1] > open ? math.max(high - open, close - low) :\n                       close[1] < open? math.max(open - close, high - low): high - low\n    val2 = ta.sma(value, 15)                   \n    pos :=  val2 > SellLevel ? 1 : -1\n    pos\n\nstrategy(title=\'Combo 2/20 EMA & Bull Power\', shorttitle=\'Combo\', overlay=true)\nvar I1 = \'●═════ 2/20 EMA ═════●\'\nLength = input.int(14, minval=1, group=I1)\nvar I2 = \'●═════  Bull Power ═════●\'\nSellLevel = input.float(-15, step=0.01, group=I2)\nvar misc = \'●═════ MISC ═════●\'\nreverse = input.bool(false, title=\'Trade reverse\', group=misc)\nvar timePeriodHeader = \'●═════ Time Start ═════●\'\nd = input.int(1, title=\'From Day\', minval=1, maxval=31, group=timePeriodHeader)\nm = input.int(1, title=\'From Month\', minval=1, maxval=12, group=timePeriodHeader)\ny = input.int(2005, title=\'From Year\', minval=0, group=timePeriodHeader)\nStartTrade = time > timestamp(y, m, d, 00, 00) ? true : false\nposEMA20 = EMA20(Length)\nprePosBP = BP(SellLevel)\niff_1 = posEMA20 == -1 and prePosBP == -1 and StartTrade ? -1 : 0\npos = posEMA20 == 1 and prePosBP == 1 and StartTrade ? 1 : iff_1\niff_2 = reverse and pos == -1 ? 1 : pos\npossig = reverse and pos == 1 ? -1 : iff_2\nif possig == 1\n    strategy.entry(\'Long\', strategy.long)\nif possig == -1\n    strategy.entry(\'Short\', strategy.short)\nif possig == 0\n    strategy.close_all()\nbarcolor(possig == -1 ? #b50404 : possig == 1 ? #079605 : #0536b3)\n'

class SMQuantitativeDualindicatorStrategy663d5c(PinePortBase, IStrategy):
    source_id = "SM_663d5cd43f257bd2"
    source_file = '量化双管齐下策略Quantitative-Dual-indicator-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'Length': 14, 'SellLevel': -15, 'reverse': False, 'd': 1, 'm': 1, 'y': 2005}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
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
