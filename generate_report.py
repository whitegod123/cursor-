# -*- coding: utf-8 -*-
"""《螺杆泵井计产模型调研报告》——以螺杆泵井为主，三模型为辅。"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


ACCENT = RGBColor(0x1F, 0x4E, 0x79)
GRAY = RGBColor(0x66, 0x66, 0x66)


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


def add_para(doc, text, bold=False, size=10.5, indent=True):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_cn_font(run, size=size, bold=bold)
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

# ======================== 封面 ========================
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("螺杆泵井计产模型调研报告")
set_cn_font(run, name_cn="黑体", size=22, bold=True, color=ACCENT)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("——以螺杆泵井计产为主线，井筒运移 / 井筒摩阻 / 泵特性模型为辅\n"
                  "机理计产流程 · 神经网络虚拟计量 · 开源资源与论文")
set_cn_font(run, size=12, color=GRAY)

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_p.add_run("2026 年 7 月")
set_cn_font(run, size=10.5, color=GRAY)
doc.add_paragraph()

# ======================== 一、总论 ========================
add_heading(doc, "一、总论：本报告回答什么问题", 1)
add_overview(doc, "本章是全文总纲。说明“计产”是什么、螺杆泵井为什么要单独建模、"
                  "本报告以什么为主线、三个辅助模型各自起什么作用。读完本章即可把握全文结构。")

add_heading(doc, "1.1 计产是什么", 2)
add_para(doc, "计产（产量计量）回答的问题是：“这口井现在产多少油/液？”"
              "传统做法依赖多相流量计（MPFM）或定期试井（投分离器），前者昂贵、后者"
              "只能拿到离散点。虚拟计量（Virtual Flow Metering，VFM）用井上已有传感器"
              "的实时工况参数，通过数学模型连续估算出产量，作为流量计的替代或补充。")
add_para(doc, "计产与“产量预测”不是一回事：计产用当前工况反算当前产量（替代流量计）；"
              "产量预测用历史产量外推未来产量（产量规划）。本报告只讨论计产。")

add_heading(doc, "1.2 为什么螺杆泵井要单独建计产模型", 2)
add_para(doc, "自喷井/气举井的产量主要由井口油嘴控制，计产信息源是油嘴尺寸与油嘴前后压差；"
              "螺杆泵（Progressive Cavity Pump，PCP）井的产量由泵控制，井口通常没有可调油嘴，"
              "计产信息源是泵的运行参数（转速、扭矩、电流）以及泵两端压差。把自喷井的油嘴"
              "计产模型直接套到螺杆泵井上是错误的，必须按泵的工作原理重新组织。")

add_heading(doc, "1.3 本报告的主线与辅线", 2)
add_para(doc, "主线：螺杆泵井的计产——既包括“机理计产”（把井筒与泵的物理模型串联求解），"
              "也包括“神经网络计产”（用数据直接学出工况→产量的映射），以及二者的混合。"
              "辅线：以下三个子模型，它们是机理计产链条上的必要部件，神经网络计产时则"
              "作为特征工程和物理约束的来源：")
add_table(
    doc,
    ["辅助模型", "在螺杆泵井计产中的作用"],
    [
        ["井筒流体运移模型",
         "描述井筒内多相流的整体行为（持液率、滑脱、流型、瞬态），"
         "给出井筒沿程压力/温度剖面的总框架，用于计算泵吸入口压力与泵压差"],
        ["井筒流体摩阻计算模型",
         "井筒压降三项（重力、摩阻、加速度）中的摩阻项，是运移模型的组成部分；"
         "直接影响泵出口到井口这一段的回压计算"],
        ["螺杆泵运行特性模型",
         "泵段的“转速–压差–排量”关系（理论排量 − 滑脱量）；"
         "螺杆泵井计产的核心子模型，产量信息的主要来源"],
    ],
    widths=[4.0, 12.0],
)
add_para(doc, "全文结构：第二章讲清机理计产的完整流程；第三章分别展开三个辅助模型的开源"
              "实现与论文；第四章讲神经网络计产如何在螺杆泵井上落地；第五章汇总可参考的"
              "公开数据集与选型建议。")

# ======================== 二、机理计产流程 ========================
add_heading(doc, "二、螺杆泵井机理计产模型：流程与概论", 1)
add_overview(doc, "本章是全文的核心理论章。先给出一口螺杆泵井从井底到地面的流动链条，"
                  "再说明机理计产如何把三个辅助模型串联起来求解出产量，最后给出分步计算流程。"
                  "读完本章，应能画出“输入什么、经过哪些模型、得到什么输出”的完整图景。")

add_heading(doc, "2.1 流动链条：流体从哪里到哪里", 2)
add_para(doc, "一口螺杆泵井的流体路径如下：", bold=True)
add_para(doc, "地层（供液）→ 井底（泵吸入口）→ 螺杆泵（增压）→ 泵出口以上油管（井筒举升）"
              "→ 井口 → 地面管线 / 计量装置。")
add_para(doc, "每一段都有自己的“压力–流量”约束：地层供液能力由流入动态（IPR）描述；"
              "泵段由螺杆泵运行特性描述；泵出口到井口由井筒流体运移模型（含摩阻计算）描述。"
              "稳态时，流过每一段的质量流量相同，压力在连接点连续。把这些约束联立求解，"
              "得到的那个“流量–压力工作点”，就是该井当前的产量。这就是机理计产的本质。")

add_heading(doc, "2.2 三个辅助模型各自管哪一段", 2)
add_table(
    doc,
    ["模型", "覆盖的物理段", "输入", "输出", "与产量的关系"],
    [
        ["螺杆泵运行特性模型",
         "泵段（转子–定子密封腔）",
         "转速、泵压差、流体黏度、泵几何（转子直径、偏心距、导程、级数）",
         "实际排量（= 理论排量 − 滑脱量）、扭矩",
         "直接给出产量；是计产的“计量元件”"],
        ["井筒流体运移模型",
         "泵出口 → 井口的油管段（也可含泵以下环空到动液面）",
         "流量、入口压力/温度、井斜、管径、流体物性（PVT）",
         "沿程压力剖面、温度剖面、持液率、流型",
         "给出泵出口压力（或回压），进而确定泵压差"],
        ["井筒流体摩阻计算模型",
         "同上油管段中的摩阻压降项",
         "流速、管径、粗糙度、流体密度/黏度、流型",
         "摩阻压降 ΔP_f",
         "运移模型压降计算的组成部分；影响泵压差"],
    ],
    widths=[3.2, 3.4, 3.4, 3.0, 3.0],
)
add_para(doc, "三者关系一句话：运移模型是井筒段的总框架，摩阻模型是运移模型内部的一个"
              "计算模块，泵特性模型是链条上独立的增压环节。计产时三者必须一起用，"
              "不能只用其中一个。")

add_heading(doc, "2.3 机理计产的求解流程（分步）", 2)
add_para(doc, "稳态节点分析（Nodal Analysis）是机理计产的标准算法。以“已知转速与井口压力、"
              "求产量”这一最常见工况为例，流程如下：")
add_para(doc, "步骤 1 —— 准备输入。泵几何参数（转子直径、偏心距、导程、级数、定子类型）；"
              "当前转速；井口油压（回压）；流体物性（原油密度、黏度、含水、气油比，来自"
              "PVT 化验或在线含水仪）；井身数据（管径、井斜、泵挂深度）。")
add_para(doc, "步骤 2 —— 假设一个试探产量 Q。")
add_para(doc, "步骤 3 —— 用井筒流体运移模型（内部调用摩阻计算）从井口往下算到泵出口："
              "以井口压力为边界、流量为 Q，积分得到泵出口压力 P_out；若有动液面或泵吸入口"
              "压力传感器，可直接读到泵入口压力 P_in，否则还需用环空液柱模型估算 P_in。"
              "泵压差 ΔP = P_out − P_in。")
add_para(doc, "步骤 4 —— 用螺杆泵运行特性模型：由转速算出理论排量 Q_th；由 ΔP、黏度、"
              "间隙算出滑脱量 Q_slip；得到泵实际排量 Q_pump = Q_th − Q_slip。")
add_para(doc, "步骤 5 —— 比较 Q_pump 与假设的 Q。若不一致，按差值修正假设流量，回到步骤 3；"
              "一致时，该 Q 即为当前产量。")
add_para(doc, "步骤 6 ——（可选）用流入动态（IPR）校核：泵吸入口压力对应的地层供液能力"
              "应与 Q 匹配；不匹配说明动液面假设或 IPR 参数需调整。")
add_para(doc, "上述迭代在商业软件（PIPESIM、Prosper）里自动完成；开源环境下可用"
              "flotech/marlim3 做步骤 3，自己实现步骤 4 的泵特性公式（见第三章）。")

add_heading(doc, "2.4 机理计产的优缺点，以及为何还要神经网络", 2)
add_para(doc, "优点：物理可解释、不依赖大量历史数据、参数变化（换泵、调转速）后仍可用。"
              "缺点：①泵滑脱模型对定子磨损、温度引起的间隙变化敏感，需定期用试井标定；"
              "②井筒多相流关联式在复杂流型下误差大；③流体物性（尤其黏度）测不准会系统性"
              "偏置产量。神经网络计产的价值，正是用现场试井数据“吃掉”这些机理模型难以"
              "精确刻画的部分——既可以完全数据驱动，也可以做成“机理算理论排量、网络学"
              "滑脱量”的混合结构（见第四章）。")

# ======================== 三、三个辅助模型 ========================
add_heading(doc, "三、三个辅助模型：开源实现与论文", 1)
add_overview(doc, "本章展开三个辅助模型本身：每个模型的物理含义、开源库/代码、关键论文。"
                  "它们是第二章流程中步骤 3、步骤 4 的具体工具。选型时：井筒段优先用现成"
                  "开源库；泵特性段目前没有开源代码，需按论文公式自行实现。")

# --- 3.1 井筒运移 ---
add_heading(doc, "3.1 井筒流体运移模型", 2)
add_para(doc, "物理含义：描述气–油–水在油管内如何流动——持液率（液体占截面多少）、"
              "相间滑脱、流型（泡状/段塞/环状等）、以及瞬态工况下的液塞运移与压力波。"
              "稳态下给出沿程压力剖面；瞬态下还能模拟启停井、段塞等动态过程。"
              "在螺杆泵井计产中，它的主要用途是：从井口压力推算泵出口压力（或反过来），"
              "从而得到泵压差。")
add_para(doc, "开源实现：", bold=True)
add_table(
    doc,
    ["项目", "地址", "能力", "适用场景"],
    [
        ["marlim3", "github.com/petrobras/marlim3\npip install marlim3",
         "Petrobras 开源的 1D 瞬态多相流模拟器；支持生产井/注入井/管网、气举、组分流体、"
         "热传导耦合；有 Python 包与独立可执行文件",
         "需要瞬态、段塞或较完整工艺模拟时首选"],
        ["ManyWells", "github.com/solution-seeker-as/manywells",
         "纯 Python 稳态漂移流（drift-flux）井筒模拟器；油水作为混合液相；"
         "含流入模型与油嘴模型边界；代码清晰，附 100 万点基准数据",
         "稳态计产、批量生成训练数据、学习算法"],
        ["NeqSim TransientPipe", "github.com/equinor/neqsim",
         "1D 瞬态气液两/三相；Zuber-Findlay 漂移流 + Taitel-Dukler/Barnea 流型判别；"
         "地形段塞、拉格朗日段塞追踪；与 SRK/PR 状态方程闪蒸耦合",
         "需要与热力学闪蒸紧耦合的瞬态分析"],
        ["co2-wellbore", "github.com/TeaAndFlow/co2-wellbore",
         "CO₂ 注入井压力/温度剖面（CoolProp + 简化漂移流）",
         "CCUS 场景；采油井可参考其结构"],
    ],
    widths=[2.8, 4.4, 5.4, 3.4],
)

# --- 3.2 井筒摩阻 ---
add_heading(doc, "3.2 井筒流体摩阻计算模型", 2)
add_para(doc, "物理含义：井筒总压降 = 重力压降 + 摩阻压降 + 加速度压降。摩阻模型专门"
              "计算其中的摩阻项，核心是摩阻系数关联式（单相：Darcy–Weisbach + Churchill/"
              "Colebrook；多相：按流型选用 Beggs & Brill、Hagedorn–Brown、Duns & Ros、"
              "Ansari 等）。它通常不单独对外使用，而是作为运移模型内部的一个模块被调用；"
              "但在工程上常单独拿出来做 VLP（垂直举升性能）曲线。")
add_para(doc, "开源实现：", bold=True)
add_table(
    doc,
    ["项目", "地址", "能力"],
    [
        ["flotech", "github.com/Nashat90/flotech\npip install flotech",
         "专门的多相流压降关联式库：Beggs & Brill、Duns & Ros、Ansari、Mukherjee & Brill、"
         "Gray、Fancher & Brown、Aziz & Govier 等；含 PVT 物性与 Vogel IPR；"
         "可直接算井筒沿程压力剖面并对比不同关联式"],
        ["pyResToolbox", "github.com/mwburgoyne/pyResToolbox",
         "4 种 VLP（Hagedorn–Brown、Beggs & Brill、Gray、Woldesemayat–Ghajar）+ IPR +"
         "节点分析；支持斜井/水平井多段；可生成 Eclipse VFPPROD 举升曲线表；有 Rust 加速"],
        ["petropt", "github.com/petropt/petropt（MIT）",
         "石油工程综合库：Beggs–Brill 全流型任意井斜压力梯度、Darcy–Weisbach + Churchill "
         "摩阻系数、PVT、IPR、递减曲线等"],
        ["fluids", "github.com/CalebBell/fluids",
         "通用流体力学库：几十种单相摩阻系数关联式 + 两相压降计算，工程底层常用"],
    ],
    widths=[2.8, 5.4, 7.8],
)
add_para(doc, "在螺杆泵井计产中的用法：步骤 3 从井口往下积分时，每个微元段的摩阻压降由"
              "上述库中的关联式计算；稠油/高含水井建议对比 Beggs & Brill 与 Hagedorn–Brown"
              "两种结果，选与试井压降匹配更好的一种。")

# --- 3.3 螺杆泵特性 ---
add_heading(doc, "3.3 螺杆泵运行特性模型", 2)
add_para(doc, "物理含义：螺杆泵是容积泵。理论排量由几何与转速唯一确定："
              "Q_th = C × n（C 由转子直径、偏心距、导程决定）。实际排量 = 理论排量 − 滑脱量。"
              "滑脱是高压腔向低压腔的内部回流，发生在定转子密封线上，主要受泵压差、"
              "间隙（或过盈）、流体黏度、定子橡胶变形影响。特性模型的任务就是在给定转速与"
              "泵压差时，算出实际排量和轴功率/扭矩。")
add_para(doc, "开源现状：目前没有现成的开源螺杆泵特性代码库，工业实现都在商业举升软件"
              "（PIPESIM PCP 模块、Prosper 等）内部。公开资源是论文中的解析模型，公式完整，"
              "可自行用几百行 Python 实现。", bold=True)
add_table(
    doc,
    ["模型/论文", "年份", "要点", "适用"],
    [
        ["Gamboa et al. 逐腔室质量平衡模型；COBEM 2009 简化版给出完整公式与求解流程",
         "2003 / 2009",
         "把滑脱分解为横向密封线与纵向密封线两个分量；对每个腔室建质量平衡方程组，"
         "Gauss–Seidel 求解腔室压力后再累加总滑脱",
         "通用单头/多头；实现难度中等，推荐作为自写代码的起点"],
        ["金属定子 PCP 间隙配合滑脱解析模型（Math. Problems in Eng., DOI:10.1155/2018/3696930）",
         "2018",
         "针对金属定子间隙配合；分别计算压差驱动滑脱与相对运动驱动滑脱；"
         "用国产实红石油装备泵做了实验验证",
         "金属定子泵"],
        ["井下工况定子变形耦合模型（J. Pet. Sci. Eng., 2020）",
         "2020",
         "Hooke 定律 + 复合圆筒理论算定子橡胶变形 → 动态间隙；"
         "耦合到表面工况特性曲线；适用多头螺杆泵",
         "橡胶定子、需考虑井下温度/压力变形时"],
    ],
    widths=[5.6, 1.8, 5.4, 3.2],
)
add_para(doc, "实现建议：先按 COBEM 2009 简化模型写出“转速、ΔP、黏度 → Q_pump”函数；"
              "用厂家特性曲线或本井试井点标定间隙等经验参数；橡胶定子井再按 2020 论文加"
              "变形修正。标定后的泵特性函数即可嵌入第二章的步骤 4。")

# ======================== 四、神经网络计产 ========================
add_heading(doc, "四、螺杆泵井的神经网络计产（虚拟计量）", 1)
add_overview(doc, "本章讲如何用神经网络做螺杆泵井计产。核心思路：让网络直接学习"
                  "“泵运行参数 + 井口工况 → 产量”的映射，用试井/流量计数据训练。"
                  "可做成纯数据驱动，也可做成“机理算理论排量、网络学滑脱量”的混合结构。"
                  "开源的神经网络计产实现大多针对自喷井，但结构可迁移；本章给出特征集、"
                  "可借鉴的开源项目、以及落地步骤。")

add_heading(doc, "4.1 为什么神经网络适合螺杆泵井计产", 2)
add_para(doc, "机理计产的薄弱环节是滑脱量——它受定子磨损、温度、黏度、间隙非线性变化影响，"
              "解析公式难以长期准确。神经网络的优势是：用足够多的“（转速、扭矩/电流、"
              "井口压温、沉没度）→ 试井产量”样本，直接拟合这条映射，把机理公式里算不准的"
              "部分吃掉。电潜泵（ESP）井已有成功的 LSTM 计产论文（输入功率、频率、压力），"
              "与螺杆泵井的输入输出几乎同构，证明这条路可行。")

add_heading(doc, "4.2 推荐特征集（按优先级）", 2)
add_table(
    doc,
    ["优先级", "特征", "对应的物理含义"],
    [
        ["必需", "泵转速（或电机频率）", "决定理论排量 Q_th，信息量最大"],
        ["必需", "扭矩，或电机电流 / 有功功率", "反映泵压差与摩擦负荷，间接编码滑脱量"],
        ["必需", "井口油压、回压", "泵出口侧边界；参与泵压差计算"],
        ["强烈建议", "泵吸入口压力，或动液面", "泵入口侧边界；与出口侧共同确定 ΔP；"
         "无传感器时用回声仪动液面推算"],
        ["建议", "井口温度", "反映流体黏度变化（稠油井对滑脱影响大）"],
        ["建议", "含水率（化验或在线）", "区分油/液产量；修正混合物黏度"],
        ["可选", "泵累计运行时长 / 冲程数", "定子磨损导致的容积效率长期衰减"],
    ],
    widths=[2.2, 5.0, 8.8],
)
add_para(doc, "训练标签：定期试井的油/液产量，或翻斗、质量流量计的连续计量。样本必须覆盖"
              "不同转速档和不同回压，否则模型在未见过的工况下会外推失败。"
              "注意：油嘴开度不是必需特征——螺杆泵井通常没有可调油嘴。")

add_heading(doc, "4.3 两种建模结构", 2)
add_para(doc, "结构 A —— 纯数据驱动。输入 4.2 特征集，输出油/液产量。"
              "网络可选：多层感知机（MLP）、LSTM（有时序时）、TCN。"
              "优点是实现简单；缺点是物理约束弱，极端工况可能给出不合理产量（如转速升高"
              "产量反而降）。")
add_para(doc, "结构 B —— 机理 + 神经网络混合（推荐）。"
              "先用泵几何与转速按公式算理论排量 Q_th；再用神经网络估计滑脱量 Q_slip"
              "（输入：转速、扭矩/电流、泵压差或井口压与沉没度、温度、含水）；"
              "最终产量 = Q_th − Q_slip。泵压差可由第三章的井筒运移/摩阻模型计算，"
              "也可由吸入口压力传感器直接得到。优点：理论排量部分物理正确，网络只学难建模"
              "的滑脱；转速变化时外推更稳。")

add_heading(doc, "4.4 可借鉴的开源神经网络计产项目", 2)
add_para(doc, "下列项目不是专门为螺杆泵井写的，但提供了可直接改用的网络结构、训练流程与"
              "数据管线。改特征集为 4.2、改标签为本井试井产量即可。")
add_table(
    doc,
    ["项目", "地址", "原问题", "对本井的借鉴点"],
    [
        ["LSTM-for-Production", "github.com/saifkhanengr/LSTM-for-Production",
         "Volve 自喷井：井下/井口压温、油嘴 → 油气水产量",
         "完整的特征工程 + LSTM 训练 Notebook，最易上手；把油嘴特征换成转速/扭矩即可"],
        ["HVFM / BiVFM-Fleet", "github.com/mmmahhhhe/HVFM\npip install HVFM",
         "机理+数据双驱动瞬态多相 VFM（TCN/MPFNet）",
         "TCN 网络结构与混合建模框架；机理部分可换成泵特性公式"],
        ["VFM (Andrianov)", "github.com/nikolai-andrianov/VFM",
         "IFAC 论文：OLGA 仿真数据训练 NN 估产",
         "论文级可复现流程；带数据集"],
        ["ManyWells ML 示例", "github.com/solution-seeker-as/manywells",
         "NTNU 官方 NN VFM 基准（scripts/ml_examples）",
         "多种网络对比实验的写法；附 100 万点仿真数据"],
        ["pi-vfm", "github.com/CryptoGuy1/pi-vfm",
         "PINN 虚拟计量，仅用压温",
         "物理信息损失的写法，可把质量守恒/排量公式写入损失函数"],
        ["Hybrid_VFM_Slugging", "github.com/caioazevedo-mdm/Hybrid_VFM_Slugging",
         "扩散模型增广 + PINN，基于 3W 数据",
         "小样本时的数据增广思路（MIT 协议）"],
    ],
    widths=[3.2, 4.6, 4.0, 4.2],
)
add_para(doc, "近邻方法参考（无代码、有论文）：《Deep Learning Models Applied Flowrate "
              "Estimation in Offshore Wells with ESP》（Energies, 2025）——巴西 5 口海上"
              "电潜泵井，输入有功功率、频率、压力（分钟级），LSTM + 机理混合；输入输出与"
              "螺杆泵井几乎同构，网络结构可直接借鉴。")

add_heading(doc, "4.5 落地实施步骤", 2)
add_para(doc, "第一步 —— 数据基线。整理近 1–2 年试井记录，对齐对应时刻的转速、扭矩/电流、"
              "井口压温、动液面/吸入口压力、含水；清洗异常点；按时间切分训练集与测试集"
              "（禁止随机切分）。样本量少时先用 XGBoost/随机森林建基线，再上神经网络。")
add_para(doc, "第二步 —— 机理辅助。用 flotech 或 marlim3 按第二章步骤 3 算各试井点的泵压差，"
              "作为网络的一个输入特征（或用于结构 B 的滑脱标签构造：Q_slip = Q_th − Q_试井）。")
add_para(doc, "第三步 —— 训练。优先试结构 B（理论排量 − 网络滑脱）；对照结构 A。"
              "网络可从 LSTM-for-Production 的代码改起，特征换成 4.2 所列。")
add_para(doc, "第四步 —— 验证与漂移处理。用后期试井盲测；重点检查调转速、调回压前后模型"
              "是否跟得上。引入泵累计运行时长特征，或按季度用新试井点微调，处理定子磨损漂移。")

# ======================== 五、数据集与选型 ========================
add_heading(doc, "五、公开数据集、相关论文补充与选型建议", 1)
add_overview(doc, "本章收尾：列出可用来练手或做方法对比的公开数据（注意：目前没有公开的"
                  "螺杆泵井生产数据集，正式上线必须用自有现场数据）；补充油嘴计量论文"
                  "（对螺杆泵井不直接适用，但“少量井口参数→产量”的思路可参考）；"
                  "最后给出针对螺杆泵井的选型清单。")

add_heading(doc, "5.1 公开数据集", 2)
add_table(
    doc,
    ["数据集", "地址", "用途与局限"],
    [
        ["Volve 油田", "Equinor 公开；Kaggle：lamyalbert/volve-production-data",
         "真实油田日产量 + 井口/井下压温 + 油嘴开度；练特征工程与训练流程。"
         "局限：多为自喷/气举井，无螺杆泵参数"],
        ["ManyWells", "huggingface.co/datasets/solution-seeker-as/manywells",
         "2000 口井、100 万点仿真，专为 VFM 基准；练网络结构对比。"
         "局限：无泵模型"],
        ["Petrobras 3W 2.0", "github.com/petrobras/3W",
         "海上井多变量时序 + 异常事件标注；练异常工况下的鲁棒性。"
         "局限：偏事件检测，非计产标签"],
        ["HVFM 瞬态数据", "随 pip install HVFM 发布",
         "OLGA 仿真瞬态多相流；练 TCN/混合 VFM"],
    ],
    widths=[3.2, 5.6, 7.2],
)
add_para(doc, "重要提醒：公开数据只能用来验证方法管线。螺杆泵井计产模型的训练与标定，"
              "必须使用本油田的试井与泵运行数据。", bold=True)

add_heading(doc, "5.2 油嘴计量论文（辅助参考，非本井主路径）", 2)
add_para(doc, "油嘴是自喷井的“计量元件”，对应螺杆泵井里泵的角色。下列论文对螺杆泵井"
              "不直接适用，但展示了“少量易测参数 → 产量”的经典与 ML 路线，特征工程与"
              "验证方法可借鉴。")
add_bullet(doc, "经典机理：Gilbert(1954) 经验式；Ashford & Pierce(1974)；Sachdeva(1986)；"
               "Perkins(1993，对比研究精度最优)；Al-Safran & Kelkar(2009)。"
               "综述：J. Pet. Sci. Eng. 2021《Modelling oil and gas flow rate through chokes》。")
add_bullet(doc, "机器学习：Sci Rep 2024《Modeling liquid rate through wellhead chokes using ML》"
               "（Adaboost-SVR，误差 5.15%）；Sci Rep 2025 两篇（GBM+SADE+SHAP；CNN/MLP/RBFN）；"
               "《油气储运》2024《基于物理-数据融合的油嘴气液两相虚拟计量方法》。")

add_heading(doc, "5.3 针对螺杆泵井的选型清单", 2)
add_para(doc, "若目标是尽快上线可用的计产：", bold=True)
add_bullet(doc, "井筒段：flotech（稳态压降，上手最快）或 marlim3（需要瞬态时）；")
add_bullet(doc, "泵特性：按 COBEM 2009 / 2018 金属定子论文自写解析模型，用厂家曲线与试井标定；")
add_bullet(doc, "神经网络：采用结构 B（理论排量 − 网络滑脱），代码从 LSTM-for-Production 改特征起步；"
               "有时序数据再上 LSTM/TCN（参考 HVFM）；")
add_bullet(doc, "标签与验证：试井产量；严格按时间切分；覆盖多转速、多回压工况。")
add_para(doc, "若目标是方法研究与对比：ManyWells 数据 + 其官方 ML 示例做网络结构消融；"
              "用本井数据做迁移验证；参考 ESP 井 Energies 2025 论文的混合建模与不确定性评估写法。")
add_para(doc, "不建议：把自喷井油嘴计产模型或仅用历史产量做时序预测的模型，直接当作螺杆泵井"
              "计产模型使用——前者信息源不对，后者回答的是另一个问题。")

doc.save("/workspace/油田计产神经网络模型开源资源调研报告.docx")
print("saved")
