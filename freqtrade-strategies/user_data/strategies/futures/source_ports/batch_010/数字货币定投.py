"""Deep preservation port of original Python strategy 数字货币定投.md."""
ORIGINAL_SOURCE = 'def onTick():\n\t\n\texchange_count = len(exchanges)\n\tfor i in range(exchange_count):\n\t\taccount = exchanges[i].GetAccount()\n\n\t\tmarketName = exchanges[i].GetName()\n\t\tdepth = exchanges[i].GetDepth()\n\t\tLog("Market ",marketName,exchanges[i].GetCurrency(),"Account Balance [",account["Balance"],"] Stocks[",account["Stocks"],"]")\n\t\tif account and depth and account["Balance"] > accountLimitMoney :\n\t\t\tbidPrice = depth["Asks"][0]["Price"] \n\t\t\tif bidPrice <  maxBidPrice :\n\t\t\t\tamount = orderAmount\n\t\t\t\tif amount <= account["Balance"]:\n\t\t\t\t\texchanges[i].Buy(amount)\n\t\t\t\telse:\n\t\t\t\t\tLog("Account Balance is less than bid Amount")\n\t\t\telse:\n\t\t\t\tLog("Bid Price >= maxBidPrice, not process")\n\t\telse:\n\t\t\tLog("Account Balance <= accountLimitMoney")\ndef main() :\n\twhile 1:\n\t\t\n\t\tonTick()\n\t\ttime.sleep(orderTimeInterval)'
SOURCE_FILE = '数字货币定投.md'
SOURCE_FEATURES = ['for ', 'while ', 'exchanges[', 'GetDepth', 'GetAccount']
SOURCE_FIDELITY_NOTES = ['Original source is Python; retained as the canonical implementation with only packaging/syntax-safety changes when needed.']

def get_original_source():
    return ORIGINAL_SOURCE
