"""batch_011 port of 策略与买入持有的可视化比较Visual-Comparison-between-Strategy-and-Buy-Hold-Returns.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-12-28 00:00:00\nend: 2024-01-04 00:00:00\nperiod: 3m\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=4\nstrategy("VS Buy Hold", precision=2)\n\nbnh_info_panel = input(true, title=\'Enable Info Panel\')\nbnh_indicator_panel = input(true, title=\'Enable Indicator Panel\')\n\n//COMPARISON DATE RANGE//\nbnh_FromYear = input(1970, title="From Year", minval=1970)\nbnh_FromMonth = input(1, title="From Month", minval=1, maxval=12)\nbnh_FromDay = input(1, title="From Day", minval=1, maxval=31)\n\nbnh_ToYear = input(2050, title="To Year", minval=2010)\nbnh_ToMonth = input(12, title="To Month", minval=1, maxval=12)\nbnh_ToDay = input(31, title="To Day", minval=1, maxval=31)\n\nbnh_start = timestamp(bnh_FromYear, bnh_FromMonth, bnh_FromDay, 00, 00)\nbnh_finish = timestamp(bnh_ToYear, bnh_ToMonth, bnh_ToDay, 23, 59)\nbnh_timeCond = time >= bnh_start and time <= bnh_finish ? true: false\n    \n//Note: If you are going to use the COMPARISON DATE RANGE above, apply bnh_timeCond\n//      to your strategy parameters.\n\n\n/////////////////////////////////////////////////////////////////////////////////////\n//////////////////////////////STRATEGY SCRIPT START//////////////////////////////////\n\n//=========================PLACEHOLDER MA CROSS STRATEGY=========================//\nfastLength = 50\nslowLength = 200\nprice = close\n\nmafast = sma(price, fastLength)\nmaslow = sma(price, slowLength)\nstrategy.initial_capital = 50000\npositionSize = strategy.initial_capital / close\n\nif (crossover(mafast, maslow) and bnh_timeCond) // <= bnh_timeCond added as a condition\n    strategy.entry("MA2CrossLE", strategy.long, positionSize, comment="MA2CrossLE")\n\nif (crossunder(mafast, maslow) and bnh_timeCond) // <= bnh_timeCond added as a condition\n    strategy.entry("MA2CrossSE", strategy.short, positionSize, comment="MA2CrossSE")\n\n//////////////////////////////STRATEGY SCRIPT END////////////////////////////////////\n/////////////////////////////////////////////////////////////////////////////////////\n\n\n\n//STRATEGY EQUITY\nstrategy_pnl = strategy.netprofit + strategy.openprofit\nbnh_strategy_pnl_pcnt = (strategy_pnl / strategy.initial_capital) * 100\n\n\n//BUY AND HOLD EQUITY\nfloat bnh_start_bar = na\nbnh_start_bar := na(bnh_start_bar[1]) and bnh_timeCond? close : bnh_start_bar[1]\nbnl_buy_hold_equity = ((close - bnh_start_bar)/bnh_start_bar) * 100\n\n\n//STRATEGY VS BUY AND HOLD STATS\nbnh_vs_diff = bnh_strategy_pnl_pcnt - bnl_buy_hold_equity\n\nbnh_bar_counter = 0\nbnh_bar_counter := bnh_vs_diff > 0 ? nz(bnh_bar_counter[1]) + 1 : bnh_bar_counter[1]\n\nbnh_bar_counter2 = 0\nbnh_bar_counter2 := bnh_vs_diff <= 0 ? nz(bnh_bar_counter2[1]) + 1 : bnh_bar_counter2[1]\n\nbnh_pcnt_above = (bnh_bar_counter/(bnh_bar_counter + bnh_bar_counter2))*100\nbnh_pcnt_below = (bnh_bar_counter2/(bnh_bar_counter + bnh_bar_counter2))*100\n\nbnh_average_diff = cum(bnh_vs_diff) / (bnh_bar_counter + bnh_bar_counter2)\n\n\n//PLOTS AND LABELS\nbnh_diff_color = bnh_vs_diff > 0 ? color.green : color.red\nplot(bnh_vs_diff, style=plot.style_columns, color=bnh_diff_color, transp=60, title=\'SvB\')\nplot(bnh_strategy_pnl_pcnt, color=color.yellow, linewidth=2, title="SR")\nplot(bnl_buy_hold_equity, color=color.blue, title="BHR")\n\n// draw_IndicatorLabel(_text, _x, _y, label_color, font_color)=>\n//     string_text = _text\n//     var label la_indicator = na\n//     label.delete(la_indicator)\n//     la_indicator := label.new(\n//          x=_x, y=_y, \n//          text=string_text, xloc=xloc.bar_index, yloc=yloc.price, \n//          color=label_color, style=label.style_labeldown, textcolor=font_color, size=size.small)\n\n// draw_InfoPanel(_text, _x, _y, font_size)=>\n//     var label la_panel = na\n//     label.delete(la_panel)\n//     la_panel := label.new(\n//          x=_x, y=_y, \n//          text=_text, xloc=xloc.bar_time, yloc=yloc.price, \n//          color=color.new(#383838, 5), style=label.style_labelup, textcolor=color.white, size=font_size)\n\n// if bnh_indicator_panel         \n//     draw_IndicatorLabel("Difference", bar_index, bnh_vs_diff, color.new(color.gray, 40), color.white)\n//     draw_IndicatorLabel("Strategy P/L", bar_index, bnh_strategy_pnl_pcnt, color.new(color.yellow, 50), color.white)\n//     draw_IndicatorLabel("Buy & Hold P/L", bar_index, bnl_buy_hold_equity, color.new(color.blue, 50), color.white)\n\n// info_panel_x = time_close + round(change(time) * 200)\n// info_panel_y = max(max(bnl_buy_hold_equity, bnh_strategy_pnl_pcnt), bnh_vs_diff) + abs(bnh_vs_diff * 0.25)\n\n\n// title = "STRATEGY vs BUY & HOLD STATS"\n// row0 = "-----------------------------------------------------"\n// row1 = \'Bars Above Buy & Hold: \' + tostring(bnh_pcnt_above, \'#.##\') + \'%\'\n// row2 = \'Bars Below Buy & Hold: \' + tostring(bnh_pcnt_below, \'#.##\') + \'%\'\n// row3 = \'All Time Ave. Difference: \' + tostring(bnh_average_diff, \'#.##\') + \'%\'\n\n// panel_text = \'\\n\' + title + \'\\n\' + row0 + \'\\n\' + row1 + \'\\n\\n\' + row2 + \'\\n\\n\' + row3 + \'\\n\'\n\n// if bnh_info_panel\n//     draw_InfoPanel(panel_text, info_panel_x, info_panel_y, size.normal)\n\n'

class SMC4A11984E2C0F60E(PinePortBase, IStrategy):
    source_id = "SM_c4a11984e2c0f60e"
    source_file = '策略与买入持有的可视化比较Visual-Comparison-between-Strategy-and-Buy-Hold-Returns.md'
    timeframe = '3m'
    can_short = True
    source_defaults = {'bnh_info_panel': True, 'bnh_indicator_panel': True, 'bnh_FromYear': 1970, 'bnh_FromMonth': 1, 'bnh_FromDay': 1, 'bnh_ToYear': 2050, 'bnh_ToMonth': 12, 'bnh_ToDay': 31}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['func', 'broker_state', 'var_state', 'alert_or_drawing']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
