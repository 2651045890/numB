"""Extracted from 马丁变种原始版.md (FMZ Python source).
Original source preserved verbatim below.
"""

'''backtest
start: 2021-05-01 00:00:00
end: 2021-05-14 00:00:00
period: 1m
basePeriod: 1m
exchanges: [{"eid":"Futures_Binance","currency":"EOS_USDT","balance":1000}]
args: [["zuokong",true],["n",3],["E",0.02]]
'''
def main():
    while True:
        exchange.SetContractType("swap")
        exchange.SetMarginLevel(MarginLevel)
        ticker = _C(exchange.GetTicker)
        account = _C(exchange.GetAccount)
        position = _C(exchange.GetPosition)
        if zuoduo:
            if len(position) == 0:   
                    exchange.SetDirection("buy")
                    exchange.Buy(-1, k, "开多")
            if len(position) > 0:
                if position[0].Type==0:
                    
                    if position[0].Price+Q<ticker["Last"]:
                        exchange.SetDirection("closebuy")
                        exchange.Sell(-1, position[0].Amount) 
                        account = exchange.GetAccount()
                        LogProfit(account["Balance"]) 
                    fx=(E/n)*position[0].Amount  
                    if position[0].Profit<position[0].Margin * -fx :
                        #轮询加仓
                            exchange.SetDirection("buy")
                            exchange.Buy(-1, k)
                            LogProfit(account["Balance"])     
        if zuokong:
            if len(position) == 0:   
                    exchange.SetDirection("sell")
                    exchange.Sell(-1, k, "开空")
            if len(position) > 0:
                if position[0].Type == 1 :
                    fp=Q*position[0].Amount
                    if position[0].Profit > 0.01*fp*ticker["Last"] :
                        exchange.SetDirection("closesell")
                        exchange.Buy(-1, position[0].Amount) 
                        account = exchange.GetAccount()
                        LogProfit(account["Balance"]) 
                    fx=(E/n)*position[0].Amount  
                    if position[0].Profit<position[0].Margin * -fx :
                        #轮询加仓
                            exchange.SetDirection("sell")
                            exchange.Sell(-1, n)
                            LogProfit(account["Balance"])
        
        Sleep(3000)
