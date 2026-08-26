import os
import re
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path

# 获取项目根目录
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

def parse_duration(duration_str):
    """Convert duration string (e.g., '4 days, 5:27:00') to total hours."""
    if not duration_str or duration_str == '0:00':
        return 0
    try:
        if 'days' in duration_str:
            days, time = duration_str.split(', ')
            days = int(days.split()[0])
            h, m, s = map(int, time.split(':'))
            return days * 24 + h + m / 60 + s / 3600
        else:
            h, m, s = map(int, time.split(':'))
            return h + m / 60 + s / 3600
    except:
        return 0

def parse_win_draw_loss(value):
    """Add Chinese annotation to Win Draw Loss Win% field."""
    try:
        # Split the value, e.g., "1 / 0 / 0 / 100%"
        parts = value.replace(' ', '').split('/')
        if len(parts) == 4:
            wins, draws, losses, win_pct = parts
            return f"{value} (胜{wins}平{draws}负{losses}胜率{win_pct})"
        return value
    except:
        return value

def parse_table(lines, start_idx):
    """Parse a table from lines starting at start_idx, return headers and rows."""
    headers = []
    rows = []
    i = start_idx
    first = True
    while i < len(lines):
        if lines[i].startswith('┃') or lines[i].startswith('│'):
            splitter = lines[i][0]
            parts = [part.strip() for part in lines[i].split(splitter)[1:-1]]
            if first:
                headers = parts
                first = False
            else:
                rows.append(parts)
            i += 1
        elif lines[i].startswith('└'):
            break
        else:
            i += 1
    return headers, rows, i

def parse_summary_metrics(lines, start_idx):
    """Parse the SUMMARY METRICS section into a dictionary."""
    data = {}
    i = start_idx
    skipped_header = False
    while i < len(lines):
        if lines[i].startswith('┃') or lines[i].startswith('│'):
            splitter = lines[i][0]
            parts = [part.strip() for part in lines[i].split(splitter)[1:-1]]
            if not skipped_header:
                skipped_header = True
            else:
                metric, value = parts
                data[metric] = value
            i += 1
        elif lines[i].startswith('└'):
            break
        else:
            i += 1
    return data, i

def extract_data_from_file(file_content):
    """Extract numerical data from the backtesting report with bilingual column names and content."""
    lines = file_content.splitlines()
    data = {}
    strategy_name = ''
    
    # Extract strategy name
    for line in lines:
        if line.startswith('Result for strategy'):
            strategy_name = line.split('Result for strategy ')[1].strip()
            data['Strategy_(策略名称)'] = strategy_name  # 策略名称：回测使用的交易策略名称
            break
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Parse BACKTESTING REPORT
        if line == 'BACKTESTING REPORT':
            i += 1  # Skip the top border
            headers, rows, i = parse_table(lines, i)
            for row in rows:
                pair = row[0]
                prefix = f"Backtest_{pair.replace('/', '_')}_" if pair != 'TOTAL' else 'Backtest_TOTAL_'
                for header, value in zip(headers[1:], row[1:]):  # Skip Pair column
                    if header == 'Avg Duration':
                        value = parse_duration(value)  # 平均持仓时间：交易的平均持续时间（小时）
                        header_display = 'Avg_Duration_(平均持仓时间)'
                    elif header == 'Win  Draw  Loss  Win%':
                        value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
                        header_display = 'Win_Draw_Loss_Win%_(胜平负及胜率)'
                    elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
                        try:
                            value = float(value)
                        except:
                            pass
                    # Add Chinese explanation to header
                    header_key = header.replace(' ', '_')
                    if header == 'Trades':
                        header_display = f"Trades_(交易次数)"  # 交易次数：回测中的交易总数
                    elif header == 'Avg Profit %':
                        header_display = f"Avg_Profit_%_(平均利润百分比)"  # 平均利润百分比：每笔交易的平均利润率
                    elif header == 'Tot Profit USDT':
                        header_display = f"Tot_Profit_USDT_(总利润USDT)"  # 总利润USDT：回测的总盈利金额（USDT）
                    elif header == 'Tot Profit %':
                        header_display = f"Tot_Profit_%_(总利润百分比)"  # 总利润百分比：回测的总盈利百分比
                    elif header == 'Win  Draw  Loss  Win%':
                        header_display = f"Win_Draw_Loss_Win%_(胜平负及胜率)"  # 胜平负及胜率：交易的胜、平、负次数及胜率
                    else:
                        header_display = f"{header_key}_({header})"
                    data[f"{prefix}{header_display}"] = value
        
        # # Parse LEFT OPEN TRADES REPORT
        # elif line == 'LEFT OPEN TRADES REPORT':
        #     i += 1  # Skip the top border
        #     headers, rows, i = parse_table(lines, i)
        #     for row in rows:
        #         pair = row[0]
        #         prefix = f"LeftOpen_{pair.replace('/', '_')}_" if pair != 'TOTAL' else 'LeftOpen_TOTAL_'
        #         for header, value in zip(headers[1:], row[1:]):  # Skip Pair column
        #             if header == 'Avg Duration':
        #                 value = parse_duration(value)  # 平均持仓时间：未平仓交易的平均持续时间（小时）
        #                 header_display = 'Avg_Duration_(平均持仓时间)'
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
        #                 header_display = 'Win_Draw_Loss_Win%_(未平仓胜平负及胜率)'
        #             elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
        #                 try:
        #                     value = float(value)
        #                 except:
        #                     pass
        #             # Add Chinese explanation to header
        #             header_key = header.replace(' ', '_')
        #             if header == 'Trades':
        #                 header_display = f"Trades_(未平仓交易次数)"  # 未平仓交易次数：未平仓交易总数
        #             elif header == 'Avg Profit %':
        #                 header_display = f"Avg_Profit_%_(未平仓平均利润百分比)"  # 未平仓平均利润百分比：未平仓交易的平均利润率
        #             elif header == 'Tot Profit USDT':
        #                 header_display = f"Tot_Profit_USDT_(未平仓总利润USDT)"  # 未平仓总利润USDT：未平仓交易的盈利金额（USDT）
        #             elif header == 'Tot Profit %':
        #                 header_display = f"Tot_Profit_%_(未平仓总利润百分比)"  # 未平仓总利润百分比：未平仓交易的总盈利百分比
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 header_display = f"Win_Draw_Loss_Win%_(未平仓胜平负及胜率)"  # 未平仓胜平负及胜率：未平仓交易的胜、平、负次数及胜率
        #             else:
        #                 header_display = f"{header_key}_({header})"
        #             data[f"{prefix}{header_display}"] = value
        
        # Parse ENTER TAG STATS
        elif line == 'ENTER TAG STATS':
            i += 1  # Skip the top border
            headers, rows, i = parse_table(lines, i)
            for row in rows:
                tag = row[0] if row[0] else 'None'
                prefix = f"EnterTag_{tag}_" if tag != 'TOTAL' else 'EnterTag_TOTAL_'
                for header, value in zip(headers[1:], row[1:]):  # Skip Enter Tag column
                    if header == 'Avg Duration':
                        value = parse_duration(value)  # 平均持仓时间：基于进入标签的交易平均持续时间（小时）
                        header_display = 'Avg_Duration_(平均持仓时间)'
                    elif header == 'Win  Draw  Loss  Win%':
                        value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
                        header_display = 'Win_Draw_Loss_Win%_(进入标签胜平负及胜率)'
                    elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
                        try:
                            value = float(value)
                        except:
                            pass
                    # Add Chinese explanation to header
                    header_key = header.replace(' ', '_')
                    if header == 'Entries':
                        header_display = f"Entries_(进入交易次数)"  # 进入交易次数：基于进入标签的交易总数
                    elif header == 'Avg Profit %':
                        header_display = f"Avg_Profit_%_(进入标签平均利润百分比)"  # 进入标签平均利润百分比：基于进入标签的平均利润率
                    elif header == 'Tot Profit USDT':
                        header_display = f"Tot_Profit_USDT_(进入标签总利润USDT)"  # 进入标签总利润USDT：基于进入标签的总盈利（USDT）
                    elif header == 'Tot Profit %':
                        header_display = f"Tot_Profit_%_(进入标签总利润百分比)"  # 进入标签总利润百分比：基于进入标签的总盈利百分比
                    elif header == 'Win  Draw  Loss  Win%':
                        header_display = f"Win_Draw_Loss_Win%_(进入标签胜平负及胜率)"  # 进入标签胜平负及胜率：基于进入标签的胜、平、负次数及胜率
                    else:
                        header_display = f"{header_key}_({header})"
                    data[f"{prefix}{header_display}"] = value
        
        # # Parse EXIT REASON STATS
        # elif line == 'EXIT REASON STATS':
        #     i += 1  # Skip the top border
        #     headers, rows, i = parse_table(lines, i)
        #     for row in rows:
        #         reason = row[0].replace(' ', '_')
        #         prefix = f"ExitReason_{reason}_"
        #         for header, value in zip(headers[1:], row[1:]):  # Skip Exit Reason column
        #             if header == 'Avg Duration':
        #                 value = parse_duration(value)  # 平均持仓时间：基于退出原因的交易平均持续时间（小时）
        #                 header_display = 'Avg_Duration_(平均持仓时间)'
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
        #                 header_display = 'Win_Draw_Loss_Win%_(退出原因胜平负及胜率)'
        #             elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
        #                 try:
        #                     value = float(value)
        #                 except:
        #                     pass
        #             # Add Chinese explanation to header
        #             header_key = header.replace(' ', '_')
        #             if header == 'Exits':
        #                 header_display = f"Exits_(退出交易次数)"  # 退出交易次数：基于退出原因的交易总数
        #             elif header == 'Avg Profit %':
        #                 header_display = f"Avg_Profit_%_(退出原因平均利润百分比)"  # 退出原因平均利润百分比：基于退出原因的平均利润率
        #             elif header == 'Tot Profit USDT':
        #                 header_display = f"Tot_Profit_USDT_(退出原因总利润USDT)"  # 退出原因总利润USDT：基于退出原因的总盈利（USDT）
        #             elif header == 'Tot Profit %':
        #                 header_display = f"Tot_Profit_%_(退出原因总利润百分比)"  # 退出原因总利润百分比：基于退出原因的总盈利百分比
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 header_display = f"Win_Draw_Loss_Win%_(退出原因胜平负及胜率)"  # 退出原因胜平负及胜率：基于退出原因的胜、平、负次数及胜率
        #             else:
        #                 header_display = f"{header_key}_({header})"
        #             data[f"{prefix}{header_display}"] = value
        
        # # Parse MIXED TAG STATS
        # elif line == 'MIXED TAG STATS':
        #     i += 1  # Skip the top border
        #     headers, rows, i = parse_table(lines, i)
        #     for row in rows:
        #         tag = row[0] if row[0] else 'None'
        #         reason = row[1].replace(' ', '_')
        #         prefix = f"Mixed_{tag}_{reason}_" if tag != 'TOTAL' else f"Mixed_TOTAL_{reason}_"
        #         for header, value in zip(headers[2:], row[2:]):  # Skip Enter Tag and Exit Reason
        #             if header == 'Avg Duration':
        #                 value = parse_duration(value)  # 平均持仓时间：基于进入标签和退出原因的交易平均持续时间（小时）
        #                 header_display = 'Avg_Duration_(平均持仓时间)'
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
        #                 header_display = 'Win_Draw_Loss_Win%_(混合标签胜平负及胜率)'
        #             elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
        #                 try:
        #                     value = float(value)
        #                 except:
        #                     pass
        #             # Add Chinese explanation to header
        #             header_key = header.replace(' ', '_')
        #             if header == 'Trades':
        #                 header_display = f"Trades_(混合标签交易次数)"  # 混合标签交易次数：基于进入标签和退出原因的交易总数
        #             elif header == 'Avg Profit %':
        #                 header_display = f"Avg_Profit_%_(混合标签平均利润百分比)"  # 混合标签平均利润百分比：基于进入标签和退出原因的平均利润率
        #             elif header == 'Tot Profit USDT':
        #                 header_display = f"Tot_Profit_USDT_(混合标签总利润USDT)"  # 混合标签总利润USDT：基于进入标签和退出原因的总盈利（USDT）
        #             elif header == 'Tot Profit %':
        #                 header_display = f"Tot_Profit_%_(混合标签总利润百分比)"  # 混合标签总利润百分比：基于进入标签和退出原因的总盈利百分比
        #             elif header == 'Win  Draw  Loss  Win%':
        #                 header_display = f"Win_Draw_Loss_Win%_(混合标签胜平负及胜率)"  # 混合标签胜平负及胜率：基于进入标签和退出原因的胜、平、负次数及胜率
        #             else:
        #                 header_display = f"{header_key}_({header})"
        #             data[f"{prefix}{header_display}"] = value
        
        # Parse SUMMARY METRICS
        elif line == 'SUMMARY METRICS':
            i += 1  # Skip the top border
            metrics, i = parse_summary_metrics(lines, i)
            for metric, value in metrics.items():
                key = metric.replace(' ', '_').replace('%', 'Pct').replace('/', '_').replace('(', '').replace(')', '')
                if 'Duration' in metric:
                    value = parse_duration(value)  # 平均持仓时间：总结报告中的交易平均持续时间（小时）
                    metric_display = f"{key}_(平均持仓时间)"
                elif 'date' in metric.lower() or 'from' in metric.lower() or 'to' in metric.lower() or 'start' in metric.lower() or 'end' in metric.lower():
                    try:
                        value = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')  # 日期时间：回测的开始或结束时间
                        metric_display = f"{key}_(日期时间)"
                    except:
                        try:
                            value = value.split()[0]
                            value = float(value)
                            metric_display = f"{key}_({metric})"
                        except:
                            metric_display = f"{key}_({metric})"
                elif metric == 'Days win draw lose':
                    value = parse_win_draw_loss(value) if '/' in value else value  # 胜平负天数：添加中文注解如果适用
                    metric_display = f"{key}_(胜平负天数)"
                else:
                    # Extract number if possible
                    match = re.search(r'[-+]?\d*\.?\d+', value)
                    if match:
                        value = float(match.group())
                    elif 'USDT' in value:
                        value = float(value.split()[0])  # 金额：如USDT表示的货币金额
                    # Add Chinese explanation to metric
                    if metric == 'Backtesting from':
                        metric_display = f"Backtesting_from_(回测开始时间)"  # 回测开始时间：回测的起始日期和时间
                    elif metric == 'Backtesting to':
                        metric_display = f"Backtesting_to_(回测结束时间)"  # 回测结束时间：回测的结束日期和时间
                    elif metric == 'Trading Mode':
                        metric_display = f"Trading_Mode_(交易模式)"  # 交易模式：回测使用的交易模式（如现货、期货）
                    elif metric == 'Max open trades':
                        metric_display = f"Max_open_trades_(最大同时持仓交易数)"  # 最大同时持仓交易数：回测中允许的最大同时开放交易数量
                    elif metric == 'Total Daily Avg Trades':
                        metric_display = f"Total_Daily_Avg_Trades_(日均交易次数)"  # 日均交易次数：每日平均交易数量
                    elif metric == 'Starting balance':
                        metric_display = f"Starting_balance_(初始余额)"  # 初始余额：回测开始时的账户余额
                    elif metric == 'Final balance':
                        metric_display = f"Final_balance_(最终余额)"  # 最终余额：回测结束时的账户余额
                    elif metric == 'Absolute profit':
                        metric_display = f"Absolute_profit_(绝对利润)"  # 绝对利润：回测期间的总绝对盈利
                    elif metric == 'Total profit %':
                        metric_display = f"Total_profit_Pct_(总利润百分比)"  # 总利润百分比：整个回测的总盈利百分比
                    elif metric == 'CAGR %':
                        metric_display = f"CAGR_Pct_(年化收益率)"  # 年化收益率：复合年增长率
                    elif metric == 'Sortino':
                        metric_display = f"Sortino_(索提诺比率)"  # 索提诺比率：衡量下行风险调整后的回报
                    elif metric == 'Sharpe':
                        metric_display = f"Sharpe_(夏普比率)"  # 夏普比率：衡量风险调整后的回报
                    elif metric == 'Calmar':
                        metric_display = f"Calmar_(卡尔马比率)"  # 卡尔马比率：衡量最大回撤调整后的回报
                    elif metric == 'SQN':
                        metric_display = f"SQN_(系统质量数)"  # 系统质量数：衡量交易系统质量的指标
                    elif metric == 'Profit factor':
                        metric_display = f"Profit_factor_(盈利因子)"  # 盈利因子：总盈利与总亏损的比率
                    elif metric == 'Expectancy Ratio':
                        metric_display = f"Expectancy_Ratio_(期望比率)"  # 期望比率：每笔交易的平均预期回报
                    elif metric == 'Avg. daily profit':
                        metric_display = f"Avg._daily_profit_(日均利润)"  # 日均利润：每日平均盈利金额
                    elif metric == 'Avg. stake amount':
                        metric_display = f"Avg._stake_amount_(平均下注金额)"  # 平均下注金额：每笔交易的平均投入金额
                    elif metric == 'Total trade volume':
                        metric_display = f"Total_trade_volume_(总交易量)"  # 总交易量：回测期间的总交易金额
                    elif metric == 'Best Pair':
                        metric_display = f"Best_Pair_(最佳交易对)"  # 最佳交易对：表现最好的交易货币对
                    elif metric == 'Worst Pair':
                        metric_display = f"Worst_Pair_(最差交易对)"  # 最差交易对：表现最差的交易货币对
                    elif metric == 'Best trade':
                        metric_display = f"Best_trade_(最佳交易)"  # 最佳交易：盈利最高的单笔交易
                    elif metric == 'Worst trade':
                        metric_display = f"Worst_trade_(最差交易)"  # 最差交易：亏损最高的单笔交易
                    elif metric == 'Best day':
                        metric_display = f"Best_day_(最佳交易日)"  # 最佳交易日：盈利最高的交易日
                    elif metric == 'Worst day':
                        metric_display = f"Worst_day_(最差交易日)"  # 最差交易日：亏损最高的交易日
                    elif metric == 'Days win draw lose':
                        metric_display = f"Days_win_draw_lose_(胜平负天数)"  # 胜平负天数：盈利、持平、亏损的天数统计
                    elif metric == 'Min Max Avg. Duration Winners':
                        metric_display = f"Min_Max_Avg._Duration_Winners_(赢家交易的最小最大平均持仓时间)"  # 赢家交易的最小最大平均持仓时间：盈利交易的持仓时间统计
                    elif metric == 'Min Max Avg. Duration Losers':
                        metric_display = f"Min_Max_Avg._Duration_Losers_(输家交易的最小最大平均持仓时间)"  # 输家交易的最小最大平均持仓时间：亏损交易的持仓时间统计
                    elif metric == 'Max Consecutive Wins / Loss':
                        metric_display = f"Max_Consecutive_Wins___Loss_(最大连续盈利亏损次数)"  # 最大连续盈利亏损次数：连续盈利或亏损的最大次数
                    elif metric == 'Rejected Entry signals':
                        metric_display = f"Rejected_Entry_signals_(拒绝的进入信号)"  # 拒绝的进入信号：被拒绝的交易进入信号数量
                    elif metric == 'Entry/Exit Timeouts':
                        metric_display = f"Entry_Exit_Timeouts_(进入退出超时)"  # 进入退出超时：交易进入或退出超时的次数
                    elif metric == 'Min balance':
                        metric_display = f"Min_balance_(最低余额)"  # 最低余额：回测期间的最低账户余额
                    elif metric == 'Max balance':
                        metric_display = f"Max_balance_(最高余额)"  # 最高余额：回测期间的最高账户余额
                    elif metric == 'Max % of account underwater':
                        metric_display = f"Max_Pct_of_account_underwater_(账户最大亏损百分比)"  # 账户最大亏损百分比：账户最大回撤百分比
                    elif metric == 'Absolute drawdown':
                        metric_display = f"Absolute_drawdown_(绝对回撤)"  # 绝对回撤：账户余额的最大绝对下降金额
                    elif metric == 'Drawdown duration':
                        metric_display = f"Drawdown_duration_(回撤持续时间)"  # 回撤持续时间：最大回撤的持续时间
                    elif metric == 'Profit at drawdown start':
                        metric_display = f"Profit_at_drawdown_start_(回撤开始时利润)"  # 回撤开始时利润：回撤开始时的累计利润
                    elif metric == 'Profit at drawdown end':
                        metric_display = f"Profit_at_drawdown_end_(回撤结束时利润)"  # 回撤结束时利润：回撤结束时的累计利润
                    elif metric == 'Drawdown start':
                        metric_display = f"Drawdown_start_(回撤开始时间)"  # 回撤开始时间：最大回撤开始的日期时间
                    elif metric == 'Drawdown end':
                        metric_display = f"Drawdown_end_(回撤结束时间)"  # 回撤结束时间：最大回撤结束的日期时间
                    elif metric == 'Market change':
                        metric_display = f"Market_change_(市场变化)"  # 市场变化：回测期间市场的总体变化百分比
                    else:
                        metric_display = f"{key}_({metric})"
                data[f"Summary_{metric_display}"] = value
        
        # Parse STRATEGY SUMMARY
        elif line == 'STRATEGY SUMMARY':
            i += 1  # Skip the top border
            headers, rows, i = parse_table(lines, i)
            for row in rows:
                strategy = row[0]
                prefix = f"StrategySummary_{strategy}_"
                for header, value in zip(headers[1:], row[1:]):  # Skip Strategy column
                    if header == 'Avg Duration':
                        value = parse_duration(value)  # 平均持仓时间：策略总结中的交易平均持续时间（小时）  # 交易时间相加取平均
                        header_display = 'Avg_Duration_(平均持仓时间)' 
                    elif header == 'Drawdown':
                        try:
                            value = float(value.split()[0])  # 最大回撤：策略的最大资金回撤金额
                            header_display = 'Drawdown_(损失USDT_最大回撤)' # 最高点到最低点损失了多少钱
                        except:
                            pass
                    elif header == 'Win  Draw  Loss  Win%':
                        value = parse_win_draw_loss(value)  # 胜平负及胜率：添加中文注解
                        header_display = 'Win_Draw_Loss_Win%_(策略胜平负及胜率)'
                        # 胜了多少次？负了多次？平了多少次？胜的在总次数中的占比。
                    elif '%' in value or value.replace('.', '', 1).replace('-', '', 1).isdigit():
                        try:
                            value = float(value)
                        except:
                            pass
                    # Add Chinese explanation to header
                    header_key = header.replace(' ', '_')
                    if header == 'Trades':
                        header_display = f"Trades_(策略交易次数)"  # 策略交易次数：特定策略的交易总数 open->close是一次
                    elif header == 'Avg Profit %':
                        header_display = f"Avg_Profit_%_(策略平均利润百分比)"  # 策略平均利润百分比：特定策略的平均利润率 -> 收益率相加做平均
                    elif header == 'Tot Profit USDT':
                        header_display = f"Tot_Profit_USDT_(策略总利润USDT)" # 策略总利润USDT：特定策略的总盈利（USDT）-> 赚的usdt相加
                    elif header == 'Tot Profit %':
                        header_display = f"Tot_Profit_%_(策略总利润百分比)" # 策略总利润百分比：特定策略的总盈利百分比 ->  赚的usdt 在总usdt中占比
                    elif header == 'Win  Draw  Loss  Win%':
                        header_display = f"Win_Draw_Loss_Win%_(策略胜平负及胜率)"  # 策略胜平负及胜率：特定策略的胜、平、负次数及胜率
                    else:
                        header_display = f"{header_key}_({header})"
                    data[f"{prefix}{header_display}"] = value
        
        i += 1
    
    return data

def process_folder(input_folder, output_file):
    """Process all text files in the input folder and save to an Excel file."""
    all_data = []
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            with open(os.path.join(input_folder, filename), 'r', encoding='utf-8') as f:
                content = f.read()
                data = extract_data_from_file(content)
                data['Filename_(文件名)'] = filename  # 文件名：输入的回测报告文件名
                all_data.append(data)
    
    # Create DataFrame
    df = pd.DataFrame(all_data)
    
    # Reorder columns to have Filename and Strategy first
    cols = ['Filename_(文件名)', 'Strategy_(策略名称)'] + [col for col in df.columns if col not in ['Filename_(文件名)', 'Strategy_(策略名称)']]
    df = df[cols]
    df = df[df['Summary_CAGR_Pct_(年化收益率)'] > 0]
    df = df[df['Backtest_DOGE_USDT_Tot_Profit_%_(总利润百分比)'] > 10]

    

    # Save to Excel
    df.to_excel(output_file, index=False)
    print(f"Excel file saved as {output_file}")

# Example usage
if __name__ == "__main__":
    # 使用项目根目录的相对路径
    input_folder = PROJECT_ROOT / "backtest_txts" / "DOGE"  # Replace with your folder path
    output_file = PROJECT_ROOT / "backtest_results.xlsx"  # Output Excel file
    process_folder(str(input_folder), str(output_file))