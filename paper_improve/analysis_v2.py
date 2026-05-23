"""
C题改进版 v2: 核心计算脚本
修正：
1. 匹配原论文失败判定标准（最小游览时长 + 当日结束时间>21:00）
2. 设计真正可行的稳健改进方案
3. 生成论文所需图表
"""

import numpy as np
import itertools
from collections import defaultdict
import json

# ============================================================
# 1. 基础数据
# ============================================================
spots = {
    'A1':  {'name': '古城老街',   'type': '人文古迹', 'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.5, 'pref': 8.6, 'load': 1},
    'A2':  {'name': '海洋乐园',   'type': '主题游乐', 'open': 9.0,  'close': 18.0, 't_min': 3.0, 't_comf': 5.0, 'pref': 9.2, 'load': 3},
    'A3':  {'name': '滨海浴场',   'type': '休闲度假', 'open': 0.0,  'close': 24.0, 't_min': 1.0, 't_comf': 3.0, 'pref': 7.5, 'load': 1},
    'A4':  {'name': '森林公园',   'type': '自然山林', 'open': 8.0,  'close': 17.0, 't_min': 3.5, 't_comf': 4.5, 'pref': 8.0, 'load': 3},
    'A5':  {'name': '民俗古村',   'type': '人文乡村', 'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.2, 'load': 2},
    'A6':  {'name': '山野溪谷',   'type': '自然徒步', 'open': 8.0,  'close': 17.0, 't_min': 3.0, 't_comf': 4.0, 'pref': 7.8, 'load': 3},
    'A7':  {'name': '环湖湿地',   'type': '生态休闲', 'open': 0.0,  'close': 24.0, 't_min': 1.5, 't_comf': 2.5, 'pref': 6.8, 'load': 1},
    'A8':  {'name': '亲子农庄',   'type': '亲子休闲', 'open': 9.0,  'close': 18.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 8.3, 'load': 2},
    'A9':  {'name': '山地观景台', 'type': '自然观景', 'open': 8.0,  'close': 17.5, 't_min': 1.5, 't_comf': 2.5, 'pref': 7.0, 'load': 2},
    'A10': {'name': '文创小镇',   'type': '人文休闲', 'open': 9.0,  'close': 20.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.6, 'load': 1},
}
ids = list(spots.keys())

dist = {
    'H':  {'H':0.0,'A1':0.5,'A2':0.8,'A3':0.3,'A4':1.5,'A5':0.6,'A6':1.2,'A7':0.4,'A8':0.7,'A9':1.0,'A10':0.5},
    'A1': {'H':0.5,'A1':0.0,'A2':0.4,'A3':0.6,'A4':1.2,'A5':0.3,'A6':1.0,'A7':0.5,'A8':0.3,'A9':0.8,'A10':0.2},
    'A2': {'H':0.8,'A1':0.4,'A2':0.0,'A3':0.5,'A4':1.0,'A5':0.6,'A6':0.9,'A7':0.7,'A8':0.2,'A9':0.6,'A10':0.3},
    'A3': {'H':0.3,'A1':0.6,'A2':0.5,'A3':0.0,'A4':1.3,'A5':0.8,'A6':1.4,'A7':0.2,'A8':0.6,'A9':1.1,'A10':0.5},
    'A4': {'H':1.5,'A1':1.2,'A2':1.0,'A3':1.3,'A4':0.0,'A5':1.0,'A6':0.4,'A7':1.4,'A8':0.9,'A9':0.3,'A10':1.1},
    'A5': {'H':0.6,'A1':0.3,'A2':0.6,'A3':0.8,'A4':1.0,'A5':0.0,'A6':0.8,'A7':0.7,'A8':0.5,'A9':0.7,'A10':0.4},
    'A6': {'H':1.2,'A1':1.0,'A2':0.9,'A3':1.4,'A4':0.4,'A5':0.8,'A6':0.0,'A7':1.3,'A8':0.8,'A9':0.5,'A10':0.9},
    'A7': {'H':0.4,'A1':0.5,'A2':0.7,'A3':0.2,'A4':1.4,'A5':0.7,'A6':1.3,'A7':0.0,'A8':0.6,'A9':1.0,'A10':0.4},
    'A8': {'H':0.7,'A1':0.3,'A2':0.2,'A3':0.6,'A4':0.9,'A5':0.5,'A6':0.8,'A7':0.6,'A8':0.0,'A9':0.5,'A10':0.3},
    'A9': {'H':1.0,'A1':0.8,'A2':0.6,'A3':1.1,'A4':0.3,'A5':0.7,'A6':0.5,'A7':1.0,'A8':0.5,'A9':0.0,'A10':0.7},
    'A10':{'H':0.5,'A1':0.2,'A2':0.3,'A3':0.5,'A4':1.1,'A5':0.4,'A6':0.9,'A7':0.4,'A8':0.3,'A9':0.7,'A10':0.0},
}

T_MORNING = 1.5
T_LUNCH   = 1.0
T_DINNER  = 1.0
T_CHECKIN = 0.5

# ============================================================
# 2. 问题一：TOPSIS计算
# ============================================================
def compute_q1():
    data = {}
    for s in ids:
        sp = spots[s]
        d0 = dist['H'][s]
        avg_d = np.mean([dist[s][t] for t in ids if t != s])
        window = sp['close'] - sp['open']
        openness = 0.0 if window >= 24 else (24 - window) / 24.0
        data[s] = {'d0': d0, 'avg_d': avg_d, 'openness': openness}
    
    pref_vals = [spots[s]['pref'] for s in ids]
    t_vals = [spots[s]['t_comf'] for s in ids]
    comm_vals = [0.5*data[s]['d0'] + 0.5*data[s]['avg_d'] for s in ids]
    jam_vals = [0.45*data[s]['d0'] + 0.35*data[s]['avg_d'] + 0.20*data[s]['openness'] for s in ids]
    
    t_norm = [(v-min(t_vals))/(max(t_vals)-min(t_vals)) if max(t_vals)!=min(t_vals) else 0.5 for v in t_vals]
    load_norm = [(spots[s]['load']-1)/2.0 for s in ids]
    comf_vals = [0.5*load_norm[i] + 0.35*t_norm[i] + 0.15*data[ids[i]]['openness'] for i in range(10)]
    
    def minmax(vals, reverse=False):
        mn, mx = min(vals), max(vals)
        if mx == mn: return [0.5]*len(vals)
        return [(mx-v)/(mx-mn) if reverse else (v-mn)/(mx-mn) for v in vals]
    
    indicators = {
        '喜好度': minmax(pref_vals),
        '耗时灵活性': minmax(t_vals, reverse=True),
        '通勤便利性': minmax(comm_vals, reverse=True),
        '抗拥堵能力': minmax(jam_vals, reverse=True),
        '整体舒适度': minmax(comf_vals, reverse=True),
    }
    
    keys = list(indicators.keys())
    X = np.array([[indicators[k][i] for k in keys] for i in range(10)])
    X_pos = X + 1e-10
    P = X_pos / X_pos.sum(axis=0)
    k_const = 1.0 / np.log(10)
    e = -k_const * (P * np.log(P)).sum(axis=0)
    d = 1 - e
    w = d / d.sum()
    
    V = X * w
    V_plus = V.max(axis=0)
    V_minus = V.min(axis=0)
    D_plus = np.sqrt(((V - V_plus)**2).sum(axis=1))
    D_minus = np.sqrt(((V - V_minus)**2).sum(axis=1))
    S = D_minus / (D_plus + D_minus)
    
    ranking = sorted(range(10), key=lambda i: -S[i])
    
    print("熵权法权重:")
    for i, k_name in enumerate(keys):
        print(f"  {k_name}: w = {w[i]:.4f}")
    
    print("\n景点综合优先级:")
    for rank, idx in enumerate(ranking, 1):
        s = ids[idx]
        level = '高' if rank <= 4 else ('中' if rank <= 8 else '低')
        print(f"  {rank}. {s} {spots[s]['name']}: S={S[idx]:.4f} ({level})")
    
    return S, w


# ============================================================
# 3. 行程模拟器
# ============================================================
def simulate_day(spot_ids, rng, p1=0.20, p2=0.08, include_dinner=True):
    """
    模拟一天行程 (含随机扰动)
    返回: (success, end_time, details_dict)
    success: 当天是否成功
    """
    morning = T_MORNING * rng.uniform(0.8, 1.2)
    lunch = T_LUNCH * rng.uniform(0.8, 1.2) if len(spot_ids) == 2 else 0
    dinner = T_DINNER * rng.uniform(0.8, 1.2) if include_dinner else 0
    
    t = 7.0 + morning
    road_delay_total = 0
    queue_total = 0
    
    # 第一个景点
    s1 = spot_ids[0]
    sp1 = spots[s1]
    
    drive1 = dist['H'][s1]
    rd1 = 0
    if is_peak(t, t+drive1):
        if rng.random() < p1: rd1 = rng.uniform(1, 4)
    else:
        if rng.random() < p2: rd1 = rng.uniform(0, 1.5)
    t += drive1 + rd1
    road_delay_total += rd1
    
    q1 = rng.uniform(0.5, 3.0) if 9 <= t < 12 else rng.uniform(0, 1.0)
    t += q1
    queue_total += q1
    
    if t < sp1['open']: t = sp1['open']
    v1_start = t
    v1_end = t + sp1['t_comf']
    t = v1_end
    v1_ok = (v1_end - v1_start) >= sp1['t_min'] - 1e-6
    
    v2_ok = True
    if len(spot_ids) == 2:
        s2 = spot_ids[1]
        sp2 = spots[s2]
        
        t += lunch
        
        drive2 = dist[s1][s2]
        rd2 = 0
        if is_peak(t, t+drive2):
            if rng.random() < p1: rd2 = rng.uniform(1, 4)
        else:
            if rng.random() < p2: rd2 = rng.uniform(0, 1.5)
        t += drive2 + rd2
        road_delay_total += rd2
        
        q2 = rng.uniform(0.5, 3.0) if 9 <= t < 12 else rng.uniform(0, 1.0)
        t += q2
        queue_total += q2
        
        if t < sp2['open']: t = sp2['open']
        v2_start = t
        v2_end = t + sp2['t_comf']
        t = v2_end
        v2_ok = (v2_end - v2_start) >= sp2['t_min'] - 1e-6
    
    # 返回酒店
    last = spot_ids[-1]
    drive_back = dist[last]['H']
    rd_back = 0
    if is_peak(t, t+drive_back):
        if rng.random() < p1: rd_back = rng.uniform(1, 4)
    else:
        if rng.random() < p2: rd_back = rng.uniform(0, 1.5)
    t += drive_back + rd_back
    road_delay_total += rd_back
    
    if include_dinner:
        t += dinner
    
    end_ok = t <= 21.0 + 1e-6
    success = v1_ok and v2_ok and end_ok
    
    return {
        'success': success,
        'end_time': t,
        'v1_ok': v1_ok,
        'v2_ok': v2_ok,
        'end_ok': end_ok,
        'road_delay': road_delay_total,
        'queue_delay': queue_total,
        'flex_delay': abs(morning - T_MORNING) + abs(lunch - T_LUNCH) + abs(dinner - T_DINNER),
    }

def is_peak(t1, t2):
    for ps, pe in [(7,9),(11,13),(16,18)]:
        if t1 < pe and t2 > ps: return True
    return False


def mc_evaluate(schedule, n_sims=20000, p1=0.20, p2=0.08, seed=42):
    """蒙特卡罗评估一个5日行程"""
    rng = np.random.default_rng(seed)
    
    overall_fails = 0
    daily_fails = [0]*5
    daily_mintime_fails = [0]*5
    daily_overtime_fails = [0]*5
    
    road_delays = [[] for _ in range(5)]
    queue_delays = [[] for _ in range(5)]
    flex_delays = [[] for _ in range(5)]
    end_times = [[] for _ in range(5)]
    
    for _ in range(n_sims):
        any_fail = False
        for d, day in enumerate(schedule):
            has_dinner = d < 4  # 第1-4天有晚餐
            res = simulate_day(day['spots'], rng, p1, p2, include_dinner=has_dinner)
            
            end_times[d].append(res['end_time'])
            road_delays[d].append(res['road_delay'])
            queue_delays[d].append(res['queue_delay'])
            flex_delays[d].append(res['flex_delay'])
            
            if not res['success']:
                daily_fails[d] += 1
                if not res['v1_ok'] or not res['v2_ok']:
                    daily_mintime_fails[d] += 1
                if not res['end_ok']:
                    daily_overtime_fails[d] += 1
                any_fail = True
        
        if any_fail:
            overall_fails += 1
    
    return {
        'reliability': 1 - overall_fails/n_sims,
        'daily_fails': [f/n_sims for f in daily_fails],
        'daily_mintime': [f/n_sims for f in daily_mintime_fails],
        'daily_overtime': [f/n_sims for f in daily_overtime_fails],
        'road_delays': road_delays,
        'queue_delays': queue_delays,
        'flex_delays': flex_delays,
        'end_times': end_times,
    }


# ============================================================
# 4. 多种行程方案
# ============================================================
def make_plan(spots_list):
    """构造行程方案数据"""
    plan = []
    for day_spots in spots_list:
        pref = sum(spots[s]['pref'] for s in day_spots)
        drive = dist['H'][day_spots[0]]
        for i in range(len(day_spots)-1):
            drive += dist[day_spots[i]][day_spots[i+1]]
        drive += dist[day_spots[-1]]['H']
        load = sum(spots[s]['load'] for s in day_spots)
        
        # 计算理想结束时间
        t = 7.0 + T_MORNING
        t += dist['H'][day_spots[0]]
        if t < spots[day_spots[0]]['open']:
            t = spots[day_spots[0]]['open']
        t += spots[day_spots[0]]['t_comf']
        if len(day_spots) == 2:
            t += T_LUNCH + dist[day_spots[0]][day_spots[1]]
            if t < spots[day_spots[1]]['open']:
                t = spots[day_spots[1]]['open']
            t += spots[day_spots[1]]['t_comf']
        t += dist[day_spots[-1]]['H']
        
        plan.append({'spots': day_spots, 'pref': pref, 'drive': drive, 'load': load, 'end_t': t})
    return plan


# 原始方案 (同原论文)
PLAN_ORIGINAL = make_plan([['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']])

# 改进方案v1: 将A2+A8拆分, A4+A9拆分, 增加缓冲
# Day1: A5 民俗古村
# Day2: A1+A10 古城老街+文创小镇 (强联动, 轻负荷)
# Day3: A2 海洋乐园 (单独, 避免叠加)
# Day4: A8+A4 → 改为 A8+A9 (农庄+观景台, 0.5h车程)
# Day5: A3+A7 滨海浴场+环湖湿地 (轻松收尾)
PLAN_IMPROVED_V1 = make_plan([['A5'], ['A1','A10'], ['A2'], ['A8','A9'], ['A3','A7']])

# 改进方案v2: 更保守, 最多7景点
# Day1: A10 文创小镇 (缓冲)
# Day2: A1+A8 古城老街+亲子农庄 (0.3h, 强联动, 中负荷)
# Day3: A2 海洋乐园 (单独)
# Day4: A4 森林公园 (单独, 远郊)
# Day5: A3+A7 滨海浴场+环湖湿地 (轻松)
PLAN_IMPROVED_V2 = make_plan([['A10'], ['A1','A8'], ['A2'], ['A4'], ['A3','A7']])

# 稳健方案: 最大化可靠度
# Day1: A5+A10 民俗古村+文创小镇 (0.4h, 轻负荷)
# Day2: A1+A8 古城老街+亲子农庄 (0.3h)
# Day3: A2 海洋乐园 (单独)
# Day4: A9 山地观景台 (单独, 近郊)
# Day5: A3+A7 滨海浴场+环湖湿地 (0.2h, 超轻)
PLAN_ROBUST = make_plan([['A5','A10'], ['A1','A8'], ['A2'], ['A9'], ['A3','A7']])

# 极简方案: 5景点, 全部低负荷
PLAN_MINIMAL = make_plan([['A10'], ['A1','A8'], ['A3'], ['A9'], ['A5','A7']])


# ============================================================
# 5. 主程序
# ============================================================
def print_plan(plan, name):
    """打印行程"""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    total_pref = 0
    for d, day in enumerate(plan, 1):
        s_str = ' → '.join(day['spots'])
        n_str = ' → '.join([spots[s]['name'] for s in day['spots']])
        has_dinner = d <= 4
        ideal_end = day['end_t'] + (T_DINNER if has_dinner else 0)
        print(f"  第{d}天: {s_str} ({n_str})")
        print(f"    喜好度={day['pref']:.1f}, 行车={day['drive']:.1f}h, 负荷={day['load']}, 理想结束={ideal_end:.2f}")
        total_pref += day['pref']
    all_spots = [s for day in plan for s in day['spots']]
    print(f"  共{len(all_spots)}个景点, 总满意度={total_pref:.1f}")


def run_all():
    print("="*70)
    print("C题改进版 v2: 核心计算")
    print("="*70)
    
    # 问题一
    print("\n\n" + "="*70)
    print("【问题一】景点多维评价与优先级")
    print("="*70)
    S, w = compute_q1()
    
    # 问题二
    print("\n\n" + "="*70)
    print("【问题二】基准行程 (纳入晚餐)")
    print("="*70)
    
    plans = [
        ("原始方案", PLAN_ORIGINAL),
        ("改进方案v1 (A2单独+A8/A9联动)", PLAN_IMPROVED_V1),
        ("改进方案v2 (A4单独)", PLAN_IMPROVED_V2),
        ("稳健方案 (最大化可靠度)", PLAN_ROBUST),
        ("极简方案 (5景点)", PLAN_MINIMAL),
    ]
    
    for name, plan in plans:
        print_plan(plan, name)
    
    # 问题三
    print("\n\n" + "="*70)
    print("【问题三】蒙特卡罗模拟 (含晚餐, 20000次)")
    print("="*70)
    
    scenarios = [("轻度", 0.10, 0.03), ("中度", 0.20, 0.08), ("强扰动", 0.35, 0.15)]
    
    all_results = {}
    for plan_name, plan in plans:
        print(f"\n--- {plan_name} ---")
        all_results[plan_name] = {}
        for s_name, p1, p2 in scenarios:
            res = mc_evaluate(plan, n_sims=20000, p1=p1, p2=p2)
            all_results[plan_name][s_name] = res
            print(f"  {s_name}扰动: 可靠度={res['reliability']*100:.2f}%")
            for d in range(5):
                print(f"    第{d+1}天: 失败={res['daily_fails'][d]*100:.1f}% "
                      f"(时长不达标={res['daily_mintime'][d]*100:.1f}%, 超时={res['daily_overtime'][d]*100:.1f}%)")
    
    # 灵敏度分析
    print("\n\n" + "="*70)
    print("【灵敏度分析】堵车概率 vs 可靠度")
    print("="*70)
    
    p1_vals = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    sens = {}
    for plan_name, plan in [("原始方案", PLAN_ORIGINAL), ("稳健方案", PLAN_ROBUST)]:
        print(f"\n{plan_name}:")
        sens[plan_name] = []
        for p1 in p1_vals:
            p2 = p1 * 0.4
            res = mc_evaluate(plan, n_sims=10000, p1=p1, p2=p2)
            sens[plan_name].append((p1, res['reliability']))
            print(f"  p1={p1:.2f} → 可靠度={res['reliability']*100:.2f}%")
    
    # 输出JSON供绘图使用
    output = {
        'q1_weights': {k: float(w[i]) for i, k in enumerate(['喜好度','耗时灵活性','通勤便利性','抗拥堵能力','整体舒适度'])},
        'plans': {},
        'sensitivity': {},
    }
    for plan_name, plan in plans:
        output['plans'][plan_name] = {
            'spots': [day['spots'] for day in plan],
            'total_pref': sum(day['pref'] for day in plan),
            'n_spots': sum(len(day['spots']) for day in plan),
        }
        for s_name in ['轻度','中度','强扰动']:
            res = all_results[plan_name][s_name]
            output['plans'][plan_name][s_name] = {
                'reliability': res['reliability'],
                'daily_fails': res['daily_fails'],
                'daily_mintime': res['daily_mintime'],
                'daily_overtime': res['daily_overtime'],
            }
    for plan_name in sens:
        output['sensitivity'][plan_name] = sens[plan_name]
    
    with open('results.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\n结果已保存到 results.json")
    
    # 打印改进效果总结
    print("\n\n" + "="*70)
    print("【改进效果总结】")
    print("="*70)
    print(f"{'方案':<25} {'景点数':>6} {'满意度':>8} {'轻度可靠':>10} {'中度可靠':>10} {'强扰动可靠':>12}")
    print("-"*75)
    for plan_name, plan in plans:
        n = sum(len(d['spots']) for d in plan)
        pref = sum(d['pref'] for d in plan)
        r_l = all_results[plan_name]['轻度']['reliability']
        r_m = all_results[plan_name]['中度']['reliability']
        r_h = all_results[plan_name]['强扰动']['reliability']
        print(f"{plan_name:<25} {n:>6} {pref:>8.1f} {r_l*100:>9.2f}% {r_m*100:>9.2f}% {r_h*100:>11.2f}%")


if __name__ == '__main__':
    run_all()
