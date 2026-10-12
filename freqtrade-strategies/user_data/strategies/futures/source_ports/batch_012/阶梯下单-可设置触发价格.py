"""Source-preserving Python port envelope for 阶梯下单-可设置触发价格.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function adjustFloat(v) {\n    return Math.floor(parseFloat(v.toFixed(10))*1000)/1000;\n}\n\nfunction GetAccount(e) {\n    var account;\n    while (!(account = exchange.GetAccount())) {\n        Sleep(Interval);\n    }\n    return account;\n}\n\nfunction GetTicker() {\n    var ticker;\n    while (!(ticker = exchange.GetTicker())) {\n        Sleep(1000);\n    }\n    return ticker;\n}\n\nfunction main() {\n    var ticker = GetTicker();\n    var InitPrice = ticker.Last;\n    if (EnableTrigger) {\n        Log(\'当前价格: \', InitPrice, InitPrice > TriggerPrice ? \'价格跌破\' : \'价格涨超\', TriggerPrice, \'时触发阶梯下单\');\n        while (true) {\n            if (InitPrice > TriggerPrice && ticker.Last < TriggerPrice) {\n                Log(\'当前价格\', ticker.Last, \'价格跌破 \', TriggerPrice, \'元, 开始下单\');\n                break;\n            } else if (InitPrice < TriggerPrice && ticker.Last > TriggerPrice) {\n                Log(\'当前价格\', ticker.Last, \'价格涨超 \', TriggerPrice, \'元, 开始下单\');\n                break;\n            }\n            ticker = GetTicker();\n            Sleep(1000);\n        }\n    }\n    var account = GetAccount();\n    var needMoney = 0;\n    var needStocks = 0;\n    for (var i = 0; i < OrderNum; i++) {\n        needMoney += (StartPrice - (i * PriceDiff)) * Amount;\n        needStocks += Amount;\n    }\n\n    if (OpType == 0) {\n        if (needMoney > account.Balance) {\n            throw "没有足够的钱下单";\n        }\n        for (var i = 0; i < OrderNum; i++) {\n            exchange.Buy(adjustFloat(StartPrice - (i * PriceDiff)), Amount);\n        }\n    } else {\n        if (needStocks > account.Stocks) {\n            throw "没有足够的币下单";\n        }\n        for (var i = 0; i < OrderNum; i++) {\n            exchange.Sell(adjustFloat(StartPrice + (i * PriceDiff)), Amount);\n        }        \n    }\n    Log("全部委托完成");\n}\n'
SOURCE_FILE = '阶梯下单-可设置触发价格.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
