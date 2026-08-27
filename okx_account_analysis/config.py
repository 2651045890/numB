"""OKX API 配置。密钥只从进程环境变量读取。"""
import os

API_KEY = os.getenv("OKX_API_KEY", "")
SECRET_KEY = os.getenv("OKX_SECRET_KEY", "")
PASSPHRASE = os.getenv("OKX_PASSPHRASE", "")

# OKX API 基础URL
BASE_URL = "https://www.okx.com"

# 是否使用模拟盘（Demo Trading）
USE_SIMULATED = os.getenv("OKX_SIMULATED", "True").lower() == "true"  # 默认使用模拟盘

# 代理设置（如果需要）
PROXY_CONFIG = {
    "http": os.getenv("OKX_HTTP_PROXY", "http://127.0.0.1:7897"),
    "https": os.getenv("OKX_HTTPS_PROXY", "http://127.0.0.1:7897"),
}

# 是否使用代理（如果代理未运行，可以设置为False）
USE_PROXY = os.getenv("OKX_USE_PROXY", "False").lower() == "true"
