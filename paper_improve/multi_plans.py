"""
问题二补充：多套备选行程方案设计
基于不同出游偏好维度，生成4套方案并对比
"""
import numpy as np
import json

# ============================================================
# 基础数据 (同前)
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

T_MORNING = 1.5
T_LUNCH   = 1.0
T_DINNER  = 1.0

def calc_day(spots_list, include_dinner=True):
    """计算单日行程的理想时间"""
    t = 7.0 + T_MORNING
    t += dist['H'][spots_list[0]]
    if t < spots[spots_list[0]]['open']:
        t = spots[spots_list[0]]['open']
    t += spots[spots_list[0]]['t_comf']
    
    if len(spots_list) == 2:
        t += T_LUNCH + dist[spots_list[0]][spots_list[1]]
        if t < spots[spots_list[1]]['open']:
            t = spots[spots_list[1]]['open']
        t += spots[spots_list[1]]['t_comf']
    
    t += dist[spots_list[-1]]['H']
    if include_dinner:
        t += T_DINNER
    
    pref = sum(spots[s]['pref'] for s in spots_list)
    drive = dist['H'][spots_list[0]]
    for i in range(len(spots_list)-1):
        drive += dist[spots_list[i]][spots_list[i+1]]
    drive += dist[spots_list[-1]]['H']
    load = sum(spots[s]['load'] for s in spots_list)
    
    return {
        'spots': spots_list,
        'end_t': round(t, 2),
        'pref': round(pref, 1),
        'drive': round(drive, 1),
        'load': load,
        'slack': round(21.0 - t, 1),
    }

def calc_plan(plan_days):
    """计算完整5日行程"""
    result = []
    for d, day_spots in enumerate(plan_days):
        has_dinner = d < 4
        info = calc_day(day_spots, include_dinner=has_dinner)
        result.append(info)
    return result

def print_plan(plan, name, description):
    """打印行程方案"""
    print(f"\n{'='*70}")
    print(f"  方案名称: {name}")
    print(f"  偏好定位: {description}")
    print(f"{'='*70}")
    
    all_spots = []
    total_pref = 0
    total_drive = 0
    max_load = 0
    min_slack = 99
    
    for d, day in enumerate(plan, 1):
        s_str = ' → '.join(day['spots'])
        n_str = ' → '.join([spots[s]['name'] for s in day['spots']])
        print(f"  第{d}天: {s_str} ({n_str})")
        print(f"    喜好度={day['pref']}, 行车={day['drive']}h, 负荷={day['load']}, "
              f"结束={day['end_t']:.2f}, 缓冲={day['slack']:.1f}h")
        all_spots.extend(day['spots'])
        total_pref += day['pref']
        total_drive += day['drive']
        max_load = max(max_load, day['load'])
        min_slack = min(min_slack, day['slack'])
    
    n_spots = len(all_spots)
    avg_drive = total_drive / 5
    load_balance = max(plan[d]['load'] for d in range(5)) - min(plan[d]['load'] for d in range(5))
    
    print(f"\n  汇总指标:")
    print(f"    景点数: {n_spots}")
    print(f"    总满意度: {total_pref}")
    print(f"    日均行车: {avg_drive:.1f}h")
    print(f"    最大单日负荷: {max_load}")
    print(f"    负荷均衡差: {load_balance}")
    print(f"    最小缓冲时间: {min_slack:.1f}h")
    
    return {
        'name': name,
        'description': description,
        'spots': all_spots,
        'n_spots': n_spots,
        'total_pref': total_pref,
        'avg_drive': round(avg_drive, 1),
        'max_load': max_load,
        'load_balance': load_balance,
        'min_slack': min_slack,
        'plan': plan,
    }


# ============================================================
# 四套备选方案
# ============================================================

# 方案A: 满意度优先型
# 核心思路: 优先安排高喜好度景点, 利用强联动组合最大化满意度
PLAN_A = calc_plan([
    ['A5'],           # 轻量开局
    ['A1', 'A10'],    # 人文联动 (喜好度16.2)
    ['A2', 'A8'],     # 亲子联动 (喜好度17.5)
    ['A4', 'A9'],     # 自然联动 (喜好度15.0)
    ['A3'],           # 轻松收尾
])

# 方案B: 均衡稳健型
# 核心思路: 避免高耗时叠加, 每日留足缓冲, 兼顾满意度与可靠性
PLAN_B = calc_plan([
    ['A5', 'A10'],    # 人文联动 (轻负荷, 车程0.4h)
    ['A1', 'A8'],     # 人文+亲子 (车程0.3h)
    ['A2'],           # 海洋乐园单独 (避免叠加)
    ['A4'],           # 森林公园单独 (远郊)
    ['A3', 'A7'],     # 滨水收尾 (超轻负荷)
])

# 方案C: 轻松休闲型
# 核心思路: 全部单景点或低负荷组合, 最大化时间弹性, 适合带小孩家庭
PLAN_C = calc_plan([
    ['A10'],          # 文创小镇 (弹性开放到20:00)
    ['A1', 'A8'],     # 人文+亲子 (舒适组合)
    ['A3'],           # 滨海浴场 (全天开放, 轻松)
    ['A9'],           # 山地观景台 (短时高颜值)
    ['A5', 'A7'],     # 古村+湿地 (低负荷收尾)
])

# 方案D: 深度体验型
# 核心思路: 选5个高喜好度景点, 每个给足舒适游览时间, 不赶路
PLAN_D = calc_plan([
    ['A1'],           # 古城老街 (深度游3.5h)
    ['A2'],           # 海洋乐园 (深度游5.0h)
    ['A4'],           # 森林公园 (深度游4.5h)
    ['A8', 'A10'],    # 亲子+文创 (舒适联动)
    ['A3'],           # 滨海浴场 (放松收尾)
])


# ============================================================
# 输出所有方案
# ============================================================
if __name__ == '__main__':
    print("="*70)
    print("  问题二补充：多套备选行程方案设计")
    print("  针对不同出游偏好的四套方案")
    print("="*70)
    
    plans = [
        (PLAN_A, "方案A：满意度优先型", 
         "追求景点数量和喜好度最大化, 适合精力充沛、希望多打卡的家庭"),
        (PLAN_B, "方案B：均衡稳健型", 
         "兼顾满意度与时间弹性, 避免高耗时叠加, 适合一般家庭"),
        (PLAN_C, "方案C：轻松休闲型", 
         "最大化时间弹性, 每日不赶路, 适合带幼儿或老人的家庭"),
        (PLAN_D, "方案D：深度体验型", 
         "精选5个景点深度游览, 不追求打卡数量, 适合注重体验质量的家庭"),
    ]
    
    summaries = []
    for plan, name, desc in plans:
        info = print_plan(plan, name, desc)
        summaries.append(info)
    
    # 对比总表
    print(f"\n\n{'='*70}")
    print("  四套方案对比总表")
    print(f"{'='*70}")
    print(f"{'方案':<20} {'景点数':>6} {'总满意度':>8} {'日均行车':>8} {'最大负荷':>8} {'最小缓冲':>8}")
    print("-"*60)
    for info in summaries:
        print(f"{info['name']:<20} {info['n_spots']:>6} {info['total_pref']:>8.1f} "
              f"{info['avg_drive']:>7.1f}h {info['max_load']:>8} {info['min_slack']:>7.1f}h")
    
    # 保存结果
    output = []
    for info in summaries:
        output.append({
            'name': info['name'],
            'description': info['description'],
            'n_spots': info['n_spots'],
            'total_pref': info['total_pref'],
            'avg_drive': info['avg_drive'],
            'max_load': info['max_load'],
            'load_balance': info['load_balance'],
            'min_slack': info['min_slack'],
            'spots': info['spots'],
            'days': [{'spots': d['spots'], 'end_t': d['end_t'], 'pref': d['pref'], 
                      'drive': d['drive'], 'load': d['load'], 'slack': d['slack']} 
                     for d in info['plan']],
        })
    
    with open('multi_plans.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print("\n结果已保存到 multi_plans.json")
