"""
C题改进版：景点优选与行程规划 - 核心计算脚本
改进点：
1. 第二问基准行程纳入晚餐（第1-4天）
2. 第三问增加稳健改进方案对比
3. 增加堵车概率灵敏度分析
4. 增加可靠度-满意度Pareto分析
"""

import numpy as np
import itertools
from collections import defaultdict

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

ids = ['A1','A2','A3','A4','A5','A6','A7','A8','A9','A10']

# 车程矩阵 (酒店为H)
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

# 通用固定耗时
T_MORNING = 1.5   # 起床+早餐+整装
T_LUNCH   = 1.0   # 午餐
T_DINNER  = 1.0   # 晚餐
T_CHECKIN = 0.5   # 入住/退房

# ============================================================
# 2. 问题一：多维指标与TOPSIS
# ============================================================
def compute_q1():
    """计算景点多维指标与综合优先级"""
    # 原始数据
    data = {}
    for s in ids:
        sp = spots[s]
        d0 = dist['H'][s]  # 酒店到景点车程
        avg_d = np.mean([dist[s][t] for t in ids if t != s])  # 到其他景点平均车程
        
        # 开放时间紧张度 (可用游览窗口越短越紧张)
        window = sp['close'] - sp['open']
        if window >= 24:  # 全天开放
            openness = 0.0
        else:
            openness = (24 - window) / 24.0
        
        data[s] = {
            'pref': sp['pref'],
            't_comf': sp['t_comf'],
            'd0': d0,
            'avg_d': avg_d,
            'openness': openness,
            'load': sp['load'],
        }
    
    # 构造五维指标 (越大越优)
    # 1. 喜好度: 直接用pref
    pref_vals = [data[s]['pref'] for s in ids]
    
    # 2. 耗时灵活性: 舒适游览时长越短越好
    t_vals = [data[s]['t_comf'] for s in ids]
    
    # 3. 通勤便利性: 0.5*d0 + 0.5*avg_d 越小越好
    comm_vals = [0.5*data[s]['d0'] + 0.5*data[s]['avg_d'] for s in ids]
    
    # 4. 抗拥堵能力: 0.45*d0 + 0.35*avg_d + 0.20*openness 越小越好
    jam_vals = [0.45*data[s]['d0'] + 0.35*data[s]['avg_d'] + 0.20*data[s]['openness'] for s in ids]
    
    # 5. 整体舒适度: 0.5*load + 0.35*t_comf_norm + 0.15*openness 越小越好
    load_norm = [(data[s]['load']-1)/2.0 for s in ids]  # 归一化到[0,1]
    t_norm = [(data[s]['t_comf']-min(t_vals))/(max(t_vals)-min(t_vals)) for s in ids]
    comf_vals = [0.5*load_norm[i] + 0.35*t_norm[i] + 0.15*data[ids[i]]['openness'] for i in range(10)]
    
    # Min-Max标准化 (效益型直接, 成本型反向)
    def minmax(vals, reverse=False):
        mn, mx = min(vals), max(vals)
        if mx == mn:
            return [0.5]*len(vals)
        if reverse:
            return [(mx-v)/(mx-mn) for v in vals]
        else:
            return [(v-mn)/(mx-mn) for v in vals]
    
    indicators = {
        '喜好度': minmax(pref_vals),
        '耗时灵活性': minmax(t_vals, reverse=True),
        '通勤便利性': minmax(comm_vals, reverse=True),
        '抗拥堵能力': minmax(jam_vals, reverse=True),
        '整体舒适度': minmax(comf_vals, reverse=True),
    }
    
    # 熵权法
    n = len(ids)
    m = len(indicators)
    keys = list(indicators.keys())
    X = np.array([[indicators[k][i] for k in keys] for i in range(n)])  # n x m
    
    # 避免log(0), 加微小值
    X_pos = X + 1e-10
    col_sums = X_pos.sum(axis=0)
    P = X_pos / col_sums  # 归一化
    
    k = 1.0 / np.log(n)
    e = -k * (P * np.log(P)).sum(axis=0)  # 信息熵
    d = 1 - e  # 差异系数
    w = d / d.sum()  # 权重
    
    print("=" * 60)
    print("问题一：熵权法权重")
    print("=" * 60)
    for i, k_name in enumerate(keys):
        print(f"  {k_name}: w = {w[i]:.4f}")
    
    # TOPSIS
    V = X * w  # 加权矩阵
    V_plus = V.max(axis=0)
    V_minus = V.min(axis=0)
    
    D_plus = np.sqrt(((V - V_plus)**2).sum(axis=1))
    D_minus = np.sqrt(((V - V_minus)**2).sum(axis=1))
    S = D_minus / (D_plus + D_minus)
    
    ranking = sorted(range(n), key=lambda i: -S[i])
    
    print("\n景点综合优先级排序:")
    print(f"{'排名':<4} {'景点':<10} {'喜好度':>6} {'耗时灵活':>8} {'通勤便利':>8} {'抗拥堵':>6} {'舒适度':>6} {'综合指数':>8} {'优先级':>6}")
    for rank, idx in enumerate(ranking, 1):
        s = ids[idx]
        level = '高' if rank <= 4 else ('中' if rank <= 8 else '低')
        print(f"{rank:<4} {s+' '+spots[s]['name']:<10} "
              f"{indicators['喜好度'][idx]:>6.4f} {indicators['耗时灵活性'][idx]:>8.4f} "
              f"{indicators['通勤便利性'][idx]:>8.4f} {indicators['抗拥堵能力'][idx]:>6.4f} "
              f"{indicators['整体舒适度'][idx]:>6.4f} {S[idx]:>8.4f} {level:>6}")
    
    return S, indicators, w

# ============================================================
# 3. 问题二：基准行程规划 (纳入晚餐)
# ============================================================
def compute_day_schedule(spot_ids, include_dinner=True):
    """
    计算一天的行程时序安排
    spot_ids: 当天景点列表 (1个或2个)
    include_dinner: 是否纳入返回酒店后的晚餐
    返回: (可行, 结束时间, 行程详情列表)
    """
    details = []
    t = 7.0  # 7:00 起床
    
    # 起床+早餐+整装
    t += T_MORNING
    details.append(('起床早餐', 7.0, t))
    
    # 第一个景点
    s1 = spot_ids[0]
    sp1 = spots[s1]
    
    # 驱车前往第一个景点
    drive1 = dist['H'][s1]
    t += drive1
    details.append((f'驱车→{s1}', t - drive1, t))
    
    # 到达时间检查：不能早于开放时间
    if t < sp1['open']:
        t = sp1['open']
    
    # 排队等待 (基准行程不考虑)
    # 游览
    visit1_start = t
    visit1_end = t + sp1['t_comf']
    t = visit1_end
    details.append((f'游览{s1}', visit1_start, visit1_end))
    
    if len(spot_ids) == 2:
        s2 = spot_ids[1]
        sp2 = spots[s2]
        
        # 午餐 (在两个景点之间)
        lunch_start = t
        t += T_LUNCH
        details.append(('午餐', lunch_start, t))
        
        # 驱车前往第二个景点
        drive2 = dist[s1][s2]
        t += drive2
        details.append((f'驱车→{s2}', t - drive2, t))
        
        # 到达时间检查
        if t < sp2['open']:
            t = sp2['open']
        
        # 游览
        visit2_start = t
        visit2_end = t + sp2['t_comf']
        t = visit2_end
        details.append((f'游览{s2}', visit2_start, visit2_end))
    
    # 返回酒店
    last_spot = spot_ids[-1]
    drive_back = dist[last_spot]['H']
    t += drive_back
    details.append((f'返回酒店', t - drive_back, t))
    
    # 晚餐 (仅第1-4天)
    if include_dinner:
        dinner_start = t
        t += T_DINNER
        details.append(('晚餐', dinner_start, t))
    
    # 检查约束
    # 1. 所有景点游览时长 >= t_min
    for item in details:
        if item[0].startswith('游览'):
            sid = item[0].replace('游览', '')
            duration = item[2] - item[1]
            if duration < spots[sid]['t_min'] - 1e-6:
                return False, t, details, f"{sid}游览时长{duration:.2f}h < 最小{spots[sid]['t_min']}h"
    
    # 2. 结束时间 <= 21:00
    if t > 21.0 + 1e-6:
        return False, t, details, f"结束时间{t:.2f} > 21:00"
    
    # 3. 开放时间检查
    for item in details:
        if item[0].startswith('游览'):
            sid = item[0].replace('游览', '')
            sp = spots[sid]
            if sp['open'] < 24:  # 非全天开放
                if item[1] < sp['open'] - 1e-6:
                    return False, t, details, f"{sid}到达时间早于开放时间"
    
    return True, t, details, "OK"


def compute_day_score(spot_ids):
    """计算一天方案的综合得分"""
    pref_sum = sum(spots[s]['pref'] for s in spot_ids)
    drive_sum = dist['H'][spot_ids[0]]
    for i in range(len(spot_ids)-1):
        drive_sum += dist[spot_ids[i]][spot_ids[i+1]]
    drive_sum += dist[spot_ids[-1]]['H']
    load_sum = sum(spots[s]['load'] for s in spot_ids)
    return pref_sum, drive_sum, load_sum


def generate_all_day_plans():
    """枚举所有可行的单日方案"""
    plans = []
    # 单景点
    for s in ids:
        ok, end_t, details, msg = compute_day_schedule([s], include_dinner=True)
        if ok:
            pref, drive, load = compute_day_score([s])
            plans.append({
                'spots': [s],
                'end_t': end_t,
                'details': details,
                'pref': pref,
                'drive': drive,
                'load': load,
            })
    
    # 双景点
    for s1, s2 in itertools.permutations(ids, 2):
        ok, end_t, details, msg = compute_day_schedule([s1, s2], include_dinner=True)
        if ok:
            pref, drive, load = compute_day_score([s1, s2])
            plans.append({
                'spots': [s1, s2],
                'end_t': end_t,
                'details': details,
                'pref': pref,
                'drive': drive,
                'load': load,
            })
    
    return plans


def solve_dp(all_plans):
    """
    动态规划求解五日行程
    状态: dp[d][used_spots_bitmask] = (best_score, plan_sequence)
    """
    n_spots = len(ids)
    spot_to_idx = {s: i for i, s in enumerate(ids)}
    
    # 按天分组计划
    day_plans = all_plans  # 所有可行单日方案
    
    # DP: dp[d][mask] = (score, plan_list)
    INF_NEG = -1e18
    dp = [defaultdict(lambda: (INF_NEG, [])) for _ in range(6)]
    dp[0][(0,)] = (0.0, [])  # 初始状态: 0天, 0景点
    
    for d in range(1, 6):  # 第1-5天
        is_last_4_days = (d <= 4)  # 前4天有晚餐
        for plan in day_plans:
            plan_spots = plan['spots']
            plan_mask = tuple(sorted([spot_to_idx[s] for s in plan_spots]))
            
            # 检查该方案是否包含晚餐 (前4天需要)
            # 这里简化: 所有plan都已包含晚餐, 第5天不包含晚餐的单独处理
            include_dinner = (d <= 4)
            
            # 重新计算第5天(不包含晚餐)
            if d == 5:
                ok, end_t, details, msg = compute_day_schedule(plan_spots, include_dinner=False)
                if not ok:
                    continue
            
            for prev_mask, (prev_score, prev_plans) in list(dp[d-1].items()):
                # 检查景点不重复
                used = set(prev_mask)
                conflict = False
                for idx in plan_mask:
                    if idx in used:
                        conflict = True
                        break
                if conflict:
                    continue
                
                new_mask = tuple(sorted(set(prev_mask) | set(plan_mask)))
                
                # 计算综合得分 (多目标加权)
                # 总满意度
                total_pref = prev_score + plan['pref']
                # 行车负荷惩罚
                drive_penalty = plan['drive'] * 0.3
                # 松紧均衡: 用结束时间差异
                
                new_score = total_pref - drive_penalty
                
                if new_score > dp[d][new_mask][0]:
                    dp[d][new_mask] = (new_score, prev_plans + [plan])
    
    # 找最优解 (5-8个景点)
    best_score = INF_NEG
    best_plans = None
    best_count = 0
    
    for mask, (score, plans) in dp[5].items():
        n_selected = len(mask)
        if 5 <= n_selected <= 8:
            # 综合评价: 满意度 - 行车负荷 - 松紧不均衡
            total_pref = sum(p['pref'] for p in plans)
            total_drive = sum(p['drive'] for p in plans)
            drive_loads = [p['drive'] for p in plans]
            activity_times = [p['end_t'] - 7.0 for p in plans]  # 简化
            
            # 松紧不均衡惩罚
            mean_drive = np.mean(drive_loads)
            std_drive = np.std(drive_loads)
            mean_act = np.mean(activity_times)
            std_act = np.std(activity_times)
            
            Z = total_pref - 0.3*total_drive - 0.5*std_drive - 0.3*std_act
            
            if Z > best_score:
                best_score = Z
                best_plans = plans
                best_count = n_selected
    
    return best_plans, best_score, best_count


def solve_greedy_with_dinner():
    """
    贪心+枚举求解: 纳入晚餐的基准行程
    更可靠的方法: 先生成所有可行5日方案, 取最优
    """
    all_plans = generate_all_day_plans()
    print(f"\n可行单日方案总数: {len(all_plans)}")
    
    # 按景点数分类
    single_plans = [p for p in all_plans if len(p['spots']) == 1]
    double_plans = [p for p in all_plans if len(p['spots']) == 2]
    print(f"  单景点方案: {len(single_plans)}")
    print(f"  双景点方案: {len(double_plans)}")
    
    # 用DP求解
    best_plans, best_score, best_count = solve_dp(all_plans)
    
    if best_plans is None:
        print("未找到可行方案!")
        return None
    
    return best_plans, best_score, best_count


def print_schedule(plans, title="基准行程"):
    """打印行程安排"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}")
    
    for d, plan in enumerate(plans, 1):
        spots_str = ' → '.join(plan['spots'])
        names_str = ' → '.join([spots[s]['name'] for s in plan['spots']])
        print(f"\n第{d}天: {spots_str} ({names_str})")
        print(f"  喜好度: {plan['pref']:.1f}, 行车: {plan['drive']:.1f}h, 体力负荷: {plan['load']}")
        for item in plan['details']:
            name, start, end = item
            print(f"  {start:05.2f} - {end:05.2f}  {name}")
        print(f"  当日结束: {plan['end_t']:05.2f}")
    
    # 汇总
    total_pref = sum(p['pref'] for p in plans)
    total_spots = sum(len(p['spots']) for p in plans)
    all_spots = []
    for p in plans:
        all_spots.extend(p['spots'])
    
    print(f"\n汇总: 共{total_spots}个景点, 总喜好度={total_pref:.1f}")
    print(f"景点: {', '.join(all_spots)}")


# ============================================================
# 4. 问题三：蒙特卡罗模拟
# ============================================================
def monte_carlo_sim(plans, n_sims=20000, p1=0.20, p2=0.08, seed=42):
    """
    蒙特卡罗模拟评估行程可靠度
    plans: 五日行程方案
    p1: 高峰拥堵概率
    p2: 平峰拥堵概率
    """
    rng = np.random.default_rng(seed)
    
    n_fail = 0
    daily_fails = [0] * 5
    fail_by_mintime = [0] * 5
    fail_by_overtime = [0] * 5
    
    # 每日延迟统计
    road_delays = [[] for _ in range(5)]
    queue_delays = [[] for _ in range(5)]
    flex_delays = [[] for _ in range(5)]
    
    for sim in range(n_sims):
        overall_fail = False
        
        for d, plan in enumerate(plans):
            day_fail = False
            spots_today = plan['spots']
            
            # 随机通用耗时
            morning = T_MORNING * rng.uniform(0.8, 1.2)
            lunch = T_LUNCH * rng.uniform(0.8, 1.2)
            dinner = T_DINNER * rng.uniform(0.8, 1.2) if d < 4 else 0
            checkin = T_CHECKIN * rng.uniform(0.8, 1.2)
            
            t = 7.0 + morning
            
            # 第一个景点
            s1 = spots_today[0]
            sp1 = spots[s1]
            
            # 驱车 (可能堵车)
            drive1_base = dist['H'][s1]
            road_delay1 = 0
            if is_peak_hour(t, t + drive1_base):
                if rng.random() < p1:
                    road_delay1 = rng.uniform(1, 4)
            else:
                if rng.random() < p2:
                    road_delay1 = rng.uniform(0, 1.5)
            t += drive1_base + road_delay1
            
            # 到达后排队
            queue1 = 0
            if 9.0 <= t < 12.0:
                queue1 = rng.uniform(0.5, 3.0)
            else:
                queue1 = rng.uniform(0, 1.0)
            t += queue1
            
            # 游览
            if t < sp1['open']:
                t = sp1['open']
            visit1_start = t
            visit1_end = t + sp1['t_comf']
            t = visit1_end
            
            if len(spots_today) == 2:
                s2 = spots_today[1]
                sp2 = spots[s2]
                
                # 午餐
                t += lunch
                
                # 驱车
                drive2_base = dist[s1][s2]
                road_delay2 = 0
                if is_peak_hour(t, t + drive2_base):
                    if rng.random() < p1:
                        road_delay2 = rng.uniform(1, 4)
                else:
                    if rng.random() < p2:
                        road_delay2 = rng.uniform(0, 1.5)
                t += drive2_base + road_delay2
                
                # 排队
                queue2 = 0
                if 9.0 <= t < 12.0:
                    queue2 = rng.uniform(0.5, 3.0)
                else:
                    queue2 = rng.uniform(0, 1.0)
                t += queue2
                
                # 游览
                if t < sp2['open']:
                    t = sp2['open']
                visit2_start = t
                visit2_end = t + sp2['t_comf']
                t = visit2_end
                
                # 检查第二个景点
                if visit2_end - visit2_start < sp2['t_min'] - 1e-6:
                    day_fail = True
                    fail_by_mintime[d] += 1
            
            # 检查第一个景点
            if visit1_end - visit1_start < sp1['t_min'] - 1e-6:
                day_fail = True
                fail_by_mintime[d] += 1
            
            # 返回酒店
            last_spot = spots_today[-1]
            drive_back = dist[last_spot]['H']
            road_delay_back = 0
            if is_peak_hour(t, t + drive_back):
                if rng.random() < p1:
                    road_delay_back = rng.uniform(1, 4)
            else:
                if rng.random() < p2:
                    road_delay_back = rng.uniform(0, 1.5)
            t += drive_back + road_delay_back
            
            # 晚餐
            if d < 4:
                t += dinner
            
            # 检查结束时间
            if t > 21.0 + 1e-6:
                day_fail = True
                fail_by_overtime[d] += 1
            
            if day_fail:
                daily_fails[d] += 1
                overall_fail = True
            
            # 记录延迟
            total_road = road_delay1 + (road_delay2 if len(spots_today)==2 else 0) + road_delay_back
            total_queue = queue1 + (queue2 if len(spots_today)==2 else 0)
            total_flex = (morning - T_MORNING) + (lunch - T_LUNCH if len(spots_today)==2 else 0) + (dinner - T_DINNER if d<4 else 0)
            
            road_delays[d].append(total_road)
            queue_delays[d].append(total_queue)
            flex_delays[d].append(abs(total_flex))
        
        if overall_fail:
            n_fail += 1
    
    reliability = 1 - n_fail / n_sims
    
    return {
        'reliability': reliability,
        'n_fail': n_fail,
        'n_sims': n_sims,
        'daily_fails': [f/n_sims for f in daily_fails],
        'fail_by_mintime': [f/n_sims for f in fail_by_mintime],
        'fail_by_overtime': [f/n_sims for f in fail_by_overtime],
        'road_delays': road_delays,
        'queue_delays': queue_delays,
        'flex_delays': flex_delays,
    }


def is_peak_hour(t_start, t_end):
    """判断行程是否经过高峰时段"""
    peak_ranges = [(7.0, 9.0), (11.0, 13.0), (16.0, 18.0)]
    for ps, pe in peak_ranges:
        if t_start < pe and t_end > ps:
            return True
    return False


def sensitivity_analysis(plans):
    """堵车概率灵敏度分析"""
    print("\n" + "=" * 70)
    print("堵车概率灵敏度分析")
    print("=" * 70)
    
    p1_values = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    results = []
    
    for p1 in p1_values:
        p2 = p1 * 0.4  # 平峰约为高峰的40%
        res = monte_carlo_sim(plans, n_sims=10000, p1=p1, p2=p2)
        results.append((p1, p2, res['reliability']))
        print(f"  p1={p1:.2f}, p2={p2:.2f} → 可靠度={res['reliability']*100:.2f}%")
    
    return results


def pareto_analysis():
    """
    Pareto分析: 满意度 vs 可靠度
    生成多种方案, 比较其满意度和可靠度
    """
    print("\n" + "=" * 70)
    print("Pareto分析: 满意度 vs 可靠度")
    print("=" * 70)
    
    # 方案1: 原始方案 (A5, A1+A10, A2+A8, A4+A9, A3)
    plan_original = [
        {'spots': ['A5'], 'pref': 7.2, 'drive': 1.2, 'load': 2, 'end_t': 16.42,
         'details': [('起床早餐',7.0,8.5),('驱车→A5',8.5,9.1),('游览A5',9.1,12.1),('返回酒店',12.1,12.7),('晚餐',12.7,13.7)]},
        {'spots': ['A1','A10'], 'pref': 16.2, 'drive': 1.2, 'load': 2, 'end_t': 17.12,
         'details': [('起床早餐',7.0,8.5),('驱车→A1',8.5,9.0),('游览A1',9.0,12.5),('午餐',12.5,13.5),('驱车→A10',13.5,13.7),('游览A10',13.7,16.7),('返回酒店',16.7,17.2),('晚餐',17.2,18.2)]},
        {'spots': ['A2','A8'], 'pref': 17.5, 'drive': 1.7, 'load': 5, 'end_t': 18.12,
         'details': [('起床早餐',7.0,8.5),('驱车→A2',8.5,9.3),('游览A2',9.3,14.3),('午餐',14.3,15.3),('驱车→A8',15.3,15.5),('游览A8',15.5,17.5),('返回酒店',17.5,18.2),('晚餐',18.2,19.2)]},
        {'spots': ['A4','A9'], 'pref': 15.0, 'drive': 2.8, 'load': 5, 'end_t': 18.18,
         'details': [('起床早餐',7.0,8.5),('驱车→A4',8.5,10.0),('游览A4',10.0,14.5),('午餐',14.5,15.5),('驱车→A9',15.5,15.8),('游览A9',15.8,17.3),('返回酒店',17.3,18.3),('晚餐',18.3,19.3)]},
        {'spots': ['A3'], 'pref': 7.5, 'drive': 0.6, 'load': 1, 'end_t': 17.36,
         'details': [('起床早餐',7.0,8.5),('驱车→A3',8.5,8.8),('游览A3',8.8,11.8),('返回酒店',11.8,12.1)]},
    ]
    
    # 方案2: 改进方案 - A4+A9拆分, A2单独一天
    # 第1天: A5 民俗古村
    # 第2天: A1+A10 古城老街+文创小镇
    # 第3天: A2 海洋乐园 (单独)
    # 第4天: A4 森林公园 (单独) + A8 亲子农庄
    # 第5天: A3+A9 滨海浴场+山地观景台
    plan_improved = [
        {'spots': ['A5'], 'pref': 7.2, 'drive': 1.2, 'load': 2, 'end_t': 16.42,
         'details': [('起床早餐',7.0,8.5),('驱车→A5',8.5,9.1),('游览A5',9.1,12.1),('返回酒店',12.1,12.7),('晚餐',12.7,13.7)]},
        {'spots': ['A1','A10'], 'pref': 16.2, 'drive': 1.2, 'load': 2, 'end_t': 17.12,
         'details': [('起床早餐',7.0,8.5),('驱车→A1',8.5,9.0),('游览A1',9.0,12.5),('午餐',12.5,13.5),('驱车→A10',13.5,13.7),('游览A10',13.7,16.7),('返回酒店',16.7,17.2),('晚餐',17.2,18.2)]},
        {'spots': ['A2'], 'pref': 9.2, 'drive': 1.6, 'load': 3, 'end_t': 17.6,
         'details': [('起床早餐',7.0,8.5),('驱车→A2',8.5,9.3),('游览A2',9.3,14.3),('返回酒店',14.3,15.1),('晚餐',15.1,16.1)]},
        {'spots': ['A4','A8'], 'pref': 16.3, 'drive': 2.9, 'load': 5, 'end_t': 18.4,
         'details': [('起床早餐',7.0,8.5),('驱车→A4',8.5,10.0),('游览A4',10.0,14.5),('午餐',14.5,15.5),('驱车→A8',15.5,16.4),('游览A8',16.4,18.4),('返回酒店',18.4,19.1),('晚餐',19.1,20.1)]},
        {'spots': ['A3','A9'], 'pref': 14.5, 'drive': 1.9, 'load': 3, 'end_t': 17.8,
         'details': [('起床早餐',7.0,8.5),('驱车→A3',8.5,8.8),('游览A3',8.8,11.8),('午餐',11.8,12.8),('驱车→A9',12.8,13.9),('游览A9',13.9,16.4),('返回酒店',16.4,17.4)]},
    ]
    
    # 方案3: 稳健方案 - 全部单景点或低负荷双景点
    # 第1天: A10 文创小镇
    # 第2天: A1+A8 古城老街+亲子农庄
    # 第3天: A2 海洋乐园 (单独)
    # 第4天: A9 山地观景台 (单独)
    # 第5天: A3+A7 滨海浴场+环湖湿地
    plan_robust = [
        {'spots': ['A10'], 'pref': 7.6, 'drive': 1.0, 'load': 1, 'end_t': 16.0,
         'details': [('起床早餐',7.0,8.5),('驱车→A10',8.5,9.0),('游览A10',9.0,12.0),('返回酒店',12.0,12.5),('晚餐',12.5,13.5)]},
        {'spots': ['A1','A8'], 'pref': 16.9, 'drive': 1.3, 'load': 3, 'end_t': 17.5,
         'details': [('起床早餐',7.0,8.5),('驱车→A1',8.5,9.0),('游览A1',9.0,12.5),('午餐',12.5,13.5),('驱车→A8',13.5,13.8),('游览A8',13.8,16.8),('返回酒店',16.8,17.5),('晚餐',17.5,18.5)]},
        {'spots': ['A2'], 'pref': 9.2, 'drive': 1.6, 'load': 3, 'end_t': 17.6,
         'details': [('起床早餐',7.0,8.5),('驱车→A2',8.5,9.3),('游览A2',9.3,14.3),('返回酒店',14.3,15.1),('晚餐',15.1,16.1)]},
        {'spots': ['A9'], 'pref': 7.0, 'drive': 2.0, 'load': 2, 'end_t': 15.5,
         'details': [('起床早餐',7.0,8.5),('驱车→A9',8.5,9.5),('游览A9',9.5,12.0),('返回酒店',12.0,13.0),('晚餐',13.0,14.0)]},
        {'spots': ['A3','A7'], 'pref': 14.3, 'drive': 0.9, 'load': 2, 'end_t': 16.5,
         'details': [('起床早餐',7.0,8.5),('驱车→A3',8.5,8.8),('游览A3',8.8,11.8),('午餐',11.8,12.8),('驱车→A7',12.8,13.0),('游览A7',13.0,15.5),('返回酒店',15.5,15.9)]},
    ]
    
    # 方案4: 极端稳健 - 最少景点(5个), 全部低负荷
    plan_minimal = [
        {'spots': ['A5'], 'pref': 7.2, 'drive': 1.2, 'load': 2, 'end_t': 16.0,
         'details': [('起床早餐',7.0,8.5),('驱车→A5',8.5,9.1),('游览A5',9.1,12.1),('返回酒店',12.1,12.7),('晚餐',12.7,13.7)]},
        {'spots': ['A1'], 'pref': 8.6, 'drive': 1.0, 'load': 1, 'end_t': 15.5,
         'details': [('起床早餐',7.0,8.5),('驱车→A1',8.5,9.0),('游览A1',9.0,12.5),('返回酒店',12.5,13.0),('晚餐',13.0,14.0)]},
        {'spots': ['A8','A10'], 'pref': 15.9, 'drive': 1.3, 'load': 3, 'end_t': 17.8,
         'details': [('起床早餐',7.0,8.5),('驱车→A8',8.5,9.2),('游览A8',9.2,12.2),('午餐',12.2,13.2),('驱车→A10',13.2,13.5),('游览A10',13.5,16.5),('返回酒店',16.5,17.0),('晚餐',17.0,18.0)]},
        {'spots': ['A3'], 'pref': 7.5, 'drive': 0.6, 'load': 1, 'end_t': 14.0,
         'details': [('起床早餐',7.0,8.5),('驱车→A3',8.5,8.8),('游览A3',8.8,11.8),('返回酒店',11.8,12.1),('晚餐',12.1,13.1)]},
        {'spots': ['A7'], 'pref': 6.8, 'drive': 0.8, 'load': 1, 'end_t': 14.5,
         'details': [('起床早餐',7.0,8.5),('驱车→A7',8.5,8.9),('游览A7',8.9,11.4),('返回酒店',11.4,11.8)]},
    ]
    
    plans_list = [
        ("原始方案(8景点)", plan_original),
        ("改进方案A(8景点)", plan_improved),
        ("稳健方案(7景点)", plan_robust),
        ("极简方案(5景点)", plan_minimal),
    ]
    
    results = []
    for name, plan in plans_list:
        total_pref = sum(p['pref'] for p in plan)
        n_spots = sum(len(p['spots']) for p in plan)
        
        # 中度扰动
        res = monte_carlo_sim(plan, n_sims=20000, p1=0.20, p2=0.08)
        
        results.append({
            'name': name,
            'n_spots': n_spots,
            'total_pref': total_pref,
            'reliability': res['reliability'],
            'daily_fails': res['daily_fails'],
        })
        
        print(f"\n{name}:")
        print(f"  景点数: {n_spots}, 总满意度: {total_pref:.1f}")
        print(f"  中度扰动可靠度: {res['reliability']*100:.2f}%")
        for d in range(5):
            print(f"    第{d+1}天失败率: {res['daily_fails'][d]*100:.2f}%")
    
    return results


# ============================================================
# 5. 主程序
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("C题改进版：景点优选与行程规划")
    print("=" * 70)
    
    # 问题一
    print("\n\n" + "=" * 70)
    print("第一部分：问题一 - 景点多维评价与优先级")
    print("=" * 70)
    S, indicators, w = compute_q1()
    
    # 问题二: 生成基准行程 (纳入晚餐)
    print("\n\n" + "=" * 70)
    print("第二部分：问题二 - 基准行程规划 (纳入晚餐)")
    print("=" * 70)
    
    # 使用手工设计的行程 (基于DP结果和联动组合)
    # 第1天: A5 民俗古村 (轻量开局)
    # 第2天: A1+A10 古城老街+文创小镇 (强联动)
    # 第3天: A2+A8 海洋乐园+亲子农庄 (强联动)
    # 第4天: A4+A9 森林公园+山地观景台 (强联动)
    # 第5天: A3 滨海浴场 (轻松收尾)
    
    baseline_plans = []
    for day_spots in [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']]:
        include_dinner = (len(baseline_plans) < 4)  # 前4天有晚餐
        ok, end_t, details, msg = compute_day_schedule(day_spots, include_dinner=include_dinner)
        if ok:
            pref, drive, load = compute_day_score(day_spots)
            baseline_plans.append({
                'spots': day_spots,
                'end_t': end_t,
                'details': details,
                'pref': pref,
                'drive': drive,
                'load': load,
            })
        else:
            print(f"  {day_spots} 不可行: {msg}")
    
    print_schedule(baseline_plans, "原始基准行程 (纳入晚餐)")
    
    # 问题三: 蒙特卡罗模拟
    print("\n\n" + "=" * 70)
    print("第三部分：问题三 - 蒙特卡罗模拟")
    print("=" * 70)
    
    # 三种情景
    scenarios = [
        ("轻度扰动", 0.10, 0.03),
        ("中度扰动", 0.20, 0.08),
        ("强扰动",   0.35, 0.15),
    ]
    
    for name, p1, p2 in scenarios:
        res = monte_carlo_sim(baseline_plans, n_sims=20000, p1=p1, p2=p2)
        print(f"\n{name} (p1={p1}, p2={p2}):")
        print(f"  整体可靠度: {res['reliability']*100:.2f}%")
        for d in range(5):
            print(f"    第{d+1}天: 失败率={res['daily_fails'][d]*100:.2f}%, "
                  f"最小游览时长不达标={res['fail_by_mintime'][d]*100:.2f}%, "
                  f"超时={res['fail_by_overtime'][d]*100:.2f}%")
    
    # 灵敏度分析
    sens_results = sensitivity_analysis(baseline_plans)
    
    # Pareto分析 (对比多种方案)
    print("\n\n" + "=" * 70)
    print("第四部分：Pareto分析 - 多方案对比")
    print("=" * 70)
    pareto_results = pareto_analysis()
    
    # 保存结果
    print("\n\n" + "=" * 70)
    print("所有计算完成!")
    print("=" * 70)
