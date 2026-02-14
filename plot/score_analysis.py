import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from config import CONFIG
from logger_config import analysis_logger


def _calculate_score_and_return(df, score_column, forward_days=10):
    """
    计算分数和未来收益/上涨概率
    
    参数:
        df: 数据框
        score_column: 分数列名
        forward_days: 向前看的天数
    
    返回:
        scores: 分数列表
        up_probs: 上涨概率列表
        expected_returns: 预期收益列表
    """
    scores = []
    up_probs = []
    expected_returns = []
    
    for i in range(len(df) - forward_days):
        current_score = df[score_column].iloc[i]
        if pd.isna(current_score):
            continue
        
        future_prices = df['close'].iloc[i+1:i+forward_days+1]
        if len(future_prices) < forward_days:
            continue
        
        future_return = (future_prices.iloc[-1] - df['close'].iloc[i]) / df['close'].iloc[i]
        up_prob = 1 if future_return > 0 else 0
        
        scores.append(current_score)
        up_probs.append(up_prob)
        expected_returns.append(future_return)
    
    return scores, up_probs, expected_returns


def _calculate_correlation(data, score_col, value_col):
    """
    计算相关系数
    
    参数:
        data: 数据框，包含score_col和value_col两列
        score_col: 分数列名
        value_col: 值列名（上涨概率或收益）
    
    返回:
        corr_right: 右侧(score > 0)的相关系数
        corr_left: 左侧(score <= 0)的相关系数
        corr_total: 总体相关系数
    """
    right_mask = data[score_col] > 0
    left_mask = data[score_col] <= 0
    
    corr_right = data[right_mask][score_col].corr(data[right_mask][value_col]) if right_mask.sum() > 0 else np.nan
    corr_left = data[left_mask][score_col].corr(data[left_mask][value_col]) if left_mask.sum() > 0 else np.nan
    corr_total = data[score_col].corr(data[value_col])
    
    return corr_right, corr_left, corr_total


def _plot_score_analysis(df, score_column, metric_type, forward_days, 
                         bin_width, title_prefix, figure_name, color):
    """
    通用的分数分析绘图函数
    
    参数:
        df: 数据框
        score_column: 分数列名
        metric_type: 指标类型，'up_probability' 或 'expected_return'
        forward_days: 向前看的天数
        bin_width: 分箱宽度
        title_prefix: 标题前缀
        figure_name: 图片保存名
        color: 柱子颜色
    """
    if score_column not in df.columns:
        analysis_logger.warning(f"列 '{score_column}' 不存在于数据框中")
        return
    
    scores, up_probs, expected_returns = _calculate_score_and_return(df, score_column, forward_days)
    
    if not scores:
        analysis_logger.warning(f"没有有效的 {score_column} 数据")
        return
    
    if metric_type == 'up_probability':
        data = pd.DataFrame({'score': scores, 'metric': up_probs})
        metric_label = f'Up Probability (Next {forward_days} Days)'
        correlation_label = f'{title_prefix} Score vs Up Probability'
    else:  # expected_return
        data = pd.DataFrame({'score': scores, 'metric': expected_returns})
        metric_label = f'Expected Return (Next {forward_days} Days)'
        correlation_label = f'{title_prefix} Score vs Expected Return'
    
    # 计算分箱统计
    min_score = data['score'].min()
    max_score = data['score'].max()
    bins = np.arange(min_score, max_score + bin_width, bin_width)
    data['score_bin'] = pd.cut(data['score'], bins=bins)
    bin_stats = data.groupby('score_bin').agg({'metric': 'mean'}).reset_index()
    bin_stats['bin_left'] = [interval.left for interval in bin_stats['score_bin']]
    
    # 计算相关系数
    corr_right, corr_left, corr_total = _calculate_correlation(data, 'score', 'metric')
    
    # 记录到日志
    analysis_logger.info(f"\nCorrelation coefficients - {correlation_label}:")
    analysis_logger.info(f"Right side (score > 0): {corr_right:.4f}")
    analysis_logger.info(f"Left side (score <= 0): {corr_left:.4f}")
    analysis_logger.info(f"Total: {corr_total:.4f}")
    analysis_logger.info("-" * 50)
    
    # 绘图
    plt.figure(figsize=(14, 8))
    plt.bar(bin_stats['bin_left'], bin_stats['metric'], width=bin_width, 
            alpha=0.7, color=color, edgecolor='black')
    plt.xlabel(f'{title_prefix} Score')
    plt.ylabel(metric_label)
    plt.title(f'{title_prefix} Score vs {metric_label} - Bin Width: {bin_width}')
    plt.grid(True, alpha=0.3, axis='y')
    
    # 对于收益图表，添加零线
    if metric_type == 'expected_return':
        plt.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/{figure_name}')
    plt.close()
    
    analysis_logger.info(f"已生成图表: {figure_name}")


def plot_score_vs_up_probability(df, forward_days=None):
    """绘制标准分与上涨概率"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'standard_score', 'up_probability',
        forward_days, bin_width=CONFIG['BIN_WIDTH_PROBABILITY'],
        title_prefix='RSRS Standard',
        figure_name='figure16_score_vs_up_probability.png',
        color='blue'
    )


def plot_score_vs_expected_return(df, forward_days=None):
    """绘制标准分与预期收益"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'standard_score', 'expected_return',
        forward_days, bin_width=CONFIG['BIN_WIDTH_RETURN'],
        title_prefix='RSRS Standard',
        figure_name='figure17_score_vs_expected_return.png',
        color='green'
    )


def plot_modified_score_vs_up_probability(df, forward_days=None):
    """绘制修正标准分与上涨概率"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'modified_standard_score', 'up_probability',
        forward_days, bin_width=CONFIG['BIN_WIDTH_PROBABILITY'],
        title_prefix='Modified RSRS Standard',
        figure_name='figure18_modified_score_vs_up_probability.png',
        color='purple'
    )


def plot_modified_score_vs_expected_return(df, forward_days=None):
    """绘制修正标准分与预期收益"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'modified_standard_score', 'expected_return',
        forward_days, bin_width=CONFIG['BIN_WIDTH_RETURN'],
        title_prefix='Modified RSRS Standard',
        figure_name='figure19_modified_score_vs_expected_return.png',
        color='orange'
    )


def plot_right_skewed_score_vs_up_probability(df, forward_days=None):
    """绘制右偏标准分与上涨概率"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'right_skewed_standard_score', 'up_probability',
        forward_days, bin_width=CONFIG['BIN_WIDTH_PROBABILITY'],
        title_prefix='Right Skewed RSRS Standard',
        figure_name='figure21_right_skewed_score_vs_up_probability.png',
        color='brown'
    )


def plot_right_skewed_score_vs_expected_return(df, forward_days=None):
    """绘制右偏标准分与预期收益"""
    forward_days = forward_days or CONFIG['FORWARD_DAYS']
    _plot_score_analysis(
        df, 'right_skewed_standard_score', 'expected_return',
        forward_days, bin_width=CONFIG['BIN_WIDTH_RETURN'],
        title_prefix='Right Skewed RSRS Standard',
        figure_name='figure22_right_skewed_score_vs_expected_return.png',
        color='darkred'
    )