"""Source-preserving Python port envelope for 费率汇总.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = "\n\nfunction main() {\n    const binanceFundingRate = {\n        type: 'table',\n        title: '币安费率',\n        cols: ['交易对', '指数价', '标记价', '基差', '资金费率', '费率时间'],\n        rows: []\n    };\n\n    const gateFundingRate = {\n        type: 'table',\n        title: 'GateIO费率',\n        cols: ['交易对', '指数价', '标记价', '基差', '资金费率', '费率时间'],\n        rows: []\n    };\n\n    const okexFundingRate = {\n        type: 'table',\n        title: 'OKEX费率',\n        cols: ['交易对', '指数价', '标记价', '基差', '资金费率', '费率时间'],\n        rows: []\n    };\n\n    while (true) {\n        const data = JSON.parse(HttpQuery('https://fapi.binance.com/fapi/v1/premiumIndex'));\n        binanceFundingRate.rows = data.map(({ symbol, lastFundingRate, markPrice, indexPrice, nextFundingTime }) => [\n            symbol,\n            indexPrice,\n            markPrice,\n            _N((+markPrice - indexPrice) / +indexPrice * 100, 4) + '%',\n            _N(lastFundingRate * 100, 4) + '%',\n            _D(nextFundingTime)]);\n\n        const dataGate = JSON.parse(HttpQuery('https://api.gateio.ws/api/v4/futures/usdt/contracts'));\n        gateFundingRate.rows = dataGate.map(({ name, funding_rate, mark_price, index_price, funding_next_apply }) => [\n            name,\n            index_price,\n            mark_price,\n            _N((+mark_price - index_price) / +index_price * 100, 4) + '%',\n            _N(funding_rate * 100, 4) + '%',\n            _D(funding_next_apply * 1000)]);\n\n        const instruments = JSON.parse(HttpQuery('https://www.okex.com/api/swap/v3/instruments'));\n        okexFundingRate.rows = [];\n        instruments.map(a => a.instrument_id).forEach(instrument_id => {\n            const item = JSON.parse(HttpQuery(`https://www.okex.com/api/swap/v3/instruments/${instrument_id}/funding_time`))\n            okexFundingRate.rows.push([instrument_id, '-', '-', '-', _N(item.funding_rate * 100, 4) + '%', _D(new Date(item.funding_time))]);\n        });\n\n        LogStatus('\\n`' + JSON.stringify([binanceFundingRate, gateFundingRate, okexFundingRate]) + '`\\n');\n        Sleep(60000);\n    }\n}"
SOURCE_FILE = '费率汇总.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
