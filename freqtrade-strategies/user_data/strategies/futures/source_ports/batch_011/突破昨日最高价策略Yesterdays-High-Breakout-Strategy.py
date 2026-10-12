"""batch_011 port of 突破昨日最高价策略Yesterdays-High-Breakout-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-10-06 00:00:00\nend: 2023-11-05 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// Author: © tumiza 999 \n// © TheSocialCryptoClub\n\n//@version=5\n\nstrategy("Yesterday\'s High v.17.07", overlay=true, pyramiding = 1,\n         initial_capital=10000, \n         default_qty_type=strategy.percent_of_equity, default_qty_value=10,\n         slippage=1, backtest_fill_limits_assumption=1, use_bar_magnifier=true,\n         commission_type=strategy.commission.percent, commission_value=0.075\n         )\n\n// -----------------------------------------------------------------------------\n// ROC Filter\n// -----------------------------------------------------------------------------\n\n// f_security function by LucF for PineCoders available here: https://www.tradingview.com/script/cyPWY96u-How-to-avoid-repainting-when-using-security-PineCoders-FAQ/\nf_security(_sym, _res, _src, _rep) => request.security(_sym, _res, _src[not _rep and barstate.isrealtime ? 1 : 0])[_rep or barstate.isrealtime ? 0 : 1]\nhigh_daily = f_security(syminfo.tickerid, "D", high, false)\n\nroc_enable = input.bool(false, "", group="ROC Filter from CloseD", inline="roc")\nroc_threshold = input.float(1, "Treshold", step=0.5, group="ROC Filter from CloseD", inline="roc")\n\nclosed = f_security(syminfo.tickerid,"1D",close, false)\nroc_filter= roc_enable ? (close-closed)/closed*100  > roc_threshold  : true\n\n\n// -----------------------------------------------------------------------------\n// Trigger Point \n// -----------------------------------------------------------------------------\n\nopen_session = ta.change(time(\'D\'))\nprice_session = ta.valuewhen(open_session, open, 0)\ntf_session = timeframe.multiplier <= 60\n\nbgcolor(open_session and tf_session ?color.new(color.blue,80):na, title = "Session")\n\nfirst_bar = 0\nif open_session\n    first_bar := bar_index\n\nvar max_today = 0.0\nvar min_today = 0.0\nvar high_daily1 = 0.0\nvar low_daily1 = 0.0\nvar today_open = 0.0\n\nif first_bar\n    high_daily1 := max_today\n    low_daily1 := min_today\n    today_open := open\n    max_today := high\n    min_today := low\n\n\nif high >= max_today\n    max_today := high\n\nif low < min_today\n    min_today := low\n\n\nsame_day  = today_open == today_open[1]\n\nplot( timeframe.multiplier <= 240 and same_day ? high_daily1 : na, color= color.yellow , style=plot.style_linebr, linewidth=1, title=\'High line\')\nplot( timeframe.multiplier <= 240 and same_day ? low_daily1 : na, color= #E8000D , style=plot.style_linebr, linewidth=1, title=\'Low line\')\n\n// -----------------------------------------------------------------------------\n// Strategy settings \n// -----------------------------------------------------------------------------\n\nGap = input.float(1,"Gap%", step=0.5, tooltip="Gap di entrata su entry_price -n anticipa entrata, con +n posticipa entrata", group = "Entry")\nGap2 = (high_daily1 * Gap)/100\n\nsl  = input.float(3, "Stop-loss", step= 0.5,  group = "Entry")\ntp  = input.float(9, "Take-profit", step= 0.5, group = "Entry")\nstop_loss_price = strategy.position_avg_price * (1-sl/100)\ntake_price = strategy.position_avg_price * (1+tp/100)\n\nsl_trl = input.float(2, "Trailing-stop", step = 0.5, tooltip = "Attiva trailing stop dopo che ha raggiunto...",group = "Trailing Stop Settings")//group = "Trailing Stop Settings")\nAtrl= input.float(1, "Offset Trailing", step=0.5,tooltip = "Distanza dal prezzo", group = "Trailing Stop Settings")\nstop_trl_price_cond = sl_trl * high/syminfo.mintick/100\nstop_trl_price_offset_cond = Atrl * high/syminfo.mintick/100\n\nstop_tick = sl * high/syminfo.mintick/100\nprofit_tick = tp * high/syminfo.mintick/100\n\nmess_buy = "buy"\nmess_sell = "sell"\n\n// -----------------------------------------------------------------------------\n// Entry - Exit - Close\n// -----------------------------------------------------------------------------\n\nif close < high_daily1 and roc_filter\n    strategy.entry("Entry", strategy.long, stop = high_daily1 + (Gap2), alert_message = mess_buy)\n\nts_n  = input.bool(true, "Trailing-stop", tooltip = "Attiva o disattiva trailing-stop", group = "Trailing Stop Settings")\nclose_ema = input.bool(false, "Close EMA", tooltip = "Attiva o disattiva chiusura su EMA", group = "Trailing Stop Settings")\nlen1 = input.int(10, "EMA length", step=1, group = "Trailing Stop Settings")\nma1 = ta.ema(close, len1)\n\nplot(ma1, title=\'EMA\', color=color.new(color.yellow, 0))\n\nif ts_n == true\n    strategy.exit("Trailing-Stop","Entry",loss= stop_tick, stop= stop_loss_price, limit= take_price, trail_points = stop_trl_price_cond, trail_offset = stop_trl_price_offset_cond, comment_loss="Stop-Loss!!",comment_profit ="CASH!!", comment_trailing = "TRL-Stop!!", alert_message = mess_sell)\nelse\n    strategy.exit("TP-SL", "Entry",loss= stop_tick, stop=stop_loss_price, limit= take_price, comment_loss= "Stop-loss!!!", comment_profit = "CASH!!", alert_message = mess_sell)\n\nif close_ema == true and ta.crossunder(close,ma1)\n    strategy.close("Entry",comment = "Close" , alert_message = mess_sell)\n\n'

class SM66D6A48953DA7036(PinePortBase, IStrategy):
    source_id = "SM_66d6a48953da7036"
    source_file = '突破昨日最高价策略Yesterdays-High-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'roc_enable': False, 'roc_threshold': 1, 'Gap': 1, 'sl': 3, 'tp': 9, 'sl_trl': 2, 'Atrl': 1, 'ts_n': True, 'close_ema': False, 'len1': 10}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 10
    source_commission_percent = 0.075
    source_pyramiding = 1
    source_initial_capital = 10000
    source_reproduce_stops = True
    source_risk_flags = ['mtf', 'func', 'broker_state', 'entry_price_order', 'exit_order', 'var_state', 'timeframe']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
