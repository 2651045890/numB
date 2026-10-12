"""Source-preserving Python port envelope for 麦语言网格策略.md.

Original language: pascal.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'pascal'
ORIGINAL_SOURCE = 'VARIABLE:V1:1;\nIF dtkc>0 AND BKVOL=0 THEN BEGIN 1,BK(dtkc);V1:C;INFO(1,V1);END\nIF ktkc>0 AND SKVOL=0 THEN BEGIN 1,SK(ktkc);V1:C;INFO(1,V1);END\nIF BKVOL>0 AND C>V1/(1-y) THEN BEGIN 1,SP(jian);V1:C;INFO(1,V1);END\nIF BKVOL>0 AND C<V1*(1-s) THEN BEGIN 1,BK(jia);V1:C;INFO(1,V1);END\nIF SKVOL>0 AND C<V1/(1+y) THEN BEGIN 1,BP(jian);V1:C;INFO(1,V1);END\nIF SKVOL>0 AND C>V1*(1+s) THEN BEGIN 1,SK(jia);V1:C;INFO(1,V1);END\nMULTSIG(0,0,60,0);\nTRADE_AGAIN(1000);\n'
SOURCE_FILE = '麦语言网格策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
