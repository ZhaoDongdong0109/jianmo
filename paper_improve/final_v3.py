"""
C题最终修正版 v3 - 完整距离矩阵 + 严格约束
"""
import numpy as np
import json

# 完整距离矩阵 (来自题目)
spots_ids = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10']
_dist_matrix = [
    # H    A1   A2   A3   A4   A5   A6   A7   A8   A9   A10
    [0.0, 0.5, 0.8, 0.3, 1.5, 0.6, 1.2, 0.4, 0.7, 1.0, 0.5],  # H
    [0.5, 0.0, 0.4, 0.6, 1.2, 0.3, 1.0, 0.5, 0.3, 0.8, 0.2],  # A1
    [0.8, 0.4, 0.0, 0.5, 1.0, 0.6, 0.9, 0.7, 0.2, 0.6, 0.3],  # A2
    [0.3, 0.6, 0.5, 0.0, 1.3, 0.8, 1.4, 0.2, 0.6, 1.1, 0.5],  # A3
    [1.5, 1.2, 1.0, 1.3, 0.0, 1.0, 0.4, 1.4, 0.9, 0.3, 1.1],  # A4
    [0.6, 0.3, 0.6, 0.8, 1.0, 0.0, 0.8, 0.7, 0.5, 0.7, 0.4],  # A5
    [1.2, 1.0, 0.9, 1.4, 0.4, 0.8, 0.0, 1.3, 0.8, 0.5, 0.9],  # A6
    [0.4, 0.5, 0.7, 0.2, 1.4, 0.7, 1.3, 0.0, 0.6, 1.0, 0.4],  # A7
    [0.7, 0.3, 0.2, 0.6, 0.9, 0.5, 0.8, 0.6, 0.0, 0.5, 0.3],  # A8
    [1.0, 0.8, 0.6, 1.1, 0.3, 0.7, 0.5, 1.0, 0.5, 0.0, 0.7],  # A9
    [0.5, 0.2, 0.3, 0.5, 1.1, 0.4, 0.9, 0.4, 0.3, 0.7, 0.0],  # A10
]

all_ids = ['H'] + spots_ids
dist_map = {}
for i, a in enumerate(all_ids):
    for j, b in enumerate(all_ids):
        dist_map[(a,b)] = _dist_matrix[i][j]

def D(a,b): return dist_map[(a,b)]

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

HOME = 4.0; T_M = 1.5; T_L = 1.0; T_CI = 0.5

def is_peak(t1,t2):
    for ps,pe in [(7,9),(11,13),(16,18)]:
        if t1<pe and t2>ps: return True
    return False

def sim_day(day_spots, day_idx, rng, p1, p2):
    morning = T_M * rng.uniform(0.8, 1.2)
    lunch = T_L * rng.uniform(0.8, 1.2) if len(day_spots)==2 else 0
    checkin = T_CI * rng.uniform(0.8, 1.2)
    
    if day_idx == 0:
        t = 7.0 + morning + HOME + checkin
        hard_end = 21.0
    elif day_idx == 4:
        t = 7.0 + morning
        hard_end = 21.0 - checkin - HOME
    else:
        t = 7.0 + morning
        hard_end = 21.0
    
    s1 = day_spots[0]; sp1 = spots[s1]
    d1 = D('H', s1)
    rd1 = rng.uniform(1,4) if (is_peak(t,t+d1) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d1) and rng.random()<p2) else 0)
    t += d1 + rd1
    q1 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
    t += q1
    if t < sp1['open']: t = sp1['open']
    v1s = t; t += sp1['t_comf']; v1e = t
    v1ok = (v1e-v1s) >= sp1['t_min'] - 1e-6
    
    v2ok = True; rd2 = 0; q2 = 0
    if len(day_spots)==2:
        s2 = day_spots[1]; sp2 = spots[s2]
        t += lunch
        d2 = D(s1, s2)
        rd2 = rng.uniform(1,4) if (is_peak(t,t+d2) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d2) and rng.random()<p2) else 0)
        t += d2 + rd2
        q2 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
        t += q2
        if t < sp2['open']: t = sp2['open']
        v2s = t; t += sp2['t_comf']; v2e = t
        v2ok = (v2e-v2s) >= sp2['t_min'] - 1e-6
    
    last = day_spots[-1]
    db = D(last, 'H')
    rdb = rng.uniform(1,4) if (is_peak(t,t+db) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+db) and rng.random()<p2) else 0)
    t += db + rdb
    return_time = t
    end_time = t + checkin + HOME if day_idx==4 else t
    end_ok = return_time <= 21.0 + 1e-6
    if day_idx==4: end_ok = end_ok and (end_time <= 21.0 + 1e-6)
    return v1ok and v2ok and end_ok

def mc(plan_days, n=20000, p1=0.20, p2=0.08, seed=42):
    rng = np.random.default_rng(seed)
    fails = 0; daily = [0]*5
    for _ in range(n):
        any_f = False
        for idx,day in enumerate(plan_days):
            if not sim_day(day, idx, rng, p1, p2):
                daily[idx]+=1; any_f=True
        if any_f: fails+=1
    return 1-fails/n, [x/n for x in daily]

def ideal_check(day_spots, day_idx):
    if day_idx==0: t=7.0+T_M+HOME+T_CI; hard=21.0
    elif day_idx==4: t=7.0+T_M; hard=21.0-T_CI-HOME
    else: t=7.0+T_M; hard=21.0
    s1=day_spots[0]; t+=D('H',s1)
    if t<spots[s1]['open']: t=spots[s1]['open']
    t+=spots[s1]['t_comf']
    if len(day_spots)==2:
        t+=T_L+D(day_spots[0],day_spots[1])
        s2=day_spots[1]
        if t<spots[s2]['open']: t=spots[s2]['open']
        t+=spots[s2]['t_comf']
    t+=D(day_spots[-1],'H')
    return t<=hard+1e-6, t, hard-t

# ============================================================
# 四套可行方案 (严格验证)
# ============================================================
plans = {
    'A-满意度优先(8景点)': {
        'days': [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']],
    },
    'B-均衡稳健(8景点)': {
        'days': [['A10'], ['A1','A8'], ['A2','A9'], ['A4','A3'], ['A5']],
    },
    'C-改进均衡(7景点)': {
        'days': [['A10'], ['A1','A8'], ['A2'], ['A4','A9'], ['A3']],
    },
    'D-深度体验(6景点)': {
        'days': [['A1'], ['A2'], ['A4'], ['A8','A10'], ['A3']],
    },
}

print("="*70)
print("C题最终修正版 v3 - 完整距离矩阵")
print("="*70)

print("\n【每日时间窗口】")
print("  第1天: 13:00~21:00 (8h) [家→酒店4h+入住0.5h]")
print("  第2-4天: 8:30~21:00 (12.5h)")
print("  第5天: 8:30~16:30 (8h) [退房0.5h+回家4h]")

print("\n【方案可行性验证】")
for pname, pinfo in plans.items():
    all_ok = True
    for idx, day in enumerate(pinfo['days']):
        ok, end_t, buf = ideal_check(day, idx)
        s_str = '→'.join(day)
        if not ok:
            print(f"  {pname} D{idx+1} {s_str}: ❌ {end_t:.2f}>{21.0 if idx<4 else 16.5:.1f}")
            all_ok = False
    if all_ok:
        n = sum(len(d) for d in pinfo['days'])
        pf = sum(spots[s]['pref'] for d in pinfo['days'] for s in d)
        print(f"  {pname}: ✅ {n}景点, 满意度{pf:.1f}")

print(f"\n【蒙特卡罗评估】p1=0.20, p2=0.08, N=20000")
print(f"{'方案':<22} {'景点':>4} {'满意度':>6} {'可靠度':>8} {'D1':>6} {'D2':>6} {'D3':>6} {'D4':>6} {'D5':>6}")
print("-"*72)

mc_res = {}
for pname, pinfo in plans.items():
    r, dl = mc(pinfo['days'], n=20000, p1=0.20, p2=0.08)
    ns = sum(len(d) for d in pinfo['days'])
    pf = sum(spots[s]['pref'] for d in pinfo['days'] for s in d)
    mc_res[pname] = {'r':r, 'dl':dl}
    print(f"{pname:<22} {ns:>4} {pf:>6.1f} {r*100:>7.2f}% {' '.join([f'{x*100:>5.1f}%' for x in dl])}")

print(f"\n【灵敏度分析】")
print(f"{'p1':>6}", end='')
for pn in plans: print(f"  {pn:>18}", end='')
print()
print("-"*82)

sens = {}
for p1 in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    p2 = p1*0.4
    print(f"{p1:>6.2f}", end='')
    for pname, pinfo in plans.items():
        r,_ = mc(pinfo['days'], n=10000, p1=p1, p2=p2)
        if pname not in sens: sens[pname] = []
        sens[pname].append((p1, r))
        print(f"  {r*100:>17.2f}%", end='')
    print()

output = {}
for pname, pinfo in plans.items():
    output[pname] = {
        'days': pinfo['days'],
        'n_spots': sum(len(d) for d in pinfo['days']),
        'total_pref': sum(spots[s]['pref'] for d in pinfo['days'] for s in d),
        'reliability_p20': mc_res[pname]['r'],
        'daily_fails_p20': mc_res[pname]['dl'],
        'sensitivity': sens.get(pname, []),
    }
with open('results_final.json','w',encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2, default=str)
print("\n已保存到 results_final.json")
