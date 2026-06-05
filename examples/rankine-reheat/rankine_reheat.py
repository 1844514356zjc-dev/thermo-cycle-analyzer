#!/usr/bin/env python3
"""
再热朗肯循环 (Reheat Rankine Cycle) 热力分析与 T-s 图绘制
Nature 论文级别图表风格

工况参数：
  锅炉压力 P_boiler = 15 MPa
  汽轮机入口温度 T_turbine_in = 600 °C
  再热压力 P_reheat = 3 MPa
  再热温度 T_reheat = 600 °C
  冷凝器压力 P_cond = 10 kPa
"""

import sys
import platform
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams

try:
    from CoolProp.CoolProp import PropsSI
except ImportError:
    print("错误：需要安装 CoolProp 库。请运行：pip install CoolProp")
    sys.exit(1)

# =============================================================================
# 1. 工况参数
# =============================================================================
P_boiler = 15e6       # 锅炉压力 15 MPa [Pa]
T_turb_in = 600 + 273.15  # 汽轮机入口温度 600 °C [K]
P_reheat = 3e6        # 再热压力 3 MPa [Pa]
T_reheat = 600 + 273.15   # 再热温度 600 °C [K]
P_cond = 10e3         # 冷凝器压力 10 kPa [Pa]

# 假设条件
eta_turb = 1.0        # 汽轮机等熵效率 100%（理想）
eta_pump = 1.0        # 泵等熵效率 100%（理想）
eta_isen_turb1 = eta_turb
eta_isen_turb2 = eta_turb

# =============================================================================
# 2. 状态点计算
# =============================================================================

# --- 状态点 1：冷凝器出口（饱和液体） ---
P1 = P_cond
T1 = PropsSI('T', 'P', P1, 'Q', 0, 'Water')
h1 = PropsSI('H', 'P', P1, 'Q', 0, 'Water')
s1 = PropsSI('S', 'P', P1, 'Q', 0, 'Water')
x1 = 0.0  # 饱和液体

# --- 状态点 2：泵出口（等熵压缩至锅炉压力） ---
P2 = P_boiler
s2s = s1  # 等熵
T2 = PropsSI('T', 'P', P2, 'S', s2s, 'Water')
h2 = PropsSI('H', 'P', P2, 'S', s2s, 'Water')
s2 = s2s

# --- 状态点 3：锅炉出口 / 高压汽轮机入口 ---
P3 = P_boiler
T3 = T_turb_in
h3 = PropsSI('H', 'P', P3, 'T', T3, 'Water')
s3 = PropsSI('S', 'P', P3, 'T', T3, 'Water')

# --- 状态点 4：高压汽轮机出口（等熵膨胀至再热压力） ---
P4 = P_reheat
s4s = s3  # 等熵
h4s = PropsSI('H', 'P', P4, 'S', s4s, 'Water')
T4 = PropsSI('T', 'P', P4, 'S', s4s, 'Water')
h4 = h4s
s4 = s4s
# 检查是否在两相区
s4f = PropsSI('S', 'P', P4, 'Q', 0, 'Water')
s4g = PropsSI('S', 'P', P4, 'Q', 1, 'Water')
if s4 < s4g:
    x4 = (s4 - s4f) / (s4g - s4f)
else:
    x4 = 1.0  # 过热

# --- 状态点 5：再热器出口 / 低压汽轮机入口 ---
P5 = P_reheat
T5 = T_reheat
h5 = PropsSI('H', 'P', P5, 'T', T5, 'Water')
s5 = PropsSI('S', 'P', P5, 'T', T5, 'Water')

# --- 状态点 6：低压汽轮机出口（等熵膨胀至冷凝器压力） ---
P6 = P_cond
s6s = s5  # 等熵
h6s = PropsSI('H', 'P', P6, 'S', s6s, 'Water')
T6 = PropsSI('T', 'P', P6, 'S', s6s, 'Water')
h6 = h6s
s6 = s6s
# 干度
s6f = PropsSI('S', 'P', P6, 'Q', 0, 'Water')
s6g = PropsSI('S', 'P', P6, 'Q', 1, 'Water')
x6 = (s6 - s6f) / (s6g - s6f)

# =============================================================================
# 3. 性能指标计算
# =============================================================================
w_turb1 = h3 - h4          # 高压汽轮机做功 [J/kg]
w_turb2 = h5 - h6          # 低压汽轮机做功 [J/kg]
w_turb = w_turb1 + w_turb2  # 总汽轮机做功 [J/kg]
w_pump = h2 - h1            # 泵耗功 [J/kg]
w_net = w_turb - w_pump     # 净功 [J/kg]

q_boiler = h3 - h2          # 锅炉吸热量 [J/kg]
q_reheat = h5 - h4          # 再热器吸热量 [J/kg]
q_in = q_boiler + q_reheat  # 总吸热量 [J/kg]
q_out = h6 - h1             # 冷凝器放热量 [J/kg]

eta_th = w_net / q_in       # 热效率
bwr = w_pump / w_turb       # 背功比

# 卡诺效率（参考）
T_H = T_turb_in  # 最高温度 [K]
T_L = T1          # 最低温度 [K]
eta_carnot = 1 - T_L / T_H

# =============================================================================
# 4. 打印分析报告
# =============================================================================
print("=" * 70)
print("  再热朗肯循环 (Reheat Rankine Cycle) 热力分析报告")
print("=" * 70)

print("\n## 一、输入参数")
print(f"  {'参数':<25s} {'值':<20s} {'来源'}")
print(f"  {'-'*60}")
print(f"  {'锅炉压力':<25s} {'15 MPa':<20s} {'给定'}")
print(f"  {'汽轮机入口温度':<25s} {'600 °C':<20s} {'给定'}")
print(f"  {'再热压力':<25s} {'3 MPa':<20s} {'给定'}")
print(f"  {'再热温度':<25s} {'600 °C':<20s} {'给定'}")
print(f"  {'冷凝器压力':<25s} {'10 kPa':<20s} {'给定'}")
print(f"  {'汽轮机等熵效率':<25s} {'100 %':<20s} {'假设（理想）'}")
print(f"  {'泵等熵效率':<25s} {'100 %':<20s} {'假设（理想）'}")
print(f"  {'忽略动能和势能变化':<25s} {'—':<20s} {'假设'}")

print("\n## 二、状态点参数")
header = f"  {'状态点':<6s} {'P (MPa)':<10s} {'T (°C)':<10s} {'h (kJ/kg)':<12s} {'s (kJ/(kg·K))':<15s} {'x':<8s} {'说明'}"
print(header)
print(f"  {'-'*80}")

states = [
    (1, P1/1e6, T1-273.15, h1/1e3, s1/1e3, x1, "冷凝器出口 (饱和液体)"),
    (2, P2/1e6, T2-273.15, h2/1e3, s2/1e3, "—", "泵出口 (过冷水)"),
    (3, P3/1e6, T3-273.15, h3/1e3, s3/1e3, "—", "锅炉出口 (过热蒸汽)"),
    (4, P4/1e6, T4-273.15, h4/1e3, s4/1e3, f"{x4:.4f}", "高压汽轮机出口"),
    (5, P5/1e6, T5-273.15, h5/1e3, s5/1e3, "—", "再热器出口 (过热蒸汽)"),
    (6, P6/1e6, T6-273.15, h6/1e3, s6/1e3, f"{x6:.4f}", "低压汽轮机出口 (湿蒸汽)"),
]

for st in states:
    i, P, T, h, s, x, desc = st
    print(f"  {i:<6d} {P:<10.2f} {T:<10.2f} {h:<12.2f} {s:<15.4f} {str(x):<8s} {desc}")

print("\n## 三、循环性能指标")
print(f"  循环热效率 η_th       = {eta_th*100:.2f} %")
print(f"  卡诺效率 η_carnot     = {eta_carnot*100:.2f} %")
print(f"  高压汽轮机做功 w_t1   = {w_turb1/1e3:.2f} kJ/kg")
print(f"  低压汽轮机做功 w_t2   = {w_turb2/1e3:.2f} kJ/kg")
print(f"  总汽轮机做功 w_t      = {w_turb/1e3:.2f} kJ/kg")
print(f"  泵耗功 w_p            = {w_pump/1e3:.2f} kJ/kg")
print(f"  净功 w_net            = {w_net/1e3:.2f} kJ/kg")
print(f"  锅炉吸热量 q_boiler   = {q_boiler/1e3:.2f} kJ/kg")
print(f"  再热器吸热量 q_reheat = {q_reheat/1e3:.2f} kJ/kg")
print(f"  总吸热量 q_in         = {q_in/1e3:.2f} kJ/kg")
print(f"  冷凝器放热量 q_out    = {q_out/1e3:.2f} kJ/kg")
print(f"  背功比 BWR            = {bwr*100:.2f} %")

print("\n## 四、分析与讨论")
print(f"  1. 再热朗肯循环热效率为 {eta_th*100:.2f}%，对应卡诺效率为 {eta_carnot*100:.2f}%。")
print(f"  2. 低压汽轮机出口蒸汽干度 x6 = {x6:.4f}，高于常规下限 0.88，")
print(f"     说明再热有效提升了末级干度，有利于减少叶片水蚀。")
print(f"  3. 再热使平均吸热温度提高，从而提高了循环热效率。")
print(f"  4. 背功比仅为 {bwr*100:.2f}%，泵耗功远小于汽轮机做功。")

# =============================================================================
# 5. T-s 图绘制 — Nature 论文风格
# =============================================================================

# --- 全局字体与样式设置 (Nature 规范) ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Helvetica', 'Arial', 'PingFang SC', 'SimHei']
rcParams['font.size'] = 6
rcParams['axes.linewidth'] = 0.5
rcParams['xtick.major.width'] = 0.5
rcParams['ytick.major.width'] = 0.5
rcParams['xtick.major.size'] = 2.5
rcParams['ytick.major.size'] = 2.5
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['xtick.minor.visible'] = False
rcParams['ytick.minor.visible'] = False
rcParams['legend.frameon'] = False
rcParams['axes.grid'] = False
rcParams['figure.facecolor'] = 'white'
rcParams['axes.facecolor'] = 'white'
rcParams['savefig.facecolor'] = 'white'
rcParams['pdf.fonttype'] = 42       # TrueType 字体嵌入（Nature 要求）
rcParams['ps.fonttype'] = 42

# --- 饱和曲线 ---
T_crit = PropsSI('Tcrit', 'Water')
T_sat = np.linspace(273.16, T_crit - 0.1, 500)
sf = np.array([PropsSI('S', 'T', T, 'Q', 0, 'Water') for T in T_sat])
sg = np.array([PropsSI('S', 'T', T, 'Q', 1, 'Water') for T in T_sat])

# --- 循环过程路径 ---

# 过程 1->2：泵压缩（等熵，在 T-s 图上几乎是一条竖线）
T_12 = np.linspace(T1, T2, 50)
s_12 = np.full_like(T_12, s1)

# 过程 2->3：锅炉加热（等压，从过冷水到过热蒸汽）
P_23 = P_boiler
T_sat_at_Pb = PropsSI('T', 'P', P_23, 'Q', 0, 'Water')
s_satl_at_Pb = PropsSI('S', 'P', P_23, 'Q', 0, 'Water')
s_satg_at_Pb = PropsSI('S', 'P', P_23, 'Q', 1, 'Water')

# 过冷水加热段 (2 -> 饱和液体)，T2 非常接近饱和温度，留一点余量
T_start_sub = T2
T_end_sub = T_sat_at_Pb - 0.01  # 避免刚好在饱和线上数值问题
if T_end_sub > T_start_sub + 0.1:
    T_2_to_satl = np.linspace(T_start_sub, T_end_sub, 40)
    s_2_to_satl = np.array([PropsSI('S', 'P', P_23, 'T', T, 'Water') for T in T_2_to_satl])
else:
    T_2_to_satl = np.array([T_start_sub])
    s_2_to_satl = np.array([s2])

# 两相区
T_2phase_high = np.full(50, T_sat_at_Pb)
s_2phase_high = np.linspace(s_satl_at_Pb, s_satg_at_Pb, 50)

# 过热区（从饱和蒸汽到锅炉出口温度）
T_sup_to3 = np.linspace(T_sat_at_Pb + 0.01, T3, 80)
s_sup_to3 = np.array([PropsSI('S', 'P', P_23, 'T', T, 'Water') for T in T_sup_to3])

# 合并 2->3
T_23 = np.concatenate([T_2_to_satl, T_2phase_high, T_sup_to3])
s_23 = np.concatenate([s_2_to_satl, s_2phase_high, s_sup_to3])

# 过程 3->4：高压汽轮机等熵膨胀
# 沿等熵线 s=s3，从 P_boiler 膨胀到 P_reheat
P_34 = np.linspace(P_boiler, P_reheat, 100)
T_34 = np.array([PropsSI('T', 'P', P, 'S', s3, 'Water') for P in P_34])
s_34 = np.full_like(T_34, s3)

# 过程 4->5：再热器等压加热
T_45 = np.linspace(T4, T5, 80)
s_45 = np.array([PropsSI('S', 'P', P_reheat, 'T', T, 'Water') for T in T_45])

# 过程 5->6：低压汽轮机等熵膨胀
P_56 = np.linspace(P_reheat, P_cond, 150)
T_56 = np.array([PropsSI('T', 'P', P, 'S', s5, 'Water') for P in P_56])
s_56 = np.full_like(T_56, s5)

# 过程 6->1：冷凝器等压放热（从湿蒸汽到饱和液体）
# 沿 P_cond 等压线
T_sat_at_Pc = PropsSI('T', 'P', P_cond, 'Q', 0, 'Water')
s_6_to_1 = np.linspace(s6, s1, 80)
T_6_to_1 = np.full(80, T_sat_at_Pc)

# --- 创建图形 ---
fig, ax = plt.subplots(figsize=(3.5, 2.8), dpi=300)

# Nature 推荐色板
color_cycle = '#0C5DA5'     # 蓝色 - 循环路径
color_sat = '#888888'        # 灰色 - 饱和曲线
color_reheat = '#FF2C00'     # 红色 - 再热段
color_fill = '#0C5DA5'       # 填充色

# 绘制饱和曲线（灰色虚线）
ax.plot(sf / 1e3, T_sat - 273.15, '--', color=color_sat, linewidth=0.6,
        label='Saturated liquid')
ax.plot(sg / 1e3, T_sat - 273.15, '--', color=color_sat, linewidth=0.6,
        label='Saturated vapor')

# 填充饱和曲线之间的区域（极低透明度）
ax.fill(np.concatenate([sf / 1e3, sg[::-1] / 1e3]),
        np.concatenate([T_sat - 273.15, (T_sat - 273.15)[::-1]]),
        color=color_sat, alpha=0.05)

# 绘制循环路径
# 1->2 泵（蓝色）
ax.plot(s_12 / 1e3, T_12 - 273.15, '-', color=color_cycle, linewidth=0.9)

# 2->3 锅炉（蓝色）
ax.plot(s_23 / 1e3, T_23 - 273.15, '-', color=color_cycle, linewidth=0.9)

# 3->4 高压汽轮机（蓝色）
ax.plot(s_34 / 1e3, T_34 - 273.15, '-', color=color_cycle, linewidth=0.9)

# 4->5 再热器（红色，以区分再热过程）
ax.plot(s_45 / 1e3, T_45 - 273.15, '-', color=color_reheat, linewidth=0.9)

# 5->6 低压汽轮机（蓝色）
ax.plot(s_56 / 1e3, T_56 - 273.15, '-', color=color_cycle, linewidth=0.9)

# 6->1 冷凝器（蓝色）
ax.plot(s_6_to_1 / 1e3, T_6_to_1 - 273.15, '-', color=color_cycle, linewidth=0.9)

# 填充循环区域（低透明度）
s_cycle = np.concatenate([s_12, s_23, s_34, s_45, s_56, s_6_to_1]) / 1e3
T_cycle = np.concatenate([T_12, T_23, T_34, T_45, T_56, T_6_to_1]) - 273.15
ax.fill(s_cycle, T_cycle, color=color_fill, alpha=0.08)

# 标注状态点
state_points = [
    (s1 / 1e3, T1 - 273.15, '1'),
    (s2 / 1e3, T2 - 273.15, '2'),
    (s3 / 1e3, T3 - 273.15, '3'),
    (s4 / 1e3, T4 - 273.15, '4'),
    (s5 / 1e3, T5 - 273.15, '5'),
    (s6 / 1e3, T6 - 273.15, '6'),
]

for sx, tx, label in state_points:
    ax.plot(sx, tx, 'o', markersize=3.5, markeredgecolor='black',
            markerfacecolor='white', markeredgewidth=0.6, zorder=5)
    # 偏移标注位置
    offset_x, offset_y = 0.05, 8
    if label == '1':
        offset_x, offset_y = -0.25, -15
    elif label == '2':
        offset_x, offset_y = -0.15, -15
    elif label == '3':
        offset_x, offset_y = 0.08, 8
    elif label == '4':
        offset_x, offset_y = 0.08, -12
    elif label == '5':
        offset_x, offset_y = 0.08, 8
    elif label == '6':
        offset_x, offset_y = -0.25, -15
    ax.annotate(label, (sx, tx), xytext=(sx + offset_x, tx + offset_y),
                fontsize=6, fontweight='bold', ha='center', va='center',
                color='black')

# 过程标注（直接在曲线旁，无图例框）
# 锅炉
idx_mid_boiler = len(s_2_to_satl) + len(T_2phase_high) // 2
ax.annotate('Boiler', xy=(s_23[idx_mid_boiler] / 1e3, T_23[idx_mid_boiler] - 273.15),
            fontsize=5, color=color_cycle, ha='left',
            xytext=(s_23[idx_mid_boiler] / 1e3 + 0.15, T_23[idx_mid_boiler] - 273.15 + 10))

# 再热器
idx_mid_reheat = len(T_45) // 2
ax.annotate('Reheater', xy=(s_45[idx_mid_reheat] / 1e3, T_45[idx_mid_reheat] - 273.15),
            fontsize=5, color=color_reheat, ha='left',
            xytext=(s_45[idx_mid_reheat] / 1e3 + 0.1, T_45[idx_mid_reheat] - 273.15 + 8))

# 高压汽轮机
ax.annotate('HP Turbine', xy=(s_34[0] / 1e3, T_34[0] - 273.15),
            fontsize=5, color=color_cycle, ha='right',
            xytext=(s_34[0] / 1e3 - 0.15, T_34[0] - 273.15 - 20))

# 低压汽轮机
idx_mid_lt = len(T_56) // 2
ax.annotate('LP Turbine', xy=(s_56[idx_mid_lt] / 1e3, T_56[idx_mid_lt] - 273.15),
            fontsize=5, color=color_cycle, ha='left',
            xytext=(s_56[idx_mid_lt] / 1e3 + 0.05, T_56[idx_mid_lt] - 273.15 + 10))

# 冷凝器
ax.annotate('Condenser', xy=((s6 + s1) / 2 / 1e3, T6 - 273.15),
            fontsize=5, color=color_cycle, ha='center',
            xytext=((s6 + s1) / 2 / 1e3, T6 - 273.15 - 18))

# 泵
ax.annotate('Pump', xy=(s_12[len(T_12) // 2] / 1e3, (T1 + T2) / 2 - 273.15),
            fontsize=5, color=color_cycle, ha='right',
            xytext=(s1 / 1e3 - 0.2, (T1 + T2) / 2 - 273.15 + 10))

# 坐标轴标签
ax.set_xlabel('Specific entropy, $s$ (kJ kg$^{-1}$ K$^{-1}$)', fontsize=7)
ax.set_ylabel('Temperature, $T$ (°C)', fontsize=7)
ax.tick_params(axis='both', which='major', labelsize=5.5)

# 去掉上边和右边的边框线（Nature 规范）
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 设置坐标轴范围
ax.set_xlim(0, max(sg / 1e3) * 1.02)
y_max = max(T3, T5) - 273.15
ax.set_ylim(-10, y_max + 30)

# 紧凑布局
plt.tight_layout(pad=0.5)

# --- 保存 ---
output_dir = '/Users/zhujingchen/thermo-cycle-analyzer/examples/rankine-reheat/'
png_path = output_dir + 'rankine_reheat_ts.png'
pdf_path = output_dir + 'rankine_reheat_ts.pdf'

fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(pdf_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n图表已保存：")
print(f"  PNG: {png_path}")
print(f"  PDF: {pdf_path}")

plt.close()
print("\n完成！")
