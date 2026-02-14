import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import backtest_slope_strategy
from data_processing import calculate_rsrs_slope


def plot_parameter_sensitivity_strategy_curves(df, n_range=None):
    """绘制不同N参数下的策略曲线"""
    n_range = n_range or CONFIG['PARAMETER_SENSITIVITY_N_RANGE']
    
    plt.figure(figsize=(12, 8))
    
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    dates = pd.to_datetime(df['date'])
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='black', linewidth=2)
    
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan', 'magenta']
    
    analysis_logger.info("\n参数敏感性分析 - 策略曲线:")
    
    for i, n in enumerate(n_range):
        df_with_slope = calculate_rsrs_slope(df, n=n)
        slope_signals = backtest_slope_strategy(df_with_slope, buy_threshold=CONFIG['SLOPE_BUY_THRESHOLD'],
                                               sell_threshold=CONFIG['SLOPE_SELL_THRESHOLD'])
        values = calculate_portfolio_value(df_with_slope, slope_signals)
        
        plt.plot(dates, values, label=f'N={n}', color=colors[i % len(colors)], linewidth=1.5)
        
        final_value = values[-1]
        analysis_logger.info(f"N={n}: 最终净值={final_value:.4f}")
    
    plt.title('RSRS Slope Strategy Performance with Different N Parameters (N=14 to 24)', fontsize=14)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=8, loc='upper left')
    plt.grid(True, alpha=0.3)
    
    analysis_logger.info("-" * 50)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure11_slope_strategy_parameter_curves.png')
    plt.close()
    
    analysis_logger.info("已生成图表: figure11_slope_strategy_parameter_curves.png")


def plot_parameter_sensitivity_n(df, n_range=None):
    """绘制N参数敏感性分析图"""
    n_range = n_range or CONFIG['PARAMETER_SENSITIVITY_N_RANGE']
    
    final_values = []
    
    analysis_logger.info("\n参数敏感性分析 - 最终净值:")
    
    for n in n_range:
        df_with_slope = calculate_rsrs_slope(df, n=n)
        slope_signals = backtest_slope_strategy(df_with_slope, buy_threshold=CONFIG['SLOPE_BUY_THRESHOLD'],
                                               sell_threshold=CONFIG['SLOPE_SELL_THRESHOLD'])
        values = calculate_portfolio_value(df_with_slope, slope_signals)
        final_value = values[-1]
        final_values.append(final_value)
        
        analysis_logger.info(f"N={n}: {final_value:.4f}")
    
    analysis_logger.info("-" * 50)
    
    plt.figure(figsize=(12, 8))
    plt.scatter(n_range, final_values, s=80, color='blue', alpha=0.7)
    plt.title('RSRS Slope Strategy Parameter Sensitivity (N)', fontsize=14)
    plt.xlabel('Parameter N (Slope Calculation Window)', fontsize=12)
    plt.ylabel('Final Net Value', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 12)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure12_slope_strategy_parameter_sensitivity_n.png')
    plt.close()
    
    analysis_logger.info("已生成图表: figure12_slope_strategy_parameter_sensitivity_n.png")
    
    return dict(zip(n_range, final_values))


def plot_optimized_strategies_parameter_sensitivity_m(df, m_range=None):
    """绘制不同优化指标策略参数敏感性（标准分计算周期M）- 图28"""
    
    m_range = m_range or [450, 500, 550, 600, 650, 700, 750, 800]
    
    # 存储结果
    single_strategy_values = []      # 单指标策略
    price_optimized_values = []      # 价格优化策略  
    volume_optimized_values = []     # 交易量优化策略
    
    analysis_logger.info("\n=== 优化策略参数敏感性分析 (M) ===")
    analysis_logger.info("M参数范围: " + ", ".join(map(str, m_range)))
    
    for m in m_range:
        analysis_logger.info(f"\n计算 M={m} 的策略表现...")
        
        # 1. 单指标策略（标准分策略）
        from data_processing import calculate_standard_score
        df_single = calculate_standard_score(df, m=m)
        from strategy import backtest_standard_score_strategy
        single_signals, _ = backtest_standard_score_strategy(df_single)
        single_values = calculate_portfolio_value(df_single, single_signals)
        single_strategy_values.append(single_values[-1])
        
        # 2. 价格优化策略
        from strategy import backtest_price_optimized_standard_score_strategy
        price_signals, _ = backtest_price_optimized_standard_score_strategy(df_single)
        price_values = calculate_portfolio_value(df_single, price_signals)
        price_optimized_values.append(price_values[-1])
        
        # 3. 交易量优化策略
        from data_processing import calculate_volume_correlation
        df_volume = calculate_volume_correlation(df_single)
        from strategy import backtest_volume_optimized_standard_score_strategy
        volume_signals, _ = backtest_volume_optimized_standard_score_strategy(df_volume)
        volume_values = calculate_portfolio_value(df_volume, volume_signals)
        volume_optimized_values.append(volume_values[-1])
        
        analysis_logger.info(f"M={m}: 单指标={single_values[-1]:.3f}, 价格优化={price_values[-1]:.3f}, 交易量优化={volume_values[-1]:.3f}")
    
    # 绘制图表
    plt.figure(figsize=(12, 8))
    
    plt.plot(m_range, single_strategy_values, marker='o', label='Single Indicator', color='blue', linewidth=2, markersize=6)
    plt.plot(m_range, price_optimized_values, marker='s', label='Price Optimized', color='red', linewidth=2, markersize=6)
    plt.plot(m_range, volume_optimized_values, marker='^', label='Volume Correlation Optimized', color='green', linewidth=2, markersize=6)
    
    plt.title('Parameter Sensitivity of Different Optimized Indicator Strategies \n(Standard Score Calculation Period M)', fontsize=14)
    plt.xlabel('Parameter M (Standard Score Calculation Window)', fontsize=12)
    plt.ylabel('Final Net Value', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # 添加数据标签
    for i, m in enumerate(m_range):
        plt.annotate(f'{single_strategy_values[i]:.1f}', (m, single_strategy_values[i]), 
                    textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        plt.annotate(f'{price_optimized_values[i]:.1f}', (m, price_optimized_values[i]), 
                    textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
        plt.annotate(f'{volume_optimized_values[i]:.1f}', (m, volume_optimized_values[i]), 
                    textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure28_optimized_strategies_parameter_sensitivity_m.png')
    plt.close()
    
    # 记录详细结果（对应研报表7）
    analysis_logger.info("\n" + "="*60)
    analysis_logger.info("优化策略参数敏感性结果 (对应研报表7)")
    analysis_logger.info("="*60)
    analysis_logger.info("M参数 | 单指标净值 | 价格优化净值 | 相关性优化净值")
    analysis_logger.info("-" * 55)
    
    for i, m in enumerate(m_range):
        analysis_logger.info(f"{m:5d} | {single_strategy_values[i]:11.3f} | {price_optimized_values[i]:12.3f} | {volume_optimized_values[i]:15.3f}")
    
    # 找到最佳参数
    best_single_m = m_range[single_strategy_values.index(max(single_strategy_values))]
    best_price_m = m_range[price_optimized_values.index(max(price_optimized_values))]
    best_volume_m = m_range[volume_optimized_values.index(max(volume_optimized_values))]
    
    analysis_logger.info("\n最佳参数:")
    analysis_logger.info(f"单指标策略最佳M: {best_single_m}, 净值: {max(single_strategy_values):.3f}")
    analysis_logger.info(f"价格优化策略最佳M: {best_price_m}, 净值: {max(price_optimized_values):.3f}")
    analysis_logger.info(f"交易量优化策略最佳M: {best_volume_m}, 净值: {max(volume_optimized_values):.3f}")
    
    analysis_logger.info("Generated chart: figure28_optimized_strategies_parameter_sensitivity_m.png")
    
    return {
        'm_range': m_range,
        'single_strategy': single_strategy_values,
        'price_optimized': price_optimized_values,
        'volume_optimized': volume_optimized_values
    }