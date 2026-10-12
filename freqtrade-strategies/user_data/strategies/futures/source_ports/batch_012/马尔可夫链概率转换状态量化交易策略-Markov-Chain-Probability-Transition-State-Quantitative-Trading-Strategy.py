"""batch_012 port of 马尔可夫链概率转换状态量化交易策略-Markov-Chain-Probability-Transition-State-Quantitative-Trading-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '//@version=5\nstrategy("Markov Chain Strategy", overlay=true)\n\n// Input parameters for transition probabilities\nprob_bull_to_bull = input.float(0.7, title="Bull to Bull Transition Probability")\nprob_bull_to_bear = input.float(0.2, title="Bull to Bear Transition Probability")\nprob_bull_to_stagnant = input.float(0.1, title="Bull to Stagnant Transition Probability")\n\nprob_bear_to_bull = input.float(0.3, title="Bear to Bull Transition Probability")\nprob_bear_to_bear = input.float(0.5, title="Bear to Bear Transition Probability")\nprob_bear_to_stagnant = input.float(0.2, title="Bear to Stagnant Transition Probability")\n\nprob_stagnant_to_bull = input.float(0.4, title="Stagnant to Bull Transition Probability")\nprob_stagnant_to_bear = input.float(0.3, title="Stagnant to Bear Transition Probability")\nprob_stagnant_to_stagnant = input.float(0.3, title="Stagnant to Stagnant Transition Probability")\n\n// Define price states\nvar float prev_close = na\nvar int state = na\n\n// Calculate the current state\nif (not na(prev_close)) \n    if (close > prev_close) \n        state := 2 // Bull\n    else if (close < prev_close) \n        state := 1 // Bear\n    else \n        state := 3 // Stagnant\n\nprev_close := close\n\n// Transition logic (simplified)\nvar float transition_counter = 0\ntransition_counter := (transition_counter + 1) % 10\n\nif (state == 2)  // Bull\n    if (transition_counter < prob_bull_to_bull * 10)\n        state := 2\n    else if (transition_counter < (prob_bull_to_bull + prob_bull_to_bear) * 10)\n        state := 1\n    else\n        state := 3\nelse if (state == 1)  // Bear\n    if (transition_counter < prob_bear_to_bull * 10)\n        state := 2\n    else if (transition_counter < (prob_bear_to_bull + prob_bear_to_bear) * 10)\n        state := 1\n    else\n        state := 3\nelse if (state == 3)  // Stagnant\n    if (transition_counter < prob_stagnant_to_bull * 10)\n        state := 2\n    else if (transition_counter < (prob_stagnant_to_bull + prob_stagnant_to_bear) * 10)\n        state := 1\n    else\n        state := 3\n\n// Strategy logic\nif (state == 2)\n    strategy.entry("Buy", strategy.long)\nelse if (state == 1)\n    strategy.entry("Sell", strategy.short)\nelse \n    strategy.close("Buy")\n    strategy.close("Sell")\n\n'

class SMMarkovChainProbabilityTransitionStateQuantitativeTradind3daca(PinePortBase, IStrategy):
    source_id = "SM_d3dacaf92641087c"
    source_file = '马尔可夫链概率转换状态量化交易策略-Markov-Chain-Probability-Transition-State-Quantitative-Trading-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'prob_bull_to_bull': 0.7, 'prob_bull_to_bear': 0.2, 'prob_bull_to_stagnant': 0.1, 'prob_bear_to_bull': 0.3, 'prob_bear_to_bear': 0.5, 'prob_bear_to_stagnant': 0.2, 'prob_stagnant_to_bull': 0.4, 'prob_stagnant_to_bear': 0.3, 'prob_stagnant_to_stagnant': 0.3}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
