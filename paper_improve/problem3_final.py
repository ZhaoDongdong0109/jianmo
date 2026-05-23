"""
问题三: 基于距离的拥堵概率模型 + 蒙特卡罗模拟
核心假设: 堵车概率与车程正相关
"""
import numpy as np
import json

# 完整距离矩阵
all_ids = ['H','A1','A2','A3','A4','A5','A6','A7','A8','A9','A10']
M = [
    [0.0, 0.5, 0.8, 0.3, 1.5, 0.6, 1.2, 0.4, 0.7, 1.0, 0.5],
    [0.5, 0.0, 0.4, 0.6, 1.2, 0.3, 1.0, 0.5, 0.3, 0.8, 0.2],
    [0.8, 0.4, 0.0, 0.5, 1.0, 0.6, 0.9, 0.7, 0.2, 0.6, 0.3],
    [0.3, 0.6, 0.5, 0.0, 1.3, 0.8, 1.4, 0.2, 0.6, 1.1, 0.5],
    [1.5, 1.2, 1.0, 1.3, 0.0, 1.0, 0.4, 1.4, 0.9, 0.3, 1.1],
    [0.6, 0.3, 0.6, 0.8, 1.0, 0.0, 0.8, 0.7, 0.5, 0.7, 0.4],
    [1.2, 1.0, 0.9, 1.4, 0.4, 0.8, 0.0, 1.3, 0.8, 0.5, 0.9],
    [0.4, 0.5, 0.7, 0.2, 1.4, 0.7, 1.3, 0.0, 0.6, 1.0, 0.4],
    [0.7, 0.3, 0.2, 0.6, 0.9, 0.5, 0.8, 0.6, 0.0, 0.5, 0.3],
    [1.0, 0.8, 0.6, 1.1, 0.3, 0.7, 0.5, 1.0, 0.5, 0.0, 0.7],
    [0.5, 0.2, 0.3, 0.5, 1.1, 0.4, 0.9, 0.4, 0.3, 0.7, 0.0],
]
DD = {}
for i,a in enumerate(all_ids):
    for j,b in enumerate(all_ids):
        DD[(a,b)] = M[i][j]

spots = {
    'A1':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.5, 'pref': 8.6},
    'A2':  {'open': 9.0,  'close': 18.0, 't_min': 3.0, 't_comf': 5.0, 'pref': 9.2},
    'A3':  {'open': 0.0,  'close': 24.0, 't_min': 1.0, 't_comf': 3.0, 'pref': 7.5},
    'A4':  {'open': 8.0,  'close': 17.0, 't_min': 3.5, 't_comf': 4.5, 'pref': 8.0},
    'A5':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.2},
    'A7':  {'open': 0.0,  'close': 24.0, 't_min': 1.5, 't_comf': 2.5, 'pref': 6.8},
    'A8':  {'open': 9.0,  'close': 18.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 8.3},
    'A9':  {'open': 8.0,  'close': 17.5, 't_min': 1.5, 't_comf': 2.5, 'pref': 7.0},
    'A10': {'open': 9.0,  'close': 20.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.6},
}

TM=1.5; TL=1.0; TD=1.0; TCI=0.5; HOME=4.0

def is_peak(t1, t2):
    for ps, pe in [(7,9),(11,13),(16,18)]:
        if t1 < pe and t2 > ps: return True
    return False

def congestion_prob(distance, alpha=0.3):
    """
    堵车概率与车程正相关
    p(d) = min(alpha * d, 1.0)
    alpha: 拥堵系数, 表示每小时车程对应的拥堵概率增量
    """
    return min(alpha * distance, 1.0)

def sim_day(day_spots, day_idx, rng, alpha=0.3):
    """
    模拟一天行程
    alpha: 拥堵系数 (p = alpha * distance)
    """
    # 通用耗时: 使用题目标准值 (固定, 不是随机变量)
    # "可在±20%范围内合理微调"是指设计时可选, 不是每次随机浮动
    morning = TM    # 固定 1.5h
    lunch = TL if len(day_spots)==2 else 0  # 固定 1.0h
    dinner = TD     # 固定 1.0h
    checkin = TCI   # 固定 0.5h
    
    if day_idx == 0:
        t = 7.0 + morning + HOME + checkin  # 入住有浮动
        hard_end = 21.0
    elif day_idx == 4:
        t = 7.0 + morning
        hard_end = 21.0 - TCI - HOME  # 退房用固定0.5h
    else:
        t = 7.0 + morning
        hard_end = 21.0
    
    # 第一个景点
    s1 = day_spots[0]; sp1 = spots[s1]
    d1 = DD['H', s1]
    p1 = congestion_prob(d1, alpha)
    rd1 = rng.uniform(1,4) if (is_peak(t, t+d1) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t, t+d1) and rng.random()<p1*0.5) else 0)
    t += d1 + rd1
    q1 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
    t += q1
    if t < sp1['open']: t = sp1['open']
    v1s = t; t += sp1['t_comf']; v1e = t
    v1ok = (v1e - v1s) >= sp1['t_min'] - 1e-6
    
    # 第二个景点
    v2ok = True; rd2 = 0; q2 = 0
    if len(day_spots) == 2:
        s2 = day_spots[1]; sp2 = spots[s2]
        t += lunch
        d2 = DD[s1, s2]
        p2 = congestion_prob(d2, alpha)
        rd2 = rng.uniform(1,4) if (is_peak(t, t+d2) and rng.random()<p2) else (rng.uniform(0,1.5) if (not is_peak(t, t+d2) and rng.random()<p2*0.5) else 0)
        t += d2 + rd2
        q2 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
        t += q2
        if t < sp2['open']: t = sp2['open']
        v2s = t; t += sp2['t_comf']; v2e = t
        v2ok = (v2e - v2s) >= sp2['t_min'] - 1e-6
    
    # 晚餐
    t += dinner
    
    # 返回酒店
    last = day_spots[-1]
    db = DD[last, 'H']
    pb = congestion_prob(db, alpha)
    rdb = rng.uniform(1,4) if (is_peak(t, t+db) and rng.random()<pb) else (rng.uniform(0,1.5) if (not is_peak(t, t+db) and rng.random()<pb*0.5) else 0)
    t += db + rdb
    return_time = t
    
    end_time = t + TCI + HOME if day_idx==4 else t  # 退房固定0.5h
    end_ok = return_time <= 21.0 + 1e-6
    if day_idx==4: end_ok = end_ok and (end_time <= 21.0 + 1e-6)
    
    return {
        'success': v1ok and v2ok and end_ok,
        'v1_ok': v1ok, 'v2_ok': v2ok, 'end_ok': end_ok,
        'road_delay': rd1 + rd2 + rdb,
        'queue_delay': q1 + q2,
    }

def mc(plan_days, n=20000, alpha=0.3, seed=42):
    rng = np.random.default_rng(seed)
    fails = 0; daily = [0]*5
    road_contrib = [0]*5; queue_contrib = [0]*5
    
    for _ in range(n):
        any_f = False
        for idx, day in enumerate(plan_days):
            res = sim_day(day, idx, rng, alpha)
            if not res['success']:
                daily[idx] += 1
                any_f = True
            road_contrib[idx] += res['road_delay']
            queue_contrib[idx] += res['queue_delay']
        if any_f: fails += 1
    
    avg_road = [x/n for x in road_contrib]
    avg_queue = [x/n for x in queue_contrib]
    
    return {
        'reliability': 1 - fails/n,
        'daily_fails': [x/n for x in daily],
        'avg_road_delay': avg_road,
        'avg_queue_delay': avg_queue,
    }

# 四套方案
plans = {
    'A-满意度优先(8)': [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']],
    'B-均衡稳健(8)':   [['A3'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A5']],
    'C-改进均衡(7)':   [['A10'], ['A1','A8'], ['A2'], ['A4','A9'], ['A3']],
    'D-深度体验(6)':   [['A1'], ['A2'], ['A4'], ['A8','A10'], ['A3']],
}

print("="*70)
print("问题三: 距离拥堵模型 + 蒙特卡罗模拟")
print("p(d) = min(α·d, 1.0), 高峰时p, 平峰时p*0.5")
print("="*70)

# α灵敏度分析
print(f"\n{'α':>6}", end='')
for pn in plans: print(f"  {pn:>16}", end='')
print()
print("-"*76)

for alpha in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]:
    print(f"{alpha:>6.1f}", end='')
    for pn, pd in plans.items():
        res = mc(pd, n=10000, alpha=alpha)
        print(f"  {res['reliability']*100:>15.2f}%", end='')
    print()

# 详细分析 (α=0.3)
print(f"\n{'='*70}")
print("详细分析 α=0.3")
print(f"{'='*70}")

for pn, pd in plans.items():
    res = mc(pd, n=20000, alpha=0.3)
    ns = sum(len(d) for d in pd)
    pf = sum(spots[s]['pref'] for d in pd for s in d)
    print(f"\n{pn}: {ns}景点, 满意度{pf:.1f}")
    print(f"  整体可靠度: {res['reliability']*100:.2f}%")
    for d in range(5):
        print(f"  D{d+1}: 失败{res['daily_fails'][d]*100:.1f}%, "
              f"平均道路延时{res['avg_road_delay'][d]:.2f}h, "
              f"平均排队{res['avg_queue_delay'][d]:.2f}h")
    
    # 扰动贡献
    total_road = sum(res['avg_road_delay'])
    total_queue = sum(res['avg_queue_delay'])
    total = total_road + total_queue
    if total > 0:
        print(f"  扰动贡献: 道路{total_road/total*100:.1f}%, 排队{total_queue/total*100:.1f}%")
