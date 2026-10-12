"""batch_011 port of 移动平均与相对强弱指标策略Moving-Average-Relative-Strength-Index-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-11-20 00:00:00\nend: 2023-11-24 06:00:00\nperiod: 10m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\n\nstrategy(title = "RSI versus SMA", shorttitle = "RSI vs SMA", overlay = false, pyramiding = 0, default_qty_type = strategy.percent_of_equity, default_qty_value = 10, currency = currency.GBP)\n\n// Revision:        1\n// Author:          @JayRogers\n//\n// *** USE AT YOUR OWN RISK ***\n// - Nothing is perfect, and all decisions by you are on your own head. And stuff.\n//\n// Description:\n//  - It\'s RSI versus a Simple Moving Average.. Not sure it really needs much more description.\n//  - Should not repaint - Automatically offsets by 1 bar if anything other than "open" selected as RSI source.\n\n// === INPUTS ===\n// rsi\nrsiSource   = input(defval = open, title = "RSI Source")\nrsiLength   = input(defval = 8, title = "RSI Length", minval = 1)\n// sma\nmaLength    = input(defval = 34, title = "MA Period", minval = 1)\n// invert trade direction\ntradeInvert = input(defval = false, title = "Invert Trade Direction?")\n// risk management\nuseStop     = input(defval = false, title = "Use Initial Stop Loss?")\nslPoints    = input(defval = 25, title = "Initial Stop Loss Points", minval = 1)\nuseTS       = input(defval = true, title = "Use Trailing Stop?")\ntslPoints   = input(defval = 120, title = "Trail Points", minval = 1)\nuseTSO      = input(defval = false, title = "Use Offset For Trailing Stop?")\ntslOffset   = input(defval = 20, title = "Trail Offset Points", minval = 1)\n// === /INPUTS ===\n\n// === BASE FUNCTIONS ===\n// delay for direction change actions\nswitchDelay(exp, len) =>\n    average = len >= 2 ? sum(exp, len) / len : exp[1]\n    up      = exp > average\n    down    = exp < average\n    state   = up ? true : down ? false : up[1]\n// === /BASE FUNCTIONS ===\n\n// === SERIES and VAR ===\n// rsi\nshunt = rsiSource == open ? 0 : 1\nrsiUp = rma(max(change(rsiSource[shunt]), 0), rsiLength)\nrsiDown = rma(-min(change(rsiSource[shunt]), 0), rsiLength)\nrsi = (rsiDown == 0 ? 100 : rsiUp == 0 ? 0 : 100 - (100 / (1 + rsiUp / rsiDown))) - 50 // shifted 50 points to make 0 median\n// sma of rsi\nrsiMa   = sma(rsi, maLength)\n// self explanatory..\ntradeDirection = tradeInvert ? 0 <= rsiMa ? true : false : 0 >= rsiMa ? true : false\n// === /SERIES ===\n\n// === PLOTTING ===\nbarcolor(color = tradeDirection ? green : red, title = "Bar Colours")\n// hlines\nmedianLine  = hline(0, title = \'Median\', color = #996600,  linewidth = 1)\nlimitUp     = hline(25, title = \'Limit Up\', color = silver,  linewidth = 1)\nlimitDown   = hline(-25, title = \'Limit Down\', color = silver,  linewidth = 1)\n// rsi and ma\nrsiLine     = plot(rsi, title = \'RSI\', color = purple, linewidth = 2, style = line, transp = 50)\nareaLine    = plot(rsiMa, title = \'Area MA\', color = silver, linewidth = 1, style = area, transp = 70)\n// === /PLOTTING ===\n\ngoLong() => not tradeDirection[1] and tradeDirection\nkillLong() => tradeDirection[1] and not tradeDirection\nstrategy.entry(id = "Buy", long = true, when = goLong())\nstrategy.close(id = "Buy", when = killLong())\n\ngoShort() => tradeDirection[1] and not tradeDirection\nkillShort() => not tradeDirection[1] and tradeDirection\nstrategy.entry(id = "Sell", long = false, when = goShort())\nstrategy.close(id = "Sell", when = killShort())\n\nif (useStop)\n    strategy.exit("XSL", from_entry = "Buy", loss = slPoints)\n    strategy.exit("XSS", from_entry = "Sell", loss = slPoints)\n// if we\'re using the trailing stop\nif (useTS and useTSO) // with offset\n    strategy.exit("XSL", from_entry = "Buy", trail_points = tslPoints, trail_offset = tslOffset)\n    strategy.exit("XSS", from_entry = "Sell", trail_points = tslPoints, trail_offset = tslOffset)\nif (useTS and not useTSO) // without offset\n    strategy.exit("XSL", from_entry = "Buy", trail_points = tslPoints)\n    strategy.exit("XSS", from_entry = "Sell", trail_points = tslPoints)'

class SMDBC6F6DB73D9243E(PinePortBase, IStrategy):
    source_id = "SM_dbc6f6db73d9243e"
    source_file = '移动平均与相对强弱指标策略Moving-Average-Relative-Strength-Index-Strategy.md'
    timeframe = '10m'
    can_short = False
    source_defaults = {'rsiLength': 8, 'maLength': 34, 'tradeInvert': False, 'useStop': False, 'slPoints': 25, 'useTS': True, 'tslPoints': 120, 'useTSO': False, 'tslOffset': 20}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
