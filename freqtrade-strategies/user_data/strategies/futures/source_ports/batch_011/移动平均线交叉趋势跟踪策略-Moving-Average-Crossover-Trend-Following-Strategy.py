"""batch_011 port of 移动平均线交叉趋势跟踪策略-Moving-Average-Crossover-Trend-Following-Strategy.md.

The original Pine source is preserved verbatim in PINE_SOURCE.  This file uses
the batch_011 source-preserving runtime and the same PinePortBase strategy
surface used by batch_001.  See source_fidelity_notes before parity claims.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch011_runtime import Batch011Runtime

PINE_SOURCE = '/*backtest\nstart: 2024-07-12 00:00:00\nend: 2025-02-22 08:00:00\nperiod: 1h\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"SOL_USDT"}]\n*/\n\n//@version=5\nstrategy("MA Crossover [ClémentCrypto]", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=20, initial_capital=10000,process_orders_on_close=true)\n\n// Groupe pour le choix entre preset et personnalisé\nusePreset = input.bool(title="Utiliser Preset", defval=true, group="Mode Selection")\n\n// Inputs pour la stratégie\ntimeframeChoice = input.string(title="Timeframe Preset", defval="1H", options=["1H", "4H", "1D", "1W", "2W"], group="Preset Settings")\ntradeDirection = input.string(title="Trading Direction", defval="Long Only", options=["Long Only", "Short Only", "Both Directions"], group="Strategy Settings")\n\n// Paramètres personnalisés MA\ncustomFastLength = input.int(title="Custom Fast MA Length", defval=23, minval=1, group="Custom MA Settings")\ncustomSlowLength = input.int(title="Custom Slow MA Length", defval=395, minval=1, group="Custom MA Settings")\ncustomMAType = input.string(title="Custom MA Type", defval="EMA", options=["SMA", "EMA"], group="Custom MA Settings")\n\n// Paramètres MA optimisés pour chaque timeframe\nvar int fastLength = 0\nvar int slowLength = 0\nvar string maType = ""\n\nif usePreset\n    if timeframeChoice == "1H"\n        fastLength := 23\n        slowLength := 395\n        maType := "EMA"\n    else if timeframeChoice == "4H"\n        fastLength := 41\n        slowLength := 263\n        maType := "SMA"\n    else if timeframeChoice == "1D"\n        fastLength := 8\n        slowLength := 44\n        maType := "SMA"\n    else if timeframeChoice == "1W"\n        fastLength := 32\n        slowLength := 38\n        maType := "SMA"\n    else if timeframeChoice == "2W"\n        fastLength := 17\n        slowLength := 20\n        maType := "SMA"\nelse\n    fastLength := customFastLength\n    slowLength := customSlowLength\n    maType := customMAType\n\n// Calcul des moyennes mobiles\nfastMA = maType == "SMA" ? ta.sma(close, fastLength) : ta.ema(close, fastLength)\nslowMA = maType == "SMA" ? ta.sma(close, slowLength) : ta.ema(close, slowLength)\n\n// Conditions de trading simplifiées\nlongEntier = ta.crossover(fastMA, slowMA)\nlongExit = ta.crossunder(fastMA, slowMA)\nshortEntier = ta.crossunder(fastMA, slowMA)\nshortExit = ta.crossover(fastMA, slowMA)\n\n// Définition des couleurs\nvar BULL_COLOR = color.new(#00ff9f, 20)\nvar BEAR_COLOR = color.new(#ff0062, 20)\nvar BULL_COLOR_LIGHT = color.new(#00ff9f, 90)\nvar BEAR_COLOR_LIGHT = color.new(#ff0062, 90)\n\n// Couleurs des lignes MA\nfastMAColor = fastMA > slowMA ? BULL_COLOR : BEAR_COLOR\nslowMAColor = color.new(#FF6D00, 60)\n\n// Gestion des positions\nif tradeDirection == "Long Only"\n    if (longEntier)\n        strategy.entry("Long", strategy.long)\n    if (longExit)\n        strategy.close("Long")\n        \nelse if tradeDirection == "Short Only"\n    if (shortEntier)\n        strategy.entry("Short", strategy.short)\n    if (shortExit)\n        strategy.close("Short")\n        \nelse if tradeDirection == "Both Directions"\n    if (longEntier)\n        strategy.entry("Long", strategy.long)\n    if (longExit)\n        strategy.close("Long")\n    if (shortEntier)\n        strategy.entry("Short", strategy.short)\n    if (shortExit)\n        strategy.close("Short")\n\n// Plots\nvar fastMAplot = plot(fastMA, "Fast MA", color=fastMAColor, linewidth=2)\nvar slowMAplot = plot(slowMA, "Slow MA", color=slowMAColor, linewidth=1)\nfill(fastMAplot, slowMAplot, color=fastMA > slowMA ? BULL_COLOR_LIGHT : BEAR_COLOR_LIGHT)\n\n\n\n// Barres colorées\nbarcolor(fastMA > slowMA ? color.new(BULL_COLOR, 90) : color.new(BEAR_COLOR, 90))'

class SMA67DF49616F05BE9(PinePortBase, IStrategy):
    source_id = "SM_a67df49616f05be9"
    source_file = '移动平均线交叉趋势跟踪策略-Moving-Average-Crossover-Trend-Following-Strategy.md'
    timeframe = '1h'
    can_short = True
    source_defaults = {'usePreset': True, 'timeframeChoice': '1H', 'tradeDirection': 'Long Only', 'customFastLength': 23, 'customSlowLength': 395, 'customMAType': 'EMA'}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 20
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 10000
    source_reproduce_stops = False
    source_risk_flags = ['var_state']
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_011 md and exposed through the same PinePortBase interface used by batch_001.', 'Generic runtime port: files using MTF, custom functions, loops/arrays, stateful broker variables, or complex resting-order semantics require per-strategy parity review before claiming TradingView/FMZ-equivalent backtests.']

    def pine_indicators(self, dataframe, params):
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch011Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
