#!/usr/bin/env python3
"""
回热布雷顿循环 (Regenerative Brayton Cycle) T-s 图绘制
Nature 论文级别图表风格

循环流程：压气机 → 回热器(高压侧) → 燃烧室 → 燃气轮机 → 回热器(低压侧) → 排气

状态点编号：
  1 - 压气机入口
  2 - 压气机出口（理想等熵压缩）
  3 - 回热器高压侧出口（经回热器预热后进入燃烧室）
  4 - 燃烧室出口 / 燃气轮机入口
  5 - 燃气轮机出口（理想等熵膨胀）
  6 - 回热器低压侧出口（经回热器冷却后排入大气）
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import platform
import os

# =====================================================================
# 1. 参数定义
# =====================================================================
# 用户给定参数
T1 = 300.0       # 压气机入口温度 [K]
r_p = 10.0       # 增压比
T4 = 1500.0      # 燃气轮机入口温度 [K]
epsilon = 0.8    # 回热器有效率

# 假设参数
gamma = 1.4      # 空气比热比 (理想气体，定比热容)
cp = 1.005       # 空气定压比热容 [kJ/(kg·K)]
R_air = 0.287    # 空气气体常数 [kJ/(kg·K)]
P1 = 101.325     # 压气机入口压力 [kPa] (标准大气压)

# =====================================================================
# 2. 状态点计算
# =====================================================================
# 状态 1：压气机入口
P1_val = P1
s1_ref = 0.0  # 以状态1为参考，s1 = 0

# 状态 2：压气机出口（理想等熵压缩）
P2 = r_p * P1_val
T2 = T1 * r_p ** ((gamma - 1) / gamma)
s2 = s1_ref  # 等熵过程 s2 = s1

# 状态 5：燃气轮机出口（理想等熵膨胀）
P5 = P1_val  # 膨胀回大气压力
T5 = T4 * (1 / r_p) ** ((gamma - 1) / gamma)
# s5 以状态4为参考计算
s4_ref = 0.0  # 重新以状态4为参考
s5_ref = s4_ref  # 等熵膨胀 s5 = s4

# 统一熵参考：选择统一参考态 s=0 at T=T1, P=P1
# 理想气体 s(T,P) = cp*ln(T/T1) - R*ln(P/P1)
def entropy(T, P):
    """计算相对于参考态(T1, P1)的比熵 [kJ/(kg·K)]"""
    return cp * np.log(T / T1) - R_air * np.log(P / P1_val)

s1 = entropy(T1, P1_val)
s2 = entropy(T2, P2)
s5 = entropy(T5, P5)

# 状态 4：燃烧室出口 / 燃气轮机入口
P4 = P2  # 燃烧室中压力近似不变
s4 = entropy(T4, P4)

# 状态 3：回热器高压侧出口
# 回热器有效率：epsilon = (T3 - T2) / (T5 - T2)
T3 = T2 + epsilon * (T5 - T2)
P3 = P2  # 回热器中压力损失忽略
s3 = entropy(T3, P3)

# 状态 6：回热器低压侧出口
# 能量守恒：cp*(T3-T2) = cp*(T5-T6)  =>  T6 = T5 - (T3-T2)
T6 = T5 - (T3 - T2)
P6 = P1_val  # 排入大气
s6 = entropy(T6, P6)

# 比焓 (理想气体, h = cp * T)
h1 = cp * T1
h2 = cp * T2
h3 = cp * T3
h4 = cp * T4
h5 = cp * T5
h6 = cp * T6

# =====================================================================
# 3. 性能指标计算
# =====================================================================
w_compressor = h2 - h1       # 压气机耗功 [kJ/kg]
w_turbine = h4 - h5          # 燃气轮机做功 [kJ/kg]
w_net = w_turbine - w_compressor  # 净功 [kJ/kg]
q_in = h4 - h3               # 燃烧室吸热量 [kJ/kg]
q_out = h6 - h1               # 排热 [kJ/kg]
eta = w_net / q_in * 100      # 热效率 [%]
bwr = w_compressor / w_turbine  # 背功比

# 无回热时的效率（对比用）
q_in_no_regen = h4 - h2
eta_no_regen = w_net / q_in_no_regen * 100

# 卡诺效率（对比用）
eta_carnot = (1 - T1 / T4) * 100

# =====================================================================
# 4. 打印分析报告
# =====================================================================
print("=" * 65)
print("      回热布雷顿循环 (Regenerative Brayton Cycle) 分析报告")
print("=" * 65)

print("\n--- 一、输入参数 ---")
print(f"{'参数':<25} {'值':<20} {'来源'}")
print("-" * 60)
print(f"{'压气机入口温度 T₁':<25} {T1:<20.1f} {'给定'}")
print(f"{'增压比 rₚ':<25} {r_p:<20.1f} {'给定'}")
print(f"{'燃气轮机入口温度 T₄':<25} {T4:<20.1f} {'给定'}")
print(f"{'回热器有效率 ε':<25} {epsilon:<20.2f} {'给定'}")
print(f"{'压气机入口压力 P₁':<25} {P1_val:<20.2f} {'假设 (标准大气压)'}")
print(f"{'比热比 γ':<25} {gamma:<20.2f} {'假设 (空气)'}")
print(f"{'定压比热容 cₚ':<25} {cp:<20.3f} {'假设 (空气)'}")

print("\n--- 二、假设条件 ---")
print("  1. 工质为理想空气，定比热容 (cp = 1.005 kJ/(kg·K), γ = 1.4)")
print("  2. 压气机和燃气轮机均为理想等熵过程 (η_s = 100%)")
print("  3. 忽略燃烧室和回热器中的压力损失")
print("  4. 忽略动能和势能变化")
print("  5. 回热器按给定的有效率 0.8 运行")

print("\n--- 三、状态点参数 ---")
print(f"{'状态点':<8} {'描述':<15} {'T (K)':<10} {'P (kPa)':<12} {'h (kJ/kg)':<12} {'s (kJ/(kg·K))':<15}")
print("-" * 72)
for label, desc, T, P, h, s in [
    ("1", "压气机入口",   T1, P1_val, h1, s1),
    ("2", "压气机出口",   T2, P2,     h2, s2),
    ("3", "回热器出口(高)",T3, P3,     h3, s3),
    ("4", "燃气轮机入口", T4, P4,     h4, s4),
    ("5", "燃气轮机出口", T5, P5,     h5, s5),
    ("6", "回热器出口(低)",T6, P6,     h6, s6),
]:
    print(f"{label:<8} {desc:<15} {T:<10.2f} {P:<12.2f} {h:<12.2f} {s:<15.4f}")

print("\n--- 四、循环性能指标 ---")
print(f"  压气机耗功  w_c   = {w_compressor:>8.2f} kJ/kg")
print(f"  燃气轮机做功 w_t  = {w_turbine:>8.2f} kJ/kg")
print(f"  净功        w_net = {w_net:>8.2f} kJ/kg")
print(f"  燃烧室吸热量 q_in = {q_in:>8.2f} kJ/kg")
print(f"  排热量      q_out = {q_out:>8.2f} kJ/kg")
print(f"  背功比      bwr   = {bwr:>8.4f}")
print(f"  ─────────────────────────────────")
print(f"  回热循环热效率 η   = {eta:>8.2f} %")
print(f"  无回热热效率       = {eta_no_regen:>8.2f} %")
print(f"  卡诺效率           = {eta_carnot:>8.2f} %")
print(f"  ─────────────────────────────────")
print(f"  回热使效率提升     = {eta - eta_no_regen:>8.2f} 个百分点")

print("\n--- 五、分析与讨论 ---")
print(f"  1. 回热布雷顿循环效率 ({eta:.2f}%) 比简单布雷顿循环 ({eta_no_regen:.2f}%)")
print(f"     提高了 {eta - eta_no_regen:.2f} 个百分点。")
print(f"  2. 回热器将燃气轮机排气中的 {epsilon*100:.0f}% 可用热量")
print(f"     回收用于预热压气机出口空气，减少了燃烧室所需的燃料输入。")
print(f"  3. 卡诺效率为 {eta_carnot:.2f}%，本循环效率与卡诺效率之比为")
print(f"     {eta/eta_carnot*100:.1f}%。")
print(f"  4. 进一步改进方向：多级压缩中间冷却 + 多级膨胀再热 + 回热，")
print(f"     可使布雷顿循环效率更接近卡诺效率。")
print("=" * 65)

# =====================================================================
# 5. 绘制 T-s 图 (Nature 论文风格)
# =====================================================================

# --- Nature 风格全局设置 ---
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['Helvetica', 'Arial']
rcParams['font.size'] = 6
rcParams['axes.linewidth'] = 0.5      # 坐标轴线宽 0.5 pt
rcParams['xtick.major.width'] = 0.5
rcParams['ytick.major.width'] = 0.5
rcParams['xtick.major.size'] = 2.5    # 刻度线长度 2-3 pt
rcParams['ytick.major.size'] = 2.5
rcParams['xtick.direction'] = 'in'    # 刻度线向内
rcParams['ytick.direction'] = 'in'
rcParams['xtick.minor.visible'] = True
rcParams['ytick.minor.visible'] = True
rcParams['xtick.minor.size'] = 1.5
rcParams['ytick.minor.size'] = 1.5
rcParams['xtick.minor.width'] = 0.4
rcParams['ytick.minor.width'] = 0.4
rcParams['lines.linewidth'] = 0.9
rcParams['axes.labelsize'] = 7        # 坐标轴标题 7 pt
rcParams['xtick.labelsize'] = 5.5     # 刻度标签 5-6 pt
rcParams['ytick.labelsize'] = 5.5
rcParams['legend.fontsize'] = 5.5
rcParams['figure.dpi'] = 300
rcParams['savefig.dpi'] = 300
rcParams['text.usetex'] = False
rcParams['mathtext.default'] = 'regular'

# 中文 fallback 字体
if platform.system() == 'Darwin':
    chinese_font = 'PingFang SC'
elif platform.system() == 'Windows':
    chinese_font = 'SimHei'
else:
    chinese_font = 'WenQuanYi Micro Hei'

# 颜色方案 (Nature 推荐)
COLOR_CYCLE = '#0C5DA5'     # 蓝色 - 循环路径
COLOR_HEAT_IN = '#FF2C00'   # 红色 - 吸热
COLOR_HEAT_OUT = '#00B945'  # 绿色 - 放热
COLOR_REGEN = '#FF9500'     # 橙色 - 回热
COLOR_GRAY = '#888888'      # 灰色

# 图宽：单栏 89 mm = 3.5 inch
fig_width_mm = 89
fig_width_in = fig_width_mm / 25.4
fig_height_in = fig_width_in * 0.85  # 稍窄一点

fig, ax = plt.subplots(figsize=(fig_width_in, fig_height_in))
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# --- 构造各过程的连续路径 ---

def isobar_heating_entropy(T_start, T_end, P, n=80):
    """等压加热/冷却过程的 s(T)"""
    T_arr = np.linspace(T_start, T_end, n)
    s_arr = np.array([entropy(T, P) for T in T_arr])
    return s_arr, T_arr

def isentropic_compress_entropy(T_start, T_end, s_val, n=80):
    """等熵压缩过程"""
    T_arr = np.linspace(T_start, T_end, n)
    s_arr = np.full_like(T_arr, s_val)
    return s_arr, T_arr

def isobar_heating_curve(s_start_T, s_end_T, P, T_const, n=80):
    """等压过程中的等温线段 (用于回热器内部展示)"""
    s_arr = np.linspace(s_start_T, s_end_T, n)
    T_arr = np.full_like(s_arr, T_const)
    return s_arr, T_arr

# 过程 1→2: 等熵压缩 (竖直线)
s_12, T_12 = isentropic_compress_entropy(T1, T2, s1)

# 过程 2→3: 等压加热 (回热器高压侧, P = P2)
s_23, T_23 = isobar_heating_entropy(T2, T3, P2)

# 过程 3→4: 等压加热 (燃烧室, P = P4 = P2)
s_34, T_34 = isobar_heating_entropy(T3, T4, P4)

# 过程 4→5: 等熵膨胀 (竖直线)
s_45, T_45 = isentropic_compress_entropy(T4, T5, s4)

# 过程 5→6: 等压冷却 (回热器低压侧, P = P5 = P1)
s_56, T_56 = isobar_heating_entropy(T5, T6, P5)

# 过程 6→1: 等压冷却 (排气/环境冷却, P = P6 = P1)
s_61, T_61 = isobar_heating_entropy(T6, T1, P6)

# --- 填充循环区域 ---
# 将整个循环的 s 和 T 拼接
s_cycle = np.concatenate([s_12, s_23, s_34, s_45, s_56, s_61])
T_cycle = np.concatenate([T_12, T_23, T_34, T_45, T_56, T_61])
ax.fill(s_cycle, T_cycle, alpha=0.08, color=COLOR_CYCLE, zorder=0)

# --- 绘制各过程曲线 ---
# 1→2 等熵压缩
ax.plot(s_12, T_12, color=COLOR_CYCLE, linewidth=1.0, solid_capstyle='round', zorder=2)
# 2→3 回热器加热 (高压侧)
ax.plot(s_23, T_23, color=COLOR_REGEN, linewidth=0.85, linestyle='--', zorder=2)
# 3→4 燃烧室加热
ax.plot(s_34, T_34, color=COLOR_HEAT_IN, linewidth=1.0, solid_capstyle='round', zorder=2)
# 4→5 等熵膨胀
ax.plot(s_45, T_45, color=COLOR_CYCLE, linewidth=1.0, solid_capstyle='round', zorder=2)
# 5→6 回热器冷却 (低压侧)
ax.plot(s_56, T_56, color=COLOR_REGEN, linewidth=0.85, linestyle='--', zorder=2)
# 6→1 环境冷却
ax.plot(s_61, T_61, color=COLOR_HEAT_OUT, linewidth=1.0, solid_capstyle='round', zorder=2)

# --- 绘制等压参考线 (淡色虚线, 帮助理解) ---
# 高压等压线 P2 延伸 (从 T1 延伸到 T4 范围, 用于对照)
T_ref_high = np.linspace(T2 * 0.95, T4 * 1.02, 100)
s_ref_high = np.array([entropy(T, P2) for T in T_ref_high])
ax.plot(s_ref_high, T_ref_high, color=COLOR_GRAY, linewidth=0.3, linestyle=':', zorder=1)

# 低压等压线 P1 延伸
T_ref_low = np.linspace(T1 * 0.95, T5 * 1.05, 100)
s_ref_low = np.array([entropy(T, P1_val) for T in T_ref_low])
ax.plot(s_ref_low, T_ref_low, color=COLOR_GRAY, linewidth=0.3, linestyle=':', zorder=1)

# --- 标注过程 (曲线旁直接标注，不用图例框) ---
# 先画过程标注，再画状态点标注，保证状态点在最上层

# 等熵压缩
mid_12_s = s1
mid_12_T = (T1 + T2) / 2
ax.annotate('Isentropic\ncompression', (mid_12_s, mid_12_T),
            xytext=(-30, 0), textcoords='offset points',
            fontsize=4.5, color=COLOR_CYCLE, ha='right', va='center',
            style='italic')

# 回热器高压侧
mid_23_s = (s2 + s3) / 2
mid_23_T = (T2 + T3) / 2
ax.annotate('Regenerator\n(high-P)', (mid_23_s, mid_23_T),
            xytext=(0, 12), textcoords='offset points',
            fontsize=4.5, color=COLOR_REGEN, ha='center', va='bottom',
            style='italic')

# 燃烧室
mid_34_s = (s3 + s4) / 2
mid_34_T = (T3 + T4) / 2
ax.annotate('Combustion\nchamber', (mid_34_s, mid_34_T),
            xytext=(25, 0), textcoords='offset points',
            fontsize=4.5, color=COLOR_HEAT_IN, ha='left', va='center',
            style='italic')

# 等熵膨胀
mid_45_s = s4
mid_45_T = (T4 + T5) / 2
ax.annotate('Isentropic\nexpansion', (mid_45_s, mid_45_T),
            xytext=(25, 0), textcoords='offset points',
            fontsize=4.5, color=COLOR_CYCLE, ha='left', va='center',
            style='italic')

# 回热器低压侧 (标注放在曲线中点偏上位置，远离状态点6)
mid_56_s = (s5 + s6) / 2
mid_56_T = (T5 + T6) / 2
ax.annotate('Regenerator\n(low-P)', (mid_56_s, mid_56_T),
            xytext=(0, 12), textcoords='offset points',
            fontsize=4.5, color=COLOR_REGEN, ha='center', va='bottom',
            style='italic')

# 排气冷却
mid_61_s = (s6 + s1) / 2
mid_61_T = (T6 + T1) / 2
ax.annotate('Heat\nrejection', (mid_61_s, mid_61_T),
            xytext=(-18, -8), textcoords='offset points',
            fontsize=4.5, color=COLOR_HEAT_OUT, ha='right', va='center',
            style='italic')

# --- 标注状态点 (最后绘制，保证在最上层) ---
state_points = [
    (s1, T1, "1"),
    (s2, T2, "2"),
    (s3, T3, "3"),
    (s4, T4, "4"),
    (s5, T5, "5"),
    (s6, T6, "6"),
]

for s_pt, T_pt, label in state_points:
    ax.plot(s_pt, T_pt, 'o', markersize=3.5, markeredgecolor='black',
            markeredgewidth=0.5, markerfacecolor='white', zorder=10)
    # 状态点编号偏移量 (避免与曲线/标注重叠)
    offsets = {
        "1": (-10, -10),
        "2": (-10, 10),
        "3": (-10, 10),
        "4": (10, 10),
        "5": (10, -10),
        "6": (12, -12),
    }
    dx, dy = offsets.get(label, (0.05, 20))
    ax.annotate(label, (s_pt, T_pt), xytext=(dx, dy),
                textcoords='offset points', fontsize=6,
                fontweight='bold', ha='center', va='center',
                color='#333333', zorder=10)

# --- 等压参考线标注 ---
# P1 标注
s_p1_label = entropy(T1 * 1.1, P1_val)
ax.annotate('$P_1$', (s_p1_label, T1 * 0.98), fontsize=5, color=COLOR_GRAY,
            ha='left', va='top')
# P2 标注
s_p2_label = entropy(T2 * 0.97, P2)
ax.annotate('$P_2$', (s_p2_label, T2 * 0.96), fontsize=5, color=COLOR_GRAY,
            ha='left', va='bottom')

# --- 坐标轴设置 ---
ax.set_xlabel('Specific entropy, $s$ (kJ kg$^{-1}$ K$^{-1}$)', fontsize=7, labelpad=2)
ax.set_ylabel('Temperature, $T$ (K)', fontsize=7, labelpad=2)

# 坐标范围
s_all = [s1, s2, s3, s4, s5, s6]
s_margin = (max(s_all) - min(s_all)) * 0.12
ax.set_xlim(min(s_all) - s_margin, max(s_all) + s_margin * 1.5)
ax.set_ylim(T1 * 0.82, T4 * 1.06)

# 去掉上边和右边的边框线
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# 不使用网格
ax.grid(False)

# 紧凑布局
plt.tight_layout(pad=0.5)

# --- 保存 ---
output_dir = os.path.dirname(os.path.abspath(__file__))
png_path = os.path.join(output_dir, 'brayton_regenerative_Ts.png')
pdf_path = os.path.join(output_dir, 'brayton_regenerative_Ts.pdf')

fig.savefig(png_path, dpi=300, bbox_inches='tight', facecolor='white')
fig.savefig(pdf_path, bbox_inches='tight', facecolor='white')
print(f"\n图片已保存：")
print(f"  PNG: {png_path}")
print(f"  PDF: {pdf_path}")

plt.close()

# =====================================================================
# 6. 额外：绘制对比图 (回热 vs 无回热)
# =====================================================================
fig2, ax2 = plt.subplots(figsize=(fig_width_in, fig_height_in))
fig2.patch.set_facecolor('white')
ax2.set_facecolor('white')

# 无回热循环路径：1 → 2 → 4 → 5 → 1
# 过程 2→4 (无回热): 等压加热直接到 T4
s_24_noregen, T_24_noregen = isobar_heating_entropy(T2, T4, P2)
# 过程 5→1: 等压冷却
s_51_noregen, T_51_noregen = isobar_heating_entropy(T5, T1, P1_val)

# 填充无回热循环
s_nr = np.concatenate([s_12, s_24_noregen, s_45, s_51_noregen])
T_nr = np.concatenate([T_12, T_24_noregen, T_45, T_51_noregen])
ax2.fill(s_nr, T_nr, alpha=0.06, color=COLOR_GRAY, zorder=0, label='_nolegend_')

# 无回热路径 (灰色实线)
ax2.plot(s_12, T_12, color=COLOR_GRAY, linewidth=0.6, zorder=1)
ax2.plot(s_24_noregen, T_24_noregen, color=COLOR_GRAY, linewidth=0.6, zorder=1)
ax2.plot(s_45, T_45, color=COLOR_GRAY, linewidth=0.6, zorder=1)
ax2.plot(s_51_noregen, T_51_noregen, color=COLOR_GRAY, linewidth=0.6, zorder=1)

# 填充回热循环
ax2.fill(s_cycle, T_cycle, alpha=0.1, color=COLOR_CYCLE, zorder=1, label='_nolegend_')

# 回热循环路径 (蓝色实线 + 橙色虚线)
ax2.plot(s_12, T_12, color=COLOR_CYCLE, linewidth=1.0, zorder=3)
ax2.plot(s_23, T_23, color=COLOR_REGEN, linewidth=0.85, linestyle='--', zorder=3)
ax2.plot(s_34, T_34, color=COLOR_HEAT_IN, linewidth=1.0, zorder=3)
ax2.plot(s_45, T_45, color=COLOR_CYCLE, linewidth=1.0, zorder=3)
ax2.plot(s_56, T_56, color=COLOR_REGEN, linewidth=0.85, linestyle='--', zorder=3)
ax2.plot(s_61, T_61, color=COLOR_HEAT_OUT, linewidth=1.0, zorder=3)

# 标注状态点
for s_pt, T_pt, label in state_points:
    ax2.plot(s_pt, T_pt, 'o', markersize=3.5, markeredgecolor='black',
            markeredgewidth=0.5, markerfacecolor='white', zorder=5)
    dx, dy = offsets.get(label, (0.05, 20))
    ax2.annotate(label, (s_pt, T_pt), xytext=(dx, dy),
                textcoords='offset points', fontsize=6,
                fontweight='bold', ha='center', va='center',
                color='#333333')

# 标注无回热的额外点
# 状态 2' = 状态 2 (重合), 状态 4' = 状态 4 (重合)
# 只标注 "simple" 和 "regenerative"
ax2.annotate('Simple cycle', (entropy(T2 + 100, P2), T2 + 100),
            fontsize=4.5, color=COLOR_GRAY, style='italic', ha='left')
ax2.annotate('Regenerative cycle', (entropy(T3, P2), T3 - 60),
            fontsize=4.5, color=COLOR_CYCLE, style='italic', ha='center')

# 等压参考线
ax2.plot(s_ref_high, T_ref_high, color=COLOR_GRAY, linewidth=0.3, linestyle=':', zorder=1)
ax2.plot(s_ref_low, T_ref_low, color=COLOR_GRAY, linewidth=0.3, linestyle=':', zorder=1)

ax2.set_xlabel('Specific entropy, $s$ (kJ kg$^{-1}$ K$^{-1}$)', fontsize=7, labelpad=2)
ax2.set_ylabel('Temperature, $T$ (K)', fontsize=7, labelpad=2)

ax2.set_xlim(min(s_all) - s_margin, max(s_all) + s_margin * 1.5)
ax2.set_ylim(T1 * 0.82, T4 * 1.06)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.grid(False)

plt.tight_layout(pad=0.5)

png_path2 = os.path.join(output_dir, 'brayton_comparison_Ts.png')
pdf_path2 = os.path.join(output_dir, 'brayton_comparison_Ts.pdf')
fig2.savefig(png_path2, dpi=300, bbox_inches='tight', facecolor='white')
fig2.savefig(pdf_path2, bbox_inches='tight', facecolor='white')
print(f"\n对比图已保存：")
print(f"  PNG: {png_path2}")
print(f"  PDF: {pdf_path2}")
plt.close()

print("\n全部完成。")
