# -*- coding: utf-8 -*-
"""生成《油田计产神经网络模型开源资源调研报告》Word 文档。"""

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn


ACCENT = RGBColor(0x1F, 0x4E, 0x79)


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
    sizes = {1: 16, 2: 14, 3: 12}
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

# 页面设置
for section in doc.sections:
    section.top_margin = Cm(2.54)
    section.bottom_margin = Cm(2.54)
    section.left_margin = Cm(3.17)
    section.right_margin = Cm(3.17)

# ============ 封面标题 ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("油田计产神经网络模型\n开源资源调研报告")
set_cn_font(run, name_cn="黑体", size=22, bold=True, color=ACCENT)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("——虚拟计量（VFM）、产量预测神经网络模型与公开数据集汇总")
set_cn_font(run, size=12, color=RGBColor(0x66, 0x66, 0x66))

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_p.add_run("2026 年 7 月")
set_cn_font(run, size=10.5, color=RGBColor(0x66, 0x66, 0x66))

doc.add_paragraph()

# ============ 概述 ============
add_heading(doc, "一、概述", 1)
add_para(doc, "油田计产（用工况参数实时反算单井产量）在国际文献中一般称为虚拟计量"
              "（Virtual Flow Metering，VFM）或软测量（Soft Sensing）。本报告汇总了目前"
              "公开可获取的神经网络/机器学习计产模型开源实现、配套公开数据集以及仅有论文"
              "的前沿方法，供选型和二次开发参考。")
add_para(doc, "需要特别说明：所有开源项目提供的均为“模型结构 + 训练代码”，没有可以直接"
              "用于生产井的预训练权重。计产模型高度依赖具体井的流体物性（PVT）、井身结构、"
              "油嘴特性与传感器配置，必须使用目标井自己的试井/多相流量计（MPFM）数据训练"
              "或标定后才能使用。工业级产品（Solution Seeker、SLB OLGA Online 等）全部闭源。")

# ============ 核心推荐 ============
add_heading(doc, "二、核心推荐（论文级、带数据、可复现）", 1)
add_table(
    doc,
    ["项目", "地址", "方法", "说明"],
    [
        ["VFM (Andrianov)", "github.com/nikolai-andrianov/VFM",
         "神经网络", "IFAC 论文官方代码+数据集，用 OLGA 仿真井数据训练神经网络估产，"
         "本领域被引用最多的开源实现（20 星）"],
        ["HVFM / BiVFM-Fleet", "github.com/mmmahhhhe/HVFM\npip install HVFM",
         "TCN（MPFNet）", "机理+数据双驱动分布式虚拟计量框架，单井评估 MAPE 0.15%，"
         "随包发布瞬态多相流数据集；机理部分依赖 OLGA，可替换"],
        ["ManyWells ML 示例", "github.com/solution-seeker-as/manywells",
         "多种NN基准", "NTNU 官方神经网络 VFM 基准示例（scripts/ml_examples），"
         "配套 100 万点、2000 口井仿真数据集（HuggingFace 下载）"],
        ["LSTM-for-Production", "github.com/saifkhanengr/LSTM-for-Production",
         "多变量 LSTM", "基于 Volve 真实数据：井下压温、油管压差、环空压力、油嘴开度、"
         "井口压温 → 油气水三相产量，全流程 Notebook，最易上手"],
    ],
    widths=[3.2, 4.6, 2.4, 5.8],
)

# ============ 专门的 VFM 实现 ============
add_heading(doc, "三、专门的虚拟计量（VFM）神经网络实现", 1)
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["pi-vfm", "github.com/CryptoGuy1/pi-vfm",
         "物理信息神经网络（PINN）虚拟计量，仅用常规压力/温度传感器估算多相流量，"
         "专门处理含水率超出训练分布的泛化问题"],
        ["virtual_flow_forecasting", "github.com/sidnei-almeida/virtual_flow_forecasting",
         "LSTM 虚拟计量，从压力传感器数据预测管道流量（葡萄牙语注释）"],
        ["Hybrid_VFM_Slugging", "github.com/caioazevedo-mdm/Hybrid_VFM_Slugging",
         "扩散模型（DDPM）生成段塞流合成数据 + PINN 训练鲁棒 VFM，"
         "基于 Petrobras 3W 数据集，MIT 协议"],
        ["VolveDigitalTwin", "github.com/MillyDzukou/VolveDigitalTwin",
         "Volve 油田数字孪生全栈平台（React/Django + ML 管线做 VFM），"
         "适合参考工程化落地方式"],
        ["Virtual-Flow-Metering", "github.com/mahyar-ahmadi/Virtual-Flow-Metering",
         "个人小项目，代码量少，可作参考"],
        ["vfm", "github.com/pcperera/vfm", "个人小项目"],
        ["Virtual-Flow-Meter", "github.com/AhmadSidaoui/Virtual-Flow-Meter", "个人小项目"],
        ["Statistical-analysis-of-VFM", "github.com/NRT23/Statistical-analysis-of-Virtual-Flow-Meter",
         "VFM 统计分析 Notebook"],
        ["MPFM Calibration", "github.com/GustavoLacourt/MultiphaseFlowMeterCalibration",
         "非神经网络：用分离器测量数据标定多相流量计（MPFM）的方法，计产工作流配套"],
    ],
    widths=[4.0, 5.4, 6.6],
)

# ============ 产量预测神经网络 ============
add_heading(doc, "四、基于工况参数/历史数据的产量神经网络", 1)
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["Oil-Production-Flow-Rate-Prediction", "github.com/rafiarsy/Oil-Production-Flow-Rate-Prediction-Deep-Neural-Network",
         "RNN/LSTM 产量预测，带 Walk-Forward 时序验证"],
        ["Oil-production-prediction-LSTM", "github.com/qinchaoxu/Oil-production-prediction-using-LSTM-based-on-Keras",
         "Keras LSTM 产油量预测（5 星）"],
        ["Deep-learning-Class-Final-Exam-Project", "github.com/Dr-LazyMazy/Deep-learning-Class-Final-Exam-Project",
         "多种深度学习架构在 Volve 产量预测上的对比研究（论文配套，带数据集）"],
        ["Deep-Learn-Oil", "github.com/akashlevy/Deep-Learn-Oil",
         "CNN/GRU/LSTM/SimpleRNN 等多架构油井时序预测工具集（Keras/Theano，较早期）"],
        ["AC_decline_curve", "github.com/adrienCAD/AC_decline_curve",
         "递减曲线分析（Arps）+ LSTM 混合产量预测"],
        ["Oil-Production-Prediction-by-LSTM", "github.com/bietongxuan/Oil-Production-Prediction-by-LSTM",
         "LSTM 产量预测"],
        ["Machine-Learning-Production-Prediction", "github.com/bengsoon/Machine-Learning-Production-Prediction",
         "非神经网络（决策树/随机森林/XGBoost），但“虚拟计量器”定位与特征工程流程最完整，"
         "适合作为建模流程参考"],
        ["oil-and-gas", "github.com/jamiubadmusng/oil-and-gas",
         "ARIMA/Prophet/LSTM/XGBoost 产量预测 + 异常检测（Volve 数据）"],
        ["reservoir-forecasting-app", "github.com/lazy70/reservoir-forecasting-app",
         "Streamlit 应用：Prophet/XGBoost/LSTM 油气产量预测，可上传数据在线出结果"],
    ],
    widths=[4.6, 6.2, 5.2],
)

# ============ 中文仓库 ============
add_heading(doc, "五、中文开源仓库", 1)
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["BP 神经网络油田产量预测", "github.com/HuO50/BP-neural-net-work-For-Oil-Field",
         "BP 神经网络预测油田产量（国内经典做法）"],
        ["TCN+加权预测器油气井产量预测", "github.com/hehe-rook/An-oil-and-gas-well-production-prediction-model-based-on-TCN-and-weight-predictor",
         "TCN + 加权预测器的油气井产量时序预测（13 星）"],
        ["OIL-software", "github.com/hehe-rook/OIL-software",
         "同一作者为中石油开发的“岩相智探、甜点寻优、钻井优化与产量预测”一体化系统参考代码"],
        ["HetSTGCN", "github.com/janqsong/HetSTGCN",
         "基于时空图神经网络（STGCN）的石油产量预测——少见的考虑井间关系的实现"],
    ],
    widths=[5.0, 6.4, 4.6],
)

# ============ 油嘴计量 ============
add_heading(doc, "六、油嘴（Choke）计量方向", 1)
add_bullet(doc, "github.com/1o-o1/Choke-size-prediction 及 github.com/durjoy221B/Choke_Size_Prediction："
               "孟加拉油气井数据，油嘴参数 → 气产量的机器学习回归，"
               "相当于经典 Gilbert 型油嘴计产公式的数据驱动版本。")
add_bullet(doc, "中文文献参考：《基于物理-数据融合的油嘴气液两相虚拟计量方法》（《油气储运》2024），"
               "油嘴节流机理方程 + 深度神经网络反演质量含气率，仅依赖现有温压测量系统实现气液计量"
               "（无开源代码，思路可复现）。")

# ============ 公开数据集 ============
add_heading(doc, "七、配套公开数据集", 1)
add_table(
    doc,
    ["数据集", "来源/地址", "内容与用途"],
    [
        ["Volve 油田数据集", "Equinor 公开；Kaggle：lamyalbert/volve-production-data",
         "北海 Volve 油田 2008–2016 全生命周期真实数据：日产量、井口/井下压温、油嘴开度等。"
         "真实数据首选，绝大多数开源计产项目的训练数据"],
        ["ManyWells", "huggingface.co/datasets/solution-seeker-as/manywells",
         "2000 口垂直井、100 万数据点的多相流仿真数据，含气/油/水流量、流型标签，"
         "专为 VFM 基准测试设计（sol/nsol/nscl 三个子集）"],
        ["Petrobras 3W 2.0", "github.com/petrobras/3W",
         "海上油井多变量时间序列 + 专家标注异常事件（段塞、闭井、仪表故障等），"
         "偏异常检测，传感器数据也可用于软测量研究（477 星）"],
        ["HVFM 瞬态多相流数据集", "随 HVFM pip 包/仓库发布",
         "OLGA 批量仿真生成的瞬态多相流数据，配套 BiVFM-Fleet 框架"],
    ],
    widths=[3.6, 5.6, 6.8],
)

# ============ 论文 ============
add_heading(doc, "八、仅有论文、无开源代码的前沿方法（方法参考）", 1)
add_bullet(doc, "贝叶斯神经网络 VFM：Grimstad, Hotvedt 等（NTNU），arXiv:2102.01391，"
               "60 口真实井、5 个油气资产，带不确定性量化，平均误差 4%–6%。")
add_bullet(doc, "混合建模博士论文：Bikmukhametov《First Principles and Machine Learning "
               "Virtual Flow Metering》（NTNU 2020，全文公开），梯度提升 + RNN + 多相流物理"
               "混合，含该领域最全面的文献综述与方法论。")
add_bullet(doc, "WISE 基础模型：arXiv 2604.23767，FiLM + 跨模态注意力 + 质量守恒软约束的"
               "设计感知多任务模型，ManyWells 基准上 VFM 误差降低至 1/13，"
               "迁移到 Volve 真实井油量 R²=0.89。")
add_bullet(doc, "集成学习 VFM：AL-Qutami et al. (2018) 系列，神经网络/集成学习虚拟计量，"
               "被后续多篇论文作为基线。")
add_bullet(doc, "电潜泵（ESP）井：LSTM 混合模型流量估计（Energies 2025，巴西 5 口海上井，"
               "输入有功功率、频率、压力等分钟级数据）；深度神经网络 ESP 建模 + MCMC "
               "不确定性评估（Heliyon 2024）。均无代码，但方法描述详细。"),

# ============ 结论 ============
add_heading(doc, "九、选型建议", 1)
add_para(doc, "1. 快速上手：以 saifkhanengr/LSTM-for-Production 为骨架，把输入特征替换为"
              "目标井的工况参数，标签用试井或 MPFM 数据。")
add_para(doc, "2. 方法研究与对比：使用 ManyWells 数据集与其官方 NN 示例作为基准，"
              "参考 HVFM 的 TCN 结构做增强。")
add_para(doc, "3. 机理+数据混合路线：NeqSim（github.com/equinor/neqsim）的 VirtualFlowMeter "
              "与 ML 混合模型接口，或参考 Bikmukhametov 博士论文的混合建模方案。")
add_para(doc, "4. 特殊井型（如螺杆泵井）：目前无现成开源实现，建议采用“井筒压降开源库"
              "（marlim3/flotech）+ 泵特性解析模型 + 神经网络修正”的组合方案，"
              "用现场数据（转速、扭矩、电流、井口压温）训练。")

doc.save("/workspace/油田计产神经网络模型开源资源调研报告.docx")
print("saved")
