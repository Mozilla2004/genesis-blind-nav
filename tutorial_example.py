#!/usr/bin/env python3
"""
Genesis-Kernel 实战教程：量子优化 Max-Cut 问题
作者：Genesis Research
日期：2026-01-28
"""

import numpy as np
import matplotlib.pyplot as plt
from genesis_kernel.templates.optimization import QuantumOptimizationActivator

# ============================================
# 步骤 1：定义问题（Max-Cut）
# ============================================

def create_maxcut_hamiltonian(adj_matrix):
    """
    创建 Max-Cut 问题的哈密顿量

    参数：
        adj_matrix: 邻接矩阵 (n x n)

    返回：
        H: 问题哈密顿量 (2^n x 2^n)
    """
    n = adj_matrix.shape[0]
    dim = 2**n
    H = np.zeros((dim, dim))

    # Pauli Z 矩阵
    Z = np.array([[1, 0], [0, -1]])

    # Max-Cut 哈密顿量: H = -Σ_{i,j} J_{ij} * (1 - σ_z^i ⊗ σ_z^j) / 2
    for i in range(n):
        for j in range(i+1, n):
            if adj_matrix[i, j] > 0:
                # 构建 σ_z^i ⊗ σ_z^j
                op_list = [np.eye(2)] * n
                op_list[i] = Z
                op_list[j] = Z

                # 计算 Kronecker 积
                zz_op = op_list[0]
                for op in op_list[1:]:
                    zz_op = np.kron(zz_op, op)

                H -= adj_matrix[i, j] * (np.eye(dim) - zz_op) / 2

    return H

# ============================================
# 步骤 2：准备问题实例
# ============================================

# 示例：4个节点的图
print("="*60)
print("📊 Max-Cut 问题示例")
print("="*60)

# 邻接矩阵
adjacency = np.array([
    [0, 1, 1, 0],
    [1, 0, 1, 1],
    [1, 1, 0, 1],
    [0, 1, 1, 0]
])

print("\n图结构（邻接矩阵）:")
print(adjacency)

# 创建问题哈密顿量
H_problem = create_maxcut_hamiltonian(adjacency)
print(f"\n问题维度: {H_problem.shape[0]}x{H_problem.shape[0]}")

# 计算理论最小能量（精确对角化）
eigenvalues = np.linalg.eigvalsh(H_problem)
exact_ground_energy = eigenvalues[0]
print(f"理论基态能量: {exact_ground_energy:.4f}")

# ============================================
# 步骤 3：激活量子优化
# ============================================

print("\n" + "="*60)
print("🌀 启动 Genesis-AI 量子优化")
print("="*60)

# 创建激活器
activator = QuantumOptimizationActivator(
    problem_hamiltonian=H_problem,
    num_qubits=4
)

# 设置已知最优值（用于评估）
activator.known_optimum = exact_ground_energy
activator.target_energy = exact_ground_energy

# 运行激活协议
final_result, report = activator.activate(
    target_energy=exact_ground_energy,
    max_iterations=50
)

# ============================================
# 步骤 4：分析结果
# ============================================

print("\n" + "="*60)
print("📈 优化结果分析")
print("="*60)

print(f"\n最优解: {final_result['solution']}")
print(f"最优能量: {final_result['energy']:.4f}")
print(f"理论最优: {exact_ground_energy:.4f}")
print(f"近似比: {final_result['energy']/exact_ground_energy:.4f}")

# 绘制演化轨迹
if len(activator.evolution_log) > 0:
    iterations = [log['iteration'] for log in activator.evolution_log]
    energies = [log['energy'] for log in activator.evolution_log]
    superposition = [log['secure']['S'] for log in activator.evolution_log]
    entanglement = [log['secure']['E'] for log in activator.evolution_log]
    coherence = [log['secure']['C'] for log in activator.evolution_log]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # 能量收敛
    axes[0].plot(iterations, energies, 'b-', linewidth=2, label='能量')
    axes[0].axhline(y=exact_ground_energy, color='r', linestyle='--', label='理论最优')
    axes[0].set_xlabel('迭代次数')
    axes[0].set_ylabel('能量')
    axes[0].set_title('能量收敛曲线')
    axes[0].legend()
    axes[0].grid(True)

    # SECURE 指标
    axes[1].plot(iterations, superposition, 'g-', label='叠加度 (S)')
    axes[1].plot(iterations, entanglement, 'b-', label='纠缠度 (E)')
    axes[1].plot(iterations, coherence, 'r-', label='相干性 (C)')
    axes[1].set_xlabel('迭代次数')
    axes[1].set_ylabel('指标值')
    axes[1].set_title('SECURE 指标演化')
    axes[1].legend()
    axes[1].grid(True)
    axes[1].set_ylim([0, 1])

    plt.tight_layout()
    plt.savefig('genesis_kernel_optimization_results.png', dpi=150)
    print(f"\n✓ 结果图表已保存: genesis_kernel_optimization_results.png")

# ============================================
# 步骤 5：与经典算法对比
# ============================================

print("\n" + "="*60)
print("⚖️ 与经典算法对比")
print("="*60)

# 贪心算法
def greedy_maxcut(adj_matrix):
    """简单的贪心算法"""
    n = adj_matrix.shape[0]
    cut = np.zeros(n, dtype=int)

    for i in range(n):
        # 计算放在哪一侧收益更大
        gain_0 = np.sum(adj_matrix[i, cut == 1])
        gain_1 = np.sum(adj_matrix[i, cut == 0])
        cut[i] = 1 if gain_1 > gain_0 else 0

    # 计算 cut 值
    cut_value = 0
    for i in range(n):
        for j in range(i+1, n):
            if cut[i] != cut[j]:
                cut_value += adj_matrix[i, j]

    return cut, cut_value

classic_cut, classic_value = greedy_maxcut(adjacency)
print(f"\n经典贪心算法解: {classic_cut}")
print(f"经典算法 cut 值: {classic_value}")
print(f"量子算法解: {final_result['solution']}")

# 将量子解转换为 cut
quantum_cut = np.array([int(b) for b in final_result['solution']])
quantum_value = 0
for i in range(4):
    for j in range(i+1, 4):
        if quantum_cut[i] != quantum_cut[j]:
            quantum_value += adjacency[i, j]

print(f"量子算法 cut 值: {quantum_value}")
print(f"改进: {(quantum_value - classic_value) / classic_value * 100:.1f}%")

print("\n" + "="*60)
print("🎉 教程完成！")
print("="*60)
print("\n你已学会：")
print("  ✓ 定义量子优化问题")
print("  ✓ 创建问题哈密顿量")
print("  ✓ 使用 Genesis-AI 激活协议")
print("  ✓ 分析 SECURE 指标")
print("  ✓ 与经典算法对比")
print("\n下一步：尝试你自己的优化问题！")
