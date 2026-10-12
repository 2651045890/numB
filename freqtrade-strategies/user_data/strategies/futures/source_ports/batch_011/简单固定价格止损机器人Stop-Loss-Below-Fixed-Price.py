"""Source-preserving Python port envelope for 简单固定价格止损机器人Stop-Loss-Below-Fixed-Price.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = "function CancelPendingOrders() {\n    var orders = _C(exchange.GetOrders);\n    for (var j = 0; j < orders.length; j++) {\n        exchange.CancelOrder(orders[j].Id, orders[j]);\n    }\n}\nfunction StopLoss(){\n    var done = false\n    while(!done){\n        var ticker = _C(exchange.GetTicker)\n        account = _C(exchange.GetAccount)\n        var price = ticker.Buy\n        var amount = account.Stocks\n        try{\n            if(amount > 0){\n                var id = exchange.Sell(price, amount);\n                if(id){\n                    exchange.CancelOrder(id)\n                }\n                else{\n                    Log('all coins are sold')\n                    Log('total coins: ', account.Stocks)\n                    done = true\n                }\n            }\n        }catch(err){\n            Log('error, stop')\n            done = true\n        }\n        Sleep(1000);\n    }\n}\nfunction main() {\n    Log('robot starts to run')\n    CancelPendingOrders()\n    var account = _C(exchange.GetAccount)\n    Log('total coins: ', account.Stocks);\n    while(true){\n        var ticker = _C(exchange.GetTicker)\n        if(ticker.Last <= StopPrice){\n            Log('Last price is:', ticker.Last, 'Stop price is: ', StopPrice)\n            Log('the stop price has reached, start to sell')\n            StopLoss();\n            break;\n        }\n        Sleep(Intervel*1000)\n    }\n    Log('robot has stopped')\n}"
SOURCE_FILE = '简单固定价格止损机器人Stop-Loss-Below-Fixed-Price.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
