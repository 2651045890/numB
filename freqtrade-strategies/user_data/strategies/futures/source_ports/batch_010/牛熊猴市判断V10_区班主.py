"""Deep semantic map of FMZ JavaScript strategy 牛熊猴市判断V10_区班主.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '牛熊猴市判断V10_区班主.md'
SOURCE_FEATURES = ['var ', 'while ', 'exchange.', 'Sleep(', 'GetRecords']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '/*backtest\nstart: 2019-01-01 00:00:00\nend: 2019-10-10 00:00:00\nperiod: 1d\nexchanges: [{"eid":"Bitfinex","currency":"BTC_USD"}]\n*/\n//通过快慢周期的高低点判断当前处于什么市场\n//注册币乎后https://m.bihu.com/signup?i=1ewtKO&s=4&c=4\n//搜索 物联网区块链 可以联系到作者区班主\nfunction main() {\n    var dhigh;\n    var dlow;\n    var mhigh;\n    var mlow;\n    var status_name=["猴市","大牛","小牛","大熊","小熊"];  //定义并赋值\n    var before_status=0;\n    var now_status=0;\n    while (true) {\n        var drecords = exchange.GetRecords(PERIOD_D1);\n        var mrecords = exchange.GetRecords(PERIOD_M30);\n        //日线5天内的高低点(不包含当前Bar)\n        dhigh=TA.Highest(drecords, dnum, \'High\');\n        dlow=TA.Lowest(drecords, dnum, \'Low\');\n       \n        //30分钟线10个周期内的高低点(不包含当前Bar)\n        mhigh=TA.Highest(mrecords, mnum, \'High\');\n        mlow=TA.Lowest(mrecords, mnum, \'Low\');\n        \n        if(mlow>dhigh){ //分钟低点突破日高点，大牛开始\n            now_status=1;\n            //Log("大牛");\n        }else if(mhigh>dhigh&&mlow<=dhigh){ //分钟高点突破日高点，但是分钟低点还没突破日高点，小牛开始\n            now_status=2;\n            //Log("小牛");\n        }else if(mhigh<dlow){  //分钟低点跌破日低点，大熊开始\n            now_status=3;\n            //Log("大熊");\n        }else if(mlow<dlow&&mhigh>dlow){  //分钟低点跌破日低点，但是分钟高点还没跌破日低点，小熊开始\n            now_status=4;\n            //Log("小熊");\n        }else{  //没有方向，猴市\n            now_status=0;\n            //Log("猴市");\n        }\n        if(now_status!=before_status){\n            Log("日线高点",dhigh," 日线低点",dlow,"30分钟线高点",mhigh," 30分钟线低点",mlow);\n            Log(status_name[before_status],"转",status_name[now_status]);\n            before_status=now_status;\n        }\n        Sleep(Interval*1000);\n    }\n}'

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
