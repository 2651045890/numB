"""batch_011 port of 趋势回调微调策略Mini-Pullback-Supertrend-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-06 00:00:00\nend: 2023-10-12 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(title="pullb", overlay = true, initial_capital = 10000, default_qty_value = 100, default_qty_type = strategy.percent_of_equity)\n\n//variables\n\n///emas var\nema_src = input.source(close, "EMA Source")\nema_1 = input.int(21, \'EMA 1 len\')\nema_2 = input(50, \'EMA 2 len\')\nema_3 = input(200, \'EMA 3 len\')\n\n///macd var\nmac_src = input.source(close, "MACD Source")\nmac_1 = input.int(12, \'MACD Fast\')\nmac_2 = input.int(26, \'MACD Signal\')\nmac_3 = input.int(9, \'MACD Histogram\')\n\n///rsi var\nrsi_src = input.source(close, "RSI Source")\nrsi_len = input.int(14, \'RSI Len\')\n\n///stoch var\nsmoothK = input.int(3, "K", minval=1)\nsmoothD = input.int(3, "D", minval=1)\nlengthRSI = input.int(14, "RSI Length", minval=1)\nlengthStoch = input.int(14, "Stochastic Length", minval=1)\nstoch_src = input(close, title="RSI Source Stoch")\n\n//usage variables\nema_b = input.bool(true, "Use EMA Filter")\nrsi_b = input.bool(true, "Use RSI Filter")\nmacd_b = input.bool(true, "Use MACD Filter")\n//stoch_b = input(title="Use STOCH Filter", type=bool, defval=true)\n\n//emaas\nema1 = ta.ema(ema_src, ema_1)\nema2 = ta.ema(ema_src, ema_2)\nema3 = ta.ema(ema_src, ema_3)\n\n//macd\n[macdLine, signalLine, histLine] = ta.macd(mac_src, mac_1, mac_2, mac_3)\n\n//rsi\nrsi = ta.rsi(rsi_src, rsi_len)\n\n//stoch\nrsi1 = ta.rsi(stoch_src, lengthRSI)\nk = ta.sma(ta.stoch(rsi1, rsi1, rsi1, lengthStoch), smoothK)\nd = ta.sma(k, smoothD)\n\n//supertrend\nPeriods = input.int(14, "ATR Period")\nsrc_st = input.source(close, "Supertrend Source")\nMultiplier = input.float(2.0 , "ATR Multiplier")\nchangeATR= input.bool(true, "Change ATR Calculation Method ?")\nshowsignals = input.bool(true, "Show Buy/Sell Signals ?")\nhighlighting = input.bool(true, "Highlighter On/Off ?")\natr2 = ta.sma(ta.tr, Periods)\natr3= changeATR ? ta.atr(Periods) : atr2\nup=src_st-(Multiplier*atr3)\nup1 = nz(up[1],up)\nup := close[1] > up1 ? math.max(up,up1) : up\ndn=src_st+(Multiplier*atr3)\ndn1 = nz(dn[1], dn)\ndn := close[1] < dn1 ? math.min(dn, dn1) : dn\ntrend = 1\ntrend := nz(trend[1], trend)\ntrend := trend == -1 and close > dn1 ? 1 : trend == 1 and close < up1 ? -1 : trend\nbuySignal = trend == 1 and trend[1] == -1\nsellSignal = trend == -1 and trend[1] == 1\n\n//conditions\n///buy\nrsi_cond_b = if rsi_b\n    rsi >= 50\nelse \n    true\n\nmacd_cond_b = if macd_b\n    (histLine >= 0 or histLine < histLine[1])\nelse\n    true\nema_cond_b = if ema_b\n    (ema1 > ema2 and ema2 > ema3)\nelse \n    true\n\nlook_for = input.int(5, "Bars from cross to signal")\n\nstoch_signal_sum = 0\nfor i = 0 to (look_for)\n    if k[i] > d[i] and k[i + 1] < d[i + 1] and (k[i + 1] < 20 and d[i + 1] < 20)\n        stoch_signal_sum := stoch_signal_sum + 1\n        \nstoch_cond_b = if stoch_signal_sum > 0\n    if k > 80 and d > 80\n        false\n    else\n        true\nelse\n    false\n\n\nsup_cond_b = buySignal\n\nbuy_sig = (rsi_cond_b and macd_cond_b and ema_cond_b and stoch_cond_b and sup_cond_b)\n\ntp_b = close + (ta.atr(14) * 3)\nsl_b = close - (ta.atr(14) * 1.5)\n\nif (buy_sig)\n    strategy.entry("long", strategy.long)\n    strategy.exit("exit", "long", stop = sl_b, limit = tp_b)\nplot(tp_b)\nplot(sl_b)\n\n'

class SM82F7355AFEB62D17(PinePortBase, IStrategy):
    source_id = "SM_82f7355afeb62d17"
    source_file = '趋势回调微调策略Mini-Pullback-Supertrend-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'ema_1': 21, 'ema_2': 50, 'ema_3': 200, 'mac_1': 12, 'mac_2': 26, 'mac_3': 9, 'rsi_len': 14, 'smoothK': 3, 'smoothD': 3, 'lengthRSI': 14, 'lengthStoch': 14, 'ema_b': True, 'rsi_b': True, 'macd_b': True, 'Periods': 14, 'Multiplier': 2.0, 'changeATR': True, 'showsignals': True, 'highlighting': True, 'look_for': 5}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['loop', 'tuple', 'exit_order', 'var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
