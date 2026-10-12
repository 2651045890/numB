"""Source-preserving Python port envelope for 设定比特币价格并微信推送教学-Push-the-price-information-to-telegram.md.

Original language: javascript. This source uses FMZ exchange/event APIs or another
event-driven runtime. It cannot be truthfully represented as a candle-only
PinePortBase strategy without an API/order-book adapter, so the exact source is
retained for a dedicated semantic port instead of inventing behavior.
"""
ORIGINAL_LANGUAGE = 'javascript'
ORIGINAL_SOURCE = '/*\nThis stragegy will sent a message to your telegram when the price is higher or lower than\nthe set price.\nAll stragegy must has a main function as the entrance.\n*/\nfunction main() {\n     //change symbol,will cover the default exchange which was set when start a bot.Currency is a strategy arguments\n    exchange.IO("currency", Currency)   \n    var lastPushTime = 0    //the variable of last push timestamp.\n    while(true){    //run a infinite loop, which is the basic structure\n        var ticker = _C(exchange.GetTicker) // for information about GetTicker, check on https://fmz-docs.readthedocs.io/en/latest/code_Instruction/Market%20API.html#getticker\n        if(ticker.Last > UpPrice || ticker.Last < LowPrice){    //ticker.Last represents the last deal price\n            if(Date.now() - lastPushTime > 300*1000){    //only push once in 5 mins, Date.now() return ms.\n                lastPushTime = Date.now()    //update lastPushTime\n                Log(Currency, \'Price is: \', ticker.Last, \'@\')    //Log the price on the bot\'s page and sent the message. \'@\' in the end means push message\n            }\n        }\n        Log(Currency, \'Price is: \', ticker.Last) //just log the price\n        Sleep(Interval*1000)    //check the last price again after Interval seconds\n    }\n}'
SOURCE_FILE = '设定比特币价格并微信推送教学-Push-the-price-information-to-telegram.md'

class EventDrivenPortRequired(RuntimeError):
    pass

def main(*args, **kwargs):
    raise EventDrivenPortRequired(
        f"{SOURCE_FILE} is {ORIGINAL_LANGUAGE} and requires an FMZ/event-driven adapter; "
        "a fake candle-strategy translation would not be semantically equivalent."
    )
