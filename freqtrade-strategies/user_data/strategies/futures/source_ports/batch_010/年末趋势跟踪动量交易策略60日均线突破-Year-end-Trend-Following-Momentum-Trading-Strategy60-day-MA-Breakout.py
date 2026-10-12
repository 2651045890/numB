"""Source-faithful deep-assisted port of 年末趋势跟踪动量交易策略60日均线突破-Year-end-Trend-Following-Momentum-Trading-Strategy60-day-MA-Breakout.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_fd7d37f2(PinePortBase, IStrategy):
    source_file = '年末趋势跟踪动量交易策略60日均线突破-Year-end-Trend-Following-Momentum-Trading-Strategy60-day-MA-Breakout.md'
    timeframe = '3m'
    can_short = False
    source_defaults = {'startDate': 'timestamp("2010-01-01"', 'endDate': 'timestamp("2024-12-31"', 'length': 60}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 1
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'for ', '=>']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'startDate', 'op': '=', 'expr': 'input(defval=timestamp("2010-01-01"), title="Start Date")', 'conditions': []}, {'mode': '', 'name': 'endDate', 'op': '=', 'expr': 'input(defval=timestamp("2024-12-31"), title="End Date")', 'conditions': []}, {'mode': '', 'name': 'length', 'op': '=', 'expr': 'input.int(defval=60, title="MA Length", minval=1)', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': 'ta.sma(close, length)', 'conditions': []}, {'mode': '', 'name': 'slope', 'op': '=', 'expr': 'ta.sma(ma, 14) - ta.sma(ma, 14)[1]', 'conditions': []}, {'mode': '', 'name': 'withinDateRange', 'op': '=', 'expr': 'true', 'conditions': []}, {'mode': '', 'name': 'isLastTradingDayOfYear', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'yearNow', 'op': '=', 'expr': 'year(time)', 'conditions': []}, {'mode': '', 'name': 'isLastTradingDayOfYear', 'op': ':=', 'expr': 'isTradingDay(time)', 'conditions': ['(month == 12 and dayofmonth == 31)']}, {'mode': '', 'name': 'isLastTradingDayOfYear', 'op': ':=', 'expr': 'isTradingDay(time) and not isTradingDay(time + 86400000)', 'conditions': ['(month == 12 and dayofmonth == 30)']}, {'mode': '', 'name': 'isLastTradingDayOfYear', 'op': ':=', 'expr': 'isTradingDay(time) and not isTradingDay(time + 86400000) and not isTradingDay(time + 86400000 * 2)', 'conditions': ['(month == 12 and dayofmonth == 29)']}]
    pine_user_functions = [{'name': 'isTradingDay', 'args': 'day', 'body': 'true'}]
    pine_controls = [{'indent': 0, 'statement': 'if (month == 12 and dayofmonth == 31)'}, {'indent': 0, 'statement': 'else if (month == 12 and dayofmonth == 30)'}, {'indent': 0, 'statement': 'else if (month == 12 and dayofmonth == 29)'}, {'indent': 0, 'statement': 'if (withinDateRange and ta.crossover(close, ma) and slope > 0)'}, {'indent': 0, 'statement': 'if (isLastTradingDayOfYear)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long)', 'conditions': ['(withinDateRange and ta.crossover(close, ma) and slope > 0)'], 'statement': 'strategy.entry("Buy", strategy.long)'}, {'kind': 'close_all', 'call': 'strategy.close_all(comment="Sell at year-end")', 'conditions': ['(isLastTradingDayOfYear)'], 'statement': 'strategy.close_all(comment="Sell at year-end")'}]
    original_pine = '/*backtest\nstart: 2025-01-09 00:00:00\nend: 2025-01-16 00:00:00\nperiod: 3m\nbasePeriod: 3m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":49999}]\n*/\n\n//@version=5\nstrategy("Buy above 60-day MA, Sell at year-end", overlay=true, pyramiding=1)\n\n// Define inputs for start and end dates\nstartDate = input(defval=timestamp("2010-01-01"), title="Start Date")\nendDate = input(defval=timestamp("2024-12-31"), title="End Date")\n\n// Define 60-day moving average\nlength = input.int(defval=60, title="MA Length", minval=1)\nma = ta.sma(close, length)\nslope = ta.sma(ma, 14) - ta.sma(ma, 14)[1]\n\n// Check if current bar is within the specified date range\nwithinDateRange = true\n\n// Function to check if a day is a trading day (Monday to Friday)\nisTradingDay(day) => true\n\n// Check if current bar is the last trading day of the year\n// Check if current bar is the last trading day of the year\nisLastTradingDayOfYear = false\nyearNow = year(time)\nif (month == 12 and dayofmonth == 31)\n    isLastTradingDayOfYear := isTradingDay(time)\nelse if (month == 12 and dayofmonth == 30)\n    isLastTradingDayOfYear := isTradingDay(time) and not isTradingDay(time + 86400000)\nelse if (month == 12 and dayofmonth == 29)\n    isLastTradingDayOfYear := isTradingDay(time) and not isTradingDay(time + 86400000) and not isTradingDay(time + 86400000 * 2)\n\n// Plot moving average\nplot(ma, color=color.blue, linewidth=2)\n\n// Buy when closing price crosses above 60-day MA and up trend\nif (withinDateRange and ta.crossover(close, ma) and slope > 0)\n    strategy.entry("Buy", strategy.long)\n\n// Sell all positions at the last trading day of the year\nif (isLastTradingDayOfYear)\n    strategy.close_all(comment="Sell at year-end")\n\n// Plot buy and sell signals\n//plotshape(series=ta.crossover(close, ma), location=location.belowbar, color=color.green, style=shape.labelup, text="Buy")\n//plotshape(series=isLastTradingDayOfYear, location=location.abovebar, color=color.red, style=shape.labeldown, text="Sell")'

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
