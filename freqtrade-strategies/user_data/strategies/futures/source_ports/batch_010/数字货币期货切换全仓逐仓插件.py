"""Deep semantic map of FMZ JavaScript strategy 数字货币期货切换全仓逐仓插件.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '数字货币期货切换全仓逐仓插件.md'
SOURCE_FEATURES = ['var ', 'exchange.']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = 'function main() {\n    var posType = [false, true][type]\n    var name = exchange.GetName()\n    if (name == "Futures_Binance") {\n        exchange.IO("cross", posType)\n    } else if (name == "Futures_HuobiDM") {\n        exchange.IO("cross", posType)    \n    } else if (name == "Futures_Bibox") {\n        exchange.IO("cross", posType)        \n    } else if (name == "Futures_Bitget") {\n        exchange.IO("cross", posType)        \n    } else if (name == "Futures_AOFEX") {\n        exchange.IO("cross", posType)      \n    } else if (name == "Futures_Pionex") {\n        exchange.IO("cross", posType)      \n    } else {\n        throw "not support!"\n    }\n    return name + "切换 cross :" + posType\n}'

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
