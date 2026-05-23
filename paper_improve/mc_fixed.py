import numpy as np

combos = {(1,10):0.2,(2,8):0.2,(3,7):0.2,(1,8):0.3,(8,10):0.3,(4,9):0.3,(5,10):0.4}
visit_time = {1:3.5,2:4,3:5,4:3,5:3,6:3,7:3,8:3,9:3,10:4}
hotel_drive = {1:0.13,2:0.5,3:0.5,4:0.5,5:0.5,6:0.5,7:0.5,8:0.5,9:0.5,10:0.17}
windows = [8.0, 12.5, 12.5, 12.5, 8.0]
dinner = 1.0

# 四套方案 (1-based)
plans = {
    "人文偏好": [[10],[1,8],[3,7],[5],[4]],
    "自然偏好": [[3],[4,9],[2,8],[7],[5]],
    "亲子偏好": [[8],[3,7],[10,1],[2],[5]],
    "均衡偏好": [[10],[1,8],[3,7],[5],[4]],
}

np.random.seed(42)
N = 20000

def get_queue(arrive_hour):
    """根据实际到达时间生成排队时间"""
    if 9 <= arrive_hour <= 12:
        return np.random.uniform(0.5, 2.5)  # 高峰
    elif 8 <= arrive_hour < 9 or 12 < arrive_hour <= 14:
        return np.random.uniform(0, 1.0)    # 次高峰
    else:
        return np.random.uniform(0, 0.3)    # 低峰

for alpha in [0.1, 0.2, 0.3]:
    print(f"\n{'='*60}")
    print(f"α={alpha}")
    print(f"{'='*60}")
    for pref, plan in plans.items():
        ok = 0
        fail_d = np.zeros(5)
        fail_detail = {d: {"cong":0, "queue":0, "both":0} for d in range(5)}
        
        for _ in range(N):
            good = True
            for d, day in enumerate(plan):
                if not day: continue
                
                # 计算到达各景点的时间点
                if d == 0:
                    clock = 13.0  # Day1: 13:00出发
                else:
                    clock = 8.5   # Day2-5: 8:30出发
                
                total_actual = 0
                extra_drive = 0
                extra_queue = 0
                
                for i, a in enumerate(day):
                    # 到达时间
                    if i == 0:
                        clock += hotel_drive[a]
                    else:
                        # 景点间转移
                        prev = day[i-1]
                        key = (min(prev,a), max(prev,a))
                        clock += combos.get(key, 0.5)
                    
                    arrive_h = clock
                    
                    # 排队
                    q = get_queue(arrive_h)
                    extra_queue += q
                    clock += q
                    
                    # 游览
                    clock += visit_time[a]
                
                # 堵车 (对整个行程的总行车时间)
                if len(day) == 1:
                    base_drive = hotel_drive[day[0]] * 2
                else:
                    a, b = day
                    base_drive = hotel_drive[a] + hotel_drive[b] + combos.get((min(a,b),max(a,b)), 0.5)
                
                if np.random.random() < min(alpha * base_drive, 1.0):
                    beta = np.random.uniform(0.15, 0.5)  # 堵车延误15%-50%
                    extra_drive = base_drive * beta
                
                # 总耗时
                visit_total = sum(visit_time[a] for a in day)
                actual = visit_total + base_drive + extra_drive + extra_queue + dinner
                
                if actual > windows[d]:
                    good = False
                    fail_d[d] += 1
                    break
            
            if good: ok += 1
        
        R = ok / N
        fp = fail_d / N * 100
        bn = np.argmax(fp)
        print(f"  {pref}: R={R:.3f}  日失败率: " + " ".join([f"D{d+1}={fp[d]:.1f}%" for d in range(5)]))

