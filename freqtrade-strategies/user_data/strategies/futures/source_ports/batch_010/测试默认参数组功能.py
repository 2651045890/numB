"""Deep semantic map of FMZ JavaScript strategy 测试默认参数组功能.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '测试默认参数组功能.md'
SOURCE_FEATURES = ['Sleep(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2017-03-01        \nend: 2017-03-02           \nperiod: 15              \nmode: 1                 \n*/\n\n/*defaults\nnumber : 0\nbool: false\nstring: Hello BotVS！\ncomboBox : 2\n*/\n\nfunction main(){\n    while(true){\n        LogStatus("测试默认参数！");\n        Sleep(1000);\n    }\n}'

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
