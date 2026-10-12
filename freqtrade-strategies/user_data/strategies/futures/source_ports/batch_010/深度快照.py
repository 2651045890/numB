"""Deep semantic map of FMZ JavaScript strategy 深度快照.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '深度快照.md'
SOURCE_FEATURES = ['var ', 'for ', 'exchange.', 'GetDepth']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = "function main() {\n    var tbl = { \n        type: 'table', \n        title: '深度快照 @ ' + _D(), \n        cols: ['#', 'Amount', 'Ask', 'Bid', 'Amount'], \n        rows: []\n    };\n    var d = exchange.GetDepth();\n    for (var i = 0; i < Math.min(Math.min(d.Asks.length, d.Bids.length), 15); i++) {\n        tbl.rows.push([i, d.Asks[i].Amount, d.Asks[i].Price+'#ff0000', d.Bids[i].Price+'#0000ff', d.Bids[i].Amount]);\n    }\n    return tbl;\n}"

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
