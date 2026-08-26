import subprocess
import logging
from datetime import datetime
import json
import os
from pathlib import Path

# 获取项目根目录（假设脚本在 my_custom_code 文件夹中）
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent  # 项目根目录

# Configure logging
# 延迟初始化 logging，确保 PROJECT_ROOT 已定义
def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler((PROJECT_ROOT / 'freqtrade_batch.log').as_posix()),
            logging.StreamHandler()
        ]
    )

# 在模块加载时设置 logging
setup_logging()

class FreqtradeRunner:
    def __init__(self):
        self.command_history = []
        
    def run_command(self, command, description):
        """Execute shell command and log results"""
        logging.info(f"Starting: {description}")
        logging.debug(f"Full command: {command}")
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            self.command_history.append({
                'command': command,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })
            logging.info(f"Completed successfully: {description}")
            logging.debug(f"Command output:\n{result.stdout}")
            return True
        except subprocess.CalledProcessError as e:
            # 移除错误的路径删除逻辑，避免误匹配交易对（如 DOGE/USDT）
            # 如果需要清理临时文件，应该明确指定文件路径
            pass

            self.command_history.append({
                'command': command,
                'status': 'failed',
                'error': e.stderr,
                'timestamp': datetime.now().isoformat()
            })
            logging.error(f"Execution failed: {description}")
            logging.error(f"Error output:\n{e.stderr}")
            return False

    def generate_commands(self, timeframes, strategy, pairs, timerange):
        """Generate commands for specific parameters"""
        commands = []
        
        for timeframe in timeframes:
            # 使用项目根目录的路径
            txtfile = PROJECT_ROOT / "backtest_txts" / f"{pairs}_{strategy.replace('/','_')}_{timerange.replace('-','_')}_{timeframe}.txt"
            logfile = PROJECT_ROOT / "backtest_logs" / f"{pairs}_{strategy.replace('/','_')}_{timerange.replace('-','_')}_{timeframe}.log"

            # 获取文件夹路径
            txt_dir = txtfile.parent
            log_dir = logfile.parent

            # 检查文件夹是否存在，如果不存在则创建
            txt_dir.mkdir(parents=True, exist_ok=True)
            log_dir.mkdir(parents=True, exist_ok=True)

            config_path = PROJECT_ROOT / "user_data" / "config.json"
            config_arg = f"--config {config_path.as_posix()}" if config_path.exists() else ""
            
            download_cmd = (
                f"freqtrade download-data "
                f"{config_arg} "
                f"--timeframe {timeframe} "
                f"--pairs {pairs} "
                f"--timerange {timerange} "
                f"--exchange okx"
            ).strip()
            
            backtest_cmd = (
                f"freqtrade backtesting "
                f"{config_arg} "
                f"--strategy {strategy} "
                f"--timeframe {timeframe} "
                f"--timerange {timerange} > {txtfile.as_posix()} "
                f"--logfile {logfile.as_posix()}"
            ).strip()

       
            # 假设你知道数据存储路径和文件名的结构
            data_path = PROJECT_ROOT / "user_data" / "data" / "okx" / f"{pairs.replace('/','_')}-{timeframe}.feather"
            if not data_path.exists(): # 不存在则爬
                commands.append((
                    download_cmd,
                    backtest_cmd,
                    f"Timeframe: {timeframe}, Strategy: {strategy}"
                ))
            else:
                if not logfile.exists(): # 不存在
                    if False: # 如果设置为True, 强制爬
                        commands.append((
                        download_cmd,
                        backtest_cmd,
                        f"Timeframe: {timeframe}, Strategy: {strategy}"
                        ))
                    else: # 如果有False，则爬这个。
                        # 20200730-20250924 > backtest_output.txt
                        commands.append((
                            False,
                            backtest_cmd,
                            f"Timeframe: {timeframe}, Strategy: {strategy}"
                        ))
                else: # 如果存在
                    print("Strategy already exists, skipping download.")
                    if False: # 如果设置为True, 强制爬
                        commands.append((
                        download_cmd,
                        backtest_cmd,
                        f"Timeframe: {timeframe}, Strategy: {strategy}"
                        ))
                    else: # 如果有False，则爬这个。
                        # 20200730-20250924 > backtest_output.txt
                        commands.append((
                            False,
                            False,
                            f"Timeframe: {timeframe}, Strategy: {strategy}"
                        ))
            
        return commands

    def run_batch(self, timeframes, strategy, pairs, timerange):
        """Execute batch of commands for given parameters"""
        commands = self.generate_commands(timeframes, strategy, pairs, timerange)
        
        for download_cmd, backtest_cmd, description in commands:
            if download_cmd:
                if self.run_command(download_cmd, f"Downloading data - {description}"):
                    self.run_command(backtest_cmd, f"Backtesting strategy - {description}")
            else:
                if backtest_cmd:
                    self.run_command(backtest_cmd, f"Backtesting strategy - {description}")

    def export_history(self, filename='command_history.json'):
        """Export execution history"""
        # 保存到项目根目录
        history_path = PROJECT_ROOT / filename
        with open(history_path, 'w') as f:
            json.dump(self.command_history, f, indent=2)

if __name__ == "__main__":

    """
    1m — 每分钟
    5m — 每 5 分钟
    15m — 每 15 分钟
    30m — 每 30 分钟
    1h — 每小时
    2h — 每 2 小时
    3h — 每 3 小时
    4h — 每 4 小时
    6h — 每 6 小时
    8h — 每 8 小时
    12h — 每 12 小时
    1d — 每天
    3d — 每 3 天
    1w — 每周
    2w — 每两周
    1M — 每月
    """

    # 定义参数
    # strategies = ['Bandtastic', 'BreakEven', 'Diamond']  # 可以增加不同的策略
    # strategies = ['advanced_Strategy001']
    strategies = ['AwesomeStrategy', 'PowerTower', 'Bandtastic', 'Strategy001', 'BreakEven', 
    'Strategy001_custom_exit', 'hlhb', 'CustomStoplossWithPSAR', 'Strategy002', 
    'Diamond', 'Strategy003', 'mabStra', 'FixedRiskRewardLoss', 'Strategy004', 
    'minimal_Strategy001', 'GodStra', 'Strategy005', 'multi_tf', 'Heracles', 
    'Supertrend', 'sample_strategy', 'HourBasedStrategy', 'SwingHighToSky', 
    'sample_strategy_ MyStrategy', 'InformativeSample', 'UniversalMACD', 
    'sample_strategy_BbandRsi', 'MultiMa', 'PatternRecognition', 'advanced_Strategy001']
    strategies = strategies[0:1]
    pairs_list = ['DOGE/USDT']  # 多个交易对
    timeranges = ['20200730-20250924']  # 不同时间范围
    # 定义时间框架（OKX 支持的时间框架）
    # OKX 支持: ['1m', '3m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w', '1M', '3M']
    # 移除了 OKX 不支持的时间框架: '8h', '3d'
    timeframes = ['1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d', '1w']
    # timeframes = ['1h', '2h', '4h', '6h', '12h', '1d', '1w']
    # 初始化 FreqtradeRunner
    runner = FreqtradeRunner()
    # 遍历所有的策略、交易对和时间范围
    for strategy in strategies:
        for pairs in pairs_list:
            for timerange in timeranges:
                print(f"Running backtest for strategy: {strategy}, pair: {pairs}, timerange: {timerange}")
                # 运行批量回测
                runner.run_batch(timeframes, strategy, pairs, timerange)
                # 导出历史数据
                runner.export_history()

                # 可以根据需要，导出或者保存每次回测的结果
                # 比如保存回测结果到文件或数据库
                # runner.export_results_to_file(strategy, pairs, timerange)

    #  EXIT REASON STATS   
    #  MIXED TAG STATS     
    # LEFT OPEN TRADES REPORT  