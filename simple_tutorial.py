#!/usr/bin/env python3
"""
Genesis-Kernel 简化教程：量子优化 Max-Cut 问题
不需要 scipy，纯 numpy 实现
"""

import numpy as np
import matplotlib.pyplot as plt

# ============================================
# 简化的量子优化激活器
# ============================================

class SimpleQuantumOptimizer:
    """简化的量子优化器（教程版）"""

    def __init__(self, problem_hamiltonian, num_qubits):
        self.H_problem = problem_hamiltonian
        self.n_qubits = num_qubits
        self.dim = 2 ** num_qubits
        self.evolution_log = []

        # SECURE 指标
        self.secure_state = {
            'S': 0,  # Superposition
            'E': 0,  # Entanglement
            'C': 0,  # Coherence
            'U': 0,  # Uncertainty
            'R': 0,  # Resilience
            'E2': 0  # Evolution stability
        }

    def matrix_exp(self, H, t):
        """简化的矩阵指数（使用 Taylor 展开）"""
        # 简单的 Taylor 展开: exp(-iHt) ≈ I - iHt - (Ht)²/2 + ...
        result = np.eye(H.shape[0], dtype=complex)
        term = np.eye(H.shape[0], dtype=complex)

        for n in range(1, 10):  # 10项近似
            term = term @ (-1j * H * t / n)
            result += term

        return result

    def activate(self, target_energy, max_iterations=50):
        """主激活流程"""
        print("="*60)
        print("🌀 简化版 Genesis-AI 量子优化")
        print("="*60)

        # 阶段1：初始化
        print("\n[阶段1] 态制备...")
        state = self._initialize_state()
        self._update_secure('S', state)

        # 阶段2：优化迭代
        print("\n[阶段2] 优化迭代...")
        for iteration in range(max_iterations):
            # 测量当前能量
            current_energy = self._measure_energy(state)

            # 记录日志
            self.evolution_log.append({
                'iteration': iteration,
                'state': state.copy(),
                'energy': current_energy,
                'secure': self.secure_state.copy()
            })

            # 打印进度
            if iteration % 10 == 0:
                print(f"  迭代 {iteration:3d} | 能量: {current_energy:8.4f} | "
                      f"目标: {target_energy:8.4f} | 能隙: {abs(current_energy - target_energy):8.4f}")

            # 收敛检查
            if abs(current_energy - target_energy) < 0.01:
                print(f"\n✓ 在第 {iteration} 次迭代收敛!")
                break

            # 演化一步
            state = self._evolution_step(state, target_energy)

        # 阶段3：测量
        print("\n[阶段3] 测量结果...")
        final_result = self._measure(state)

        # 阶段4：报告
        print("\n[阶段4] 生成报告...")
        report = self._generate_report(final_result, target_energy)

        return final_result, report

    def _initialize_state(self):
        """初始化均匀叠加态"""
        state_vector = np.ones(self.dim) / np.sqrt(self.dim)
        rho = np.outer(state_vector, state_vector.conj())

        # 计算参与比
        PR = 1 / np.sum(np.abs(state_vector)**4)
        print(f"  → 均匀叠加态: {self.dim} 个基态")
        print(f"  → 参与比: {PR:.2f}")

        return rho

    def _evolution_step(self, state, target_energy):
        """演化单步"""
        # 自适应参数
        current_energy = self._measure_energy(state)
        energy_gap = abs(current_energy - target_energy)

        if energy_gap > 1.0:
            dt = 0.1
        elif energy_gap > 0.1:
            dt = 0.05
        else:
            dt = 0.02

        # 构造驱动哈密顿量（简化版）
        H_driver = self._construct_driver_hamiltonian()

        # 混合哈密顿量
        alpha = 0.5  # 混合参数
        H_total = alpha * H_driver + (1 - alpha) * self.H_problem

        # 幺正演化
        U = self.matrix_exp(H_total, dt)
        new_state = U @ state @ U.conj().T

        # 更新 SECURE 指标
        self._update_all_secure(new_state)

        return new_state

    def _construct_driver_hamiltonian(self):
        """构造驱动哈密顿量（Pauli X 求和）"""
        X = np.array([[0, 1], [1, 0]])
        H_driver = np.zeros((self.dim, self.dim), dtype=complex)

        for i in range(self.n_qubits):
            op_list = [np.eye(2)] * self.n_qubits
            op_list[i] = X

            X_op = op_list[0]
            for op in op_list[1:]:
                X_op = np.kron(X_op, op)

            H_driver += X_op

        return H_driver

    def _measure(self, state):
        """测量（简化版）"""
        # 计算概率分布
        probs = np.real(np.diag(state))

        # 找最大概率的基态
        max_idx = np.argmax(probs)
        solution = format(max_idx, f'0{self.n_qubits}b')
        energy = self._measure_energy(state)

        return {
            'solution': solution,
            'energy': energy,
            'probabilities': probs
        }

    def _measure_energy(self, state):
        """测量期望能量"""
        return np.real(np.trace(self.H_problem @ state))

    def _update_secure(self, dimension, state):
        """更新单个 SECURE 维度"""
        if dimension == 'S':
            # Superposition: 参与比
            eigenvalues = np.linalg.eigvalsh(state)
            eigenvalues = eigenvalues[eigenvalues > 1e-10]
            PR = 1 / np.sum(eigenvalues**2)
            self.secure_state['S'] = PR / self.dim

        elif dimension == 'C':
            # Coherence: l1-norm
            rho_diag = np.diag(np.diag(state))
            self.secure_state['C'] = np.sum(np.abs(state - rho_diag))

        elif dimension == 'U':
            # Uncertainty: 能量方差
            energy = self._measure_energy(state)
            energy_sq = np.real(np.trace(self.H_problem @ self.H_problem @ state))
            variance = energy_sq - energy**2
            self.secure_state['U'] = np.sqrt(variance) if variance > 0 else 0

    def _update_all_secure(self, state):
        """更新所有 SECURE 维度"""
        for dim in ['S', 'C', 'U']:
            self._update_secure(dim, state)

        # E 和 R 使用简化值
        self.secure_state['E'] = 0.5
        self.secure_state['R'] = 0.8
        self.secure_state['E2'] = 0.7

    def _generate_report(self, result, target_energy):
        """生成报告"""
        print("\n" + "="*60)
        print("📊 优化报告")
        print("="*60)

        print(f"\n最优解: {result['solution']}")
        print(f"最优能量: {result['energy']:.4f}")
        print(f"目标能量: {target_energy:.4f}")
        print(f"误差: {abs(result['energy'] - target_energy):.4f}")

        print("\n🔒 SECURE 指标:")
        for dim, value in self.secure_state.items():
            print(f"  {dim}: {value:.3f}")

        print("\n⚡ 效率指标:")
        print(f"  总迭代: {len(self.evolution_log)}")

        return {
            'solution': result['solution'],
            'energy': result['energy'],
            'secure': self.secure_state
        }


# ============================================
# 主程序
# ============================================

def create_maxcut_hamiltonian(adj_matrix):
    """创建 Max-Cut 哈密顿量"""
    n = adj_matrix.shape[0]
    dim = 2**n
    H = np.zeros((dim, dim))

    Z = np.array([[1, 0], [0, -1]])

    for i in range(n):
        for j in range(i+1, n):
            if adj_matrix[i, j] > 0:
                op_list = [np.eye(2)] * n
                op_list[i] = Z
                op_list[j] = Z

                zz_op = op_list[0]
                for op in op_list[1:]:
                    zz_op = np.kron(zz_op, op)

                H -= adj_matrix[i, j] * (np.eye(dim) - zz_op) / 2

    return H


def main():
    print("="*60)
    print("📚 Genesis-Kernel 简化教程")
    print("="*60)

    # 问题定义
    adjacency = np.array([
        [0, 1, 1, 0],
        [1, 0, 1, 1],
        [1, 1, 0, 1],
        [0, 1, 1, 0]
    ])

    print("\n图结构:")
    print(adjacency)

    # 创建哈密顿量
    H_problem = create_maxcut_hamiltonian(adjacency)
    eigenvalues = np.linalg.eigvalsh(H_problem)
    exact_ground_energy = eigenvalues[0]

    print(f"\n理论基态能量: {exact_ground_energy:.4f}")

    # 优化
    optimizer = SimpleQuantumOptimizer(H_problem, num_qubits=4)
    result, report = optimizer.activate(target_energy=exact_ground_energy, max_iterations=100)

    # 绘图
    if len(optimizer.evolution_log) > 0:
        iterations = [log['iteration'] for log in optimizer.evolution_log]
        energies = [log['energy'] for log in optimizer.evolution_log]

        plt.figure(figsize=(10, 6))
        plt.plot(iterations, energies, 'b-', linewidth=2, label='能量')
        plt.axhline(y=exact_ground_energy, color='r', linestyle='--', label='理论最优')
        plt.xlabel('迭代次数', fontsize=12)
        plt.ylabel('能量', fontsize=12)
        plt.title('Genesis-AI 能量收敛曲线', fontsize=14)
        plt.legend()
        plt.grid(True)
        plt.savefig('simple_tutorial_results.png', dpi=150)
        print(f"\n✓ 图表已保存: simple_tutorial_results.png")

    print("\n" + "="*60)
    print("🎉 教程完成！")
    print("="*60)
    print("\n你已学会：")
    print("  ✓ 创建问题哈密顿量")
    print("  ✓ 初始化量子态")
    print("  ✓ 执行优化迭代")
    print("  ✓ 分析收敛过程")


if __name__ == "__main__":
    main()
