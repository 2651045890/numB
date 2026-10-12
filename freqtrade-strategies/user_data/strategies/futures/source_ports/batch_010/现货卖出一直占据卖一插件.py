"""Deep semantic map of FMZ JavaScript strategy 现货卖出一直占据卖一插件.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '现货卖出一直占据卖一插件.md'
SOURCE_FEATURES = ['var ', 'exchange.', '_C(', 'Sleep(', 'GetTicker', 'GetDepth', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = "function GetPrecision(){\n    var precision = {price:0, amount:0}\n    var depth = exchange.GetDepth()\n    for(var i=0;i<depth.Asks.length;i++){\n        var amountPrecision = depth.Asks[i].Amount.toString().indexOf('.') > -1 ? depth.Asks[i].Amount.toString().split('.')[1].length : 0\n        precision.amount = Math.max(precision.amount,amountPrecision)\n        var pricePrecision = depth.Asks[i].Price.toString().indexOf('.') > -1 ? depth.Asks[i].Price.toString().split('.')[1].length : 0\n        precision.price = Math.max(precision.price,pricePrecision)\n    }\n    return precision\n}\n\nfunction main(){\n    var initAccount = exchange.GetAccount()\n    if(!initAccount){return '无法获取账户信息'}\n    var precision = GetPrecision()\n    var sellPrice = 0\n    var lastId = 0\n    var done = false\n    while(true){\n        var account = _C(exchange.GetAccount)\n        var dealAmount = - account.Stocks + initAccount.Stocks\n        var ticker = _C(exchange.GetTicker)\n        if(SellAmount - dealAmount > 1/Math.pow(10,precision.amount) && ticker.Sell < sellPrice){\n            if(lastId){exchange.CancelOrder(lastId)}\n            var id = exchange.Sell(ticker.Sell, _N(SellAmount - dealAmount,precision.amount))\n            if(id){\n                lastId = id\n            }else{\n                done = true\n            }\n        }\n        if(BuyAmount - dealAmount <= 1/Math.pow(10,precision.amount)){done = true}\n        if(done){\n            var avgCost = (-initAccount.Balance + account.Balance)/dealAmount\n            return 'order is done, avg cost is ' + avgCost  // including fee cost\n        }\n        Sleep(Intervel*1000)\n    }\n}"

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
