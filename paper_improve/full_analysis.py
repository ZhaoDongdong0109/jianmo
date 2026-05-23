import numpy as np

# ==================== 基础数据 ====================
combos = {(1,10):0.2,(2,8):0.2,(3,7):0.2,(1,8):0.3,(8,10):0.3,(4,9):0.3,(5,10):0.4}
visit_time = {1:3.5,2:4,3:5,4:3,5:3,6:3,7:3,8:3,9:3,10:4}
hotel_drive = {1:0.13,2:0.5,3:0.5,4:0.5,5:0.5,6:0.5,7:0.5,8:0.5,9:0.5,10:0.17}
windows = [8.0, 12.5, 12.5, 12.5, 8.0]
dinner = 1.0
a_names = {1:"古城老街",2:"海洋乐园",3:"滨海浴场",4:"森林公园",5:"民俗古村",6:"山野溪谷",7:"环湖湿地",8:"亲子农庄",9:"山地观景台",10:"文创小镇"}

# ==================== 评分矩阵 (5维) ====================
scores = np.array([
    [10,3,4,9,8],[4,6,10,7,7],[3,10,7,8,9],[2,8,5,5,5],
    [8,5,4,6,7],[1,9,3,4,4],[3,9,6,7,8],[3,5,10,8,8],
    [2,8,4,5,5],[9,4,7,8,8]
])
criteria = ["人文价值","自然风光","亲子互动","通勤便利","整体舒适"]

# ==================== AHP ====================
A_humanity = np.array([[1,7,5,5,3],[1/7,1,1/3,1/3,1/5],[1/5,3,1,1,1/3],[1/5,3,1,1,1/3],[1/3,5,3,3,1]])
A_nature   = np.array([[1,1/7,3,3,1/5],[7,1,7,7,3],[1/3,1/7,1,1,1/5],[1/3,1/7,1,1,1/5],[5,1/3,5,5,1]])
A_family   = np.array([[1,3,1/5,1/3,1],[1/3,1,1/7,1/5,1/3],[5,7,1,3,5],[3,5,1/3,1,3],[1,3,1/5,1/3,1]])
A_balanced = np.array([[1,3,2,3,1],[1/3,1,1/2,1,1/3],[1/2,2,1,2,1/2],[1/3,1,1/2,1,1/3],[1,3,2,3,1]])

def ahp_weights(matrix):
    n = matrix.shape[0]
    eigvals, eigvecs = np.linalg.eig(matrix)
    idx = np.argmax(eigvals.real)
    w = eigvecs[:,idx].real; w = w/w.sum()
    CI = (eigvals[idx].real - n)/(n-1)
    RI = {1:0,2:0,3:0.58,4:0.90,5:1.12}[n]
    CR = CI/RI if RI else 0
    return w, eigvals[idx].real, CI, CR

def topsis(scores, weights):
    mn, mx = scores.min(0), scores.max(0)
    normed = (scores-mn)/(mx-mn)
    V = normed * weights
    dp = np.sqrt(((V-V.max(0))**2).sum(1))
    dm = np.sqrt(((V-V.min(0))**2).sum(1))
    return dm/(dp+dm)

# ==================== 四偏好权重 ====================
scenarios = {"人文偏好":A_humanity,"自然偏好":A_nature,"亲子偏好":A_family,"均衡偏好":A_balanced}
all_weights = {}
for name, A in scenarios.items():
    w, lmax, ci, cr = ahp_weights(A)
    all_weights[name] = w
    S = topsis(scores, w)
    ranking = np.argsort(-S)
    print(f"\n{'='*60}")
    print(f"{name}  AHP权重: {[f'{x:.3f}' for x in w]}  CR={cr:.4f}")
    print(f"TOPSIS排序:")
    for r, i in enumerate(ranking,1):
        lv = "高" if S[i]>0.6 else ("中" if S[i]>0.4 else "低")
        print(f"  {r}. A{i+1} {a_names[i+1]:6s}  S={S[i]:.4f} [{lv}]")

# ==================== 问题二: 四套行程方案 ====================
sats = {}
for name, w in all_weights.items():
    sats[name] = topsis(scores, w)

def day_cost(day):
    if len(day)==1:
        a=day[0]; return visit_time[a]+hotel_drive[a]*2+dinner
    a,b=day; key=(min(a,b),max(a,b))
    return visit_time[a]+visit_time[b]+hotel_drive[a]+hotel_drive[b]+combos.get(key,0.5)+dinner

def make_plan(pref_name):
    S = sats[pref_name]
    ranking = np.argsort(-S)
    selected = set(ranking[:8])
    plan = [None]*5; used = set()
    # Day1: 近的高分单景点
    for a in ranking:
        if a in selected and a not in used and day_cost([a])<=windows[0]:
            plan[0]=[a]; used.add(a); break
    # Day5: 远的低分单景点
    for a in reversed(ranking):
        if a in selected and a not in used and day_cost([a])<=windows[4]:
            plan[4]=[a]; used.add(a); break
    # Day2-4: 联动组合优先
    for d in [1,2,3]:
        rem = [a for a in ranking if a in selected and a not in used]
        best_pair=None; best_sc=-1
        for i,a in enumerate(rem):
            for b in rem[i+1:]:
                if (min(a,b),max(a,b)) in combos and day_cost([a,b])<=windows[d]:
                    sc = S[a]+S[b]
                    if sc>best_sc: best_sc=sc; best_pair=[a,b]
        if best_pair:
            plan[d]=best_pair; used.update(best_pair)
        elif rem:
            plan[d]=[rem[0]]; used.add(rem[0])
    # 补漏
    rem = [a for a in ranking if a in selected and a not in used]
    for d in range(5):
        if plan[d] is None:
            if rem: plan[d]=[rem[0]]; used.add(rem[0]); rem.pop(0)
            else: plan[d]=[]
    return plan

print(f"\n{'='*60}")
print("问题二: 四种偏好的行程方案")
print(f"{'='*60}")

all_plans = {}
for pref in ["人文偏好","自然偏好","亲子偏好","均衡偏好"]:
    plan = make_plan(pref)
    all_plans[pref] = plan
    S = sats[pref]
    total_sat = sum(S[a] for day in plan for a in day)
    n_attr = sum(len(day) for day in plan)
    print(f"\n--- {pref} ({n_attr}景点, 满意度={total_sat:.2f}) ---")
    for d,day in enumerate(plan):
        names = "→".join([f"A{a+1}" for a in day])
        cost = day_cost(day)
        buf = windows[d]-cost
        print(f"  D{d+1}: {names:20s}  耗时{cost:.1f}h  缓冲{buf:.1f}h")

# ==================== 问题三: 蒙特卡洛可靠度 ====================
print(f"\n{'='*60}")
print("问题三: 蒙特卡洛可靠度分析 (N=20000)")
print(f"{'='*60}")

np.random.seed(42)
N = 20000

for alpha in [0.1, 0.2, 0.3]:
    print(f"\n--- α={alpha} (堵车概率系数) ---")
    for pref in ["人文偏好","自然偏好","亲子偏好","均衡偏好"]:
        plan = all_plans[pref]
        success_count = 0
        fail_days = np.zeros(5)
        
        for _ in range(N):
            all_ok = True
            for d,day in enumerate(plan):
                if not day: continue
                # 堵车
                if len(day)==1:
                    a=day[0]; base_drive=hotel_drive[a]*2
                else:
                    a,b=day; base_drive=hotel_drive[a]+hotel_drive[b]+combos.get((min(a,b),max(a,b)),0.5)
                
                p_cong = min(alpha * base_drive, 1.0)
                if np.random.random() < p_cong:
                    beta = np.random.uniform(0.2, 0.8)
                    actual_drive = base_drive * (1+beta)
                else:
                    actual_drive = base_drive
                
                # 排队
                total_queue = 0
                for a in day:
                    if d==0:
                        # Day1: 13:00后到, 非高峰
                        total_queue += np.random.uniform(0, 1.0)
                    else:
                        # 9:00前到可能避开高峰
                        arrive_h = 8.5 + hotel_drive[a]
                        if 9 <= arrive_h <= 12:
                            total_queue += np.random.uniform(0.5, 3.0)
                        else:
                            total_queue += np.random.uniform(0, 1.0)
                
                visit = sum(visit_time[a] for a in day)
                actual = visit + actual_drive + total_queue + dinner
                
                if actual > windows[d]:
                    all_ok = False
                    fail_days[d] += 1
                    break
            
            if all_ok:
                success_count += 1
        
        R = success_count / N
        fail_pct = fail_days / N * 100
        bottleneck_d = np.argmax(fail_pct)
        print(f"  {pref}: 可靠度 R={R:.4f}  最薄弱D{bottleneck_d+1}(失败率{fail_pct[bottleneck_d]:.1f}%)")

