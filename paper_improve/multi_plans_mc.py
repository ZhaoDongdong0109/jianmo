"""
对4套备选方案进行蒙特卡罗可靠度评估
"""
import numpy as np
import json

spots = {
    'A1':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.5, 'pref': 8.6, 'load': 1},
    'A2':  {'open': 9.0,  'close': 18.0, 't_min': 3.0, 't_comf': 5.0, 'pref': 9.2, 'load': 3},
    'A3':  {'open': 0.0,  'close': 24.0, 't_min': 1.0, 't_comf': 3.0, 'pref': 7.5, 'load': 1},
    'A4':  {'open': 8.0,  'close': 17.0, 't_min': 3.5, 't_comf': 4.5, 'pref': 8.0, 'load': 3},
    'A5':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.2, 'load': 2},
    'A6':  {'open': 8.0,  'close': 17.0, 't_min': 3.0, 't_comf': 4.0, 'pref': 7.8, 'load': 3},
    'A7':  {'open': 0.0,  'close': 24.0, 't_min': 1.5, 't_comf': 2.5, 'pref': 6.8, 'load': 1},
    'A8':  {'open': 9.0,  'close': 18.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 8.3, 'load': 2},
    'A9':  {'open': 8.0,  'close': 17.5, 't_min': 1.5, 't_comf': 2.5, 'pref': 7.0, 'load': 2},
    'A10': {'open': 9.0,  'close': 20.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.6, 'load': 1},
}
dist = {
    'H':  {'A1':0.5,'A2':0.8,'A3':0.3,'A4':1.5,'A5':0.6,'A6':1.2,'A7':0.4,'A8':0.7,'A9':1.0,'A10':0.5},
    'A1': {'H':0.5,'A2':0.4,'A3':0.6,'A4':1.2,'A5':0.3,'A6':1.0,'A7':0.5,'A8':0.3,'A9':0.8,'A10':0.2},
    'A2': {'H':0.8,'A1':0.4,'A3':0.5,'A4':1.0,'A5':0.6,'A6':0.9,'A7':0.7,'A8':0.2,'A9':0.6,'A10':0.3},
    'A3': {'H':0.3,'A1':0.6,'A2':0.5,'A4':1.3,'A5':0.8,'A6':1.4,'A7':0.2,'A8':0.6,'A9':1.1,'A10':0.5},
    'A4': {'H':1.5,'A1':1.2,'A2':1.0,'A3':1.3,'A5':1.0,'A6':0.4,'A7':1.4,'A8':0.9,'A9':0.3,'A10':1.1},
    'A5': {'H':0.6,'A1':0.3,'A2':0.6,'A3':0.8,'A4':1.0,'A6':0.8,'A7':0.7,'A8':0.5,'A9':0.7,'A10':0.4},
    'A6': {'H':1.2,'A1':1.0,'A2':0.9,'A3':1.4,'A4':0.4,'A5':0.8,'A7':1.3,'A8':0.8,'A9':0.5,'A10':0.9},
    'A7': {'H':0.4,'A1':0.5,'A2':0.7,'A3':0.2,'A4':1.4,'A5':0.7,'A6':1.3,'A8':0.6,'A9':1.0,'A10':0.4},
    'A8': {'H':0.7,'A1':0.3,'A2':0.2,'A3':0.6,'A4':0.9,'A5':0.5,'A6':0.8,'A7':0.6,'A9':0.5,'A10':0.3},
    'A9': {'H':1.0,'A1':0.8,'A2':0.6,'A3':1.1,'A4':0.3,'A5':0.7,'A6':0.5,'A7':1.0,'A8':0.5,'A10':0.7},
    'A10':{'H':0.5,'A1':0.2,'A2':0.3,'A3':0.5,'A4':1.1,'A5':0.4,'A6':0.9,'A7':0.4,'A8':0.3,'A9':0.7},
}

T_MORNING, T_LUNCH, T_DINNER = 1.5, 1.0, 1.0

def is_peak(t1, t2):
    for ps, pe in [(7,9),(11,13),(16,18)]:
        if t1 < pe and t2 > ps: return True
    return False

def sim_day(spots_list, rng, p1, p2, has_dinner):
    morning = T_MORNING * rng.uniform(0.8, 1.2)
    lunch = T_LUNCH * rng.uniform(0.8, 1.2) if len(spots_list)==2 else 0
    dinner = T_DINNER * rng.uniform(0.8, 1.2) if has_dinner else 0
    
    t = 7.0 + morning
    s1 = spots_list[0]
    d1 = dist['H'][s1]
    rd1 = rng.uniform(1,4) if (is_peak(t,t+d1) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d1) and rng.random()<p2) else 0)
    t += d1 + rd1
    q1 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
    t += q1
    if t < spots[s1]['open']: t = spots[s1]['open']
    v1s = t; t += spots[s1]['t_comf']; v1e = t
    v1ok = (v1e-v1s) >= spots[s1]['t_min']-1e-6
    
    v2ok = True
    if len(spots_list)==2:
        s2 = spots_list[1]
        t += lunch
        d2 = dist[s1][s2]
        rd2 = rng.uniform(1,4) if (is_peak(t,t+d2) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d2) and rng.random()<p2) else 0)
        t += d2 + rd2
        q2 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
        t += q2
        if t < spots[s2]['open']: t = spots[s2]['open']
        v2s = t; t += spots[s2]['t_comf']; v2e = t
        v2ok = (v2e-v2s) >= spots[s2]['t_min']-1e-6
    
    last = spots_list[-1]
    db = dist[last]['H']
    rdb = rng.uniform(1,4) if (is_peak(t,t+db) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+db) and rng.random()<p2) else 0)
    t += db + rdb
    if has_dinner: t += dinner
    
    return v1ok and v2ok and t<=21.0+1e-6

def mc(plan_days, n=20000, p1=0.20, p2=0.08, seed=42):
    rng = np.random.default_rng(seed)
    fails = 0
    daily = [0]*5
    for _ in range(n):
        any_f = False
        for d, day in enumerate(plan_days):
            ok = sim_day(day, rng, p1, p2, d<4)
            if not ok: daily[d]+=1; any_f=True
        if any_f: fails+=1
    return 1-fails/n, [x/n for x in daily]

# 4套方案
plans = {
    'A-满意度优先': [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']],
    'B-均衡稳健':   [['A5','A10'], ['A1','A8'], ['A2'], ['A4'], ['A3','A7']],
    'C-轻松休闲':   [['A10'], ['A1','A8'], ['A3'], ['A9'], ['A5','A7']],
    'D-深度体验':   [['A1'], ['A2'], ['A4'], ['A8','A10'], ['A3']],
}

scenarios = [('轻度',0.10,0.03), ('中度',0.20,0.08), ('强扰动',0.35,0.15)]

print(f"{'方案':<16} {'景点':>4} {'满意度':>6} {'轻度':>8} {'中度':>8} {'强扰动':>8}")
print("-"*56)

results = {}
for name, days in plans.items():
    n_spots = sum(len(d) for d in days)
    pref = sum(spots[s]['pref'] for d in days for s in d)
    results[name] = {'n_spots': n_spots, 'pref': pref, 'days': days, 'scenarios': {}}
    vals = []
    for sname, p1, p2 in scenarios:
        r, dl = mc(days, p1=p1, p2=p2)
        results[name]['scenarios'][sname] = {'reliability': r, 'daily': dl}
        vals.append(f"{r*100:.1f}%")
    print(f"{name:<16} {n_spots:>4} {pref:>6.1f} {vals[0]:>8} {vals[1]:>8} {vals[2]:>8}")

# 保存
with open('multi_plans_mc.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2, default=str)
print("\n已保存到 multi_plans_mc.json")
