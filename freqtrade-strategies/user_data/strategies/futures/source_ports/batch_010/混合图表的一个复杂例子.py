"""Deep semantic map of FMZ JavaScript strategy 混合图表的一个复杂例子.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '混合图表的一个复杂例子.md'
SOURCE_FEATURES = ['var ', 'while ', 'exchange.', 'GetTicker']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2020-03-11 00:00:00\nend: 2020-04-09 23:59:00\nperiod: 1d\nexchanges: [{"eid":"Bitfinex","currency":"BTC_USD"}]\n*/\n\nvar chartCfg = {\n    subtitle: {\n        text: "subtitle",\n    },\n    yAxis: [{\n        height: "40%",\n        lineWidth: 2,\n        title: {\n            text: \'PnL\',\n        },\n        tickPixelInterval: 20,\n        minorGridLineWidth: 1,\n        minorTickWidth: 0,\n        opposite: true,\n        labels: {\n            align: "right",\n            x: -3,\n        }\n    }, {\n        title: {\n            text: \'Profit\',\n        },\n        top: "42%",\n        height: "18%",\n        offset: 0,\n        lineWidth: 2\n    }, {\n        title: {\n            text: \'Vol\',\n        },\n        top: \'62%\',\n        height: \'18%\',\n        offset: 0,\n        lineWidth: 2\n    }, {\n        title: {\n            text: \'Asset\',\n        },\n        top: \'82%\',\n        height: \'18%\',\n        offset: 0,\n        lineWidth: 2\n    }],\n    series: [{\n        name: \'PnL\',\n        data: [],\n        id: \'primary\',\n        tooltip: {\n            xDateFormat: \'%Y-%m-%d %H:%M:%S\'\n        },\n        yAxis: 0\n    }, {\n        type: \'column\',\n        lineWidth: 2,\n        name: \'Profit\',\n        data: [],\n        yAxis: 1,\n    }, {\n        type: \'column\',\n        name: \'Trade\',\n        data: [],\n        yAxis: 2\n    }, {\n        type: \'area\',\n        step: true,\n        lineWidth: 0,\n        name: \'Long\',\n        data: [],\n        yAxis: 2\n    }, {\n        type: \'area\',\n        step: true,\n        lineWidth: 0,\n        name: \'Short\',\n        data: [],\n        yAxis: 2\n    }, {\n        type: \'line\',\n        step: true,\n        color: \'#5b4b00\',\n        name: \'Asset\',\n        data: [],\n        yAxis: 3\n    }, {\n        type: \'pie\',\n        innerSize: \'70%\',\n        name: \'Random\',\n        data: [],\n        center: [\'3%\', \'6%\'],\n        size: \'15%\',\n        dataLabels: {\n            enabled: false\n        },\n        startAngle: -90,\n        endAngle: 90,\n    }],\n};\n\nfunction main() {\n    let c = Chart(chartCfg);\n    let preTicker = null;\n    while (true) {\n        let t = exchange.GetTicker();\n        \n        c.add(0, [t.Time, t.Last]); // PnL\n        c.add(1, [t.Time, preTicker ? t.Last - preTicker.Last : 0]); // profit\n        let r = Math.random();\n        var pos = parseInt(t.Time/86400);\n        c.add(2, [t.Time, pos/2]); // Vol\n        c.add(3, [t.Time, r > 0.8 ? pos : null]); // Long\n        c.add(4, [t.Time, r < 0.8 ? -pos : null]); // Short\n        c.add(5, [t.Time, Math.random() * 100]); // Asset\n        // update pie\n        chartCfg.series[chartCfg.series.length-1].data = [\n            ["A", Math.random()*100],\n            ["B", Math.random()*100],\n         ];\n        c.update(chartCfg)\n        preTicker = t;\n    }\n}'

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
