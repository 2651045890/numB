"""batch_011 port of 自适应均值通道突破交易策略基于EMA和ATR的动态波动区间交易系统-Adaptive-Mean-Channel-Breakout-Trading-Strategy-Dynamic-Volatility-Range-Trading-System-Based-on-EMA-and-ATR.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-02-11 00:00:00\nend: 2025-02-08 08:00:00\nperiod: 1d\nbasePeriod: 1d\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © rolguergf34585\n\n//@version=5\nstrategy("Grupo ROG - Cash Bands", overlay=true)\n\nPeriodoATR = input.int(defval=14,title="Período ATR")\nPeriodoMedia = input.int(defval=10,title="Período Média Móvel")\nPeriodoFiltro = input.int(defval=30,title="Período Média Filtro")\nMult = input.float(defval=0.5,title="Multiplicador",step=0.1)\nCasas_Decimais = input.int(defval=5,title="Casas Decimais")\n\nema = ta.ema(close,PeriodoMedia)\nfiltro = ta.ema(close,PeriodoFiltro)\natr = ta.atr(PeriodoATR)\n\nupper = math.round(ema+atr*Mult,Casas_Decimais) \nbasis = ema\nlower = math.round(ema-atr*Mult,Casas_Decimais) \n\ntendencia = lower>filtro?1:upper<filtro?-1:0\n\nplot(upper,color=color.red)\nplot(lower,color=color.green)\n//plot(filtro,color=color.white)\n\nbarcolor(tendencia==1?color.green:tendencia==-1?color.red:color.white)\n\nlongCondition = true//tendencia==1 //and close < lower[1]\nshortCondition = true//tendencia==-1 //and close > upper[1]\n\n// if (strategy.position_size>0)\n//     strategy.exit("Long", limit=upper[0])\n// if (strategy.position_size<0)\n//     strategy.exit("Short", limit=lower[0])\n\nif (longCondition)\n    strategy.entry("Long", strategy.long, limit=lower[0])\nif (shortCondition)\n    strategy.entry("Short", strategy.short, limit=upper[0])\n\n\n\n'

class SMA286072767EDE914(PinePortBase, IStrategy):
    source_id = "SM_a286072767ede914"
    source_file = '自适应均值通道突破交易策略基于EMA和ATR的动态波动区间交易系统-Adaptive-Mean-Channel-Breakout-Trading-Strategy-Dynamic-Volatility-Range-Trading-System-Based-on-EMA-and-ATR.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'PeriodoATR': 14, 'PeriodoMedia': 10, 'PeriodoFiltro': 30, 'Mult': 0.5, 'Casas_Decimais': 5}
    source_qty_type = 'fixed'
    source_qty_value = 1
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000
    source_reproduce_stops = False
    source_risk_flags = ['broker_state', 'entry_price_order', 'exit_order']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
