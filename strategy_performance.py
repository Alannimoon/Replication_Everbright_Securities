import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import (
    backtest_slope_strategy,
    backtest_standard_score_strategy,
    backtest_modified_standard_score_strategy,
    backtest_right_skewed_standard_score_strategy,
    _get_start_index,
)
from backtest import calculate_strategy_statistics, log_strategy_statistics


def _plot_strategy_comparison(df, strategy_list, title, figure_name, compute_stats=False):
    """
    通用的策略对比绘图函数
    
    参数:
        df: 数据框
        strategy_list: 策略列表，每个元素为 (name, signals, color, should_log)
        title: 图表标题
        figure_name: 图表文件名
        compute_stats: 是否计算统计信息
    """
    plt.figure(figsize=(12, 8))
    
    dates = pd.to_datetime(df['date'])
    
    # 绘制买入持有基准
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='black', linewidth=2)
    
    analysis_logger.info(f"\n{title}:")
    
    # 绘制各个策略
    for strategy_name, signals, color, should_compute_stats in strategy_list:
        values = calculate_portfolio_value(df, signals)
        plt.plot(dates, values, label=strategy_name, color=color, linewidth=1.5)
        
        # 如果需要，计算统计信息
        if compute_stats and should_compute_stats:
            stats = calculate_strategy_statistics(df, signals, strategy_name)
            log_strategy_statistics(stats)
    
    plt.title(title, fontsize=14)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/{figure_name}')
    plt.close()
    
    analysis_logger.info(f"已生成图表: {figure_name}")


def plot_strategy_performance(df):
    """绘制基础策略性能对比（斜率 + 标准分 + 买入持有）"""
    
    # 生成信号
    slope_signals = backtest_slope_strategy(
        df, 
        buy_threshold=CONFIG['SLOPE_BUY_THRESHOLD'],
        sell_threshold=CONFIG['SLOPE_SELL_THRESHOLD']
    )
    score_signals, _ = backtest_standard_score_strategy(df)
    
    # 策略列表：(名称, 信号, 颜色, 是否计算统计)
    strategy_list = [
        ('slope strategy', slope_signals, 'gray', True),
        ('score strategy', score_signals, 'purple', True),
    ]
    
    _plot_strategy_comparison(
        df,
        strategy_list,
        'performance of RSRS strategies on hs300 index (from 2005-02-18 to 2017-03-31)',
        'figure9_rsrs_strategy_performance.png',
        compute_stats=True
    )
    
    # 记录最终净值对比
    slope_values = calculate_portfolio_value(df, slope_signals)
    score_values = calculate_portfolio_value(df, score_signals)
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    
    analysis_logger.info("\n策略表现对比:")
    analysis_logger.info(f"买入持有策略: {bh_values[-1]:.2f}")
    analysis_logger.info(f"斜率指标策略: {slope_values[-1]:.2f}")
    analysis_logger.info(f"标准分策略: {score_values[-1]:.2f}")
    analysis_logger.info("-" * 50)


def plot_different_score_strategies_comparison(df, compute_stats=True):
    """绘制不同分数策略的对比（标准分 + 修正 + 右偏 + 买入持有）"""
    
    analysis_logger.info("\n不同分数策略对比:")
    
    # 计算各个策略的信号
    analysis_logger.info("计算Standard Score Strategy...")
    standard_signals, _ = backtest_standard_score_strategy(df)
    
    analysis_logger.info("计算Modified Standard Score Strategy...")
    modified_signals, _ = backtest_modified_standard_score_strategy(df)
    
    analysis_logger.info("计算Right Skewed Standard Score Strategy...")
    right_skewed_signals, _ = backtest_right_skewed_standard_score_strategy(df)
    
    # 策略列表：(名称, 信号, 颜色, 是否计算统计)
    strategy_list = [
        ('Standard Score', standard_signals, 'blue', compute_stats),
        ('Modified Score', modified_signals, 'green', compute_stats),
        ('Right Skewed Score', right_skewed_signals, 'red', compute_stats),
    ]
    
    _plot_strategy_comparison(
        df,
        strategy_list,
        'Comparison of Different RSRS Standard Score Strategies on HS300 Index',
        'figure23_different_score_strategies_comparison.png',
        compute_stats=compute_stats
    )
    
    # 记录最终净值对比
    standard_values = calculate_portfolio_value(df, standard_signals)
    modified_values = calculate_portfolio_value(df, modified_signals)
    right_skewed_values = calculate_portfolio_value(df, right_skewed_signals)
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    
    analysis_logger.info("\n最终净值对比:")
    analysis_logger.info(f"HS300 Buy & Hold: {bh_values[-1]:.2f}")
    analysis_logger.info(f"Standard Score Strategy: {standard_values[-1]:.2f}")
    analysis_logger.info(f"Modified Score Strategy: {modified_values[-1]:.2f}")
    analysis_logger.info(f"Right Skewed Score Strategy: {right_skewed_values[-1]:.2f}")
    analysis_logger.info("-" * 50)


import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import (
    backtest_slope_strategy,
    backtest_standard_score_strategy,
    backtest_modified_standard_score_strategy,
    backtest_right_skewed_standard_score_strategy,
    backtest_price_optimized_right_skewed_strategy,
    backtest_volume_optimized_right_skewed_strategy
)

def plot_all_strategies_comparison(df):
    """绘制所有策略净值曲线对比（图32）"""
    
    analysis_logger.info("\n=== All Strategies Comparison ===")
    
    # 计算所有策略的净值
    strategies_data = []
    
    # 1. 斜率策略
    analysis_logger.info("Calculating Slope Strategy...")
    slope_signals = backtest_slope_strategy(df)
    slope_values = calculate_portfolio_value(df, slope_signals)
    strategies_data.append(('Slope Strategy', slope_signals, slope_values, 'gray'))
    
    # 2. 标准分策略
    analysis_logger.info("Calculating Standard Score Strategy...")
    standard_signals, _ = backtest_standard_score_strategy(df)
    standard_values = calculate_portfolio_value(df, standard_signals)
    strategies_data.append(('Standard Score', standard_signals, standard_values, 'blue'))
    
    # 3. 修正标准分策略
    analysis_logger.info("Calculating Modified Standard Score Strategy...")
    modified_signals, _ = backtest_modified_standard_score_strategy(df)
    modified_values = calculate_portfolio_value(df, modified_signals)
    strategies_data.append(('Modified Score', modified_signals, modified_values, 'green'))
    
    # 4. 右偏标准分策略
    analysis_logger.info("Calculating Right Skewed Standard Score Strategy...")
    right_skewed_signals, _ = backtest_right_skewed_standard_score_strategy(df)
    right_skewed_values = calculate_portfolio_value(df, right_skewed_signals)
    strategies_data.append(('Right Skewed Score', right_skewed_signals, right_skewed_values, 'orange'))
    
    # 5. 价格优化右偏标准分策略
    analysis_logger.info("Calculating Price Optimized Right Skewed Strategy...")
    price_optimized_signals, _ = backtest_price_optimized_right_skewed_strategy(df)
    price_optimized_values = calculate_portfolio_value(df, price_optimized_signals)
    strategies_data.append(('Price Optimized Right Skewed', price_optimized_signals, price_optimized_values, 'red'))
    
    # 6. 交易量优化右偏标准分策略
    analysis_logger.info("Calculating Volume Optimized Right Skewed Strategy...")
    from data_processing import calculate_volume_correlation
    df_volume = calculate_volume_correlation(df)
    volume_optimized_signals, _ = backtest_volume_optimized_right_skewed_strategy(df_volume)
    volume_optimized_values = calculate_portfolio_value(df, volume_optimized_signals)
    strategies_data.append(('Volume Optimized Right Skewed', volume_optimized_signals, volume_optimized_values, 'purple'))
    
    # 买入持有基准
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    
    # 绘图
    plt.figure(figsize=(14, 8))
    dates = pd.to_datetime(df['date'])
    
    # 绘制买入持有基准
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='black', linewidth=2.5)
    
    # 绘制所有策略
    for strategy_name, signals, values, color in strategies_data:
        plt.plot(dates, values, label=strategy_name, color=color, linewidth=1.5)
    
    plt.title('Comparison of All RSRS Strategies Performance on HS300 Index', fontsize=16)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=9, loc='upper left')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure32_all_strategies_comparison.png', dpi=300)
    plt.close()
    
    # 记录最终净值对比
    analysis_logger.info("\n" + "="*60)
    analysis_logger.info("All Strategies Final Net Value Comparison")
    analysis_logger.info("="*60)
    analysis_logger.info(f"{'Strategy':<30} {'Final Value':<12} {'Outperformance':<15}")
    analysis_logger.info("-" * 60)
    
    analysis_logger.info(f"{'HS300 Buy & Hold':<30} {bh_values[-1]:<12.2f} {'-':<15}")
    
    for strategy_name, signals, values, color in strategies_data:
        final_value = values[-1]
        outperformance = (final_value - bh_values[-1]) / bh_values[-1] * 100
        analysis_logger.info(f"{strategy_name:<30} {final_value:<12.2f} {outperformance:+.1f}%")
    
    # 记录交易次数对比
    analysis_logger.info("\nTrade Count Comparison:")
    analysis_logger.info(f"{'Strategy':<30} {'Trade Count':<12}")
    analysis_logger.info("-" * 45)
    
    for strategy_name, signals, values, color in strategies_data:
        trade_count = len([i for i in range(1, len(signals)) if signals[i] != signals[i-1]])
        analysis_logger.info(f"{strategy_name:<30} {trade_count:<12}")
    
    analysis_logger.info("Generated chart: figure32_all_strategies_comparison.png")
    
    return strategies_data