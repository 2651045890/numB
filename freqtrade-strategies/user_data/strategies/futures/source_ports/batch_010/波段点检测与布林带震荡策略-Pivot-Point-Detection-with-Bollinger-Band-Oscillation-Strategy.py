"""Source-faithful deep-assisted port of 波段点检测与布林带震荡策略-Pivot-Point-Detection-with-Bollinger-Band-Oscillation-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_b7ffe8cf(PinePortBase, IStrategy):
    source_file = '波段点检测与布林带震荡策略-Pivot-Point-Detection-with-Bollinger-Band-Oscillation-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {'lookback': 20, 'std_factor': 2, 'atr_lookback': 14, 'bb_percentile': 25, 'atr_percentile': 30}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'lookback', 'op': '=', 'expr': 'input(20, title="Bollinger Bands Lookback")', 'conditions': []}, {'mode': '', 'name': 'std_factor', 'op': '=', 'expr': 'input(2, title="Bollinger Bands Std Dev")', 'conditions': []}, {'mode': '', 'name': 'atr_lookback', 'op': '=', 'expr': 'input(14, title="ATR Lookback")', 'conditions': []}, {'mode': '', 'name': 'bb_percentile', 'op': '=', 'expr': 'input(25, title="BB Width Percentile") / 100 // Convert to decimal', 'conditions': []}, {'mode': '', 'name': 'atr_percentile', 'op': '=', 'expr': 'input(30, title="ATR Percentile") / 100 // Convert to decimal', 'conditions': []}, {'mode': '', 'name': 'ma', 'op': '=', 'expr': 'ta.sma(close, lookback)', 'conditions': []}, {'mode': '', 'name': 'bb_std', 'op': '=', 'expr': 'ta.stdev(close, lookback)', 'conditions': []}, {'mode': '', 'name': 'upper_bb', 'op': '=', 'expr': 'ma + (std_factor * bb_std)', 'conditions': []}, {'mode': '', 'name': 'lower_bb', 'op': '=', 'expr': 'ma - (std_factor * bb_std)', 'conditions': []}, {'mode': '', 'name': 'bb_width', 'op': '=', 'expr': '(upper_bb - lower_bb) / ma', 'conditions': []}, {'mode': '', 'name': 'atr', 'op': '=', 'expr': 'ta.atr(atr_lookback)', 'conditions': []}, {'mode': '', 'name': 'nATR', 'op': '=', 'expr': 'atr / close', 'conditions': []}, {'mode': '', 'name': 'bb_width_min', 'op': '=', 'expr': 'ta.lowest(bb_width, lookback)', 'conditions': []}, {'mode': '', 'name': 'bb_width_max', 'op': '=', 'expr': 'ta.highest(bb_width, lookback)', 'conditions': []}, {'mode': '', 'name': 'bb_threshold', 'op': '=', 'expr': 'bb_width_min + (bb_width_max - bb_width_min) * bb_percentile', 'conditions': []}, {'mode': '', 'name': 'nATR_min', 'op': '=', 'expr': 'ta.lowest(nATR, lookback)', 'conditions': []}, {'mode': '', 'name': 'nATR_max', 'op': '=', 'expr': 'ta.highest(nATR, lookback)', 'conditions': []}, {'mode': '', 'name': 'atr_threshold', 'op': '=', 'expr': 'nATR_min + (nATR_max - nATR_min) * atr_percentile', 'conditions': []}, {'mode': '', 'name': 'sideways', 'op': '=', 'expr': 'bb_width < bb_threshold', 'conditions': []}, {'mode': '', 'name': 'middle_bb', 'op': '=', 'expr': '(upper_bb + lower_bb) / 2', 'conditions': []}, {'mode': '', 'name': 'close_to_middle', 'op': '=', 'expr': 'math.abs(close - middle_bb) / close < 0.02 // Within 2% of middle BB', 'conditions': []}, {'mode': '', 'name': 'buy_signal', 'op': '=', 'expr': 'sideways and (nATR < atr_threshold) and close_to_middle', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=buy_signal)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=buy_signal)'}]
    original_pine = '/*backtest\nstart: 2024-03-25 00:00:00\nend: 2025-03-24 00:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BNB_USDT"}]\n*/\n\n//@version=5\nstrategy("Pivot Point Detection", overlay=true)\n\n// === INPUT PARAMETERS ===\nlookback = input(20, title="Bollinger Bands Lookback")\nstd_factor = input(2, title="Bollinger Bands Std Dev")\natr_lookback = input(14, title="ATR Lookback")\nbb_percentile = input(25, title="BB Width Percentile") / 100  // Convert to decimal\natr_percentile = input(30, title="ATR Percentile") / 100  // Convert to decimal\n\n// === BOLLINGER BANDS CALCULATION ===\nma = ta.sma(close, lookback)\nbb_std = ta.stdev(close, lookback)\nupper_bb = ma + (std_factor * bb_std)\nlower_bb = ma - (std_factor * bb_std)\nbb_width = (upper_bb - lower_bb) / ma\n\n// === ATR & NORMALIZED ATR ===\natr = ta.atr(atr_lookback)\nnATR = atr / close\n\n// === APPROXIMATING PERCENTILE USING ROLLING LOWEST & HIGHEST ===\n// This approximates the percentile value by interpolating within a rolling window.\nbb_width_min = ta.lowest(bb_width, lookback)\nbb_width_max = ta.highest(bb_width, lookback)\nbb_threshold = bb_width_min + (bb_width_max - bb_width_min) * bb_percentile\n\nnATR_min = ta.lowest(nATR, lookback)\nnATR_max = ta.highest(nATR, lookback)\natr_threshold = nATR_min + (nATR_max - nATR_min) * atr_percentile\n\n// === SIDEWAYS MARKET CONFIRMATION ===\nsideways = bb_width < bb_threshold\n\n// === BUY SIGNAL LOGIC ===\nmiddle_bb = (upper_bb + lower_bb) / 2\nclose_to_middle = math.abs(close - middle_bb) / close < 0.02  // Within 2% of middle BB\n\nbuy_signal = sideways and (nATR < atr_threshold) and close_to_middle\n\n// === PLOT BOLLINGER BANDS ===\nplot(upper_bb, color=color.gray, linewidth=1, title="Upper BB")\nplot(lower_bb, color=color.gray, linewidth=1, title="Lower BB")\n\n// === PLOT BUY SIGNALS ===\nplotshape(buy_signal, location=location.belowbar, color=color.green, style=shape.labelup, size=size.small, title="Buy Signal")\n\n// === STRATEGY EXECUTION ===\nstrategy.entry("Buy", strategy.long, when=buy_signal)'

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
