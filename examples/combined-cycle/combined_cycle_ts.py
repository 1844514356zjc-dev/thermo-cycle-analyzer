#!/usr/bin/env python3
"""
联合循环 (Combined Cycle) 热力循环分析
燃气轮机 (Brayton) + 余热锅炉 + 汽轮机 (Rankine)

Nature 论文风格 T-s 图
使用 CoolProp 获取真实物性
"""

import sys
import numpy as np

try:
    from CoolProp.CoolProp import PropsSI
except ImportError:
    print("Error: CoolProp is required. Install with: pip install CoolProp")
    sys.exit(1)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import matplotlib.font_manager as fm

# ============================================================
# 1. 输入参数
# ============================================================

# --- 布雷顿循环 (燃气侧) ---
T1_brayton = 290.0       # K, 压气机入口温度
P1_brayton = 101.325     # kPa, 压气机入口压力 (1 atm)
r_p        = 20.0        # 增压比
T3_brayton = 1600.0      # K, 燃气轮机入口温度
eta_c      = 1.0         # 压气机等熵效率 (理想)
eta_gt     = 1.0         # 燃气轮机等熵效率 (理想)

# --- 朗肯循环 (蒸汽侧) ---
P_steam    = 8000.0      # kPa, 余热锅炉蒸汽压力 (8 MPa)
T_steam_C  = 520.0       # °C
T_steam    = T_steam_C + 273.15  # K
P_cond     = 8.0         # kPa, 冷凝器压力
eta_t_rank = 1.0         # 汽轮机等熵效率 (理想)
eta_pump   = 1.0         # 泵等熵效率 (理想)

# 空气物性常数
gamma_air = 1.4
cp_air    = 1.005        # kJ/(kg*K)

# ============================================================
# 2. 布雷顿循环状态点计算 (空气, 理想气体)
# ============================================================

# 状态点 1: 压气机入口
T1 = T1_brayton
P1 = P1_brayton

# 状态点 2: 压气机出口 (等熵压缩)
T2 = T1 * r_p ** ((gamma_air - 1) / gamma_air)
P2 = P1 * r_p

# 状态点 3: 燃烧室出口 / 燃气轮机入口
T3 = T3_brayton
P3 = P2

# 状态点 4: 燃气轮机出口 (等熵膨胀)
T4 = T3 / (r_p ** ((gamma_air - 1) / gamma_air))
P4 = P1

# 布雷顿循环性能 (每 kg 空气)
h1_b = cp_air * T1
h2_b = cp_air * T2
h3_b = cp_air * T3
h4_b = cp_air * T4

w_compressor = h2_b - h1_b
w_gas_turbine = h3_b - h4_b
q_in_brayton = h3_b - h2_b
w_net_brayton = w_gas_turbine - w_compressor
q_out_brayton = h4_b - h1_b

T4_exhaust = T4  # K

# ============================================================
# 3. 朗肯循环状态点计算 (水/蒸汽, CoolProp)
# ============================================================

# 状态点 5: 冷凝器出口 (饱和液体)
P5 = P_cond
T5 = PropsSI('T', 'P', P5 * 1000, 'Q', 0, 'Water')
h5 = PropsSI('H', 'P', P5 * 1000, 'Q', 0, 'Water') / 1000
s5 = PropsSI('S', 'P', P5 * 1000, 'Q', 0, 'Water') / 1000
x5 = 0.0

# 状态点 6: 泵出口 (等熵压缩到 P_steam)
P6 = P_steam
v5 = 1.0 / PropsSI('D', 'P', P5 * 1000, 'Q', 0, 'Water')
w_pump_s = v5 * (P6 - P5)
h6 = h5 + w_pump_s
T6 = PropsSI('T', 'H', h6 * 1000, 'P', P6 * 1000, 'Water')
s6 = PropsSI('S', 'H', h6 * 1000, 'P', P6 * 1000, 'Water') / 1000

# 状态点 7: 余热锅炉出口 / 汽轮机入口 (过热蒸汽)
P7 = P_steam
T7 = T_steam
h7 = PropsSI('H', 'P', P7 * 1000, 'T', T7, 'Water') / 1000
s7 = PropsSI('S', 'P', P7 * 1000, 'T', T7, 'Water') / 1000

# 状态点 8: 汽轮机出口 (等熵膨胀到 P_cond)
P8 = P_cond
s8 = s7
h8 = PropsSI('H', 'P', P8 * 1000, 'S', s8 * 1000, 'Water') / 1000
T8 = PropsSI('T', 'P', P8 * 1000, 'S', s8 * 1000, 'Water')
x8 = PropsSI('Q', 'P', P8 * 1000, 'S', s8 * 1000, 'Water')

# 朗肯循环性能
w_steam_turbine = h7 - h8
w_pump_actual = h6 - h5
w_net_rankine = w_steam_turbine - w_pump_actual
q_in_rankine = h7 - h6
q_out_rankine = h8 - h5

# ============================================================
# 4. 联合循环: 能量匹配
# ============================================================

T_sat_steam = PropsSI('T', 'P', P_steam * 1000, 'Q', 0, 'Water')
T_pinch = 20.0
T_stack = T_sat_steam + T_pinch

q_available = cp_air * (T4_exhaust - T_stack)
mass_ratio = q_available / q_in_rankine

w_net_total = w_net_brayton + mass_ratio * w_net_rankine
q_in_total = q_in_brayton
eta_combined = w_net_total / q_in_total * 100

# ============================================================
# 5. 打印报告
# ============================================================

print("=" * 70)
print("联合循环 (Combined Cycle) 热力循环分析报告")
print("=" * 70)

print("\n## 一、输入参数\n")
print(f"{'参数':<30s} {'值':<20s} {'来源':<10s}")
print("-" * 60)
params = [
    ("压气机入口温度",         f"{T1_brayton:<.1f} K",    "给定"),
    ("增压比",                 f"{r_p:<.1f}",             "给定"),
    ("燃气轮机入口温度",       f"{T3_brayton:<.1f} K",    "给定"),
    ("余热锅炉蒸汽压力",       f"{P_steam/1000:<.1f} MPa","给定"),
    ("余热锅炉蒸汽温度",       f"{T_steam_C:<.1f} °C",    "给定"),
    ("冷凝器压力",             f"{P_cond:<.1f} kPa",      "给定"),
    ("压气机等熵效率",         f"{eta_c*100:<.1f} %",      "假设"),
    ("燃气轮机等熵效率",       f"{eta_gt*100:<.1f} %",     "假设"),
    ("汽轮机等熵效率",         f"{eta_t_rank*100:<.1f} %", "假设"),
    ("泵等熵效率",             f"{eta_pump*100:<.1f} %",   "假设"),
    ("节点温差",               f"{T_pinch:<.1f} K",       "假设"),
]
for name, val, src in params:
    print(f"  {name:<28s} {val:<20s} {src}")

print("\n## 二、假设条件\n")
print("  1. 空气为理想气体, cp = 1.005 kJ/(kg·K), gamma = 1.4")
print("  2. 各部件等熵效率均为 100% (理想循环)")
print("  3. 忽略动能和势能变化")
print("  4. 忽略管道压力损失")
print("  5. 余热锅炉节点温差 (Pinch Point) 取 20 K")
print("  6. 燃气侧比热容为常数")

print("\n## 三、状态点参数\n")
print("  --- 布雷顿循环 (燃气侧, 1 kg 空气) ---\n")
print(f"  {'点':<4s} {'T (K)':<10s} {'P (kPa)':<12s} {'h (kJ/kg)':<14s}")
print("  " + "-" * 40)
print(f"  {'1':<4s} {T1:<10.2f} {P1:<12.2f} {h1_b:<14.2f}")
print(f"  {'2':<4s} {T2:<10.2f} {P2:<12.2f} {h2_b:<14.2f}")
print(f"  {'3':<4s} {T3:<10.2f} {P3:<12.2f} {h3_b:<14.2f}")
print(f"  {'4':<4s} {T4:<10.2f} {P4:<12.2f} {h4_b:<14.2f}")

print(f"\n  --- 朗肯循环 (蒸汽侧, 1 kg 蒸汽) ---\n")
print(f"  {'点':<4s} {'T (°C)':<10s} {'P (kPa)':<12s} {'h (kJ/kg)':<14s} {'s (kJ/kg·K)':<14s} {'x':<8s}")
print("  " + "-" * 62)
print(f"  {'5':<4s} {T5-273.15:<10.2f} {P5:<12.2f} {h5:<14.2f} {s5:<14.4f} {'0.00':<8s}")
print(f"  {'6':<4s} {T6-273.15:<10.2f} {P6:<12.2f} {h6:<14.2f} {s6:<14.4f} {'---':<8s}")
print(f"  {'7':<4s} {T7-273.15:<10.2f} {P7:<12.2f} {h7:<14.2f} {s7:<14.4f} {'---':<8s}")
print(f"  {'8':<4s} {T8-273.15:<10.2f} {P8:<12.2f} {h8:<14.2f} {s8:<14.4f} {x8:<8.4f}")

print("\n## 四、循环性能指标\n")
eta_brayton = w_net_brayton / q_in_brayton * 100
eta_rankine = w_net_rankine / q_in_rankine * 100

print("  --- 布雷顿循环 ---")
print(f"    燃气轮机做功:       w_gt    = {w_gas_turbine:.2f} kJ/kg_air")
print(f"    压气机耗功:         w_c     = {w_compressor:.2f} kJ/kg_air")
print(f"    布雷顿净功:         w_net,B = {w_net_brayton:.2f} kJ/kg_air")
print(f"    吸热量:             q_in    = {q_in_brayton:.2f} kJ/kg_air")
print(f"    布雷顿热效率:       eta_B   = {eta_brayton:.2f} %")

print("\n  --- 朗肯循环 ---")
print(f"    汽轮机做功:         w_st    = {w_steam_turbine:.2f} kJ/kg_steam")
print(f"    泵耗功:             w_p     = {w_pump_actual:.4f} kJ/kg_steam")
print(f"    朗肯净功:           w_net,R = {w_net_rankine:.2f} kJ/kg_steam")
print(f"    吸热量 (HRSG):      q_HRSG  = {q_in_rankine:.2f} kJ/kg_steam")
print(f"    朗肯热效率:         eta_R   = {eta_rankine:.2f} %")

print("\n  --- 联合循环 ---")
print(f"    蒸汽/空气质量比:    m_ratio = {mass_ratio:.6f} kg_steam/kg_air")
print(f"    排烟温度:           T_stack = {T_stack:.2f} K ({T_stack-273.15:.2f} °C)")
print(f"    总净功:             w_net   = {w_net_total:.2f} kJ/kg_air")
print(f"    总吸热量:           q_in    = {q_in_total:.2f} kJ/kg_air")
print(f"    联合循环热效率:     eta_CC  = {eta_combined:.2f} %")

T_H = T3_brayton
T_L = T5
eta_carnot = (1 - T_L / T_H) * 100
print(f"\n    卡诺效率 (参考):    eta_Carnot = {eta_carnot:.2f} %")
print(f"    联合循环 / 卡诺:    {eta_combined/eta_carnot*100:.2f} %")

# ============================================================
# 6. 绘制 Nature 风格 T-s 图
# ============================================================

# --- 全局字体与样式 (Nature 规范) ---
rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 6,
    'axes.linewidth': 0.5,
    'xtick.major.width': 0.5,
    'ytick.major.width': 0.5,
    'xtick.major.size': 3,
    'ytick.major.size': 3,
    'xtick.direction': 'in',
    'ytick.direction': 'in',
    'xtick.minor.visible': False,
    'ytick.minor.visible': False,
    'axes.labelsize': 7,
    'xtick.labelsize': 5.5,
    'ytick.labelsize': 5.5,
    'legend.fontsize': 5.5,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'text.antialiased': True,
    'axes.unicode_minus': False,
})

# --- 颜色方案 (Nature 推荐) ---
C_BRAYTON  = '#0C5DA5'
C_RANKINE  = '#FF2C00'
C_SAT      = '#888888'

# --- 创建画布: 双栏宽度 (183 mm = 7.2 inch), 用于联合循环双图 ---
fig_width = 7.2   # inch, Nature 双栏
fig_height = 3.0   # inch

fig, (ax_b, ax_r) = plt.subplots(1, 2, figsize=(fig_width, fig_height),
                                  gridspec_kw={'width_ratios': [1, 1.1], 'wspace': 0.35})
fig.patch.set_facecolor('white')

# ==========================
# Panel (a): 布雷顿循环 T-s
# ==========================
ax_b.set_facecolor('white')

# 布雷顿熵值 (用 CoolProp Air)
s1_abs = PropsSI('S', 'T', T1, 'P', P1 * 1000, 'Air') / 1000
s2_abs = PropsSI('S', 'T', T2, 'P', P2 * 1000, 'Air') / 1000
s3_abs = PropsSI('S', 'T', T3, 'P', P3 * 1000, 'Air') / 1000
s4_abs = PropsSI('S', 'T', T4, 'P', P4 * 1000, 'Air') / 1000

n_pts = 100

# 1->2 等熵 (垂直线)
# 2->3 等压加热
T_23 = np.linspace(T2, T3, n_pts)
s_23 = np.array([PropsSI('S', 'T', T, 'P', P2 * 1000, 'Air') / 1000 for T in T_23])
# 3->4 等熵 (垂直线)
# 4->1 等压放热
T_41 = np.linspace(T4, T1, n_pts)
s_41 = np.array([PropsSI('S', 'T', T, 'P', P1 * 1000, 'Air') / 1000 for T in T_41])

# 绘制布雷顿循环路径
ax_b.plot([s1_abs, s2_abs], [T1 - 273.15, T2 - 273.15], '-', color=C_BRAYTON, lw=0.9, zorder=3)
ax_b.plot(s_23, T_23 - 273.15, '-', color=C_BRAYTON, lw=0.9, zorder=3)
ax_b.plot([s3_abs, s4_abs], [T3 - 273.15, T4 - 273.15], '-', color=C_BRAYTON, lw=0.9, zorder=3)
ax_b.plot(s_41, T_41 - 273.15, '-', color=C_BRAYTON, lw=0.9, zorder=3)

# 填充
s_fill = np.concatenate([[s1_abs], [s2_abs], s_23, [s3_abs], [s4_abs], s_41[::-1]])
T_fill = np.concatenate([[T1], [T2], T_23, [T3], [T4], T_41[::-1]])
ax_b.fill(s_fill, T_fill - 273.15, color=C_BRAYTON, alpha=0.08, zorder=0)

# 状态点标记
b_pts = {'1': (s1_abs, T1), '2': (s2_abs, T2), '3': (s3_abs, T3), '4': (s4_abs, T4)}
for lbl, (sv, tv) in b_pts.items():
    ax_b.plot(sv, tv - 273.15, 'o', ms=3.5, mfc='white', mec=C_BRAYTON, mew=0.6, zorder=5)
    offsets = {'1': (-6, -8), '2': (-6, 6), '3': (5, 6), '4': (5, -8)}
    dx, dy = offsets[lbl]
    ax_b.annotate(lbl, (sv, tv - 273.15), xytext=(dx, dy),
                  textcoords='offset points', fontsize=6,
                  color=C_BRAYTON, fontweight='bold', ha='center', va='center')

# 排气余热标注
ax_b.annotate('', xy=(s4_abs + 0.02, T_stack - 273.15), xytext=(s4_abs + 0.02, T4 - 273.15),
              arrowprops=dict(arrowstyle='<->', color=C_SAT, lw=0.5))
ax_b.text(s4_abs + 0.06, (T4 + T_stack) / 2 - 273.15, 'HRSG',
          fontsize=5, color=C_SAT, fontstyle='italic', va='center')

ax_b.set_xlabel('s (kJ kg$^{-1}$ K$^{-1}$)', fontsize=7)
ax_b.set_ylabel('T ($^\\circ$C)', fontsize=7)
ax_b.text(0.03, 0.96, '(a) Brayton cycle', transform=ax_b.transAxes,
          fontsize=6.5, fontweight='bold', va='top')
ax_b.spines['top'].set_visible(False)
ax_b.spines['right'].set_visible(False)

# ==========================
# Panel (b): 朗肯循环 T-s
# ==========================
ax_r.set_facecolor('white')

# 饱和曲线
T_sat_range = np.linspace(273.16 + 1, 647.096 - 1, 500)
s_liq, s_vap, T_sv = [], [], []
for T in T_sat_range:
    try:
        sf = PropsSI('S', 'T', T, 'Q', 0, 'Water') / 1000
        sg = PropsSI('S', 'T', T, 'Q', 1, 'Water') / 1000
        s_liq.append(sf)
        s_vap.append(sg)
        T_sv.append(T)
    except Exception:
        continue

T_sv = np.array(T_sv)
s_liq = np.array(s_liq)
s_vap = np.array(s_vap)

ax_r.plot(s_liq, T_sv - 273.15, '--', color=C_SAT, lw=0.5, zorder=1)
ax_r.plot(s_vap, T_sv - 273.15, '--', color=C_SAT, lw=0.5, zorder=1)

# 朗肯循环路径
# 5->6 泵 (垂直线, 几乎不可见)
s_56 = np.array([s5, s6])
T_56 = np.array([T5, T6])

# 6->7 等压加热
T_67 = np.linspace(T6, T7, n_pts)
s_67 = np.array([PropsSI('S', 'T', T, 'P', P_steam * 1000, 'Water') / 1000 for T in T_67])

# 7->8 等熵膨胀 (垂直线)
s_78 = np.array([s7, s8])
T_78 = np.array([T7, T8])

# 8->5 等压放热
s_85_arr = np.linspace(s8, s5, n_pts)
T_85 = np.array([PropsSI('T', 'S', s * 1000, 'P', P_cond * 1000, 'Water') for s in s_85_arr])

ax_r.plot(s_56, T_56 - 273.15, '-', color=C_RANKINE, lw=0.9, zorder=3)
ax_r.plot(s_67, T_67 - 273.15, '-', color=C_RANKINE, lw=0.9, zorder=3)
ax_r.plot(s_78, T_78 - 273.15, '-', color=C_RANKINE, lw=0.9, zorder=3)
ax_r.plot(s_85_arr, T_85 - 273.15, '-', color=C_RANKINE, lw=0.9, zorder=3)

# 填充
s_r_fill = np.concatenate([s_56, s_67, s_78, s_85_arr])
T_r_fill = np.concatenate([T_56, T_67, T_78, T_85])
ax_r.fill(s_r_fill, T_r_fill - 273.15, color=C_RANKINE, alpha=0.10, zorder=0)

# 状态点标记
r_pts = {'5': (s5, T5), '6': (s6, T6), '7': (s7, T7), '8': (s8, T8)}
for lbl, (sv, tv) in r_pts.items():
    ax_r.plot(sv, tv - 273.15, 'o', ms=3.5, mfc='white', mec=C_RANKINE, mew=0.6, zorder=5)
    offsets = {'5': (6, -6), '6': (-6, 6), '7': (-6, 6), '8': (6, -6)}
    dx, dy = offsets[lbl]
    ax_r.annotate(lbl, (sv, tv - 273.15), xytext=(dx, dy),
                  textcoords='offset points', fontsize=6,
                  color=C_RANKINE, fontweight='bold', ha='center', va='center')

# 标注过程
ax_r.text(0.45, 0.55, 'HRSG', transform=ax_r.transAxes,
          fontsize=5, color=C_RANKINE, fontstyle='italic',
          ha='center', va='center', rotation=55)

ax_r.set_xlabel('s (kJ kg$^{-1}$ K$^{-1}$)', fontsize=7)
ax_r.set_ylabel('T ($^\\circ$C)', fontsize=7)
ax_r.text(0.03, 0.96, '(b) Rankine cycle', transform=ax_r.transAxes,
          fontsize=6.5, fontweight='bold', va='top')
ax_r.spines['top'].set_visible(False)
ax_r.spines['right'].set_visible(False)

# --- 整体标题 ---
fig.text(0.5, -0.02,
         f'$\\eta_{{\\mathrm{{CC}}}}$ = {eta_combined:.1f}%    '
         f'$\\eta_{{\\mathrm{{Brayton}}}}$ = {eta_brayton:.1f}%    '
         f'$\\eta_{{\\mathrm{{Rankine}}}}$ = {eta_rankine:.1f}%    '
         f'$\\eta_{{\\mathrm{{Carnot}}}}$ = {eta_carnot:.1f}%',
         fontsize=6, ha='center', va='top', color='#333333')

plt.tight_layout(pad=0.5)

# --- 保存 ---
output_dir = '/Users/zhujingchen/thermo-cycle-analyzer/examples/combined-cycle'
png_path = f'{output_dir}/combined_cycle_Ts.png'
pdf_path = f'{output_dir}/combined_cycle_Ts.pdf'

fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(pdf_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n图片已保存:")
print(f"  PNG: {png_path}")
print(f"  PDF: {pdf_path}")
plt.close(fig)

# ============================================================
# 7. 分析与讨论
# ============================================================
print("\n## 五、分析与讨论\n")
print(f"  1. 联合循环热效率为 {eta_combined:.2f}%, 远高于单独布雷顿循环 ({eta_brayton:.2f}%)")
print(f"     和单独朗肯循环 ({eta_rankine:.2f}%)。")
print(f"  2. 卡诺效率 (T_H = {T3_brayton:.0f} K, T_L = {T5:.1f} K) = {eta_carnot:.2f}%。")
print(f"     联合循环达到卡诺效率的 {eta_combined/eta_carnot*100:.1f}%。")
print(f"  3. 燃气轮机排气温度 {T4:.1f} K ({T4-273.15:.1f} C), 足以驱动余热锅炉。")
print(f"  4. 排烟温度 {T_stack:.1f} K ({T_stack-273.15:.1f} C), 仍有余热可利用。")
print(f"  5. 实际联合循环考虑各项损失后, 热效率一般为 55-63%。")
print("=" * 70)
