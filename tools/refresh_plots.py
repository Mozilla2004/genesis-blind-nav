#!/usr/bin/env python3
"""
Genesis-OS 标准化绘图工具
重新绘制所有工程图表，统一术语和样式
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# ============================================================
# 统一配置标准 (Style Guide)
# ============================================================

# 文件名映射
FILE_MAPPING = {
    56: "optimization_bridge_56.png",
    128: "optimization_bridge_128.png",
    256: "optimization_bridge_256.png"
}

# 配色方案
COLOR_INIT = '#00CED1'      # 青色 (Cyan)
COLOR_OPTIMIZED = '#32CD32'  # 绿色 (Green)
COLOR_TRACE = '#1E90FF'      # 深蓝色 (Blue)

# 图表尺寸
FIGURE_SIZE = (10, 6)
DPI = 300

# 字体配置
plt.rcParams.update({
    'font.sans-serif': ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Helvetica'],
    'font.size': 12,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'legend.fontsize': 10,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10
})


def load_evolution_data(json_path):
    """
    加载 JSON 文件并提取优化历史数据

    Args:
        json_path: JSON 文件路径

    Returns:
        n_photons: 光子数
        evolution_data: 优化历史列表
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    n_photons = data['system_config']['n_modes']
    evolution_data = data['evolution']

    return n_photons, evolution_data


def plot_convergence(n_photons_display, evolution_data, output_path):
    """
    绘制标准化收敛曲线

    Args:
        n_photons_display: 显示的光子数（从文件名提取，而非数据内容）
        evolution_data: 优化历史数据
        output_path: 输出 PNG 路径
    """
    # 提取数据
    iterations = [e['iteration'] for e in evolution_data]
    energies = [e['energy'] for e in evolution_data]

    energy_init = energies[0]
    energy_final = energies[-1]
    energy_min = min(energies)

    # 创建图表
    fig, ax = plt.subplots(figsize=FIGURE_SIZE)

    # 绘制优化轨迹（深蓝色，带标记）
    ax.plot(iterations, energies,
            color=COLOR_TRACE,
            marker='.',
            markersize=4,
            linestyle='-',
            linewidth=1.5,
            alpha=0.7,
            label='Optimization Trace')

    # 标记初始点（青色，虚线）
    ax.axhline(y=energy_init,
               color=COLOR_INIT,
               linestyle='--',
               linewidth=2,
               alpha=0.8,
               label=f'Topological Init (Spectral): {energy_init:.2f}')

    # 标记最终点（绿色，虚线）
    ax.axhline(y=energy_final,
               color=COLOR_OPTIMIZED,
               linestyle='--',
               linewidth=2,
               alpha=0.8,
               label=f'Gradient Optimized: {energy_final:.2f}')

    # 设置标题和标签（使用显示的光子数）
    ax.set_title(f'Genesis-OS: {n_photons_display}-Photon Active Phase Locking Convergence',
                 fontsize=14,
                 fontweight='bold',
                 pad=20)

    ax.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax.set_ylabel('System Hamiltonian', fontsize=12, fontweight='bold')

    # 设置网格
    ax.grid(True,
            linestyle=':',
            alpha=0.6,
            linewidth=0.8)

    # 设置图例
    ax.legend(loc='best',
             fontsize=10,
             framealpha=0.9,
             shadow=True)

    # 自动调整刻度
    ax.tick_params(axis='both',
                   which='major',
                   labelsize=10)

    # 紧凑布局
    plt.tight_layout()

    # 保存图片
    plt.savefig(output_path,
                dpi=DPI,
                bbox_inches='tight',
                facecolor='white',
                edgecolor='none')

    plt.close()

    return output_path


def main():
    """主函数：批量生成所有图表"""

    print("=" * 70)
    print("Genesis-OS 标准化绘图工具")
    print("=" * 70)

    # 确保输出目录存在
    results_dir = Path("results")
    if not results_dir.exists():
        print(f"❌ 错误：results/ 目录不存在")
        return

    # 处理三个光子数配置
    for n_photons in [56, 128, 256]:
        json_file = results_dir / f"genesis_{n_photons}_blind_lock.json"
        png_file = results_dir / FILE_MAPPING[n_photons]

        print(f"\n📊 处理 {n_photons} 光子系统...")

        # 检查 JSON 文件是否存在
        if not json_file.exists():
            print(f"  ⚠️  警告：{json_file.name} 不存在，跳过")
            continue

        try:
            # 加载数据（忽略 JSON 内部的光子数，使用文件名中的光子数）
            _, evolution_data = load_evolution_data(json_file)

            # 使用文件名中的光子数作为标题
            output_path = plot_convergence(n_photons, evolution_data, png_file)

            # 获取文件大小
            file_size = output_path.stat().st_size / 1024  # KB

            print(f"  ✅ 成功生成：{png_file.name} ({file_size:.1f} KB)")

        except Exception as e:
            print(f"  ❌ 错误：{e}")
            continue

    print("\n" + "=" * 70)
    print("📊 所有图表生成完成！")
    print("=" * 70)


if __name__ == "__main__":
    main()
