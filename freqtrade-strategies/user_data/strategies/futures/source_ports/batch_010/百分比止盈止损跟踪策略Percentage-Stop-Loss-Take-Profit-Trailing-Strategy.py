"""Deep Pine v3 port of the SMA crossover long strategy with live avg-price SL/TP."""
from freqtrade.strategy import IStrategy
import pine_ta as ta
from pine_port_base import PinePortBase

class SMB010_003_PercentageSLTP(PinePortBase, IStrategy):
    timeframe="1h"; can_short=False
    source_file="百分比止盈止损跟踪策略Percentage-Stop-Loss-Take-Profit-Trailing-Strategy.md"
    source_defaults={"sma_per":200,"sl_inp":0.02,"tp_inp":0.01}
    source_qty_type="fixed"; source_qty_value=1.0; source_initial_capital=1_000_000.0
    source_pyramiding=0; source_commission_percent=0.0; source_reproduce_stops=True
    source_fidelity_notes=["Despite the filename, there is no trailing stop; stop/target are fixed percentages of strategy.position_avg_price."]
    def pine_indicators(self,d,p):
        sma=ta.pine_sma(d['close'],int(p['sma_per']))
        d['pine_sma']=sma; d['pine_entry']=ta.pine_crossover(d['close'],sma)
        return d
    def pine_context(self,d,p):
        return {'entry':d['pine_entry'].to_numpy(bool),'sl':float(p['sl_inp']),'tp':float(p['tp_inp'])}
    def pine_script(self,broker,i,ctx):
        if ctx['entry'][i]: broker.entry('Simple SMA Entry','long')
        if broker.position_size>0:
            avg=broker.position_avg_price
            broker.exit('Stop Loss/TP','Simple SMA Entry',stop=avg*(1-ctx['sl']),limit=avg*(1+ctx['tp']))
