"""Deep semantic map of FMZ JavaScript strategy 短信通知接口测试.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '短信通知接口测试.md'
SOURCE_FEATURES = []
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = "function main() {\n    if (SMSAPI.length > 10 && SMSAPI.indexOf('http') == 0 && SMSAPI.indexOf('{BODY}') != -1) {\n        Log('发送: ', Msg);\n        HttpQuery(SMSAPI.replace('{BODY}', encodeURIComponent(Msg)));\n        Log('发送完成, 请检测是否收到短信');\n    } else {\n        Log('参数配置错误, 请重新检测短信接口');\n    }\n}"

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
