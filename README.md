# thermo-cycle-analyzer

一个 Claude Code Skill，用于热力循环的计算分析与可视化。

## 功能

- 支持多种热力循环：朗肯循环 (Rankine)、布雷顿循环 (Brayton)、卡诺循环 (Carnot)、联合循环 (Combined Cycle)
- 支持变体：再热、回热等
- 自动计算所有状态点参数（温度、压力、比焓、比熵、干度）
- 计算循环性能指标（热效率、净功、吸热量、放热量、背功比）
- 生成 Nature 论文级别的 T-s 图 / P-v 图（Python + matplotlib）
- 输出结构化分析报告

## 安装

将 `thermo-cycle-analyzer.skill` 文件导入 Claude Code 即可使用。

或者手动安装：将 `SKILL.md` 放入 `~/.claude/skills/thermo-cycle-analyzer/` 目录。

## 使用示例

用自然语言描述工况参数即可：

```
帮我分析一个朗肯循环：锅炉压力 10MPa，汽轮机入口温度 500°C，冷凝器压力 10kPa
```

```
分析一个燃气轮机循环：压气机入口 300K，增压比 12，燃气轮机入口 1400K
```

```
联合循环分析：燃气轮机入口 1400K，增压比 15，余热锅炉产生 5MPa/400°C 蒸汽，冷凝器 10kPa
```

## 依赖

生成图表需要 Python 环境，脚本会自动调用以下库：

- matplotlib
- numpy
- CoolProp（用于水蒸气真实物性，如未安装脚本会给出提示）

## 图表风格

图表严格遵循 Nature 期刊出版标准：

- 图宽 89mm（单栏）/ 183mm（双栏）
- Helvetica 字体，5–7 pt
- 300 DPI，同时输出 PDF（矢量）和 PNG
- 去除上、右边框，刻度向内
- Nature 推荐配色，色盲友好
- 无网格线，无图例框，极简设计

## License

MIT
