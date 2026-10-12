"""Source-preserving Python port envelope for 马丁格尔测试.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '// 马丁格尔策略\nvar baseAmount = 0.001; // 初始下单数量\nvar martingaleFactor = 1.01; // 加码因子\nvar maxOrders = 100; // 最大下单次数\nvar currentOrders = 0; // 当前下单次数\nvar currentAmount = baseAmount; // 当前下单数量\n\nfunction main() {\n    while (true) {\n        var ticker = exchange.GetTicker();\n        var price = ticker.Last;\n        var buyPrice = price - 1000; // 设置买入价为当前价格减1\n        var sellPrice = price + 500; // 设置卖出价为当前价格加1\n        if (currentOrders < maxOrders) {\n            // 下单\n            if (currentOrders % 2 == 0) {\n                // 偶数次下单买入\n                var orderId = exchange.Buy(buyPrice, currentAmount);\n                if (orderId) {\n                    currentOrders++;\n                    currentAmount *= martingaleFactor;\n                }\n            } else {\n                // 奇数次下单卖出\n                var orderId = exchange.Sell(sellPrice, currentAmount);\n                if (orderId) {\n                    currentOrders++;\n                    currentAmount *= martingaleFactor;\n                }\n            }\n        } else {\n            // 达到最大下单次数，退出循环\n            break;\n        }\n        Sleep(1000); // 等待1秒钟\n    }\n}\n'
SOURCE_FILE = '马丁格尔测试.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
