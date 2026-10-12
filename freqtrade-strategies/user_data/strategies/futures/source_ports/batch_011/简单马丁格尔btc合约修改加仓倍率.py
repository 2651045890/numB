"""Source-preserving Python port envelope for 简单马丁格尔btc合约修改加仓倍率.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2017-06-26 00:00:00\nend: 2022-02-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"XXX_USDT"}]\n*/\nvar symbols = ["BTC_USDT", "LTC_USDT", "EOS_USDT", "ETH_USDT"]\nvar buyValue = 1000\nfunction main(){\n  for(var i=0;i<symbols.length;i++){\n      exchange.SetCurrency(symbols[i])\n      var ticker = exchange.GetTicker()\n      var amount = _N(buyValue/ticker.Sell, 3)\n      exchange.Buy(ticker.Sell, amount)\n      Sleep(1000)\n  }\n}\nvar n = 0.001 //初始下单数\nvar MarginLevel = 50 //合约杠杆 \nvar profit = 0.05 //期望收益 ，不能小于手续费 \nvar bet = 1.5//倍率\n\n//取随机数 \nfunction sum(m, n) {\u3000\u3000\n    var num = Math.floor(Math.random() * (m - n) + n);\u3000\u3000\n    return num;\n}\n\n\nfunction main() {\n    var ret = exchange.IO("api", "POST", "/fapi/v1/positionSide/dual", "dualSidePosition=true")\n    // ret : {"code":200,"msg":"success"}\n    Log(ret)\n}\nfunction main() {\n\n    exchange.SetContractType("swap")\n    exchange.SetMarginLevel(MarginLevel)\n    var position = []\n    while (true) {\n        position = exchange.GetPosition()\n        if (position.length == 0) {\n            //取随机数0、1作为方向\n            var redom = sum(2, 0)\n            Log(redom)\n            if (redom == 0) {\n                n=0.001\n                exchange.SetDirection("sell")\n                exchange.Sell(-1, n, "开空")\n            }\n            if (redom == 1) {\n                n=0.001\n                exchange.SetDirection("buy")\n                exchange.Buy(-1, n, "开多")\n            }\n\n        }\n        if (position.length > 0) {\n\n            if (position[0].Type == 0) {\n                //盈利大于期望 \n                if (position[0].Profit > profit) {\n                    \n                    exchange.SetDirection("closebuy")\n                    exchange.Sell(-1, position[0].Amount)\n                }\n                //负盈利大于保证金 则加仓\n\n                if (position[0].Profit < position[0].Margin * -2) {\n                   n = n * bet\n                    exchange.SetDirection("buy")\n                    exchange.Buy(-1, position[0].Amount=n)\n                }\n            }\n            if (position[0].Type == 1) {\n                if (position[0].Profit > profit) {\n                    \n                    exchange.SetDirection("closesell")\n                    exchange.Buy(-1, position[0].Amount)\n                }\n                if (position[0].Profit < position[0].Margin * -2) {\n                    n = n * bet\n                    exchange.SetDirection("sell")\n                    exchange.Sell(-1, position[0].Amount=n)\n                }\n            }\n            Sleep(60000)\n        }\n    }\n\n}'
SOURCE_FILE = '简单马丁格尔btc合约修改加仓倍率.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
