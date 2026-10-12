"""Source-preserving Python port envelope for 范例-定时测试微信消息推送.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function main(){\n    var initTime = (new Date()).getTime() ;\n    Log("程序起始时间：",$.getTimeByNormal(initTime) );\n    var preDif = 0;\n    var str = "";\n    while(true){\n        var nowTime = (new Date()).getTime();\n        if(  Math.floor((nowTime - initTime) / (1000*60*10) ) !== preDif ){\n            str = $.getTimeByNormal(nowTime);\n            Log("从程序开始执行，已过10分钟！提醒。"+"--现在时间："+str+"推送微信@" );\n            preDif = Math.floor((nowTime - initTime) / (1000*60*10) ) ;\n        }\n        Sleep(2000); \n    }\n}'
SOURCE_FILE = '范例-定时测试微信消息推送.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
