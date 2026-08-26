# 我的代码修改汇总

本文档整理了所有对 freqtrade 仓库的修改和新增代码，方便与 git 仓库进行对比。

**生成时间**: 2025-02-03  
**Git 仓库版本**: stable (c86484b15)  
**文件位置**: 所有新增文件已统一移动到 `my_custom_code/` 文件夹中

---

## 📝 目录

1. [修改的文件](#修改的文件)
2. [新增的文件](#新增的文件)
3. [代码对比](#代码对比)

---

## 修改的文件

### 1. `freqtrade/commands/arguments.py`

**修改位置**: 第 357 行附近

**修改内容**:
```python
def _build_args(self, optionlist: list[str], parser: ArgumentParser | _ArgumentGroup) -> None:
    print("optionlist:", optionlist)
    # optionlist: ['pairs', 'pairs_file', 'days', 'new_pairs_days', 'include_inactive', 'no_parallel_download']
    # 多了个 no_parallel_download
    for val in optionlist:
        opt = AVAILABLE_CLI_OPTIONS[val]
        options = deepcopy(opt.kwargs)
```

**说明**: 添加了调试打印，用于查看 optionlist 的内容。

---

### 2. `freqtrade/commands/cli_options.py`

**修改位置**: 
- 第 561 行附近（修改 `no_parallel_download` 选项）
- 第 832 行附近（修改 `lookahead_allow_limit_orders` 选项）

**Git 仓库版本**:

1. **`no_parallel_download` 选项** (Git 仓库):
```python
"no_parallel_download": Arg(
    "--no-parallel-download",
    help="Disable parallel startup download. Only use this if you experience issues.",
    action="store_true",
),
```

2. **`lookahead_allow_limit_orders` 选项** (Git 仓库):
```python
"lookahead_allow_limit_orders": Arg(
    "--allow-limit-orders",
    help=(
        "Allow limit orders in lookahead analysis (could cause false positives "
        "in lookahead analysis results)."
    ),
    action="store_true",
),
```

**我的修改版本**:

1. **`no_parallel_download` 选项** (我的版本):
```python
"no_parallel_download": Arg(
    "--no-parallel-download",
    help="Disable parallel downloading of data.",
    action="store_true",
    default=False,
),
```

2. **`lookahead_allow_limit_orders` 选项** (我的版本):
```python
"lookahead_allow_limit_orders": Arg(
    "--lookahead-allow-limit-orders",
    help="Allow limit orders in lookahead analysis.",
    action="store_true",
    default=False,
),
```

**差异说明**: 
- `no_parallel_download`: 修改了帮助文本，添加了 `default=False` 参数
- `lookahead_allow_limit_orders`: 修改了命令行参数名称（从 `--allow-limit-orders` 改为 `--lookahead-allow-limit-orders`），简化了帮助文本，添加了 `default=False` 参数

---

## 新增的文件

### 1. `test_okx_connection.py` - OKX 交易所测试脚本

**文件路径**: `my_custom_code/test_okx_connection.py`

**功能**: 测试 OKX 交易所连接，支持代理和模拟盘模式

**主要代码**:
```python
"""
# 1) ccxt 直测（带代理）
import ccxt
ex = ccxt.okx({
    "timeout": 30000,
    "enableRateLimit": True,
    "options": {"defaultType": "spot"},
    "proxies": {
        "http":  "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890",
    },
})
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
        "http":  "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890",
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
```

---

### 2. `batch_backtest_runner.py` - 批量回测运行器

**文件路径**: `my_custom_code/batch_backtest_runner.py`

**功能**: 批量执行 freqtrade 数据下载和回测命令

**主要功能**:
- 自动生成下载和回测命令
- 检查数据文件是否存在，避免重复下载
- 记录执行历史和日志
- 支持多策略、多交易对、多时间框架的批量回测

**关键代码片段**:
```python
class FreqtradeRunner:
    def __init__(self):
        self.command_history = []
        
    def run_command(self, command, description):
        """Execute shell command and log results"""
        # ... 执行命令并记录结果
        
    def generate_commands(self, timeframes, strategy, pairs, timerange):
        """Generate commands for specific parameters"""
        # ... 生成下载和回测命令
        
    def run_batch(self, timeframes, strategy, pairs, timerange):
        """Execute batch of commands for given parameters"""
        # ... 批量执行命令
```

**使用示例**:
```python
strategies = ['AwesomeStrategy', 'PowerTower', 'Bandtastic', ...]
pairs_list = ['DOGE/USDT']
timeranges = ['20200730-20250924']
timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '8h', '12h', '1d', '3d', '1w']

runner = FreqtradeRunner()
for strategy in strategies:
    for pairs in pairs_list:
        for timerange in timeranges:
            runner.run_batch(timeframes, strategy, pairs, timerange)
```

---

### 3. `backtest_result_parser.py` - 回测结果解析器（完整版）

**文件路径**: `my_custom_code/backtest_result_parser.py`

**功能**: 解析 freqtrade 回测报告文本文件，提取关键指标并导出为 Excel

**主要功能**:
- 解析 BACKTESTING REPORT、ENTER TAG STATS、SUMMARY METRICS、STRATEGY SUMMARY 等部分
- 添加中文注释和说明
- 过滤和筛选数据（如总利润百分比 > 100%，夏普比率 > 0）
- 导出为 Excel 文件

**关键函数**:
```python
def parse_duration(duration_str):
    """Convert duration string to total hours."""
    
def parse_win_draw_loss(value):
    """Add Chinese annotation to Win Draw Loss Win% field."""
    
def extract_data_from_file(file_content, filename):
    """Extract numerical data from the backtesting report."""
    
def process_folder(input_folder, output_file):
    """Process all text files in the input folder and save to an Excel file."""
```

**使用示例**:
```python
input_folder = "/Users/htq/Desktop/真正的金融/币圈/freqtrade/backtest_txts/DOGE"
output_file = "backtest_results.xlsx"
process_folder(input_folder, output_file)
```

---

### 4. `backtest_result_parser_simple.py` - 回测结果解析器（简化版）

**文件路径**: `my_custom_code/backtest_result_parser_simple.py`

**功能**: 简化版的回测结果解析器，功能与 `backtest_result_parser.py` 类似但代码更简洁

**主要区别**:
- 简化了 SUMMARY METRICS 的解析逻辑
- 使用不同的过滤条件（CAGR > 0，总利润百分比 > 10%）

---

### 5. `backtest_json_to_csv.py` - JSON 转 CSV 工具

**文件路径**: `my_custom_code/backtest_json_to_csv.py`

**功能**: 将 freqtrade 回测结果 JSON 文件转换为 CSV 格式

**主要功能**:
- 解析 JSON 格式的回测结果
- 提取交易数据（开仓、平仓、盈亏等）
- 格式化时间戳
- 生成统计信息（总交易数、盈利交易数、胜率等）

**使用示例**:
```bash
python backtest_json_to_csv.py "user_data/backtest_results/backtest-result-2025-09-18_10-34-46/backtest-result-2025-09-18_10-34-46.json"
```

**关键函数**:
```python
def parse_json_file(json_file_path):
    """解析JSON文件并提取交易数据"""
    
def convert_to_csv(trades_data, output_path):
    """将交易数据转换为CSV文件"""
```

---

### 6. `batch_dryrun_manager.py` - 批量模拟盘管理器

**文件路径**: `my_custom_code/batch_dryrun_manager.py`

**功能**: 批量启动和管理多个 freqtrade 模拟盘实例

**主要功能**:
- 自动生成配置文件（每个实例独立的端口、数据库、日志）
- 启动/停止/查看状态/重启多个实例
- 支持多策略、多时间框架同时运行
- 自动端口分配和冲突检测

**配置示例**:
```python
PLANS = [
    {"strategy": "MultiMa", "timeframe": "15m", "pairs": ["DOGE/USDT"]},
    {"strategy": "MultiMa", "timeframe": "30m", "pairs": ["DOGE/USDT"]},
    {"strategy": "GodStra", "timeframe": "1m", "pairs": ["DOGE/USDT"]},
    # ... 更多配置
]
```

**使用示例**:
```bash
python3 batch_dryrun_manager.py start
python3 batch_dryrun_manager.py status
python3 batch_dryrun_manager.py stop
python3 batch_dryrun_manager.py restart
```

**关键功能**:
- 每个实例独立的 API 端口（从 8100 开始）
- 每个实例独立的 RPC 端口（从 11000 开始）
- 每个实例独立的数据库文件
- 每个实例独立的日志文件

---

### 7. `backtest_results_summary.md` - 策略回测结果表格

**文件路径**: `my_custom_code/backtest_results_summary.md`

**内容**: 记录了不同策略在不同时间框架下的回测结果

**表格包含**:
- 策略名称
- 文件名/周期
- 交易次数 (Trades)
- 胜率
- 总收益%
- 最大回撤%
- 平均持仓时间

**示例数据**:
```
| 策略                | 文件名/周期                                        | Trades |   胜率 |   总收益% |     最大回撤% | 平均持仓     |
| ----------------- | --------------------------------------------- | -----: | ---: | -----: | --------: | -------- |
| **MultiMa**       | `USDT_MultiMa_20200730_20250924_15m.txt`      |    298 | 38.9 | 314.51 | **14.47** | 11:03:00 |
| **GodStra**       | `USDT_GodStra_20200730_20250924_1m.txt`       |     58 | 69.0 | 596.68 | **22.43** | 7天7:44   |
```

---

### 8. `my_readme.md` - 使用说明文档

**文件路径**: `my_custom_code/my_readme.md`

**内容**: 记录了 freqtrade 的使用教程、命令示例和配置说明

**主要内容**:
- Freqtrade 安装和配置
- 数据下载命令
- 回测命令
- 策略创建
- 交易所配置（代理设置）
- 常用命令列表

---

### 9. `my_readme_code.md` - 代码说明文档

**文件路径**: `my_custom_code/my_readme_code.md`

**内容**: 简短的官方文档链接

---

## 代码对比

### Git Diff 对比

#### 1. `freqtrade/commands/arguments.py`

**Git 仓库版本** (无此修改):
```python
def _build_args(self, optionlist: list[str], parser: ArgumentParser | _ArgumentGroup) -> None:
    for val in optionlist:
        opt = AVAILABLE_CLI_OPTIONS[val]
        options = deepcopy(opt.kwargs)
```

**我的修改版本**:
```python
def _build_args(self, optionlist: list[str], parser: ArgumentParser | _ArgumentGroup) -> None:
    print("optionlist:", optionlist)
    # optionlist: ['pairs', 'pairs_file', 'days', 'new_pairs_days', 'include_inactive', 'no_parallel_download']
    # 多了个 no_parallel_download
    for val in optionlist:
        opt = AVAILABLE_CLI_OPTIONS[val]
        options = deepcopy(opt.kwargs)
```

**差异**: 添加了调试打印语句

---

#### 2. `freqtrade/commands/cli_options.py`

**Git 仓库版本**:
```python
"no_parallel_download": Arg(
    "--no-parallel-download",
    help="Disable parallel startup download. Only use this if you experience issues.",
    action="store_true",
),
```

```python
"lookahead_allow_limit_orders": Arg(
    "--allow-limit-orders",
    help=(
        "Allow limit orders in lookahead analysis (could cause false positives "
        "in lookahead analysis results)."
    ),
    action="store_true",
),
```

**我的修改版本**:
```python
"no_parallel_download": Arg(
    "--no-parallel-download",
    help="Disable parallel downloading of data.",
    action="store_true",
    default=False,
),
```

```python
"lookahead_allow_limit_orders": Arg(
    "--lookahead-allow-limit-orders",
    help="Allow limit orders in lookahead analysis.",
    action="store_true",
    default=False,
),
```

**差异**: 
1. `no_parallel_download`: 修改了帮助文本，添加了 `default=False`
2. `lookahead_allow_limit_orders`: 修改了命令行参数名称，简化了帮助文本，添加了 `default=False`

---

## 总结

### 修改统计

- **修改的文件**: 2 个
  - `freqtrade/commands/arguments.py`
  - `freqtrade/commands/cli_options.py`

- **新增的文件**: 9+ 个（已统一移动到 `my_custom_code/` 文件夹）
  - `my_custom_code/okx_test.py` - OKX 测试脚本
  - `my_custom_code/py_run.py` - 批量回测运行器
  - `my_custom_code/py2_main.py` - 回测结果解析器（完整版）
  - `my_custom_code/py2.py` - 回测结果解析器（简化版）
  - `my_custom_code/json_to_csv_converter.py` - JSON 转 CSV 工具
  - `my_custom_code/ft_batch_dryrun.py` - 批量模拟盘管理器
  - `my_custom_code/模拟盘.md` - 回测结果表格
  - `my_custom_code/my_readme.md` - 使用说明
  - `my_custom_code/my_readme_code.md` - 代码说明

### 主要功能

1. **调试功能**: 在 `arguments.py` 中添加调试打印
2. **新命令行选项**: 添加数据下载和回测分析的控制选项
3. **批量回测工具**: 自动化批量回测流程
4. **结果分析工具**: 解析回测报告并导出为 Excel
5. **模拟盘管理**: 批量启动和管理多个模拟盘实例
6. **数据转换工具**: JSON 转 CSV 工具

### 注意事项

1. **敏感信息**: `okx_test.py` 中包含 API 密钥，建议不要提交到公共仓库
2. **路径硬编码**: 部分脚本中包含硬编码的路径，需要根据实际情况修改
3. **依赖项**: 部分脚本可能需要额外的 Python 包（如 `pandas`, `openpyxl`, `python-dotenv`）

---

## 使用建议

1. **备份**: 在应用这些修改前，建议先备份原始文件
2. **测试**: 在测试环境中先验证修改是否正常工作
3. **版本控制**: 建议将这些修改记录在版本控制系统中，方便后续对比和回滚
4. **文档更新**: 如果修改了核心功能，建议更新相关文档

---

**生成工具**: 自动整理脚本  
**最后更新**: 2025-01-XX
