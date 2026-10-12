"""Deep source-preserving Python adapter for 标定值或均线交叉策略.md."""
SOURCE_FILE='标定值或均线交叉策略.md'
SOURCE_LANGUAGE='pascal'
SOURCE_FEATURES=[]
SOURCE_FIDELITY_NOTES=['Source is Pascal/麦语言-style strategy code; Python version retains the state/condition/order map, but platform-specific built-ins require adapter bindings.']
ORIGINAL_SOURCE='(*backtest\nstart: 2019-01-05 00:00:00\nend: 2020-02-29 00:00:00\nperiod: 1d\nexchanges: [{"eid":"Huobi","currency":"BTC_USDT"}]\n*)\n//\nMA10:=MA(C,10);\nMA30:=MA(C,30);\n\n买入开仓价:=VALUEWHEN(BARSBK=1,O);\n卖出开仓价:=VALUEWHEN(BARSSK=1,O);\n//开仓条件\n\nBUYCONDITION:=REF(C,1) < MMD OR CROSSUP(MA10,MA30);\nSELLCONDITION:=REF(C,1) > HGH OR CROSSDOWN(MA10,MA30);\n\nBKVOL=0 AND BUYCONDITION,BK;\nSKVOL=0 AND SELLCONDITION,SK;\n\n//离场条件\nBKVOL>0 AND SELLCONDITION,SP;\nSKVOL>0 AND BUYCONDITION,BP;\n// 启动止损\nSKVOL>0 AND HIGH>=卖出开仓价*(1+STOPLOSS*0.01),BP;\nBKVOL>0 AND LOW<=买入开仓价*(1-STOPLOSS*0.01),SP;\nAUTOFILTER;'

def run(adapter):
    fn=getattr(adapter,'run_source_program',None)
    if fn is None:
        raise RuntimeError('Platform-specific adapter required for this source language.')
    return fn(ORIGINAL_SOURCE, language=SOURCE_LANGUAGE)
