import numpy as np

combos = {(1,10):0.2,(2,8):0.2,(3,7):0.2,(1,8):0.3,(8,10):0.3,(4,9):0.3,(5,10):0.4}
visit_time = {1:3.5,2:4,3:5,4:3,5:3,6:3,7:3,8:3,9:3,10:4}
hotel_drive = {1:0.13,2:0.5,3:0.5,4:0.5,5:0.5,6:0.5,7:0.5,8:0.5,9:0.5,10:0.17}
windows = [8.0, 12.5, 12.5, 12.5, 8.0]
dinner = 1.0
a_names = {1:"古城老街",2:"海洋乐园",3:"滨海浴场",4:"森林公园",5:"民俗古村",6:"山野溪谷",7:"环湖湿地",8:"亲子农庄",9:"山地观景台",10:"文创小镇"}

scores = np.array([
    [10,3,4,9,8],[4,6,10,7,7],[3,10,7,8,9],[2,8,5,5,5],
    [8,5,4,6,7],[1,9,3,4,4],[3,9,6,7,8],[3,5,10,8,8],
    [2,8,4,5,5],[9,4,7,8,8]
])

A_h = np.array([[1,7,5,5,3],[1/7,1,1/3,1/3,1/5],[1/5,3,1,1,1/3],[1/5,3,1,1,1/3],[1/3,5,3,3,1]])
A_n = np.array([[1,1/7,3,3,1/5],[7,1,7,7,3],[1/3,1/7,1,1,1/5],[1/3,1/7,1,1,1/5],[5,1/3,5,5,1]])
A_f = np.array([[1,3,1/5,1/3,1],[1/3,1,1/7,1/5,1/3],[5,7,1,3,5],[3,5,1/3,1,3],[1,3,1/5,1/3,1]])
A_b = np.array([[1,3,2,3,1],[1/3,1,1/2,1,1/3],[1/2,2,1,2,1/2],[1/3,1,1/2,1,1/3],[1,3,2,3,1]])

def ahp_w(A):
    n=A.shape[0]; ev,ec=np.linalg.eig(A); i=np.argmax(ev.real)
    w=ec[:,i].real; w=w/w.sum()
    CI=(ev[i].real-n)/(n-1); RI={1:0,2:0,3:0.58,4:0.90,5:1.12}[n]
    return w, ev[i].real, CI, CI/RI if RI else 0

def topsis(scores, w):
    mn,mx=scores.min(0),scores.max(0); n=(scores-mn)/(mx-mn); V=n*w
    dp=np.sqrt(((V-V.max(0))**2).sum(1)); dm=np.sqrt(((V-V.min(0))**2).sum(1))
    return dm/(dp+dm)

scenarios = {"人文偏好":A_h,"自然偏好":A_n,"亲子偏好":A_f,"均衡偏好":A_b}
all_S = {}
all_w = {}
for name,A in scenarios.items():
    w,lmax,ci,cr = ahp_w(A); all_w[name]=w
    S = topsis(scores,w); all_S[name]=S
    ranking = np.argsort(-S)+1  # 1-based
    print(f"\n{name}: 权重=[{','.join(f'{x:.3f}' for x in w)}] CR={cr:.4f}")
    for r,idx in enumerate(ranking):
        s=S[idx-1]; lv="高" if s>0.6 else ("中" if s>0.4 else "低")
        print(f"  {r+1}. A{idx} {a_names[idx]:6s} S={s:.4f} [{lv}]")

# ============ 行程方案 ============
def day_cost(day):
    if len(day)==1:
        a=day[0]; return visit_time[a]+hotel_drive[a]*2+dinner
    a,b=day; key=(min(a,b),max(a,b))
    return visit_time[a]+visit_time[b]+hotel_drive[a]+hotel_drive[b]+combos.get(key,0.5)+dinner

def make_plan(pref):
    S=all_S[pref]; ranking=list(np.argsort(-S)+1)  # 1-based
    sel=set(ranking[:8]); plan=[None]*5; used=set()
    # Day1
    for a in ranking:
        if a in sel and a not in used and day_cost([a])<=windows[0]:
            plan[0]=[a]; used.add(a); break
    # Day5
    for a in reversed(ranking):
        if a in sel and a not in used and day_cost([a])<=windows[4]:
            plan[4]=[a]; used.add(a); break
    # Day2-4
    for d in [1,2,3]:
        rem=[a for a in ranking if a in sel and a not in used]
        best=None; bsc=-1
        for i,a in enumerate(rem):
            for b in rem[i+1:]:
                if (min(a,b),max(a,b)) in combos and day_cost([a,b])<=windows[d]:
                    sc=S[a-1]+S[b-1]
                    if sc>bsc: bsc=sc; best=[a,b]
        if best: plan[d]=best; used.update(best)
        elif rem: plan[d]=[rem[0]]; used.add(rem[0])
    rem=[a for a in ranking if a in sel and a not in used]
    for d in range(5):
        if plan[d] is None:
            if rem: plan[d]=[rem.pop(0)]
            else: plan[d]=[]
    return plan

print(f"\n{'='*70}")
print("问题二: 四套行程方案")
print(f"{'='*70}")
all_plans={}
for pref in ["人文偏好","自然偏好","亲子偏好","均衡偏好"]:
    plan=make_plan(pref); all_plans[pref]=plan
    S=all_S[pref]
    sat=sum(S[a-1] for day in plan for a in day)
    nattr=sum(len(day) for day in plan)
    print(f"\n--- {pref} ({nattr}景点, 满意度={sat:.2f}) ---")
    for d,day in enumerate(plan):
        nm="→".join([f"A{a}" for a in day])
        c=day_cost(day); buf=windows[d]-c
        vis=sum(visit_time[a] for a in day)
        if len(day)==2:
            a,b=day; drv=hotel_drive[a]+hotel_drive[b]+combos.get((min(a,b),max(a,b)),0.5)
        else: drv=hotel_drive[day[0]]*2
        print(f"  D{d+1}: {nm:16s} 游{vis:.1f}h+车{drv:.1f}h+餐1h={c:.1f}h 缓冲{buf:.1f}h")

# ============ 蒙特卡洛 ============
print(f"\n{'='*70}")
print("问题三: 蒙特卡洛可靠度 (N=20000)")
print(f"{'='*70}")
np.random.seed(42); N=20000

for alpha in [0.1,0.2,0.3]:
    print(f"\nα={alpha}:")
    for pref in ["人文偏好","自然偏好","亲子偏好","均衡偏好"]:
        plan=all_plans[pref]; ok=0; fail_d=np.zeros(5)
        for _ in range(N):
            good=True
            for d,day in enumerate(plan):
                if not day: continue
                if len(day)==1: bd=hotel_drive[day[0]]*2
                else:
                    a,b=day; bd=hotel_drive[a]+hotel_drive[b]+combos.get((min(a,b),max(a,b)),0.5)
                if np.random.random()<min(alpha*bd,1):
                    bd*=1+np.random.uniform(0.2,0.8)
                tq=0
                for a in day:
                    if d==0: tq+=np.random.uniform(0,1)
                    else:
                        arr=8.5+hotel_drive[a]
                        if 9<=arr<=12: tq+=np.random.uniform(0.5,3)
                        else: tq+=np.random.uniform(0,1)
                act=sum(visit_time[a] for a in day)+bd+tq+dinner
                if act>windows[d]: good=False; fail_d[d]+=1; break
            if good: ok+=1
        R=ok/N; fp=fail_d/N*100; bn=np.argmax(fp)
        print(f"  {pref}: R={R:.3f} 最弱D{bn+1}(失败{fp[bn]:.1f}%)")

