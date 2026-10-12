"""Deep Pine v5 port: Bollinger/EMA-band trend regime with asymmetric entries/exits."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

class SMB010_002_BollingerTrendShock(PinePortBase, IStrategy):
    timeframe="1h"; can_short=True
    source_file="布林带趋势震荡交易策略Bollinger-Trend-Shock-Trading-Strategy.md"
    source_defaults={"bollL":20,"bollmult":2.3,"smaL":200}
    source_qty_type="fixed"; source_qty_value=1.0; source_initial_capital=10000.0
    source_pyramiding=0; source_commission_percent=0.0; source_reproduce_stops=False
    source_fidelity_notes=["The source really uses crossover(close, upper) for SHORT entry; this unusual direction is preserved.",
                           "The 230-period SMA used in short exit is hard-coded, not smaL."]
    def pine_indicators(self, dataframe, params):
        c,h=dataframe['close'],dataframe['high']
        basis=ta.pine_ema(c,int(params['bollL']))
        dev=float(params['bollmult'])*ta.pine_stdev(c,int(params['bollL']))
        upper,lower=basis+dev,basis-dev
        trend=ta.pine_sma(c,int(params['smaL']))
        sma230=ta.pine_sma(c,230)
        dataframe['pine_longT']=(upper>trend)&(basis>trend)&(lower>=trend)
        dataframe['pine_shortT']=(upper<trend)&(basis<trend)&(lower<=trend)
        dataframe['pine_longE']=ta.pine_crossover(c,lower)
        dataframe['pine_shortE']=ta.pine_crossover(c,upper)
        dataframe['pine_long_exit']=ta.pine_crossover(h,upper)
        dataframe['pine_short_exit']=ta.pine_crossunder(c,basis)|ta.pine_crossover(c,sma230)
        return dataframe
    def pine_context(self,d,p):
        return {k:d['pine_'+k].to_numpy(bool) for k in ['longT','shortT','longE','shortE','long_exit','short_exit']}
    def pine_script(self,broker,i,ctx):
        if ctx['longT'][i] and ctx['longE'][i]: broker.entry('多','long')
        if ctx['long_exit'][i]: broker.close('多')
        if ctx['shortE'][i] and ctx['shortT'][i]: broker.entry('空','short')
        if ctx['short_exit'][i]: broker.close('空')
