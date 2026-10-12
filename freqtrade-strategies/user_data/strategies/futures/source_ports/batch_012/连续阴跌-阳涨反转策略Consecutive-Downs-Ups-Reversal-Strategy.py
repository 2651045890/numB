"""batch_012 port of 连续阴跌-阳涨反转策略Consecutive-Downs-Ups-Reversal-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2023-03-02 00:00:00\nend: 2024-03-07 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n//@version=5\nstrategy("Bottom Out Strategy", overlay=true)\nconsecutiveBarsUp = input(2)\nconsecutiveBarsDown = input(3)\nprice = close\nups = 0.0\nups := price > price[1] ? nz(ups[1]) + 1 : 0\ndns = 0.0\ndns := price < price[1] ? nz(dns[1]) + 1 : 0\nvar entry_bar_index = 1000000\nvar active = false\nvar stop_loss = 0.0\n\n// === INPUT BACKTEST RANGE ===\ni_from = input(defval = timestamp("01 Jan 2023 00:00 +0000"), title = "From")\ni_thru = input(defval = timestamp("01 Mar 2024 00:00 +0000"), title = "Thru")\n// === FUNCTION EXAMPLE ===\ndate() => true\n\nentry_condition() => \n\tdate() and dns[2] >= consecutiveBarsDown and ups >= consecutiveBarsUp and not active\n\nexit_condition() =>\n\tdate() and active and (close < nz(stop_loss) or close < high - 2 * ta.atr(7))\n\nif (entry_condition())\n\tstrategy.entry("ConsDnLong", strategy.long, comment="CDLEntry")\n\tentry_bar_index := bar_index\n\tactive := true\n\tstop_loss := math.min(close, close[1], close[2])\n\t// log.info("Entry at bar {0}, close={1}, stop_loss={2} ", entry_bar_index, close, stop_loss)\nif (exit_condition())\n\tstrategy.close("ConsDnLong", comment = "CDLClose")\n\t// log.info("Close at bar {0}", bar_index)\n\tentry_bar_index := 1000000\n\tactive := false\n// if (dns >= consecutiveBarsDown)\n// \tstrategy.entry("ConsDnSE", strategy.short, comment="ConsDnSE")\n//plot(strategy.equity, title="equity", color=color.red, linewidth=2, style=plot.style_areabr)\nplot(high - 2* ta.atr(7))\n'

class SMConsecutiveDownsUpsReversalStrategyccc15c(PinePortBase, IStrategy):
    source_id = "SM_ccc15c5ae025b817"
    source_file = '连续阴跌-阳涨反转策略Consecutive-Downs-Ups-Reversal-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'consecutiveBarsUp': 2, 'consecutiveBarsDown': 3, 'i_from': 'timestamp("01 Jan 2023 00:00 +0000")', 'i_thru': 'timestamp("01 Mar 2024 00:00 +0000")'}
    source_qty_type = 'fixed'
    source_qty_value = 1.0
    source_commission_percent = 0.0
    source_pyramiding = 0
    source_initial_capital = 1000000.0
    source_reproduce_stops = False
    source_fidelity_notes = ['Generated from the exact Pine source embedded in the corresponding batch_012 md and exposed through the same PinePortBase interface used by batch_001.', 'Custom Pine function(s) are present; the original source is embedded verbatim and this generic pass flags them for per-strategy semantic verification.']

    def pine_indicators(self, dataframe, params):
        # Runtime evaluates the source against the complete OHLCV frame.
        return dataframe

    def pine_context(self, dataframe, params):
        runtime = Batch012Runtime(PINE_SOURCE, dataframe, params, self.source_file)
        return runtime.context()

    def pine_script(self, broker, i, ctx):
        ctx["runtime"].step(broker, i)
