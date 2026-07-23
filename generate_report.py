# -*- coding: utf-8 -*-
"""《开源螺杆泵井神经网络计产模型调研报告》"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

ACCENT = RGBColor(0x1F, 0x4E, 0x79)
GRAY = RGBColor(0x66, 0x66, 0x66)
RED = RGBColor(0xC0, 0x39, 0x2B)


def set_cn_font(run, name_cn="宋体", name_en="Calibri", size=None, bold=None, color=None):
    run.font.name = name_en
    r = run._element.rPr.rFonts
    r.set(qn("w:eastAsia"), name_cn)
    if size:
        run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color


def add_heading(doc, text, level=1):
    h = doc.add_heading("", level=level)
    run = h.add_run(text)
    sizes = {1: 16, 2: 13, 3: 12}
    set_cn_font(run, name_cn="黑体", size=sizes.get(level, 12), bold=True, color=ACCENT)
    return h


def add_para(doc, text, bold=False, size=10.5, indent=True, color=None):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_cn_font(run, size=size, bold=bold, color=color)
    return p


def add_overview(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run("【本章概述】")
    set_cn_font(run, name_cn="黑体", size=10.5, bold=True, color=ACCENT)
    run = p.add_run(text)
    set_cn_font(run, size=10.5)
    return p


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(4)
    if bold_prefix:
        run = p.add_run(bold_prefix)
        set_cn_font(run, size=10.5, bold=True)
    run = p.add_run(text)
    set_cn_font(run, size=10.5)
    return p


def add_table(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = ""
        run = hdr[i].paragraphs[0].add_run(h)
        set_cn_font(run, name_cn="黑体", size=10.5, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(val)
            set_cn_font(run, size=10)
    if widths:
        for i, w in enumerate(widths):
            for row in table.rows:
                row.cells[i].width = Cm(w)
    doc.add_paragraph()
    return table


doc = Document()
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

# ========== 封面 ==========
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("开源螺杆泵井神经网络计产模型\n调研报告")
set_cn_font(run, name_cn="黑体", size=22, bold=True, color=ACCENT)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("核心问题：有没有开源的螺杆泵井神经网络计产模型？\n"
                  "结论 · 最接近的开源替代 · 机理辅助三模型 · 自建路径")
set_cn_font(run, size=12, color=GRAY)

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_p.add_run("2026 年 7 月（文件名：开源螺杆泵井神经网络计产模型调研报告.docx）")
set_cn_font(run, size=10.5, color=GRAY)
doc.add_paragraph()

# ========== 第一章：核心结论 ==========
add_heading(doc, "一、核心结论（请先读这一章）", 1)
add_overview(doc, "本章直接回答你要的东西：开源的「螺杆泵井神经网络计产模型」有没有。"
                  "结论写在最前面，避免再被其他资料冲淡。")

add_para(doc, "结论：截至本报告检索日，公开渠道（GitHub / PyPI / 论文配套代码）中，"
              "没有发现专门针对螺杆泵（PCP）井、以神经网络做实时产量计量（虚拟计量）的"
              "开源成品模型（即：输入泵转速/扭矩/电流等 → 输出当前油/液产量，"
              "且提供可训练代码与说明的项目）。", bold=True, color=RED)

add_para(doc, "检索范围包括英文关键词 progressive cavity pump / PCP + neural / LSTM / "
              "machine learning / virtual flow meter / soft sensor / flow rate / metering，"
              "以及中文关键词「螺杆泵」「计产」「产量」「神经网络」。"
              "与螺杆泵相关的开源项目存在，但用途是资产管理、几何设计、故障诊断，"
              "不是神经网络计产。与「人工举升 + 神经网络」最接近的开源是电潜泵（ESP）"
              "数字孪生，可作结构参考，仍不是螺杆泵计产。")

add_heading(doc, "1.1 检索到的螺杆泵相关开源（均非神经网络计产）", 2)
add_table(
    doc,
    ["项目", "地址", "实际做什么", "是否计产NN"],
    [
        ["pump_ai_software（螺杆泵AI软件）",
         "github.com/xiansurfer/pump_ai_software",
         "宏观控制图（扭矩/泵效）、故障预警、生存分析；国内油田电泵/螺杆泵故障数据",
         "否（故障诊断，非产量计量）"],
        ["ScrewPumpCalculator",
         "github.com/aiguoli/ScrewPumpCalculator",
         "螺杆泵参数计算与型线设计（SolidWorks 二次开发）",
         "否（几何设计）"],
        ["PCP-Tracker-Project",
         "github.com/Mabubakr86/PCP-Tracker-Project",
         "螺杆泵资产跟踪桌面应用",
         "否（资产管理）"],
        ["progressive-cavity-pump（OpenSCAD）",
         "github.com/Rmurthy1/progressive-cavity-pump",
         "泵三维几何建模",
         "否"],
        ["accapumps/progressive-cavity-pumps",
         "github.com/accapumps/progressive-cavity-pumps",
         "泵研究资料仓库",
         "否"],
    ],
    widths=[3.8, 4.8, 5.0, 2.4],
)

add_heading(doc, "1.2 最接近、可迁移的开源神经网络（需改特征后自训）", 2)
add_para(doc, "以下项目是「通用虚拟计量 / 工况→产量」神经网络开源实现。"
              "它们不是螺杆泵专用，但代码完整，把输入从油嘴/井口压温改成"
              "转速、扭矩、电流、沉没度等泵参数，用本井试井产量做标签，即可做成螺杆泵井计产模型。"
              "这是目前落地的现实路径。", bold=True)
add_table(
    doc,
    ["优先级", "项目", "地址", "原任务", "如何改成螺杆泵井计产"],
    [
        ["首选", "LSTM-for-Production",
         "github.com/saifkhanengr/LSTM-for-Production",
         "Volve：井下/井口压温、油嘴 → 油气水产量",
         "删油嘴特征；加入转速、扭矩/电流、沉没度；标签换成本井试井产量"],
        ["推荐", "HVFM（TCN/MPFNet）",
         "github.com/mmmahhhhe/HVFM\npip install HVFM",
         "机理+数据双驱动瞬态多相 VFM",
         "保留 TCN 结构；机理部分换成「理论排量−滑脱」泵公式"],
        ["推荐", "VFM (Andrianov)",
         "github.com/nikolai-andrianov/VFM",
         "IFAC 论文配套 NN 估产 + 数据集",
         "沿用训练管线；特征与标签换为泵工况与试井产量"],
        ["参考", "ManyWells ml_examples",
         "github.com/solution-seeker-as/manywells",
         "NTNU 官方 NN VFM 基准示例",
         "练网络对比方法；数据为仿真井筒，无泵"],
        ["参考", "pi-vfm / Hybrid_VFM_Slugging",
         "CryptoGuy1/pi-vfm\ncaioazevedo-mdm/Hybrid_VFM_Slugging",
         "PINN / 扩散增广 VFM",
         "可把泵排量守恒写入物理损失"],
        ["近邻（ESP）", "ESP Digital Twin",
         "github.com/abhi133113/Artificial-lift-ESP-Autonomous",
         "电潜泵：LSTM 预测 + 异常检测 + 泵曲线物理校验",
         "人工举升 NN 最接近；任务偏预测/故障，需改成「当前产量」回归"],
    ],
    widths=[1.6, 2.8, 4.2, 3.4, 4.0],
)

add_heading(doc, "1.3 为什么几乎没有开源螺杆泵计产 NN", 2)
add_bullet(doc, "计产模型必须用本井试井/流量计数据训练，公开预训练权重没有通用价值；")
add_bullet(doc, "螺杆泵井运行数据多为油田内部数据，几乎不公开；")
add_bullet(doc, "工业虚拟计量产品（含人工举升）全部闭源；")
add_bullet(doc, "学术上螺杆泵相关公开工作更多是特性曲线解析模型、CFD、故障诊断，而非开源计产 NN。")

# ========== 第二章：计产定义与机理流程 ==========
add_heading(doc, "二、螺杆泵井计产定义与机理计产流程", 1)
add_overview(doc, "在动手改开源 NN 之前，必须先弄清「计产」在螺杆泵井上意味着什么，"
                  "以及机理法如何用三个辅助模型算出产量。神经网络计产是在学同一条映射。")

add_heading(doc, "2.1 计产 vs 产量预测（不要搞混）", 2)
add_table(
    doc,
    ["", "计产（本报告目标）", "产量预测（不是目标）"],
    [
        ["问题", "这口井现在产多少？", "未来一周/一月产多少？"],
        ["输入", "当前泵工况（转速、扭矩、电流、压温…）", "历史产量序列"],
        ["输出", "当前油/液产量", "未来产量"],
        ["用途", "替代/补充流量计、试井间隔内连续计量", "产量规划、递减分析"],
    ],
    widths=[2.4, 6.8, 6.8],
)

add_heading(doc, "2.2 螺杆泵井为什么不能用油嘴计产模型", 2)
add_para(doc, "自喷井产量主要由油嘴控制，信息源是油嘴尺寸与压差；"
              "螺杆泵井产量由泵控制，井口通常无可调油嘴，信息源是转速、扭矩/电流与泵两端压差。"
              "油嘴 NN/经验式对螺杆泵井不直接适用。")

add_heading(doc, "2.3 机理计产概论：一条流动链 + 三个辅助模型", 2)
add_para(doc, "流动路径：地层 → 泵吸入口 → 螺杆泵（增压）→ 油管井筒 → 井口 → 地面。"
              "稳态时各段流量相同、压力在接点连续。把各段「压力–流量」约束联立求解，"
              "得到的工作点流量就是产量。三个辅助模型分工如下：")
add_table(
    doc,
    ["辅助模型", "管哪一段", "输入 → 输出", "在计产中的作用"],
    [
        ["螺杆泵运行特性模型（核心）",
         "泵段",
         "转速、泵压差、黏度、泵几何 → 实际排量、扭矩",
         "直接给出产量：Q = Q理论 − Q滑脱；是「计量元件」"],
        ["井筒流体运移模型（辅助）",
         "泵出口→井口油管（及环空液柱）",
         "流量、边界压力、管径井斜、PVT → 沿程压力/温度/持液率",
         "算出泵出口压力或回压，从而得到泵压差"],
        ["井筒流体摩阻计算模型（辅助）",
         "运移模型内部的摩阻压降项",
         "流速、管径、粗糙度、物性 → ΔP摩阻",
         "运移模型的组成部分，影响泵压差精度"],
    ],
    widths=[3.4, 3.0, 5.0, 4.6],
)

add_heading(doc, "2.4 机理计产求解流程（六步）", 2)
add_para(doc, "已知转速与井口压力、求产量时：")
add_para(doc, "① 准备：泵几何、转速、井口油压、流体物性、井身与泵挂深度。"
              "② 假设试探产量 Q。"
              "③ 井筒运移（内含摩阻）从井口积分到泵出口 → P_out；结合吸入口压力或动液面得 P_in；"
              "泵压差 ΔP = P_out − P_in。"
              "④ 泵特性：Q_th = C×转速；Q_slip = f(ΔP, 黏度, 间隙…)；Q_pump = Q_th − Q_slip。"
              "⑤ 比较 Q_pump 与假设 Q，不一致则修正假设，回到③；一致则该 Q 为产量。"
              "⑥（可选）用 IPR 校核泵吸入口压力与地层供液是否匹配。")
add_para(doc, "神经网络计产学的就是「转速、扭矩/电流、井口压、沉没度… → Q」这条映射；"
              "混合结构则固定 Q_th = C×n，只让网络学 Q_slip。")

# ========== 第三章：三辅助模型开源 ==========
add_heading(doc, "三、三个辅助模型的开源实现（服务计产，不是计产 NN 本身）", 1)
add_overview(doc, "本章是辅线。井筒运移/摩阻有成熟开源库，可用来算泵压差特征；"
                  "泵特性目前没有开源代码，只有论文公式需自写。"
                  "它们不能替代神经网络计产，但可嵌入混合模型。")

add_heading(doc, "3.1 井筒流体运移模型", 2)
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["marlim3", "github.com/petrobras/marlim3\npip install marlim3",
         "Petrobras 1D 瞬态多相流模拟器（生产井/管网/热耦合）"],
        ["ManyWells", "github.com/solution-seeker-as/manywells",
         "Python 稳态漂移流井筒模拟器 + 百万点基准数据"],
        ["NeqSim TransientPipe", "github.com/equinor/neqsim",
         "瞬态漂移流 + 流型判别 + 段塞追踪 + EOS 闪蒸"],
    ],
    widths=[3.2, 5.4, 7.4],
)

add_heading(doc, "3.2 井筒流体摩阻计算模型", 2)
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["flotech", "pip install flotech",
         "Beggs & Brill、Duns & Ros、Ansari、Gray 等压降关联式 + PVT + IPR"],
        ["pyResToolbox", "github.com/mwburgoyne/pyResToolbox",
         "VLP（含 Hagedorn–Brown 等）+ 节点分析 + Eclipse VFP 表"],
        ["petropt / fluids", "github.com/petropt/petropt\ngithub.com/CalebBell/fluids",
         "Beggs–Brill、Darcy–Weisbach、多种摩阻系数"],
    ],
    widths=[3.2, 5.4, 7.4],
)

add_heading(doc, "3.3 螺杆泵运行特性模型（无开源成品，论文自写）", 2)
add_para(doc, "核心公式：实际排量 = 理论排量 − 滑脱量；Q_th = C × 转速。"
              "开源现状：无现成库。可自写的论文：")
add_bullet(doc, "Gamboa 逐腔室质量平衡 / COBEM 2009 简化模型（推荐实现起点）；")
add_bullet(doc, "金属定子间隙滑脱解析模型（Math. Problems in Eng., 2018, DOI:10.1155/2018/3696930）；")
add_bullet(doc, "井下定子变形耦合模型（J. Pet. Sci. Eng., 2020）。")

# ========== 第四章：如何自建 ==========
add_heading(doc, "四、螺杆泵井神经网络计产：自建路径（主路径）", 1)
add_overview(doc, "既然没有成品开源，本章给出可执行的自建方案：特征集、两种网络结构、"
                  "改哪些开源仓库、训练与验证步骤。这是你真正要落地时应跟随的章节。")

add_heading(doc, "4.1 特征集（不要油嘴开度）", 2)
add_table(
    doc,
    ["优先级", "特征", "物理含义"],
    [
        ["必需", "泵转速 / 电机频率", "决定理论排量"],
        ["必需", "扭矩或电流 / 有功功率", "编码泵压差与负荷、间接反映滑脱"],
        ["必需", "井口油压、回压", "泵出口侧边界"],
        ["强烈建议", "泵吸入口压力或动液面", "与出口侧共同定 ΔP"],
        ["建议", "井口温度、含水率", "黏度与油/液拆分"],
        ["可选", "泵累计运行时长", "定子磨损漂移"],
    ],
    widths=[2.4, 5.0, 8.6],
)
add_para(doc, "标签：试井油/液产量，或翻斗/质量流量计连续计量。"
              "样本须覆盖多转速、多回压，否则外推失败。")

add_heading(doc, "4.2 两种结构", 2)
add_para(doc, "结构 A（纯数据驱动）：特征 → MLP/LSTM/TCN → 产量。实现快，极端工况可能不合理。")
add_para(doc, "结构 B（推荐，机理+NN）：Q = C×转速 − NN(转速, 扭矩/电流, ΔP或压温沉没度, …)。"
              "ΔP 可用第三章井筒模型算，或用吸入口压力传感器。"
              "理论排量物理正确，网络只学滑脱，调转速时更稳。")

add_heading(doc, "4.3 推荐改造步骤", 2)
add_para(doc, "① 克隆 LSTM-for-Production，跑通 Volve 示例弄清管线。"
              "② 换成自有数据表，特征按 4.1，标签用试井产量；按时间切分训练/测试。"
              "③ 先 XGBoost 基线，再 LSTM/MLP；有条件上结构 B。"
              "④ 需要更强时序时，把网络换成 HVFM 的 TCN。"
              "⑤ 用后期试井盲测；关注调转速前后是否跟得上；按季度用新试井微调防磨损漂移。")

add_heading(doc, "4.4 可参考但非开源代码的论文", 2)
add_bullet(doc, "ESP 井 LSTM 流量估计（Energies 2025）：输入功率、频率、压力，与螺杆泵井输入同构；")
add_bullet(doc, "NTNU 贝叶斯 NN VFM、Bikmukhametov 博士论文、WISE 基础模型：方法可借鉴，无 PCP 专用开源。")

# ========== 第五章：选型清单 ==========
add_heading(doc, "五、选型清单（针对你的螺杆泵井）", 1)
add_overview(doc, "一页纸结论：要什么、不要指望什么、立刻做什么。")
add_para(doc, "要找的「开源螺杆泵井神经网络计产成品」：目前没有。", bold=True, color=RED)
add_para(doc, "立刻可做：", bold=True)
add_bullet(doc, "计产 NN 代码骨架：改 LSTM-for-Production / HVFM（第一章表）；")
add_bullet(doc, "泵压差特征：flotech 或 marlim3（第三章）；")
add_bullet(doc, "泵理论排量与滑脱：自写解析式 + 试井标定（第三章 3.3）；")
add_bullet(doc, "训练数据：必须用本油田螺杆泵井试井与泵运行数据（无公开同类数据集）。")
add_para(doc, "不要做：把油嘴计产 NN 或「历史产量时序预测」项目直接当螺杆泵井计产用。")

doc.save("/workspace/开源螺杆泵井神经网络计产模型调研报告.docx")
print("saved new name")

# 同步覆盖旧文件名，并删除易混淆的旧内容说明
import shutil
shutil.copy(
    "/workspace/开源螺杆泵井神经网络计产模型调研报告.docx",
    "/workspace/油田计产神经网络模型开源资源调研报告.docx",
)
print("also updated old filename")
