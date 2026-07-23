# -*- coding: utf-8 -*-
"""开源螺杆泵井神经网络计产——相关模型与迁移指南（精简清晰版）"""

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


def H(doc, text, level=1):
    h = doc.add_heading("", level=level)
    run = h.add_run(text)
    set_cn_font(run, name_cn="黑体", size={1: 16, 2: 13, 3: 12}[level], bold=True, color=ACCENT)


def P(doc, text, bold=False, indent=True):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.space_after = Pt(6)
    run = p.add_run(text)
    set_cn_font(run, size=10.5, bold=bold)


def B(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style="List Bullet")
    p.paragraph_format.space_after = Pt(3)
    if bold_prefix:
        r = p.add_run(bold_prefix)
        set_cn_font(r, size=10.5, bold=True)
    r = p.add_run(text)
    set_cn_font(r, size=10.5)


def T(doc, headers, rows, widths=None):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Light Grid Accent 1"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = ""
        run = table.rows[0].cells[i].paragraphs[0].add_run(h)
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


doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.54)
    s.left_margin = s.right_margin = Cm(3.17)

# ---- 封面 ----
t = doc.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("螺杆泵井神经网络计产\n相关开源模型与迁移指南")
set_cn_font(r, name_cn="黑体", size=20, bold=True, color=ACCENT)

st = doc.add_paragraph()
st.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = st.add_run("结论 → 计产定义与机理流程 → 相关开源 → 怎么迁移 → 辅助工具 → 附录")
set_cn_font(r, size=12, color=GRAY)

d = doc.add_paragraph()
d.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = d.add_run("2026 年 7 月")
set_cn_font(r, size=10.5, color=GRAY)
doc.add_paragraph()

# ==================== 1 ====================
H(doc, "一、结论（一句话）", 1)
P(doc, "目前没有专门针对「螺杆泵井」的开源神经网络计产成品；"
       "但有一批「工况参数 → 产量」的通用虚拟计量（VFM）开源神经网络，"
       "以及人工举升（电潜泵）相关开源，可以迁移到螺杆泵井上使用。"
       "迁移的核心只有一件事：把输入特征换成泵工况（转速、扭矩/电流等），"
       "用本井试井产量当标签重新训练。", bold=True)

# ==================== 2 计产定义与机理流程 ====================
H(doc, "二、螺杆泵井计产定义与机理计产流程", 1)
P(doc, "迁移神经网络之前，先弄清「计产」在螺杆泵井上是什么意思，以及机理法如何算出产量。"
       "神经网络学的就是同一条映射。")

H(doc, "2.1 计产是什么（与产量预测的区别）", 2)
T(doc,
  ["", "计产（本报告目标）", "产量预测（不是目标）"],
  [
      ["问题", "这口井现在产多少？", "未来一周/一月产多少？"],
      ["输入", "当前泵工况（转速、扭矩、电流、压温…）", "历史产量序列"],
      ["输出", "当前油/液产量", "未来产量"],
      ["用途", "替代/补充流量计、试井间隔内连续计量", "产量规划、递减分析"],
  ],
  widths=[2.4, 6.8, 6.8])
P(doc, "本报告只讨论计产。第三章以后的开源迁移，全部是「当前工况 → 当前产量」。")

H(doc, "2.2 为什么螺杆泵井要单独建计产模型", 2)
P(doc, "自喷井/气举井产量主要由井口油嘴控制，计产信息源是油嘴尺寸与油嘴前后压差；"
       "螺杆泵井产量由泵控制，井口通常没有可调油嘴，计产信息源是转速、扭矩/电流以及泵两端压差。"
       "把自喷井油嘴计产模型直接套过来是错的。")

H(doc, "2.3 机理计产概论：流动链 + 三个辅助模型", 2)
P(doc, "流动路径：地层 → 泵吸入口 → 螺杆泵（增压）→ 油管井筒 → 井口 → 地面。"
       "稳态时各段流量相同、压力在接点连续。把各段「压力–流量」约束联立求解，"
       "得到的工作点流量就是产量。三个辅助模型分工：")
T(doc,
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
  widths=[3.4, 3.0, 5.0, 4.6])
P(doc, "一句话：运移是井筒总框架，摩阻是运移内部的一块，泵特性是链条上的增压与计量核心。"
       "三者一起用；神经网络可以学整条映射，也可以只学其中的滑脱项。")

H(doc, "2.4 机理计产求解流程（六步）", 2)
P(doc, "以「已知转速与井口压力、求产量」为例（稳态节点分析）：")
B(doc, "准备输入：泵几何（转子直径、偏心距、导程、级数）、当前转速、井口油压、"
       "流体物性（密度、黏度、含水、气油比）、井身与泵挂深度。",
  bold_prefix="步骤 1 — ")
B(doc, "假设一个试探产量 Q。", bold_prefix="步骤 2 — ")
B(doc, "用井筒运移模型（内部调用摩阻计算）从井口往下积分到泵出口，得到泵出口压力 P_out；"
       "结合吸入口压力传感器或动液面得到 P_in；泵压差 ΔP = P_out − P_in。",
  bold_prefix="步骤 3 — ")
B(doc, "用螺杆泵特性模型：理论排量 Q_th = C × 转速；滑脱量 Q_slip = f(ΔP, 黏度, 间隙…)；"
       "泵实际排量 Q_pump = Q_th − Q_slip。",
  bold_prefix="步骤 4 — ")
B(doc, "比较 Q_pump 与假设的 Q；不一致则修正假设回到步骤 3；一致则该 Q 即为当前产量。",
  bold_prefix="步骤 5 — ")
B(doc, "（可选）用流入动态 IPR 校核：泵吸入口压力对应的地层供液能力应与 Q 匹配。",
  bold_prefix="步骤 6 — ")
P(doc, "开源环境下：步骤 3 可用 flotech / marlim3（见第五章）；步骤 4 需按论文自写泵特性公式。"
       "神经网络计产等于用数据直接拟合「转速、扭矩/电流、井口压、沉没度… → Q」；"
       "混合结构则固定 Q_th = C×n，只让网络学 Q_slip（见第四章结构 B）。")

H(doc, "2.5 为何还要神经网络", 2)
P(doc, "机理计产的薄弱环节是滑脱量——受定子磨损、温度、黏度、间隙非线性变化影响，"
       "解析公式难以长期准确。神经网络用试井样本拟合这条映射，可吃掉机理算不准的部分；"
       "与机理公式结合（结构 B）时，既保留物理外推，又提高现场精度。")

# ==================== 3 ====================
H(doc, "三、相关开源模型（按迁移优先级）", 1)
P(doc, "下表只列「能拿来改成螺杆泵井计产」的开源。与计产无关的（故障诊断、几何设计、资产管理）放在第七章附录。")

T(doc,
  ["优先级", "项目", "地址", "原用途", "迁移价值"],
  [
      ["1（首选）", "LSTM-for-Production",
       "github.com/saifkhanengr/LSTM-for-Production",
       "Volve 油田：井口/井下压温、油嘴开度 → 油气水产量（Keras LSTM）",
       "管线最完整、最好改；把油嘴换成转速/扭矩即可"],
      ["2", "HVFM",
       "github.com/mmmahhhhe/HVFM\npip install HVFM",
       "机理+数据双驱动多相虚拟计量（TCN）",
       "网络更强；机理部分可换成泵「理论排量−滑脱」"],
      ["3", "Andrianov VFM",
       "github.com/nikolai-andrianov/VFM",
       "IFAC 论文配套：神经网络估产 + 数据集",
       "论文级可复现训练流程"],
      ["4", "ManyWells ML 示例",
       "github.com/solution-seeker-as/manywells\n（scripts/ml_examples）",
       "NTNU 官方神经网络 VFM 基准",
       "对比不同网络结构时用"],
      ["5", "pi-vfm",
       "github.com/CryptoGuy1/pi-vfm",
       "物理信息神经网络（PINN）虚拟计量",
       "可把泵排量公式写入损失函数"],
      ["6", "ESP Digital Twin",
       "github.com/abhi133113/Artificial-lift-ESP-Autonomous",
       "电潜泵：LSTM + 泵曲线物理校验",
       "同为人工举升，输入最像（频率/功率/压力）；需改成「当前产量」回归"],
  ],
  widths=[1.8, 3.0, 4.6, 4.0, 2.6])

P(doc, "说明：电潜泵（ESP）与螺杆泵（PCP）都是人工举升，传感器形态接近"
       "（转速/频率、电流/功率、压力），所以第 6 项虽然不是计产成品，迁移思路最接近。"
       "第 1–5 项是通用「工况→产量」计产网络，改特征后就是螺杆泵井计产模型。")

# ==================== 4 ====================
H(doc, "四、怎么迁移（按步骤做）", 1)

H(doc, "4.1 迁移对照：原模型 → 螺杆泵井", 2)
T(doc,
  ["项目", "原输入（删掉或替换）", "换成螺杆泵井输入", "原输出", "换成"],
  [
      ["LSTM-for-Production 等",
       "油嘴开度、井下压温、环空压力…",
       "转速、扭矩或电流、井口油压、回压、沉没度/吸入口压力、井口温度、含水",
       "油气水日产量",
       "本井试井油/液产量（或翻斗计量）"],
      ["ESP Digital Twin",
       "频率、有功功率、PIP 等",
       "几乎可直接对应：频率→转速，功率→电流/扭矩，压力保留",
       "未来趋势/异常",
       "改成当前时刻产量回归（换损失与标签）"],
  ],
  widths=[3.0, 3.6, 4.2, 2.4, 2.8])

H(doc, "4.2 推荐特征（螺杆泵井）", 2)
T(doc,
  ["是否必需", "特征", "作用"],
  [
      ["必需", "泵转速（或电机频率）", "决定理论排量，信息量最大"],
      ["必需", "扭矩，或电机电流/有功功率", "反映泵压差与负荷"],
      ["必需", "井口油压、回压", "泵出口侧压力"],
      ["强烈建议", "泵吸入口压力，或动液面", "与出口侧一起定泵压差"],
      ["建议", "井口温度、含水率", "黏度与油/液拆分"],
      ["不要用", "油嘴开度", "螺杆泵井通常没有可调油嘴，原模型里有则删掉"],
  ],
  widths=[2.4, 5.2, 8.4])

H(doc, "4.3 两种迁移结构（选一种）", 2)
P(doc, "结构 A —— 直接换特征（最快）", bold=True)
P(doc, "打开 LSTM-for-Production 的 Notebook，把特征列改成上面的泵特征，标签改成试井产量，"
       "按时间切分训练/测试，重新 fit。适合先跑通、看效果。")
P(doc, "结构 B —— 机理 + 网络（更稳，推荐）", bold=True)
P(doc, "产量 = 理论排量 − 滑脱量。理论排量用公式算死：Q理论 = C × 转速（C 由泵几何决定）；"
       "只让神经网络预测滑脱量（输入仍是转速、扭矩/电流、压差或压温沉没度等）。"
       "最终产量 = Q理论 − 网络输出。调转速时外推比纯黑盒稳。"
       "若用 HVFM，可把其「机理模块」换成这个泵公式。")

H(doc, "4.4 具体操作清单（建议从第 1 项开源改起）", 2)
B(doc, "克隆仓库，按 README 用 Volve 示例跑通，确认环境没问题。",
  bold_prefix="第 1 步：跑通原项目。")
B(doc, "整理本井数据表：时间戳对齐的转速、扭矩/电流、井口压、沉没度、温度、含水 + 试井产量。"
       "清洗停井、缺测；按时间前后切分训练集/测试集（不要随机打乱）。",
  bold_prefix="第 2 步：准备本井数据。")
B(doc, "在代码里替换特征列名与标签列；删掉油嘴相关特征；标准化方式可沿用原项目。",
  bold_prefix="第 3 步：改输入输出。")
B(doc, "先训练结构 A；有余力再做结构 B（先算 Q理论，标签改为 试井产量−Q理论 即滑脱）。",
  bold_prefix="第 4 步：训练。")
B(doc, "用后期试井盲测；重点看「调转速、调回压」后误差是否可接受；"
       "定期用新试井点微调，抵消定子磨损。",
  bold_prefix="第 5 步：验证与维护。")

H(doc, "4.5 迁移时常见坑", 2)
B(doc, "样本太少或只覆盖一个转速档 → 换转速就失效。尽量收集多转速、多回压试井点。")
B(doc, "随机划分训练/测试 → 时间泄漏，指标虚高。必须按时间切分。")
B(doc, "把「产量预测」（用历史产量猜未来）当成计产 → 问题都答错了。计产输入必须是当前工况。")
B(doc, "没有公开螺杆泵井数据集，不能指望下载现成权重；必须用自有井数据训练。")

# ==================== 5 ====================
H(doc, "五、辅助工具（算泵压差时用，不是 NN 本身）", 1)
P(doc, "迁移神经网络时，若没有吸入口压力传感器，可用井筒模型从井口压力反算泵压差，"
       "作为网络的一个输入特征（或用于结构 B）。")
T(doc,
  ["用途", "开源工具", "地址"],
  [
      ["井筒压降 / 运移（算泵出口压力）", "flotech（关联式，上手快）、marlim3（瞬态）、ManyWells（稳态漂移流）",
       "pip install flotech\ngithub.com/petrobras/marlim3\ngithub.com/solution-seeker-as/manywells"],
      ["泵理论排量与滑脱（结构 B）", "无开成品库；按论文自写：Q理论=C×n，滑脱用 Gamboa/COBEM2009 或 2018 金属定子模型",
       "论文 DOI:10.1155/2018/3696930 等"],
  ],
  widths=[4.0, 6.5, 5.5])

# ==================== 6 ====================
H(doc, "六、你现在该做什么", 1)
B(doc, "打开 LSTM-for-Production，跑通示例。", bold_prefix="今天：")
B(doc, "导出本井「泵参数 + 试井产量」对齐表，按 4.2 列好特征。", bold_prefix="本周：")
B(doc, "完成结构 A 训练与盲测；误差可接受再上结构 B。", bold_prefix="下一步：")
P(doc, "一句话回顾：没有螺杆泵专用开源计产 NN → 用通用 VFM 开源（首选 LSTM-for-Production）"
       "→ 特征换成泵工况、标签用试井产量重新训练 → 有条件做成「理论排量 − 网络滑脱」。", bold=True)

# ==================== 7 附录 ====================
H(doc, "七、附录：螺杆泵相关开源（非计产，勿与第三章混淆）", 1)
P(doc, "检索时还会碰到一批名字带「螺杆泵 / PCP」的开源仓库。"
       "它们做的是故障诊断、几何设计、资产管理等，不是「工况→产量」的神经网络计产。"
       "列在此处以免遗漏，也避免误当成计产模型使用。")
T(doc,
  ["项目", "地址", "实际做什么", "能否当计产用"],
  [
      ["pump_ai_software（螺杆泵AI软件）",
       "github.com/xiansurfer/pump_ai_software",
       "宏观控制图（扭矩/泵效）、故障预警、生存分析；国内油田泵故障数据",
       "否（故障诊断）"],
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
  widths=[3.8, 4.8, 5.0, 2.4])
P(doc, "若业务同时需要「计产 + 故障诊断」，可并行使用：计产走第三章开源 + 第四章迁移；"
       "故障诊断可参考 pump_ai_software 的控制图与预警思路。二者输入传感器有重叠"
       "（转速、扭矩、电流），但训练标签不同（产量 vs 故障类别），不能混成一个模型。")

out1 = "/workspace/开源螺杆泵井神经网络计产模型调研报告.docx"
out2 = "/workspace/油田计产神经网络模型开源资源调研报告.docx"
doc.save(out1)
doc.save(out2)
print("saved", out1)
