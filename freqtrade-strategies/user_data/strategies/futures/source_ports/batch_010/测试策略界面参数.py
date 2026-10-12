"""Deep semantic map of FMZ JavaScript strategy 测试策略界面参数.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '测试策略界面参数.md'
SOURCE_FEATURES = []
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2023-06-21 00:00:00\nend: 2024-06-26 00:00:00\nperiod: 1d\nbasePeriod: 1h\nexchanges: [{"eid":"Futures_OKX","currency":"BTC_USD"}]\n*/\n\nfunction main() {\n    Log("---------------------------开始测试数字类型参数---------------------------")\n    Log("变量pNum1:", pNum1, ", 变量值类型：", typeof(pNum1))\n    Log("变量pNum2:", pNum2, ", 变量值类型：", typeof(pNum2))\n    Log("变量pNum3:", pNum3, ", 变量值类型：", typeof(pNum3))\n    Log("变量pNum4:", pNum4, ", 变量值类型：", typeof(pNum4))\n    \n    Log("---------------------------开始测试布尔类型参数---------------------------")\n    Log("变量pBool1:", pBool1, ", 变量值类型：", typeof(pBool1))\n    Log("变量pBool2:", pBool2, ", 变量值类型：", typeof(pBool2))\n\n    Log("---------------------------开始测试字符串类型参数---------------------------")\n    Log("变量pStr1:", pStr1, ", 变量值类型：", typeof(pStr1))\n    Log("变量pStr2:", pStr2, ", 变量值类型：", typeof(pStr2))\n    Log("变量pStr3:", pStr3, ", 变量值类型：", typeof(pStr3))\n    Log("变量pStr4:", pStr4, ", 变量值类型：", typeof(pStr4))\n\n    Log("---------------------------开始测试下拉框类型参数---------------------------")\n    Log("变量pCombox1:", pCombox1, ", 变量值类型：", typeof(pCombox1))\n    Log("变量pCombox2:", pCombox2, ", 变量值类型：", typeof(pCombox2))\n    Log("变量pCombox3:", pCombox3, ", 变量值类型：", typeof(pCombox3))\n\n    Log("---------------------------开始测试加密串类型参数---------------------------")\n    Log("变量pSecretStr1:", pSecretStr1, ", 变量值类型：", typeof(pSecretStr1))\n}'

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
