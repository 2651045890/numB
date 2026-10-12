"""batch_011 port of 趋势追踪移动止损策略Trend-Tracking-Trailing-Stop-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-01-16 00:00:00\nend: 2024-01-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bendre ADX Sup Trend", overlay = true)\n\n///////////////////////////\n// SuperTrend + Pivot Point\n//////////////////////////\n\nsrc =  input(close, title="EMA Source")\nPPprd = input(defval = 2, title="Pivot Point Period")\nAtrFactor=input(defval = 2, title = "ATR Factor")\nAtrPd=input(defval = 18, title = "ATR Period")\n\nStartDate = input(timestamp("1 Dec 2022"), title="Start Date")\nEndDate = input(timestamp("12 Jan 2023"), title="End Date")\n\nvar float ph = na\nvar float pl = na\nph := ta.pivothigh(PPprd, PPprd)\npl :=ta.pivotlow(PPprd, PPprd)\n\nfloat center = na\ncenter := center[1]\n// float lastpp = ph ? ph : pl ? pl : 0.0\nfloat lastpp = na(ph) ? na(pl) ? na : pl : ph\n\nif lastpp > 0\n    if na(center)\n        center := lastpp\n    else\n        center := (center * 2 + lastpp) / 3\n\nUp = center - (AtrFactor * ta.atr(AtrPd))\nDn = center + (AtrFactor * ta.atr(AtrPd))\n\nvar float TUp = na\nvar float TDown = na\nTrend = 0\nTUp := close[1] > TUp[1] ? math.max(Up, TUp[1]) : Up\nTDown := close[1] < TDown[1] ? math.min(Dn, TDown[1]) : Dn\nTrend := close > TDown[1] ? 1: close < TUp[1]? -1: nz(Trend[1], 1)\nTrailingsl = Trend == 1 ? TUp : TDown\n\n// Lines\nlinecolor = Trend == 1 and nz(Trend[1]) == 1 ? color.lime : Trend == -1 and nz(Trend[1]) == -1 ? color.red : na\nplot(Trailingsl, color = linecolor ,  linewidth = 2, title = "PP SuperTrend")\n\nbsignalSSPP = close > Trailingsl\nssignalSSPP = close < Trailingsl\n\n\n///////\n// ADX\n//////\n\nlenADX = 14\nth = 14\nTrueRange = math.max(math.max(high-low, math.abs(high-nz(close[1]))), math.abs(low-nz(close[1])))\nDirectionalMovementPlus = high-nz(high[1]) > nz(low[1])-low ? math.max(high-nz(high[1]), 0): 0\nDirectionalMovementMinus = nz(low[1])-low > high-nz(high[1]) ? math.max(nz(low[1])-low, 0): 0\nSmoothedTrueRange = 0.0\nSmoothedTrueRange := nz(SmoothedTrueRange[1]) - (nz(SmoothedTrueRange[1])/lenADX) + TrueRange\nSmoothedDirectionalMovementPlus = 0.0\nSmoothedDirectionalMovementPlus := nz(SmoothedDirectionalMovementPlus[1]) - (nz(SmoothedDirectionalMovementPlus[1])/lenADX) + DirectionalMovementPlus\nSmoothedDirectionalMovementMinus = 0.0\nSmoothedDirectionalMovementMinus := nz(SmoothedDirectionalMovementMinus[1]) - (nz(SmoothedDirectionalMovementMinus[1])/lenADX) + DirectionalMovementMinus\nDIPlus = SmoothedDirectionalMovementPlus / SmoothedTrueRange * 100\nDIMinus = SmoothedDirectionalMovementMinus / SmoothedTrueRange * 100\nDX = math.abs(DIPlus-DIMinus) / (DIPlus+DIMinus)*100\nADX = ta.sma(DX, lenADX)\n\n\n//////\n// MA\n/////\n\nlenMA = 21\nsrcMA = input(close, title="Source")\n// offsetMA = input(title="Offset", type=input.integer, defval=0, minval=-500, maxval=500)\noffsetMA = input(0, title="Offset")\noutMA = ta.sma(srcMA, lenMA)\n\n//\n// RSI\n//\nlength = input( 14 )\noverSold = input( 30 )\noverBought = input( 65 )\nprice = close\nvrsi = ta.rsi(price, length)\n\n\n// Buy - Sell Entries\nbuy = bsignalSSPP and outMA < close and ADX > th\nsell = ssignalSSPP \n\n\nif (buy and vrsi > overBought)\n    // .order // Tuned version\n    strategy.entry("Buy", strategy.long)\n    // strategy.close("Sell", "close Sell")\n\nif (sell) and (strategy.position_size > 0)\n    // strategy.entry("Sell", strategy.short)\n    strategy.close("Buy", "Close Buy")\n\n// if(sell and vrsi < overSold )\n//     strategy.entry("Sell", strategy.short)\n\n// if(buy) and (strategy.position_size > 0)\n//     strategy.close("Sell", "close Sell")\n\n\n\n'

class SM3B3E5CA9DD448E64(PinePortBase, IStrategy):
    source_id = "SM_3b3e5ca9dd448e64"
    source_file = '趋势追踪移动止损策略Trend-Tracking-Trailing-Stop-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'PPprd': 2, 'AtrFactor': 2, 'AtrPd': 18, 'offsetMA': 0, 'length': 14, 'overSold': 30, 'overBought': 65}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
