"""Source-preserving Python port envelope for 通过HttpQuery直接获取币安K线数据.md.

Original language: javascript.  This strategy is not PineScript and uses FMZ
exchange/event APIs or MyLanguage semantics.  It cannot be truthfully mapped to
the batch_001 candle PinePortBase engine without an event/order-book adapter.
The exact source is retained in ORIGINAL_SOURCE for a dedicated translation.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '// GetRecords_Binance_Swap("5m", "ETHUSDT")\n// GetRecords_Binance_Swap("4h", "ETHUSDT")\nfunction GetRecords_Binance_Swap(period, symbol) {\n    //  var url = "https://api.binance.com/api/v3/klines?symbol=" + symbol + "&interval=" + period    // 现货\n    var url = "https://fapi.binance.com/fapi/v1/klines?symbol=" + symbol + "&interval=" + period       //  U本位永续\n    var ret = HttpQuery(url)\n\n    try {\n        var jsonData = JSON.parse(ret)\n        var records = []\n        for (var i = 0; i < jsonData.length; i++) {\n            records.push({\n                Time: jsonData[i][0],\n                High: Number(jsonData[i][2]),\n                Open: Number(jsonData[i][1]),\n                Low: Number(jsonData[i][3]),\n                Close: Number(jsonData[i][4]),\n                Volume: Number(jsonData[i][5]),\n            });\n        }\n        return records\n    } catch (e) {\n        Log(e)\n    }\n}\n'
SOURCE_FILE = '通过HttpQuery直接获取币安K线数据.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ event/order-book adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
