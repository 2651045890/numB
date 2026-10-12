"""Deep semantic map of FMZ JavaScript strategy 测试策略交互控件.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '测试策略交互控件.md'
SOURCE_FEATURES = ['var ', 'while ', 'Sleep(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'function main() {\n    var lastCmd = ""\n    while (true) {\n        var cmd = GetCommand()\n        if (cmd) {\n            Log(cmd)\n            lastCmd = cmd\n        }\n        LogStatus(_D(), lastCmd)\n        Sleep(500)\n    }\n}'

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
