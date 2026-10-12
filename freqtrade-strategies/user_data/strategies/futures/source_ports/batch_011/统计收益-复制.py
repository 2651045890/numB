"""Source-preserving Python port envelope for 统计收益-复制.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'var okrights=0;\nvar vcright=0;\nvar InitRights=0;\nvar totalrights=0;\nvar profit=0;\nvar oldprofit=0;\n\nSetErrorFilter("502:|503:|unexpected|network|timeout|WSARecv|Connect|GetAddr|no such|reset|http|received|EOF");\n\n\n\nfunction Rights() {\n        \n        var accountok;\n        var accountvc;\n        while (!(accountok = exchanges[0].GetAccount())) {\n            Sleep(500);\n        }\n        while (!(accountvc = exchanges[1].GetAccount())) {\n            Sleep(500);\n        }\n        var objok;\n        var objvc;\n        \n        objok=JSON.parse(exchanges[0].GetRawJSON());\n        objvc=JSON.parse(exchanges[1].GetRawJSON());\n        \n        okrights=objok.info["btc"].rights;\n        vcrights=objvc.dynamicRights;\n        totalrights=okrights+vcrights;\n        \n        \n}\n\nfunction main(){\n    Rights();\n    InitRights=totalrights;\n   Log("初始权益合计_BTC",InitRights);\n   while(true){\n    Rights();\n    profit=totalrights-InitRights;\n    if(profit!==oldprofit){\n    LogProfit(profit,"BTC");\n    oldprofit=profit;\n    }\n    Sleep(LXT*1000);\n   }\n   \n \n}\n\n\n\n'
SOURCE_FILE = '统计收益-复制.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
