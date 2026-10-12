"""Source-faithful deep-assisted port of 条件开仓马丁.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_3c517316(PinePortBase, IStrategy):
    source_file = '条件开仓马丁.md'
    timeframe = '5m'
    can_short = False
    source_defaults = {'colorBe': 'color.new(#000000', 'colorBu': 'color.new(#4CAF50', 'multiplier': 1.8, 'lookback': 120, 'len': 7, 'lensig': 26}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 1
    source_initial_capital = 10000.0
    source_commission_percent = 0.04
    source_features = ['varip', 'label.']
    source_fidelity_notes = ['Uses persistent Pine state (var/varip); state is order-dependent and must be evaluated bar-by-bar, not replaced by a vectorized fill-forward approximation.', 'Drawing/table calls are display-only unless their IDs/state are later read; preserved in source map but excluded from trade signal calculation where non-causal.']
    pine_assignments = [{'mode': '', 'name': 'colorBe', 'op': '=', 'expr': 'input.color(title="Bearish candle", defval=color.new(#000000, 0))', 'conditions': []}, {'mode': '', 'name': 'colorBu', 'op': '=', 'expr': 'input.color(title="Bullish candle", defval=color.new(#4CAF50, 0))', 'conditions': []}, {'mode': '', 'name': 'multiplier', 'op': '=', 'expr': 'input.float(title="Multiplier", defval=1.8)', 'conditions': []}, {'mode': '', 'name': 'lookback', 'op': '=', 'expr': 'input.int(title="Lookback lenght", defval=120)', 'conditions': []}, {'mode': '', 'name': 'average', 'op': '=', 'expr': 'math.sum(high - low, lookback) / lookback * multiplier', 'conditions': []}, {'mode': '', 'name': 'averageVol', 'op': '=', 'expr': 'math.sum(volume, 200) / 200 * multiplier * 1.5', 'conditions': []}, {'mode': '', 'name': 'ema', 'op': '=', 'expr': 'ta.ema(close, 50)', 'conditions': []}, {'mode': '', 'name': 'len', 'op': '=', 'expr': 'input.int(7, minval=1, title="DI Length")', 'conditions': []}, {'mode': '', 'name': 'lensig', 'op': '=', 'expr': 'input.int(26, title="ADX Smoothing", minval=1, maxval=50)', 'conditions': []}, {'mode': 'varip', 'name': 'usedBuCandle', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': 'varip', 'name': 'usedBeCandle', 'op': '=', 'expr': 'false', 'conditions': []}, {'mode': '', 'name': 'bullishCondition', 'op': '=', 'expr': 'close > open and close > ema and high - low > average and adx>30 and adx < 50 and volume > averageVol and direction == -1', 'conditions': []}, {'mode': '', 'name': 'bearishCondition', 'op': '=', 'expr': 'close < open and close < ema and high - low > average and adx>30 and adx < 50 and volume > averageVol and direction == 1', 'conditions': []}, {'mode': '', 'name': 'usedBuCandle', 'op': ':=', 'expr': 'false', 'conditions': ['direction != direction[1]']}, {'mode': '', 'name': 'usedBeCandle', 'op': ':=', 'expr': 'false', 'conditions': ['direction != direction[1]']}, {'mode': '', 'name': 'usedBuCandle', 'op': ':=', 'expr': 'true', 'conditions': ['bullishCondition']}, {'mode': '', 'name': 'usedBeCandle', 'op': ':=', 'expr': 'true', 'conditions': ['bearishCondition']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if direction != direction[1]'}, {'indent': 0, 'statement': 'if bullishCondition and usedBuCandle == false'}, {'indent': 0, 'statement': 'else if bearishCondition and usedBeCandle == false'}, {'indent': 0, 'statement': 'if bullishCondition'}, {'indent': 0, 'statement': 'else if bearishCondition'}]
    pine_orders = []
    original_pine = '// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n//  DiegoRoz0\n//@version=5\n// https://cn.tradingview.com/script/76QDmNz9\n// 2022年，500%的利润\nstrategy("Big candle", overlay=true,  pyramiding=1,initial_capital = 10000, default_qty_type= strategy.percent_of_equity, default_qty_value = 100, calc_on_order_fills=false, slippage=0,commission_type=strategy.commission.percent,commission_value=0.04)\n\n//inputs\ncolorBe = input.color(title="Bearish candle", defval=color.new(#000000, 0))\ncolorBu = input.color(title="Bullish candle", defval=color.new(#4CAF50, 0))\nmultiplier = input.float(title="Multiplier", defval=1.8)\nlookback = input.int(title="Lookback lenght", defval=120)\n\naverage = math.sum(high - low, lookback) / lookback * multiplier\naverageVol = math.sum(volume, 200) / 200 * multiplier * 1.5\n\nema = ta.ema(close, 50)\nlen = input.int(7, minval=1, title="DI Length")\nlensig = input.int(26, title="ADX Smoothing", minval=1, maxval=50)\n[diplus, diminus, adx] = ta.dmi(len, lensig)\n\n[supertrend, direction] = ta.supertrend(2, 10)\n\nvarip usedBuCandle = false\nvarip usedBeCandle = false\nbullishCondition = close > open and close > ema and high - low > average and adx>30 and adx < 50 and volume > averageVol and direction == -1\nbearishCondition = close < open and close < ema and high - low > average and adx>30 and adx < 50 and volume > averageVol and direction == 1\n\nif direction != direction[1]\n    usedBuCandle := false\n    usedBeCandle := false\n\nbarcolor(bullishCondition and usedBuCandle == false ? colorBu: bearishCondition and usedBeCandle == false ? colorBe: na)\nif bullishCondition and usedBuCandle == false\n    label.new(bar_index, low, color = color.green, text = "Bu ", style = label.style_label_up)\n\nelse if bearishCondition and usedBeCandle == false\n    label.new(bar_index, high, color = color.orange, text = "Be ")\n\nif bullishCondition\n    usedBuCandle := true\n\nelse if bearishCondition \n    usedBeCandle := true \n\n//BACKTESTING inputs ----------------------------'

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
