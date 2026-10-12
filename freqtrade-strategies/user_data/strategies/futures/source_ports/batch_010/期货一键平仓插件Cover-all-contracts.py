"""Deep semantic map of FMZ JavaScript strategy 期货一键平仓插件Cover-all-contracts.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '期货一键平仓插件Cover-all-contracts.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'Sleep(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = "function main(){\n    while(ture){\n        var pos = exchange.GetPosition()\n        var ticker = exchange.GetTicekr()\n        if(!ticker){return '无法获取ticker'}\n        if(!pos || pos.length == 0 ){return '已无持仓'}\n        for(var i=0;i<pos.length;i++){\n            if(pos[i].Type == PD_LONG){\n                exchange.SetContractType(pos[i].ContractType)\n                exchange.SetDirection('closebuy')\n                exchange.Sell(ticker.Buy, pos[i].Amount - pos[i].FrozenAmount)\n            }\n            if(pos[i].Type == PD_SHORT){\n                exchange.SetContractType(pos[i].ContractType)\n                exchange.SetDirection('closesell')\n                exchange.Buy(ticker.Sell, pos[i].Amount - pos[i].FrozenAmount)\n            }\n        }\n        var orders = exchange.Getorders()\n        Sleep(500)\n        for(var j=0;j<orders.length;j++){\n            if(orders[i].Status == ORDER_STATE_PENDING){\n                exchange.CancelOrder(orders[i].Id)\n            }\n        }\n    }\n}"

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
