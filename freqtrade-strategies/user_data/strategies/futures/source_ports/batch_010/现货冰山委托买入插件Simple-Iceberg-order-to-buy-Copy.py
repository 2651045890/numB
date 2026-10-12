"""Semantic Python port of the FMZ spot iceberg-buy plugin.

The function repeatedly posts BUYSIZE at the current ask, waits INTERVAL, then
cancels any remainder until the cumulative acquired amount is within one slice
of BUYAMOUNT.  It then reports average cash cost exactly as the JavaScript does.
"""
from typing import Protocol, Any
import time
class Exchange(Protocol):
    def GetAccount(self) -> Any: ...
    def GetTicker(self) -> Any: ...
    def Buy(self, price: float, amount: float): ...
    def CancelOrder(self, order_id): ...

def iceberg_buy(exchange: Exchange, buy_amount: float, buy_size: float, interval: float, sleep=time.sleep) -> str:
    init_account=exchange.GetAccount()
    while True:
        account=exchange.GetAccount(); deal_amount=account.Stocks-init_account.Stocks; ticker=exchange.GetTicker()
        if buy_amount-deal_amount>=buy_size:
            order_id=exchange.Buy(ticker.Sell,buy_size); sleep(interval)
            if order_id: exchange.CancelOrder(order_id)
            else: raise RuntimeError('buy error')
        else:
            account=exchange.GetAccount(); acquired=account.Stocks-init_account.Stocks
            avg_cost=(init_account.Balance-account.Balance)/acquired
            return f'Iceberg order to buy is done, avg cost is {avg_cost}'
