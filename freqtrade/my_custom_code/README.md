# 自定义代码文件夹

本文件夹包含所有对 freqtrade 仓库的自定义修改和新增代码。

## 📁 文件夹说明

此文件夹用于统一管理所有自定义代码，避免与 freqtrade 官方代码混淆。

## 📝 文件列表

### 工具脚本

1. **test_okx_connection.py** - OKX 交易所连接测试脚本
   - 测试 OKX API 连接
   - 支持代理配置
   - 支持模拟盘模式

2. **batch_backtest_runner.py** - 批量回测运行器
   - 自动化批量回测流程
   - 支持多策略、多交易对、多时间框架
   - 自动检查数据文件，避免重复下载

3. **backtest_result_parser.py** - 回测结果解析器（完整版）
   - 解析 freqtrade 回测报告文本文件
   - 提取关键指标并导出为 Excel
   - 支持中文注释和说明

4. **backtest_result_parser_simple.py** - 回测结果解析器（简化版）
   - 简化版的回测结果解析器

5. **backtest_json_to_csv.py** - JSON 转 CSV 工具
   - 将 freqtrade 回测结果 JSON 文件转换为 CSV 格式
   - 提取交易数据并生成统计信息

6. **batch_dryrun_manager.py** - 批量模拟盘管理器
   - 批量启动和管理多个 freqtrade 模拟盘实例
   - 自动分配端口和配置
   - 支持启动/停止/查看状态/重启

### 文档

7. **backtest_results_summary.md** - 策略回测结果表格
   - 记录不同策略在不同时间框架下的回测结果

8. **freqtrade_usage_guide.md** - 使用说明文档
   - freqtrade 使用教程和命令示例

9. **code_documentation.md** - 代码说明文档
   - 简短的官方文档链接

10. **code_changes_summary.md** - 代码修改汇总文档
    - 详细记录所有修改和新增的代码
    - 包含与 Git 仓库的对比

11. **test_report.md** - 测试报告
    - 代码测试和修复记录

## 🔧 使用说明

### 运行脚本

所有脚本都可以从项目根目录运行，例如：

```bash
# 从项目根目录运行
python my_custom_code/batch_backtest_runner.py

# 或者进入文件夹后运行
cd my_custom_code
python batch_backtest_runner.py
```

### 注意事项

1. **路径问题**: 部分脚本中包含硬编码的路径，需要根据实际情况修改
2. **依赖项**: 确保安装了所需的 Python 包（如 `pandas`, `openpyxl`, `python-dotenv`）
3. **敏感信息**: `test_okx_connection.py` 中包含 API 密钥，请妥善保管

## 📊 修改的文件

以下文件在 freqtrade 仓库中被修改（不在本文件夹中）：

- `freqtrade/commands/arguments.py` - 添加了调试打印
- `freqtrade/commands/cli_options.py` - 修改了命令行选项配置

详细修改说明请查看 `code_changes_summary.md`。

## 🔄 版本信息

- **创建时间**: 2025-02-03
- **Freqtrade 版本**: stable (c86484b15)
- **最后更新**: 2025-02-03
