# "五一"五日自驾景点优选与行程规划

2025年五一数学建模竞赛论文及代码

## 项目简介

针对"五一"假期五日自驾游的景点选择与行程规划问题，建立系统化的数学模型，在满足时间窗口约束的前提下，科学选择景点并合理安排行程。

## 方法概述

### 问题一：景点综合评价（AHP-TOPSIS法）

- 采用**层次分析法（AHP）**构建不同偏好下的判断矩阵，确定指标权重
- 通过**TOPSIS法**计算各景点与理想解的相对贴近度，得到优先级排序
- 针对四种偏好（人文型、自然型、亲子型、均衡型）分别给出不同排序结果

### 问题二：多目标优化行程规划

- 建立以**满意度最大化、行车时间最小化、缓冲最大化**为目标的优化模型
- 考虑每日时间窗口、景点数量、联动组合等约束
- 针对四种偏好设计四套不同的行程方案，含详细日程时序表

### 问题三：随机扰动下的可靠度分析

- 建立**堵车概率模型**：$p(d) = \min(\alpha \cdot d, 1.0)$
- 建立**入园排队时间模型**：按时段服从不同均匀分布
- 采用**蒙特卡洛模拟**（20000次）计算各方案可靠度
- 分析薄弱环节与扰动贡献度

## 文件结构

```
.
├── README.md                          # 项目说明
├── problem.pdf                        # 原始题目
├── paper.tex                          # 论文初稿
├── paper_improve/
│   ├── paper_final.tex                # ✅ 最终论文（LaTeX源文件）
│   ├── fig_*.png                      # 论文配图
│   ├── analysis.py / analysis_v2.py   # 数据分析脚本
│   ├── final_v2.py / final_v3.py      # 方案优化脚本
│   ├── multi_plans.py                 # 多方案生成
│   ├── multi_plans_mc.py              # 蒙特卡洛模拟
│   ├── problem3_final.py              # 问题三求解
│   ├── gen_figures.py / gen_multi_figs.py  # 图表生成
│   ├── results.json / results_final.json   # 计算结果
│   └── multi_plans.json / multi_plans_mc.json  # 方案数据
└── paper_figs/
    ├── fig2.png ~ fig13.png           # 分析图表
```

## 核心结果

| 偏好类型 | TOP3景点 | 选景点数 | 总满意度 |
|---------|---------|---------|---------|
| 人文偏好 | 文创小镇、古城老街、民俗古村 | 7 | 3.71 |
| 自然偏好 | 滨海浴场、环湖湿地、山野溪谷 | 7 | 4.09 |
| 亲子偏好 | 亲子农庄、海洋乐园、文创小镇 | 7 | 4.00 |
| 均衡偏好 | 文创小镇、古城老街、滨海浴场 | 7 | 3.87 |

## 技术栈

- **建模**：Python (NumPy, Pandas, Matplotlib)
- **论文**：LaTeX (ctexart, pgfplots, booktabs)
- **方法**：AHP、TOPSIS、多目标优化、蒙特卡洛模拟

## 编译论文

```bash
cd paper_improve
xelatex paper_final.tex
xelatex paper_final.tex  # 两次编译生成目录
```
