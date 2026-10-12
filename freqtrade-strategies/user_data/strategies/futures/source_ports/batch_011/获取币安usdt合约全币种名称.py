"""Source-preserving Python port envelope for 获取币安usdt合约全币种名称.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function unique (str) {\n\tvar arr = str.split(\',\');\n\treturn Array.from(new Set(arr)).join(\',\')\n}\n\nfunction main() {\n    var exchange_info = JSON.parse(HttpQuery(\'https://fapi.binance.com/fapi/v1/exchangeInfo\'));\n    var str = \'\';\n    exchange_info.symbols.forEach(function(exitem, index) {\n        if (exitem.symbol.indexOf(\'USDT\') == -1) {return}\n        if (exitem.symbol.indexOf(\'BTCST\') !== -1) {return}\n        if (exitem.symbol.indexOf(\'BTCDOM\') !== -1) {return}\n        var content = \',\';\n        if (index == exchange_info.symbols.length - 1) {\n            content = \'\';\n        }\n        str += exitem.baseAsset + content;\n    });\n\tLog(\'全合约币种数量：\', unique(str).split(\',\').length)\n    Log(\'全合约币种名称：\',unique(str))\n    // return leverageBracket;\n\n    let leverageBracket = exchange.IO("api", "GET", "/fapi/v1/leverageBracket", "timestamp=" + new Date().getTime())\n    let newList = leverageBracket.map((item) => {\n        return {\n            symbol: item.symbol,\n            leverage: item.brackets[0].initialLeverage\n        }\n    })\n    let selectLeverage = 25;\n    newList = newList.filter((item) => {\n        return item.leverage >= selectLeverage;\n    })\n    Log(\'筛选币数量：\' , newList.length);\n    let str2 = \'\'\n\n    newList.forEach(function(exitem, index) {\n        if (exitem.symbol.indexOf(\'USDT\') == -1) {return}\n        if (exitem.symbol.indexOf(\'BTCST\') !== -1) {return}\n        if (exitem.symbol.indexOf(\'BTCDOM\') !== -1) {return}\n        var content = \',\';\n        if (index == newList.length - 1) {\n            content = \'\';\n        }\n        str2 += exitem.baseAsset + content;\n    });\n    Log(\'筛选币名称：\', str);\n}\n'
SOURCE_FILE = '获取币安usdt合约全币种名称.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
