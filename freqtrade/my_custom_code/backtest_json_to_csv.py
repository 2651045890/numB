#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Freqtrade回测结果JSON转CSV工具
将Freqtrade回测结果JSON文件转换为CSV格式，便于分析和处理

使用方法:
python json_to_csv_converter.py <json_file_path>

输出文件将保存在同一目录下，文件名为原文件名.csv
"""

import json
import csv
import sys
import os
from pathlib import Path
from datetime import datetime
import pandas as pd


def parse_json_file(json_file_path):
    """
    解析JSON文件并提取交易数据
    
    Args:
        json_file_path (str): JSON文件路径
        
    Returns:
        list: 交易数据列表
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取交易数据
        trades_data = []
        
        # 遍历策略
        for strategy_name, strategy_data in data.get('strategy', {}).items():
            trades = strategy_data.get('trades', [])
            
            for trade in trades:
                # 基本交易信息
                trade_info = {
                    'strategy': strategy_name,
                    'pair': trade.get('pair', ''),
                    'stake_amount': trade.get('stake_amount', 0),
                    'max_stake_amount': trade.get('max_stake_amount', 0),
                    'amount': trade.get('amount', 0),
                    'open_date': trade.get('open_date', ''),
                    'close_date': trade.get('close_date', ''),
                    'open_rate': trade.get('open_rate', 0),
                    'close_rate': trade.get('close_rate', 0),
                    'fee_open': trade.get('fee_open', 0),
                    'fee_close': trade.get('fee_close', 0),
                    'trade_duration': trade.get('trade_duration', 0),
                    'profit_ratio': trade.get('profit_ratio', 0),
                    'profit_abs': trade.get('profit_abs', 0),
                    'exit_reason': trade.get('exit_reason', ''),
                    'initial_stop_loss_abs': trade.get('initial_stop_loss_abs', 0),
                    'initial_stop_loss_ratio': trade.get('initial_stop_loss_ratio', 0),
                    'stop_loss_abs': trade.get('stop_loss_abs', 0),
                    'stop_loss_ratio': trade.get('stop_loss_ratio', 0),
                    'min_rate': trade.get('min_rate', 0),
                    'max_rate': trade.get('max_rate', 0),
                    'is_open': trade.get('is_open', False),
                    'enter_tag': trade.get('enter_tag', ''),
                    'leverage': trade.get('leverage', 1.0),
                    'is_short': trade.get('is_short', False),
                    'open_timestamp': trade.get('open_timestamp', 0),
                    'close_timestamp': trade.get('close_timestamp', 0),
                    'funding_fees': trade.get('funding_fees', 0.0)
                }
                
                # 添加订单信息（如果需要详细订单数据）
                orders = trade.get('orders', [])
                if orders:
                    # 获取开仓和平仓订单
                    entry_order = None
                    exit_order = None
                    
                    for order in orders:
                        if order.get('ft_is_entry', False):
                            entry_order = order
                        else:
                            exit_order = order
                    
                    # 添加开仓订单信息
                    if entry_order:
                        trade_info.update({
                            'entry_order_amount': entry_order.get('amount', 0),
                            'entry_order_price': entry_order.get('safe_price', 0),
                            'entry_order_cost': entry_order.get('cost', 0),
                            'entry_order_timestamp': entry_order.get('order_filled_timestamp', 0)
                        })
                    
                    # 添加平仓订单信息
                    if exit_order:
                        trade_info.update({
                            'exit_order_amount': exit_order.get('amount', 0),
                            'exit_order_price': exit_order.get('safe_price', 0),
                            'exit_order_cost': exit_order.get('cost', 0),
                            'exit_order_timestamp': exit_order.get('order_filled_timestamp', 0),
                            'exit_order_tag': exit_order.get('ft_order_tag', '')
                        })
                
                trades_data.append(trade_info)
        
        return trades_data
        
    except Exception as e:
        print(f"解析JSON文件时出错: {e}")
        return []


def convert_to_csv(trades_data, output_path):
    """
    将交易数据转换为CSV文件
    
    Args:
        trades_data (list): 交易数据列表
        output_path (str): 输出CSV文件路径
    """
    if not trades_data:
        print("没有找到交易数据")
        return
    
    try:
        # 使用pandas创建DataFrame
        df = pd.DataFrame(trades_data)
        
        # 格式化时间戳列
        timestamp_columns = ['open_timestamp', 'close_timestamp', 'entry_order_timestamp', 'exit_order_timestamp']
        for col in timestamp_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], unit='ms', errors='coerce')
        
        # 保存为CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"成功转换为CSV文件: {output_path}")
        print(f"共转换 {len(trades_data)} 条交易记录")
        
        # 显示基本统计信息
        print("\n基本统计信息:")
        print(f"总交易数: {len(df)}")
        print(f"盈利交易数: {len(df[df['profit_abs'] > 0])}")
        print(f"亏损交易数: {len(df[df['profit_abs'] < 0])}")
        print(f"总盈亏: {df['profit_abs'].sum():.6f}")
        print(f"平均盈亏: {df['profit_abs'].mean():.6f}")
        print(f"胜率: {len(df[df['profit_abs'] > 0]) / len(df) * 100:.2f}%")
        
    except Exception as e:
        print(f"转换为CSV时出错: {e}")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python json_to_csv_converter.py <json_file_path>")
        print("示例: python json_to_csv_converter.py backtest-result.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    
    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"文件不存在: {json_file_path}")
        sys.exit(1)
    
    # 生成输出文件路径
    input_path = Path(json_file_path)
    output_path = input_path.parent / f"{input_path.stem}.csv"
    
    print(f"输入文件: {json_file_path}")
    print(f"输出文件: {output_path}")
    print("开始转换...")
    
    # 解析JSON文件
    trades_data = parse_json_file(json_file_path)
    
    if not trades_data:
        print("未找到有效的交易数据")
        sys.exit(1)
    
    # 转换为CSV
    convert_to_csv(trades_data, output_path)


if __name__ == "__main__":
    main()

# python json_to_csv_converter.py "user_data/backtest_results/backtest-result-2025-09-18_10-34-46/backtest-result-2025-09-18_10-34-46.json" 


