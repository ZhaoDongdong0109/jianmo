"""生成多套方案对比图"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np

font_path = '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
fm.fontManager.addfont(font_path)
prop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = [prop.get_name(), 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 数据
plans = ['A-满意度优先', 'B-均衡稳健', 'C-轻松休闲', 'D-深度体验']
short = ['方案A\n满意度优先', '方案B\n均衡稳健', '方案C\n轻松休闲', '方案D\n深度体验']
n_spots = [8, 8, 7, 6]
pref = [63.4, 63.2, 53.0, 49.2]
r_light = [0.0, 40.5, 59.3, 62.6]
r_mod   = [0.0, 23.5, 44.4, 46.5]
r_heavy = [0.0, 9.6, 25.5, 26.8]
min_slack = [0.7, 2.5, 2.5, 3.0]
colors = ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12']

fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 图1: 满意度 vs 可靠度 (中度扰动)
ax = axes[0]
for i in range(4):
    ax.scatter(pref[i], r_mod[i], s=n_spots[i]*100, color=colors[i], 
               edgecolors='black', linewidth=2, zorder=5, alpha=0.85)
    ax.annotate(short[i], (pref[i], r_mod[i]), 
                textcoords="offset points", xytext=(12, 8),
                fontsize=9, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor=colors[i], alpha=0.15))
ax.axhline(y=90, color='red', linestyle='--', linewidth=2, alpha=0.6, label='90%目标')
ax.set_xlabel('总满意度', fontsize=12)
ax.set_ylabel('中度扰动可靠度 (%)', fontsize=12)
ax.set_title('满意度 vs 可靠度', fontsize=13, fontweight='bold')
ax.set_ylim(-5, 100)
ax.grid(alpha=0.3)
ax.legend(fontsize=10)

# 图2: 三情景可靠度对比
ax = axes[1]
x = np.arange(4)
w = 0.25
bars1 = ax.bar(x-w, r_light, w, label='轻度扰动', color='#2ECC71', edgecolor='white')
bars2 = ax.bar(x, r_mod, w, label='中度扰动', color='#F39C12', edgecolor='white')
bars3 = ax.bar(x+w, r_heavy, w, label='强扰动', color='#E74C3C', edgecolor='white')
ax.axhline(y=90, color='red', linestyle='--', linewidth=2, alpha=0.6)
ax.set_xticks(x)
ax.set_xticklabels(short, fontsize=9)
ax.set_ylabel('可靠度 (%)', fontsize=12)
ax.set_title('三情景可靠度对比', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0, 100)
ax.grid(axis='y', alpha=0.3)
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        h = bar.get_height()
        if h > 2:
            ax.text(bar.get_x()+bar.get_width()/2, h+1, f'{h:.0f}%', 
                    ha='center', va='bottom', fontsize=8)

# 图3: 最小缓冲时间
ax = axes[2]
bars = ax.bar(range(4), min_slack, color=colors, edgecolor='white', linewidth=1.5)
ax.axhline(y=1.0, color='red', linestyle='--', linewidth=2, alpha=0.6, label='1h安全线')
ax.set_xticks(range(4))
ax.set_xticklabels(short, fontsize=9)
ax.set_ylabel('最小缓冲时间 (h)', fontsize=12)
ax.set_title('每日最小时间缓冲', fontsize=13, fontweight='bold')
ax.legend(fontsize=10)
ax.set_ylim(0, 4)
ax.grid(axis='y', alpha=0.3)
for bar, val in zip(bars, min_slack):
    ax.text(bar.get_x()+bar.get_width()/2, val+0.05, f'{val:.1f}h', 
            ha='center', va='bottom', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('fig_multi_plans.png', dpi=200, bbox_inches='tight')
plt.close()
print("已生成: fig_multi_plans.png")

# 额外: 每套方案的每日结束时间对比
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
plan_days = {
    'A-满意度优先': [13.70, 18.20, 20.20, 20.30, 12.10],
    'B-均衡稳健':   [18.00, 18.50, 16.10, 17.00, 15.90],
    'C-轻松休闲':   [13.50, 18.50, 13.10, 14.00, 16.70],
    'D-深度体验':   [14.00, 16.10, 17.00, 18.00, 12.10],
}
plan_labels = {
    'A-满意度优先': ['A5', 'A1+A10', 'A2+A8', 'A4+A9', 'A3'],
    'B-均衡稳健':   ['A5+A10', 'A1+A8', 'A2', 'A4', 'A3+A7'],
    'C-轻松休闲':   ['A10', 'A1+A8', 'A3', 'A9', 'A5+A7'],
    'D-深度体验':   ['A1', 'A2', 'A4', 'A8+A10', 'A3'],
}

for idx, (name, times) in enumerate(plan_days.items()):
    ax = axes[idx//2][idx%2]
    days = ['第1天', '第2天', '第3天', '第4天', '第5天']
    bars = ax.bar(range(5), times, color=colors[idx], edgecolor='white', alpha=0.85)
    ax.axhline(y=21, color='red', linestyle='--', linewidth=2, alpha=0.7)
    ax.set_xticks(range(5))
    ax.set_xticklabels([f'{d}\n{s}' for d, s in zip(days, plan_labels[name])], fontsize=9)
    ax.set_ylabel('结束时间', fontsize=10)
    ax.set_title(f'{name}', fontsize=12, fontweight='bold')
    ax.set_ylim(10, 22)
    ax.set_yticks([12, 14, 16, 18, 20, 21])
    ax.set_yticklabels(['12:00','14:00','16:00','18:00','20:00','21:00'])
    ax.grid(axis='y', alpha=0.3)
    for bar, val in zip(bars, times):
        ax.text(bar.get_x()+bar.get_width()/2, val+0.1, f'{val:.1f}', 
                ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('fig_multi_plans_schedule.png', dpi=200, bbox_inches='tight')
plt.close()
print("已生成: fig_multi_plans_schedule.png")
