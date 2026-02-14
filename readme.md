README - v1
目前完成了研报中第二部分的所有图表的复现绘制

代码结构


rsrs_analysis/
├── main.py                      # 主程序入口和分析流程
├── config.py                    # 配置参数
├── data_processing.py           # 斜率、标准分计算
├── strategy.py                  # 交易策略
├── backtest.py                  # 其他指标计算
├── utils.py                     # 净值计算等辅助函数
├── logger_config.py             # 日志配置
├── hs300_data.csv               # 沪深300历史数据
└── plot/                        # 可视化模块
    ├── indicators.py            # 指标分布图
    ├── score_analysis.py        # 标准分-收益相关性分析
    ├── strategy_performance.py  # 策略对比图表
    ├── cost_analysis.py         # 交易成本影响分析
    └── parameter_sensitivity.py # 参数变化图表
运行 main.py 即可得到全部结果，生成文件夹 log 存储日志和 picture 存储图片。

TODO：第三部分的复现：组合策略；数据迁移