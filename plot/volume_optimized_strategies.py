import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import (
    backtest_volume_optimized_standard_score_strategy,
    backtest_volume_optimized_modified_score_strategy,
    backtest_volume_optimized_right_skewed_strategy,
)
from backtest import calculate_strategy_statistics, log_strategy_statistics

def plot_volume_optimized_strategies_comparison(df):
    """绘制各标准分指标策略在交易量相关性优化下的净值比较（图27）"""
    
    analysis_logger.info("\n=== Volume Optimized Strategies Analysis ===")
    
    # 计算各个交易量优化策略的信号
    analysis_logger.info("Calculating Volume Optimized Standard Score Strategy...")
    standard_signals, _ = backtest_volume_optimized_standard_score_strategy(df)
    
    analysis_logger.info("Calculating Volume Optimized Modified Score Strategy...")
    modified_signals, _ = backtest_volume_optimized_modified_score_strategy(df)
    
    analysis_logger.info("Calculating Volume Optimized Right Skewed Strategy...")
    right_skewed_signals, _ = backtest_volume_optimized_right_skewed_strategy(df)
    
    # 策略列表
    strategy_list = [
        ('Correlation Optimized Standard Score', standard_signals, 'blue', True),
        ('Correlation Optimized Modified Score', modified_signals, 'green', True),
        ('Correlation Optimized Right Skewed Score', right_skewed_signals, 'red', True),
    ]
    
    # 绘图
    plt.figure(figsize=(12, 8))
    
    dates = pd.to_datetime(df['date'])
    
    # 绘制买入持有基准
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='black', linewidth=2)
    
    # 绘制各个策略
    for strategy_name, signals, color, should_compute_stats in strategy_list:
        values = calculate_portfolio_value(df, signals)
        plt.plot(dates, values, label=strategy_name, color=color, linewidth=1.5)
        
        # 计算统计信息
        if should_compute_stats:
            stats = calculate_strategy_statistics(df, signals, strategy_name)
            log_strategy_statistics(stats)
    
    plt.title('Performance of Different RSRS Standard Score Strategies \nwith Volume Correlation Optimization on HS300 Index', fontsize=14)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure27_volume_optimized_strategies_comparison.png')
    plt.close()
    
    # 记录最终净值对比
    standard_values = calculate_portfolio_value(df, standard_signals)
    modified_values = calculate_portfolio_value(df, modified_signals)
    right_skewed_values = calculate_portfolio_value(df, right_skewed_signals)
    
    analysis_logger.info("\nVolume Optimized Strategies Final Net Value Comparison:")
    analysis_logger.info(f"HS300 Buy & Hold: {bh_values[-1]:.2f}")
    analysis_logger.info(f"Correlation Optimized Standard Score: {standard_values[-1]:.2f}")
    analysis_logger.info(f"Correlation Optimized Modified Score: {modified_values[-1]:.2f}")
    analysis_logger.info(f"Correlation Optimized Right Skewed Score: {right_skewed_values[-1]:.2f}")
    analysis_logger.info("-" * 50)
    
    analysis_logger.info("Generated chart: figure27_volume_optimized_strategies_comparison.png")