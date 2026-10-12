"""Deep source-preserving Python adapter for 暴力马丁适合eth和btc-Copy.md."""
SOURCE_FILE='暴力马丁适合eth和btc-Copy.md'
SOURCE_LANGUAGE='pascal'
SOURCE_FEATURES=[]
SOURCE_FIDELITY_NOTES=['Source is Pascal/麦语言-style strategy code; Python version retains the state/condition/order map, but platform-specific built-ins require adapter bindings.']
ORIGINAL_SOURCE='(*backtest\nstart: 2022-01-01 08:00:00\nend: 2022-02-02 00:00:00\nperiod: 6h\nbasePeriod: 1m\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT","balance":600,"fee":[0.008,0.025]}]\nargs: [["RunMode",1,126961],["TradeAmount",0.001,126961],["MaxCacheLen",3000,126961],["ContractType","swap",126961],["MinLot",0.001,126961],["LoopInterval",1,126961],["SyncDelay",1,126961],["MarginLevel",50,126961]]\n*)\n\n\n\n\nTR:=MAX(MAX((HIGH-LOW),ABS(REF(CLOSE,1)-HIGH)),ABS(REF(CLOSE,1)-LOW));\nATR:WMA(TR,10); //求26个周期内真实波幅的简单移动平均\nTC:N;//MAX(ROUND(5/C*MONEY/200,3),0.002);//手续费0.023，杠杆50倍\nyue:ABS(BKVOL+SKVOL);\njunjia:ABS(BKPRICEAV+SKPRICEAV);\n\n\n\nCCC^^WMA(C,20);\nAA^^WMA(C,10);\n\n\n\nBKVOL=0 AND SKVOL=0 AND  REF(AA,1)>REF(CCC,1)  , BK(TC);\n\n\nISLASTBK AND C < BKPRICE-ATR*0.1 , BK(ROUND(XX*BKVOL,3));\n\n\nBKVOL>0 AND C > BKPRICEAV+ATR*0.1 , SP(BKVOL);\n\n\n\n\nREF(AA,1)<REF(CCC,1)    AND BKVOL>0,SP(BKVOL);\n INFO(REF(AA,1)<REF(CCC,1)    AND BKVOL>0, \'止损离场\');\n \n \n\nSKVOL=0 AND BKVOL=0 AND  REF(AA,1)<REF(CCC,1)  , SK(TC);\n\n\n\nISLASTSK AND C > SKPRICE + 0.1*ATR, SK(ROUND(XX*SKVOL,3));\n\n\nSKVOL>0 AND C < SKPRICEAV - 0.1*ATR , BP(SKVOL);\n\n\n\n\n\nREF(AA,1)>REF(CCC,1)   AND SKVOL>0,BP(SKVOL);\n INFO(REF(AA,1)>REF(CCC,1)AND SKVOL>0  , \'止损离场\');\nMULTSIG(0, 0, 50, 0);\nTRADE_AGAIN(100);'

def run(adapter):
    fn=getattr(adapter,'run_source_program',None)
    if fn is None:
        raise RuntimeError('Platform-specific adapter required for this source language.')
    return fn(ORIGINAL_SOURCE, language=SOURCE_LANGUAGE)
