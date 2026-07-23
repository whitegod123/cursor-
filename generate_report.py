# -*- coding: utf-8 -*-
"""生成《油田计产神经网络模型开源资源调研报告》Word 文档。"""

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
    """每章开头的概述段落：加【本章概述】前缀并整体加粗底色风格。"""
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

# ============ 封面标题 ============
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = title.add_run("油田计产神经网络模型\n开源资源调研报告")
set_cn_font(run, name_cn="黑体", size=22, bold=True, color=ACCENT)

sub = doc.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = sub.add_run("——虚拟计量（VFM）、产量预测神经网络模型与公开数据集汇总")
set_cn_font(run, size=12, color=GRAY)

date_p = doc.add_paragraph()
date_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
run = date_p.add_run("2026 年 7 月")
set_cn_font(run, size=10.5, color=GRAY)

doc.add_paragraph()

# ============ 一、概述 ============
add_heading(doc, "一、概述", 1)
add_para(doc, "油田计产（用工况参数实时反算单井产量）在国际文献中一般称为虚拟计量"
              "（Virtual Flow Metering，VFM）或软测量（Soft Sensing）。本报告汇总了目前"
              "公开可获取的神经网络/机器学习计产模型开源实现、配套公开数据集，以及仅有"
              "论文的前沿方法，供选型和二次开发参考。")
add_para(doc, "需要首先厘清两类容易混淆的模型，本报告的章节也按此划分：", bold=True)
add_table(
    doc,
    ["类型", "输入 → 输出", "回答的问题", "本报告对应章节"],
    [
        ["计产 / 虚拟计量（VFM）",
         "当前时刻的工况参数（井口/井下压力、温度、油嘴开度等）→ 当前时刻的油气水产量",
         "“这口井现在的产量是多少？”用于替代多相流量计（MPFM）和试井",
         "第三、四、六章"],
        ["产量预测（Forecasting）",
         "历史产量序列（+历史工况）→ 未来一段时间的产量",
         "“这口井未来一周/一月产多少？”用于产量规划、递减分析",
         "第五章"],
    ],
    widths=[3.4, 5.6, 4.6, 2.4],
)
add_para(doc, "两类模型常用相同的网络结构（BP/LSTM/TCN 等），区别在于输入输出的定义："
              "计产模型学习的是“工况 → 产量”的物理映射，可实时使用；产量预测模型学习的是"
              "产量自身的时间规律，属于时间序列外推。选型时务必先确认自己要解决的是哪一类问题。")
add_para(doc, "另需说明：所有开源项目提供的均为“模型结构 + 训练代码”，没有可直接用于"
              "生产井的预训练权重。计产模型高度依赖具体井的流体物性（PVT）、井身结构、"
              "油嘴特性与传感器配置，必须用目标井自己的试井/MPFM 数据训练或标定后才能使用。"
              "工业级产品（Solution Seeker、SLB OLGA Online 等）全部闭源。")

# ============ 二、核心推荐 ============
add_heading(doc, "二、核心推荐（论文级、带数据、可复现）", 1)
add_overview(doc, "本章从后文全部资源中挑出 4 个质量最高的项目——筛选标准是：有正式论文支撑、"
                  "附带公开数据集、代码完整可复现。时间有限只看这一章即可。其中前三个针对"
                  "“计产/虚拟计量”问题，第四个（LSTM-for-Production）用真实油田数据做"
                  "“工况参数 → 当日产量”，介于计产与预测之间，是最容易上手的入门项目。")
add_table(
    doc,
    ["项目", "地址", "方法", "针对问题", "说明"],
    [
        ["VFM (Andrianov)", "github.com/nikolai-andrianov/VFM",
         "神经网络", "计产（VFM）",
         "IFAC 论文官方代码+数据集，用 OLGA 仿真井数据训练神经网络估产，"
         "本领域被引最多的开源实现（20 星）"],
        ["HVFM / BiVFM-Fleet", "github.com/mmmahhhhe/HVFM\npip install HVFM",
         "TCN（MPFNet）", "计产（VFM）",
         "机理+数据双驱动分布式虚拟计量框架，单井评估 MAPE 0.15%，"
         "随包发布瞬态多相流数据集；机理部分依赖 OLGA，可替换"],
        ["ManyWells ML 示例", "github.com/solution-seeker-as/manywells",
         "多种NN基准", "计产（VFM）",
         "NTNU 官方神经网络 VFM 基准示例（scripts/ml_examples），"
         "配套 100 万点、2000 口井仿真数据集（HuggingFace 下载）"],
        ["LSTM-for-Production", "github.com/saifkhanengr/LSTM-for-Production",
         "多变量 LSTM", "计产为主",
         "基于 Volve 真实数据：井下压温、油管压差、环空压力、油嘴开度、"
         "井口压温 → 油气水三相产量，全流程 Notebook，最易上手"],
    ],
    widths=[2.8, 4.2, 2.2, 2.2, 4.6],
)

# ============ 三、VFM 实现 ============
add_heading(doc, "三、专门的虚拟计量（VFM）神经网络实现", 1)
add_overview(doc, "本章针对“实时计产”问题：模型输入当前时刻的传感器工况参数（压力、温度、"
                  "油嘴开度等），输出当前时刻的多相流量，目标是替代昂贵的多相流量计（MPFM）"
                  "或作为试井之间的连续计量手段。这类项目的共同特点是把自己定位为“虚拟流量计”，"
                  "关注实时性、物理一致性和对工况变化的泛化能力；部分项目采用物理信息神经网络"
                  "（PINN）或“机理模型+神经网络修正”的混合路线来提升可信度。")
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

# ============ 四、工况参数计产 ============
add_heading(doc, "四、基于工况参数的产量回归神经网络（Volve 等真实数据）", 1)
add_overview(doc, "本章同样针对“计产”问题，但项目定位偏学习/研究性质：用 Volve 等公开真实"
                  "油田数据，建立“工况参数（井下/井口压温、油嘴开度等）→ 日产量”的回归模型。"
                  "与第三章的区别在于：第三章的项目以“虚拟流量计产品”为目标（实时、多相、"
                  "考虑物理约束），本章的项目以“建模流程演示”为目标（日粒度、重特征工程与"
                  "模型对比）。想学习完整建模流程（数据清洗、特征选择、调参、验证）从本章入手最合适。")
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["LSTM-for-Production", "github.com/saifkhanengr/LSTM-for-Production",
         "多变量 LSTM，井下压温/油嘴/井口压温 → 油气水三相产量（核心推荐，见第二章）"],
        ["Oil-Production-Flow-Rate-Prediction", "github.com/rafiarsy/Oil-Production-Flow-Rate-Prediction-Deep-Neural-Network",
         "RNN/LSTM 产量回归，带 Walk-Forward 时序验证"],
        ["Deep-learning-Class-Final-Exam-Project", "github.com/Dr-LazyMazy/Deep-learning-Class-Final-Exam-Project",
         "多种深度学习架构在 Volve 产量建模上的对比研究（论文配套，带数据集）"],
        ["Machine-Learning-Production-Prediction", "github.com/bengsoon/Machine-Learning-Production-Prediction",
         "非神经网络（决策树/随机森林/XGBoost），但“虚拟计量器”定位明确，"
         "特征工程与建模流程最完整，适合作为流程参考"],
        ["Predictive-Modeling-Volve", "github.com/padronfrancis1/Predictive-Modeling-of-Oil-Production-Wells-Volve-Dataset",
         "Volve 数据 EDA + 建模管线，分析压力/油嘴开度与产量关系，含调参与模型堆叠"],
    ],
    widths=[4.6, 6.2, 5.2],
)

# ============ 五、产量预测 ============
add_heading(doc, "五、基于历史数据的产量预测神经网络（含中文仓库）", 1)
add_overview(doc, "注意：本章针对的是“产量预测”问题，不是计产。这类模型输入历史产量序列"
                  "（有的加上历史工况），输出未来一段时间的产量，本质是时间序列外推，"
                  "服务于产量规划、递减分析和异常发现，不能用来替代流量计做实时计量。"
                  "此前调研中发现的中文仓库（BP 神经网络、TCN、时空图神经网络三个）经核对代码，"
                  "全部属于本章“历史数据产量预测”类型，已归入本章并在表中标注语言。")
add_table(
    doc,
    ["项目", "地址", "说明"],
    [
        ["TCN+加权预测器（中文）", "github.com/hehe-rook/An-oil-and-gas-well-production-prediction-model-based-on-TCN-and-weight-predictor",
         "TCN + 加权预测器的油气井产量时间序列预测，PyTorch 实现，README 有详细中文讲解（13 星）"],
        ["HetSTGCN（中文）", "github.com/janqsong/HetSTGCN",
         "时空图神经网络（STGCN）石油产量预测——少见的考虑井间空间关系的实现"],
        ["BP 神经网络油田产量预测（中文）", "github.com/HuO50/BP-neural-net-work-For-Oil-Field",
         "BP 神经网络预测油田产量（国内最经典的做法）"],
        ["OIL-software（中文）", "github.com/hehe-rook/OIL-software",
         "为中石油开发的“岩相智探、甜点寻优、钻井优化与产量预测”一体化系统参考代码"],
        ["Oil-production-prediction-LSTM", "github.com/qinchaoxu/Oil-production-prediction-using-LSTM-based-on-Keras",
         "Keras LSTM 产油量时序预测（5 星）"],
        ["Deep-Learn-Oil", "github.com/akashlevy/Deep-Learn-Oil",
         "CNN/GRU/LSTM/SimpleRNN 等多架构油井时序预测工具集（Keras/Theano，较早期）"],
        ["AC_decline_curve", "github.com/adrienCAD/AC_decline_curve",
         "递减曲线分析（Arps）+ LSTM 混合产量预测"],
        ["Oil-Production-Prediction-by-LSTM", "github.com/bietongxuan/Oil-Production-Prediction-by-LSTM",
         "LSTM 产量预测"],
        ["oil-and-gas", "github.com/jamiubadmusng/oil-and-gas",
         "ARIMA/Prophet/LSTM/XGBoost 产量预测 + 异常检测（Volve 数据）"],
        ["reservoir-forecasting-app", "github.com/lazy70/reservoir-forecasting-app",
         "Streamlit 应用：Prophet/XGBoost/LSTM 油气产量预测，可上传数据在线出结果"],
    ],
    widths=[4.6, 6.2, 5.2],
)

# ============ 六、油嘴计量 ============
add_heading(doc, "六、油嘴（Choke）计量方向", 1)
add_overview(doc, "本章针对计产的一个细分场景：油嘴节流计量——利用油嘴上下游压力（温度）、"
                  "油嘴尺寸等少量参数反算通过油嘴的流量，相当于经典 Gilbert 型油嘴计产公式的"
                  "数据驱动版本。它可以看作“简化版 VFM”：所需传感器最少、实施成本最低，"
                  "适合井口只有常规温压计量的老井改造场景。")
add_bullet(doc, "github.com/1o-o1/Choke-size-prediction 及 github.com/durjoy221B/Choke_Size_Prediction："
               "孟加拉油气井数据，油嘴参数 → 气产量的机器学习回归。")
add_bullet(doc, "中文文献参考：《基于物理-数据融合的油嘴气液两相虚拟计量方法》（《油气储运》2024），"
               "油嘴节流机理方程 + 深度神经网络反演质量含气率，仅依赖现有温压测量系统实现气液计量，"
               "流量误差约 10% 以内（无开源代码，但公式与特征完整，可复现）。")

# ============ 七、数据集 ============
add_heading(doc, "七、配套公开数据集", 1)
add_overview(doc, "本章汇总训练上述模型可用的公开数据集。选择原则：要做真实井验证用 Volve"
                  "（唯一完整公开的真实油田生产数据）；要做方法研究和大样本训练用 ManyWells"
                  "（专为 VFM 基准设计的仿真数据）；要研究异常工况下的计量鲁棒性用 3W"
                  "（带专家标注的异常事件）。")
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

# ============ 八、论文 ============
add_heading(doc, "八、仅有论文、无开源代码的前沿方法（方法参考）", 1)
add_overview(doc, "本章列出方法上最先进、但未开源代码的工作，价值在于提供可复现的方法论："
                  "网络结构、特征设计、物理约束方式和不确定性量化手段在论文中均有详细描述，"
                  "适合在前几章开源代码的基础上按论文思路做增强。")
add_bullet(doc, "贝叶斯神经网络 VFM：Grimstad, Hotvedt 等（NTNU），arXiv:2102.01391，"
               "60 口真实井、5 个油气资产，带不确定性量化，平均误差 4%–6%。")
add_bullet(doc, "混合建模博士论文：Bikmukhametov《Machine Learning and First Principles "
               "Modeling Applied to Multiphase Flow Estimation》（NTNU 2020，全文公开），"
               "梯度提升 + RNN + 多相流物理混合，含该领域最全面的文献综述与方法论。")
add_bullet(doc, "WISE 基础模型：arXiv 2604.23767，FiLM + 跨模态注意力 + 质量守恒软约束的"
               "设计感知多任务模型，ManyWells 基准上 VFM 误差降低至 1/13，"
               "迁移到 Volve 真实井油量 R²=0.89。")
add_bullet(doc, "集成学习 VFM：AL-Qutami et al. (2018) 系列，神经网络/集成学习虚拟计量，"
               "被后续多篇论文作为基线。")
add_bullet(doc, "电潜泵（ESP）井：LSTM 混合模型流量估计（Energies 2025，巴西 5 口海上井，"
               "输入有功功率、频率、压力等分钟级数据）；深度神经网络 ESP 建模 + MCMC "
               "不确定性评估（Heliyon 2024）。均无代码，但方法描述详细。")

# ============ 九、选型建议 ============
add_heading(doc, "九、选型建议", 1)
add_overview(doc, "本章按四种典型使用场景给出落地路径，均以前文资源为基础。核心原则："
                  "先明确要解决的是计产还是产量预测（见第一章对照表），再按数据条件选模型。")
add_para(doc, "1. 快速上手计产：以 saifkhanengr/LSTM-for-Production 为骨架，把输入特征替换为"
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
