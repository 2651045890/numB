"""Source-preserving Python port envelope for 融资融币统计.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = 'function getLoanInfo(exchange, type) {\n    var loanInfo;\n    var dueAmount;\n    if (exchange.GetName() == "OKCoin") { \n        loanInfo = exchange.IO("api", "borrows_info", "symbol=cny");\n        if (type == "btc") {\n            dueAmount = loanInfo.borrow_btc + loanInfo.interest_btc;\n        }\n        else if (type == "ltc") {\n            dueAmount = loanInfo.borrow_ltc + loanInfo.interest_ltc;\n        }   \n        else if (type == "cny") {\n            dueAmount = loanInfo.borrow_cny + loanInfo.interest_cny;\n        }\n    }\n    else if (exchange.GetName() == "Huobi") {\n        loanInfo = exchange.IO("api", "get_loans", "market=cny");\n        dueAmount = 0;\n            for (var i = 0; i < loanInfo.length; i++) {\n                if (type == "cny" && loanInfo[i].type == 1 || type == "btc" && loanInfo[i].type == 2 || type == "ltc" && loanInfo[i].type == 3) {\n                    dueAmount += (Number(loanInfo[i].loan_amount) - Number(loanInfo[i].repayment_amount) + Number(loanInfo[i].interest_nopay) + Number(loanInfo[i].interest_payed));\n                }\n            }\n    }\n    else \n        throw "暂不支持交易所: " + exchange.GetName();\n    return dueAmount;\n}\n\nfunction main() {\n    for (var i = 0; i < exchanges.length; i++)\n        Log(exchanges[i].GetName(),\n            "未归还CNY:", getLoanInfo(exchanges[i], "cny"),\n            "未归还BTC:", getLoanInfo(exchanges[i], "btc"),\n            "未归还LTC:", getLoanInfo(exchanges[i], "ltc")\n           );\n}'
SOURCE_FILE = '融资融币统计.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
