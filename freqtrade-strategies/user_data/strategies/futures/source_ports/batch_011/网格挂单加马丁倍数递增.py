"""Source-preserving Python port envelope for 网格挂单加马丁倍数递增.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2017-06-26 00:00:00\nend: 2022-02-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"ETH_USDT"}]\n*/\nvar MarginLevel=20\nexchange.SetMarginLevel(MarginLevel)\nfunction cancelAll() {\n    while (true) {\n        var orders = _C(exchange.GetOrders)\n        if (orders.length == 0) { \n            break \n        }\n        for (var i = 0 ; i < orders.length ; i++) {\n            exchange.CancelOrder(orders[i].Id, orders[i])\n            Sleep(interval)\n        }\n    }\n}\n\n\nfunction getLong(arr, kind) {\n    var ret = null \n    for (var i = 0 ; i < arr.length ; i++) {\n        if (arr[i].Type == (kind == "pos" ? PD_LONG : ORDER_TYPE_BUY)) {\n            ret = arr[i]\n        }\n    }\n    return ret\n}\n\nfunction pendingBidOrders(firstPrice) {\n    var index = 0\n    var bet=ratio\n    var n = baseAmount\n    while (true) {\n        var pos = _C(exchange.GetPosition)\n        var price = firstPrice - index * baseSpacing\n         n=n*ratio\n        index++\n        exchange.SetDirection("buy")\n        exchange.Buy(price, amount=n)        \n        if (pos.length != 0) {\n            var longPos = getLong(pos, "pos")\n            if (longPos) {\n                exchange.SetDirection("closebuy")\n                exchange.Sell(longPos.Price + profitTarget, longPos.Amount)\n            }\n        }\n        while (true) {\n            Sleep(interval)\n            if (!getLong(_C(exchange.GetOrders), "orders")) {\n                cancelAll()\n                break\n            }\n            if (!getLong(_C(exchange.GetPosition), "pos")) {\n                cancelAll()\n                return \n            }\n        }\n    }\n}\n\nfunction main() {\n    exchange.SetContractType(symbol)\n    while (true) {\n        pendingBidOrders(_C(exchange.GetTicker).Last)\n    }\n}'
SOURCE_FILE = '网格挂单加马丁倍数递增.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
