"""batch_012 port of 通道突破反转交易策略Volatility-Breakout-Reversal-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-02-12 00:00:00\nend: 2024-02-18 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\n//@author=LucF\n\n// Volatility System [LucF]\n// v1.0, 2019.04.14\n\n// The Volatility System was created by Welles Wilder.\n// It first appeared in his seminal masterpiece "New Concepts in Technical Trading Systems" (1978).\n// He describes it on pp.23-26, in the chapter discussing the first presentation ever of the "Volatility Index",\n// which later became known as ATR.\n// Performance of the strategy usually increases with the time frame.\n// Tuning of ATR length and, especially, the ARC factor, is key.\n\n// This code runs as a strategy, which cannot generate alerts.\n// If you want to use the alerts it must be converted to an indicator.\n// To do so:\n//      1. Swap the following 2 lines by commenting the first and uncommenting the second.\n//      2. Comment out the last 4 lines containing the strategy() calls.\n//      3. Save.\nstrategy(title="Volatility System by Wilder [LucF]", shorttitle="Volatility System [Strat]", overlay=true, precision=8, pyramiding=0, initial_capital=100000, default_qty_type=strategy.percent_of_equity, default_qty_value=100, commission_type=strategy.commission.percent, commission_value=0.1)\n// study("Volatility System by Wilder [LucF]", shorttitle="Volatility System", precision=8, overlay=true)\n\n// -------------- Colors\nMyGreenRaw = color(#00FF00,0),      MyGreenMedium = color(#00FF00,50),  MyGreenDark = color(#00FF00,75),    MyGreenDarkDark = color(#00FF00,92)\nMyRedRaw = color(#FF0000,0),        MyRedMedium = color(#FF0000,30),    MyRedDark = color(#FF0000,75),      MyRedDarkDark = color(#FF0000,90)\n\n// -------------- Inputs\nLongsOnly = input(false,"Longs only")\nShortsOnly = input(false,"Shorts only")\nAtrLength = input(9, "ATR length", minval=2)\nArcFactor = input(1.8, "ARC factor", minval=0, type=float,step=0.1)\nShowSAR = input(false, "Show all SARs (Stop & Reverse)")\nHideSAR = input(false, "Hide all SARs")\nShowTriggers = input(false, "Show Entry/Exit triggers")\nShowTradedBackground = input(false, "Show Traded Background")\n\nFromYear  = input(defval = 2000,    title = "From Year", minval = 1900)\nFromMonth = input(defval = 1,      title = "From Month", minval = 1, maxval = 12)\nFromDay   = input(defval = 1,       title = "From Day", minval = 1, maxval = 31)\nToYear    = input(defval = 9999,    title = "To Year", minval = 1900)\nToMonth   = input(defval = 1,       title = "To Month", minval = 1, maxval = 12)\nToDay     = input(defval = 1,       title = "To Day", minval = 1, maxval = 31)\n\n// -------------- Date range filtering\nFromDate = timestamp(FromYear, FromMonth, FromDay, 00, 00)\nToDate = timestamp(ToYear, ToMonth, ToDay, 23, 59)\nTradeDateIsAllowed() => true\n\n// -------------- Calculate Stop & Reverse (SAR) points using Average Range Constant (ARC)\nArc   = atr(AtrLength)*ArcFactor\nSarLo = highest(close, AtrLength)-Arc\nSarHi = lowest(close, AtrLength)+Arc\n\n// -------------- Entries/Exits\nInLong = false\nInShort = false\nEnterLong = TradeDateIsAllowed() and not InLong[1] and crossover(close, SarHi[1])\nEnterShort = TradeDateIsAllowed() and not InShort[1] and crossunder(close, SarLo[1])\nInLong := (InLong[1] and not EnterShort[1]) or (EnterLong[1] and not ShortsOnly)\nInShort := (InShort[1] and not EnterLong[1]) or (EnterShort[1] and not LongsOnly)\n\n// -------------- Plots\n// SAR points\nplot( not HideSAR and ((InShort or EnterLong) or ShowSAR)? SarHi:na, color=MyRedMedium, style=circles, linewidth=2, title="SAR High")\nplot( not HideSAR and ((InLong or EnterShort) or ShowSAR)? SarLo:na, color=MyGreenMedium, style=circles, linewidth=2, title="SAR Low")\n// Entry/Exit markers\nplotshape( ShowTriggers and not ShortsOnly and EnterLong, style=shape.triangleup, location=location.belowbar, color=MyGreenRaw, size=size.small, text="")\nplotshape( ShowTriggers and not LongsOnly and EnterShort, style=shape.triangledown, location=location.abovebar, color=MyRedRaw, size=size.small, text="")\n// Exits when printing only longs or shorts\nplotshape( ShowTriggers and ShortsOnly and InShort[1] and EnterLong, style=shape.triangleup, location=location.belowbar, color=MyRedMedium, transp=70, size=size.small, text="")\nplotshape( ShowTriggers and LongsOnly and InLong[1] and EnterShort, style=shape.triangledown, location=location.abovebar, color=MyGreenMedium, transp=70, size=size.small, text="")\n// Background\nbgcolor( color=ShowTradedBackground? InLong and not ShortsOnly?MyGreenDarkDark: InShort and not LongsOnly? MyRedDarkDark:na:na)\n\n// ---------- Alerts\nalertcondition( EnterLong or EnterShort, title="1. Reverse", message="Reverse")\nalertcondition( EnterLong, title="2. Long", message="Long")\nalertcondition( EnterShort, title="3. Short", message="Short")\n\n// ---------- Strategy reversals\nstrategy.entry("Long", strategy.long, when=EnterLong and not ShortsOnly)\nstrategy.entry("Short", strategy.short, when=EnterShort  and not LongsOnly)\nstrategy.close("Short", when=EnterLong and ShortsOnly)\nstrategy.close("Long", when=EnterShort and LongsOnly)\n\n'

class SMVolatilityBreakoutReversalTradingStrategyc7ed95(PinePortBase, IStrategy):
    source_id = "SM_c7ed952cadfca235"
    source_file = '通道突破反转交易策略Volatility-Breakout-Reversal-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'LongsOnly': False, 'ShortsOnly': False, 'AtrLength': 9, 'ArcFactor': 1.8, 'ShowSAR': False, 'HideSAR': False, 'ShowTriggers': False, 'ShowTradedBackground': False, 'FromYear': 2000, 'FromMonth': 1, 'FromDay': 1, 'ToYear': 9999, 'ToMonth': 1, 'ToDay': 1}
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
