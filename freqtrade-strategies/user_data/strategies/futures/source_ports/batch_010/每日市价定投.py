"""Deep semantic map of FMZ JavaScript strategy 每日市价定投.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '每日市价定投.md'
SOURCE_FEATURES = ['var ', 'while ', 'exchange.', 'Sleep(', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'function main() {\n   Log(exchange.GetAccount());\n\n   \n   //最近一次投资的日期\n   var lastInvestDate = \'\';\n\n   while (true) {\n       //每次轮询，间隔时间为60秒\n       Sleep(60 * 1000);\n\n       //如果当前日期和最近一次投资日期相同，说明当天已经投过了，跳过\n       var now = new Date();\n       var date = now.toISOString().slice(0,10);\n       if (date == lastInvestDate) {\n           continue;\n       }\n\n       lastInvestDate = date;\n       Log("日期: " + date);\n\n    \n       exchange.Buy(-1, singleInvestAmount);\n   }\n}'

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
