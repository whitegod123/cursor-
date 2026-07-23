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
    """每章开头的概述段落。"""
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
run = sub.add_run("——虚拟计量（VFM）、产量预测神经网络模型、油嘴计量论文、\n螺杆泵井计产专题与公开数据集汇总")
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
              "公开可获取的神经网络/机器学习计产模型开源实现、油嘴计量经典与前沿论文、"
              "配套公开数据集，并针对螺杆泵（PCP）井的计产路径设立专题章节。")
add_para(doc, "需要首先厘清两类容易混淆的模型，本报告的章节也按此划分：", bold=True)
add_table(
    doc,
    ["类型", "输入 → 输出", "回答的问题", "本报告对应章节"],
    [
        ["计产 / 虚拟计量（VFM）",
         "当前时刻的工况参数（井口/井下压力、温度、油嘴开度、泵转速等）→ 当前时刻的油气水产量",
         "“这口井现在的产量是多少？”用于替代多相流量计（MPFM）和试井",
         "第三、四、六、七、八章"],
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
              "举升方式与传感器配置，必须用目标井自己的试井/MPFM 数据训练或标定后才能使用。"
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
add_heading(doc, "六、油嘴（Choke）计量：开源代码与论文", 1)
add_overview(doc, "本章针对计产的一个细分场景：油嘴节流计量——利用油嘴上下游压力（温度）、"
                  "油嘴尺寸等少量参数反算通过油嘴的流量。它可以看作“简化版 VFM”：所需传感器"
                  "最少、实施成本最低，主要适用于自喷井/气举井。油嘴计量的论文积累最深厚，"
                  "分为三代：经验公式（1954 年起）、机理模型（1974 年起）、机器学习模型"
                  "（近十年）。注意：螺杆泵井井口一般不装可调油嘴，本章方法对螺杆泵井不直接"
                  "适用，但其“少量井口参数 → 产量”的建模思路可平移到泵参数上（见第八章）。")

add_heading(doc, "6.1 开源代码", 2)
add_bullet(doc, "github.com/1o-o1/Choke-size-prediction 及 github.com/durjoy221B/Choke_Size_Prediction："
               "孟加拉油气井数据，油嘴参数 → 气产量的机器学习回归。")

add_heading(doc, "6.2 经典经验/机理模型论文（机理计产软件油嘴模块的理论来源）", 2)
add_table(
    doc,
    ["模型", "年代", "类型", "要点"],
    [
        ["Gilbert", "1954", "经验公式",
         "最早的临界流经验式：产量 ∝ 井口压力×油嘴直径^a/GLR^b；"
         "Ros(1961)、Achong、Baxendell 为同形式改系数版本"],
        ["Ashford & Pierce", "1974", "机理模型", "基于能量方程的临界/亚临界流模型（SPE 4541）"],
        ["Sachdeva et al.", "1986", "机理模型", "临界+亚临界统一模型（SPE 15657），应用最广"],
        ["Perkins", "1993", "机理模型",
         "多相混合物临界/亚临界流理论模型（SPE 20633）；对比研究（1239 个数据点）"
         "表明精度最优，推荐首选"],
        ["Schüller et al.", "2003/2006", "机理模型", "考虑相间滑脱的油气水三相质量流量模型"],
        ["Al-Safran & Kelkar", "2009", "机理模型",
         "在 Sachdeva/Perkins 基础上加入常数滑脱与上游动能项，修正一致性问题"],
    ],
    widths=[3.4, 2.0, 2.4, 8.2],
)
add_bullet(doc, "系统综述推荐：《Modelling oil and gas flow rate through chokes: A critical "
               "review of extant models》（J. Pet. Sci. Eng., 2021, DOI:10.1016/j.petrol.2021.109775），"
               "将 1954 年以来的全部模型列表对比；另见 ASME 综述《A Review of Multiphase "
               "Flow Through Chokes》。")

add_heading(doc, "6.3 机器学习/神经网络油嘴计产论文（近两年）", 2)
add_table(
    doc,
    ["论文", "年份/期刊", "方法与结论"],
    [
        ["Modeling liquid rate through wellhead chokes using ML techniques",
         "2024, Scientific Reports",
         "565 个数据点；Adaboost-SVR/MARS/RBF/MLP 对比，输入井口压力、GLR、油嘴尺寸；"
         "最优误差 AAPRE 5.15%，并给出新经验关联式；敏感性分析表明油嘴尺寸影响最大"],
        ["Cost-effective tool for choke flow rate prediction in sub-critical oil wells",
         "2025, Scientific Reports",
         "GBM + 自适应差分进化（SADE）调参 + SHAP 可解释性分析；"
         "输入 GOR、油嘴尺寸、含水（BS&W）、井口压力、原油 API"],
        ["ML-based prediction of well performance parameters for wellhead choke flow optimization",
         "2025, Scientific Reports",
         "CNN/MLP/RBFN 对比，MLP 最优（测试 R²=0.994）；"
         "输入液量、井口压力、油嘴尺寸（D64）、BS&W、GLR"],
        ["ANN-driven empirical equation for real-time prediction of natural gas flow through chokes",
         "2025, Int. J. Petroleum Technology",
         "5 神经元小型 ANN 反推出闭式经验公式，现场无需运行模型即可手算；"
         "训练/测试 AAPE<2%，R>0.99"],
        ["Gas Rate Predictive Model as an Alternative to Choke Equations",
         "2024, SPE 219234",
         "机器学习气产量模型替代传统油嘴方程"],
        ["基于物理-数据融合的油嘴气液两相虚拟计量方法（中文）",
         "2024,《油气储运》",
         "油嘴节流机理方程 + DNN 反演质量含气率；仅用节流温差、压差均值/标准差等 "
         "9 个特征，覆盖分层/波浪/段塞/环状流，流量误差约 10% 以内"],
    ],
    widths=[5.2, 3.2, 7.6],
)

# ============ 七、四类模型的关系 ============
add_heading(doc, "七、油嘴模型与井筒摩阻、井筒运移、螺杆泵特性模型的关系", 1)
add_overview(doc, "本章回答一个常见困惑：油嘴模型、井筒流体摩阻计算模型、井筒流体运移模型、"
                  "螺杆泵运行特性模型是什么关系？结论：它们不是竞争关系，而是一口井机理计产"
                  "模型中“串联”的四个子模块，分别描述流体从井底到地面沿途经过的不同部件。"
                  "把它们的“压力-流量”约束联立求解（节点分析）得到的工作点流量就是产量——"
                  "这是机理法计产的本质；神经网络计产则是让网络从数据中直接学出这四个子模型的"
                  "联合映射。")
add_para(doc, "流动路径：地层 →（井底）→ 井筒 →（螺杆泵，如有）→ 井口 →（油嘴，如有）→ 地面管线。"
              "同一股流量依次流过所有环节，每个模型给出自己那一段的压力-流量约束：", bold=True)
add_table(
    doc,
    ["模型", "描述哪一段", "在计产中的角色"],
    [
        ["井筒流体运移模型",
         "井筒内多相流的整体行为：持液率、相间滑脱、流型转换、瞬态运移",
         "给出井筒沿程压力/温度剖面的“总框架”，是井筒段的完整描述"],
        ["井筒流体摩阻计算模型",
         "井筒压降三项（重力、摩阻、加速度）中的摩阻项",
         "运移模型的一个组成部分（子集），常以摩阻系数关联式形式出现"],
        ["螺杆泵运行特性模型",
         "泵段的“转速-压差-排量”特性关系（理论排量 − 滑脱量）",
         "链条中的增压环节；人工举升井的“计量元件”——泵参数直接编码产量信息"],
        ["油嘴模型",
         "井口节流件的“压差-流量”关系（临界/亚临界流）",
         "链条末端的节流环节；自喷井/气举井的“计量元件”"],
    ],
    widths=[3.6, 5.8, 6.6],
)
add_para(doc, "关键结论：自喷井靠油嘴计产（油嘴模型是主角，井筒模型用于计算回压）；"
              "螺杆泵井靠泵计产（泵特性模型是主角：转速 × 理论排量 − 滑脱量 = 产量，"
              "井筒摩阻/运移模型用于计算泵进出口压差）。因此第六章的油嘴计量方法对螺杆泵井"
              "不直接适用，思路平移方法见第八章。", bold=True)
add_para(doc, "上述子模型的开源实现情况：井筒运移/摩阻有成熟开源库——marlim3"
              "（github.com/petrobras/marlim3，Petrobras 开源的 1D 瞬态多相流模拟器，"
              "pip install marlim3）、flotech（多相流压降关联式库：Beggs & Brill、Duns & Ros、"
              "Ansari 等，pip install flotech）、pyResToolbox（VLP+IPR+节点分析）、"
              "NeqSim TransientPipe（瞬态漂移流+段塞追踪）；螺杆泵运行特性模型目前无开源实现，"
              "仅有公开论文中的解析模型（见第八章）。")

# ============ 八、螺杆泵井计产专题 ============
add_heading(doc, "八、螺杆泵（PCP）井计产专题", 1)
add_overview(doc, "本章针对螺杆泵井的计产路径。螺杆泵井与自喷井的根本区别：产量由泵控制"
                  "而非油嘴控制，井口一般无可调油嘴，因此计产的“信息源”是泵的运行参数"
                  "（转速、扭矩、电流/有功功率）而非油嘴参数。本章给出计量原理、神经网络"
                  "特征集建议、可参考的论文与资源，以及落地实施路径。")

add_heading(doc, "8.1 计量原理", 2)
add_para(doc, "螺杆泵计产的机理基础：实际排量 = 理论排量 − 滑脱量。理论排量由泵几何"
              "（转子直径、偏心距、导程）和转速唯一确定（Q理论 = 常数 × 转速）；滑脱量是"
              "高压端向低压端的内部回流，主要受泵压差、定转子间隙/过盈、流体黏度影响。"
              "泵压差由井筒两侧压力决定（需井筒摩阻/运移模型或泵吸入口压力传感器），"
              "扭矩/电流则反映泵压差和摩擦负荷。因此“转速 + 扭矩/电流 + 井口压温"
              "（+ 泵吸入口压力）”这组参数已经完整编码了产量信息，神经网络学习的就是"
              "这组参数到产量的映射。")

add_heading(doc, "8.2 神经网络特征集建议", 2)
add_table(
    doc,
    ["优先级", "特征", "作用"],
    [
        ["必需", "泵转速（或电机频率）", "决定理论排量，信息量最大"],
        ["必需", "扭矩或电机电流/有功功率", "反映泵压差与负荷，间接编码滑脱量"],
        ["必需", "井口油压、回压", "泵出口侧边界条件"],
        ["强烈建议", "泵吸入口压力（沉没度）", "泵入口侧边界条件，与出口侧共同确定泵压差；"
         "无此传感器时可用动液面数据替代"],
        ["建议", "井口温度", "反映流体黏度变化（对滑脱量影响大，稠油井尤其重要）"],
        ["建议", "含水率（化验或在线）", "区分油水产量、修正混合物黏度"],
        ["可选", "泵运行时长/累计冲程", "反映定子磨损导致的容积效率衰减（长期漂移项）"],
    ],
    widths=[2.2, 5.2, 8.6],
)
add_para(doc, "标签（训练目标）：定期试井的油/液产量，或翻斗/质量流量计的连续计量数据。"
              "建议训练时把“泵滑脱明显不同的工况”（不同转速档、不同回压）都覆盖到，"
              "否则模型在未见过的转速下会外推失效。")

add_heading(doc, "8.3 可参考的论文与资源", 2)
add_bullet(doc, "螺杆泵特性解析模型（无开源代码，公式完整可复现）：①金属定子 PCP 间隙滑脱"
               "解析模型（Mathematical Problems in Engineering, 2018, DOI:10.1155/2018/3696930，"
               "国产实红石油装备泵实验验证）；②井下工况定子变形耦合模型（J. Pet. Sci. Eng., "
               "2020：Hooke 定律+复合圆筒理论，适用多头螺杆泵）；③Gamboa et al. 逐腔室"
               "质量平衡滑脱模型（COBEM 2009 有完整公式与求解流程）。")
add_bullet(doc, "近邻方法平移——电潜泵（ESP）井深度学习计产：《Deep Learning Models Applied "
               "Flowrate Estimation in Offshore Wells with ESP》（Energies, 2025）：巴西 5 口"
               "海上井，输入有功功率、频率、压力（分钟级），LSTM+机理混合模型；输入输出定义"
               "与螺杆泵井计产几乎同构，网络结构可直接借鉴。")
add_bullet(doc, "油嘴 ML 论文的思路平移（见第六章）：把“油嘴尺寸、井口压力 → 产量”替换为"
               "“转速、扭矩/电流、泵压差 → 产量”，特征工程与验证方法完全通用。")
add_bullet(doc, "井筒段开源工具（算泵压差用）：marlim3、flotech、pyResToolbox（见第七章）。")

add_heading(doc, "8.4 实施路径建议", 2)
add_para(doc, "第一步（数据基线）：整理试井记录与对应时刻的泵参数（转速、扭矩/电流、井口"
              "压温、沉没度），按 8.2 特征集构建样本；样本量少时先用 XGBoost/随机森林建基线，"
              "再上神经网络（LSTM/TCN）。")
add_para(doc, "第二步（模型结构）：参考第二章 LSTM-for-Production 的流程骨架 + HVFM 的 TCN "
              "结构；如需物理一致性，可按“理论排量公式 + 神经网络学滑脱量”的混合结构"
              "（相当于把第 8.1 节机理式中难算的滑脱项交给网络）。")
add_para(doc, "第三步（滑脱标定与漂移处理）：用不同转速/回压下的试井点标定滑脱项；"
              "引入泵运行时长特征或定期重训练，处理定子磨损导致的长期漂移。")
add_para(doc, "第四步（验证）：按时间切分训练/测试集（禁止随机切分），用后期试井数据做"
              "盲测；关注转速调整前后模型是否跟得上。")

# ============ 九、数据集 ============
add_heading(doc, "九、配套公开数据集", 1)
add_overview(doc, "本章汇总训练上述模型可用的公开数据集。选择原则：要做真实井验证用 Volve"
                  "（唯一完整公开的真实油田生产数据）；要做方法研究和大样本训练用 ManyWells"
                  "（专为 VFM 基准设计的仿真数据）；要研究异常工况下的计量鲁棒性用 3W"
                  "（带专家标注的异常事件）。注意：目前没有公开的螺杆泵井生产数据集，"
                  "螺杆泵井建模必须依靠自有现场数据。")
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

# ============ 十、论文 ============
add_heading(doc, "十、仅有论文、无开源代码的前沿方法（方法参考）", 1)
add_overview(doc, "本章列出方法上最先进、但未开源代码的工作，价值在于提供可复现的方法论："
                  "网络结构、特征设计、物理约束方式和不确定性量化手段在论文中均有详细描述，"
                  "适合在前几章开源代码的基础上按论文思路做增强。油嘴方向的论文已单列于第六章，"
                  "螺杆泵/电潜泵方向的论文已单列于第八章。")
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

# ============ 十一、选型建议 ============
add_heading(doc, "十一、选型建议", 1)
add_overview(doc, "本章按四种典型使用场景给出落地路径，均以前文资源为基础。核心原则："
                  "先明确要解决的是计产还是产量预测（见第一章对照表），再按井的举升方式和"
                  "数据条件选模型。螺杆泵井直接按第 4 条（详见第八章专题）。")
add_para(doc, "1. 快速上手计产（自喷井）：以 saifkhanengr/LSTM-for-Production 为骨架，"
              "把输入特征替换为目标井的工况参数，标签用试井或 MPFM 数据。")
add_para(doc, "2. 方法研究与对比：使用 ManyWells 数据集与其官方 NN 示例作为基准，"
              "参考 HVFM 的 TCN 结构做增强。")
add_para(doc, "3. 机理+数据混合路线：NeqSim（github.com/equinor/neqsim）的 VirtualFlowMeter "
              "与 ML 混合模型接口，或参考 Bikmukhametov 博士论文的混合建模方案。")
add_para(doc, "4. 螺杆泵井（本项目场景）：按第八章专题执行——特征用“转速、扭矩/电流、"
              "井口压温、沉没度”，结构参考 LSTM-for-Production/HVFM，机理增强用"
              "“理论排量公式 + 神经网络学滑脱量”的混合结构，泵压差可由 marlim3/flotech "
              "井筒模型计算；用试井数据训练，按时间切分验证。")

doc.save("/workspace/油田计产神经网络模型开源资源调研报告.docx")
print("saved")
