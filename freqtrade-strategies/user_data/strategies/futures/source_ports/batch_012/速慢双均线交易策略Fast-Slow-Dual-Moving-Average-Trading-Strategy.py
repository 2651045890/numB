"""batch_012 port of 速慢双均线交易策略Fast-Slow-Dual-Moving-Average-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-20 00:00:00\nend: 2023-10-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\n\nstrategy("SMA Strategy", shorttitle="SMA Strategy", overlay=true, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\n// === Inputs ===\n// short ma\nmaFastSource = input(defval=close, title="Fast MA Source")\nmaFastLength = input(defval=3, title="Fast MA Period", minval=1)\n\n// long ma\nmaSlowSource = input(defval=close, title="Slow MA Source")\nmaSlowLength = input(defval=9, title="Slow MA Period", minval=1)\n\n// Trade direction\nshorting = input(defval=false, title="Short only?")\nlongonly = input(defval=true, title="Long only?")\nswapping = input(defval=false, title="Swap orders?")\n// risk management\nuseStop = input(defval=false, title="Use Initial Stop Loss?")\nslPoints = input(defval=25, title="Initial Stop Loss Points", minval=1)\nuseTS = input(defval=false, title="Use Trailing Stop?")\ntslPoints = input(defval=120, title="Trail Points", minval=1)\nuseTSO = input(defval=false, title="Use Offset For Trailing Stop?")\ntslOffset = input(defval=20, title="Trail Offset Points", minval=1)\n\n// Messages for buy and sell\nmessage_long_entry  = input("Long entry message", title="Long entry message")\nmessage_long_exit   = input("Long exit message", title="Long exit message")\nmessage_short_entry = input("Short entry message", title="Short entry message")\nmessage_short_exit  = input("Short exit message", title="Short exit message")\n\n// Calculate start/end date and time condition\nstartDate  = input(timestamp("2021-01-01T00:00:00"), type = input.time)\nfinishDate = input(timestamp("2021-12-31T00:00:00"), type = input.time)\n \ntime_cond  = true\n// === Vars and Series ===\nfastMA = sma(maFastSource, maFastLength)\nslowMA = sma(maSlowSource, maSlowLength)\n\nplot(fastMA, color=color.blue)\nplot(slowMA, color=color.purple)\n\ngoLong() =>\n    crossover(fastMA, slowMA)\nkillLong() =>\n    crossunder(fastMA, slowMA)\n    \n// Long only\nif longonly\n    strategy.entry("Buy", strategy.long, when=goLong() and time_cond, alert_message = message_long_entry)\n    strategy.close("Buy", when=killLong() and time_cond, alert_message = message_long_exit)\n\n// Short only\nif shorting\n    strategy.entry("Sell", strategy.short, when=killLong() and time_cond, alert_message = message_short_entry)\n    strategy.close("Sell", when=goLong() and time_cond, alert_message = message_short_exit)\n    \n// Order Swapping\nif swapping\n    strategy.entry("Buy", strategy.long, when=goLong() and time_cond, alert_message = message_long_entry)\n    strategy.entry("Sell", strategy.short, when=killLong() and time_cond, alert_message = message_short_entry)\n\nif useStop\n    strategy.exit("XLS", from_entry="Buy", stop=strategy.position_avg_price / 1.08, alert_message = message_long_exit)\n    strategy.exit("XSS", from_entry="Sell", stop=strategy.position_avg_price * 1.08, alert_message = message_short_exit)\n\n\n'

class SMFastSlowDualMovingAverageTradingStrategyf08858(PinePortBase, IStrategy):
    source_id = "SM_f08858fe3ca40ecd"
    source_file = '速慢双均线交易策略Fast-Slow-Dual-Moving-Average-Trading-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'maFastSource': 'close', 'maFastLength': 3, 'maSlowSource': 'close', 'maSlowLength': 9, 'shorting': False, 'longonly': True, 'swapping': False, 'useStop': False, 'slPoints': 25, 'useTS': False, 'tslPoints': 120, 'useTSO': False, 'tslOffset': 20, 'message_long_entry': 'Long entry message', 'message_long_exit': 'Long exit message', 'message_short_entry': 'Short entry message', 'message_short_exit': 'Short exit message', 'startDate': 'timestamp("2021-01-01T00:00:00")', 'finishDate': 'timestamp("2021-12-31T00:00:00")'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
