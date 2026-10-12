"""Source-preserving Python port envelope for 简单马丁格尔多空交易策略.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2017-06-26 00:00:00\nend: 2022-02-16 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","currency":"eth_USDT""currency":"bch_USDT"}]\n*/\n\nvar n =0.001 //初始下单数\nvar MarginLevel = 50 //合约杠杆 \nvar profit = 0.05 //期望收益 ，不能小于手续费 \nvar bet=1//倍率\n\n\n//取随机数 \nfunction sum(m, n) {\u3000\u3000\n    var num = Math.floor(Math.random() * (m - n) + n);\u3000\u3000\n    return num;\n}\n\nfunction main() {\n    var ret = exchange.IO("api", "POST", "/fapi/v1/positionSide/dual", "dualSidePosition=true")\n    // ret : {"code":200,"msg":"success"}\n    Log(ret)\n}\n   \n    \nfunction main() {\n    exchange.SetContractType("swap")\n    exchange.SetMarginLevel(MarginLevel)\n    var position = []\n    while (true) {\n        position = exchange.GetPosition()\n        if (position.length == 0) {\n            //取随机数0、1作为方向\n            var redom = sum(2, 0)\n            Log(redom)\n            if (redom == 0) {\n                n=0.001\n                exchange.SetDirection("sell")\n                exchange.Sell(-1, n, "开空")\n            }\n            if (redom == 1) {\n                n=0.002\n                exchange.SetDirection("buy")\n                exchange.Buy(-1, n, "开多")\n            }\n\n        }\n        if (position.length > 0) {\n\n            if (position[0].Type == 0) {\n                //盈利大于期望 \n                if (position[0].Profit > profit) {\n                    exchange.SetDirection("closebuy")\n                    exchange.Sell(-1, position[0].Amount)\n                    \n                    let redom = Math.random()\n                    n=0.002\n                    if (redom < 0.5) {  \n                     n=0.003\n                    exchange.SetDirection("sell")\n                    exchange.Sell(-1, n, "空头")\n                }\n                    }\n                //负盈利大于保证金 则加仓\n\n                if (position[0].Profit < position[0].Margin * -1) {\n                    n=n*bet\n                    exchange.SetDirection("buy")\n                    exchange.Buy(-1, position[0].Amount=n)\n                   \n                }\n            }\n            if (position[0].Type == 1) {\n                if (position[0].Profit > profit) {\n                    exchange.SetDirection("closesell")\n                    exchange.Buy(-1, position[0].Amount)\n                    let redom = Math.random()\n                    n=0.004\n                    if (redom > 0.5) {  \n                    exchange.SetDirection("buy")\n                    exchange.Buy(-1, n, "多头")\n                }\n                }\n                if (position[0].Profit < position[0].Margin * -1) {\n                    n=n*bet\n                    exchange.SetDirection("sell")\n                    exchange.Sell(-1, position[0].Amount=n)\n                }\n            }\n            Sleep(60000)\n        }\n    }\n\n}'
SOURCE_FILE = '简单马丁格尔多空交易策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
