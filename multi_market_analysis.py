import matplotlib.pyplot as plt
import pandas as pd
import os
from config import CONFIG
from logger_config import analysis_logger
from utils import calculate_portfolio_value, buy_hold_strategy
from strategy import backtest_price_optimized_right_skewed_strategy
from backtest import calculate_strategy_statistics, log_strategy_statistics

def plot_strategy_on_market(market_key, market_config):
    """Run price optimized right skewed strategy on specified market"""
    
    data_file = market_config['data_file']
    market_name = market_config['name']
    benchmark_name = market_config['benchmark_name']
    
    analysis_logger.info(f"\n=== Running strategy on {market_name} ===")
    
    try:
        # Load market data
        if not os.path.exists(data_file):
            analysis_logger.warning(f"Data file not found: {data_file}")
            return None
            
        df = pd.read_csv(data_file)
        analysis_logger.info(f"Successfully loaded {market_name} data: {len(df)} rows")
        
        # Check required columns
        required_columns = ['date', 'close', 'high', 'low']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            analysis_logger.error(f"Missing required columns in {data_file}: {missing_columns}")
            return None
        
        # Calculate all standard scores (using unified parameters n=18, m=600)
        from data_processing import (
            calculate_rsrs_slope, calculate_standard_score, 
            calculate_modified_standard_score, calculate_right_skewed_standard_score
        )
        
        df = calculate_rsrs_slope(df, n=18)
        df = calculate_standard_score(df, m=600)
        df = calculate_modified_standard_score(df)
        df = calculate_right_skewed_standard_score(df)
        
        # Calculate strategy signals
        signals, _ = backtest_price_optimized_right_skewed_strategy(df)
        
        # Calculate net values
        values = calculate_portfolio_value(df, signals)
        bh_signals = buy_hold_strategy(df)
        bh_values = calculate_portfolio_value(df, bh_signals)
        
        # Plot
        plt.figure(figsize=(12, 8))
        dates = pd.to_datetime(df['date'])
        
        plt.plot(dates, bh_values, label=f'{benchmark_name} Buy & Hold', color='black', linewidth=2)
        plt.plot(dates, values, label='Price Optimized Right Skewed Score Strategy', color='red', linewidth=1.5)
        
        plt.title(f'Price Optimized Right Skewed Standard Score Strategy \non {market_name} Index', fontsize=14)
        plt.ylabel('Net Value', fontsize=12)
        plt.xlabel('Date', fontsize=12)
        plt.legend(fontsize=10)
        plt.grid(True, alpha=0.3)
        
        # Save chart
        if market_key == 'sh50':
            figure_name = 'figure30_sh50_strategy.png'
        elif market_key == 'zz500':
            figure_name = 'figure31_zz500_strategy.png'
        else:
            figure_name = f'strategy_{market_key}.png'
            
        plt.tight_layout()
        plt.savefig(f'{CONFIG["PICTURE_DIR"]}/{figure_name}')
        plt.close()
        
        # Calculate statistics
        stats = calculate_strategy_statistics(df, signals, f'Price Optimized Right Skewed on {market_name}')
        log_strategy_statistics(stats)
        
        analysis_logger.info(f"Generated chart: {figure_name}")
        
        return {
            'market': market_name,
            'strategy_final_value': values[-1],
            'benchmark_final_value': bh_values[-1],
            'stats': stats
        }
        
    except Exception as e:
        analysis_logger.error(f"Failed to run strategy on {market_name}: {e}")
        return None

def plot_multi_market_strategies():
    """Plot price optimized right skewed strategy performance on different markets (Figure 30, 31)"""
    
    analysis_logger.info("\n=== Multi-Market Strategy Analysis ===")
    
    results = {}
    
    # Run strategy on SSE 50 (Figure 30)
    if 'sh50' in CONFIG['MARKETS']:
        sh50_config = CONFIG['MARKETS']['sh50']
        results['sh50'] = plot_strategy_on_market('sh50', sh50_config)
    else:
        analysis_logger.warning("SSE 50 configuration not found in MARKETS")
    
    # Run strategy on CSI 500 (Figure 31)  
    if 'zz500' in CONFIG['MARKETS']:
        zz500_config = CONFIG['MARKETS']['zz500']
        results['zz500'] = plot_strategy_on_market('zz500', zz500_config)
    else:
        analysis_logger.warning("CSI 500 configuration not found in MARKETS")
    
    # Summary comparison
    analysis_logger.info("\n" + "="*60)
    analysis_logger.info("Multi-Market Strategy Performance Summary")
    analysis_logger.info("="*60)
    
    for market_key, result in results.items():
        if result:
            market_name = result['market']
            strategy_value = result['strategy_final_value']
            benchmark_value = result['benchmark_final_value']
            outperformance = (strategy_value - benchmark_value) / benchmark_value * 100
            
            analysis_logger.info(f"{market_name}:")
            analysis_logger.info(f"  Strategy Final Value: {strategy_value:.2f}")
            analysis_logger.info(f"  Benchmark Final Value: {benchmark_value:.2f}")
            analysis_logger.info(f"  Outperformance: {outperformance:+.1f}%")
            analysis_logger.info("-" * 40)
    
    return results