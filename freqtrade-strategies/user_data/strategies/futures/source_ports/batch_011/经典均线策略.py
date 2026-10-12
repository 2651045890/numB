"""Source-preserving Python port envelope for 经典均线策略.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2019-01-01 00:00:00\nend: 2019-07-01 00:00:00\nperiod: 1d\nexchanges: [{"eid":"Bitfinex","currency":"BTC_USD"}]\n*/\n\nfunction main() {\n    var STATE_IDLE  = -1;\n    var state = STATE_IDLE;\n    var entryPrice = 0;\n    var initAccount = _C(exchange.GetAccount);\n    Log(initAccount);\n    while (true) {\n        if (state === STATE_IDLE) {\n            var n = $.Cross(FastPeriod, SlowPeriod);\n            if (Math.abs(n) >= EnterPeriod) {\n                var account = _C(exchange.GetAccount);\n                var ticker = _C(exchange.GetTicker);\n                var obj = n > 0 ? $.Buy(_N(account.Balance * PositionRatio / ticker.Sell, 3)) : $.Sell(_N(account.Stocks * PositionRatio, 3));\n                if (obj) {\n                    opAmount = obj.amount;\n                    entryPrice = obj.price;\n                    state = n > 0 ? PD_LONG : PD_SHORT;\n                    Log("开仓详情", obj, "交叉周期", n);\n                }\n            }\n        } else {\n            var n = $.Cross(ExitFastPeriod, ExitSlowPeriod);\n            var needCover = Math.abs(n) >= ExitPeriod && ((state === PD_LONG && n < 0) || (state === PD_SHORT && n > 0));\n            if (needCover) {\n                Log("离市平仓");\n            } else {\n                var ticker = _C(exchange.GetTicker);\n                if (state === PD_LONG) {\n                    if (ticker.Buy < entryPrice*(1-StopLossRatio)) {\n                        needCover = true;\n                        Log("止损平仓");\n                    }\n                } else {\n                    if (ticker.Sell > entryPrice*(1+StopLossRatio)) {\n                        needCover = true;\n                        Log("止损平仓");\n                    }\n                }\n            }\n            if (needCover) {\n                var nowAccount = _C(exchange.GetAccount);\n                var obj = state === PD_LONG ? $.Sell(_N(nowAccount.Stocks - initAccount.Stocks, 3)) : $.Buy(_N(initAccount.Stocks - nowAccount.Stocks, 3));\n                state = STATE_IDLE;\n                nowAccount = _C(exchange.GetAccount);\n                LogProfit(nowAccount.Balance - initAccount.Balance, \'钱:\', nowAccount.Balance, \'币:\', nowAccount.Stocks, \'平仓详情:\', obj, "交叉周期", n);\n            }\n        }\n        Sleep(Interval*1000);\n    }\n}'
SOURCE_FILE = '经典均线策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
