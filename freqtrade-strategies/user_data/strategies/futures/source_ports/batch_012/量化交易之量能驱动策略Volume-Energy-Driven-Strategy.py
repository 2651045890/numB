"""batch_012 port of 量化交易之量能驱动策略Volume-Energy-Driven-Strategy.md.

This file preserves the original Pine source verbatim in PINE_SOURCE and uses
Batch012Runtime to replay the common Pine subset through PinePortBase/PineBroker.
See source_fidelity_notes before treating a backtest as parity-certified.
"""
from freqtrade.strategy import IStrategy
from pine_port_base import PinePortBase
from _batch012_runtime import Batch012Runtime

PINE_SOURCE = '/*backtest\nstart: 2022-12-28 00:00:00\nend: 2024-01-03 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT"}]\n*/\n\n// This source code is subject to the terms of the Mozilla Public License 2.0 at https://mozilla.org/MPL/2.0/\n// © Shuttle_Club\n//@version=5\n\nstrategy(\'Volume fight strategy\', default_qty_type=strategy.cash, default_qty_value=10000, currency=\'USD\', commission_value=0.04, calc_on_order_fills=false, calc_on_every_tick=false, initial_capital=10000)\n\ndirection = input.string(\'ANY\', \'Direction\', options=[\'LONG\', \'SHORT\', \'ANY\'], tooltip=\'Select the direction of trade.\\n\\nВыберите направление торговли.\')\nma = input.int(11, \'Search_range\', minval=1, tooltip=\'The range of estimation of the predominance of bullish or bearish volume (quantity bars). The smaller the TF, the higher the range value should be used to filter out false signals.\\n\\nДиапазон оценки преобладания бычьего или медвежьего объема (количество баров). Чем меньше ТФ, тем выше следует использовать значение диапазона, чтобы отфильтровать ложные сигналы.\')\ndelta = input.float(15, \'Smoothing_for_flat,%\', step=0.5, minval=0, tooltip=\'Smoothing to reduce false signals and highlight the flat zone. If you set the percentage to zero, the flat zones will not be highlighted, but there will be much more false signals, since the indicator becomes very sensitive when the smoothing percentage decreases.\\n\\nСглаживание для уменьшения ложных сигналов и выделения зоны флета. Если выставить процент равным нулю, то зоны флета выделяться не будут, но будет гораздо больше ложных сигналов, так как индикатор становится очень чувствительным при снижении процента сглаживания\')\nbgshow = input.bool(true, \'Show background zones\', tooltip=\'Show the color background of the current trading zone.\\n\\nПоказывать цветовой фон текущей торговой зоны.\')\nall_signal_show = input.bool(false, \'Show each setup in zone\', tooltip=\'Show every signals into trading zone.\\n\\nПоказывать каждый сигнал внутри торговой зоны.\')\n\n/////   CALCULATION\nbull_vol = open < close ? volume : volume * (high - open) / (high - low)  //determine the share of bullish volume\nbear_vol = open > close ? volume : volume * (open - low) / (high - low)  //determine the share of bearish volume\navg_bull_vol = ta.vwma(bull_vol, ma)  //determine vwma\navg_bear_vol = ta.vwma(bear_vol, ma)\ndiff_vol = ta.sma(avg_bull_vol / volume - 1 - (avg_bear_vol / volume - 1), ma)  //normalize and smooth the values\nvol_flat = math.abs(avg_bull_vol + avg_bear_vol) / 2  //determine average value for calculation flat-filter\n\n/////   SIGNALS\nup = int(na), up := nz(up[1])\ndn = int(na), dn := nz(dn[1])\nbull = avg_bull_vol > avg_bear_vol and vol_flat / avg_bull_vol < 1 - delta / 100  //determine up zones\nbear = avg_bull_vol < avg_bear_vol and vol_flat / avg_bear_vol < 1 - delta / 100  //determine dn zones\n\nif bull\n    up += 1, dn := 0\n    dn\nif bear\n    dn += 1, up := 0\n    up\nif not bull and not bear and all_signal_show\n    up := 0, dn := 0\n    dn\n\n/////   PLOTTING\nplotshape(bull and up == 1, \'UP\', location=location.bottom, style=shape.triangleup, color=color.new(color.green, 0), size=size.tiny)\nplotshape(bear and dn == 1, \'DN\', location=location.top, style=shape.triangledown, color=color.new(color.red, 0), size=size.tiny)\nbgcolor(title=\'Trading zones\', color=bgshow and avg_bull_vol > avg_bear_vol and vol_flat / avg_bull_vol < 1 - delta / 100 ? color.new(color.green, 85) : bgshow and avg_bull_vol < avg_bear_vol and vol_flat / avg_bear_vol < 1 - delta / 100 ? color.new(color.red, 85) : na)\nplot(diff_vol, \'Volume difference\', style=plot.style_area, color=avg_bull_vol > avg_bear_vol and vol_flat / avg_bull_vol < 1 - delta / 100 ? color.new(color.green, 0) : avg_bull_vol < avg_bear_vol and vol_flat / avg_bear_vol < 1 - delta / 100 ? color.new(color.red, 0) : color.new(color.gray, 50))\n\nstrategy.close(\'Short\', comment=\'close\', when=bull and up == 1)\nstrategy.close(\'Long\', comment=\'close\', when=bear and dn == 1)\nstrategy.entry(\'Long\', strategy.long, when=direction != \'SHORT\' and bull and up == 1)\nstrategy.entry(\'Short\', strategy.short, when=direction != \'LONG\' and bear and dn == 1)\n\nif bull and up==1\n    alert(\'Bullish movement! LONG trading zone\', alert.freq_once_per_bar_close)\nif bear and dn==1\n    alert(\'Bearish movement! SHORT trading zone\', alert.freq_once_per_bar_close)\n    \n'

class SMVolumeEnergyDrivenStrategy2c59ec(PinePortBase, IStrategy):
    source_id = "SM_2c59eca3307404f9"
    source_file = '量化交易之量能驱动策略Volume-Energy-Driven-Strategy.md'
    timeframe = '1d'
    can_short = True
    source_defaults = {'direction': 'ANY', 'ma': 11, 'delta': 15, 'bgshow': True, 'all_signal_show': False}
    source_qty_type = 'cash'
    source_qty_value = 10000
    source_commission_percent = 0.04
    source_pyramiding = 0
    source_initial_capital = 10000
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
