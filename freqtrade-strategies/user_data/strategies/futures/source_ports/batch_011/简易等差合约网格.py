"""Extracted from 简易等差合约网格.md (FMZ Python source). Original source preserved below.
"""

'''backtest
start: 2021-01-01 00:00:00
end: 2021-11-17 00:00:00
period: 1m
basePeriod: 1m
exchanges: [{"eid":"Futures_Binance","currency":"BTC_USDT","balance":2500}]
args: [["H",30],["n1",0.001],["grid",300],["xia",50000]]
'''

def CancelPendingOrders():
    orders = _C(exchanges[0].GetOrders)
    if len(orders)>0:
        for j in range(len(orders)):
            exchanges[0].CancelOrder(orders[j].Id, orders[j])
            j=j+1

def main():
    exchange.SetContractType('swap')
    exchange.SetMarginLevel(M)
    currency=exchange.GetCurrency()
    if _G('buyp') and _G('sellp'):
        buyp=_G('buyp')
        sellp=_G('sellp')
        Log('读取网格价格')
    else:
        ticker=exchange.GetTicker()
        buyp=ticker["Last"]-grid
        sellp=ticker["Last"]+grid
        _G('buyp',buyp)
        _G('sellp',sellp)
        Log('网格数据初始化')
    while True:
            account=exchange.GetAccount()
            ticker=exchange.GetTicker()
            position=exchange.GetPosition()
            orders=exchange.GetOrders()
            if len(position)==0:
                if ticker["Last"]>shang:
                    exchange.SetDirection('sell')
                    exchange.Sell(-1,n1*H)
                    Log(currency,'到达开空区域,买入空头底仓')
                    
                else:
                    exchange.SetDirection('buy')
                    exchange.Buy(-1,n1*H)
                    Log(currency,'到达开多区域,买入多头底仓')
            if len(position)==1:
                if position[0]["Type"]==1:
                    if ticker["Last"]<xia:
                        Log(currency,'空单全部止盈反手')
                        exchange.SetDirection('closesell')
                        exchange.Buy(-1,position[0].Amount)
                    else:
                        orders=exchange.GetOrders()
                        if len(orders)==0:
                            exchange.SetDirection('sell')
                            exchange.Sell(sellp,n1)
                            exchange.SetDirection('closesell')
                            exchange.Buy(buyp,n1)
                        if len(orders)==1:
                            if orders[0]["Type"]==1: #止盈成交
                                Log(currency,'网格减仓,当前份数:',position[0].Amount)
                                CancelPendingOrders()
                                buyp=buyp-grid
                                sellp=sellp-grid
                                LogProfit(account["Balance"])
                            if orders[0]["Type"]==0:
                                Log(currency,'网格加仓,当前份数:',position[0].Amount)
                                CancelPendingOrders()
                                buyp=buyp+grid
                                sellp=sellp+grid
                                LogProfit(account["Balance"])
            
                if position[0]["Type"]==0:
                    if ticker["Last"]>float(shang):
                        Log(currency,'多单全部止盈反手')
                        exchange.SetDirection('closebuy')
                        exchange.Sell(-1,position[0].Amount)
                    else:
                        orders=exchange.GetOrders()
                        if len(orders)==0:
                            exchange.SetDirection('buy')
                            exchange.Buy(buyp,n1)
                            exchange.SetDirection('closebuy')
                            exchange.Sell(sellp,n1)
                        if len(orders)==1:
                            if orders[0]["Type"]==0: #止盈成交
                                Log(currency,'网格减仓,当前份数:',position[0].Amount)
                                CancelPendingOrders()
                                buyp=buyp+grid
                                sellp=sellp+grid
                                LogProfit(account["Balance"])
                            if orders[0]["Type"]==1:
                                Log(currency,'网格加仓,当前份数:',position[0].Amount)
                                CancelPendingOrders()
                                buyp=buyp-grid
                                sellp=sellp-grid
                                LogProfit(account["Balance"])
