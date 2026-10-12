"""Deep semantic map of FMZ JavaScript strategy 火币精度.md.

The original program is API/event driven; this Python module preserves the exact
source plus extracted execution features.  Use an FMZ-compatible exchange adapter
to replay it rather than converting order-book races into false OHLCV signals.
"""
SOURCE_FILE = '火币精度.md'
SOURCE_FEATURES = ['var ', '_C(']
SOURCE_FIDELITY_NOTES = ['FMZ JavaScript is event/API driven. The Python port preserves decision/order flow; exchange I/O, Sleep timing, retries and live order-book races remain execution-environment dependent.']
ORIGINAL_JAVASCRIPT = "var _symbols = _C(getSymbols)\nvar _cacheTicker = {}\n\nfunction parseJson(str) {\n    try {\n        return JSON.parse(str)\n    } catch(e) {\n        Log(str + e.message + '#FF0000')\n        return null\n    }\n}\n\nfunction getSymbols() {\n    var ret = parseJson(HttpQuery('https://api.huobi.pro/v1/common/symbols'))\n    if (ret && ret.status === 'ok') {\n        return ret.data\n    } else {\n        return null\n    }\n}\n\nfunction getTicker(ex) {\n    var currency = getCurreny(ex)\n    if (_cacheTicker[currency] && Unix() - _cacheTicker[currency].UpdatedAt < TICKER_EXPIRE_TIME) {\n        return _cacheTicker[currency]\n    }\n    var sym = currency.replace('_', '').toLocaleLowerCase()\n    var ret = parseJson(HttpQuery('https://api.huobi.pro/market/detail/merged?symbol=' + sym))\n    if (ret && ret.status === 'ok') {\n        _cacheTicker[currency] = _.extend({ UpdatedAt: Unix() }, ret.tick)\n        return ret.data\n    } else {\n        return null\n    }\n}\n\nfunction getCurreny(ex) {\n    var currency = null\n    if (typeof(ex) === 'object') {\n        return ex.GetCurrency()\n    } else {\n        return ex\n    }\n}\n\nfunction getCoin(ex) {\n    var currency = getCurreny(ex)\n    var currencyAry = _.map(currency.split('_'), function(sym) { return sym.toLocaleLowerCase() })\n    return _.find(_symbols, function(coin) {\n        return currencyAry[0] === coin['base-currency'] && currencyAry[1] === coin['quote-currency']\n    })\n}\n\n$.getSymbols = getSymbols\n\n$.getAmountPrecision = function (ex) {\n    var coin = getCoin(ex)\n    if (coin) {\n        return coin['amount-precision']\n    }\n    return 0\n}\n\n$.getPricePrecision = function(ex) {\n    var coin = getCoin(ex)\n    if (coin) {\n        return coin['price-precision']\n    }\n    return 0\n}\n\n$.getMinOrderAmount = function(ex, price) {\n    var coin = getCoin(ex)\n    if (coin) {\n        price = price || _C(getTicker, ex).close\n        return +(new Decimal(coin['min-order-value']).mul(1.1).div(price).toFixed($.getAmountPrecision(ex), Decimal.ROUND_CEIL))\n    }\n    return 0\n}\n\n$.getMaxOrderAmount = function(ex) {\n    var coin = getCoin(ex)\n    if (coin) {\n        return coin['max-order-amt']\n    }\n    return 0\n}\n\n$.getValuePrecision = function(ex) {\n    var coin = getCoin(ex)\n    if (coin) {\n        return coin['value-precision']\n    }\n    return 0\n}\n\n$.getMinValue = function(ex) {\n    var coin = getCoin(ex)\n    if (coin) {\n        return coin['min-order-value']\n    }\n    return 0\n}"

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
