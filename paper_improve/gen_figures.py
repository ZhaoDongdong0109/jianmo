"""
生成论文改进版所需图表
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import json
import os

# 设置中文字体
import matplotlib.font_manager as fm
font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = [prop.get_name(), 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 配色方案
COLORS = {
    'primary': '#2E86AB',
    'secondary': '#A23B72', 
    'accent': '#F18F01',
    'success': '#2ECC71',
    'danger': '#E74C3C',
    'warning': '#F39C12',
    'light': '#ECF0F1',
    'dark': '#2C3E50',
}

PLAN_COLORS = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6']
PLAN_NAMES = ['原始方案', '改进方案v1 (A2单独+A8/A9联动)', '改进方案v2 (A4单独)', '稳健方案 (最大化可靠度)', '极简方案 (5景点)']
PLAN_SHORT = ['原始方案', '改进v1', '改进v2', '稳健方案', '极简方案']

# 加载结果
with open('results.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ============================================================
# 图1: 景点综合优先级排序 (改进版)
# ============================================================
def fig_priority_ranking():
    spots_ordered = ['A1','A8','A3','A10','A7','A5','A2','A9','A6','A4']
    names = ['古城老街','亲子农庄','滨海浴场','文创小镇','环湖湿地',
             '民俗古村','海洋乐园','山地观景台','山野溪谷','森林公园']
    scores = [0.7488, 0.6576, 0.6422, 0.6363, 0.5720, 
              0.5047, 0.5008, 0.4718, 0.3082, 0.2757]
    levels = ['高','高','高','高','中','中','中','中','低','低']
    level_colors = {'高': '#2ECC71', '中': '#F39C12', '低': '#E74C3C'}
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(spots_ordered)), scores, 
                   color=[level_colors[l] for l in levels],
                   edgecolor='white', linewidth=0.5, height=0.7)
    
    ax.set_yticks(range(len(spots_ordered)))
    ax.set_yticklabels([f'{s} {n}' for s, n in zip(spots_ordered, names)], fontsize=11)
    ax.set_xlabel('综合优先指数 S', fontsize=12)
    ax.set_title('景点综合优先级排序（熵权法 + TOPSIS）', fontsize=14, fontweight='bold')
    ax.invert_yaxis()
    ax.set_xlim(0, 0.85)
    
    # 添加数值标签
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(score + 0.01, i, f'{score:.4f}', va='center', fontsize=10)
    
    # 添加优先级区域标注
    ax.axhline(y=3.5, color='gray', linestyle='--', alpha=0.5)
    ax.axhline(y=7.5, color='gray', linestyle='--', alpha=0.5)
    ax.text(0.82, 1.5, '高优先级', fontsize=10, color='#2ECC71', fontweight='bold', ha='center')
    ax.text(0.82, 5.5, '中优先级', fontsize=10, color='#F39C12', fontweight='bold', ha='center')
    ax.text(0.82, 8.5, '低优先级', fontsize=10, color='#E74C3C', fontweight='bold', ha='center')
    
    plt.tight_layout()
    plt.savefig('fig_new_priority.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_priority.png")


# ============================================================
# 图2: 多方案可靠度对比
# ============================================================
def fig_reliability_comparison():
    scenarios = ['轻度', '中度', '强扰动']
    x = np.arange(len(scenarios))
    width = 0.15
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    scenario_keys = ['轻度', '中度', '强扰动']
    for i, plan_name in enumerate(PLAN_NAMES):
        reliabilities = []
        for s_key in scenario_keys:
            r = data['plans'][plan_name][s_key]['reliability'] * 100
            reliabilities.append(r)
        bars = ax.bar(x + i*width, reliabilities, width, 
                      label=PLAN_SHORT[i], color=PLAN_COLORS[i],
                      edgecolor='white', linewidth=0.5)
        # 数值标签
        for bar, val in zip(bars, reliabilities):
            if val > 2:
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                       f'{val:.1f}%', ha='center', va='bottom', fontsize=8)
    
    ax.axhline(y=90, color='red', linestyle='--', linewidth=2, alpha=0.7, label='90%目标线')
    ax.set_xlabel('扰动情景', fontsize=12)
    ax.set_ylabel('整体可靠度 (%)', fontsize=12)
    ax.set_title('不同扰动情景下各方案整体可靠度对比', fontsize=14, fontweight='bold')
    ax.set_xticks(x + width*2)
    ax.set_xticklabels(scenarios, fontsize=11)
    ax.legend(loc='upper right', fontsize=9)
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fig_new_reliability.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_reliability.png")


# ============================================================
# 图3: 每日失败概率分解 (改进方案v2 vs 原始方案)
# ============================================================
def fig_daily_failure():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    for idx, (plan_name, title) in enumerate([
        ('原始方案', '原始方案（中度扰动）'),
        ('改进方案v2 (A4单独)', '改进方案v2（中度扰动）')
    ]):
        ax = axes[idx]
        res = data['plans'][plan_name]['中度']
        days = ['第1天', '第2天', '第3天', '第4天', '第5天']
        daily_fails = [f*100 for f in res['daily_fails']]
        
        spots_info = {
            '原始方案': ['A5', 'A1→A10', 'A2→A8', 'A4→A9', 'A3'],
            '改进方案v2 (A4单独)': ['A10', 'A1→A8', 'A2', 'A4', 'A3→A7'],
        }
        
        bars = ax.bar(range(5), daily_fails, color=[COLORS['danger'] if f>30 else COLORS['warning'] if f>10 else COLORS['success'] for f in daily_fails],
                      edgecolor='white', linewidth=0.5)
        
        ax.set_xticks(range(5))
        ax.set_xticklabels([f'{d}\n{s}' for d, s in zip(days, spots_info[plan_name])], fontsize=10)
        ax.set_ylabel('失败概率 (%)', fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold')
        ax.set_ylim(0, 105)
        ax.grid(axis='y', alpha=0.3)
        
        for bar, val in zip(bars, daily_fails):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                   f'{val:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('fig_new_daily_fail.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_daily_fail.png")


# ============================================================
# 图4: 灵敏度分析
# ============================================================
def fig_sensitivity():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    p1_vals = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    
    for i, plan_name in enumerate(['原始方案', '稳健方案']):
        sens = data['sensitivity'][plan_name]
        p_vals = [s[0] for s in sens]
        r_vals = [s[1]*100 for s in sens]
        ax.plot(p_vals, r_vals, 'o-', color=PLAN_COLORS[i], linewidth=2.5, 
                markersize=8, label=PLAN_SHORT[i])
    
    ax.axhline(y=90, color='red', linestyle='--', linewidth=2, alpha=0.7, label='90%目标')
    ax.fill_between(p1_vals, 0, 90, alpha=0.05, color='red')
    
    ax.set_xlabel('高峰拥堵概率 $p_1$', fontsize=12)
    ax.set_ylabel('整体可靠度 (%)', fontsize=12)
    ax.set_title('堵车概率灵敏度分析', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fig_new_sensitivity.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_sensitivity.png")


# ============================================================
# 图5: Pareto前沿 (满意度 vs 可靠度)
# ============================================================
def fig_pareto():
    fig, ax = plt.subplots(figsize=(10, 6))
    
    for i, plan_name in enumerate(PLAN_NAMES):
        plan = data['plans'][plan_name]
        pref = plan['total_pref']
        n_spots = plan['n_spots']
        r_light = plan['轻度']['reliability'] * 100
        r_moderate = plan['中度']['reliability'] * 100
        
        ax.scatter(pref, r_moderate, s=n_spots*80, color=PLAN_COLORS[i], 
                   edgecolors='black', linewidth=1.5, zorder=5, alpha=0.8)
        ax.annotate(f'{plan_name}\n({n_spots}景点)', 
                    (pref, r_moderate), 
                    textcoords="offset points", xytext=(10, 5),
                    fontsize=9, fontweight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor=PLAN_COLORS[i], alpha=0.2))
    
    ax.axhline(y=90, color='red', linestyle='--', linewidth=2, alpha=0.7, label='90%目标')
    ax.set_xlabel('总满意度', fontsize=12)
    ax.set_ylabel('中度扰动可靠度 (%)', fontsize=12)
    ax.set_title('Pareto分析：满意度 vs 可靠度', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.set_ylim(0, 100)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fig_new_pareto.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_pareto.png")


# ============================================================
# 图6: 每日行车负荷与结束时间对比
# ============================================================
def fig_schedule_comparison():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    plans_drive = {
        '原始方案': [1.2, 1.2, 1.7, 2.8, 0.6],
        '改进方案v2': [1.0, 1.5, 1.6, 3.0, 0.9],
        '稳健方案': [1.5, 1.5, 1.6, 2.0, 0.9],
    }
    
    plans_endtime = {
        '原始方案': [13.70, 18.20, 20.20, 20.30, 12.10],
        '改进方案v2': [13.50, 18.50, 16.10, 17.00, 15.90],
        '稳健方案': [18.00, 18.50, 16.10, 14.00, 15.90],
    }
    
    days = ['第1天', '第2天', '第3天', '第4天', '第5天']
    x = np.arange(5)
    
    # 行车负荷
    ax = axes[0]
    for i, (name, drives) in enumerate(plans_drive.items()):
        ax.plot(x, drives, 'o-', color=[COLORS['danger'], COLORS['primary'], COLORS['success']][i],
                linewidth=2.5, markersize=8, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=11)
    ax.set_ylabel('行车时长 (h)', fontsize=12)
    ax.set_title('每日行车负荷对比', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(alpha=0.3)
    
    # 结束时间
    ax = axes[1]
    for i, (name, times) in enumerate(plans_endtime.items()):
        ax.plot(x, times, 'o-', color=[COLORS['danger'], COLORS['primary'], COLORS['success']][i],
                linewidth=2.5, markersize=8, label=name)
    ax.axhline(y=21, color='red', linestyle='--', linewidth=2, alpha=0.7, label='21:00边界')
    ax.set_xticks(x)
    ax.set_xticklabels(days, fontsize=11)
    ax.set_ylabel('理想结束时间 (h)', fontsize=12)
    ax.set_title('每日理想结束时间对比（含晚餐）', fontsize=13, fontweight='bold')
    ax.legend(fontsize=10)
    ax.set_ylim(10, 22)
    ax.set_yticks([12, 14, 16, 18, 20, 21])
    ax.set_yticklabels(['12:00', '14:00', '16:00', '18:00', '20:00', '21:00'])
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('fig_new_schedule.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_schedule.png")


# ============================================================
# 图7: 熵权法权重饼图
# ============================================================
def fig_weights():
    labels = ['喜好度', '耗时灵活性', '通勤便利性', '抗拥堵能力', '整体舒适度']
    weights = [0.2719, 0.1699, 0.1486, 0.1609, 0.2487]
    colors = ['#3498DB', '#2ECC71', '#F39C12', '#E74C3C', '#9B59B6']
    
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(weights, labels=labels, autopct='%1.1f%%',
                                       colors=colors, startangle=90,
                                       textprops={'fontsize': 12},
                                       pctdistance=0.75)
    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_fontweight('bold')
    
    ax.set_title('熵权法指标权重分布', fontsize=14, fontweight='bold', pad=20)
    plt.tight_layout()
    plt.savefig('fig_new_weights.png', dpi=200, bbox_inches='tight')
    plt.close()
    print("已生成: fig_new_weights.png")


if __name__ == '__main__':
    fig_priority_ranking()
    fig_reliability_comparison()
    fig_daily_failure()
    fig_sensitivity()
    fig_pareto()
    fig_schedule_comparison()
    fig_weights()
    print("\n所有图表生成完成!")
