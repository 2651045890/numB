"""batch_012 port of 高精度RSI和布林带突破策略与优化风险比-High-Precision-RSI-and-Bollinger-Bands-Breakout-Strategy-with-Optimized-Risk-Reward-Ratio.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-06-01 00:00:00\nend: 2024-06-30 23:59:59\nperiod: 1h\nbasePeriod: 15m\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Estratégia de Alta Acertividade com R/R 1:5", overlay=true)\n\n// Parâmetros do RSI e Bollinger Bands\nrsi_length = input.int(14, title="Período do RSI")\nrsi_overbought = input.int(70, title="Nível de Sobrecompra do RSI")\nrsi_oversold = input.int(30, title="Nível de Sobrevenda do RSI")\nbb_length = input.int(20, title="Período das Bandas de Bollinger")\nbb_stddev = input.float(2.0, title="Desvio Padrão das Bandas de Bollinger")\ntp_ratio = input.float(5.0, title="Take Profit Ratio (R/R)")\nsl_ratio = input.float(1.0, title="Stop Loss Ratio (R/R)")\n\n// Cálculo do RSI\nrsi = ta.rsi(close, rsi_length)\n\n// Cálculo das Bandas de Bollinger\nbasis = ta.sma(close, bb_length)\ndev = bb_stddev * ta.stdev(close, bb_length)\nupper_bb = basis + dev\nlower_bb = basis - dev\n\n// Cálculo do Volume Médio\navg_volume = ta.sma(volume, 20)\n\n// Condições para Compra e Venda\nbuy_condition = (rsi < rsi_oversold) and (close < lower_bb) and (volume > avg_volume)\nsell_condition = (rsi > rsi_overbought) and (close > upper_bb) and (volume > avg_volume)\n\n// Definição do Take Profit e Stop Loss baseados no R/R\npip_size = syminfo.mintick\natr = ta.atr(14)\ntake_profit = atr * tp_ratio\nstop_loss = atr * sl_ratio\n\n// Execução da Estratégia de Compra\nif (buy_condition)\n    strategy.entry("Compra", strategy.long)\n    strategy.exit("Take Profit/Stop Loss", "Compra", limit=close + take_profit, stop=close - stop_loss)\n\n// Execução da Estratégia de Venda\nif (sell_condition)\n    strategy.entry("Venda", strategy.short)\n    strategy.exit("Take Profit/Stop Loss", "Venda", limit=close - take_profit, stop=close + stop_loss)\n\n// Plotagem das Bandas de Bollinger, RSI e Volume\nplot(upper_bb, color=color.red, title="Banda Superior")\nplot(lower_bb, color=color.green, title="Banda Inferior")\nplot(rsi, color=color.purple, title="RSI")\nhline(rsi_overbought, "RSI Sobrecompra", color=color.red, linestyle=hline.style_dashed)\nhline(rsi_oversold, "RSI Sobrevenda", color=color.green, linestyle=hline.style_dashed)\nplot(volume, color=color.blue, title="Volume")\nplot(avg_volume, color=color.orange, title="Volume Médio")\n\n// Estilo de fundo baseado na posição\nbgcolor(buy_condition ? color.green : sell_condition ? color.red : na, transp=80)\n\n'

class SMRSIHighPrecisionRSIandBollingerBandsBreakoutStrategywit08c971(PinePortBase, IStrategy):
    source_id = "SM_08c97170ab7e1ec9"
    source_file = '高精度RSI和布林带突破策略与优化风险比-High-Precision-RSI-and-Bollinger-Bands-Breakout-Strategy-with-Optimized-Risk-Reward-Ratio.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'rsi_length': 14, 'rsi_overbought': 70, 'rsi_oversold': 30, 'bb_length': 20, 'bb_stddev': 2.0, 'tp_ratio': 5.0, 'sl_ratio': 1.0}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = True
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
