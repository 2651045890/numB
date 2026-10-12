"""batch_012 port of 高级多重趋势确认的EMA供需区域动态套利策略-Advanced-Multi-Trend-Confirmation-EMA-Supply-Demand-Zone-Dynamic-Scalping-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-02-08 00:00:00\nend: 2025-02-06 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Optimized Scalping Strategy with EMA & Supply/Demand Zones", overlay=true)\n\n// Inputs\nema9_length = input(9, title="EMA 9 Length")\nema15_length = input(15, title="EMA 15 Length")\nhigher_tf = input.timeframe("15", title="Higher Timeframe for Zones")\natr_mult = input(1.5, title="ATR Multiplier for Stop Loss")\nrisk_reward = input.float(1.2, title="Risk-Reward Ratio", options=[1.2, 1.3, 1.4])\n\n// Calculating EMAs\nema9 = ta.ema(close, ema9_length)\nema15 = ta.ema(close, ema15_length)\n\n// Function to detect supply & demand zones\nget_zone(tf) =>\n    high_tf_high = request.security(syminfo.tickerid, tf, ta.highest(high, 50))\n    high_tf_low = request.security(syminfo.tickerid, tf, ta.lowest(low, 50))\n    [high_tf_high, high_tf_low]\n\n[supply_zone, demand_zone] = get_zone(higher_tf)\n\n// ATR-based Stop Loss and Take Profit\natr = ta.atr(14)\nlong_sl = close - (atr * atr_mult)\nlong_tp = close + (atr * atr_mult * risk_reward)\nshort_sl = close + (atr * atr_mult)\nshort_tp = close - (atr * atr_mult * risk_reward)\n\n// Entry conditions with volume and trend confirmation\nlongCondition = ta.rising(ema9, 3) and ta.rising(ema15, 3) and close > demand_zone and ta.sma(volume, 20) > ta.sma(volume, 50)\nshortCondition = ta.falling(ema9, 3) and ta.falling(ema15, 3) and close < supply_zone and ta.sma(volume, 20) > ta.sma(volume, 50)\n\n// Exit conditions using ATR-based SL/TP with additional trend confirmation\nexitLong = (close >= long_tp or close <= long_sl) and ta.falling(ema9, 2)\nexitShort = (close <= short_tp or close >= short_sl) and ta.rising(ema9, 2)\n\n// Executing trades with improved risk management\nif longCondition\n    strategy.entry("Long", strategy.long)\n    strategy.exit("Long Exit", from_entry="Long", stop=long_sl, limit=long_tp)\nif shortCondition\n    strategy.entry("Short", strategy.short)\n    strategy.exit("Short Exit", from_entry="Short", stop=short_sl, limit=short_tp)\n\n// Plotting\nplot(ema9, color=color.blue, title="EMA 9")\nplot(ema15, color=color.red, title="EMA 15")\nplot(supply_zone, color=color.orange, title="Supply Zone")\nplot(demand_zone, color=color.green, title="Demand Zone")\n\n'

class SMEMAAdvancedMultiTrendConfirmationEMASupplyDemandZoneDynaf6f36(PinePortBase, IStrategy):
    source_id = "SM_af6f36c1adb28c01"
    source_file = '高级多重趋势确认的EMA供需区域动态套利策略-Advanced-Multi-Trend-Confirmation-EMA-Supply-Demand-Zone-Dynamic-Scalping-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'ema9_length': 9, 'ema15_length': 15, 'higher_tf': '15', 'atr_mult': 1.5, 'risk_reward': 1.2}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'request.security/security is present: generic adapter keeps the expression but same-frame evaluation is only an approximation; manual multi-timeframe parity verification is required.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
