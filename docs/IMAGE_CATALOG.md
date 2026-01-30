# Genesis-OS Image Catalog

**文档版本**: v1.0
**更新日期**: 2026-01-30
**用途**: 图片文件说明与索引

---

## 📊 Results 目录图片索引

### **1. optimization_bridge_56.png** ✅ Standardized

- **尺寸**: 2953 x 1749 px (187.6 KB)
- **格式**: PNG RGBA, 300 DPI
- **生成时间**: 2026-01-30 19:20
- **生成工具**: `tools/refresh_plots.py`
- **数据源**: `results/genesis_56_blind_lock.json`
- **内容**: 56-photon active phase locking convergence curve
- **术语**:
  - Title: "Genesis-OS: 56-Photon Active Phase Locking Convergence"
  - Legend: Topological Init (Spectral), Gradient Optimized
  - Y-Axis: System Hamiltonian

---

### **2. optimization_bridge_128.png** ✅ Standardized

- **尺寸**: 2953 x 1749 px (186.5 KB)
- **格式**: PNG RGBA, 300 DPI
- **生成时间**: 2026-01-30 19:20
- **生成工具**: `tools/refresh_plots.py`
- **数据源**: `results/genesis_128_blind_lock.json`
- **内容**: 128-photon active phase locking convergence curve
- **注意**: JSON 文件内部标记为 56 光子（数据文件问题）

---

### **3. optimization_bridge_256.png** ✅ Standardized

- **尺寸**: 2953 x 1749 px (193.1 KB)
- **格式**: PNG RGBA, 300 DPI
- **生成时间**: 2026-01-30 19:20
- **生成工具**: `tools/refresh_plots.py`
- **数据源**: `results/genesis_256_blind_lock.json`
- **内容**: 256-photon active phase locking convergence curve
- **突破**: Coherence 0.702 (+1,202% improvement)

---

### **4. simple_tutorial_results.png** ⚠️ Legacy

- **尺寸**: 1500 x 900 px (48 KB)
- **格式**: PNG RGBA
- **首次提交**: d958b92 (2026-01-29)
- **来源**: Genesis-Kernel simple tutorial
- **状态**: 包含中文字符，待英文化
- **用途**: 6-mode demonstration visualization

---

### **5. locking_trace.png** ⚠️ Legacy

- **尺寸**: 1781 x 1480 px (114 KB)
- **格式**: PNG RGBA
- **首次提交**: d958b92 (2026-01-29)
- **来源**: Phase locking demonstration
- **状态**: 包含中文字符，待英文化
- **用途**: Locking process trace visualization

---

## 🛠️ 图片生成工具

### **tools/refresh_plots.py** (Recommended)

**功能**: 批量生成标准化图表

**用法**:
```bash
python3 tools/refresh_plots.py
```

**特性**:
- ✅ 自动读取 JSON 数据
- ✅ 统一术语标准
- ✅ 标准化配色方案
- ✅ 高分辨率输出 (300 DPI)
- ✅ 英文标签（无中文）

**输出**:
- `optimization_bridge_56.png`
- `optimization_bridge_128.png`
- `optimization_bridge_256.png`

---

## 📋 图片标准化检查清单

- [x] optimization_bridge_56.png - ✅ 已标准化（英文）
- [x] optimization_bridge_128.png - ✅ 已标准化（英文）
- [x] optimization_bridge_256.png - ✅ 已标准化（英文）
- [ ] simple_tutorial_results.png - ⚠️ 待英文化
- [ ] locking_trace.png - ⚠️ 待英文化

---

## 🎨 术语标准化对照表

| 中文（旧） | English (New) |
|-----------|---------------|
| 56模 | 56-Photon |
| 128模 | 128-Photon |
| 256模 | 256-Photon |
| 能量 | System Hamiltonian |
| 相干性 | Coherence |
| 相位锁定 | Phase Locking |
| 拓扑初始化 | Topological Init (Spectral) |
| 梯度优化 | Gradient Optimized |
| 系统哈密顿量 | System Hamiltonian |

---

## 🔄 更新历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2026-01-30 | v1.0 | 初始版本，记录所有图片信息 |

---

**维护说明**:
- 当生成新图片时，请更新此文档
- 确保所有图片符合标准化术语规范
- 优先使用英文标签，避免中文字符
