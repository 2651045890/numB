"""Source-faithful deep-assisted port of 平滑海坚线买卖策略Heikin-Ashi-Smoothed-Buy-and-Sell-Strategy.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_33a65fb8(PinePortBase, IStrategy):
    source_file = '平滑海坚线买卖策略Heikin-Ashi-Smoothed-Buy-and-Sell-Strategy.md'
    timeframe = '2d'
    can_short = False
    source_defaults = {'MaPeriod': 65}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100.0
    source_pyramiding = 0
    source_initial_capital = 1000.0
    source_commission_percent = 0.0
    source_features = ['strategy.entry', 'strategy.close']
    source_fidelity_notes = []
    pine_assignments = [{'mode': '', 'name': 'MaPeriod', 'op': '=', 'expr': 'input (title="Moving Average Period?", type=input.integer, defval=65, minval=5, maxval=100, step=5)', 'conditions': []}, {'mode': '', 'name': 'maOpen', 'op': '=', 'expr': 'ema(open , MaPeriod)', 'conditions': []}, {'mode': '', 'name': 'maHigh', 'op': '=', 'expr': 'ema(high , MaPeriod)', 'conditions': []}, {'mode': '', 'name': 'maLow', 'op': '=', 'expr': 'ema(low , MaPeriod)', 'conditions': []}, {'mode': '', 'name': 'maClose', 'op': '=', 'expr': 'ema(close, MaPeriod)', 'conditions': []}, {'mode': '', 'name': 'haClose', 'op': '=', 'expr': '(maOpen+maHigh+maLow+maClose)/4', 'conditions': []}, {'mode': '', 'name': 'haOpen', 'op': '=', 'expr': '0.0', 'conditions': []}, {'mode': '', 'name': 'haOpen', 'op': ':=', 'expr': 'na(haOpen[1]) ? (maOpen[1]+maClose[1])/2 : (haOpen[1]+haClose[1])/2', 'conditions': []}, {'mode': '', 'name': 'haHigh', 'op': '=', 'expr': 'max(maHigh, max(haClose, haOpen))', 'conditions': []}, {'mode': '', 'name': 'haLow', 'op': '=', 'expr': 'min(maLow , max(haClose, haOpen))', 'conditions': []}, {'mode': '', 'name': 'B0', 'op': '=', 'expr': 'haClose - haOpen', 'conditions': []}, {'mode': '', 'name': 'B1', 'op': '=', 'expr': 'haClose[1] - haOpen[1]', 'conditions': []}, {'mode': '', 'name': 'B2', 'op': '=', 'expr': 'haClose[2] - haOpen[2]', 'conditions': []}, {'mode': '', 'name': 'BuyCondition', 'op': '=', 'expr': 'B0 > 0.0 and B1 > 0.0 and B2 > 0.0 and haClose > haClose[1] and haClose[1] > haClose[2]', 'conditions': []}, {'mode': '', 'name': 'SellCondition', 'op': '=', 'expr': 'B0 < 0.0 and B1 < 0.0 and B2 < 0.0 and haClose < haClose[1] and haClose[1] < haClose[2]', 'conditions': []}, {'mode': '', 'name': 'last_signal', 'op': '=', 'expr': '0', 'conditions': []}, {'mode': '', 'name': 'Buy_final', 'op': '=', 'expr': 'BuyCondition and (nz(last_signal[1]) == 0 or nz(last_signal[1]) ==-1)', 'conditions': []}, {'mode': '', 'name': 'Sell_final', 'op': '=', 'expr': 'SellCondition and (nz(last_signal[1]) == 0 or nz(last_signal[1]) == 1)', 'conditions': []}, {'mode': '', 'name': 'last_signal', 'op': ':=', 'expr': 'Buy_final ? 1 : Sell_final ? -1 : last_signal[1]', 'conditions': []}]
    pine_user_functions = []
    pine_controls = []
    pine_orders = [{'kind': 'entry', 'call': 'strategy.entry("Buy", strategy.long, when=Buy_final)', 'conditions': [], 'statement': 'strategy.entry("Buy", strategy.long, when=Buy_final)'}, {'kind': 'close', 'call': 'strategy.close("Buy", when=Sell_final)', 'conditions': [], 'statement': 'strategy.close("Buy", when=Sell_final)'}]
    original_pine = '/*backtest\nstart: 2022-09-30 00:00:00\nend: 2023-10-06 00:00:00\nperiod: 2d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//Masoud Abdoli\n//Heikin Ashi Smoothed Buy & Sell Strategy Rev.4\n//Date: 01-Oct-2021\n//@version=4\n\nstrategy(title="Abdoli\'s Heikin Ashi Smoothed Buy & Sell Strategy Rev.4", shorttitle="Heikin-Ashi Smoothed Rev.4", overlay=true,\n initial_capital=1000, default_qty_type=strategy.percent_of_equity, default_qty_value=100)\n\nMaPeriod = input (title="Moving Average Period?", type=input.integer, defval=65, minval=5, maxval=100, step=5)\n\nmaOpen  = ema(open , MaPeriod)\nmaHigh  = ema(high , MaPeriod)\nmaLow   = ema(low  , MaPeriod)\nmaClose = ema(close, MaPeriod)\n\nhaClose = (maOpen+maHigh+maLow+maClose)/4\nhaOpen = 0.0\nhaOpen:= na(haOpen[1]) ? (maOpen[1]+maClose[1])/2 : (haOpen[1]+haClose[1])/2\nhaHigh = max(maHigh, max(haClose, haOpen))\nhaLow  = min(maLow , max(haClose, haOpen))\n\nplotcandle(haOpen, haHigh, haLow, haClose, title="heikin-Ashi smoothed", color=haOpen>haClose ? color.orange : color.blue)\n\nB0 = haClose    - haOpen\nB1 = haClose[1] - haOpen[1]\nB2 = haClose[2] - haOpen[2]\nBuyCondition = B0 > 0.0 and B1 > 0.0 and B2 > 0.0 and haClose > haClose[1] and haClose[1] > haClose[2]\nSellCondition= B0 < 0.0 and B1 < 0.0 and B2 < 0.0 and haClose < haClose[1] and haClose[1] < haClose[2]\n\nlast_signal = 0\nBuy_final  = BuyCondition  and (nz(last_signal[1]) == 0 or nz(last_signal[1]) ==-1)\nSell_final = SellCondition and (nz(last_signal[1]) == 0 or nz(last_signal[1]) == 1)\nlast_signal := Buy_final ? 1 : Sell_final ? -1 : last_signal[1]\n\nplotshape(Buy_final , style=shape.labelup  , location=location.belowbar, color=color.blue, title="Buy label" , text="BUY" , textcolor=color.white)\nplotshape(Sell_final, style=shape.labeldown, location=location.abovebar, color=color.red , title="Sell label", text="SELL", textcolor=color.white)\n\nstrategy.entry("Buy", strategy.long, when=Buy_final)\nstrategy.close("Buy", when=Sell_final)'

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
