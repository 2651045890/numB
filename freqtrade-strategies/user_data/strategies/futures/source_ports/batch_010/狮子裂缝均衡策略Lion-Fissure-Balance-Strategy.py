"""Source-faithful deep-assisted port of 狮子裂缝均衡策略Lion-Fissure-Balance-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_450311e5(PinePortBase, IStrategy):
    source_file = '狮子裂缝均衡策略Lion-Fissure-Balance-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'source': 'close', 'smallMAPeriod': 2, 'bigMAPeriod': 8, 'percentBelowToBuy': 1}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 5.0
    source_pyramiding = 0
    source_initial_capital = 10000.0
    source_commission_percent = 0.1
    source_features = ['strategy.entry', 'strategy.close', 'strategy.closedtrades', 'strategy.equity', 'var ', 'for ', '=>', 'barstate.', 'table.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'source', 'op': '=', 'expr': 'input(title = "Source", defval = close)', 'conditions': []}, {'mode': '', 'name': 'smallMAPeriod', 'op': '=', 'expr': 'input(title = "Small Moving Average", defval = 2)', 'conditions': []}, {'mode': '', 'name': 'bigMAPeriod', 'op': '=', 'expr': 'input(title = "Big Moving Average", defval = 8)', 'conditions': []}, {'mode': '', 'name': 'percentBelowToBuy', 'op': '=', 'expr': 'input(title = "Percent below to buy %", defval = 1)', 'conditions': []}, {'mode': '', 'name': 'smallMA', 'op': '=', 'expr': 'ta.sma(source, smallMAPeriod)', 'conditions': []}, {'mode': '', 'name': 'bigMA', 'op': '=', 'expr': 'ta.sma(source, bigMAPeriod)', 'conditions': []}, {'mode': '', 'name': 'buyMA', 'op': '=', 'expr': '((100 - percentBelowToBuy) / 100) * ta.sma(source, bigMAPeriod)[0]', 'conditions': []}, {'mode': '', 'name': 'buy', 'op': '=', 'expr': 'ta.crossunder(smallMA, buyMA)', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if(buy)'}, {'indent': 0, 'statement': 'if(strategy.openprofit >= strategy.position_avg_price * 0.01) // 1% profit target'}, {'indent': 0, 'statement': 'if(ta.barssince(buy) >= 7) //Timed Exit, if you fail to make 1 percent in 7 candles.'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("BUY", strategy.long)', 'conditions': [], 'statement': 'strategy.entry("BUY", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("BUY")', 'conditions': [], 'statement': 'strategy.close("BUY")'}, {'kind': 'close', 'call': 'strategy.close("BUY")', 'conditions': [], 'statement': 'strategy.close("BUY")'}]
    original_pine = '/*backtest\nstart: 2023-10-02 00:00:00\nend: 2023-11-01 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © TraderHalai\n// This script was born out of my quest to be able to display strategy back test statistics on charts to allow for easier backtesting on devices that do not natively support backtest engine (such as mobile phones, when I am backtesting from away from my computer). There are already a few good ones on TradingView, but most / many are too complicated for my needs.\n//\n//Found an excellent display backtest engine by \'The Art of Trading\'. This script is a snippet of his hard work, with some very minor tweaks and changes. Much respect to the original author.\n//\n//Full credit to the original author of this script. It can be found here: https://www.tradingview.com/script/t776tkZv-Hammers-Stars-Strategy/?offer_id=10&aff_id=15271\n//\n// This script can be copied and airlifted onto existing strategy scripts of your own, and integrates out of the box without implementation of additional functions. I\'ve also added Max Runup, Average Win and Average Loss per trade to the orignal script.\n//\n//Will look to add in more performance metrics in future, as I further develop this script.\n//\n//Feel free to use this display panel in your scripts and strategies.\n\n//Thanks and enjoy! :)\n//@version=5\n// strategy("Strategy BackTest Display Statistics - TraderHalai", overlay=true, default_qty_value= 5, default_qty_type = strategy.percent_of_equity, initial_capital=10000,  commission_type=strategy.commission.percent, commission_value=0.1)\n\n//DEMO basic strategy - Use your own strategy here -  Jaws Mean Reversion from my profile used here\nsource = input(title = "Source", defval = close)\nsmallMAPeriod = input(title = "Small Moving Average", defval = 2)\nbigMAPeriod = input(title = "Big Moving Average", defval = 8)\npercentBelowToBuy = input(title = "Percent below to buy %", defval = 1)\n\nsmallMA = ta.sma(source, smallMAPeriod)\nbigMA =  ta.sma(source, bigMAPeriod) \nbuyMA = ((100 - percentBelowToBuy) / 100) * ta.sma(source, bigMAPeriod)[0]\n\nbuy = ta.crossunder(smallMA, buyMA)\nif(buy)\n    strategy.entry("BUY", strategy.long)\n\nif(strategy.openprofit >= strategy.position_avg_price * 0.01) // 1% profit target\n    strategy.close("BUY")\n\nif(ta.barssince(buy) >= 7) //Timed Exit, if you fail to make 1 percent in 7 candles.\n    strategy.close("BUY")\n    \n///////////////////////////// --- BEGIN TESTER CODE --- ////////////////////////\n// COPY below into your strategy to enable display\n////////////////////////////////////////////////////////////////////////////////\n\n// strategy.initial_capital = 50000\n// // Declare performance tracking variables\n// drawTester = input.bool(true, "Draw Tester")\n// var balance = strategy.initial_capital\n// var drawdown = 0.0\n// var maxDrawdown = 0.0\n// var maxBalance = 0.0\n// var totalWins = 0\n// var totalLoss = 0\n\n// // Prepare stats table\n// var table testTable = table.new(position.top_right, 5, 2, border_width=1)\n// f_fillCell(_table, _column, _row, _title, _value, _bgcolor, _txtcolor) =>\n//     _cellText = _title + "\\n" + _value\n//     table.cell(_table, _column, _row, _cellText, bgcolor=_bgcolor, text_color=_txtcolor)\n    \n// // Custom function to truncate (cut) excess decimal places\n// truncate(_number, _decimalPlaces) =>\n//     _factor = math.pow(10, _decimalPlaces)\n//     int(_number * _factor) / _factor\n    \n// // Draw stats table\n// var bgcolor = color.new(color.black,0)\n// if drawTester\n//     if barstate.islastconfirmedhistory\n//         // Update table\n//         dollarReturn = strategy.netprofit\n//         f_fillCell(testTable, 0, 0, "Total Trades:", str.tostring(strategy.closedtrades), bgcolor, color.white)\n//         f_fillCell(testTable, 0, 1, "Win Rate:", str.tostring(truncate((strategy.wintrades/strategy.closedtrades)*100,2)) + "%", bgcolor, color.white)\n//         f_fillCell(testTable, 1, 0, "Starting:", "$" + str.tostring(strategy.initial_capital), bgcolor, color.white)\n//         f_fillCell(testTable, 1, 1, "Ending:", "$" + str.tostring(truncate(strategy.initial_capital + strategy.netprofit,2)), bgcolor, color.white)\n//         f_fillCell(testTable, 2, 0, "Avg Win:", "$"+ str.tostring(truncate(strategy.grossprofit / strategy.wintrades, 2)), bgcolor, color.white)\n//         f_fillCell(testTable, 2, 1, "Avg Loss:", "$"+ str.tostring(truncate(strategy.grossloss / strategy.losstrades, 2)), bgcolor, color.white)\n//         f_fillCell(testTable, 3, 0, "Profit Factor:", str.tostring(truncate(strategy.grossprofit / strategy.grossloss,2)), strategy.grossprofit > strategy.grossloss ? color.green : color.red, color.white)\n//         f_fillCell(testTable, 3, 1, "Max Runup:",  str.tostring(truncate(strategy.max_runup, 2 )), bgcolor, color.white)\n//         f_fillCell(testTable, 4, 0, "Return:", (dollarReturn > 0 ? "+" : "") + str.tostring(truncate((dollarReturn / strategy.initial_capital)*100,2)) + "%", dollarReturn > 0 ? color.green : color.red, color.white)\n//         f_fillCell(testTable, 4, 1, "Max DD:", str.tostring(truncate((strategy.max_drawdown / strategy.equity) * 100 ,2)) + "%", color.red, color.white)\n// // --- END TESTER CODE --- ///////////////'

    def pine_indicators(self, dataframe, params):
        self._semantic_rt = SemanticRuntime(dataframe, params, self.pine_assignments, self.pine_user_functions)
        return self._semantic_rt.materialize()

    def pine_context(self, dataframe, params):
        # Keep the complete, strategy-specific semantic program available to the
        # broker replay layer.  Hand-audited files replace this with compact numpy
        # arrays; assisted files intentionally retain the original expressions.
        return {'dataframe': dataframe, 'params': dict(params), 'orders': self.pine_orders,
                'assignments': self.pine_assignments, 'functions': self.pine_user_functions,
                'source': self.original_pine}

    def pine_script(self, broker, i, ctx):
        # The order program is preserved explicitly above.  Stateful Pine programs
        # (var/arrays/security/broker-state reads) require the chain verifier/runtime
        # replay to execute their exact bar-by-bar semantics.  This method does not
        # fabricate orders when an expression cannot be proven equivalent.
        replay = getattr(broker, 'replay_source_program', None)
        if replay is not None:
            return replay(self.original_pine, i, ctx)
        return None
