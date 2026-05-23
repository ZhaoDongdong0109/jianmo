import numpy as np

# ========== AHP 层次分析法 ==========

# 5个指标: 喜好度C1, 耗时灵活性C2, 通勤便利性C3, 抗拥堵能力C4, 整体舒适度C5

# 1-9标度含义:
# 1=同等重要, 3=稍微重要, 5=明显重要, 7=强烈重要, 9=极端重要
# 倒数表示反向比较

# ========== 四种偏好场景的判断矩阵 ==========

# 场景A: 人文偏好 (喜欢历史街区、古村、文创)
A_humanity = np.array([
    [1,   3,   5,   5,   3],    # C1喜好度最重要
    [1/3, 1,   3,   3,   1],    # C2耗时灵活性
    [1/5, 1/3, 1,   1,   1/3],  # C3通勤便利性
    [1/5, 1/3, 1,   1,   1/3],  # C4抗拥堵能力
    [1/3, 1,   3,   3,   1],    # C5整体舒适度
])

# 场景B: 自然偏好 (喜欢山水、海滩、湿地)
A_nature = np.array([
    [1,   1/3, 3,   1,   1/3],  # C1喜好度
    [3,   1,   5,   3,   1],    # C2耗时灵活性 (自然景点需要更多时间)
    [1/3, 1/5, 1,   1/3, 1/5],  # C3通勤便利性
    [1,   1/3, 3,   1,   1/3],  # C4抗拥堵能力
    [3,   1,   5,   3,   1],    # C5整体舒适度 (自然环境最重要)
])

# 场景C: 亲子偏好 (喜欢儿童友好、互动性强的景点)
A_family = np.array([
    [1,   3,   1,   3,   3],    # C1喜好度
    [1/3, 1,   1/3, 1,   1],    # C2耗时灵活性
    [1,   3,   1,   3,   3],    # C3通勤便利性 (带孩子交通要方便)
    [1/3, 1,   1/3, 1,   1],    # C4抗拥堵能力
    [1/3, 1,   1/3, 1,   1],    # C5整体舒适度
])

# 场景D: 均衡偏好 (各方面均衡考虑)
A_balanced = np.array([
    [1,   2,   3,   2,   1],    # C1喜好度
    [1/2, 1,   2,   1,   1/2],  # C2耗时灵活性
    [1/3, 1/2, 1,   1/2, 1/3],  # C3通勤便利性
    [1/2, 1,   2,   1,   1/2],  # C4抗拥堵能力
    [1,   2,   3,   2,   1],    # C5整体舒适度
])

# ========== AHP 计算函数 ==========

def ahp_weights(matrix):
    """计算AHP权重（特征值法）"""
    n = matrix.shape[0]
    # 计算特征值和特征向量
    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    # 取最大特征值对应的特征向量
    max_idx = np.argmax(eigenvalues.real)
    max_eigenvalue = eigenvalues[max_idx].real
    weights = eigenvectors[:, max_idx].real
    # 归一化
    weights = weights / weights.sum()
    
    # 一致性检验
    CI = (max_eigenvalue - n) / (n - 1)
    # RI 表 (1-15阶)
    RI_table = {1:0, 2:0, 3:0.58, 4:0.90, 5:1.12, 6:1.24, 7:1.32, 8:1.41, 9:1.45, 10:1.49}
    RI = RI_table.get(n, 1.49)
    CR = CI / RI if RI != 0 else 0
    
    return weights, max_eigenvalue, CI, CR

# ========== 景点评分矩阵 (原始数据) ==========
# 行: A1~A10景点, 列: C1~C5指标
# 数据来源: 题目给定的各指标评分

scores = np.array([
    # C1喜好度  C2耗时灵活性  C3通勤便利性  C4抗拥堵能力  C5整体舒适度
    [9,         8,            9,            7,            9],   # A1 古城老街
    [7,         6,            7,            5,            7],   # A2 海洋乐园
    [8,         9,            8,            8,            8],   # A3 滨海浴场
    [4,         7,            5,            6,            5],   # A4 森林公园
    [6,         7,            6,            6,            7],   # A5 民俗古村
    [3,         5,            4,            5,            4],   # A6 山野溪谷
    [6,         8,            7,            7,            7],   # A7 环湖湿地
    [8,         7,            8,            7,            8],   # A8 亲子农庄
    [5,         6,            5,            5,            6],   # A9 山地观景台
    [8,         8,            8,            7,            8],   # A10 文创小镇
])

attraction_names = [
    "A1 古城老街", "A2 海洋乐园", "A3 滨海浴场", "A4 森林公园",
    "A5 民俗古村", "A6 山野溪谷", "A7 环湖湿地", "A8 亲子农庄",
    "A9 山地观景台", "A10 文创小镇"
]

criteria_names = ["喜好度C1", "耗时灵活性C2", "通勤便利性C3", "抗拥堵能力C4", "整体舒适度C5"]

# ========== TOPSIS 计算 ==========

def topsis_rank(scores, weights):
    """TOPSIS排序"""
    # 极差标准化
    min_vals = scores.min(axis=0)
    max_vals = scores.max(axis=0)
    normed = (scores - min_vals) / (max_vals - min_vals)
    
    # 加权
    weighted = normed * weights
    
    # 正负理想解
    ideal_pos = weighted.max(axis=0)
    ideal_neg = weighted.min(axis=0)
    
    # 距离
    d_pos = np.sqrt(((weighted - ideal_pos)**2).sum(axis=1))
    d_neg = np.sqrt(((weighted - ideal_neg)**2).sum(axis=1))
    
    # 贴近度
    S = d_neg / (d_pos + d_neg)
    return S, normed, weighted

# ========== 主程序 ==========

scenarios = {
    "A 人文偏好": A_humanity,
    "B 自然偏好": A_nature,
    "C 亲子偏好": A_family,
    "D 均衡偏好": A_balanced,
}

print("=" * 80)
print("AHP-TOPSIS 多偏好分析")
print("=" * 80)

for name, matrix in scenarios.items():
    print(f"\n{'='*60}")
    print(f"场景 {name}")
    print(f"{'='*60}")
    
    # AHP权重
    weights, lambda_max, CI, CR = ahp_weights(matrix)
    
    print(f"\nAHP权重:")
    for i, w in enumerate(weights):
        print(f"  {criteria_names[i]}: {w:.4f}")
    print(f"  λ_max = {lambda_max:.4f}, CI = {CI:.4f}, CR = {CR:.4f} {'✓通过' if CR < 0.1 else '✗不通过'}")
    
    # TOPSIS排序
    S, normed, weighted = topsis_rank(scores, weights)
    
    # 排序结果
    ranking = np.argsort(-S)
    print(f"\nTOPSIS排序:")
    for rank, idx in enumerate(ranking, 1):
        level = "高" if S[idx] > 0.6 else ("中" if S[idx] > 0.4 else "低")
        print(f"  {rank}. {attraction_names[idx]:12s}  S = {S[idx]:.4f}  [{level}优先级]")

print("\n" + "=" * 80)
print("四种偏好的权重对比")
print("=" * 80)
print(f"{'指标':<12s}", end="")
for name in scenarios:
    print(f"  {name:<12s}", end="")
print()
for i, c in enumerate(criteria_names):
    print(f"{c:<12s}", end="")
    for name, matrix in scenarios.items():
        weights, _, _, _ = ahp_weights(matrix)
        print(f"  {weights[i]:.4f}      ", end="")
    print()

