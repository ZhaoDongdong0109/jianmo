"""
C题最终修正版 - 严格按题目逻辑重写
修正:
1. 第1天: 家→酒店4h + 入住0.5h, 之后才能游玩
2. 第5天: 游玩后退房0.5h + 酒店→家4h, 必须在21:00前回到酒店
3. 晚餐不计入7:00-21:00活动窗口
4. 拥堵概率作为连续参数做灵敏度分析
5. 每日出发时间: max(7:00+1.5h, 景点开放时间-车程)
"""

import numpy as np
import json

# ============================================================
# 基础数据
# ============================================================
spots = {
    'A1':  {'name': '古城老街',   'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.5, 'pref': 8.6, 'load': 1},
    'A2':  {'name': '海洋乐园',   'open': 9.0,  'close': 18.0, 't_min': 3.0, 't_comf': 5.0, 'pref': 9.2, 'load': 3},
    'A3':  {'name': '滨海浴场',   'open': 0.0,  'close': 24.0, 't_min': 1.0, 't_comf': 3.0, 'pref': 7.5, 'load': 1},
    'A4':  {'name': '森林公园',   'open': 8.0,  'close': 17.0, 't_min': 3.5, 't_comf': 4.5, 'pref': 8.0, 'load': 3},
    'A5':  {'name': '民俗古村',   'open': 8.0,  'close': 17.5, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.2, 'load': 2},
    'A6':  {'name': '山野溪谷',   'open': 8.0,  'close': 17.0, 't_min': 3.0, 't_comf': 4.0, 'pref': 7.8, 'load': 3},
    'A7':  {'name': '环湖湿地',   'open': 0.0,  'close': 24.0, 't_min': 1.5, 't_comf': 2.5, 'pref': 6.8, 'load': 1},
    'A8':  {'name': '亲子农庄',   'open': 9.0,  'close': 18.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 8.3, 'load': 2},
    'A9':  {'name': '山地观景台', 'open': 8.0,  'close': 17.5, 't_min': 1.5, 't_comf': 2.5, 'pref': 7.0, 'load': 2},
    'A10': {'name': '文创小镇',   'open': 9.0,  'close': 20.0, 't_min': 2.0, 't_comf': 3.0, 'pref': 7.6, 'load': 1},
}

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

T_MORNING = 1.5   # 起床+早餐+整装
T_LUNCH   = 1.0   # 午餐 (景点之间)
T_CHECKIN = 0.5   # 入住/退房
HOME_TO_HOTEL = 4.0  # 家到酒店车程

# ============================================================
# 关键逻辑: 每日活动时间窗口计算
# ============================================================
def calc_day_ideal(spots_list, day_idx):
    """
    计算一天的理想行程 (无随机扰动)
    day_idx: 0=第1天, 1-3=第2-4天, 4=第5天
    
    关键逻辑:
    - 第1天: 从家出发, 7:00起床 → 8:30出发 → 12:30到酒店 → 13:00入住完毕 → 开始游玩
    - 第2-4天: 从酒店出发, 7:00起床 → 8:30出发
    - 第5天: 游玩后退房0.5h + 开车4h回酒店, 必须在21:00前到家
      即: 最晚21:00到家 → 17:00离开酒店 → 16:30退房完毕 → 活动必须在16:30前结束
    
    注意: 晚餐不计入7:00-21:00活动窗口 (返回酒店后的个人安排)
    """
    
    if day_idx == 0:
        # 第1天: 家→酒店→游玩
        t_available_start = 7.0 + T_MORNING + HOME_TO_HOTEL + T_CHECKIN
        # = 7.0 + 1.5 + 4.0 + 0.5 = 13:00
        t_hard_end = 21.0  # 活动必须在21:00前结束 (返回酒店)
    elif day_idx == 4:
        # 第5天: 游玩→退房→酒店→家
        # 活动必须在 (21.0 - T_CHECKIN - HOME_TO_HOTEL) 前结束
        # = 21.0 - 0.5 - 4.0 = 16:30
        t_available_start = 7.0 + T_MORNING  # = 8:30
        t_hard_end = 21.0 - T_CHECKIN - HOME_TO_HOTEL  # = 16:30
    else:
        # 第2-4天: 从酒店出发
        t_available_start = 7.0 + T_MORNING  # = 8:30
        t_hard_end = 21.0  # 活动必须在21:00前结束 (返回酒店)
    
    # 计算行程
    details = []
    t = t_available_start
    
    # 第一个景点
    s1 = spots_list[0]
    sp1 = spots[s1]
    
    # 驱车
    drive1 = dist['H'][s1]
    t += drive1
    details.append(('drive_to', s1, t - drive1, t))
    
    # 等待开放 (如果到达时还没开门)
    if t < sp1['open']:
        t = sp1['open']
    
    # 游览
    visit1_start = t
    visit1_end = t + sp1['t_comf']
    t = visit1_end
    details.append(('visit', s1, visit1_start, visit1_end))
    
    if len(spots_list) == 2:
        s2 = spots_list[1]
        sp2 = spots[s2]
        
        # 午餐
        t += T_LUNCH
        details.append(('lunch', None, t - T_LUNCH, t))
        
        # 驱车
        drive2 = dist[s1][s2]
        t += drive2
        details.append(('drive_to', s2, t - drive2, t))
        
        # 等待开放
        if t < sp2['open']:
            t = sp2['open']
        
        # 游览
        visit2_start = t
        visit2_end = t + sp2['t_comf']
        t = visit2_end
        details.append(('visit', s2, visit2_start, visit2_end))
    
    # 返回酒店
    last = spots_list[-1]
    drive_back = dist[last]['H']
    t += drive_back
    details.append(('drive_back', None, t - drive_back, t))
    
    # 返回酒店时间 (活动结束、回到酒店的时刻)
    return_time = t
    
    # 第5天额外: 退房 + 开车回家
    end_time = t
    if day_idx == 4:
        end_time = t + T_CHECKIN + HOME_TO_HOTEL
    
    # 检查约束
    # 1. 各景点游览时长 >= t_min
    for item in details:
        if item[0] == 'visit':
            sid = item[1]
            duration = item[3] - item[2]
            if duration < spots[sid]['t_min'] - 1e-6:
                return None, f"{sid}游览时长{duration:.2f}h < 最小{spots[sid]['t_min']}h"
    
    # 2. 返回酒店时间 <= 21:00
    if return_time > 21.0 + 1e-6:
        return None, f"返回酒店时间{return_time:.2f} > 21:00"
    
    # 3. 第5天: 到家时间 <= 21:00
    if day_idx == 4 and end_time > 21.0 + 1e-6:
        return None, f"第5天到家时间{end_time:.2f} > 21:00"
    
    # 3. 开放时间检查
    for item in details:
        if item[0] == 'visit':
            sid = item[1]
            sp = spots[sid]
            if sp['open'] < 24 and item[2] < sp['open'] - 1e-6:
                return None, f"{sid}到达时间早于开放时间"
    
    return {
        'spots': spots_list,
        'details': details,
        'return_time': return_time,
        'end_time': end_time,
        'pref': sum(spots[s]['pref'] for s in spots_list),
        'drive': dist['H'][spots_list[0]] + sum(dist[spots_list[i]][spots_list[i+1]] for i in range(len(spots_list)-1)) + dist[spots_list[-1]]['H'],
        'load': sum(spots[s]['load'] for s in spots_list),
        't_available_start': t_available_start,
        't_hard_end': t_hard_end,
        'buffer': t_hard_end - return_time,
    }, "OK"


# ============================================================
# 蒙特卡罗模拟 (修正版)
# ============================================================
def is_peak(t1, t2):
    """判断时间段是否与高峰时段重叠"""
    for ps, pe in [(7,9),(11,13),(16,18)]:
        if t1 < pe and t2 > ps:
            return True
    return False

def sim_day(spots_list, day_idx, rng, p1=0.20, p2=0.08):
    """
    模拟一天行程 (含随机扰动)
    p1: 高峰拥堵概率
    p2: 平峰拥堵概率
    """
    # 通用耗时随机浮动
    morning = T_MORNING * rng.uniform(0.8, 1.2)
    lunch = T_LUNCH * rng.uniform(0.8, 1.2) if len(spots_list) == 2 else 0
    checkin = T_CHECKIN * rng.uniform(0.8, 1.2)
    
    # 确定活动开始时间和硬性结束时间
    if day_idx == 0:
        t_start = 7.0 + morning + HOME_TO_HOTEL + checkin
        t_hard_end = 21.0
    elif day_idx == 4:
        t_start = 7.0 + morning
        t_hard_end = 21.0 - checkin - HOME_TO_HOTEL
    else:
        t_start = 7.0 + morning
        t_hard_end = 21.0
    
    t = t_start
    
    # 第一个景点
    s1 = spots_list[0]
    sp1 = spots[s1]
    
    drive1 = dist['H'][s1]
    # 堵车
    rd1 = 0
    if is_peak(t, t + drive1):
        if rng.random() < p1:
            rd1 = rng.uniform(1, 4)
    else:
        if rng.random() < p2:
            rd1 = rng.uniform(0, 1.5)
    t += drive1 + rd1
    
    # 排队
    q1 = rng.uniform(0.5, 3.0) if 9 <= t < 12 else rng.uniform(0, 1.0)
    t += q1
    
    # 等待开放
    if t < sp1['open']:
        t = sp1['open']
    
    # 游览
    v1_start = t
    v1_end = t + sp1['t_comf']
    t = v1_end
    v1_ok = (v1_end - v1_start) >= sp1['t_min'] - 1e-6
    
    # 第二个景点
    v2_ok = True
    rd2 = 0
    q2 = 0
    if len(spots_list) == 2:
        s2 = spots_list[1]
        sp2 = spots[s2]
        
        t += lunch
        
        drive2 = dist[s1][s2]
        rd2 = 0
        if is_peak(t, t + drive2):
            if rng.random() < p1:
                rd2 = rng.uniform(1, 4)
        else:
            if rng.random() < p2:
                rd2 = rng.uniform(0, 1.5)
        t += drive2 + rd2
        
        q2 = rng.uniform(0.5, 3.0) if 9 <= t < 12 else rng.uniform(0, 1.0)
        t += q2
        
        if t < sp2['open']:
            t = sp2['open']
        
        v2_start = t
        v2_end = t + sp2['t_comf']
        t = v2_end
        v2_ok = (v2_end - v2_start) >= sp2['t_min'] - 1e-6
    
    # 返回酒店
    last = spots_list[-1]
    drive_back = dist[last]['H']
    rdb = 0
    if is_peak(t, t + drive_back):
        if rng.random() < p1:
            rdb = rng.uniform(1, 4)
    else:
        if rng.random() < p2:
            rdb = rng.uniform(0, 1.5)
    t += drive_back + rdb
    
    return_time = t  # 回到酒店的时间
    
    # 第5天: 退房 + 回家
    end_time = t
    if day_idx == 4:
        end_time = t + checkin + HOME_TO_HOTEL
    
    # 判定: 返回酒店时间 <= 21:00, 第5天到家时间 <= 21:00
    end_ok = return_time <= 21.0 + 1e-6
    if day_idx == 4:
        end_ok = end_ok and (end_time <= 21.0 + 1e-6)
    success = v1_ok and v2_ok and end_ok
    
    return {
        'success': success,
        'v1_ok': v1_ok,
        'v2_ok': v2_ok,
        'end_ok': end_ok,
        'return_time': return_time,
        'end_time': t,
        'road_delay': rd1 + rd2 + rdb,
        'queue_delay': q1 + q2,
    }


def mc_eval(plan_days, n_sims=20000, p1=0.20, p2=0.08, seed=42):
    """蒙特卡罗评估"""
    rng = np.random.default_rng(seed)
    
    overall_fails = 0
    daily_fails = [0] * 5
    daily_mintime = [0] * 5
    daily_overtime = [0] * 5
    
    for _ in range(n_sims):
        any_fail = False
        for d, day_spots in enumerate(plan_days):
            res = sim_day(day_spots, d, rng, p1, p2)
            if not res['success']:
                daily_fails[d] += 1
                if not res['v1_ok'] or not res['v2_ok']:
                    daily_mintime[d] += 1
                if not res['end_ok']:
                    daily_overtime[d] += 1
                any_fail = True
        if any_fail:
            overall_fails += 1
    
    return {
        'reliability': 1 - overall_fails / n_sims,
        'daily_fails': [f / n_sims for f in daily_fails],
        'daily_mintime': [f / n_sims for f in daily_mintime],
        'daily_overtime': [f / n_sims for f in daily_overtime],
    }


# ============================================================
# 主程序
# ============================================================
if __name__ == '__main__':
    print("=" * 70)
    print("C题最终修正版 - 严格按题目逻辑")
    print("=" * 70)
    
    # ---- 验证每日时间窗口 ----
    print("\n【每日活动时间窗口验证】")
    for d in range(5):
        if d == 0:
            start = 7.0 + T_MORNING + HOME_TO_HOTEL + T_CHECKIN
            end = 21.0
            note = "家→酒店4h+入住0.5h后开始"
        elif d == 4:
            start = 7.0 + T_MORNING
            end = 21.0 - T_CHECKIN - HOME_TO_HOTEL
            note = "退房0.5h+酒店→家4h前结束"
        else:
            start = 7.0 + T_MORNING
            end = 21.0
            note = "标准日"
        print(f"  第{d+1}天: {start:.1f} ~ {end:.1f} ({end-start:.1f}h可用) [{note}]")
    
    # ---- 设计多套方案 ----
    print("\n" + "=" * 70)
    print("【多套备选方案设计与验证】")
    print("=" * 70)
    
    plans = {
        'A-满意度优先': {
            'desc': '追求景点数量和喜好度最大化',
            'days': [['A5'], ['A1','A10'], ['A2','A8'], ['A4','A9'], ['A3']],
        },
        'B-均衡稳健': {
            'desc': '兼顾满意度与时间弹性',
            'days': [['A5','A10'], ['A1','A8'], ['A2'], ['A4'], ['A3','A7']],
        },
        'C-轻松休闲': {
            'desc': '最大化时间弹性，适合带老幼',
            'days': [['A10'], ['A1','A8'], ['A3'], ['A9'], ['A5','A7']],
        },
        'D-深度体验': {
            'desc': '精选景点深度游览',
            'days': [['A1'], ['A2'], ['A4'], ['A8','A10'], ['A3']],
        },
    }
    
    for pname, pinfo in plans.items():
        print(f"\n--- {pname}: {pinfo['desc']} ---")
        valid = True
        total_pref = 0
        for d, day_spots in enumerate(pinfo['days']):
            res, msg = calc_day_ideal(day_spots, d)
            if res is None:
                print(f"  第{d+1}天 {day_spots}: ❌ {msg}")
                valid = False
            else:
                total_pref += res['pref']
                day_names = ' → '.join([f"{s}({spots[s]['name']})" for s in day_spots])
                print(f"  第{d+1}天 {day_names}")
                print(f"    活动窗口: {res['t_available_start']:.1f}~{res['t_hard_end']:.1f}, "
                      f"返回酒店: {res['return_time']:.2f}, 缓冲: {res['buffer']:.1f}h, "
                      f"喜好度: {res['pref']:.1f}, 行车: {res['drive']:.1f}h")
        if valid:
            n_spots = sum(len(d) for d in pinfo['days'])
            print(f"  ✅ 可行 | {n_spots}景点 | 总满意度: {total_pref:.1f}")
        else:
            print(f"  ❌ 不可行")
    
    # ---- 蒙特卡罗评估 (中度扰动 p1=0.20) ----
    print("\n" + "=" * 70)
    print("【蒙特卡罗评估】中度扰动 p1=0.20, p2=0.08, N=20000")
    print("=" * 70)
    
    print(f"\n{'方案':<16} {'景点':>4} {'满意度':>6} {'可靠度':>8} {'第1天':>6} {'第2天':>6} {'第3天':>6} {'第4天':>6} {'第5天':>6}")
    print("-" * 70)
    
    mc_results = {}
    for pname, pinfo in plans.items():
        res = mc_eval(pinfo['days'], n_sims=20000, p1=0.20, p2=0.08)
        n_spots = sum(len(d) for d in pinfo['days'])
        total_pref = sum(spots[s]['pref'] for d in pinfo['days'] for s in d)
        mc_results[pname] = res
        
        daily_str = ' '.join([f"{f*100:>5.1f}%" for f in res['daily_fails']])
        print(f"{pname:<16} {n_spots:>4} {total_pref:>6.1f} {res['reliability']*100:>7.2f}% {daily_str}")
    
    # ---- 灵敏度分析 ----
    print("\n" + "=" * 70)
    print("【灵敏度分析】p1 从 0.05 到 0.50")
    print("=" * 70)
    
    p1_vals = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.50]
    
    print(f"\n{'p1':>6}", end='')
    for pname in plans:
        print(f"  {pname:>14}", end='')
    print()
    print("-" * 70)
    
    sens_data = {}
    for p1 in p1_vals:
        p2 = p1 * 0.4
        print(f"{p1:>6.2f}", end='')
        for pname, pinfo in plans.items():
            res = mc_eval(pinfo['days'], n_sims=10000, p1=p1, p2=p2)
            print(f"  {res['reliability']*100:>13.2f}%", end='')
            if pname not in sens_data:
                sens_data[pname] = []
            sens_data[pname].append((p1, res['reliability']))
        print()
    
    # ---- 保存结果 ----
    output = {
        'plans': {},
        'mc_results': {},
        'sensitivity': sens_data,
    }
    for pname, pinfo in plans.items():
        n_spots = sum(len(d) for d in pinfo['days'])
        total_pref = sum(spots[s]['pref'] for d in pinfo['days'] for s in d)
        output['plans'][pname] = {
            'days': pinfo['days'],
            'n_spots': n_spots,
            'total_pref': total_pref,
        }
        output['mc_results'][pname] = mc_results[pname]
    
    with open('results_final.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2, default=str)
    print("\n结果已保存到 results_final.json")
    
    # ---- 总结 ----
    print("\n" + "=" * 70)
    print("【总结】")
    print("=" * 70)
    print("修正要点:")
    print("  1. 第1天: 家→酒店4h + 入住0.5h → 13:00开始游玩")
    print("  2. 第5天: 活动必须在16:30前结束 (退房+4h回家)")
    print("  3. 晚餐不计入7:00-21:00活动窗口")
    print("  4. 拥堵概率p1作为连续参数做灵敏度分析")
