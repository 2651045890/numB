"""Source-preserving Python port envelope for 简易数字货币现货跟单机器人策略.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function test() { \n    // 测试函数\n    var ts = new Date().getTime()    \n    if (ts % (1000 * 60 * 60 * 6) > 1000 * 60 * 60 * 5.5) {\n        Sleep(1000 * 60 * 10)\n        var x = Math.random()\n        if (x > 0.5) {\n            $.Buy(exchange, x / 10)    \n        } else {\n            $.Sell(exchange, x / 10)    \n        }        \n    }\n}\n\nfunction main() {\n    LogReset(1)\n    if (exchanges.length < 2) {\n        throw "没有跟单的交易所"\n    }\n    var exName = exchange.GetName()\n    // 检测参考交易所\n    if (exName.includes("Futures_")) {\n        throw "仅支持现货跟单"\n    }\n    Log("开始监控", exName, "交易所", "#FF0000")\n    \n    // 检测跟单交易所\n    for (var i = 1 ; i < exchanges.length ; i++) {\n        if (exchanges[i].GetName().includes("Futures_")) {\n            throw "不支持期货交易所跟单"\n        }\n    }\n    \n    var initAcc = _C(exchange.GetAccount)\n    while(1) {\n        if(IsVirtual()) {\n           // 测试函数\n           test()  \n        }  \n        Sleep(5000)\n        \n        // 更新参考账户当前的账户信息\n        var nowAcc = _C(exchange.GetAccount)\n        \n        // 参考交易所账户信息\n        var refTbl = {\n            type : "table", \n            title : "参考交易所",\n            cols : ["名称", "币", "冻结币", "钱", "冻结钱"],\n            rows : []\n        }\n        refTbl.rows.push([exName, nowAcc.Stocks, nowAcc.FrozenStocks, nowAcc.Balance, nowAcc.FrozenBalance])\n        \n        // 跟单交易所账户信息\n        var followTbl = {\n            type : "table", \n            title : "跟单交易所",\n            cols : ["名称", "币", "冻结币", "钱", "冻结钱"],\n            rows : []        \n        }\n        for (var i = 1 ; i < exchanges.length ; i++) {\n            var acc = _C(exchanges[i].GetAccount)\n            var name = exchanges[i].GetName()\n            followTbl.rows.push([name, acc.Stocks, acc.FrozenStocks, acc.Balance, acc.FrozenBalance])\n        }\n        \n        // 状态栏显示\n        LogStatus(_D(), "\\n`" + JSON.stringify(refTbl) + "`", "\\n`" + JSON.stringify(followTbl) + "`")\n        \n        // 检测跟单\n        var amount = (nowAcc.Stocks + nowAcc.FrozenStocks) - (initAcc.Stocks + initAcc.FrozenStocks)\n        var func = null \n        if (amount > 0) {\n            func = $.Buy\n        } else if (amount < 0) {\n            func = $.Sell\n        } else {\n            continue\n        }\n        \n        // 执行跟单\n        Log("跟单！数量：", Math.abs(amount), "#FF0000")\n        for (var i = 1 ; i < exchanges.length ; i++) {            \n            func(exchanges[i], Math.abs(amount))\n        }\n        \n        // 执行跟单之后更新参考交易所账户信息记录\n        initAcc = nowAcc\n    }\n}'
SOURCE_FILE = '简易数字货币现货跟单机器人策略.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
