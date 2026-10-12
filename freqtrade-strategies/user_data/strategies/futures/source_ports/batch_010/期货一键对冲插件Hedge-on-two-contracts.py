"""Deep semantic map of FMZ JavaScript strategy 期货一键对冲插件Hedge-on-two-contracts.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '期货一键对冲插件Hedge-on-two-contracts.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'GetTicker']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = "function main(){\n    exchange.SetContractType(Reverse ? Contract_B : Contract_A)\n    var ticker_A = exchange.GetTicker()\n    if(!ticker_A){return 'Unable to get quotes'}\n    exchange.SetDirection('buy')\n    var id_A = exchange.Buy(ticker_A.Sell+Slip, Amount)\n    exchange.SetContractType(Reverse ? Contract_B : Contract_A)\n    var ticker_B = exchange.GetTicker()\n    if(!ticker_B){return 'Unable to get quotes'}\n    exchange.SetDirection('sell')\n    var id_B = exchange.Sell(ticker_B.Buy-Slip, Amount)\n    if(id_A){\n        exchange.SetContractType(Reverse ? Contract_B : Contract_A)\n        exchange.CancelOrder(id_A)\n    }\n    if(id_B){\n        exchange.SetContractType(Reverse ? Contract_B : Contract_A)\n        exchange.CancelOrder(id_B)\n    }\n    return 'Position: ' + JSON.stringify(exchange.GetPosition())\n}"

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
