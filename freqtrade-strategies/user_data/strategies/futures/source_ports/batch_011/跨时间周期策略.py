"""Source-preserving Python port envelope for 跨时间周期策略.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2021-02-14 00:00:00\nend: 2022-02-13 23:59:00\nperiod: 15m\nbasePeriod: 5m\nexchanges: [{"eid":"Bitfinex","currency":"BTC_USD","stocks":0}]\nargs: [["rsi_period",10]]\n*/\n\n/*\n* fast_ma: 快均线，短周期\n* slow_ma: 慢均线，长周期\n* rsi_period: rsi周期\n* tick_interval: 循环间隔\n* splide_price: 滑点\n*/\n\n// RSI指示操作状态\nvar RSI_NONE = 0;\nvar RSI_BUY = 1;\nvar RSI_SELL = 2;\n\n// 取消未成交下单\nfunction canelPendingOrders() {\n    while (true) {\n        let orders = _C(exchange.GetOrders);\n        if (orders.length == 0) {\n            break;\n        }\n        for (let i = 0; i < orders.length; i++) {\n            exchange.CancelOrder(orders[i].Id);\n        }\n    }\n}\n\n// 获取RSI操作状态\nfunction getRsiStatus(records) {\n    let rsi = TA.RSI(records, rsi_period)[records.length - 1];\n    if (rsi < 30) {\n        return RSI_BUY;\n    }\n    else if (rsi > 70) {\n        return RSI_SELL;\n    }\n    else {\n        return RSI_NONE;\n    }\n}\n\nfunction onTick() {\n    let records = _C(exchange.GetRecords, PERIOD_M15);\n    let ticker = _C(exchange.GetTicker);\n    let account = _C(exchange.GetAccount);\n    let fast = TA.MA(records, fast_ma);\n    let slow = TA.MA(records, slow_ma);\n    let n = _Cross(fast, slow);\n    if (n > 0 && getRsiStatus(records) == RSI_BUY) {\n        canelPendingOrders();\n        let price = ticker.Last + splide_price;\n        let amount = account.Balance / price - 0.1;\n        if (amount > 0.1) {\n            exchange.Buy(price, amount);\n        }\n    }\n    else if (n < 0 && getRsiStatus(records) == RSI_SELL) {\n        canelPendingOrders();\n        let price = ticker.Last - splide_price;\n        let amount = account.Stocks;\n        if (amount > 0.1) {\n            exchange.Sell(price, amount);\n        }\n    }\n}\n\nfunction main() {\n    while (true) {\n        onTick();\n        Sleep(tick_interval * 1000);\n    }\n}'
SOURCE_FILE = '跨时间周期策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
