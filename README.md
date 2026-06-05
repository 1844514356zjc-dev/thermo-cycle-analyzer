<div align="center">

# Thermo Cycle Analyzer

**热力循环计算分析与可视化工具** — Claude Code Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![CoolProp](https://img.shields.io/badge/CoolProp-IAPWS--IF97-green.svg)](http://www.coolprop.org/)

基于真实工质物性的热力循环性能计算，自动生成 **Nature 论文级别** 的 T-s / P-v 状态图。

</div>

---

## 支持的循环类型

| 循环 | 英文 | 描述 | 示例 |
|:-----|:-----|:-----|:-----|
| 朗肯循环 | Rankine Cycle | 基本蒸汽动力循环 | [再热朗肯 T-s 图](examples/rankine-reheat/rankine_reheat_ts.png) |
| 布雷顿循环 | Brayton Cycle | 燃气轮机循环 | [回热布雷顿 T-s 图](examples/brayton-regenerative/brayton_regenerative_Ts.png) |
| 卡诺循环 | Carnot Cycle | 理想热力学循环 | — |
| 联合循环 | Combined Cycle | 燃气-蒸汽联合循环 | [联合循环 T-s 图](examples/combined-cycle/combined_cycle_Ts.png) |

每种循环均支持变体形式，包括再热 (Reheat)、回热 (Regenerative)、抽汽回热 (Feedwater Heating) 等。

## 核心功能

### 热力学计算

- **状态点参数求解**：温度 T、压力 P、比焓 h、比熵 s、干度 x
- **循环性能指标**：热效率 η、净功 w_net、吸热量 q_in、放热量 q_out、背功比 BWR
- **真实工质物性**：水/水蒸气侧调用 [CoolProp](http://www.coolprop.org/)（IAPWS-IF97 标准），燃气侧采用变比热容多项式拟合
- **智能参数补全**：未给定的参数自动采用工程常用值，并在报告中明确标注来源

### 可视化输出

图表严格遵循 **Nature 期刊出版规范**：

| 规范项 | 参数 |
|:-------|:-----|
| 图宽 | 89 mm（单栏）/ 183 mm（双栏） |
| 字体 | Helvetica / Arial，坐标轴标题 7 pt，刻度 5–6 pt |
| 线宽 | 坐标轴 0.5 pt，数据线 0.75–1.0 pt |
| 刻度 | 向内 (inward)，长度 2–3 pt |
| 边框 | 仅保留左侧和底部，去除上侧和右侧 |
| 配色 | Nature 推荐高对比度色板，色盲友好 |
| 输出 | PDF（矢量）+ PNG（300 DPI）同步生成 |

### 结构化报告

自动输出包含五个部分的完整分析报告：输入参数 → 假设条件 → 状态点参数表 → 循环性能指标 → 分析与讨论。

## 安装

### 方式一：导入 .skill 文件（推荐）

下载 [thermo-cycle-analyzer.skill](thermo-cycle-analyzer.skill) 文件，在 Claude Code 中导入即可。

### 方式二：手动安装

```bash
mkdir -p ~/.claude/skills/thermo-cycle-analyzer
cp SKILL.md ~/.claude/skills/thermo-cycle-analyzer/
```

### 依赖

生成图表和物性计算需要以下 Python 库：

```bash
pip install matplotlib numpy CoolProp
```

> 如未安装 CoolProp，脚本仍可运行，水蒸气物性将退回近似公式计算。

## 使用方法

安装后在 Claude Code 中用自然语言描述工况即可触发：

**基本朗肯循环**
```
帮我分析一个朗肯循环：锅炉压力 10MPa，汽轮机入口温度 500°C，冷凝器压力 10kPa
```

**再热朗肯循环**
```
再热朗肯循环：锅炉压力 15MPa，初温 600°C，再热压力 3MPa，再热温度 600°C，冷凝器 10kPa
```

**回热布雷顿循环**
```
分析一个燃气轮机循环：压气机入口 300K，增压比 10，燃气轮机入口 1500K，带回热器，有效率 0.8
```

**联合循环**
```
联合循环分析：燃气轮机入口 1600K，增压比 20。余热锅炉产生 8MPa/520°C 蒸汽，冷凝器 8kPa
```

> 支持中英文混合输入和多种非标准术语（如"蒸汽机"、"烧水的"等）。

## 示例结果

### 再热朗肯循环（15 MPa / 600 °C / 再热 3 MPa / 600 °C）

| 状态点 | P (MPa) | T (°C) | h (kJ/kg) | s (kJ/(kg·K)) | x |
|:------:|:-------:|:------:|:---------:|:-------------:|:---:|
| 1 — 冷凝器出口 | 0.01 | 45.81 | 191.81 | 0.6492 | 0.00 |
| 2 — 泵出口 | 15.00 | 46.30 | 206.90 | 0.6492 | — |
| 3 — 锅炉出口 | 15.00 | 600.00 | 3583.13 | 6.6796 | — |
| 4 — 高压汽轮机出口 | 3.00 | 333.10 | 3075.90 | 6.6796 | 1.00 |
| 5 — 再热器出口 | 3.00 | 600.00 | 3682.83 | 7.5103 | — |
| 6 — 低压汽轮机出口 | 0.01 | 45.81 | 2380.19 | 7.5103 | 0.91 |

**热效率 45.06%** | 净功 1794.78 kJ/kg | 卡诺效率 63.47%

### 回热布雷顿循环（增压比 10 / 1500 K / ε = 0.8）

| 状态点 | T (K) | P (kPa) | 说明 |
|:------:|:-----:|:-------:|:-----|
| 1 | 300.00 | 101.33 | 压气机入口 |
| 2 | 579.21 | 1013.30 | 压气机出口 |
| 3 | 737.38 | 1013.30 | 回热器出口（高压侧） |
| 4 | 1500.00 | 1013.30 | 燃烧室出口 |
| 5 | 776.92 | 101.33 | 燃气轮机出口 |
| 6 | 618.75 | 101.33 | 回热器出口（低压侧） |

**热效率 58.20%**（无回热 48.21%，提升 +10 pp） | 净功 446.09 kJ/kg

### 联合循环（布雷顿 20 + 朗肯 8 MPa / 520 °C）

**联合循环热效率 61.54%**，达到同温限卡诺效率的 76.6%。

## 技术细节

- **水蒸气物性**：CoolProp / IAPWS-IF97 工业标准，覆盖亚临界至超临界工况
- **燃气物性**：理想气体近似，cp 采用温度多项式拟合
- **默认假设**：等熵效率 100%（理想循环），忽略动能和势能变化；用户可指定实际效率值
- **余热锅炉**：考虑节点温差 (Pinch Point) 约束，默认 20 K

## License

[MIT License](LICENSE)
