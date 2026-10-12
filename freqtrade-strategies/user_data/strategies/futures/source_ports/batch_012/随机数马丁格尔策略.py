"""Source-preserving Python port envelope for 随机数马丁格尔策略.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = "// 随机数马丁格尔策略\n// 每次下单前，根据随机数决定下单方向和下单数量\n\n// 设置初始资金和下单数量\nvar initCapital = 10000; // 初始资金\nvar initAmount = 1; // 初始下单数量\n\n// 设置随机数范围和下单比例\nvar minRand = 0; // 最小随机数\nvar maxRand = 100; // 最大随机数\nvar buyRatio = 0.5; // 买入比例\nvar sellRatio = 0.5; // 卖出比例\n\n// 定义下单函数\nfunction placeOrder(direction, amount) {\n    if (direction == 'buy') {\n        exchange.Buy(-1,amount);\n    } else if (direction == 'sell') {\n        exchange.Sell(-1,amount);\n    }\n}\n\n// 定义主函数\nfunction main() {\n    var capital = initCapital; // 当前资金\n    var amount = initAmount; // 当前下单数量\n    var lastDirection = ''; // 上次下单方向\n\n    while (true) {\n        // 生成随机数\n        var rand = Math.floor(Math.random() * (maxRand - minRand + 1)) + minRand;\n\n        // 根据随机数决定下单方向和下单数量\n        var direction = '';\n        if (rand <= buyRatio * maxRand) {\n            direction = 'buy';\n        } else if (rand >= (1 - sellRatio) * maxRand) {\n            direction = 'sell';\n        }\n\n        if (direction) {\n            // 如果方向发生变化，则重置下单数量\n            if (direction != lastDirection) {\n                amount = initAmount;\n            }\n\n            // 下单\n            placeOrder(direction, amount);\n\n            // 更新资金和下单数量\n            var orderPrice = exchange.GetTicker().Last;\n            var orderAmount = amount * orderPrice;\n            if (direction == 'buy') {\n                capital -= orderAmount;\n            } else if (direction == 'sell') {\n                capital += orderAmount;\n            }\n            amount *= 2;\n\n            // 打印日志\n            Log('下单方向：', direction, '下单数量：', amount, '当前资金：', capital);\n\n            // 更新上次下单方向\n            lastDirection = direction;\n        }\n\n        Sleep(1000);\n    }\n}\n"
SOURCE_FILE = '随机数马丁格尔策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
