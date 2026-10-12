"""Deep semantic map of FMZ JavaScript strategy 火币期货币币账户间资金划转范例.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '火币期货币币账户间资金划转范例.md'
SOURCE_FEATURES = ['var ', 'exchange.', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'function main() {\n    // API 接口描述：\n    // https://api.huobi.pro\n    // POST /v1/futures/transfer\n    // params    currency e.g. btc\n    //           amount\n    //           type futures-to-pro\n    \n    Log(exchange.GetAccount())\n    var ret = exchange.IO("api", "POST", "/v1/futures/transfer", "currency=ltc&amount=0.1&type=pro-to-futures")   // 测试的是LTC ， 币币转期货\n    Log("ret", ret)\n    \n    /* ret\n    ret {"status":"ok","data":25669845}\n    */\n}'

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
