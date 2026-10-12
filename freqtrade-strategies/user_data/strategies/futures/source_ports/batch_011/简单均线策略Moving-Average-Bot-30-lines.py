"""Source-preserving Python port envelope for 简单均线策略Moving-Average-Bot-30-lines.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*backtest\nstart: 2020-10-11 00:00:00\nend: 2020-10-11 23:59:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Binance","currency":"BTC_USDT"}]\n*/\n\nstart = false\nfunction main() {\n    Log(\'started\');\n    var initAccount = _C(exchange.GetAccount);\n    var ticker = exchange.GetTicker();\n    var InitValue = (initAccount.Stocks + initAccount.FrozenStocks)*ticker.Last + initAccount.Balance + initAccount.FrozenBalance;\n    while (true) {\n        var records = _C(exchange.GetRecords, PERIOD_M15);\n        if(!start){\n            Log(records[0], records.length)\n            start = true\n        }\n        ticker =_C(exchange.GetTicker);\n        var FastRecords = TA.MA(records,FastPeriod);\n        var SlowRecords = TA.MA(records,SlowPeriod);\n        var NowAccount = _C(exchange.GetAccount);\n        var n = _Cross(FastRecords, SlowRecords);\n        if (n >= EnterPeriod && NowAccount.Balance > 0) {\n            var Price = _N(ticker.Sell+Slippage, 2);\n            var Amount = _N(0.99*NowAccount.Balance/Price, 3);\n            if(Amount>0.1){\n               var id = exchange.Buy(Price, Amount);\n               if(exchange.GetOrders(id).Status == ORDER_STATE_PENDING){exchange.CancelOrder(id);}\n               LogProfit((NowAccount.Stocks + NowAccount.FrozenStocks)*ticker.Last + NowAccount.Balance + NowAccount.FrozenBalance - InitValue);\n            }\n        }\n        if(n <= -EnterPeriod && NowAccount.Stocks > 0) {\n            var Price = _N(ticker.Buy-Slippage, 2);\n            var Amount = _N(NowAccount.Stocks, 3);\n            if(Amount>0.1){\n                var id = exchange.Sell(Price, Amount);\n                if(exchange.GetOrders(id).Status == ORDER_STATE_PENDING){exchange.CancelOrder(id);}\n                LogProfit((NowAccount.Stocks + NowAccount.FrozenStocks)*ticker.Last + NowAccount.Balance + NowAccount.FrozenBalance - InitValue);\n            }\n        }\n        if(!IsVirtual()){\n            Sleep(Interval*1000)\n        }\n    }\n}'
SOURCE_FILE = '简单均线策略Moving-Average-Bot-30-lines.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
