"""
# 1) ccxt 直测（带代理）
import ccxt
ex = ccxt.okx({
    "timeout": 30000,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
    "proxies": {
        "http":  "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897",
    },
    # 遇到 www 子域不稳可加：
    # "hostname": "okx.com",
})
# 出现下面内容，表示通过....
# ping: 1760448836167
# markets: 2210
print("ping:", ex.fetch_time())      # 轻量心跳
ex.load_markets()
print("markets:", len(ex.markets))

# 私有接口要带 key/secret/passphrase 才能用：
# balance = ex.fetch_balance()
# print(balance.get("USDT", {}))
"""

# curl -I --max-time 8 -x http://127.0.0.1:7890 https://www.okx.com/api/v5/public/time

import ccxt

# 模拟盘和实盘不能混用
key = "358f2c93-b394-4551-a163-f802c37a5d4c"
secret = "FF6C67C33EEDB5691B781A85F4421D00"
password ="Hu265104$"
api_key = key
secret  = secret
passph  = password

ex = ccxt.okx({
    "apiKey":    api_key,
    "secret":    secret,
    "password":  passph,   # 注意：这里的 password 就是 OKX 的 Passphrase
    "timeout": 30000,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
    "proxies": {
        "http":  "http://127.0.0.1:7897",
        "https": "http://127.0.0.1:7897",
    },
})

# 【可选】模拟盘（Demo Trading）
ex.set_sandbox_mode(True)  # ccxt 会为 OKX 自动加 x-simulated-trading 头
# 或者手动：
# ex.headers = {"x-simulated-trading": "1"}
print("time:", ex.fetch_time())       # 先测连通性（公有接口）
ex.load_markets()
bal = ex.fetch_balance()              # 需要至少 Read 权限
print("USDT:", bal.get("USDT", {}))

