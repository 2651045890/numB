"""Deep semantic map of FMZ JavaScript strategy 每1分钟统计各个平台间的差价by-JackConan.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '每1分钟统计各个平台间的差价by-JackConan.md'
SOURCE_FEATURES = ['var ', 'for ', 'exchanges[', 'Sleep(', 'GetTicker']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.', 'Uses multiple exchange objects; per-symbol logic can be backtested independently, but portfolio scheduling/order concurrency requires an orchestrator.']
ORIGINAL_JAVASCRIPT = 'var maxSpace = 0;\n\nfunction adjustFloat(v) {\n    return Math.floor(v*1000)/1000;\n}\n\nfunction printCurPrice() {\n    for (var i = 0; i < exchanges.length; i++) {\n        Log(exchanges[i].GetName(),\'=\',exchanges[i].GetTicker());\n    }\n}\n\nfunction onTick() {\n    // TODO something.\n    var smallPrice = 99999;\n    var bigPrice = 0;\n    var curPrice = 0;\n    var curSpace = 0;\n    \n    for (var i = 0; i < exchanges.length; i++) {\n        curPrice = exchanges[i].GetTicker().Last;\n        if (curPrice < smallPrice){\n            smallPrice = curPrice;\n        }\n        if (curPrice > bigPrice){\n            bigPrice = curPrice;\n        }\n        curSpace = bigPrice - smallPrice;\n    }\n    \n    if (curSpace > maxSpace){\n        maxSpace = curSpace;\n        //打印各交易所当前的市场行情；\n        printCurPrice();\n        Log(\'有新高差价:\', adjustFloat(maxSpace),\'高价:\', bigPrice,\'低价:\', smallPrice, \'发生时间 →_→\');\n    }\n    Log(\'当前差价:\', adjustFloat(curSpace),\'高价:\', bigPrice,\'低价:\', smallPrice,\'最高差价:\', adjustFloat(maxSpace));\n}\n\nfunction main() {\n    if (exchanges.length < 2) {\n        Log("交易所数量最少得两个才能完成统计");\n        return;\n    }\n    while(true) {\n        onTick();\n        Sleep(60000);\n    }\n}'

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
