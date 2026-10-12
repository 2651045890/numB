"""batch_011 port of 自适应智能网格交易策略Adaptive-Intelligent-Grid-Trading-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-01-08 00:00:00\nend: 2024-01-15 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("(IK) Grid Script", overlay=true, pyramiding=14, close_entries_rule="ANY", default_qty_type=strategy.cash, initial_capital=100.0, currency="USD", commission_type=strategy.commission.percent, commission_value=0.1)\ni_autoBounds    = input(group="Grid Bounds", title="Use Auto Bounds?", defval=true, type=input.bool)                             // calculate upper and lower bound of the grid automatically? This will theorhetically be less profitable, but will certainly require less attention\ni_boundSrc      = input(group="Grid Bounds", title="(Auto) Bound Source", defval="Hi & Low", options=["Hi & Low", "Average"])     // should bounds of the auto grid be calculated from recent High & Low, or from a Simple Moving Average\ni_boundLookback = input(group="Grid Bounds", title="(Auto) Bound Lookback", defval=250, type=input.integer, maxval=500, minval=0) // when calculating auto grid bounds, how far back should we look for a High & Low, or what should the length be of our sma\ni_boundDev      = input(group="Grid Bounds", title="(Auto) Bound Deviation", defval=0.10, type=input.float, maxval=1, minval=-1)  // if sourcing auto bounds from High & Low, this percentage will (positive) widen or (negative) narrow the bound limits. If sourcing from Average, this is the deviation (up and down) from the sma, and CANNOT be negative.\ni_upperBound    = input(group="Grid Bounds", title="(Manual) Upper Boundry", defval=0.285, type=input.float)                      // for manual grid bounds only. The upperbound price of your grid\ni_lowerBound    = input(group="Grid Bounds", title="(Manual) Lower Boundry", defval=0.225, type=input.float)                      // for manual grid bounds only. The lowerbound price of your grid.\ni_gridQty       = input(group="Grid Lines",  title="Grid Line Quantity", defval=8, maxval=15, minval=3, type=input.integer)       // how many grid lines are in your grid\n\nf_getGridBounds(_bs, _bl, _bd, _up) =>\n    if _bs == "Hi & Low"\n        _up ? highest(close, _bl) * (1 + _bd) : lowest(close, _bl)  * (1 - _bd)\n    else\n        avg = sma(close, _bl)\n        _up ? avg * (1 + _bd) : avg * (1 - _bd)\n\nf_buildGrid(_lb, _gw, _gq) =>\n    gridArr = array.new_float(0)\n    for i=0 to _gq-1\n        array.push(gridArr, _lb+(_gw*i))\n    gridArr\n\nf_getNearGridLines(_gridArr, _price) =>\n    arr = array.new_int(3)\n    for i = 0 to array.size(_gridArr)-1\n        if array.get(_gridArr, i) > _price\n            array.set(arr, 0, i == array.size(_gridArr)-1 ? i : i+1)\n            array.set(arr, 1, i == 0 ? i : i-1)\n            break\n    arr\n\nvar upperBound      = i_autoBounds ? f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, true) : i_upperBound  // upperbound of our grid\nvar lowerBound      = i_autoBounds ? f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, false) : i_lowerBound // lowerbound of our grid\nvar gridWidth       = (upperBound - lowerBound)/(i_gridQty-1)                                                       // space between lines in our grid\nvar gridLineArr     = f_buildGrid(lowerBound, gridWidth, i_gridQty)                                                 // an array of prices that correspond to our grid lines\nvar orderArr        = array.new_bool(i_gridQty, false)                                                              // a boolean array that indicates if there is an open order corresponding to each grid line\n\nvar closeLineArr    = f_getNearGridLines(gridLineArr, close)                                                        // for plotting purposes - an array of 2 indices that correspond to grid lines near price\nvar nearTopGridLine = array.get(closeLineArr, 0)                                                                    // for plotting purposes - the index (in our grid line array) of the closest grid line above current price\nvar nearBotGridLine = array.get(closeLineArr, 1)                                                                    // for plotting purposes - the index (in our grid line array) of the closest grid line below current price\nstrategy.initial_capital = 50000\nfor i = 0 to (array.size(gridLineArr) - 1)\n    if close < array.get(gridLineArr, i) and not array.get(orderArr, i) and i < (array.size(gridLineArr) - 1)\n        buyId = i\n        array.set(orderArr, buyId, true)\n        strategy.entry(id=tostring(buyId), long=true, qty=(strategy.initial_capital/(i_gridQty-1))/close, comment="#"+tostring(buyId))\n    if close > array.get(gridLineArr, i) and i != 0\n        if array.get(orderArr, i-1)\n            sellId = i-1\n            array.set(orderArr, sellId, false)\n            strategy.close(id=tostring(sellId), comment="#"+tostring(sellId))\n\nif i_autoBounds\n    upperBound  := f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, true)\n    lowerBound  := f_getGridBounds(i_boundSrc, i_boundLookback, i_boundDev, false)\n    gridWidth   := (upperBound - lowerBound)/(i_gridQty-1)\n    gridLineArr := f_buildGrid(lowerBound, gridWidth, i_gridQty)\n\ncloseLineArr    := f_getNearGridLines(gridLineArr, close)\nnearTopGridLine := array.get(closeLineArr, 0)\nnearBotGridLine := array.get(closeLineArr, 1)'

class SM1E1830F94BB3399A(PinePortBase, IStrategy):
    source_id = "SM_1e1830f94bb3399a"
    source_file = '自适应智能网格交易策略Adaptive-Intelligent-Grid-Trading-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'i_autoBounds': True, 'i_boundSrc': 'Hi & Low', 'i_boundLookback': 250, 'i_boundDev': 0.1, 'i_upperBound': 0.285, 'i_lowerBound': 0.225, 'i_gridQty': 8}
    source_qty_type = 'cash'
    source_qty_value = 1
    source_commission_percent = 0.1
    source_pyramiding = 14
    source_initial_capital = 100.0
    source_reproduce_stops = False
    source_risk_flags = ['func', 'array', 'loop', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
