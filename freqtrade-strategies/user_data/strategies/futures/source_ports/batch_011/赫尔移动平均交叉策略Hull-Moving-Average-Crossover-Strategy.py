"""batch_011 port of 赫尔移动平均交叉策略Hull-Moving-Average-Crossover-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-16 00:00:00\nend: 2024-03-21 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//Basic Hull Ma Pack tinkered by InSilico \nstrategy("RKTD BETA - Hull Suite by InSilico", overlay=true)\n\n//INPUT\nsrc = input(close, title="Source")\nmodeSwitch = input("Ehma", title="Hull Variation", options=["Hma", "Thma", "Ehma"])\nlength = input(200, title="Length(180-200 for floating S/R , 55 for swing entry)")\nlengthMult = input(1.0, title="Length multiplier (Used to view higher timeframes with straight band)")\n\nuseHtf = input(false, title="Show Hull MA from X timeframe? (good for scalping)")\nhtf = input("240", title="Higher timeframe", type=input.resolution)\n\nswitchColor = input(true, "Color Hull according to trend?")\ncandleCol = input(false,title="Color candles based on Hull\'s Trend?")\nvisualSwitch  = input(true, title="Show as a Band?")\nthicknesSwitch = input(1, title="Line Thickness")\ntranspSwitch = input(40, title="Band Transparency",step=5)\n\n// Alert Messages\nlongAlertMessage = \'{"base": "BTC", "quote": "USDT", "price": \' + tostring(close) + \', "action": "long", "orderType": "market", "close":true}\'\nshortAlertMessage = \'{"base": "BTC", "quote": "USDT", "price": \' + tostring(close) + \', "action": "short", "orderType": "market", "close":true}\'\n\n//FUNCTIONS\n//HMA\nHMA(_src, _length) =>  wma(2 * wma(_src, _length / 2) - wma(_src, _length), round(sqrt(_length)))\n//EHMA    \nEHMA(_src, _length) =>  ema(2 * ema(_src, _length / 2) - ema(_src, _length), round(sqrt(_length)))\n//THMA    \nTHMA(_src, _length) =>  wma(wma(_src,_length / 3) * 3 - wma(_src, _length / 2) - wma(_src, _length), _length)\n    \n//SWITCH\nMode(modeSwitch, src, len) =>\n      modeSwitch == "Hma"  ? HMA(src, len) :\n      modeSwitch == "Ehma" ? EHMA(src, len) : \n      modeSwitch == "Thma" ? THMA(src, len/2) : na\n\n//OUT\n_hull = Mode(modeSwitch, src, int(length * lengthMult))\nHULL = useHtf ? security(syminfo.ticker, htf, _hull) : _hull\nMHULL = HULL[0]\nSHULL = HULL[2]\n\n//COLOR\nhullColor = switchColor ? (HULL > HULL[2] ? #00ff00 : #ff0000) : #ff9800\n\n//PLOT\n///< Frame\nFi1 = plot(MHULL, title="MHULL", color=hullColor, linewidth=thicknesSwitch, transp=50)\nFi2 = plot(visualSwitch ? SHULL : na, title="SHULL", color=hullColor, linewidth=thicknesSwitch, transp=50)\nalertcondition(crossover(MHULL, SHULL), title="Hull trending up.", message="Hull trending up.")\nalertcondition(crossover(SHULL, MHULL), title="Hull trending down.", message="Hull trending down.")\n///< Ending Filler\nfill(Fi1, Fi2, title="Band Filler", color=hullColor, transp=transpSwitch)\n///BARCOLOR\nbarcolor(color = candleCol ? (switchColor ? hullColor : na) : na)\n\n// Define Buy and Sell Conditions based on crossovers\nbuyCondition = crossover(MHULL, SHULL)\nsellCondition = crossunder(MHULL, SHULL)\n\n// Plotting the Hull Moving Average (HMA)\nplot(MHULL, title="MHULL", color=hullColor, linewidth=thicknesSwitch)\nplot(SHULL, title="SHULL", color=hullColor, linewidth=thicknesSwitch, transp=transpSwitch)\nfill(Fi1, Fi2, title="Band Filler", color=hullColor, transp=transpSwitch)\n\n// Execute Strategy based on Buy and Sell Conditions\nstrategy.entry("Buy", strategy.long, when=buyCondition, alert_message=longAlertMessage)\nstrategy.entry("Sell", strategy.short, when=sellCondition, alert_message=shortAlertMessage)\n\n// Additional elements like bar coloring remain unchanged\nbarcolor(color = candleCol ? (switchColor ? hullColor : na) : na)\n'

class SM9FC21BEF11C67DD4(PinePortBase, IStrategy):
    source_id = "SM_9fc21bef11c67dd4"
    source_file = '赫尔移动平均交叉策略Hull-Moving-Average-Crossover-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'modeSwitch': 'Ehma', 'length': 200, 'lengthMult': 1.0, 'useHtf': False, 'htf': '240', 'switchColor': True, 'candleCol': False, 'visualSwitch': True, 'thicknesSwitch': 1, 'transpSwitch': 40}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['mtf', 'func']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
