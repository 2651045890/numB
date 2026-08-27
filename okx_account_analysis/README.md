# OKX 账户分析工具

这是一个专门用于分析OKX账户信息的工具集。

## 功能特性

- ✅ 获取账户配置信息（持仓模式、保证金模式等）
- ✅ 获取账户余额（所有币种或指定币种）
- ✅ 获取持仓信息（现货、合约等）
- ✅ 获取挂单信息
- ✅ 获取交易手续费率
- ✅ 获取资产估值（按法币计价）
- ✅ 获取计息记录
- ✅ 获取最大可提币数量

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

### 系统环境变量（推荐）

密钥统一保存在项目外的 `/Users/htq/Desktop/数字货币/密钥.md`，
由 shell 启动配置导入环境变量。程序本身不读取密钥文件。

```bash
test -n "$OKX_API_KEY" && echo "OKX API key loaded"
```

`config.py` 只读取 `OKX_API_KEY`、`OKX_SECRET_KEY` 和
`OKX_PASSPHRASE` 环境变量。

## 使用方法

### 🚀 主入口（推荐）

使用 `main.py` 作为统一入口，提供所有功能：

```bash
# 完整分析（默认，最简单）
python main.py

# 或者指定模式
python main.py --mode analyze

# 使用模拟盘
python main.py --simulated

# 使用实盘
python main.py --real

# 快速测试连接
python main.py --mode test

# 只获取余额（JSON格式）
python main.py --mode balance

# 只获取账户配置
python main.py --mode config

# 获取持仓信息
python main.py --mode positions

# 获取挂单信息
python main.py --mode orders

# 不保存JSON文件
python main.py --no-json

# 不生成文本报告
python main.py --no-report

# 静默模式（不打印摘要）
python main.py --quiet
```

### 在Python代码中使用

```python
from main import (
    analyze_account,      # 完整分析
    get_account_balance,   # 获取余额
    get_account_config,    # 获取配置
    get_positions,         # 获取持仓
    get_orders,            # 获取挂单
    quick_test            # 快速测试
)

# 方式1: 完整分析（推荐，一键获取所有信息）
result = analyze_account(
    simulated=True,           # 使用模拟盘，None则使用config.py中的设置
    save_json=True,           # 保存JSON文件
    print_summary=True,       # 打印摘要
    generate_txt_report=True   # 生成文本报告
)

# 方式2: 快速获取特定信息
balance = get_account_balance(ccy="USDT", simulated=True)
config = get_account_config(simulated=True)
positions = get_positions(inst_type="SPOT", simulated=True)
orders = get_orders(simulated=True)

# 方式3: 快速测试连接
success = quick_test(simulated=True)
```

更多使用示例请查看 `example_usage.py` 文件。

### 其他脚本（可选）

如果需要单独运行：

```bash
# 完整分析
python account_analyzer.py

# 生成友好报告
python generate_report.py

# 快速测试
python quick_test.py
```

### 在代码中使用

```python
from account_analyzer import AccountAnalyzer

# 创建分析器（默认使用config.py中的设置）
analyzer = AccountAnalyzer(simulated=False)  # False=实盘, True=模拟盘

# 获取账户配置
config = analyzer.get_account_config()
print(config)

# 获取账户余额
balance = analyzer.get_account_balance()
print(balance)

# 获取USDT余额
usdt_balance = analyzer.get_account_balance(ccy="USDT")
print(usdt_balance)

# 获取持仓信息
positions = analyzer.get_positions()
print(positions)

# 获取现货持仓
spot_positions = analyzer.get_positions(inst_type="SPOT")
print(spot_positions)

# 综合分析
result = analyzer.analyze_all()
analyzer.print_summary(result)
```

## 文件说明

- `main.py`: **主入口文件**（推荐使用，提供统一调用接口）
- `config.py`: API配置信息
- `okx_client.py`: OKX API客户端封装
- `account_analyzer.py`: 账户分析核心程序
- `generate_report.py`: 报告生成工具
- `quick_test.py`: 快速测试脚本
- `example_usage.py`: 使用示例代码
- `requirements.txt`: Python依赖包
- `README.md`: 本说明文件

## 注意事项

1. **API权限**: 确保您的API密钥具有"读取"权限
2. **模拟盘与实盘**: 模拟盘和实盘的账户信息是分开的，请根据需要使用
3. **代理设置**: 如果在中国大陆，可能需要配置代理才能访问OKX API
4. **安全性**: 不要将包含真实API密钥的配置文件提交到版本控制系统

## 安全建议

1. 使用环境变量存储敏感信息
2. 只在项目外的 `密钥.md` 中保存密钥，通过系统环境变量导入
3. 定期轮换API密钥
4. 限制API密钥的权限范围（只授予必要的权限）
