"""batch_012 port of 高级动态追踪止损与目标盈利策略-Advanced-Dynamic-Trailing-Stop-with-Risk-Reward-Targeting-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-11-10 00:00:00\nend: 2024-12-09 08:00:00\nperiod: 2h\nbasePeriod: 2h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © ZenAndTheArtOfTrading | www.TheArtOfTrading.com\n// @version=5\nstrategy("Trailing stop 1", overlay=true)\n\n// Get user input \nint     BAR_LOOKBACK    = input.int(10, "Bar Lookback")\nint     ATR_LENGTH      = input.int(14, "ATR Length")\nfloat   ATR_MULTIPLIER  = input.float(1.0, "ATR Multiplier")\nrr                      = input.float(title="Risk:Reward", defval=3)\n\n// Basic definition\nvar float shares=na\nrisk = 1000\nvar float R=na\nE = strategy.position_avg_price\n\n// Input option to choose long, short, or both\nside = input.string("Long", title="Side", options=["Long", "Short", "Both"])\n\n// RSI exit option\nRSIexit = input.string("Yes", title="Exit at RSI extreme?", options=["Yes", "No"])\nRSIup = input(75)\nRSIdown = input(25)\n\n// Get indicator values \nfloat atrValue = ta.atr(ATR_LENGTH)\n\n// Calculate stop loss values\nvar float trailingStopLoss = na \nfloat longStop  = ta.lowest(low, BAR_LOOKBACK) - (atrValue * ATR_MULTIPLIER)\nfloat shortStop = ta.highest(high, BAR_LOOKBACK) + (atrValue * ATR_MULTIPLIER)\n\n// Check if we can take trades \nbool canTakeTrades = not na(atrValue)\nbgcolor(canTakeTrades ? na : color.red)\n\n//Long pattern\n    //Two pin bar\nonepinbar = (math.min(close,open)-low)/(high-low)>0.6 and math.min(close,open)-low>ta.sma(high-low,14)\ntwopinbar = onepinbar and onepinbar[1]\nnotatbottom = low>ta.lowest(low[1],10)\n    // Parallel\nbigred = (open-close)/(high-low)>0.8 and high-low>ta.sma(high-low,14)\nbiggreen = (close-open)/(high-low)>0.8 and high-low>ta.sma(high-low,14)\nparallel = bigred[1] and biggreen  \natbottom = low==ta.lowest(low,10)\n\n// Enter long trades (replace this entry condition)\nlongCondition = parallel \nif (longCondition and canTakeTrades and  strategy.position_size == 0 and (side == "Long" or side == "Both"))\n    R:= close-longStop\n    shares:= risk/R\n    strategy.entry("Long", strategy.long,qty=shares)\n\n// Enter short trades\xa0(replace this entry condition)\nshortCondition = parallel\nif (shortCondition and canTakeTrades and strategy.position_size == 0 and (side == "Short" or side == "Both"))\n    R:= shortStop - close\n    shares:= risk/R\n    strategy.entry("Short", strategy.short,qty=shares)\n\n// Update trailing stop\nif (strategy.position_size > 0)\n    if (na(trailingStopLoss) or longStop > trailingStopLoss)\n        trailingStopLoss := longStop\nelse if (strategy.position_size < 0)\n    if (na(trailingStopLoss) or shortStop < trailingStopLoss)\n        trailingStopLoss := shortStop\nelse\n    trailingStopLoss := na\n\n// Exit trades with trailing stop\nstrategy.exit("Long Exit",  "Long",  stop=trailingStopLoss, limit = E + rr*R )\nstrategy.exit("Short Exit", "Short", stop=trailingStopLoss, limit = E - rr*R)\n\n//Close trades at RSI extreme\nif ta.rsi(high,14)>RSIup and RSIexit == "Yes"\n    strategy.close("Long")\nif ta.rsi(low,14)<RSIdown and RSIexit == "Yes"\n    strategy.close("Short")\n\n// Draw stop loss \nplot(trailingStopLoss, "Stop Loss", color.red, 1, plot.style_linebr)\n'

class SMAdvancedDynamicTrailingStopwithRiskRewardTargetingStrat53fb5f(PinePortBase, IStrategy):
    source_id = "SM_53fb5f648a3ea990"
    source_file = '高级动态追踪止损与目标盈利策略-Advanced-Dynamic-Trailing-Stop-with-Risk-Reward-Targeting-Strategy.md'
    timeframe = '2h'
    can_short = True
    source_defaults = {'BAR_LOOKBACK': 10, 'ATR_LENGTH': 14, 'ATR_MULTIPLIER': 1.0, 'rr': 3, 'side': 'Long', 'RSIexit': 'Yes', 'RSIup': 75, 'RSIdown': 25}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
