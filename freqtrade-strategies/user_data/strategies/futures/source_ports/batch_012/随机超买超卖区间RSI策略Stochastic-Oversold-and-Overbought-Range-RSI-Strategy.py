"""batch_012 port of 随机超买超卖区间RSI策略Stochastic-Oversold-and-Overbought-Range-RSI-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-04 00:00:00\nend: 2023-12-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=3\nstrategy("imrich", shorttitle="imrich", overlay=true)\n\n\nRSIlength = input(6,title="RSI Period Length") \nRSIoverSold1 = 1\nRSIoverSold2 = 2\nRSIoverSold3 = 3\nRSIoverSold4 = 4\nRSIoverSold5 = 5\nRSIoverSold6 = 6\nRSIoverSold7 = 7\nRSIoverSold8 = 8\nRSIoverSold9 = 9\nRSIoverSold10 = 10\nRSIoverSold11 = 11\nRSIoverSold12 = 12\nRSIoverSold13 = 13\nRSIoverSold14 = 14\nRSIoverSold15 = 15\nRSIoverSold16 = 16\nRSIoverSold17 = 17\nRSIoverSold18 = 18\nRSIoverSold19 = 19\nRSIoverSold20 = 20\nRSIoverSold21 = 21\nRSIoverSold22 = 22\nRSIoverSold23 = 23\nRSIoverSold24 = 24\nRSIoverSold25 = 25\nRSIoverSold26 = 26\nRSIoverSold27 = 27\nRSIoverSold28 = 28\nRSIoverSold29 = 29\nRSIoverSold30 = 30\nRSIoverSold31 = 31\nRSIoverSold32 = 32\n\nRSIoverBought1 = 70\nRSIoverBought2 = 72\nRSIoverBought3 = 73\nRSIoverBought4 = 74\nRSIoverBought5 = 75\nRSIoverBought6 = 76\nRSIoverBought7 = 77\nRSIoverBought8 = 78\nRSIoverBought9 = 79\nRSIoverBought10 = 80\nRSIoverBought11 = 81\nRSIoverBought12 = 82\nRSIoverBought13 = 83\nRSIoverBought14 = 84\nRSIoverBought15 = 85\nRSIoverBought16 = 86\nRSIoverBought17 = 87\nRSIoverBought18 = 88\nRSIoverBought19 = 89\nRSIoverBought20 = 90\nRSIoverBought21 = 91\nRSIoverBought22 = 92\nRSIoverBought23 = 93\nRSIoverBought24 = 94\nRSIoverBought25 = 95\nRSIoverBought26 = 96\nRSIoverBought27 = 97\nRSIoverBought28 = 98\nRSIoverBought29 = 99\nRSIoverBought0 = 100\n\nprice = close\nvrsi = rsi(price, RSIlength)\n\n\n\n\n\nlong = (crossover(vrsi, RSIoverSold5)  or crossover(vrsi, RSIoverSold10) or crossover(vrsi, RSIoverSold15) or crossover(vrsi, RSIoverSold20) or crossover(vrsi, RSIoverSold25) or crossover(vrsi, RSIoverSold30) or crossover(vrsi, RSIoverSold7) or crossover(vrsi, RSIoverSold8) or crossover(vrsi, RSIoverSold9))\nclose_long = (crossunder(vrsi, RSIoverBought1) or crossunder(vrsi, RSIoverBought5) or crossunder(vrsi, RSIoverBought10) or crossunder(vrsi, RSIoverBought15) or crossunder(vrsi, RSIoverBought20) or crossunder(vrsi, RSIoverBought25) or crossunder(vrsi, RSIoverBought29))\n\nif (not na(vrsi))\n\n    if long\n        strategy.entry("RSI_BB", strategy.long, comment="RSI_BB")\n    else\n        strategy.cancel(id="RSI_BB")\n        \n    if close_long\n        strategy.close("RSI_BB")\n\n\n'

class SMRSIStochasticOversoldandOverboughtRangeRSIStrategyc42ae4(PinePortBase, IStrategy):
    source_id = "SM_c42ae45fce09ca25"
    source_file = '随机超买超卖区间RSI策略Stochastic-Oversold-and-Overbought-Range-RSI-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'RSIlength': 6}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
