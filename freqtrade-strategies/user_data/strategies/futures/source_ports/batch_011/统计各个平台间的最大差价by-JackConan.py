"""Source-preserving Python port envelope for 统计各个平台间的最大差价by-JackConan.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'var maxSpace = 0;\n\nfunction adjustFloat(v) {\n    return Math.floor(v*1000)/1000;\n}\n\nfunction printCurPrice() {\n    for (var i = 0; i < exchanges.length; i++) {\n        Log(exchanges[i].GetName(),\'=\',exchanges[i].GetTicker());\n    }\n}\n\nfunction onTick() {\n    // TODO something.\n    var smallPrice = 99999;\n    var bigPrice = 0;\n    var curPrice = 0;\n    var curSpace = 0;\n    \n    for (var i = 0; i < exchanges.length; i++) {\n        curPrice = exchanges[i].GetTicker().Buy;\n        if (curPrice < smallPrice){\n            smallPrice = curPrice;\n        }\n        if (curPrice > bigPrice){\n            bigPrice = curPrice;\n        }\n        curSpace = bigPrice - smallPrice;\n    }\n    \n    if (curSpace > maxSpace){\n        maxSpace = curSpace;\n        Log(\'差价:\', adjustFloat(maxSpace),\'高价:\', bigPrice,\'低价:\', smallPrice, \'发生时间 →_→\');\n        //打印各交易所当前的市场行情；\n        printCurPrice();\n    }\n}\n\nfunction main() {\n    if (exchanges.length < 2) {\n        Log("交易所数量最少得两个才能完成统计");\n        return;\n    }\n    while(true) {\n        onTick();\n        Sleep(60000);\n    }\n}'
SOURCE_FILE = '统计各个平台间的最大差价by-JackConan.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
