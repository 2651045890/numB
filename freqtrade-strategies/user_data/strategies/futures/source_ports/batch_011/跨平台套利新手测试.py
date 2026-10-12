"""Source-preserving Python port envelope for 跨平台套利新手测试.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2018-01-01 00:00:00\nend: 2018-08-01 14:00:00\nperiod: 1h\nexchanges: [{"eid":"Bitfinex","currency":"ETH","balance":5000,"stocks":10},{"eid":"OKCoin_EN","currency":"ETH","balance":5000,"stocks":10}]\n*/\nvar buyExchange;\nvar sellExchange;\n\nfunction calc(sellExchange, buyExchange){\n        var date = _D();\n        sellDepth = sellExchange.GetDepth();\n        sellAccount = sellExchange.GetAccount();\n        sellPrice = sellDepth.Bids[1].Price;\n        sellAmount = sellDepth.Bids[1].Amount;\n        \n        buyDepth = buyExchange.GetDepth();\n        buyAccount = buyExchange.GetAccount();\n        buyPrice = buyDepth.Asks[1].Price;\n        buyAmount = buyDepth.Asks[1].Amount;\n        \n        amount = (sellAmount > buyAmount) ? buyAmount : sellAmount;\n        amount = (amount > sellAccount.Stocks) ? sellAccount.Stocks : amount;\n        amount = (amount > buyAccount.Balance / buyPrice) ? buyAccount.Balance / buyPrice : amount;\n        priceRate = sellPrice / buyPrice;\n        if(amount > 0){\n            if(priceRate >= minRate){\n                buyExchange.Buy(-1, amount);\n                sellExchange.Sell(-1, amount);\n                Log(date);\n                Log("卖出:", sellExchange.GetName(), "卖出价格:", sellPrice, "买入:", buyExchange.GetName(), " 买入价格:", buyPrice, " 比例:", priceRate, " 总量:", amount);\n                Log(\'统计资产...\');\n                Log(\'交易所:\', exchanges[0].GetName(), \' 账户:\', exchanges[0].GetAccount());\n                Log(\'交易所:\', exchanges[1].GetName(), \' 账户:\', exchanges[1].GetAccount());\n            }\n        }\n    \n}\n\nfunction main(){\n    while(true){\n        calc(exchanges[0], exchanges[1]);\n        calc(exchanges[1], exchanges[0]);\n    }\n\n}\n'
SOURCE_FILE = '跨平台套利新手测试.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
