"""Source-faithful deep-assisted port of 支撑阻力策略结合动态风险管理系统-Support-and-Resistance-Strategy-with-Dynamic-Risk-Management-System.md.

This module was built from THIS strategy's own source.  The semantic map below
records every top-level assignment, user function, enclosing control condition
and strategy.* order call found in the original program.  Non-vectorizable Pine
state is not silently invented: fidelity gaps are listed explicitly.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from deep_semantic_runtime import SemanticRuntime

class SMB010_c422f88c(PinePortBase, IStrategy):
    source_file = '支撑阻力策略结合动态风险管理系统-Support-and-Resistance-Strategy-with-Dynamic-Risk-Management-System.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_commission_percent = 0.0
    source_features = ['strategy.exit', 'strategy.entry']
    source_fidelity_notes = ['Uses strategy.exit; stop/limit/profit/loss/trailing arguments have Pine order semantics and may fill intrabar.']
    pine_assignments = [{'mode': '', 'name': 'capital', 'op': '=', 'expr': '2000 // Capital initial de 2000 euros', 'conditions': []}, {'mode': '', 'name': 'maxAmountPerTrade', 'op': '=', 'expr': '2000 // Montant maximum à utiliser par trade', 'conditions': []}, {'mode': '', 'name': 'leverage', 'op': '=', 'expr': '20 // Effet de levier de 1:20', 'conditions': []}, {'mode': '', 'name': 'spread', 'op': '=', 'expr': '0.5 // Spread moyen en pips', 'conditions': []}, {'mode': '', 'name': 'riskPerTrade', 'op': '=', 'expr': '0.2 // 20% du capital initial par transaction', 'conditions': []}, {'mode': '', 'name': 'atrLength', 'op': '=', 'expr': "14 // Longueur de l'ATR pour le trailing stop", 'conditions': []}, {'mode': '', 'name': 'pivotHigh', 'op': '=', 'expr': 'high[1] + low[1] + close[1] / 3', 'conditions': []}, {'mode': '', 'name': 'pivotLow', 'op': '=', 'expr': 'high[1] + low[1] + close[1] / 3', 'conditions': []}, {'mode': '', 'name': 'atrValue', 'op': '=', 'expr': 'ta.atr(atrLength)', 'conditions': []}, {'mode': '', 'name': 'riskAmount', 'op': '=', 'expr': 'capital * riskPerTrade', 'conditions': []}, {'mode': '', 'name': 'positionSize', 'op': '=', 'expr': 'math.min(maxAmountPerTrade * leverage / (atrValue * 2), riskAmount / (atrValue * 2)) // Taille de la position en lots limitée par le montant maximum par trade et le risque autorisé', 'conditions': []}, {'mode': '', 'name': 'stopLossPrice', 'op': '=', 'expr': 'close - (atrValue * 2 + spread / 10)', 'conditions': ['low <= pivotLow']}, {'mode': '', 'name': 'takeProfitPrice', 'op': '=', 'expr': 'close + atrValue * 3 - spread / 10', 'conditions': ['low <= pivotLow']}, {'mode': '', 'name': 'stopLossPrice', 'op': '=', 'expr': 'close + atrValue * 2 + spread / 10', 'conditions': ['high >= pivotHigh']}, {'mode': '', 'name': 'takeProfitPrice', 'op': '=', 'expr': 'close - (atrValue * 3 - spread / 10)', 'conditions': ['high >= pivotHigh']}]
    pine_user_functions = []
    pine_controls = [{'indent': 0, 'statement': 'if low <= pivotLow'}, {'indent': 0, 'statement': 'if high >= pivotHigh'}]
    pine_orders = [{'kind': 'entry', 'call': "strategy.entry('Buy', strategy.long, qty=positionSize)", 'conditions': ['low <= pivotLow'], 'statement': "strategy.entry('Buy', strategy.long, qty=positionSize)"}, {'kind': 'exit', 'call': "strategy.exit('Exit Buy', 'Buy', stop=stopLossPrice, limit=takeProfitPrice)", 'conditions': ['low <= pivotLow'], 'statement': "strategy.exit('Exit Buy', 'Buy', stop=stopLossPrice, limit=takeProfitPrice)"}, {'kind': 'entry', 'call': "strategy.entry('Sell', strategy.short, qty=positionSize)", 'conditions': ['high >= pivotHigh'], 'statement': "strategy.entry('Sell', strategy.short, qty=positionSize)"}, {'kind': 'exit', 'call': "strategy.exit('Exit Sell', 'Sell', stop=stopLossPrice, limit=takeProfitPrice)", 'conditions': ['high >= pivotHigh'], 'statement': "strategy.exit('Exit Sell', 'Sell', stop=stopLossPrice, limit=takeProfitPrice)"}]
    original_pine = '/*backtest\nstart: 2023-07-23 00:00:00\nend: 2024-07-28 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy(\'Mon Robot de Trading\', overlay=true)\n\n// Paramètres\ncapital = 2000  // Capital initial de 2000 euros\nmaxAmountPerTrade = 2000  // Montant maximum à utiliser par trade\nleverage = 20  // Effet de levier de 1:20\nspread = 0.5  // Spread moyen en pips\nriskPerTrade = 0.2  // 20% du capital initial par transaction\natrLength = 14  // Longueur de l\'ATR pour le trailing stop\n\n// Calcul des points de pivot\npivotHigh = high[1] + low[1] + close[1] / 3\npivotLow = high[1] + low[1] + close[1] / 3\n\n// Plot des points de pivot sur le graphique\nplot(pivotHigh, color=color.new(color.red, 0), linewidth=1, title=\'Resistance\')\nplot(pivotLow, color=color.new(color.green, 0), linewidth=1, title=\'Support\')\n\n// Calcul de l\'ATR pour la gestion du risque et du trailing stop\natrValue = ta.atr(atrLength)\n\n// Calcul de la taille de la position basée sur le pourcentage de risque du capital et le montant maximum par trade\nriskAmount = capital * riskPerTrade\npositionSize = math.min(maxAmountPerTrade * leverage / (atrValue * 2), riskAmount / (atrValue * 2))  // Taille de la position en lots limitée par le montant maximum par trade et le risque autorisé\n\n// Implémentation de la stratégie avec trailing stop et take-profit\nif low <= pivotLow\n    strategy.entry(\'Buy\', strategy.long, qty=positionSize)\n\n    // Définition de l\'exit pour les achats (longs)\n    stopLossPrice = close - (atrValue * 2 + spread / 10)\n    takeProfitPrice = close + atrValue * 3 - spread / 10\n    strategy.exit(\'Exit Buy\', \'Buy\', stop=stopLossPrice, limit=takeProfitPrice)\n\nif high >= pivotHigh\n    strategy.entry(\'Sell\', strategy.short, qty=positionSize)\n\n    // Définition de l\'exit pour les ventes (courts)\n    stopLossPrice = close + atrValue * 2 + spread / 10\n    takeProfitPrice = close - (atrValue * 3 - spread / 10)\n    strategy.exit(\'Exit Sell\', \'Sell\', stop=stopLossPrice, limit=takeProfitPrice)'

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
