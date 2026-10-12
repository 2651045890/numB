"""Deep semantic map of FMZ JavaScript strategy 火币点卡.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '火币点卡.md'
SOURCE_FEATURES = ['var ']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = '$.getHBPoints = function(ex) {\n    try {\n        var accountRet = ex.IO("api", "GET", "/v1/account/accounts")\n        if (accountRet && accountRet.data) {\n            var account = _.findWhere(accountRet.data, {\n                type: \'point\'\n            })\n            if (account && account.id) {\n                var balanceRet = ex.IO("api", "GET", "/v1/account/accounts/" + account.id + "/balance")\n                if (balanceRet && balanceRet.data && balanceRet.data.list) {\n                    var balance = _.reduce(balanceRet.data.list, function(p, n) {\n                        return new Decimal(p).plus(n.balance).toNumber()\n                    }, 0)\n                    return balance\n                }\n            }\n        }\n    } catch (e) {}\n    return null\n}'

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
