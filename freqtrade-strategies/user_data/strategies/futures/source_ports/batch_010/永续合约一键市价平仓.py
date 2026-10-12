"""Deep semantic map of FMZ JavaScript strategy 永续合约一键市价平仓.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '永续合约一键市价平仓.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = "function main(){\n        exchange.SetContractType('swap')\n        exchange.SetCurrency('BNB_USDT')\n        Log(exchange.GetPosition())\n        acc = exchange.GetAccount()\n        //Log(exchange.GetAccount().Info)\n        var pos = exchange.GetAccount().Info.positions\n        var positioned = false\n        for(var i=0;i<pos.length;i++){\n            if (pos[i].positionAmt != 0){\n                positioned = true\n                var symbol = pos[i].symbol.replace('USDT','_USDT')\n                //var symbol = pos[i].symbol.replace('BUSD','_BUSD')\n                exchange.SetCurrency(symbol)\n                var amount = parseFloat(pos[i].positionAmt.replace('-',''))\n                if(pos[i].positionSide == 'LONG'){\n                    exchange.SetDirection('closebuy')\n                    exchange.Sell(-1, amount)\n                }\n                if(pos[i].positionSide == 'SHORT'){\n                    exchange.SetDirection('closesell')\n                    exchange.Buy(-1, amount)\n                }\n            }\n        }\n        if(positioned == false){\n            Log('无持仓')\n            return ('无持仓')\n        }\n        else{\n            Log('完成平仓')\n            return ('完成平仓')\n        }\n}"

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
