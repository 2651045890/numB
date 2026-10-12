"""Deep semantic map of FMZ JavaScript strategy 当周季度差价画图插件.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '当周季度差价画图插件.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'GetRecords']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'var chart = { \n    __isStock: true,    \n    title : { text : \'差价分析图\'},                     \n    xAxis: { type: \'datetime\'},                 \n    yAxis : {                                        \n        title: {text: \'差价\'},                   \n        opposite: false,                             \n    },\n    series : [                    \n        {name : "diff", data : []}, \n\n    ]\n}\nfunction main() {\n    exchange.SetContractType(\'quarter\')\n    var recordsA = exchange.GetRecords(PERIOD_M5)\n    exchange.SetContractType(\'this_week\')\n    var recordsB = exchange.GetRecords(PERIOD_M5)\n    \n    for(var i=0;i<Math.min(recordsA.length,recordsB.length);i++){\n        var diff = recordsA[recordsA.length-Math.min(recordsA.length,recordsB.length)+i].Close - recordsB[recordsB.length-Math.min(recordsA.length,recordsB.length)+i].Close\n        chart.series[0].data.push([recordsA[recordsA.length-Math.min(recordsA.length,recordsB.length)+i].Time, diff])\n    }\n    return chart\n}'

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
