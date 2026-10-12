"""Extracted from 获取持仓均价你用对了吗.md (FMZ Python source). Original source preserved below.
"""

def  getAvgPrice(position):
    if hasattr(position[0],'Info') and hasattr(position[0].Info,'cost_open'):# Huobi
        return position[0].Info.cost_open
    elif hasattr(position[0],'Info') and  hasattr(position[0].Info,'avg_cost'):#OKex
        return position[0].Info.avg_cost
    elif hasattr(position[0],'Info') and  hasattr(position[0].Info,'entryPrice'):#binance
        return position[0].Info.entryPrice
    else:
        return position[0]["Price"] 

def main():
    Log(exchange.GetAccount())
    position = exchanges[0].GetPosition()
    if len(position)>0:
        avgPrice = getAvgPrice(position)
        Log(avgPrice)
