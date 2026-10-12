"""batch_011 port of 网格美元成本平均策略Grid-Dollar-Cost-Averaging-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-22 00:00:00\nend: 2023-08-22 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("DCA Trading Strategy", overlay=true)\n\n// Define input options\nnumGrids = input.int(5, title="Number of Grids")\ngridDistance = input.float(0.5, title="Grid Distance")\nstopLossPct = input.float(1, title="Stop Loss Percentage")\ntakeProfitPct = input.float(1, title="Take Profit Percentage")\nuseMarketOrder = input.bool(false, title="Use Market Order")\n\n// Define DCA function\ndca(quantity, price, stopLoss, takeProfit) =>\n    if useMarketOrder\n        strategy.entry("DCA Buy", strategy.short, qty=quantity)\n    else\n        strategy.entry("DCA Buy", strategy.short, qty=quantity, limit=price)\n    strategy.exit("Stop Loss/ Take Profit", "DCA Buy", stop=stopLoss, limit=takeProfit)\n\n// Calculate grid levels\ngridLevels = math.floor(strategy.position_size / (numGrids + 1) + 0.5)\n\n// Calculate buy quantity\nbuyQuantity = strategy.position_size / numGrids\n\n// Loop through each grid level\nfor i = 1 to numGrids\n    priceLevel = strategy.position_avg_price * (1 - gridDistance * i)\n    stopLossPrice = priceLevel * (1 - stopLossPct / 100)\n    takeProfitPrice = priceLevel * (1 + takeProfitPct / 100)\n    dca(buyQuantity, priceLevel, stopLossPrice, takeProfitPrice)\n\n// Plot grid levels\nplotshape(series=gridLevels, title="Grid Levels", location=location.abovebar, color=color.blue, style=shape.triangleup, size=size.small)\n'

class SM423D382C2E84270C(PinePortBase, IStrategy):
    source_id = "SM_423d382c2e84270c"
    source_file = '网格美元成本平均策略Grid-Dollar-Cost-Averaging-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'numGrids': 5, 'gridDistance': 0.5, 'stopLossPct': 1, 'takeProfitPct': 1, 'useMarketOrder': False}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = True
    source_risk_flags = ['func', 'loop', 'broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
