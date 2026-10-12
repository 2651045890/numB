"""Source-preserving Python port envelope for 高低点突破成交量指数加权策略Break-High-and-Low-Volume-Index-Weighting-Strategy.md.

Original language: pascal.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'pascal'
ORIGINAL_SOURCE = '(*backtest\nstart: 2018-04-01 00:00:00\nend: 2018-05-28 00:00:00\nperiod: 1h\nexchanges: [{"eid":"Futures_OKCoin","currency":"BTC_USD"}]\nargs: [["N",100],["MINAMOUNT",10],["TradeAmount",10,126961],["ContractType","this_week",126961]]\n*)\n\nLOTS:=MAX(MINAMOUNT,INTPART(MONEYTOT/O * 0.8));\nVJQ:EMA(V*(C-REF(C,NC)),N);\nB:=VJQ>0;\nS:=VJQ<0;\nBUYPK:=BARPOS>N AND BKVOL=0 AND B AND H>=HHV(H,N);\nSELLPK:=BARPOS>N AND SKVOL=0 AND S AND L<=LLV(L,N);\nBUYP:=SKVOL>0 AND B;\nSELLP:=BKVOL>0 AND S;\n\n// 入场\n// Enter\nSELLPK,SPK(LOTS);\nBUYPK,BPK(LOTS);\n\n// 出场\n// Leave\nBUYP,BP(SKVOL);\nSELLP,SP(BKVOL);\n\n// 止损\n// Stop loss\nC>=SKPRICE*(1+SLOSS*0.01),BP(SKVOL);\nC<=BKPRICE*(1-SLOSS*0.01),SP(BKVOL);\nAUTOFILTER;\n'
SOURCE_FILE = '高低点突破成交量指数加权策略Break-High-and-Low-Volume-Index-Weighting-Strategy.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
