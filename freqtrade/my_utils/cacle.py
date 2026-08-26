def percent_change(old_price, new_price):
    if old_price == 0:
        return float('inf')  # 或者按你需求设定为 None／0
    return (new_price - old_price) / old_price * 100

# 用法示例：
# 比特币大概要-0.6
old = 100600
new = 100000

old = 168
new = 150
print(percent_change(old, new)) 

# 1. 计算某个产品一个价格到另一个价格的收益。

# 2025-11-13 00:13:29 买入了 2.41202300 SQL   手续费 -0.00241202  账户余额 2.40961193

# 
