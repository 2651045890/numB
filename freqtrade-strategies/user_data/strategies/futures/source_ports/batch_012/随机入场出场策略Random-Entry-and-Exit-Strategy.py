"""batch_012 port of 随机入场出场策略Random-Entry-and-Exit-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-10-04 00:00:00\nend: 2023-10-10 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\nargs: [["v_input_1",2]]\n*/\n\n//@version=4\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © gregoirejohnb\n//\n// "tHe MaRkEtS aRe RaNdOm", say moron academics.\n//\n// The purpose of this study is to show that most markets are NOT random! Most markets show a clear bias where we can make such easy money, that a random number generator can do it.\n// \n// === HOW THE INDICATOR WORKS ===\n// \n// -The study will randomly enter the market\n// -The study will randomly exit the market if in a trade\n// -You can choose a Long Only, Short Only, or Bidirectional strategy\n//\n// === DEFAULT VALUES AND THEIR LOGIC ===\n// \n// Percent Chance to Enter Per Bar: 10%\n// Percent Chance to Exit Per Bar: 1%\n// Direction: Long Only\n// Commission: 0\n//\n// Each bar has a 10% chance to enter the market. Each bar has a 1% to exit the market [if in a trade]. It will only enter long.\n//\n// I included zero commission for simplication. It\'s a good exercise to include a commission/slippage to see just how much trading fees take from you.\n// \n// === TIPS ===\n//\n// -Increasing "Percent Chance to Exit" will shorten the time in a trade. You can see the "Avg # Bars In Trade" go down as you increase. If "Percent Chance to Exit" is too high, the study won\'t be in the market long enough to catch any movement, possibly exiting on the same bar most of the time.\n// -If you\'re getting the red screen, that means the strategy lost so much money it went broke. Try reducing the percent equity on the Properties tab.\n// -Switch the start year to avoid black swan events like the covid drop in 2020.\n// -\n// === FINDINGS ===\n//\n// Most markets lose money with a "Random" direction strategy.\n// Most markets lose ALL money with a "Short Only" strategy.\n// Most markets make money with a "Long Only" strategy.\n// \n// Try this strategy on: Bitcoin (BTCUSD) and the NASDAQ (QQQ).\n//\n// There are two popular memes right now: "Bitcoin to the moon" and "Stocks only go up". Both are seemingly true. Bitcoin was the best performing asset of the 2010\'s, gaining several billion percent in gains. The stock market is on a 100 year long uptrend. Why? BECAUSE FIAT CURRENCIES ALWAYS GO DOWN! This is inflation. If we measure the market in terms of others assets instead of fiat, the Long Only strategy doesn\'t work anymore.\n// Try this strategy on: Bitcoin/GLD (BTCUSD/GLD), the Eurodollar (EURUSD), and the S&P 500 measured in gold (SPY/GLD).\n// \n// Bitcoin measured in gold (BTCUSD/GLD) still works with a Long Only strategy because Bitcoin increased in value over both USD and gold.\n// The Eurodollar (EURUSD) generally loses money no matter what, especially if you add any commission. This makes sense as they are both fiat currencies with similar inflation schedules.\n// Gold and the S&P 500 have gained roughly the same amount since ~2000. Some years will show better results for a long strategy, while others will favor a short strategy. Now look at just SPY or GLD (which are both measured in USD by default!) and you\'ll see the same trend again: a Long Only strategy crushes even when entering and exiting randomly.\n//\n// === "JUST TELL ME WHAT TO DO, YOU NERD!" ===\n//\n// Bulls always win and Bears always lose because fiat currencies go to zero.\n//\nstrategy(title="Random Entries Work", shorttitle="REW", overlay=true, pyramiding=0, default_qty_type=strategy.percent_of_equity, default_qty_value=100, currency=currency.USD,commission_type=strategy.commission.percent,commission_value=0)\n\n// === GENERAL INPUTS ===\nstrategy = input(defval="Long Only",title="Direction",options=["Long Only", "Short Only", "Random"])\nenter_frequency = input(defval=10,minval=1,maxval=100,title="Percent Chance to Enter")\nexit_frequency = input(defval=3, minval=0,maxval=100,title="Percent Chance to Exit",tooltip="This should be much lower than Percent Chance to Enter. Higher values decrease time in market. Lower values increase time in market.")\nstart_year = input(defval=2020, title="Start Year")\n\n\n// === LOGIC ===\nr = random(0,100)\nenter = enter_frequency > r[0]\nexit = exit_frequency > r[0]\ndirection = random(0,100) >= 50\n\n// === STRATEGY - LONG POSITION EXECUTION ===\nenterLong() =>\n    strategy.opentrades == 0 and enter and (strategy == "Long Only" or (strategy == "Random") and direction) and \n       time > timestamp(start_year, 01, 01, 01, 01)\nexitLong() =>\n    exit\nstrategy.entry(id="Long", long=strategy.long, when=enterLong())\nstrategy.close(id="Long", when=exitLong())\n// === STRATEGY - SHORT POSITION EXECUTION ===\nenterShort() =>\n    strategy.opentrades == 0 and enter and (strategy == "Short Only" or (strategy == "Random" and not direction)) and \n       time > timestamp(start_year, 01, 01, 01, 01)\nexitShort() =>\n    exit\nstrategy.entry(id="Short", long=strategy.short, when=enterShort())\nstrategy.close(id="Short", when=exitShort())\n'

class SMRandomEntryandExitStrategy9a820c(PinePortBase, IStrategy):
    source_id = "SM_9a820c84cbda0634"
    source_file = '随机入场出场策略Random-Entry-and-Exit-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'strategy': 'Long Only', 'enter_frequency': 10, 'exit_frequency': 3, 'start_year': 2020}
    source_qty_type = 'percent_of_equity'
    source_qty_value = 100
    source_commission_percent = 0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.', 'The source reads live strategy position state; batch_001-style broker-state parity must be checked manually for this file.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
