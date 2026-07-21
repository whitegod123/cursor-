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
        "第一部分　几何与运动学模型",
        "作用：型线方程、啮合运动学、理论排量 q = 4·e·D·T 与泵因数计算，一切模型的基础。",
        [  # 中文
            ("学位论文（博士）. 单螺杆泵螺杆—衬套副型线研究. （内摆线/短幅内摆线型线方程、"
             "共轭副运动分析、参数计算与优化设计；知网博硕库检索篇名）", False),
            ("学位论文（硕士）. 单螺杆泵的运动学仿真、有限元模拟及结构优化. "
             "（螺杆/定子型线方程、密封腔运动学分析；知网检索篇名）", False),
            ("学位论文（硕士）. 单螺杆泵运动学仿真及转子动力特性研究. "
             "（转子自转与公转、啮合点速度分析；知网检索篇名）", False),
            ("学位论文（硕士）. 单螺杆泵流场数值模拟及结构参数优化研究. "
             "（型线理论、运动学特征、转子受液压力/转矩分析；知网检索篇名）", False),
            ("单螺杆泵设计及特性试验研究[J].（维普收录；推导螺杆直径 D、导程 T、偏心距 e "
             "计算公式，拟合容积效率计算式，完整设计方法）", False),
            ("何存兴. 单螺杆泵设计中若干理论问题探讨[J]. 水泵技术, 1995(5): 3-10.", False),
            ("周连考, 龚绍海, 赵继生. 单螺杆泵的设计与试验研究[J]. 水泵技术, 1999(3): 19-25.", False),
            ("Moineau 理论在油田抽油螺杆泵设计中的应用[J]. 哈尔滨工程大学学报, 2000, "
             "21(4): 85-89.", False),
            ("钟功祥, 雷鹏燕, 祝令闯. 全金属单螺杆油泵工作性能的全参数分析[J]. "
             "西南石油大学学报(自然科学版), 2020, 42(3): 161-169. "
             "（偏心距/导程/间隙等几何参数对性能的影响）", False),
        ],
        [  # 英文
            ("Moineau R. A New Capsulism[D]. PhD Thesis, University of Paris, 1930. "
             "（螺杆泵原理开山之作，理论排量思想的源头）", False),
            ("Nguyen T., Al-Safran E., et al. Modeling the design and performance of "
             "progressing cavity pump using 3-D vector approach[J]. Journal of Petroleum "
             "Science and Engineering, 2014. DOI: 10.1016/j.petrol.2014.05.021", True),
            ("Saveth K.J., Klein S.T. The Progressing Cavity Pump: Principle and "
             "Capabilities[C]. SPE 18873, 1989. （PCP 原理与能力的经典综述）", False),
            ("(作者见原文) Viscous flow simulations through multi-lobe progressive cavity "
             "pumps[J]. Petroleum Science, 2020. DOI: 10.1007/s12182-020-00458-6 "
             "（内摆线理论、多头泵几何与无量纲参数组）", False),
            ("Andrade S.F.A., Valério J.V., Carvalho M.S. Asymptotic Model of the 3D Flow "
             "in a Progressing-Cavity Pump[J]. SPE Journal, 2011, 16(2): 451-462. "
             "DOI: 10.2118/142294-PA", False),
            ("Paladino E.E., Lima J.A., Almeida R.F.C., Assmann B.W. Computational Modeling "
             "of the Three-Dimensional Flow in a Metallic Stator Progressing Cavity Pump[C]. "
             "SPE 114110, 2008. DOI: 10.2118/114110-MS （基于运动学的网格运动建模）", False),
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
            ("学位论文（硕士）. 螺杆泵宏观动态控制图的应用研究. "
             "（容积效率与井底流压数学模型、动态控制图；知网检索篇名）", False),
        ],
        [
            ("Zheng L., Wu X., Han G., et al. Analytical Model for the Flow in Progressing "
             "Cavity Pump with the Metallic Stator and Rotor in Clearance Fit[J]. "
             "Mathematical Problems in Engineering, 2018. DOI: 10.1155/2018/3696930 "
             "（式(35) Q=Qt−Qs、式(36) ηv=Q/Qt，本模型主公式出处；开放获取）", True),
            ("(Olivet A. 等，署名以原文为准) New Approach for Modeling Progressive Cavity "
             "Pumps Performance[C]. SPE 84137, 2003. DOI: 10.2118/84137-MS "
             "（滑失分解为压差分量+转子运动分量，标定式结构出处）", True),
            ("Pessoa P.A.S., Paladino E.E., de Lima J.A. A Simplified Model for the Flow in "
             "a Progressive Cavity Pump[C]. COBEM 2009, COB09-1951. "
             "（漏失∝w³Δp/μ；湍流时漏失∝Δp^n, n<1；免费 PDF）", True),
            ("(作者见原文) Leakage flow correlation of a progressive cavity pump delivering "
             "shear thinning non-Newtonian fluids[J]. Int. J. Oil, Gas and Coal Technology, "
             "2017. DOI: 10.1504/IJOGCT.2017.086299 （实验回归漏失量的方法学）", True),
            ("Paladino E.E., Lima J.A., Pessoa P.A.S., Almeida R.F.C. A computational model "
             "for the flow within rigid stator progressing cavity pumps[J]. Journal of "
             "Petroleum Science and Engineering, 2011, 78(1): 178-192. "
             "DOI: 10.1016/j.petrol.2011.05.008 （三维瞬态 CFD；级间压差不均的证据）", True),
            ("(作者见原文) A 3D Transient Model for the Multiphase Flow in a "
             "Progressing-Cavity Pump[J]. SPE Journal. DOI: 10.2118/178924-PA "
             "（含气两相流下的漏失与容积效率）", False),
            ("(作者见原文) Study on performance of progressing cavity pumps (PCPs) in "
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
             "大庆石油学院学报, 2004, 28(6): 26-28. "
             "（环空螺旋流理论，负载扭矩计算平均相对误差≤2%）", False),
            ("学位论文（硕士）. 地面驱动螺杆泵抽油杆柱扭转动力学仿真研究. "
             "（理论排量/泵效、进出口压差反扭矩、摩擦反扭矩、启动扭矩；知网检索篇名）", False),
            ("学位论文（硕士）. 地面驱动螺杆泵抽油井生产系统优化设计方法研究与应用. "
             "（杆柱扭矩计算、系统功率与效率计算；知网检索篇名）", False),
            ("学位论文（硕士）. 地面驱动螺杆泵井抽油杆柱强度评价方法研究. "
             "（负载扭矩计算与强度校核；知网检索篇名）", False),
            ("学位论文（硕士）. 大港油田稠油区块电动潜油螺杆泵举升参数优化设计研究. "
             "（ESPCP 井筒温度场、神经网络系统效率预测——电参数与产液关系；知网检索篇名）",
             False),
            ("学位论文（博士）. 螺杆泵工作特性研究及应用. "
             "（抽油杆柱负载扭矩试验与计算、能耗特征分析；知网检索篇名）", False),
        ],
        [
            ("(作者见原文) Complex Fluid Flow and Mechanical Modeling of Metal Progressing "
             "Cavity Pumps PCP's[C]. SPE 150419, 2012. DOI: 10.2118/150419-MS "
             "（金属泵流动+力学联合建模，应力应变与寿命预测）", False),
            ("(作者见原文) Simulation of the operating characteristics of an all-metal "
             "conical screw pump[J]. Scientific Reports, 2025. "
             "DOI: 10.1038/s41598-025-28519-z （扭矩、能效随间隙与转速的变化规律；开放获取）",
             False),
            ("(作者见原文) Study on performance of progressing cavity pumps (PCPs) in "
             "different fit modes[C/J]. 2020. （功率消耗与机械效率对比：过盈摩擦 vs 间隙漏失）",
             False),
            ("(作者见原文) Design of Progressive Cavity Pump Wells[C]. SPE 113324, 2008. "
             "（泵扬程、转速与扭矩的设计计算关系式；Academia.edu 可免费获取）", False),
            ("(作者见原文) A 3D Transient Model for the Multiphase Flow in a "
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
            ("(作者见原文) 全金属螺杆泵工作特性试验模拟与评价[J]. 石油机械, 2018. "
             "（理论排量修正计算方法；容积损失与机械损失随压差/转速的相反趋势；期刊官网免费）",
             False),
            ("(作者见原文) 全金属螺杆泵定转子配合优化及特性试验研究[J]. 石油机械, 2018. "
             "（温度→定转子变形→间隙变化→泵效；最佳间隙 0.1~0.3 mm；期刊官网免费）", False),
            ("学位论文（硕士）. 螺杆泵井生产系统参数优化设计. "
             "（气体影响/漏失影响/综合影响三种容积效率公式，章节结构可作写作模板；"
             "知网检索篇名）", False),
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
            ("(作者见原文) Modeling the performance of progressive cavity pump under "
             "downhole conditions[J]. Journal of Petroleum Science and Engineering, 2020. "
             "（Hooke 定律+复合圆筒理论：井下压力温度→定子变形→间隙修正→漏失修正，"
             "最贴合\"修正模型\"概念，推荐精读）", False),
            ("(作者见原文) Optimizing the Clearance Fit of a Progressive Cavity Pump for "
             "the Thermal Recovery of Petroleum Using Fluid–Structure Thermal Coupling[J]. "
             "ACS Omega, 2022. DOI: 10.1021/acsomega.2c03957 "
             "（流固热耦合计算容积效率，实验偏差<5%；开放获取）", False),
            ("(作者见原文) A Computational Model for Analysis of Fluid-Structure "
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
            ("(作者见原文) A 3D Transient Model for the Multiphase Flow in a "
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
        "说明：本清单服务于论文《电潜螺杆泵运行特性模型》章节（四个子模型各成一节）。"
        "标注\"知网检索篇名\"的文献请在知网/万方以篇名精确检索获取；标注 DOI 的可通过 "
        "doi.org 直达；部分英文文献作者署名请以原文为准。红色文献为已在数字计产模型代码"
        "（espcp_metering / espcp_all_in_one.py）中作为公式依据引用的文献。"
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
