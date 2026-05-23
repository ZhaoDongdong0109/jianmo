"""
最终修正版: 严格按题目约束 + 可行方案蒙特卡罗评估
"""
import numpy as np
import json

spots = {
    'A1':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.5, 'pref': 8.6, 'load': 1},
    'A2':  {'open': 9.0,  'close': 18.0, 't_min': 3.0, 't_comf': 5.0, 'pref': 9.2, 'load': 3},
    'A3':  {'open': 0.0,  'close': 24.0, 't_min': 1.0, 't_comf': 3.0, 'pref': 7.5, 'load': 1},
    'A4':  {'open': 8.0,  'close': 17.0, 't_min': 3.5, 't_comf': 4.5, 'pref': 8.0, 'load': 3},
    'A5':  {'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.2, 'load': 2},
    'A7':  {'open': 0.0,  'close': 24.0, 't_min': 1.5, 't_comf': 2.5, 'pref': 6.8, 'load': 1},
    'A8':  {'open': 9.0,  'close': 18.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 8.3, 'load': 2},
    'A9':  {'open': 8.0,  'close': 17.5, 't_min': 1.5, 't_comf': 2.5, 'pref': 7.0, 'load': 2},
    'A10': {'open': 9.0,  'close': 20.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.6, 'load': 1},
}

dist_H = {'A1':0.5,'A2':0.8,'A3':0.3,'A4':1.5,'A5':0.6,'A7':0.4,'A8':0.7,'A9':1.0,'A10':0.5}
dist_ij = {
    ('A1','A10'):0.2, ('A1','A8'):0.3, ('A1','A5'):0.3, ('A1','A2'):0.4,
    ('A2','A8'):0.2, ('A2','A10'):0.3,
    ('A3','A7'):0.2, ('A3','A5'):0.8,
    ('A4','A9'):0.3,
    ('A5','A10'):0.4, ('A5','A7'):0.7,
    ('A8','A10'):0.3, ('A8','A9'):0.5,
}
HOME = 4.0
T_M, T_L, T_CI = 1.5, 1.0, 0.5

def get_d(a,b):
    if a==b: return 0
    if (a,b) in dist_ij: return dist_ij[(a,b)]
    if (b,a) in dist_ij: return dist_ij[(b,a)]
    return dist_H[a]+dist_H[b]

def is_peak(t1,t2):
    for ps,pe in [(7,9),(11,13),(16,18)]:
        if t1<pe and t2>ps: return True
    return False

def sim_day(day_spots, day_idx, rng, p1, p2):
    """模拟一天, 返回是否成功"""
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
    
    s1 = day_spots[0]
    sp1 = spots[s1]
    
    d1 = dist_H[s1]
    rd1 = rng.uniform(1,4) if (is_peak(t,t+d1) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d1) and rng.random()<p2) else 0)
    t += d1 + rd1
    q1 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
    t += q1
    if t < sp1['open']: t = sp1['open']
    v1s = t; t += sp1['t_comf']; v1e = t
    v1ok = (v1e-v1s) >= sp1['t_min'] - 1e-6
    
    v2ok = True
    rd2 = 0; q2 = 0
    if len(day_spots)==2:
        s2 = day_spots[1]; sp2 = spots[s2]
        t += lunch
        d2 = get_d(s1,s2)
        rd2 = rng.uniform(1,4) if (is_peak(t,t+d2) and rng.random()<p1) else (rng.uniform(0,1.5) if (not is_peak(t,t+d2) and rng.random()<p2) else 0)
        t += d2 + rd2
        q2 = rng.uniform(0.5,3) if 9<=t<12 else rng.uniform(0,1)
        t += q2
        if t < sp2['open']: t = sp2['open']
        v2s = t; t += sp2['t_comf']; v2e = t
        v2ok = (v2e-v2s) >= sp2['t_min'] - 1e-6
    
    last = day_spots[-1]
    db = dist_H[last]
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

# 可行方案
plans = {
    'A-满意度优先(8景点)': {
        'days': [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']],
        'desc': 'A5/A1+A10/A2+A8/A4+A9/A3, 最大化满意度'
    },
    'B-均衡稳健(8景点)': {
        'days': [['A10'], ['A1','A8'], ['A2','A9'], ['A4','A3'], ['A5']],
        'desc': 'A10/A1+A8/A2+A9/A4+A3/A5, 均衡分配负荷'
    },
    'C-改进均衡(7景点)': {
        'days': [['A10'], ['A1','A8'], ['A2'], ['A4','A9'], ['A3']],
        'desc': 'A10/A1+A8/A2/A4+A9/A3, A2单独一天'
    },
    'D-深度体验(6景点)': {
        'days': [['A1'], ['A2'], ['A4'], ['A8','A10'], ['A3']],
        'desc': 'A1/A2/A4/A8+A10/A3, 精选深度游'
    },
}

print("="*70)
print("最终修正版: 严格约束 + 蒙特卡罗评估")
print("="*70)

# 验证可行性
print("\n【方案可行性验证】")
for pname, pinfo in plans.items():
    all_ok = True
    for idx, day in enumerate(pinfo['days']):
        # 用理想时间验证
        if idx == 0: t = 7.0+T_M+HOME+T_CI; hard=21.0
        elif idx == 4: t = 7.0+T_M; hard=21.0-T_CI-HOME
        else: t = 7.0+T_M; hard=21.0
        
        s1 = day[0]; t += dist_H[s1]
        if t < spots[s1]['open']: t = spots[s1]['open']
        t += spots[s1]['t_comf']
        if len(day)==2:
            t += T_L + get_d(day[0],day[1])
            s2 = day[1]
            if t < spots[s2]['open']: t = spots[s2]['open']
            t += spots[s2]['t_comf']
        t += dist_H[day[-1]]
        
        if t > hard + 1e-6:
            print(f"  {pname} 第{idx+1}天 {day}: ❌ 结束{t:.2f} > {hard:.1f}")
            all_ok = False
    if all_ok:
        print(f"  {pname}: ✅ 全部可行")

# 蒙特卡罗
print(f"\n【蒙特卡罗评估】p1=0.20, p2=0.08, N=20000")
print(f"{'方案':<22} {'景点':>4} {'满意度':>6} {'可靠度':>8} {'D1':>6} {'D2':>6} {'D3':>6} {'D4':>6} {'D5':>6}")
print("-"*72)

mc_res = {}
for pname, pinfo in plans.items():
    r, dl = mc(pinfo['days'], n=20000, p1=0.20, p2=0.08)
    ns = sum(len(d) for d in pinfo['days'])
    pf = sum(spots[s]['pref'] for d in pinfo['days'] for s in d)
    mc_res[pname] = {'r':r, 'dl':dl, 'ns':ns, 'pf':pf}
    dl_str = ' '.join([f"{x*100:>5.1f}%" for x in dl])
    print(f"{pname:<22} {ns:>4} {pf:>6.1f} {r*100:>7.2f}% {dl_str}")

# 灵敏度分析
print(f"\n【灵敏度分析】p1连续变化")
print(f"{'p1':>6}", end='')
for pn in plans: print(f"  {pn:>16}", end='')
print()
print("-"*76)

for p1 in [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]:
    p2 = p1*0.4
    print(f"{p1:>6.2f}", end='')
    for pname, pinfo in plans.items():
        r,_ = mc(pinfo['days'], n=10000, p1=p1, p2=p2)
        print(f"  {r*100:>15.2f}%", end='')
    print()

# 保存
output = {}
for pname, pinfo in plans.items():
    output[pname] = {
        'days': pinfo['days'],
        'desc': pinfo['desc'],
        'n_spots': mc_res[pname]['ns'],
        'total_pref': mc_res[pname]['pf'],
        'reliability_p20': mc_res[pname]['r'],
        'daily_fails_p20': mc_res[pname]['dl'],
    }
with open('results_final.json','w',encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2, default=str)
print("\n结果已保存")
