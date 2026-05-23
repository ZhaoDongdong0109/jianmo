import numpy as np

combos = {
    (1,10): 0.2, (2,8): 0.2, (3,7): 0.2, (1,8): 0.3,
    (8,10): 0.3, (4,9): 0.3, (5,10): 0.4
}

visit_time = {1:3.5, 2:4, 3:5, 4:3, 5:3, 6:3, 7:3, 8:3, 9:3, 10:4}
hotel_drive = {1:0.13, 2:0.5, 3:0.5, 4:0.5, 5:0.5, 6:0.5, 7:0.5, 8:0.5, 9:0.5, 10:0.17}
windows = [8.0, 12.5, 12.5, 12.5, 8.0]
dinner = 1.0

satisfaction = {
    "humanity": {10:0.84, 1:0.83, 5:0.69, 3:0.42, 2:0.42, 8:0.40, 7:0.38, 4:0.15, 9:0.14, 6:0.06},
    "nature":   {3:0.88, 7:0.80, 6:0.59, 4:0.57, 9:0.57, 2:0.47, 8:0.42, 5:0.38, 10:0.36, 1:0.32},
    "family":   {8:0.84, 2:0.80, 10:0.62, 3:0.61, 7:0.47, 1:0.40, 4:0.27, 5:0.26, 9:0.16, 6:0.06},
    "balanced": {10:0.75, 1:0.68, 3:0.58, 5:0.58, 8:0.55, 2:0.53, 7:0.51, 4:0.22, 9:0.20, 6:0.15},
}

rankings = {
    "humanity": [10, 1, 5, 3, 2, 8, 7, 4, 9, 6],
    "nature":   [3, 7, 6, 4, 9, 2, 8, 5, 10, 1],
    "family":   [8, 2, 10, 3, 7, 1, 4, 5, 9, 6],
    "balanced": [10, 1, 3, 5, 8, 2, 7, 4, 9, 6],
}

names_cn = {"humanity":"人文偏好", "nature":"自然偏好", "family":"亲子偏好", "balanced":"均衡偏好"}
a_names = {1:"古城老街",2:"海洋乐园",3:"滨海浴场",4:"森林公园",5:"民俗古村",6:"山野溪谷",7:"环湖湿地",8:"亲子农庄",9:"山地观景台",10:"文创小镇"}

def day_cost(day_list):
    """计算一天的总耗时"""
    if len(day_list) == 1:
        a = day_list[0]
        return visit_time[a] + hotel_drive[a] * 2 + dinner
    elif len(day_list) == 2:
        a, b = day_list
        key = (min(a,b), max(a,b))
        transfer = combos.get(key, 0.5)
        return visit_time[a] + visit_time[b] + hotel_drive[a] + hotel_drive[b] + transfer + dinner
    return 999

def find_best_pair(candidates, pref, window):
    """在候选中找满足时间约束的最佳联动组合"""
    best = None
    best_score = -1
    for i, a in enumerate(candidates):
        for b in candidates[i+1:]:
            key = (min(a,b), max(a,b))
            if key in combos:
                cost = day_cost([a, b])
                if cost <= window:
                    score = satisfaction[pref][a] + satisfaction[pref][b]
                    if score > best_score:
                        best_score = score
                        best = [a, b]
    return best

def generate_plan_v2(pref):
    """改进的方案生成"""
    ranking = rankings[pref]
    selected = set(ranking[:8])
    plan = [None] * 5
    used = set()
    
    # Day1 (8h): 单景点, 选近的高分景点
    day1_candidates = [a for a in ranking if a in selected and a not in used]
    for a in day1_candidates:
        if day_cost([a]) <= windows[0]:
            plan[0] = [a]
            used.add(a)
            break
    
    # Day5 (8h): 先预留, 选单景点
    # 找一个适合最后一天的单景点(低分的)
    day5_candidates = [a for a in reversed(ranking) if a in selected and a not in used and day_cost([a]) <= windows[4]]
    if day5_candidates:
        plan[4] = [day5_candidates[0]]
        used.add(day5_candidates[0])
    
    # Day2-4 (12.5h): 尽量联动组合
    for d in [1, 2, 3]:
        remaining = [a for a in ranking if a in selected and a not in used]
        if len(remaining) >= 2:
            pair = find_best_pair(remaining, pref, windows[d])
            if pair:
                plan[d] = pair
                used.update(pair)
            elif remaining:
                a = remaining[0]
                if day_cost([a]) <= windows[d]:
                    plan[d] = [a]
                    used.add(a)
        elif remaining:
            a = remaining[0]
            if day_cost([a]) <= windows[d]:
                plan[d] = [a]
                used.add(a)
    
    # 如果Day5没安排, 从剩余中选
    if plan[4] is None:
        remaining = [a for a in ranking if a in selected and a not in used]
        if remaining:
            plan[4] = [remaining[0]]
            used.add(remaining[0])
    
    # 检查所有天是否可行
    for d in range(5):
        if plan[d] is None:
            plan[d] = []
        cost = day_cost(plan[d]) if plan[d] else 0
        if cost > windows[d]:
            # 拆分: 保留第一个景点
            if len(plan[d]) > 1:
                plan[d] = [plan[d][0]]
    
    return plan

print("=" * 80)
print("四种偏好下的行程方案 (修正版)")
print("=" * 80)

for pref in ["humanity", "nature", "family", "balanced"]:
    plan = generate_plan_v2(pref)
    
    total_sat = sum(satisfaction[pref][a] for day in plan for a in day)
    n_attr = sum(len(day) for day in plan)
    
    print(f"\n{'='*60}")
    print(f"方案 - {names_cn[pref]} ({n_attr}个景点, 总满意度={total_sat:.2f})")
    print(f"{'='*60}")
    
    for d, day in enumerate(plan):
        if not day:
            print(f"  D{d+1}: 自由活动")
            continue
        day_names = " → ".join([f"A{a} {a_names[a]}" for a in day])
        cost = day_cost(day)
        visit = sum(visit_time[a] for a in day)
        if len(day) == 2:
            a, b = day
            drive = hotel_drive[a] + hotel_drive[b] + combos.get((min(a,b),max(a,b)), 0.5)
        else:
            drive = hotel_drive[day[0]] * 2
        buf = windows[d] - cost
        print(f"  D{d+1}: {day_names}")
        print(f"       游览{visit:.1f}h + 行车{drive:.1f}h + 晚餐1h = {cost:.1f}h (缓冲{buf:.1f}h)")

