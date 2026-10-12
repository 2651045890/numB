"""Source-preserving Python port envelope for 简单预定买入后卖出插件Buy-then-Sell-ping-pong-strategy.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = "function CancelPendingOrders() {\n    var orders = _C(exchange.GetOrders);\n    for (var j = 0; j < orders.length; j++) {\n        exchange.CancelOrder(orders[j].Id, orders[j]);\n    }\n}\nfunction main() {\n    Log('robot starts to run')\n    if(BUYPRICE >= SELLPRICE){\n        throw 'check buy and sell price'\n    }\n    CancelPendingOrders()\n    var account = _C(exchange.GetAccount)\n    var init_account = account\n    Log('account: ', account.Balance);\n    if(account.Balance > BUYPRICE*BUYAMOUNT){\n        exchange.Buy(BUYPRICE, BUYAMOUNT);\n    }else{\n        throw 'account balances is not enough'\n    }\n    while(true){\n        account = _C(exchange.GetAccount)\n        if(account.Stocks >= init_account.Stocks + 0.01){\n            exchange.Sell(SELLPRICE, account.Stocks - init_account.Stocks)\n        }\n        Sleep(Intervel*1000)\n    }\n}\n"
SOURCE_FILE = '简单预定买入后卖出插件Buy-then-Sell-ping-pong-strategy.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
