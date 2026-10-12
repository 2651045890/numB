"""Source-preserving Python port envelope for 行情中心延时.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function main() {\n    mcc = $.NewMarketCenterClient()\n    Log(\'support list: \'+mcc.GetSupportList())\n    mcc.SubscribeSpotTicker(\'binance.com\', \'BTC_USDT\', 200)\n    Sleep(1000)\n    Log("start...")\n    var count = 0\n    \n    var max = -1\n    var min = 9999999\n    var ave = 0\n    var sum = 0\n    \n    for(var i = 0; i < 1000; i++) {\n        var start = new Date().getTime()\n        var ticker = mcc.GetSpotTicker(\'binance.com\', \'BTC_USDT\')\n        var end = new Date().getTime()\n        if (ticker === null) {\n            continue\n        }\n        count += 1\n        var pass = end - start\n        if (pass > max) {\n            max = pass\n        }\n        if (pass < min) {\n            min = pass\n        }\n        sum += pass\n    }\n    ave = sum / count\n    \n    var allstatus = \'行情中心延时测试\\n\'\n    allstatus += "https://www.fmz.com/strategy/183009\\n";\n    allstatus += "♜Q:6510676#0000ff\\n";\n    allstatus += "♜Q群:364655408#0000ff\\n";\n    allstatus += "♜微信: btstarinfo#0000ff\\n";\n    \n    var table = {\n        type: \'table\',\n        title: \'延时测试\',\n        cols: [\'测试次数\', \'最大(ms)\', \'最小(ms)\', \'平均(ms)\'],\n        rows: [\n            [\n                count, max, min, ave\n            ]\n        ]\n    }\n    allstatus += "`" + JSON.stringify(table) + "`" + "\\n";\n\n    LogStatus(allstatus)\n}'
SOURCE_FILE = '行情中心延时.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
