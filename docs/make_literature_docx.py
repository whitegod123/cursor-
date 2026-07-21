# -*- coding: utf-8 -*-
"""生成《电潜螺杆泵运行特性模型文献清单》Word 文档。

格式约定：
- 四个模型部分标题：紫色加粗；
- 已用于模型代码实现的文献：红色字体并加【已用于模型代码】标记；
- 每部分分"中文文献 / 英文文献"两块。

运行：python3 docs/make_literature_docx.py
输出：docs/电潜螺杆泵运行特性模型文献清单.docx
"""

from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

PURPLE = RGBColor(0x70, 0x30, 0xA0)
RED = RGBColor(0xC0, 0x00, 0x00)
BLACK = RGBColor(0x00, 0x00, 0x00)
GRAY = RGBColor(0x59, 0x59, 0x59)

# (文献条目, 是否已用于模型代码)
SECTIONS = [
    (
        "第一部分　几何与运动学模型（计产导向）",
        "作用：型线/结构参数 → 理论排量 q=4eDT（或泵因数 Fp）→ 理论流量 Qt=qn，"
        "是流量-漏失模型（第二部分）的直接输入。本节只收录\"参数-排量-产量\"这条链上的文献，"
        "不收录自转/公转、啮合点速度、位移-速度-加速度等纯运动学分析文献"
        "（那些服务于强度/振动/磨损分析，不进计产公式）。",
        [  # 中文
            ("[待核实作者/期号] 偏心距对类椭圆形采油螺杆泵举升性能的影响[J]. 化工机械. "
             "有限元方法计算不同偏心距 e 下的排量 q 与临界接触应力/扬程，"
             "为按产量/扬程需求反选几何参数提供依据——即\"目标产量→几何参数\"的反算路径。"
             "（篇名经网络检索获得，卷期号与年份需在知网/万方以篇名核实）", False),
            ("郑磊, 吴晓东, 韩国庆, 左翼, 范喆, 王靖惠. 全金属螺杆泵工作特性试验模拟与评价[J]. "
             "石油机械, 2018, 46(5): 77-82. DOI: 10.16082/j.cnki.issn.1001-4578.2018.05.013 "
             "（期刊官网可查：html.rhhz.net）. 提出间隙配合方式下理论排量的修正计算式 "
             "Qt=α·A0·T·n（α 为间隙修正系数），是本研究理论排量项的直接计算依据"
             "（另有选泵级数的设计方法，属选型阶段内容，非运行评估所需）。", False),
            ("郑磊, 吴晓东, 韩国庆, 徐军, 史殊哲, 李准. 全金属螺杆泵间隙漏失模型[J]. "
             "石油科学通报, 2018, 3(3): 320-331. 由结构参数计算单转理论排量（如 "
             "77.3 mL/r），并作为漏失修正前的产量基准与 Gamboa 实测数据对比验证。", True),
            ("钟功祥, 雷鹏燕, 祝令闯. 全金属单螺杆油泵工作性能的全参数分析[J]. "
             "西南石油大学学报(自然科学版), 2020, 42(3): 161-169. "
             "偏心距、导程、间隙等几何参数对排量与产量的敏感性分析。", False),
            ("单螺杆泵设计及特性试验研究[J].（维普期刊收录，正规学术数据库）. "
             "由目标流量、容积效率反算螺杆直径 D、导程 T、偏心距 e 的完整设计方法，"
             "设计实例验证。", False),
            ("何存兴. 单螺杆泵设计中若干理论问题探讨[J]. 水泵技术, 1995(5): 3-10. "
             "（几何参数与排量关系的早期系统论述）", False),
        ],
        [  # 英文
            ("Zheng L., Wu X., Han G., Li H., Zuo Y., Zhou D. Analytical Model for the Flow in Progressing "
             "Cavity Pump with the Metallic Stator and Rotor in Clearance Fit[J]. "
             "Mathematical Problems in Engineering, 2018. DOI: 10.1155/2018/3696930 "
             "（理论排量公式 q=4eDT，即本模型 PumpGeometry 的直接出处）", True),
            ("Nguyen T., Al-Safran E., Saasen A., Nes O.-M. Modeling the design and "
             "performance of progressing cavity pump using 3-D vector approach[J]. "
             "Journal of Petroleum Science and Engineering, 2014, 122: 180-186. "
             "DOI: 10.1016/j.petrol.2014.07.009 "
             "（泵因数 Fp=AF·Ps、产量 Q=Fp·ω 的严格推导，多头泵推广；流量面积 "
             "AF=2πe²(N−2)+4de）", True),
            ("Nguyen K., Nguyen T., Al-Safran E. Modeling the performance of progressive "
             "cavity pump under downhole conditions[J]. Journal of Petroleum Science and "
             "Engineering, 2020. DOI: 10.1016/j.petrol.2020.108121 "
             "式(9) Qa=理论产量−总滑失，将流量面积与导程直接代入实际产量计算，"
             "覆盖单头与多头泵。", False),
            ("[待核实作者] Experimental and CFD modelling of a Progressive Cavity Pump "
             "using overset unstructured mesh[C]. E3S Web of Conferences, ICCHMT 2021. "
             "综述并应用 Nguyen(2014) 泵因数模型与滑失模型联合预测产量性能，"
             "CFD 与实验误差 <10%。", False),
            ("Saveth K.J., Klein S.T. The Progressing Cavity Pump: Principle and "
             "Capabilities[C]. SPE 18873, 1989. （PCP 排量原理与产能范围的经典综述）", False),
            ("Moineau R. A New Capsulism[D]. PhD Thesis, University of Paris, 1930. "
             "（螺杆泵原理开山之作，理论排量 q=4eDT 思想的最初来源）", False),
        ],
    ),
    (
        "第二部分　流量-漏失特性模型",
        "作用：建立理论流量、漏失量与实际产液量的关系，Q = Qt − Qs，计产公式的机理核心。",
        [
            ("郑磊, 吴晓东, 韩国庆, 徐军, 史殊哲, 李准. 全金属螺杆泵间隙漏失模型[J]. "
             "石油科学通报, 2018, 3(3): 320-331. DOI: 10.3969/j.issn.2096-1693.2018.03.029 "
             "（压差—剪切流动漏失模型 + 实验验证）", True),
            ("姜东, 石彦, 薛建泉, 等. 螺杆泵内部滑失与泵外漏失机理研究[J]. 石油钻采工艺, "
             "2013, 35(4): 73-77.", False),
            ("操建平, 孟庆昆, 高圣平, 等. 螺杆泵漏失机理研究[J]. 机械设计与制造, "
             "2012(4): 153-155.", False),
            ("陈舟圣, 刘志龙, 杨万有, 等. 全金属螺杆泵工作特性实验研究[J]. 石油钻采工艺, "
             "2012, 34(5): 65-67.", False),
            ("姜东, 石白妮, 李增亮, 等. 全金属单螺杆泵工作性能的仿真与实验研究[J]. "
             "中国石油大学学报(自然科学版), 2014, 38(6): 134-139.", False),
            ("姜东, 石白妮, 李增亮, 等. 金属单螺杆泵外特性的数值模拟及试验研究[J]. "
             "石油机械, 2014, 42(4): 77-80.", False),
            ("姜东. 全金属螺杆泵漏失规律及配合间隙优化研究[J]. 石油机械, 2019, 47(3): 93-98. "
             "DOI: 10.160820/j.cnki.issn.1001-4578.2019.03.016（期刊官网可查：html.rhhz.net）. "
             "有限元模拟分析漏失及接触磨损规律，按黏度优化配合间隙；5 口井现场应用平均"
             "泵效提高 15.1%，单井日增油 3.13 t——难得的现场验证数据。", False),
            ("学位论文（硕士）. 螺杆泵宏观动态控制图的应用研究. "
             "（容积效率与井底流压数学模型、动态控制图；标题来自第三方检索站点，"
             "请以知网/万方原文核实）", False),
        ],
        [
            ("Zheng L., Wu X., Han G., Li H., Zuo Y., Zhou D. Analytical Model for the Flow in Progressing "
             "Cavity Pump with the Metallic Stator and Rotor in Clearance Fit[J]. "
             "Mathematical Problems in Engineering, 2018. DOI: 10.1155/2018/3696930 "
             "（式(35) Q=Qt−Qs、式(36) ηv=Q/Qt，本模型主公式出处；开放获取）", True),
            ("Gamboa J., Olivet A., Espin S. New Approach for Modeling Progressive Cavity "
             "Pumps Performance[C]. SPE 84137, 2003. DOI: 10.2118/84137-MS "
             "（滑失分解为压差分量+转子运动分量，标定式结构出处）", True),
            ("Pessoa P.A.S., Paladino E.E., de Lima J.A. A Simplified Model for the Flow in "
             "a Progressive Cavity Pump[C]. COBEM 2009, COB09-1951. "
             "（漏失∝w³Δp/μ；湍流时漏失∝Δp^n, n<1；免费 PDF）", True),
            ("Mrinal K.R., Samad A. Leakage flow correlation of a progressive cavity pump delivering "
             "shear thinning non-Newtonian fluids[J]. Int. J. Oil, Gas and Coal Technology, "
             "2017, 16(2): 166-186. DOI: 10.1504/IJOGCT.2017.086299 （实验回归漏失量的方法学）",
             True),
            ("Paladino E.E., Lima J.A., Pessoa P.A.S., Almeida R.F.C. A computational model "
             "for the flow within rigid stator progressing cavity pumps[J]. Journal of "
             "Petroleum Science and Engineering, 2011, 78(1): 178-192. "
             "DOI: 10.1016/j.petrol.2011.05.008 （三维瞬态 CFD；级间压差不均的证据）", True),
            ("[待核实作者] A 3D Transient Model for the Multiphase Flow in a "
             "Progressing-Cavity Pump[J]. SPE Journal. DOI: 10.2118/178924-PA "
             "（含气两相流下的漏失与容积效率）", False),
            ("[待核实作者] Study on performance of progressing cavity pumps (PCPs) in "
             "different fit modes[C/J]. 2020. （过盈/间隙两种配合的容积特性统一表达；"
             "ResearchGate 免费）", False),
            ("Andrade S.F.A., et al. Asymptotic Model of the 3D Flow in a Progressing-Cavity "
             "Pump[J]. SPE Journal, 2011. DOI: 10.2118/142294-PA （解析-数值之间的中间路线）",
             False),
            ("Paladino E.E., et al. Computational Modeling of the Three-Dimensional Flow in "
             "a Metallic Stator Progressing Cavity Pump[C]. SPE 114110, 2008. "
             "DOI: 10.2118/114110-MS", False),
        ],
    ),
    (
        "第三部分　功率-扭矩特性模型",
        "作用：建立电参数、轴功率、泵扭矩与负载的关系，M = Δp·q/(2π) + 摩擦扭矩；"
        "用于负载校核与压差反推。",
        [
            ("杨永华, 等. 地面驱动螺杆泵负载扭矩波动机制[J]. 中国石油大学学报(自然科学版), "
             "2011, 35(5): 120-124. DOI: 10.3969/j.issn.1673-5005.2011.05.022 "
             "（水力扭矩+摩擦扭矩分解、黏滑机制）", True),
            ("陈涛平, 王春艳, 孙兆海, 钱朝慧. 地面驱动螺杆泵抽油杆柱负载扭矩的计算[J]. "
             "大庆石油学院学报, 2004, 28(6): 26-28. 应用环空螺旋流理论建立杆管环空压降及"
             "摩擦扭矩数学模型，现场应用负载扭矩计算平均相对误差≤2%。", False),
            ("刘巨保, 罗敏, 李淑红. 地面驱动螺杆泵抽油杆柱动力学分析技术及其应用[J]. "
             "石油学报, 2005, 26(1): 121-124.（期刊官网可查：syxb-cps.com.cn，"
             "石油学报为石油工程领域权威期刊）. 构造动力间隙元描述杆管随机碰撞，"
             "大庆油田应用井口扭矩计算相对误差 1.5%。", False),
            ("董世民, 张万胜, 王强, 柴国鸿, 苏艳玲. 地面驱动螺杆泵采油杆管偏磨机理[J]. "
             "石油学报, 2012, 33(2): 304-309.（负载扭矩引起的杆管偏磨机理，"
             "与磨损修正模型第四部分呼应）", False),
            ("学位论文（博士）. 螺杆泵工作特性研究及应用. "
             "（抽油杆柱负载扭矩试验与计算、能耗特征分析；标题来自第三方检索站点，"
             "请以知网/万方原文核实）", False),
        ],
        [
            ("Zhou D., Yuan H. Design of Progressive Cavity Pump Wells[C]. SPE 113324, 2008. "
             "DOI: 10.2118/113324-MS （压差-转速-产量设计关系式，黏度对临界吸入压力的影响；"
             "Academia.edu 可免费获取全文）", False),
            ("Samuel G.R., Saveth K.J. Optimal Design of Progressing Cavity Pumps (PCP)[J]. "
             "Journal of Energy Resources Technology, 2006, 128(4). DOI: 10.1115/1.2358142 "
             "（多头泵导程与外壳直径的最优比例关系，最大流量设计）", False),
            ("[待核实作者] Complex Fluid Flow and Mechanical Modeling of Metal Progressing "
             "Cavity Pumps PCP's[C]. SPE 150419, 2012. DOI: 10.2118/150419-MS "
             "（金属泵流动+力学联合建模，应力应变与寿命预测）", False),
            ("[待核实作者] Simulation of the operating characteristics of an all-metal "
             "conical screw pump[J]. Scientific Reports, 2025. "
             "DOI: 10.1038/s41598-025-28519-z （扭矩、能效随间隙与转速的变化规律；开放获取）",
             False),
            ("[待核实作者] Study on performance of progressing cavity pumps (PCPs) in "
             "different fit modes[C/J]. 2020. （功率消耗与机械效率对比：过盈摩擦 vs 间隙漏失）",
             False),
            ("[待核实作者] A 3D Transient Model for the Multiphase Flow in a "
             "Progressing-Cavity Pump[J]. SPE Journal. DOI: 10.2118/178924-PA "
             "（黏性损耗的精确预测，轴功率组成）", False),
            ("Paladino E.E., et al. A computational model for the flow within rigid stator "
             "progressing cavity pumps[J]. JPSE, 2011. （黏性损耗/扭矩的 CFD 预测；"
             "亦列于第二部分）", True),
        ],
    ),
    (
        "第四部分　容积效率修正模型",
        "作用：综合修正压差、温度、黏度、含水、含气、磨损等因素对产液量的影响，"
        "ηv = f(Δp, T, μ, fw, 磨损)。",
        [
            ("魏纪德, 吴文祥, 曾艳. 螺杆泵定子橡胶溶胀对容积效率的影响及对策[J]. 石油机械, "
             "2005, 33(4): 16-18. （溶胀退化修正）", False),
            ("郑磊, 吴晓东, 韩国庆, 左翼, 范喆, 王靖惠. 全金属螺杆泵工作特性试验模拟与评价[J]. "
             "石油机械, 2018, 46(5): 77-82. DOI: 10.16082/j.cnki.issn.1001-4578.2018.05.013 "
             "（理论排量修正计算方法；容积损失与机械损失随压差/转速的相反趋势；期刊官网免费）",
             False),
            ("李增亮, 李昆鹏, 孙召成, 杜明超, 于然, 姜东. 全金属螺杆泵定转子配合优化及特性"
             "试验研究[J]. 石油机械, 2018, 46(2): 77-83. "
             "DOI: 10.16082/j.cnki.issn.1001-4578.2018.02.014 "
             "（温度→定转子变形→间隙变化→泵效；最佳间隙 0.1~0.3 mm；期刊官网免费）", False),
            ("姜东. 全金属螺杆泵漏失规律及配合间隙优化研究[J]. 石油机械, 2019, 47(3): 93-98. "
             "DOI: 10.160820/j.cnki.issn.1001-4578.2019.03.016 "
             "（按黏度优化配合间隙的现场应用研究；亦列于第二部分）", False),
            ("学位论文（硕士）. 螺杆泵井生产系统参数优化设计. "
             "（气体影响/漏失影响/综合影响三种容积效率公式，章节结构可作写作模板；"
             "标题来自第三方检索站点，请以知网/万方原文核实）", False),
            ("钟功祥, 雷鹏燕, 祝令闯. 全金属单螺杆油泵工作性能的全参数分析[J]. "
             "西南石油大学学报(自然科学版), 2020, 42(3): 161-169. "
             "（黏度/转速/级增压值对容积效率的影响规律）", False),
            ("杨秀萍, 郭津津. 单螺杆泵定子橡胶的接触磨损分析[J]. 润滑与密封, 2007, "
             "32(4): 33-35. （磨损修正）", False),
            ("行业标准: JB/T 8091-2014 单螺杆泵 试验方法. "
             "（黏度换算与容积效率修正的标准计算公式）", False),
            ("学位论文（博士）. 螺杆泵工作特性研究及应用. "
             "（溶胀对容积效率影响章节、定子温度场有限元分析；亦列于第三部分）", False),
        ],
        [
            ("[待核实作者] Modeling the performance of progressive cavity pump under "
             "downhole conditions[J]. Journal of Petroleum Science and Engineering, 2020. "
             "（Hooke 定律+复合圆筒理论：井下压力温度→定子变形→间隙修正→漏失修正，"
             "最贴合\"修正模型\"概念，推荐精读）", False),
            ("[待核实作者] Optimizing the Clearance Fit of a Progressive Cavity Pump for "
             "the Thermal Recovery of Petroleum Using Fluid–Structure Thermal Coupling[J]. "
             "ACS Omega, 2022. DOI: 10.1021/acsomega.2c03957 "
             "（流固热耦合计算容积效率，实验偏差<5%；开放获取）", False),
            ("[待核实作者] A Computational Model for Analysis of Fluid-Structure "
             "Interaction within Elastomeric Progressing Cavity Pumps[C]. SPE 165650, 2013. "
             "DOI: 10.2118/165650-MS （橡胶定子变形与流动的双向耦合）", False),
            ("Brinkman H.C. The viscosity of concentrated suspensions and solutions[J]. "
             "Journal of Chemical Physics, 1952, 20: 571. DOI: 10.1063/1.1700493 "
             "（水包油乳状液黏度式 μm=μw/(1−φ)^2.5，高含水黏度修正）", True),
            ("Guth E., Simha R. Untersuchungen über die Viskosität von Suspensionen und "
             "Lösungen[J]. Kolloid-Zeitschrift, 1936, 74: 266. "
             "（油包水乳状液黏度式 μm=μo·(1+2.5fw+14.1fw²)）", True),
            ("Woelflin W. The Viscosity of Crude-Oil Emulsions[C]. API Drilling and "
             "Production Practice, 1942. （采油工程乳状液黏度经典关系式）", False),
            ("[待核实作者] A 3D Transient Model for the Multiphase Flow in a "
             "Progressing-Cavity Pump[J]. SPE Journal. DOI: 10.2118/178924-PA "
             "（含气修正依据；亦列于第二部分）", False),
        ],
    ),
]


def add_entry(doc: Document, idx: int, text: str, used: bool) -> None:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.left_indent = Pt(18)
    run = p.add_run(f"[{idx}] {text}")
    run.font.size = Pt(10.5)
    run.font.color.rgb = RED if used else BLACK
    if used:
        tag = p.add_run("　【已用于模型代码】")
        tag.font.size = Pt(10.5)
        tag.font.bold = True
        tag.font.color.rgb = RED


def main() -> None:
    doc = Document()
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(10.5)

    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    tr = title.add_run("电潜螺杆泵运行特性模型 文献清单")
    tr.font.size = Pt(16)
    tr.font.bold = True

    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sr = sub.add_run("（四个模型部分·紫色标题；已用于模型代码实现的文献·红色标注）")
    sr.font.size = Pt(10)
    sr.font.color.rgb = GRAY

    note = doc.add_paragraph()
    nr = note.add_run(
        "使用须知（务必阅读）：\n"
        "① 标注 DOI 的期刊/会议论文均已通过 doi.org 或学术检索核实真实存在，可直达全文。\n"
        "② 标注\"[待核实作者]\"表示：论文标题、期刊、年卷期、DOI 经检索确认真实存在，"
        "但完整作者名单本工具未逐一核实，引用前请打开 DOI 链接确认作者信息。\n"
        "③ 标注\"知网检索篇名\"的学位论文：标题信息来自第三方论文预览/代写网站"
        "（如 51papers.com、abslw.com、ppdoc.com 等）的搜索结果摘要，本工具未直接在"
        "中国知网/万方数据核实其真实存在性与作者信息。这类网站可信度有限，"
        "引用前必须以篇名在知网/万方精确检索、确认原文存在后方可使用，"
        "不可直接以本清单信息作为参考文献。\n"
        "④ 红色标注文献为已在数字计产模型代码（espcp_metering / espcp_all_in_one.py）"
        "中作为公式依据实际引用的文献，可信度已通过代码实现与数学自洽性验证交叉确认。\n"
        "⑤ 本清单由 AI 辅助网络检索整理，属于文献线索汇总而非权威文献库，"
        "所有条目使用前均须由使用者自行核实原文。"
    )
    nr.font.size = Pt(9)
    nr.font.color.rgb = GRAY

    for part_title, part_desc, cn_list, en_list in SECTIONS:
        h = doc.add_paragraph()
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(2)
        hr = h.add_run(part_title)
        hr.font.size = Pt(14)
        hr.font.bold = True
        hr.font.color.rgb = PURPLE

        d = doc.add_paragraph()
        dr = d.add_run(part_desc)
        dr.font.size = Pt(9.5)
        dr.font.color.rgb = GRAY

        cn_h = doc.add_paragraph()
        cn_r = cn_h.add_run(f"中文文献（{len(cn_list)} 篇）")
        cn_r.font.bold = True
        cn_r.font.size = Pt(11)
        for i, (text, used) in enumerate(cn_list, 1):
            add_entry(doc, i, text, used)

        en_h = doc.add_paragraph()
        en_r = en_h.add_run(f"英文文献（{len(en_list)} 篇）")
        en_r.font.bold = True
        en_r.font.size = Pt(11)
        for i, (text, used) in enumerate(en_list, 1):
            add_entry(doc, i, text, used)

    out = "docs/电潜螺杆泵运行特性模型文献清单.docx"
    doc.save(out)
    total_cn = sum(len(s[2]) for s in SECTIONS)
    total_en = sum(len(s[3]) for s in SECTIONS)
    print(f"已生成 {out}：中文 {total_cn} 条 + 英文 {total_en} 条 = {total_cn + total_en} 条")


if __name__ == "__main__":
    main()
