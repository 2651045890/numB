"""Port of batch_002/Support-Resistance-breakout.md
Extracted source: strategy_migration/sources/SM_0ea0b9b48545330f.pine


PARTIAL: source calc_on_order_fills=true is not implemented by the shared close-bar engine. Recursive levels and trend use previous-bar values; initial historical na is preserved. Close calls precede entries."""
import numpy as np
import pandas as pd
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase


class SMSupportResistanceBreakout_0ea0b9(PinePortBase, IStrategy):
    source_id = "SM_0ea0b9b48545330f"
    source_file = 'Support-Resistance-breakout.md'
    timeframe = '4h'
    source_defaults = {'length': 21}
    source_initial_capital = 1_000_000.0
    source_fidelity_notes = ['PARTIAL: source calc_on_order_fills=true is not implemented by the shared close-bar engine. Recursive levels and trend use previous-bar values; initial historical na is preserved. Close calls precede entries.', 'Uses the existing offline Pine engine; original-platform trade comparison has not been performed.']
    source_implementation_status = 'partial_calc_on_order_fills'

    def pine_indicators(self, dataframe, params):
        h, l = dataframe.high, dataframe.low
        valid = pd.Series(np.arange(len(dataframe)) > 5, index=dataframe.index)
        hit_h = valid & (h.shift(5)<h.shift(4)) & (h.shift(4)<h.shift(3)) & (h.shift(3)>h.shift(2)) & (h.shift(2)>h.shift(1))
        hit_l = valid & (l.shift(5)>l.shift(4)) & (l.shift(4)>l.shift(3)) & (l.shift(3)<l.shift(2)) & (l.shift(2)<l.shift(1))
        hval, lval = h.shift(3).where(hit_h, 0), l.shift(3).where(hit_l, 0)
        ln, hn = ta.pine_sum(hit_l.astype(float), params['length']), ta.pine_sum(hit_h.astype(float), params['length'])
        lsum, hsum = ta.pine_sum(lval, params['length']), ta.pine_sum(hval, params['length'])
        r = (hsum / hn - lsum / ln).abs().where((ln > 0) & (hn > 0), 0)
        lvalc = lval.where((lval != 0) & (r > 0)).ffill()
        lvalr = (lval + r).where((lval != 0) & (r > 0)).ffill()
        hvalc = hval.where((hval != 0) & (r > 0)).ffill()
        hvalr = (hval - r).where((hval != 0) & (r > 0)).ffill()
        up = (dataframe.close > lvalr) & (dataframe.close > hvalr)
        down = (dataframe.close < lvalr) & (dataframe.close < hvalr)
        trend = pd.Series(np.where(up, 1, np.where(down, -1, np.nan)), index=dataframe.index).ffill()
        long_entry = (trend == 1) & (dataframe.close > hvalc)
        short_entry = (trend == -1) & (dataframe.close < lvalc)
        for key, value in dict(h=hit_h.astype(int), l=hit_l.astype(int), ln=ln, hn=hn, hval=hval, lval=lval, lsum=lsum, hsum=hsum, r=r, lvalc=lvalc, lvalr=lvalr, hvalc=hvalc, hvalr=hvalr, trend=trend).items():
            dataframe[key] = value
        dataframe['long_entry'], dataframe['short_entry'] = long_entry, short_entry
        dataframe['long'] = pd.Series(np.where(long_entry, 1, np.where(trend == -1, -1, np.nan)), index=dataframe.index).ffill()
        dataframe['short'] = pd.Series(np.where(short_entry, 1, np.where(trend == 1, -1, np.nan)), index=dataframe.index).ffill()
        return dataframe

    def pine_script(self, broker, i, ctx):
        broker.close('Long', when=ctx['trend'][i] == -1)
        broker.close('Short', when=ctx['trend'][i] == 1)
        broker.entry('Long', 'long', when=ctx['long_entry'][i])
        broker.entry('Short', 'short', when=ctx['short_entry'][i])
