import matplotlib.pyplot as plt
import pandas as pd
from config import CONFIG
from logger_config import analysis_logger


def _calculate_distribution_statistics(data, label):
    """
    计算分布统计信息并记录到日志
    
    参数:
        data: 数据序列
        label: 标签名称
    
    返回:
        统计字典
    """
    stats = {
        'Mean': data.mean(),
        'Std': data.std(),
        'Skewness': data.skew(),
        'Kurtosis': data.kurtosis(),
        'Data points': len(data)
    }
    
    analysis_logger.info(f"\n{label} Statistics ({CONFIG['STATISTICS_START_DATE']} and after):")
    for key, value in stats.items():
        analysis_logger.info(f"{key}: {value:.6f}")
    analysis_logger.info("-" * 50)
    
    return stats


def _plot_distribution_histogram(data, xlabel, title, filename, color):
    """
    绘制分布直方图
    
    参数:
        data: 数据序列
        xlabel: x轴标签
        title: 图表标题
        filename: 保存文件名
        color: 柱子颜色
    """
    plt.figure(figsize=(10, 6))
    plt.hist(data, bins=50, alpha=0.7, color=color, edgecolor='black')
    plt.xlabel(xlabel)
    plt.ylabel('Frequency')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/{filename}')
    plt.close()


def _extract_and_plot_score_distribution(df, score_column, label, xlabel, 
                                         title, filename, color):
    """
    通用的分数分布提取和绘图函数
    
    参数:
        df: 数据框
        score_column: 分数列名
        label: 统计标签名
        xlabel: x轴标签
        title: 图表标题
        filename: 保存文件名
        color: 柱子颜色
    """
    if score_column not in df.columns:
        analysis_logger.warning(f"列 '{score_column}' 不存在于数据框中")
        return
    
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    mask = df_copy['date'] >= CONFIG['STATISTICS_START_DATE']
    score_data = df_copy.loc[mask, score_column].dropna()
    
    if score_data.empty:
        analysis_logger.warning(f"没有有效的 {score_column} 数据")
        return
    
    # 计算并记录统计信息
    _calculate_distribution_statistics(score_data, label)
    
    # 绘制直方图
    _plot_distribution_histogram(score_data, xlabel, title, filename, color)
    
    analysis_logger.info(f"已生成图表: {filename}")


def plot_slope_histogram(df):
    """绘制RSRS斜率分布直方图"""
    _extract_and_plot_score_distribution(
        df, 'rsrs_slope',
        label='RSRS Slope',
        xlabel='RSRS Slope',
        title='RSRS Slope Distribution (2005-03-01 to 2017-03-31)',
        filename='figure7_rsrs_slope_histogram.png',
        color='blue'
    )


def plot_slope_mean(df, window=250):
    """绘制RSRS斜率的滚动均值"""
    df_copy = df.copy()
    df_copy['date'] = pd.to_datetime(df_copy['date'])
    df_copy = df_copy.set_index('date')
    rolling_mean = df_copy['rsrs_slope'].rolling(window=window).mean()
    
    plt.figure(figsize=(12, 6))
    plt.plot(rolling_mean.index, rolling_mean.values, linewidth=1.5, color='blue')
    plt.title(f'RSRS Slope Rolling Mean (Window = {window} Days)')
    plt.ylabel('RSRS Slope Rolling Mean')
    plt.xlabel('date')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(f'{CONFIG["PICTURE_DIR"]}/figure8_rsrs_slope_rolling_mean.png')
    plt.close()
    
    analysis_logger.info(f"已生成图表: figure8_rsrs_slope_rolling_mean.png")


def plot_standard_score_distribution(df):
    """绘制标准分分布"""
    _extract_and_plot_score_distribution(
        df, 'standard_score',
        label='RSRS Standard Score',
        xlabel='RSRS Standard Score',
        title='RSRS Standard Score Distribution (2005-03-01 to 2017-03-31)',
        filename='figure14_rsrs_standard_score_distribution.png',
        color='green'
    )


def plot_modified_standard_score_distribution(df):
    """绘制修正标准分分布"""
    _extract_and_plot_score_distribution(
        df, 'modified_standard_score',
        label='Modified RSRS Standard Score',
        xlabel='Modified RSRS Standard Score',
        title='Modified RSRS Standard Score Distribution (2005-03-01 to 2017-03-31)',
        filename='figure15_rsrs_modified_standard_score_distribution.png',
        color='orange'
    )


def plot_right_skewed_score_distribution(df):
    """绘制右偏标准分分布"""
    _extract_and_plot_score_distribution(
        df, 'right_skewed_standard_score',
        label='Right Skewed RSRS Standard Score',
        xlabel='Right Skewed RSRS Standard Score',
        title='Right Skewed RSRS Standard Score Distribution (2005-03-01 to 2017-03-31)',
        filename='figure20_rsrs_right_skewed_score_distribution.png',
        color='red'
    )