"""Deep semantic map of FMZ JavaScript strategy 数字货币现货打新抢币策略教学.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '数字货币现货打新抢币策略教学.md'
SOURCE_FEATURES = ['var ', 'for ', 'while ', 'exchange.', '_C(', 'Sleep(', 'GetDepth']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = 'function pendingOrders(ordersNum, price, amount, deltaPrice, deltaAmount) {\n    var routineOrders = []\n    var ordersIDs = []\n    for (var i = 0 ; i < ordersNum ; i++) {\n        var routine = exchange.Go("Buy", price + i * deltaPrice, amount + i * deltaAmount)\n        routineOrders.push(routine)\n        Sleep(ApiReqInterval)        \n    }\n    for (var i = 0 ; i < routineOrders.length ; i++) {\n        var orderId = routineOrders[i].wait()\n        if (orderId) {\n            ordersIDs.push(orderId)\n            Log("成功挂单", orderId)\n        }        \n    }\n    return ordersIDs\n}\n\nfunction main() {\n    if (symbol == "null" || pendingPrice == -1 || pendingAmount == -1 || pendingPrice == -1 || deltaPrice == -1 || deltaAmount == -1) {\n        throw "参数设置错误"\n    }\n    exchange.SetCurrency(symbol)\n    // 屏蔽错误信息\n    SetErrorFilter("GetDepth")\n    while (true) {\n        var msg = ""\n        var depth = exchange.GetDepth()\n        if (!depth || (depth.Bids.length == 0 && depth.Asks.length == 0)) {\n            // 没有深度\n            msg = "没有深度数据，等待！"\n            Sleep(500)\n        } else {\n            // 获取到深度\n            Log("并发下单！")\n            var ordersIDs = pendingOrders(ordersNum, pendingPrice, pendingAmount, deltaPrice, deltaAmount)\n            while (true) {\n                var orders = _C(exchange.GetOrders)\n                if (orders.length == 0) {\n                    Log("当前挂单个数0，停止运行")\n                    return \n                }\n                var tbl = {\n                    type: "table",\n                    title: "当前挂单",\n                    cols: ["id", "价格", "数量"], \n                    rows: []\n                }\n                _.each(orders, function(order) {\n                    tbl.rows.push([order.Id, order.Price, order.Amount])\n                })\n                LogStatus(_D(), "\\n`" + JSON.stringify(tbl) + "`")\n                Sleep(500)\n            }\n        }\n        LogStatus(_D(), msg)\n    }\n}'

class FMZDeepPort:
    source_file = SOURCE_FILE
    source_features = SOURCE_FEATURES
    fidelity_notes = SOURCE_FIDELITY_NOTES
    javascript = ORIGINAL_JAVASCRIPT
    def run(self, adapter):
        runner = getattr(adapter, 'run_fmz_javascript', None)
        if runner is None:
            raise RuntimeError('This strategy needs an FMZ-compatible event/API adapter; refusing to invent OHLCV-only behavior.')
        return runner(self.javascript)
