"""Source-faithful deep-assisted port of 无上引线看涨K线突破策略-No-Upper-Wick-Bullish-Candle-Breakout-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_6a20de4e(PinePortBase, IStrategy):
    source_file = '无上引线看涨K线突破策略-No-Upper-Wick-Bullish-Candle-Breakout-Strategy.md'
    timeframe = '1h'
    can_short = False
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['request.security', 'strategy.entry', 'strategy.close', 'strategy.position_size', 'timeframe.']
    source_fidelity_notes = ['Uses request.security / multi-timeframe context; exact parity depends on HTF resampling, gaps and lookahead semantics.', 'Uses barmerge.lookahead_on; source can intentionally expose/repaint future HTF values. Preserve when parity-testing, disable for live-safe testing only as a separate variant.', 'Reads broker/strategy state; signals depend on fill timing and cannot be reduced to indicator-only booleans without changing behavior.']
    pine_assignments = [{'mode': '', 'name': 'candleBodySize', 'op': '=', 'expr': 'math.abs(open - close)', 'conditions': []}, {'mode': '', 'name': 'candleWickSize', 'op': '=', 'expr': 'high - close', 'conditions': []}, {'mode': '', 'name': 'wickPercentage', 'op': '=', 'expr': '(candleWickSize / candleBodySize) * 100', 'conditions': []}, {'mode': '', 'name': 'isBullish', 'op': '=', 'expr': 'close > open', 'conditions': []}, {'mode': '', 'name': 'isWickLessThan5Percent', 'op': '=', 'expr': 'wickPercentage < 5', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': '=', 'expr': 'isBullish and isWickLessThan5Percent', 'conditions': []}, {'mode': '', 'name': 'prevLow', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'prevLow', 'op': ':=', 'expr': 'request.security(syminfo.tickerid, timeframe.period, low[1], lookahead=barmerge.lookahead_on)', 'conditions': []}, {'mode': '', 'name': 'closingPrice', 'op': '=', 'expr': 'close', 'conditions': []}, {'mode': '', 'name': 'longCondition', 'op': ':=', 'expr': 'false', 'conditions': ['closingPrice < prevLow and strategy.position_size > 0']}, {'mode': '', 'name': 'prevLow', 'op': ':=', 'expr': '0', 'conditions': ['closingPrice < prevLow and strategy.position_size > 0']}, {'mode': '', 'name': 'isBullish', 'op': ':=', 'expr': 'false', 'conditions': ['closingPrice < prevLow and strategy.position_size > 0']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if (longCondition)'}, {'indent': 0, 'statement': 'if closingPrice < prevLow and strategy.position_size > 0'}]
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Long Entry", strategy.long)', 'conditions': ['(longCondition)'], 'statement': 'strategy.entry("Long Entry", strategy.long)'}, {'kind': 'close', 'call': 'strategy.close("Long Entry")', 'conditions': ['closingPrice < prevLow and strategy.position_size > 0'], 'statement': 'strategy.close("Long Entry")'}]
    original_pine = '/*backtest\nstart: 2024-04-13 00:00:00\nend: 2024-05-13 00:00:00\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This Pine Script™ code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © nagpha\n\n//@version=5\nstrategy("My strategy", overlay=true, margin_long=100, margin_short=100)\n\ncandleBodySize = math.abs(open - close)\n\n// Calculate candle wick size\ncandleWickSize = high - close\n\n// Calculate percentage of wick to candle body\nwickPercentage = (candleWickSize / candleBodySize) * 100\n\n// Check if candle is bullish and wick is less than 1% of the body\nisBullish = close > open\nisWickLessThan5Percent = wickPercentage < 5\n\n\nlongCondition = isBullish and isWickLessThan5Percent\n\nif (longCondition)\n    // log.info("long position taken")\n    strategy.entry("Long Entry", strategy.long)\n\nfloat prevLow = 0.0\nprevLow := request.security(syminfo.tickerid, timeframe.period, low[1], lookahead=barmerge.lookahead_on)\n\nfloat closingPrice = close\n//plot(closingPrice, "Close Price", color.purple, 3)\n//plot(prevLow, "Previous Low", color.red, 3)\n//log.info("Outside: {0,number,#}",closingPrice)\n//log.info("Outside: {0,number,#}",prevLow)\n\nif closingPrice < prevLow and strategy.position_size > 0\n    //log.info("inside close: {0,number} : {0,number}",closingPrice,prevLow)\n    // log.info("position exited")\n    strategy.close("Long Entry")\n    longCondition := false\n    prevLow := 0\n    isBullish := false\n\n//plot(series=strategy.position_size > 0 ? prevLow : na, color = color.new(#40ccfb,0), style=plot.style_cross,linewidth = 5)'

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
