"""Source-preserving Python port envelope for 账户余额变动邮箱提醒-支持添加多个交易所.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '\nfunction Notify(msg) {\n    var ret = Mail(SMTPServer, SMTPUser, SMTPPass, SendMode == 0 ? SMTPUser : DstMail , msg, "余额变动 " + msg);\n    if (ret) {\n        Log("邮件通知成功");\n    } else {\n        Log("邮件通知失败");\n    }\n    Log(ret ? "邮件发送成功" : "邮件发送失败");\n    return ret;\n}\n\nfunction GetAccount(print) {\n    var all = {\n        Balance : 0,\n        Stocks  : 0,\n    };\n    var currency = exchange.GetCurrency();\n    for (var i = 0; i < exchanges.length; i++) {\n        if (exchanges[i].GetCurrency() != currency) {\n            throw "币种不相同";\n        }\n        var account;\n        while (!(account = exchanges[i].GetAccount())) {\n            Sleep(1000);\n        }\n        all.Stocks += (account.Stocks + account.FrozenStocks);\n        all.Balance += (account.Balance + account.FrozenBalance);\n        if (typeof(print) != \'undefined\' && print) {\n            Log(exchanges[i].GetName(), "钱: ", (account.Balance + account.FrozenBalance), "币: ", (account.Stocks + account.FrozenStocks));\n        }\n    }\n\n    return all;\n}\n\nfunction main() {\n    // Disable rate auto convert\n    exchange.SetRate(1);\n    if (Version() < 2.7) {\n        throw "只支持2.7或以上版本";\n    }\n    var preAccount = GetAccount(true);\n    if (!Notify("策略启成功, 总钱: " + preAccount.Balance + ", 币: " + preAccount.Stocks)) {\n        throw "Exit";\n    }\n    Log("初始信息: ", "总钱:", preAccount.Balance, "总币:", preAccount.Stocks);\n    var alertAlrelady = false;\n    while (true) {\n        Sleep(LoopInterval * 1000);\n        var account = GetAccount();\n        if (AlertMode == 2) {\n            if ((MinCoin > 0 && account.Stocks < MinCoin) || (MinCNY > 0 && account.Balance < MinCNY)) {\n                if (!alertAlrelady) {\n                    Log(account);\n                    Notify(exchange.GetName() + "资金过少 总钱: " + account.Balance + ", 币: " + account.Stocks);\n                    alertAlrelady = true;\n                }\n            } else {\n                alertAlrelady = false;\n            }\n        } else if (account.Stocks != preAccount.Stocks || account.Balance != preAccount.Balance) {\n            if (AlertMode == 0 || (MaxDiffCoin > 0 && Math.abs(account.Stocks - preAccount.Stocks) >= MaxDiffCoin) || (MaxDiffCNY > 0 && Math.abs(account.Balance - preAccount.Balance) >= MaxDiffCNY)) {\n                Log(account);\n                preAccount = account;\n                Notify(exchange.GetName() + "账户变动为 总钱: " + account.Balance + ", 币: " + account.Stocks);\n            }\n        }\n    }\n}'
SOURCE_FILE = '账户余额变动邮箱提醒-支持添加多个交易所.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
