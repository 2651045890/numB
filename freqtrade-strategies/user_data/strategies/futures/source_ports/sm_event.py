"""Bridge reviewed Python source models to the offline order-event broker."""
from dataclasses import asdict, replace
from freqtrade.enums import RunMode
from sm_broker import Broker, BrokerSettings


class EventStrategyBase:
    INTERFACE_VERSION=3
    execution_backend='pine_compat'
    startup_candle_count=0
    minimal_roi={}
    stoploss=-1.0
    process_only_new_candles=True
    use_exit_signal=True
    order_types={'entry':'market','exit':'market','stoploss':'market','stoploss_on_exchange':False}
    order_time_in_force={'entry':'GTC','exit':'GTC'}
    source_defaults={}
    declared_settings={}
    setting_notes={}

    def __init__(self,config):
        if config.get('runmode') in (RunMode.LIVE,RunMode.DRY_RUN):
            raise ValueError('Source compatibility strategies support offline backtests only')
        super().__init__(config)

    def source_parameters(self):
        values=dict(self.source_defaults)
        overrides=self.config.get('source_parameters',{})
        if set(overrides)-set(values):raise ValueError('Unknown source parameters: '+str(set(overrides)-set(values)))
        values.update(overrides)
        return values

    def source_broker_settings(self):
        # These defaults describe a chosen Pine v4/v5 chart model, not an FMZ
        # account snapshot or the numB/OKX runtime configuration.
        return BrokerSettings(**self.declared_settings)

    def prepare_source(self,dataframe,parameters):
        return self.populate_indicators(dataframe,{})

    def source_on_bar(self,bar,broker,state,parameters):
        raise NotImplementedError

    def backtest_source(self,dataframe,broker_overrides=None):
        parameters=self.source_parameters()
        df=self.prepare_source(dataframe.copy(),parameters)
        settings=self.source_broker_settings()
        if broker_overrides:settings=replace(settings,**broker_overrides)
        broker=Broker(settings);state={};positions=[];equities=[];commands=[]
        for i,bar in enumerate(df.itertuples(index=False)):
            broker.advance(i,bar)
            positions.append(broker.position_size);equities.append(broker.equity)
            before=len(broker.events)
            self.source_on_bar(bar,broker,state,parameters)
            commands.append(len(broker.events)-before)
        df['source_position']=positions;df['source_equity']=equities;df['source_command_events']=commands
        return df,broker

    def populate_indicators(self,dataframe,metadata):
        return self.prepare_source(dataframe,self.source_parameters())

    def populate_entry_trend(self,dataframe,metadata):
        raise NotImplementedError('Use numB orchestrator: execution_backend=pine_compat; Freqtrade signal engine cannot encode these orders')

    def populate_exit_trend(self,dataframe,metadata):
        raise NotImplementedError('Use numB orchestrator: execution_backend=pine_compat')
