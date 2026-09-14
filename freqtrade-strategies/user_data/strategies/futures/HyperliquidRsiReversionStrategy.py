# ============================================================
# SEMANTIC-PRESERVING FREQTRADE PORT
# Original repository: https://github.com/Crypto-Data-API/hyperliquid-backtester
# Original commit: a9dd95dafe0ce3cfae087449a51c683eda725bee
# Original files: strategies/examples/rsi_reversion.py, src/hlbt/indicators.py, src/hlbt/backtester.py
# Original market: Hyperliquid perpetual futures
# Migration target: Freqtrade Strategy Interface V3
# IMPORTANT: No strategy optimization is allowed in this port.
# ============================================================
import numpy as np
from pandas import DataFrame, Series
from freqtrade.strategy import IStrategy

def _wilder_rsi(s: Series, period: int) -> Series:
    v=s.to_numpy(dtype=float); out=np.full(v.shape,np.nan)
    if len(v)>period:
        d=np.diff(v); gain=np.where(d>0,d,0.0); loss=np.where(d<0,-d,0.0)
        ag,al=gain[:period].mean(),loss[:period].mean()
        def calc(g,l): return 100.0 if l==0 and g>0 else (50.0 if l==0 else 100.0-100.0/(1.0+g/l))
        out[period]=calc(ag,al)
        for i in range(period+1,len(v)):
            ag=(ag*(period-1)+gain[i-1])/period; al=(al*(period-1)+loss[i-1])/period; out[i]=calc(ag,al)
    return Series(out,index=s.index)

class HyperliquidRsiReversionStrategy(IStrategy):
    INTERFACE_VERSION=3; can_short=True; timeframe="15m"; startup_candle_count=60
    minimal_roi={"0":100.0}; stoploss=-0.06; use_exit_signal=True
    rsi_period=9; oversold=15.0; overbought=75.0; exit_level=50.0; time_stop_bars=144

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe["source_rsi"]=_wilder_rsi(dataframe.close,self.rsi_period); return dataframe
    def populate_entry_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe.source_rsi<=self.oversold,"enter_long"]=1
        dataframe.loc[dataframe.source_rsi>=self.overbought,"enter_short"]=1; return dataframe
    def populate_exit_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        dataframe.loc[dataframe.source_rsi>=self.exit_level,"exit_long"]=1
        dataframe.loc[dataframe.source_rsi<=self.exit_level,"exit_short"]=1; return dataframe
    def custom_exit(self,pair,trade,current_time,current_rate,current_profit,**kwargs):
        if current_profit>=0.10:return "take_profit"
        if (current_time-trade.open_date_utc).total_seconds()>=self.time_stop_bars*15*60:return "time_stop"
        return None

