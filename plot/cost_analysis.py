import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import backtest_slope_strategy, backtest_standard_score_strategy
from strategy import backtest_right_skewed_standard_score_strategy


def _plot_strategy_with_costs(df, signals, strategy_name, colors, figure_name):
    """
    通用的成本分析绘图函数
    
    参数:
        df: 数据框
        signals: 交易信号列表
        strategy_name: 策略名称
        colors: 颜色列表
        figure_name: 图表文件名
    """
    cost_rates = CONFIG['COST_RATES']
    cost_labels = CONFIG['COST_LABELS']
    
    plt.figure(figsize=(12, 8))
    
    # 绘制买入持有基准
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    dates = pd.to_datetime(df['date'])
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='orange', linewidth=1.5)
    
    # 绘制不同成本下的策略表现
    for cost_rate, color, label in zip(cost_rates, colors, cost_labels):
        values = calculate_portfolio_value(df, signals, cost_rate=cost_rate)
        plt.plot(dates, values, label=label, color=color, linewidth=1.5)
    
    plt.title(f'{strategy_name} Performance with Different Transaction Costs', fontsize=14)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # 记录最终净值
    analysis_logger.info(f"\n{strategy_name} final net value with different costs:")
    for cost_rate, label in zip(cost_rates, cost_labels):
        final_value = calculate_portfolio_value(df, signals, cost_rate=cost_rate)[-1]
        analysis_logger.info(f"{label}: {final_value:.2f}")
    
    bh_final = bh_values[-1]
    analysis_logger.info(f"HS300 Buy & Hold: {bh_final:.2f}")
    analysis_logger.info("-" * 50)
    
    # 保存图表
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/{figure_name}')
    plt.close()
    
    analysis_logger.info(f"已生成图表: {figure_name}")


def plot_slope_strategy_with_costs(df):
    """绘制斜率策略在不同成本下的表现"""
    slope_signals = backtest_slope_strategy(
        df, 
        buy_threshold=CONFIG['SLOPE_BUY_THRESHOLD'], 
        sell_threshold=CONFIG['SLOPE_SELL_THRESHOLD']
    )
    
    _plot_strategy_with_costs(
        df, 
        slope_signals, 
        'RSRS Slope Strategy',
        colors=['purple', 'red', 'grey'],
        figure_name='figure10_slope_strategy_with_costs.png'
    )


def plot_standard_score_strategy_with_costs(df):
    """绘制标准分策略在不同成本下的表现"""
    score_signals, _ = backtest_standard_score_strategy(df)
    
    _plot_strategy_with_costs(
        df, 
        score_signals, 
        'RSRS Standard Score Strategy',
        colors=['black', 'blue', 'green'],
        figure_name='figure13_standard_score_strategy_with_costs.png'
    )


def plot_right_skewed_strategy_with_costs(df):
    """绘制右偏标准分策略在不同成本下的表现"""
    right_skewed_signals, _ = backtest_right_skewed_standard_score_strategy(df)
    
    _plot_strategy_with_costs(
        df, 
        right_skewed_signals, 
        'Right Skewed Standard Score Strategy',
        colors=['black', 'blue', 'green'],
        figure_name='figure24_right_skewed_strategy_with_costs.png'
    )
    
    # 额外的交易次数统计信息
    trade_count = len([i for i in range(1, len(right_skewed_signals)) 
                      if right_skewed_signals[i] != right_skewed_signals[i-1]])
    analysis_logger.info(f"Right Skewed Strategy Trade Count: {trade_count}")


def plot_price_optimized_right_skewed_with_costs(df):
    """绘制价格优化右偏标准分指标策略在不同成本下的净值表现（图26）"""
    
    from strategy import backtest_price_optimized_right_skewed_strategy
    
    # 计算价格优化右偏标准分策略信号
    analysis_logger.info("Calculating Price Optimized Right Skewed Strategy signals...")
    signals, _ = backtest_price_optimized_right_skewed_strategy(df)
    
    cost_rates = CONFIG['COST_RATES']
    cost_labels = CONFIG['COST_LABELS']
    
    plt.figure(figsize=(12, 8))
    
    # 绘制买入持有基准
    bh_signals = buy_hold_strategy(df)
    bh_values = calculate_portfolio_value(df, bh_signals)
    dates = pd.to_datetime(df['date'])
    plt.plot(dates, bh_values, label='HS300 Buy & Hold', color='orange', linewidth=1.5)
    
    # 绘制不同成本下的策略表现
    colors = ['black', 'blue', 'green']
    for cost_rate, color, label in zip(cost_rates, colors, cost_labels):
        values = calculate_portfolio_value(df, signals, cost_rate=cost_rate)
        plt.plot(dates, values, label=label, color=color, linewidth=1.5)
    
    plt.title('Price Optimized Right Skewed Standard Score Strategy Performance \nwith Different Transaction Costs', fontsize=14)
    plt.ylabel('Net Value', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.legend(fontsize=10)
    plt.grid(True, alpha=0.3)
    
    # 记录最终净值
    analysis_logger.info(f"\nPrice Optimized Right Skewed Strategy final net value with different costs:")
    for cost_rate, label in zip(cost_rates, cost_labels):
        final_value = calculate_portfolio_value(df, signals, cost_rate=cost_rate)[-1]
        analysis_logger.info(f"{label}: {final_value:.2f}")
    
    analysis_logger.info(f"HS300 Buy & Hold: {bh_values[-1]:.2f}")
    analysis_logger.info("-" * 50)
    
    # 记录交易次数统计
    trade_count = len([i for i in range(1, len(signals)) if signals[i] != signals[i-1]])
    analysis_logger.info(f"Price Optimized Right Skewed Strategy Trade Count: {trade_count}")
    
    # 保存图表
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure26_price_optimized_right_skewed_with_costs.png')
    plt.close()
    
    analysis_logger.info(f"Generated chart: figure26_price_optimized_right_skewed_with_costs.png")