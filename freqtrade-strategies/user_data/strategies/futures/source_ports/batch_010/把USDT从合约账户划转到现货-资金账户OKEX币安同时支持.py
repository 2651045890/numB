"""Deep semantic map of FMZ JavaScript strategy 把USDT从合约账户划转到现货-资金账户OKEX币安同时支持.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '把USDT从合约账户划转到现货-资金账户OKEX币安同时支持.md'
SOURCE_FEATURES = ['var ', 'exchange.']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'function main() {\n    transferToMain(100);\n}\n\n// 从U本位合约钱包向现货钱包划转指定数量的USDT\nfunction transferToMain(amount){\n    var ret = null;\n    if (isOKexExchange()) {\n        let param = "ccy=USDT" + "&from=18" + "&amt=" + amount.toString() + "&to=6";\n        ret = exchange.IO("api", "POST", "/api/v5/asset/transfer", param);\n    } else if (isBinanceExchange()) {\n        let time = UnixNano() / 1000000;\n        let param = "type=UMFUTURE_MAIN" + "&asset=USDT" + "&amount=" + amount.toString() + "&timestamp=" + time.toString();\n        exchange.SetBase(\'https://api.binance.com\');\n        ret = exchange.IO("api", "POST", "/sapi/v1/asset/transfer", param);\n        exchange.SetBase(\'https://fapi.binance.com\');\n    } else {\n        Log("资金划转失败，不支持的交易所！");\n    }\n    if (ret) {\n        Log("已经从合约划转到现货账户: ", amount, " USDT");\n        return true;\n    } else {\n        Log("资金划转失败！");\n        return false;\n    }\n}\n\n// 判断是否币安交易所\nfunction isBinanceExchange() {\n    if (exchange.GetName() == "Futures_Binance") {\n        return true;\n    }\n    return false;\n}\n\n// 判断是否OKEX交易所\nfunction isOKexExchange() {\n    if (exchange.GetName() == "Futures_OKCoin") {\n        return true;\n    }\n    return false;\n}'

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
