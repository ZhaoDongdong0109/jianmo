import numpy as np
import json

# 联动组合 (车程h)
combos = {
    (1,10): 0.2, (2,8): 0.2, (3,7): 0.2, (1,8): 0.3,
    (8,10): 0.3, (4,9): 0.3, (5,10): 0.4
}

# 各景点游览时长 (h)
visit_time = {1:3.5, 2:4, 3:5, 4:3, 5:3, 6:3, 7:3, 8:3, 9:3, 10:4}

# 景点满意度 (TOPSIS S值) - 四种偏好
satisfaction = {
    "humanity": {1:0.83, 2:0.42, 3:0.42, 4:0.15, 5:0.69, 6:0.06, 7:0.38, 8:0.40, 9:0.14, 10:0.84},
    "nature":   {1:0.32, 2:0.47, 3:0.88, 4:0.57, 5:0.38, 6:0.59, 7:0.80, 8:0.42, 9:0.57, 10:0.36},
    "family":   {1:0.40, 2:0.80, 3:0.61, 4:0.27, 5:0.26, 6:0.06, 7:0.47, 8:0.84, 9:0.16, 10:0.62},
    "balanced": {1:0.68, 2:0.53, 3:0.58, 4:0.22, 5:0.58, 6:0.15, 7:0.51, 8:0.55, 9:0.20, 10:0.75},
}

# 酒店到各景点车程 (h)
hotel_drive = {1:0.13, 2:0.5, 3:0.5, 4:0.5, 5:0.5, 6:0.5, 7:0.5, 8:0.5, 9:0.5, 10:0.17}

# 时间窗口
# Day1: 13:00-21:00 (8h), Day2-4: 8:30-21:00 (12.5h), Day5: 8:30-16:30 (8h)
windows = [8.0, 12.5, 12.5, 12.5, 8.0]
dinner = 1.0  # 晚餐1h

def calc_day_time(singles, pair=None):
    """计算一天的时间安排"""
    total_drive = 0
    total_visit = 0
    for s in singles:
        total_drive += hotel_drive[s] * 2  # 往返
        total_visit += visit_time[s]
    if pair:
        a, b = pair
        total_drive = hotel_drive[a] + hotel_drive[b] + combos.get((min(a,b), max(a,b)), 0.5)
        total_visit = visit_time[a] + visit_time[b]
    return total_visit + total_drive + dinner

def generate_plan(pref_name, top_attractions):
    """为给定偏好生成行程方案"""
    # 选择景点: 尽量选7-8个高分景点
    selected = top_attractions[:8]
    
    # 贪心分配: 先把联动组合安排在同一天
    plan = [None] * 5  # 5天
    used = set()
    
    # Day1: 单景点 (时间短)
    day1_candidates = [a for a in selected if a not in used]
    if day1_candidates:
        best = max(day1_candidates, key=lambda x: satisfaction[pref_name][x])
        plan[0] = [best]
        used.add(best)
    
    # Day2-4: 尽量联动组合
    for d in [1, 2, 3]:
        remaining = [a for a in selected if a not in used]
        if len(remaining) >= 2:
            # 找最佳联动组合
            best_combo = None
            best_score = -1
            for i, a in enumerate(remaining):
                for b in remaining[i+1:]:
                    key = (min(a,b), max(a,b))
                    if key in combos:
                        score = satisfaction[pref_name][a] + satisfaction[pref_name][b]
                        if score > best_score:
                            best_score = score
                            best_combo = (a, b)
            if best_combo and calc_day_time([], best_combo) <= windows[d]:
                plan[d] = list(best_combo)
                used.update(best_combo)
            elif remaining:
                plan[d] = [remaining[0]]
                used.add(remaining[0])
        elif remaining:
            plan[d] = [remaining[0]]
            used.add(remaining[0])
    
    # Day5: 剩余
    remaining = [a for a in selected if a not in used]
    plan[4] = remaining if remaining else [selected[-1]]
    
    return plan

# 四种偏好的排序
rankings = {
    "humanity": [10, 1, 5, 3, 2, 8, 7, 4, 9, 6],
    "nature":   [3, 7, 6, 4, 9, 2, 8, 5, 10, 1],
    "family":   [8, 2, 10, 3, 7, 1, 4, 5, 9, 6],
    "balanced": [10, 1, 3, 5, 8, 2, 7, 4, 9, 6],
}

names_cn = {"humanity":"人文偏好", "nature":"自然偏好", "family":"亲子偏好", "balanced":"均衡偏好"}
a_names = {1:"古城老街",2:"海洋乐园",3:"滨海浴场",4:"森林公园",5:"民俗古村",6:"山野溪谷",7:"环湖湿地",8:"亲子农庄",9:"山地观景台",10:"文创小镇"}

print("=" * 70)
print("四种偏好下的行程方案")
print("=" * 70)

all_plans = {}
for pref, ranking in rankings.items():
    plan = generate_plan(pref, ranking)
    all_plans[pref] = plan
    
    total_sat = sum(satisfaction[pref][a] for day in plan for a in day)
    total_drive = sum(hotel_drive[a] for day in plan for a in day) + sum(
        combos.get((min(day[0],day[1]), max(day[0],day[1])), 0) 
        for day in plan if len(day) == 2
    )
    n_attractions = sum(len(day) for day in plan)
    
    print(f"\n{'='*50}")
    print(f"方案 - {names_cn[pref]} (选{n_attractions}个景点, 满意度{total_sat:.1f})")
    print(f"{'='*50}")
    for d, day in enumerate(plan):
        day_names = " → ".join([f"A{a} {a_names[a]}" for a in day])
        drive = sum(hotel_drive[a] for a in day)
        if len(day) == 2:
            key = (min(day[0],day[1]), max(day[0],day[1]))
            drive += combos.get(key, 0.5)
        else:
            drive += hotel_drive[day[0]]
        visit = sum(visit_time[a] for a in day)
        buf = windows[d] - visit - drive - dinner
        print(f"  D{d+1}: {day_names}  (游览{visit:.1f}h+行车{drive:.1f}h+餐1h, 缓冲{buf:.1f}h)")

