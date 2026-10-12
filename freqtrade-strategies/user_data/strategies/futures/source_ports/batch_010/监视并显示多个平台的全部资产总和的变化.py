"""Deep semantic map of FMZ JavaScript strategy 监视并显示多个平台的全部资产总和的变化.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '监视并显示多个平台的全部资产总和的变化.md'
SOURCE_FEATURES = ['var ', 'for ', 'while ', 'exchanges[', 'Sleep(', 'GetTicker', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.', 'Uses ticker/depth data; OHLCV-only backtests cannot reproduce microstructure fills exactly.', 'Uses multiple exchange objects; per-symbol logic can be backtested independently, but portfolio scheduling/order concurrency requires an orchestrator.']
ORIGINAL_JAVASCRIPT = 'var LastState = null;\n\nfunction adjustFloat(v) {\n    return Math.floor(v*1000)/1000;\n}\n\nfunction getExchangesState() {\n    var isUpdate = false;\n    var allBalance = 0;\n    var allNetStocks = 0;\n    var Cache = [];\n    var CurrencyCache = [];\n    for (var i = 0; i < exchanges.length; i++) {\n        var account = null;\n        var ticker = null;\n        while (!(account = exchanges[i].GetAccount())) {\n            Sleep(Interval);\n        }\n        while (!(ticker = exchanges[i].GetTicker())) {\n            Sleep(Interval);\n        }        \n        var name = typeof(exchanges[i].GetLabel) == \'undefined\' ? exchanges[i].GetName() : exchanges[i].GetLabel();\n        var currency = exchanges[i].GetCurrency();\n        if (typeof(CurrencyCache[currency]) == \'undefined\') {\n            CurrencyCache[currency] = 0;\n        }\n        CurrencyCache[currency] = adjustFloat(CurrencyCache[currency] + account.Stocks + account.FrozenStocks);\n        if (typeof(Cache[name]) == \'undefined\') {\n            Cache[name] = true;\n            allBalance += account.Balance + account.FrozenBalance;\n        }\n        allNetStocks += (account.Stocks + account.FrozenStocks) * ticker.Last;\n    }\n    var update = false;\n    var str = "";\n    for (var currency in CurrencyCache) {\n        str += \' \'+currency + \': \' + CurrencyCache[currency];\n        if (LastState != null) {\n            if (LastState.CurrencyCache[currency] != CurrencyCache[currency]) {\n                update = true;\n            }\n        }\n    }\n    allBalance = adjustFloat(allBalance);\n    if (LastState != null) {\n        if (LastState.allBalance != allBalance) {\n            update = true;\n        }\n    }\n    \n    return {allStocks: str, Net: adjustFloat(allNetStocks + allBalance), CurrencyCache: CurrencyCache, allBalance: allBalance, update: (LastState == null) || update};\n}\n\nfunction main() {\n    Log("所有平台的钱和币将换算成净资产显示到收益曲线里");\n    while (true) {\n        var state = getExchangesState();\n        if (state.update) {\n            LastState = state;\n            Log(\'总钱: \', state.allBalance, \'总币: \', state.allStocks);\n            LogProfit(state.Net);\n        }\n        Sleep(Math.max(TickInterval, 100));\n    }\n}'

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
