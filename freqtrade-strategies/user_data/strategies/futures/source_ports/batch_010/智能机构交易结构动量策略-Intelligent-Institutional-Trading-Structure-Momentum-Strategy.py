"""Source-faithful deep-assisted port of 智能机构交易结构动量策略-Intelligent-Institutional-Trading-Structure-Momentum-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_eb4bfdd7(PinePortBase, IStrategy):
    source_file = '智能机构交易结构动量策略-Intelligent-Institutional-Trading-Structure-Momentum-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'ema_fast', 'op': '=', 'expr': 'ta.ema(close, 9)', 'conditions': []}, {'mode': '', 'name': 'ema_slow', 'op': '=', 'expr': 'ta.ema(close, 21)', 'conditions': []}, {'mode': '', 'name': 'bullish_structure', 'op': '=', 'expr': 'ta.crossover(ema_fast, ema_slow)', 'conditions': []}, {'mode': '', 'name': 'bearish_structure', 'op': '=', 'expr': 'ta.crossunder(ema_fast, ema_slow)', 'conditions': []}, {'mode': '', 'name': 'liquidity_high', 'op': '=', 'expr': 'ta.highest(high, 50)', 'conditions': []}, {'mode': '', 'name': 'liquidity_low', 'op': '=', 'expr': 'ta.lowest(low, 50)', 'conditions': []}, {'mode': '', 'name': 'is_institutional_bullish', 'op': '=', 'expr': 'close > open and volume > ta.sma(volume, 50)', 'conditions': []}, {'mode': '', 'name': 'is_institutional_bearish', 'op': '=', 'expr': 'close < open and volume > ta.sma(volume, 50)', 'conditions': []}, {'mode': '', 'name': 'long_entry', 'op': '=', 'expr': 'bullish_structure and is_institutional_bullish', 'conditions': []}, {'mode': '', 'name': 'short_entry', 'op': '=', 'expr': 'bearish_structure and is_institutional_bearish', 'conditions': []}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (long_entry)'}, {'indent': 0, 'statement': 'if (short_entry)'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long", strategy.long, stop=liquidity_low, comment="BUY")', 'conditions': ['(long_entry)'], 'statement': 'strategy.entry("Long", strategy.long, stop=liquidity_low, comment="BUY")'}, {'kind': 'entry', 'call': 'strategy.entry("Short", strategy.short, stop=liquidity_high, comment="SELL")', 'conditions': ['(short_entry)'], 'statement': 'strategy.entry("Short", strategy.short, stop=liquidity_high, comment="SELL")'}]
    original_pine = '/*backtest\nstart: 2019-12-23 08:00:00\nend: 2024-09-24 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("SMC + ICT Scalping Strategy", overlay=true)\n\n// إعداد المتوسطات المتحركة\nema_fast = ta.ema(close, 9)\nema_slow = ta.ema(close, 21)\n\n// تحديد الهيكل السوقي (الاتجاه)\nbullish_structure = ta.crossover(ema_fast, ema_slow)\nbearish_structure = ta.crossunder(ema_fast, ema_slow)\n\n// تحديد مناطق السيولة (Liquidity Zones)\nliquidity_high = ta.highest(high, 50)\nliquidity_low = ta.lowest(low, 50)\n\n// تحديد الشموع المؤسسية (Institutional Candles)\nis_institutional_bullish = close > open and volume > ta.sma(volume, 50)\nis_institutional_bearish = close < open and volume > ta.sma(volume, 50)\n\n// إشارة الدخول\nlong_entry = bullish_structure and is_institutional_bullish\nshort_entry = bearish_structure and is_institutional_bearish\n\n// تنفيذ صفقات الشراء\nif (long_entry)\n    strategy.entry("Long", strategy.long, stop=liquidity_low, comment="BUY")\n\n// تنفيذ صفقات البيع\nif (short_entry)\n    strategy.entry("Short", strategy.short, stop=liquidity_high, comment="SELL")\n\n// رسم المتوسطات المتحركة\nplot(ema_fast, color=color.blue, linewidth=1)\nplot(ema_slow, color=color.red, linewidth=1)'

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
