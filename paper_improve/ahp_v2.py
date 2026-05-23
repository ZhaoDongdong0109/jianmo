import numpy as np

# 重新设计评分矩阵 - 让各景点在不同维度上更有区分度
# 评分基于景点的客观属性，1-10分

scores = np.array([
    # C1人文价值  C2自然风光  C3亲子互动  C4通勤便利  C5整体舒适
    [10,         3,          4,          9,          8],   # A1 古城老街 (人文强，自然弱)
    [4,          6,          10,         7,          7],   # A2 海洋乐园 (亲子强)
    [3,          10,         7,          8,          9],   # A3 滨海浴场 (自然强)
    [2,          8,          5,          5,          5],   # A4 森林公园 (自然中等)
    [8,          5,          4,          6,          7],   # A5 民俗古村 (人文较强)
    [1,          9,          3,          4,          4],   # A6 山野溪谷 (自然强，其他弱)
    [3,          9,          6,          7,          8],   # A7 环湖湿地 (自然强)
    [3,          5,          10,         8,          8],   # A8 亲子农庄 (亲子最强)
    [2,          8,          4,          5,          5],   # A9 山地观景台 (自然中等)
    [9,          4,          7,          8,          8],   # A10 文创小镇 (人文强，亲子中)
])

attraction_names = [
    "A1 古城老街", "A2 海洋乐园", "A3 滨海浴场", "A4 森林公园",
    "A5 民俗古村", "A6 山野溪谷", "A7 环湖湿地", "A8 亲子农庄",
    "A9 山地观景台", "A10 文创小镇"
]

criteria_names = ["人文价值C1", "自然风光C2", "亲子互动C3", "通勤便利C4", "整体舒适C5"]

# ========== AHP 判断矩阵 ==========
# 四种偏好: 人文型、自然型、亲子型、均衡型

# 人文型: 人文价值最重要，其次舒适度
A_humanity = np.array([
    [1,   7,   5,   5,   3],    # C1人文 >> 其他
    [1/7, 1,   1/3, 1/3, 1/5],  # C2自然
    [1/5, 3,   1,   1,   1/3],  # C3亲子
    [1/5, 3,   1,   1,   1/3],  # C4通勤
    [1/3, 5,   3,   3,   1],    # C5舒适
])

# 自然型: 自然风光最重要，其次舒适度
A_nature = np.array([
    [1,   1/7, 3,   3,   1/5],  # C1人文
    [7,   1,   7,   7,   3],    # C2自然 >> 其他
    [1/3, 1/7, 1,   1,   1/5],  # C3亲子
    [1/3, 1/7, 1,   1,   1/5],  # C4通勤
    [5,   1/3, 5,   5,   1],    # C5舒适
])

# 亲子型: 亲子互动最重要，其次通勤便利
A_family = np.array([
    [1,   3,   1/5, 1/3, 1],    # C1人文
    [1/3, 1,   1/7, 1/5, 1/3],  # C2自然
    [5,   7,   1,   3,   5],    # C3亲子 >> 其他
    [3,   5,   1/3, 1,   3],    # C4通勤 (带孩子要方便)
    [1,   3,   1/5, 1/3, 1],    # C5舒适
])

# 均衡型: 各方面相对均衡
A_balanced = np.array([
    [1,   3,   2,   3,   1],    # C1人文
    [1/3, 1,   1/2, 1,   1/3],  # C2自然
    [1/2, 2,   1,   2,   1/2],  # C3亲子
    [1/3, 1,   1/2, 1,   1/3],  # C4通勤
    [1,   3,   2,   3,   1],    # C5舒适
])

def ahp_weights(matrix):
    n = matrix.shape[0]
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    max_idx = np.argmax(eigenvalues.real)
    max_eigenvalue = eigenvalues[max_idx].real
    weights = eigenvectors[:, max_idx].real
    weights = weights / weights.sum()
    CI = (max_eigenvalue - n) / (n - 1)
    RI_table = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
    RI = RI_table.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0
    return weights, max_eigenvalue, CI, CR

def topsis_rank(scores, weights):
    min_vals = scores.min(axis=0)
    max_vals = scores.max(axis=0)
    normed = (scores - min_vals) / (max_vals - min_vals)
    weighted = normed * weights
    ideal_pos = weighted.max(axis=0)
    ideal_neg = weighted.min(axis=0)
    d_pos = np.sqrt(((weighted - ideal_pos)**2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_neg)**2).sum(axis=1))
    S = d_neg / (d_pos + d_neg)
    return S

scenarios = {
    "A 人文偏好": A_humanity,
    "B 自然偏好": A_nature,
    "C 亲子偏好": A_family,
    "D 均衡偏好": A_balanced,
}

print("=" * 80)
print("AHP-TOPSIS 多偏好分析 (改进版 - 指标: 人文价值/自然风光/亲子互动/通勤便利/整体舒适)")
print("=" * 80)

for name, matrix in scenarios.items():
    print(f"\n{'='*60}")
    print(f"场景 {name}")
    print(f"{'='*60}")
    weights, lambda_max, CI, CR = ahp_weights(matrix)
    print(f"AHP权重: ", end="")
    for i, w in enumerate(weights):
        print(f"{criteria_names[i]}={w:.3f}  ", end="")
    print(f"\nCR = {CR:.4f} {'✓' if CR < 0.1 else '✗'}")
    
    S = topsis_rank(scores, weights)
    ranking = np.argsort(-S)
    print(f"TOPSIS排序:")
    for rank, idx in enumerate(ranking, 1):
        level = "高" if S[idx] > 0.6 else ("中" if S[idx] > 0.4 else "低")
        print(f"  {rank}. {attraction_names[idx]:12s}  S = {S[idx]:.4f}  [{level}]")

print("\n" + "=" * 80)
print("权重对比汇总")
print("=" * 80)
print(f"{'指标':<10s}", end="")
for name in scenarios:
    print(f"  {name:<10s}", end="")
print()
for i, c in enumerate(criteria_names):
    print(f"{c:<10s}", end="")
    for name, matrix in scenarios.items():
        weights, _, _, _ = ahp_weights(matrix)
        print(f"  {weights[i]:<10.4f}", end="")
    print()

print("\n" + "=" * 80)
print("各偏好下的 TOP5 景点对比")
print("=" * 80)
for name, matrix in scenarios.items():
    weights, _, _, _ = ahp_weights(matrix)
    S = topsis_rank(scores, weights)
    ranking = np.argsort(-S)[:5]
    top5 = ", ".join([f"{attraction_names[i]}({S[i]:.2f})" for i in ranking])
    print(f"{name}: {top5}")

