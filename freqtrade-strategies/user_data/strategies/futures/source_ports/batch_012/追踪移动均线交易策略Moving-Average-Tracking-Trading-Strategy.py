"""batch_012 port of 追踪移动均线交易策略Moving-Average-Tracking-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-09-23 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 3h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n//Heikin Ashi Strategy  V3 by breizh29\n\n// strategy("Heikin Ashi Strategy  V3",shorttitle="HAS V3",overlay=true,default_qty_value=100,initial_capital=100,currency=currency.EUR) \nres = input(title="Heikin Ashi Candle Time Frame",  defval="30")\nhshift = input(1,title="Heikin Ashi Candle Time Frame Shift")\nres1 = input(title="Heikin Ashi EMA Time Frame",  defval="180")\nmhshift = input(0,title="Heikin Ashi EMA Time Frame Shift")\nfama = input(1,"Heikin Ashi EMA Period")\ntest = input(1,"Heikin Ashi EMA Shift")\nsloma = input(10,"Slow EMA Period")\nslomas = input(1,"Slow EMA Shift")\nmacdf = input(false,title="With MACD filter")\nres2 = input(title="MACD Time Frame",  defval="12")\nmacds = input(1,title="MACD Shift")\n\n\n\n\n//Heikin Ashi Open/Close Price\nha_t = heikinashi(syminfo.tickerid)\nha_open = security(ha_t, res, open[hshift])\nha_close = security(ha_t, res, close[hshift])\nmha_close = security(ha_t, res1, close[mhshift])\n\n//macd\n[macdLine, signalLine, histLine] = macd(close, 12, 26, 9)\nmacdl = security(ha_t,res2,macdLine[macds])\nmacdsl= security(ha_t,res2,signalLine[macds])\n\n//Moving Average\nfma = ema(mha_close[test],fama)\nsma = ema(ha_close[slomas],sloma)\nplot(fma,title="MA",color=lime,linewidth=2,style=line)\nplot(sma,title="SMA",color=red,linewidth=2,style=line)\n\n\n//Strategy\ngolong =  crossover(fma,sma) and (macdl > macdsl or macdf == false )\ngoshort =   crossunder(fma,sma) and (macdl < macdsl or macdf == false )\n\n\nstrategy.entry("Buy",strategy.long,when = golong)\nstrategy.entry("Sell",strategy.short,when = goshort)\n'

class SMMovingAverageTrackingTradingStrategy6fe528(PinePortBase, IStrategy):
    source_id = "SM_6fe52835cd7602ef"
    source_file = '追踪移动均线交易策略Moving-Average-Tracking-Trading-Strategy.md'
    timeframe = '3h'
    can_short = True
    source_defaults = {'res': '30', 'hshift': 1, 'res1': '180', 'mhshift': 0, 'fama': 1, 'test': 1, 'sloma': 10, 'slomas': 1, 'macdf': False, 'res2': '12', 'macds': 1}
    source_qty_type = 'fixed'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 100
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
