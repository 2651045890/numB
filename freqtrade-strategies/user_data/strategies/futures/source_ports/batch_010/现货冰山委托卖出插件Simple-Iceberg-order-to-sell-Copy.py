"""Deep semantic map of FMZ JavaScript strategy 现货冰山委托卖出插件Simple-Iceberg-order-to-sell-Copy.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '现货冰山委托卖出插件Simple-Iceberg-order-to-sell-Copy.md'
SOURCE_FEATURES = ['var ', 'exchange.', '_C(', 'Sleep(', 'GetTicker', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = "function main(){\n    var initAccount = _C(exchange.GetAccount)\n    if (initAccount.Stocks < SELLAMOUNT){\n        throw 'check your account amount to sell'\n    }\n    while(true){\n        var account = _C(exchange.GetAccount)\n        var dealAmount =  initAccount.Stocks - account.Stocks\n        var ticker = _C(exchange.GetTicker)\n        if(SELLAMOUNT - dealAmount >= SELLSIZE){\n            var id = exchange.Sell(ticker.Buy, SELLSIZE)\n            Sleep(INTERVAL*1000)\n            if(id){\n                exchange.CancelOrder(id) // May cause error log when the order is completed, which is all right.\n            }else{\n                throw 'sell error'\n            }\n        }else{\n            account = _C(exchange.GetAccount)\n            var avgCost = (account.Balance - initAccount.Balance)/(initAccount.Stocks - account.Stocks)\n            return 'Iceberg order to sell is done, avg price is ' + avgCost\n            \n        }\n    }\n}"

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
