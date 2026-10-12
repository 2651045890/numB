"""Source-faithful deep-assisted port of 月度趋势突破策略Monthly-Trend-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_a065614a(PinePortBase, IStrategy):
    source_file = '月度趋势突破策略Monthly-Trend-Breakout-Strategy.md'
    timeframe = '1d'
    can_short = False
    source_defaults = {'length_trama': 99}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close', 'var ', 'for ', 'line.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': 'var', 'name': 'lastEntryMonth', 'op': '=', 'expr': 'na', 'conditions': []}, {'mode': '', 'name': 'currentMonth', 'op': '=', 'expr': 'month(time)', 'conditions': []}, {'mode': '', 'name': 'length_trama', 'op': '=', 'expr': 'input(99)', 'conditions': []}, {'mode': '', 'name': 'src_trama', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'ama', 'op': '=', 'expr': '0.', 'conditions': []}, {'mode': '', 'name': 'hh', 'op': '=', 'expr': 'math.max(math.sign(ta.change(ta.highest(length_trama))), 0)', 'conditions': []}, {'mode': '', 'name': 'll', 'op': '=', 'expr': 'math.max(math.sign(ta.change(ta.lowest(length_trama)) * -1), 0)', 'conditions': []}, {'mode': '', 'name': 'tc', 'op': '=', 'expr': 'math.pow(ta.sma(hh or ll ? 1 : 0, length_trama), 2)', 'conditions': []}, {'mode': '', 'name': 'ama', 'op': ':=', 'expr': 'nz(ama[1] + tc * (src_trama - ama[1]), src_trama)', 'conditions': []}, {'mode': '', 'name': 'length_trend', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'mult', 'op': '=', 'expr': '1.0', 'conditions': []}, {'mode': '', 'name': 'ph', 'op': '=', 'expr': 'ta.pivothigh(length_trend, length_trend)', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': '=', 'expr': '0.', 'conditions': []}, {'mode': '', 'name': 'slope_ph', 'op': '=', 'expr': '0.', 'conditions': []}, {'mode': '', 'name': 'slope_ph', 'op': ':=', 'expr': 'ph ? mult : slope_ph', 'conditions': []}, {'mode': '', 'name': 'upper', 'op': ':=', 'expr': 'ph ? ph : upper - slope_ph', 'conditions': []}, {'mode': '', 'name': 'rsiLength', 'op': '=', 'expr': '14', 'conditions': []}, {'mode': '', 'name': 'up', 'op': '=', 'expr': 'ta.rma(math.max(ta.change(close), 0), rsiLength)', 'conditions': []}, {'mode': '', 'name': 'down', 'op': '=', 'expr': 'ta.rma(-math.min(ta.change(close), 0), rsiLength)', 'conditions': []}, {'mode': '', 'name': 'rsi', 'op': '=', 'expr': 'down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'close > ama and ta.crossover(close, upper) and (na(lastEntryMonth) or lastEntryMonth != currentMonth)', 'conditions': []}, {'mode': '', 'name': 'lastEntryMonth', 'op': ':=', 'expr': 'currentMonth', 'conditions': ['(longCondition)']}, {'mode': '', 'name': 'exitCondition', 'op': '=', 'expr': 'rsi > 70', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if (exitCondition)'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Long', strategy.long)", 'conditions': ['(longCondition)'], 'statement': "strategy.entry('Long', strategy.long)"}, {'kind': 'close', 'call': "strategy.close('Long')", 'conditions': ['(exitCondition)'], 'statement': "strategy.close('Long')"}]
    original_pine = '/*backtest\nstart: 2022-10-17 00:00:00\nend: 2023-10-23 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'Bannos Strategy\', shorttitle=\'Bannos\', overlay=true)\n\n//The provided script is an indicator for TradingView written in Pine Script version 5. The indicator is used to determine entry and exit points for a trading strategy. Here\'s a detailed breakdown of what the script does:\n\n// Strategy Definition:\n\n// Bannos Strategy is the full name, with a short title Bannos.\n// The overlay=true option indicates that the strategy will be overlayed on the price chart.\n// Tracking Entry Month:\n\n// A variable lastEntryMonth is set up to track the month of the last entry.\n// currentMonth identifies the current month.\n// Trend Regularity Adaptive Moving Average (TRAMA):\n\n// It takes an input of length 99 as default.\n// It uses adaptive calculations to track trend changes.\n// Trendlines with Breaks:\n\n// Identifies local peaks over a given period (in this case, 14) and calculates a slope based on these peaks.\n// Relative Strength Index (RSI):\n\n// Uses a length of 14 (default) to calculate the RSI.\n// RSI is an oscillation indicator that indicates overbought or oversold conditions.\n// Strategy Logic for Long Entry:\n\n// A long position is opened if:\n// The close price is above the TRAMA.\n// There\'s a crossover of the close price and the upper trendline.\n// The position is taken only once per month.\n// Strategy Logic for Long Exit:\n\n// The long position is closed if the RSI exceeds 70, indicating an overbought condition.\n// Plotting:\n\n// The TRAMA is plotted in red on the chart.\n// A horizontal line is also drawn at 70 to indicate the RSI\'s overbought zone.\n// In summary, this strategy aims to enter a long position when certain trend and crossover conditions are met, and close the position when the market is considered overbought as per the RSI. Additionally, it ensures entries only occur once a month.\n//\n\n\n\n// Variable pour suivre le mois de la dernière entrée\nvar float lastEntryMonth = na\ncurrentMonth = month(time)\n\n// Parameters for Trend Regularity Adaptive Moving Average (TRAMA)\nlength_trama = input(99)\nsrc_trama = close\nama = 0.\nhh = math.max(math.sign(ta.change(ta.highest(length_trama))), 0)\nll = math.max(math.sign(ta.change(ta.lowest(length_trama)) * -1), 0)\ntc = math.pow(ta.sma(hh or ll ? 1 : 0, length_trama), 2)\nama := nz(ama[1] + tc * (src_trama - ama[1]), src_trama)\n\n// Parameters for Trendlines with Breaks\nlength_trend = 14\nmult = 1.0\nph = ta.pivothigh(length_trend, length_trend)\nupper = 0.\nslope_ph = 0.\nslope_ph := ph ? mult : slope_ph\nupper := ph ? ph : upper - slope_ph\n\n// Parameters for RSI\nrsiLength = 14\nup = ta.rma(math.max(ta.change(close), 0), rsiLength)\ndown = ta.rma(-math.min(ta.change(close), 0), rsiLength)\nrsi = down == 0 ? 100 : up == 0 ? 0 : 100 - (100 / (1 + up / down))\n\n// Strategy Logic for Long Entry\nlongCondition = close > ama and ta.crossover(close, upper) and (na(lastEntryMonth) or lastEntryMonth != currentMonth)\nif (longCondition)\n    lastEntryMonth := currentMonth\n    strategy.entry(\'Long\', strategy.long)\n\n// Strategy Logic for Long Exit\nexitCondition = rsi > 70\nif (exitCondition)\n    strategy.close(\'Long\')\n\n// Plotting\nplot(ama, \'TRAMA\', color=color.red)\nhline(70, \'Overbought\', color=color.red)'

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
