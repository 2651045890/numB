"""batch_011 port of 移动平均趋势跟踪金叉做多策略Moving-Average-Trend-Following-Golden-Cross-Long-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-15 00:00:00\nend: 2023-10-22 00:00:00\nperiod: 5m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=2\nstrategy(title="MACD/EMA Long Strategy",overlay=true,scale=scale.left)\n\n\n\n// SMA Indicator - Are we in a Bull or Bear market according to 200 SMA?\nSMA = sma(close, input(200))\n\n\n\n// EMA Indicator - Are we in a rally or not?\nEMA = ema(close, input(20))\n\n\n\n//MACD Indicator - Is the MACD bullish or bearish?\n\nfastLength = input(12)\nslowlength = input(26)\nMACDLength = input(9)\n\nMACD = ema(close, fastLength) - ema(close, slowlength)\naMACD = ema(MACD, MACDLength)\ndelta = MACD - aMACD\n\n// Set Buy/Sell conditions\n\n[main,signal,histo]=macd(close,fastLength,slowlength,MACDLength)\n\nbuy_entry= if close>SMA\n    delta>0\nelse\n    delta>0 and close>EMA\n    \nstrategy.entry("Buy",true , when=buy_entry)\n\nalertcondition(delta, title=\'Long\', message=\'MACD Bullish\')\n\n\nsell_entry = if close<SMA\n    delta<0 \nelse\n    delta<0 and close<EMA\nstrategy.close("Buy",when= sell_entry)\n\n\nalertcondition(delta, title=\'Short\', message=\'MACD Bearish\')\n\n//plot(delta, title="Delta", style=cross, color=delta>=0 ? green : red )'

class SMA5BCD1C7B20406BC(PinePortBase, IStrategy):
    source_id = "SM_a5bcd1c7b20406bc"
    source_file = '移动平均趋势跟踪金叉做多策略Moving-Average-Trend-Following-Golden-Cross-Long-Strategy.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'fastLength': 12, 'slowlength': 26, 'MACDLength': 9}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['tuple']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
