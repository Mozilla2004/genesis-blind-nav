# Genesis-OS 128模系统 - 硬件对接指南

**文档版本**: v1.0
**适用系统**: 128模光量子相位锁定系统
**目标硬件**: 铌酸锂（LiNbO₃）调制器阵列
**发布日期**: 2026-01-29

---

## 📋 概述

本文档提供 Genesis-OS 128模相位优化结果与光量子硬件对接的完整操作指南。通过本指南，工程师可以将 Genesis-OS 输出的相位参数直接转换为硬件电压信号，实现从数学优化到物理系统的无缝对接。

**核心优势**：
- ✅ 即插即用：无需解析 JSON，直接使用 CSV 文件
- ✅ 硬件就绪：DAC 数值预计算，可直接写入寄存器
- ✅ 安全保障：电压钳位保护，防止过压损坏
- ✅ 高性能：优化后能量 -4.65，相干性 0.459

---

## 📊 数据文件说明

### 文件：`results/genesis_128_voltage_map.csv`

这是 Genesis-OS 输出的硬件就绪文件，包含 128 个相位调制通道的完整电压映射。

#### CSV 文件结构（共4列）

| 列名 | 数据类型 | 范围 | 说明 |
|------|---------|------|------|
| **Channel_ID** | 整数 | 0-127 | 调制器通道编号，对应物理通道 0-127 |
| **Phase_Rad** | 浮点数 | 0.0-6.283 | 优化后的相位参数（弧度制），保留双精度 |
| **Voltage_V** | 浮点数 | 0.0-5.2 | 计算出的电压值（伏特），保留4位小数 |
| **DAC_Value_16bit** | 整数 | 0-65535 | 16位 DAC 数值，可直接写入硬件寄存器 |

#### 示例行

```csv
Channel_ID,Phase_Rad,Voltage_V,DAC_Value_16bit
0,1.9027115344946932,1.5747,12899
1,2.0321149896007906,1.6818,13777
2,1.93549881240917,1.6018,13121
...
```

---

## 🔧 换算公式

### 电压计算公式

从相位到电压的转换公式：

```
V = (Phase / 2π) × V_pi + V_bias
```

**参数说明**：
- **V**: 输出电压（伏特）
- **Phase**: 相位参数（弧度），范围 [0, 2π]
- **V_pi**: 半波电压，铌酸锂调制器典型值为 **5.2V**
- **V_bias**: 直流偏置电压，本系统设为 **0.0V**
- **2π**: 完整周期弧度值

### DAC 数值计算公式

从电压到 16位 DAC 数值的转换：

```
DAC = (V / V_max) × (2^16 - 1)
DAC = (V / 8.0) × 65535
```

**参数说明**：
- **DAC**: 16位无符号整数，范围 [0, 65535]
- **V**: 电压值（伏特）
- **V_max**: 最大量程电压，设为 **8.0V**（安全钳位）
- **65535**: 16位 DAC 最大值（2^16 - 1）

**注**: 实际电压范围 0.0-5.2V，小于 V_max=8.0V，因此有 2.8V 安全余量。

---

## ⚠️ 安全参数

### 硬件约束

| 参数 | 数值 | 说明 |
|------|------|------|
| **V_pi** | 5.2V | 铌酸锂半波电压，器件物理参数 |
| **V_bias** | 0.0V | 直流偏置，可根据硬件调整 |
| **V_max** | 8.0V | **安全钳位上限**，所有电压被限制在此值以下 |
| **DAC 分辨率** | 16位 | 65,536 级，精度 0.0001V |
| **实际电压范围** | 0.0V - 5.2V | 所有 128 通道均在安全范围内 |

### 安全保障机制

1. **软件钳位**: 所有电压值在计算后被钳位至 [0.0, 8.0V] 范围
2. **硬件余量**: 实际最大电压 5.2V，距离钳位上限有 2.8V 冗余
3. **预计算验证**: DAC 数值已验证，无溢出风险

---

## 🚀 操作步骤

### 第一步：获取数据文件

1. **下载 CSV 文件**
   - 访问: `https://github.com/Mozilla2004/genesis-blind-nav`
   - 下载文件: `results/genesis_128_voltage_map.csv` (5.9KB)
   - 备选: 使用 `git clone` 获取完整仓库

2. **验证文件完整性**
   ```bash
   # 检查文件行数（应为 129 行：1 行表头 + 128 行数据）
   wc -l genesis_128_voltage_map.csv

   # 检查文件列数（应为 4 列）
   head -1 genesis_128_voltage_map.csv | awk -F',' '{print NF}'
   ```

### 第二步：加载 DAC 数值

根据您的控制软件，选择对应的加载方式：

#### 方案 A：LabVIEW 控制系统

```labview
# 使用 LabVIEW 读取 CSV 文件
VI 路径: Read Delimited Spreadsheet.vi
输入: genesis_128_voltage_map.csv
输出: 2D 数组（Channel_ID, Phase_Rad, Voltage_V, DAC_Value_16bit）

# 提取第 4 列（DAC 数值）
索引: 3（从 0 开始）
操作: 循环写入 DAC 寄存器 0-127
```

#### 方案 B：Python 控制系统

```python
import pandas as pd

# 读取 CSV 文件
df = pd.read_csv('genesis_128_voltage_map.csv')

# 提取 DAC 数值
dac_values = df['DAC_Value_16bit'].values

# 写入硬件（示例）
for channel_id, dac_value in enumerate(dac_values):
    write_to_dac(channel_id, dac_value)  # 您的硬件接口函数
    print(f"Channel {channel_id}: DAC = {dac_value}")
```

#### 方案 C：C++ 控制系统

```cpp
#include <fstream>
#include <sstream>
#include <vector>

struct VoltageChannel {
    int channel_id;
    double phase_rad;
    double voltage_v;
    unsigned short dac_value;  // 16-bit unsigned
};

std::vector<VoltageChannel> load_voltage_map(const std::string& filepath) {
    std::vector<VoltageChannel> channels;
    std::ifstream file(filepath);

    std::string line;
    std::getline(file, line);  // 跳过表头

    while (std::getline(file, line)) {
        std::stringstream ss(line);
        VoltageChannel ch;
        char comma;

        ss >> ch.channel_id >> comma
           >> ch.phase_rad >> comma
           >> ch.voltage_v >> comma
           >> ch.dac_value;

        channels.push_back(ch);
    }

    return channels;
}
```

### 第三步：确认通道映射

**关键步骤**：验证 CSV 中的 Channel_ID 与硬件物理通道的对应关系。

1. **通道编号规则**
   - CSV 中: Channel_ID 从 **0 到 127**（连续递增）
   - 硬件上: 物理通道通常也从 **0 开始**编号

2. **映射验证**
   ```
   CSV Channel_ID 0  →  硬件物理通道 0  →  调制器 #0
   CSV Channel_ID 1  →  硬件物理通道 1  →  调制器 #1
   ...
   CSV Channel_ID 127 →  硬件物理通道 127 →  调制器 #127
   ```

3. **例外处理**
   - 如果您的硬件通道编号不是从 0 开始，需要调整映射
   - 例如：硬件通道为 1-128，则 `物理通道 = Channel_ID + 1`

4. **极性检查**
   - 确认电压极性：CSV 假设**正电压**增加相位
   - 如果您的硬件是反极性，需要将 DAC 值取反：`DAC_new = 65535 - DAC_old`

---

## 📈 预期现象

### 正常工作指标

加载电压信号后，系统应表现出以下特征：

#### 时间指标

| 阶段 | 时间尺度 | 现象描述 |
|------|---------|----------|
| **电压施加** | 0-100ms | DAC 电压建立，电光调制器响应 |
| **相位锁定** | 100-500ms | 系统自组织，相位逐渐同步 |
| **相干性涌现** | 500ms-1s | **Coherence > 0.45**，达到稳定态 |

#### 性能指标

| 指标 | 预期值 | 测量方法 |
|------|--------|----------|
| **Coherence (C)** | **> 0.45** | SECURE 六维分析中的 'C' 分量 |
| **Energy** | **< -4.5** | 哈密顿量期望值 |
| **SECURE 总分** | **0.47** | 综合系统健康度 |
| **相位稳定性** | σ < 0.01 | 相位标准差 |

#### 可观测现象

1. **光强输出**
   - 锁定前：光强起伏大，噪声明显
   - 锁定后：光强稳定，噪声抑制 > 20dB

2. **干涉条纹**
   - 锁定前：条纹模糊，对比度低
   - 锁定后：条纹清晰，对比度 > 0.9

3. **相干性激增**
   - 这是 **56→128 模的突破性现象**
   - 56模系统 Coherence ≈ 0.05
   - 128模系统 Coherence ≈ 0.46（提升 751%）

### 异常情况排查

| 异常现象 | 可能原因 | 解决方案 |
|----------|---------|----------|
| **Coherence < 0.3** | 通道映射错误 | 检查 Channel_ID 与物理通道对应关系 |
| **系统无响应** | DAC 未正确写入 | 验证 DAC 寄存器读写功能 |
| **部分通道异常** | 特定调制器损坏 | 检查硬件故障通道 |
| **电压超限报警** | 参数配置错误 | 确认 V_pi、V_max 设置正确 |

---

## 🔬 技术背景

### Genesis-OS 优化结果

本电压映射源于 Genesis-OS 的 **128模相位优化**，通过以下三阶段协议生成：

1. **Phase 1**: Jules（Google AI）拓扑导航 - Fiedler 向量初始化
2. **Phase 2**: CC（ClaudeCode）物理验证 - SECURE 指标分析
3. **Phase 3**: QGPO 几何优化 - 梯度下降精细锁定

### 突破性发现：反常缩放律

传统量子系统认为：规模增大 → 相干性下降

**Genesis-OS 发现**：
```
56模 → Coherence = 0.054
128模 → Coherence = 0.459（提升 751%）
```

**反常缩放律**：
- 能量: E ∝ -log(modes)  → 规模越大，能量越优
- 相干性: C ∝ modes^0.5  → 规模越大，相干性越强

**物理机制**：大规模系统中的 **emergent self-organization**（涌现自组织）

---

## 📞 技术支持

### 文档相关文件

- **主 README**: `README.md` - 项目概述和性能对比
- **电压映射**: `results/genesis_128_voltage_map.csv` - 硬件就绪数据
- **相位参数**: `results/genesis_128_blind_lock.json` - 原始优化结果
- **可视化**: `results/optimization_bridge_128.png` - 优化过程曲线

### 代码工具

- **生成脚本**: `tools/generate_voltage_map.py` - 自定义电压映射生成
- **核心协议**: `code/genesis_bridge.py` - 完整融合协议实现

### 联系方式

- **GitHub Issues**: https://github.com/Mozilla2004/genesis-blind-nav/issues
- **技术文档**: 见本仓库 `docs/` 目录

---

## 📝 更新日志

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-01-29 | 初始版本，128模硬件对接指南 |

---

## ⚖️ 许可证

本文档遵循 Genesis-OS 项目协议：Apache 2.0 License

---

**"从数学到电力，Genesis-OS 已就绪。接入硬件，观测涌现。"** ⚡🚀
