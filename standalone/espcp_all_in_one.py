"""电潜螺杆泵（ESPCP）产液量数字计产模型 —— 单文件完整版。

本文件自包含全部模型与界面，零第三方依赖，直接运行：

    python3 espcp_all_in_one.py demo        # 端到端演示（标定→计产→校核→降级）
    python3 espcp_all_in_one.py web [端口]  # 网页界面，默认 http://127.0.0.1:8000

════════════════════════════════════════════════════════════════════
模型依据一览（代码分区与文献对照，便于下载论文核对）
════════════════════════════════════════════════════════════════════

【A 几何排量模型】PumpGeometry
  公式：q = 4·e·D·T（单头泵每转排量）；Qt = q·n
  依据：Moineau 泵运动学经典结果（几何精确解）
  - Zheng L. et al. Analytical Model for the Flow in Progressing Cavity
    Pump with the Metallic Stator and Rotor in Clearance Fit.
    Mathematical Problems in Engineering, 2018. 文中式(1)。
    DOI: 10.1155/2018/3696930（开放获取，可直接下载）
  - Nguyen T. et al. Modeling the design and performance of progressing
    cavity pump using 3-D vector approach. J. Pet. Sci. Eng., 2014.
    DOI: 10.1016/j.petrol.2014.05.021（多头泵泵因数推广）

【B 黏温 / 乳化液模型】ArrheniusViscosity, ViscosityTable,
  WaterViscosity, EmulsionViscosity
  - 油相黏温 μ(T)=A·exp(B/T)：Arrhenius–Andrade 型经验式（物性学通用）
  - 水黏度 Vogel 式 μw = 2.414e-5·10^(247.8/(T[K]−140))：
    标准物性关系式（0~370 °C 偏差 ≤2.5%），见 CRC Handbook 或
    Al-Shemmeri, Engineering Fluid Mechanics, 2012.
  - 水包油 Brinkman 式 μm = μw/(1−φo)^2.5：
    Brinkman H.C. J. Chem. Phys., 1952, 20:571.
    DOI: 10.1063/1.1700493
  - 油包水 Guth–Simha 式 μm = μo·(1+2.5·fw+14.1·fw²)：
    Guth E., Simha R. Kolloid-Zeitschrift, 1936, 74:266.
    （采油工程中常用于油水乳状液，另见 Woelflin 1942, API Drilling
    and Production Practice）

【C 排量-漏失机理模型】ClearanceGeometry, MechanisticSlippageModel
  公式：压差漏失 qs = b·w³/(12·μ·L)·Δp_stage（平行板缝隙 Poiseuille 流）
        剪切漏失 qs = b·w/2·v_rel（Couette 流）
  依据：
  - 郑磊, 吴晓东, 韩国庆, 等. 全金属螺杆泵间隙漏失模型.
    石油科学通报, 2018, 3(3): 320-331.
    DOI: 10.3969/j.issn.2096-1693.2018.03.029
    （压差—剪切流动漏失模型 + 室内实验验证；PDF 可在
    sykxtb.cup.edu.cn 免费下载）
  - Pessoa P.A.S. et al. A Simplified Model for the Flow in a
    Progressive Cavity Pump. COBEM 2009, 论文号 COB09-1951.
    （文中式(6)：漏失 ∝ w³，湍流时漏失 ∝ Δp^n, n<1；
    PDF 可在 abcm.org.br 免费下载）
  - Zheng et al. 2018（同 A）：式(35) Q = Qt − Qs，式(36) ηv = Q/Qt。
  - 级压差均匀分配假设：简化处理，实际不均，
    见 Paladino E. et al. A computational model for the flow within
    rigid stator progressing cavity pumps. J. Pet. Sci. Eng., 2011,
    78(1):178-192. DOI: 10.1016/j.petrol.2011.05.008（CFD 结果）。

【D 漏失系数标定模型】TestRecord, CalibratedSlippageModel,
  SlippageCalibrator
  公式：Qs = k_dp·Δp^α/μ^β + k_sh·n（最小二乘 + α 网格搜索）
  依据：
  - 两分量分解结构（压差分量 + 转子运动分量）：
    Olivet A. et al.(署名以原文为准) New Approach for Modeling
    Progressive Cavity Pumps Performance. SPE 84137, 2003.
    DOI: 10.2118/84137-MS
  - α<1 吸收湍流效应：Pessoa 2009（同 C）。
  - "实验数据回归漏失量"方法学：
    Karthikeshwaran R. et al.(署名以原文为准) Leakage flow correlation
    of a progressive cavity pump delivering shear thinning
    non-Newtonian fluids. Int. J. Oil, Gas and Coal Technology, 2017.
    DOI: 10.1504/IJOGCT.2017.086299

【E 扭矩-功率模型】TorqueBalance, PowerModel
  公式：M_hydraulic = Δp·q/(2π)（容积泵能量守恒通式）
        M_shaft = P_elec·η_motor·η_trans/ω
  依据：
  - 容积泵扭矩平衡通式（教科书级，任何容积泵文献均可查证）
  - 杨永华, 等. 地面驱动螺杆泵负载扭矩波动机制.
    中国石油大学学报(自然科学版), 2011, 35(5): 120-124.
    DOI: 10.3969/j.issn.1673-5005.2011.05.022
    （螺杆泵负载扭矩 = 水力扭矩 + 摩擦扭矩的分解及黏滑机制）

【F 数字计产主模型】WellSnapshot, MeteringResult, DigitalMeteringModel
  结构：Q = Qt − Qs（Zheng 2018 式(35)），
        压差通道自动切换（实测优先 / 电参数反推降级），
        电参数负载一致性校核。
  "理论排量 − 漏失修正"计产路线的现场应用先例：
  - 中国专利 CN1970991B《一种油井产液量计量、工况分析优化方法
    及其系统》（螺杆泵井产液量计算流程即此结构）。

【G 网页界面】纯标准库 HTTP 服务 + 无状态 JSON API（工程实现，无文献）

重要说明（准确性边界）：
  机理公式提供函数形状，绝对精度由单量测试标定保证（模块 D）。
  本代码经数学自洽性验证（标定可精确还原已知系数），
  未经现场数据验证；投用前请用留出法做盲测（部分测试点标定、
  其余盲测算 MAPE）。
════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import json
import math
import random
import sys
from bisect import bisect_left
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Protocol, Sequence

MINUTES_PER_DAY = 1440.0
SECONDS_PER_DAY = 86400.0
KELVIN_OFFSET = 273.15
MPA = 1.0e6


# ════════════════════════════════════════════════════════════════
# A. 几何排量模型（基础）
#    依据：Moineau 运动学；Zheng et al. 2018 式(1)
# ════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class PumpGeometry:
    """单头螺杆泵结构参数（SI 单位，长度一律用米）。

    Attributes:
        eccentricity_m: 偏心距 e [m]
        rotor_diameter_m: 转子截面直径 D [m]
        stator_lead_m: 定子导程 T [m]（转子导程的 2 倍）
        stages: 泵级数（用于计算级压差，漏失模型需要）
    """

    eccentricity_m: float
    rotor_diameter_m: float
    stator_lead_m: float
    stages: int = 1

    def __post_init__(self) -> None:
        for name in ("eccentricity_m", "rotor_diameter_m", "stator_lead_m"):
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} 必须为正数")
        if self.stages < 1:
            raise ValueError("stages 至少为 1")

    @property
    def displacement_per_rev_m3(self) -> float:
        """每转理论排量 q = 4·e·D·T [m^3/r]。Zheng 2018 式(1)。"""
        return 4.0 * self.eccentricity_m * self.rotor_diameter_m * self.stator_lead_m

    def theoretical_rate_m3d(self, speed_rpm: float) -> float:
        """理论流量 Qt [m^3/d]，speed_rpm 为泵转速 [r/min]。"""
        if speed_rpm < 0.0:
            raise ValueError("转速不能为负")
        return self.displacement_per_rev_m3 * speed_rpm * MINUTES_PER_DAY

    def stage_differential_pressure_pa(self, total_dp_pa: float) -> float:
        """泵总压差平均分配到每一级的级压差 [Pa]（简化假设，见文件头 C 段）。"""
        return total_dp_pa / self.stages


# ════════════════════════════════════════════════════════════════
# B. 黏温 / 乳化液模型（修正）
#    依据：Arrhenius–Andrade 式；Vogel 水黏度式；
#          Brinkman 1952；Guth–Simha 1936
# ════════════════════════════════════════════════════════════════


class ViscosityModel(Protocol):
    """黏温模型接口：输入温度 [°C]，输出动力黏度 [Pa·s]。"""

    def viscosity_pas(self, temperature_c: float) -> float: ...


@dataclass(frozen=True)
class ArrheniusViscosity:
    """Arrhenius 型黏温关系 μ(T) = A·exp(B/T)，T 为热力学温度 [K]。"""

    coefficient_a: float
    coefficient_b: float

    @classmethod
    def from_two_points(
        cls, t1_c: float, mu1_pas: float, t2_c: float, mu2_pas: float
    ) -> "ArrheniusViscosity":
        """由两个实测黏温点标定 A、B。"""
        if mu1_pas <= 0.0 or mu2_pas <= 0.0:
            raise ValueError("黏度必须为正数")
        t1_k = t1_c + KELVIN_OFFSET
        t2_k = t2_c + KELVIN_OFFSET
        if t1_k == t2_k:
            raise ValueError("两个标定点温度不能相同")
        b = math.log(mu1_pas / mu2_pas) / (1.0 / t1_k - 1.0 / t2_k)
        a = mu1_pas / math.exp(b / t1_k)
        return cls(coefficient_a=a, coefficient_b=b)

    def viscosity_pas(self, temperature_c: float) -> float:
        t_k = temperature_c + KELVIN_OFFSET
        if t_k <= 0.0:
            raise ValueError("温度低于绝对零度")
        return self.coefficient_a * math.exp(self.coefficient_b / t_k)


class ViscosityTable:
    """实测黏温曲线：温度升序表，黏度取对数后线性插值（黏温关系近似指数）。"""

    def __init__(
        self, temperatures_c: Sequence[float], viscosities_pas: Sequence[float]
    ) -> None:
        if len(temperatures_c) != len(viscosities_pas):
            raise ValueError("温度与黏度序列长度不一致")
        if len(temperatures_c) < 2:
            raise ValueError("至少需要两个黏温点")
        pairs = sorted(zip(temperatures_c, viscosities_pas))
        self._temps = [p[0] for p in pairs]
        self._log_mus = []
        for _, mu in pairs:
            if mu <= 0.0:
                raise ValueError("黏度必须为正数")
            self._log_mus.append(math.log(mu))
        if len(set(self._temps)) != len(self._temps):
            raise ValueError("存在重复温度点")

    def viscosity_pas(self, temperature_c: float) -> float:
        temps, log_mus = self._temps, self._log_mus
        # 表外按端点斜率外推，避免现场温度略超标定范围时直接报错
        if temperature_c <= temps[0]:
            i0, i1 = 0, 1
        elif temperature_c >= temps[-1]:
            i0, i1 = len(temps) - 2, len(temps) - 1
        else:
            i1 = bisect_left(temps, temperature_c)
            i0 = i1 - 1
        frac = (temperature_c - temps[i0]) / (temps[i1] - temps[i0])
        return math.exp(log_mus[i0] + frac * (log_mus[i1] - log_mus[i0]))


@dataclass(frozen=True)
class WaterViscosity:
    """纯水黏温解析式（Vogel 型）：

        μw = 2.414e-5 · 10^(247.8 / (T[K] − 140))  [Pa·s]

    0~370 °C 范围内与实测偏差约 2.5% 以内，无需化验标定。
    20 °C 时约 1.0 mPa·s，60 °C 时约 0.47 mPa·s。
    矿化度较高的采出水可乘一个 1.05~1.2 的盐度修正系数。
    """

    salinity_factor: float = 1.0

    def viscosity_pas(self, temperature_c: float) -> float:
        t_k = temperature_c + KELVIN_OFFSET
        if t_k <= 140.0:
            raise ValueError("温度超出水黏度解析式适用范围")
        return self.salinity_factor * 2.414e-5 * 10.0 ** (247.8 / (t_k - 140.0))


@dataclass(frozen=True)
class EmulsionViscosity:
    """油水混合液（乳状液）黏度模型，面向含水井尤其是高含水油田。

    以转相点为界自动切换连续相：

    * 含水率 ≥ 转相点（水包油，高含水油田的常态）：
      连续相为水，Brinkman(1952) 关系
          μm = μw / (1 − φo)^2.5，φo 为油的体积分数
      高含水下 μm 仅比水黏度高百分之几十，对含水率波动不敏感；
    * 含水率 < 转相点（油包水）：
      连续相为油，Guth–Simha(1936) 关系
          μm = μo · (1 + 2.5·fw + 14.1·fw²)
      黏度随含水率上升显著增大，在转相点附近达到峰值。

    转相点与原油性质有关，常见 0.5~0.7，缺资料时取默认 0.6。
    """

    oil_model: "ViscosityModel"
    water_cut: float
    water_model: "ViscosityModel" = WaterViscosity()
    inversion_point: float = 0.6

    def __post_init__(self) -> None:
        if not 0.0 <= self.water_cut <= 1.0:
            raise ValueError("含水率必须在 0~1 之间")
        if not 0.0 < self.inversion_point < 1.0:
            raise ValueError("转相点必须在 0~1 之间")

    def viscosity_pas(self, temperature_c: float) -> float:
        fw = self.water_cut
        if fw >= self.inversion_point:
            mu_w = self.water_model.viscosity_pas(temperature_c)
            oil_fraction = 1.0 - fw
            return mu_w / (1.0 - oil_fraction) ** 2.5
        mu_o = self.oil_model.viscosity_pas(temperature_c)
        return mu_o * (1.0 + 2.5 * fw + 14.1 * fw * fw)

    def with_water_cut(self, water_cut: float) -> "EmulsionViscosity":
        """含水率变化后（如月度化验更新）生成新模型，其余参数不变。"""
        return EmulsionViscosity(
            oil_model=self.oil_model,
            water_cut=water_cut,
            water_model=self.water_model,
            inversion_point=self.inversion_point,
        )


# ════════════════════════════════════════════════════════════════
# C. 排量-漏失机理模型（核心·机理骨架）
#    依据：郑磊等 2018（压差—剪切漏失模型）；Pessoa 2009 式(6)；
#          Zheng 2018 式(35)(36)
# ════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class ClearanceGeometry:
    """密封缝隙的等效结构参数（全金属泵取配合间隙，橡胶泵取工况等效间隙）。

    注意：这是对郑磊 2018 中线接触润滑理论严格解的等效简化，
    绝对值有偏差，建议仅用于趋势分析；计产请用 D 段的标定模型。
    """

    clearance_m: float
    seal_width_m: float
    seal_length_m: float
    parallel_channels: int = 2

    def __post_init__(self) -> None:
        for name in ("clearance_m", "seal_width_m", "seal_length_m"):
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} 必须为正数")
        if self.parallel_channels < 1:
            raise ValueError("parallel_channels 至少为 1")


@dataclass(frozen=True)
class MechanisticSlippageModel:
    """基于缝隙流动的机理漏失模型。

    压差漏失：平行板缝隙 Poiseuille 流经典解（漏失 ∝ w³Δp/μ，
    Pessoa 2009 式(6) 同构）；剪切漏失：Couette 流经典解。
    剪切修正系数默认 0.1 为经验值（郑磊 2018 实验表明剪切漏失影响甚微）。
    """

    geometry: PumpGeometry
    clearance: ClearanceGeometry
    shear_coefficient: float = 0.1

    def pressure_slippage_m3d(self, total_dp_pa: float, viscosity_pas: float) -> float:
        """压差漏失分量 [m^3/d]：qs = b·w³/(12·μ·L)·Δp_stage。"""
        if viscosity_pas <= 0.0:
            raise ValueError("黏度必须为正数")
        dp_stage = self.geometry.stage_differential_pressure_pa(total_dp_pa)
        c = self.clearance
        q_per_channel = (
            c.seal_width_m
            * c.clearance_m**3
            / (12.0 * viscosity_pas * c.seal_length_m)
            * dp_stage
        )
        return q_per_channel * c.parallel_channels * SECONDS_PER_DAY

    def shear_slippage_m3d(self, speed_rpm: float) -> float:
        """剪切漏失分量 [m^3/d]：qs = b·w/2·v_rel（Couette 流）。"""
        v_rel = self.geometry.stator_lead_m * speed_rpm / 60.0
        c = self.clearance
        q_per_channel = 0.5 * c.seal_width_m * c.clearance_m * v_rel
        return (
            q_per_channel
            * c.parallel_channels
            * self.shear_coefficient
            * SECONDS_PER_DAY
        )

    def slippage_m3d(
        self, total_dp_pa: float, viscosity_pas: float, speed_rpm: float
    ) -> float:
        """总漏失量 Qs [m^3/d]。"""
        return self.pressure_slippage_m3d(
            total_dp_pa, viscosity_pas
        ) + self.shear_slippage_m3d(speed_rpm)

    def actual_rate_m3d(
        self, total_dp_pa: float, viscosity_pas: float, speed_rpm: float
    ) -> float:
        """实际流量 Q = Qt − Qs（Zheng 2018 式(35)），下限截断为 0。"""
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        return max(qt - self.slippage_m3d(total_dp_pa, viscosity_pas, speed_rpm), 0.0)

    def volumetric_efficiency(
        self, total_dp_pa: float, viscosity_pas: float, speed_rpm: float
    ) -> float:
        """容积效率 ηv = Q/Qt（Zheng 2018 式(36)）。"""
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        if qt <= 0.0:
            return 0.0
        return self.actual_rate_m3d(total_dp_pa, viscosity_pas, speed_rpm) / qt


# ════════════════════════════════════════════════════════════════
# D. 漏失系数标定模型（核心·数据标定）
#    依据：SPE 84137（两分量分解）；Pessoa 2009（α<1 湍流）；
#          IJOGCT 2017（回归方法学）
# ════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class TestRecord:
    """一次单量测试记录。

    注：类名以 Test 开头，声明 __test__ = False 防止 pytest 误收集。

    Attributes:
        measured_rate_m3d: 实测产液量 [m^3/d]
        total_dp_pa: 泵压差（排出口-吸入口）[Pa]
        temperature_c: 泵挂处井温 [°C]
        speed_rpm: 泵转速 [r/min]
    """

    __test__ = False

    measured_rate_m3d: float
    total_dp_pa: float
    temperature_c: float
    speed_rpm: float


@dataclass(frozen=True)
class CalibratedSlippageModel:
    """标定后的漏失模型：Qs = k_dp·Δp^α/μ^β + k_sh·n。

    函数结构取自机理（C 段），系数由单量测试数据确定，
    机理式的系统性偏差（等效几何、压差分配、黏度绝对值）被系数吸收。
    """

    geometry: PumpGeometry
    viscosity_model: ViscosityModel
    k_dp: float
    k_sh: float
    alpha: float = 1.0
    beta: float = 1.0

    def slippage_m3d(
        self, total_dp_pa: float, temperature_c: float, speed_rpm: float
    ) -> float:
        mu = self.viscosity_model.viscosity_pas(temperature_c)
        dp = max(total_dp_pa, 0.0)
        return self.k_dp * dp**self.alpha / mu**self.beta + self.k_sh * speed_rpm

    def actual_rate_m3d(
        self, total_dp_pa: float, temperature_c: float, speed_rpm: float
    ) -> float:
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        return max(qt - self.slippage_m3d(total_dp_pa, temperature_c, speed_rpm), 0.0)

    def volumetric_efficiency(
        self, total_dp_pa: float, temperature_c: float, speed_rpm: float
    ) -> float:
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        if qt <= 0.0:
            return 0.0
        return self.actual_rate_m3d(total_dp_pa, temperature_c, speed_rpm) / qt


class SlippageCalibrator:
    """用单量测试数据标定漏失系数。

    对固定的 (α, β)，模型对 (k_dp, k_sh) 线性，直接解 2×2 正规方程；
    fit() 可选地在 α 网格上搜索使残差平方和最小的指数（湍流 α<1）。
    """

    def __init__(self, geometry: PumpGeometry, viscosity_model: ViscosityModel) -> None:
        self._geometry = geometry
        self._viscosity_model = viscosity_model

    def fit(
        self,
        records: Sequence[TestRecord],
        alpha_grid: Sequence[float] = (1.0,),
        beta: float = 1.0,
        allow_negative_shear: bool = False,
    ) -> CalibratedSlippageModel:
        """标定并返回可用的漏失模型。

        Args:
            records: 单量测试记录（至少 2 条；建议覆盖不同压差与转速）
            alpha_grid: 压差指数候选值，默认只用层流理论值 1.0
            beta: 黏度指数，层流理论值 1.0
            allow_negative_shear: 数据噪声大时剪切项可能拟出负值，
                默认将其截为 0 并退化为单参数标定
        """
        if len(records) < 2:
            raise ValueError("标定至少需要 2 条测试记录")

        slippages = []
        for r in records:
            qt = self._geometry.theoretical_rate_m3d(r.speed_rpm)
            qs = qt - r.measured_rate_m3d
            if qs < 0.0:
                raise ValueError(
                    f"实测产液量 {r.measured_rate_m3d} m3/d 超过理论排量 "
                    f"{qt:.1f} m3/d，请检查泵参数或数据"
                )
            slippages.append(qs)

        best: CalibratedSlippageModel | None = None
        best_sse = math.inf
        for alpha in alpha_grid:
            k_dp, k_sh = self._solve(records, slippages, alpha, beta)
            if k_sh < 0.0 and not allow_negative_shear:
                k_dp = self._solve_dp_only(records, slippages, alpha, beta)
                k_sh = 0.0
            k_dp = max(k_dp, 0.0)
            sse = self._sse(records, slippages, k_dp, k_sh, alpha, beta)
            if sse < best_sse:
                best_sse = sse
                best = CalibratedSlippageModel(
                    geometry=self._geometry,
                    viscosity_model=self._viscosity_model,
                    k_dp=k_dp,
                    k_sh=k_sh,
                    alpha=alpha,
                    beta=beta,
                )
        assert best is not None
        return best

    def _features(
        self, record: TestRecord, alpha: float, beta: float
    ) -> tuple[float, float]:
        mu = self._viscosity_model.viscosity_pas(record.temperature_c)
        x_dp = max(record.total_dp_pa, 0.0) ** alpha / mu**beta
        return x_dp, record.speed_rpm

    def _solve(
        self,
        records: Sequence[TestRecord],
        slippages: Sequence[float],
        alpha: float,
        beta: float,
    ) -> tuple[float, float]:
        """最小二乘解 2 参数正规方程 (X^T X) k = X^T y。"""
        s_aa = s_ab = s_bb = s_ay = s_by = 0.0
        for r, y in zip(records, slippages):
            a, b = self._features(r, alpha, beta)
            s_aa += a * a
            s_ab += a * b
            s_bb += b * b
            s_ay += a * y
            s_by += b * y
        det = s_aa * s_bb - s_ab * s_ab
        if abs(det) < 1e-30:
            # 特征共线（如所有测试同转速）：退化为单参数压差标定
            return self._solve_dp_only(records, slippages, alpha, beta), 0.0
        k_dp = (s_bb * s_ay - s_ab * s_by) / det
        k_sh = (s_aa * s_by - s_ab * s_ay) / det
        return k_dp, k_sh

    def _solve_dp_only(
        self,
        records: Sequence[TestRecord],
        slippages: Sequence[float],
        alpha: float,
        beta: float,
    ) -> float:
        num = den = 0.0
        for r, y in zip(records, slippages):
            a, _ = self._features(r, alpha, beta)
            num += a * y
            den += a * a
        return num / den if den > 0.0 else 0.0

    def _sse(
        self,
        records: Sequence[TestRecord],
        slippages: Sequence[float],
        k_dp: float,
        k_sh: float,
        alpha: float,
        beta: float,
    ) -> float:
        sse = 0.0
        for r, y in zip(records, slippages):
            a, b = self._features(r, alpha, beta)
            sse += (y - k_dp * a - k_sh * b) ** 2
        return sse


# ════════════════════════════════════════════════════════════════
# E. 扭矩-功率模型（校核/备用）
#    依据：容积泵能量守恒通式；杨永华等 2011（扭矩分解）
# ════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class TorqueBalance:
    """泵轴扭矩分解结果 [N·m]。"""

    shaft_torque_nm: float
    hydraulic_torque_nm: float
    friction_torque_nm: float

    @property
    def residual_nm(self) -> float:
        """扭矩不平衡量：轴扭矩 −（水力 + 摩擦）。"""
        return self.shaft_torque_nm - self.hydraulic_torque_nm - self.friction_torque_nm

    @property
    def relative_residual(self) -> float:
        """相对不平衡度（以轴扭矩为基准）。"""
        if self.shaft_torque_nm <= 0.0:
            return 0.0
        return self.residual_nm / self.shaft_torque_nm


@dataclass(frozen=True)
class PowerModel:
    """电参数 → 泵轴扭矩/压差的换算模型。

    M_hydraulic = Δp·q/(2π)：容积泵能量守恒（每转做功 W = Δp·q = 2π·M）。
    电机效率取恒定值为简化，轻载时偏差增大（见文件头准确性边界说明）。
    """

    geometry: PumpGeometry
    motor_efficiency: float = 0.85
    transmission_efficiency: float = 0.95
    friction_torque_nm: float = 0.0
    check_threshold: float = 0.15

    def shaft_torque_nm(self, electrical_power_w: float, speed_rpm: float) -> float:
        """由电功率和转速计算泵轴扭矩 [N·m]。"""
        if speed_rpm <= 0.0:
            raise ValueError("转速必须为正数")
        omega = 2.0 * math.pi * speed_rpm / 60.0
        p_shaft = (
            electrical_power_w * self.motor_efficiency * self.transmission_efficiency
        )
        return p_shaft / omega

    def hydraulic_torque_nm(self, total_dp_pa: float) -> float:
        """由泵压差计算水力扭矩 [N·m]：M = Δp·q/(2π)。"""
        return total_dp_pa * self.geometry.displacement_per_rev_m3 / (2.0 * math.pi)

    def torque_balance(
        self, electrical_power_w: float, speed_rpm: float, total_dp_pa: float
    ) -> TorqueBalance:
        """扭矩平衡分解，用于负载校核。"""
        return TorqueBalance(
            shaft_torque_nm=self.shaft_torque_nm(electrical_power_w, speed_rpm),
            hydraulic_torque_nm=self.hydraulic_torque_nm(total_dp_pa),
            friction_torque_nm=self.friction_torque_nm,
        )

    def load_check_ok(
        self, electrical_power_w: float, speed_rpm: float, total_dp_pa: float
    ) -> bool:
        """负载一致性校核：True 表示电参数与压差数据自洽。"""
        balance = self.torque_balance(electrical_power_w, speed_rpm, total_dp_pa)
        return abs(balance.relative_residual) <= self.check_threshold

    def estimate_dp_pa(self, electrical_power_w: float, speed_rpm: float) -> float:
        """压力计失效时的备用通道：Δp = (M_shaft − M_friction)·2π/q。"""
        m_shaft = self.shaft_torque_nm(electrical_power_w, speed_rpm)
        m_hydraulic = max(m_shaft - self.friction_torque_nm, 0.0)
        return m_hydraulic * 2.0 * math.pi / self.geometry.displacement_per_rev_m3


# ════════════════════════════════════════════════════════════════
# F. 数字计产主模型（主入口）
#    结构：Q = Qt − Qs（Zheng 2018 式(35)）+ 压差通道切换 + 负载校核
# ════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class WellSnapshot:
    """一个计产时刻的实时生产数据。

    Attributes:
        speed_rpm: 泵转速 [r/min]（变频器）
        temperature_c: 泵挂处井温 [°C]
        intake_pressure_pa: 泵吸入口压力 [Pa]，缺失填 None
        discharge_pressure_pa: 泵排出口压力 [Pa]，缺失填 None
        electrical_power_w: 电机输入有功功率 [W]，缺失填 None
    """

    speed_rpm: float
    temperature_c: float
    intake_pressure_pa: float | None = None
    discharge_pressure_pa: float | None = None
    electrical_power_w: float | None = None

    @property
    def measured_dp_pa(self) -> float | None:
        if self.intake_pressure_pa is None or self.discharge_pressure_pa is None:
            return None
        return self.discharge_pressure_pa - self.intake_pressure_pa


@dataclass(frozen=True)
class MeteringResult:
    """计产输出。

    Attributes:
        rate_m3d: 估算产液量 [m^3/d]
        theoretical_rate_m3d: 理论排量 [m^3/d]
        slippage_m3d: 漏失量 [m^3/d]
        volumetric_efficiency: 容积效率
        dp_pa: 计算使用的泵压差 [Pa]
        dp_source: 压差来源，"measured" 或 "power_fallback"
        load_check_ok: 负载校核结果；无电参数或走降级通道时为 None
    """

    rate_m3d: float
    theoretical_rate_m3d: float
    slippage_m3d: float
    volumetric_efficiency: float
    dp_pa: float
    dp_source: str
    load_check_ok: bool | None


class DigitalMeteringModel:
    """电潜螺杆泵产液量数字计产模型。

    Args:
        slippage_model: 标定后的漏失模型（含几何与黏温模型）
        power_model: 扭矩-功率模型；提供后才具备负载校核与压差降级能力
    """

    def __init__(
        self,
        slippage_model: CalibratedSlippageModel,
        power_model: PowerModel | None = None,
    ) -> None:
        self._slippage = slippage_model
        self._power = power_model

    def estimate(self, snapshot: WellSnapshot) -> MeteringResult:
        """由一个时刻的生产数据估算产液量。"""
        dp, dp_source = self._resolve_dp(snapshot)

        load_check_ok: bool | None = None
        if (
            self._power is not None
            and dp_source == "measured"
            and snapshot.electrical_power_w is not None
            and snapshot.speed_rpm > 0.0
        ):
            load_check_ok = self._power.load_check_ok(
                snapshot.electrical_power_w, snapshot.speed_rpm, dp
            )

        qt = self._slippage.geometry.theoretical_rate_m3d(snapshot.speed_rpm)
        qs = self._slippage.slippage_m3d(dp, snapshot.temperature_c, snapshot.speed_rpm)
        q = max(qt - qs, 0.0)
        eta_v = q / qt if qt > 0.0 else 0.0
        return MeteringResult(
            rate_m3d=q,
            theoretical_rate_m3d=qt,
            slippage_m3d=min(qs, qt),
            volumetric_efficiency=eta_v,
            dp_pa=dp,
            dp_source=dp_source,
            load_check_ok=load_check_ok,
        )

    def _resolve_dp(self, snapshot: WellSnapshot) -> tuple[float, str]:
        dp = snapshot.measured_dp_pa
        if dp is not None:
            return dp, "measured"
        if (
            self._power is not None
            and snapshot.electrical_power_w is not None
            and snapshot.speed_rpm > 0.0
        ):
            return (
                self._power.estimate_dp_pa(
                    snapshot.electrical_power_w, snapshot.speed_rpm
                ),
                "power_fallback",
            )
        raise ValueError(
            "泵压差不可用：吸入/排出压力缺失，且未配置扭矩-功率模型"
            "（或缺少电功率数据），无法计产"
        )


# ════════════════════════════════════════════════════════════════
# G. 网页界面（工程实现：纯标准库 HTTP 服务 + 无状态 JSON API）
# ════════════════════════════════════════════════════════════════


def compute(payload: dict[str, Any]) -> dict[str, Any]:
    """无状态计算入口：payload（SI 单位）→ 标定结果 + 计产结果。"""
    g = payload["geometry"]
    geometry = PumpGeometry(
        eccentricity_m=float(g["eccentricity_m"]),
        rotor_diameter_m=float(g["rotor_diameter_m"]),
        stator_lead_m=float(g["stator_lead_m"]),
        stages=int(g["stages"]),
    )

    v = payload["viscosity"]
    oil = ArrheniusViscosity.from_two_points(
        float(v["t1_c"]), float(v["mu1_pas"]), float(v["t2_c"]), float(v["mu2_pas"])
    )
    viscosity = EmulsionViscosity(
        oil_model=oil,
        water_cut=float(v["water_cut"]),
        inversion_point=float(v.get("inversion_point", 0.6)),
    )

    records = [
        TestRecord(
            measured_rate_m3d=float(r["measured_rate_m3d"]),
            total_dp_pa=float(r["total_dp_pa"]),
            temperature_c=float(r["temperature_c"]),
            speed_rpm=float(r["speed_rpm"]),
        )
        for r in payload["records"]
    ]
    alpha_grid = tuple(payload.get("alpha_grid", (0.6, 0.8, 1.0)))
    slippage = SlippageCalibrator(geometry, viscosity).fit(records, alpha_grid=alpha_grid)

    power = None
    p = payload.get("power")
    if p:
        power = PowerModel(
            geometry=geometry,
            motor_efficiency=float(p.get("motor_efficiency", 0.85)),
            transmission_efficiency=float(p.get("transmission_efficiency", 0.95)),
            friction_torque_nm=float(p.get("friction_torque_nm", 0.0)),
        )

    model = DigitalMeteringModel(slippage, power)
    s = payload["snapshot"]

    def _opt(key: str) -> float | None:
        value = s.get(key)
        return None if value in (None, "") else float(value)

    result = model.estimate(
        WellSnapshot(
            speed_rpm=float(s["speed_rpm"]),
            temperature_c=float(s["temperature_c"]),
            intake_pressure_pa=_opt("intake_pressure_pa"),
            discharge_pressure_pa=_opt("discharge_pressure_pa"),
            electrical_power_w=_opt("electrical_power_w"),
        )
    )
    return {
        "calibration": {
            "k_dp": slippage.k_dp,
            "k_sh": slippage.k_sh,
            "alpha": slippage.alpha,
            "beta": slippage.beta,
        },
        "result": {
            "rate_m3d": result.rate_m3d,
            "theoretical_rate_m3d": result.theoretical_rate_m3d,
            "slippage_m3d": result.slippage_m3d,
            "volumetric_efficiency": result.volumetric_efficiency,
            "dp_pa": result.dp_pa,
            "dp_source": result.dp_source,
            "load_check_ok": result.load_check_ok,
        },
    }


PAGE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>电潜螺杆泵数字计产</title>
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --line: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --ok: #4ade80; --warn: #f87171;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px; background: var(--bg); color: var(--text);
    font: 15px/1.6 system-ui, "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color: var(--muted); margin-bottom: 20px; font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; }
  .card h2 { font-size: 15px; margin: 0 0 12px; color: var(--accent); }
  label { display: block; font-size: 12px; color: var(--muted); margin: 8px 0 2px; }
  input {
    width: 100%; padding: 7px 10px; border-radius: 8px; border: 1px solid var(--line);
    background: #0b1220; color: var(--text); font-size: 14px;
  }
  input:focus { outline: 1px solid var(--accent); }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 4px 6px; text-align: center; }
  th { color: var(--muted); font-weight: normal; font-size: 12px; }
  td input { padding: 5px 6px; font-size: 13px; }
  button {
    cursor: pointer; border: none; border-radius: 8px; font-size: 14px;
    padding: 8px 14px; background: #334155; color: var(--text);
  }
  button:hover { filter: brightness(1.15); }
  .primary {
    background: var(--accent); color: #082f49; font-weight: 600;
    padding: 12px 28px; font-size: 16px; width: 100%; margin-top: 16px;
  }
  .small { padding: 4px 10px; font-size: 12px; }
  #result { margin-top: 20px; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
  .kpi { background: #0b1220; border: 1px solid var(--line); border-radius: 10px; padding: 12px; text-align: center; }
  .kpi .v { font-size: 24px; font-weight: 700; color: var(--accent); }
  .kpi .l { font-size: 12px; color: var(--muted); }
  .ok { color: var(--ok); } .warn { color: var(--warn); }
  .err { color: var(--warn); margin-top: 12px; white-space: pre-wrap; }
  .meta { color: var(--muted); font-size: 13px; margin-top: 10px; }
</style>
</head>
<body>
<h1>电潜螺杆泵产液量数字计产</h1>
<div class="sub">机理约束 + 数据标定 | 理论排量 − 漏失修正 | 电参数校核与降级</div>

<div class="grid">
  <div class="card">
    <h2>1. 泵结构参数（铭牌）</h2>
    <div class="row">
      <div><label>偏心距 e (mm)</label><input id="ecc" value="4.0"></div>
      <div><label>转子直径 D (mm)</label><input id="dia" value="40.0"></div>
    </div>
    <div class="row">
      <div><label>定子导程 T (mm)</label><input id="lead" value="200.0"></div>
      <div><label>级数</label><input id="stages" value="24"></div>
    </div>
  </div>

  <div class="card">
    <h2>2. 井液黏度（高含水乳化液模型）</h2>
    <div class="row">
      <div><label>含水率 (%)</label><input id="wc" value="90"></div>
      <div><label>转相点 (%)</label><input id="inv" value="60"></div>
    </div>
    <label>油相黏温两点（低含水井才重要）</label>
    <div class="row">
      <div><label>T1 (°C)</label><input id="t1" value="50"></div>
      <div><label>μ1 (mPa·s)</label><input id="mu1" value="1000"></div>
    </div>
    <div class="row">
      <div><label>T2 (°C)</label><input id="t2" value="80"></div>
      <div><label>μ2 (mPa·s)</label><input id="mu2" value="120"></div>
    </div>
  </div>

  <div class="card">
    <h2>3. 扭矩-功率模型（可选，用于校核/降级）</h2>
    <div class="row3">
      <div><label>电机效率</label><input id="etam" value="0.85"></div>
      <div><label>传动效率</label><input id="etat" value="0.95"></div>
      <div><label>摩擦扭矩 (N·m)</label><input id="mf" value="25"></div>
    </div>
    <div class="meta">三项留空则不启用电参数校核与压差降级。</div>
  </div>

  <div class="card" style="grid-column: 1 / -1;">
    <h2>4. 单量测试标定记录（建议 ≥ 5 条，覆盖不同压差与转速）</h2>
    <table id="rectab">
      <thead><tr>
        <th>实测产液量 (m³/d)</th><th>泵压差 (MPa)</th><th>井温 (°C)</th><th>转速 (r/min)</th><th></th>
      </tr></thead>
      <tbody></tbody>
    </table>
    <button class="small" onclick="addRow()" style="margin-top:8px;">+ 添加记录</button>
  </div>

  <div class="card" style="grid-column: 1 / -1;">
    <h2>5. 实时数据（当前时刻）</h2>
    <div class="row3">
      <div><label>转速 (r/min) *</label><input id="s_n" value="150"></div>
      <div><label>井温 (°C) *</label><input id="s_t" value="60"></div>
      <div><label>电功率 (kW)</label><input id="s_p" value=""></div>
    </div>
    <div class="row">
      <div><label>泵吸入口压力 (MPa)</label><input id="s_pin" value="3.0"></div>
      <div><label>泵排出口压力 (MPa)</label><input id="s_pout" value="7.2"></div>
    </div>
    <div class="meta">压力缺失且填了电功率时，自动走电参数降级通道反推压差。</div>
    <button class="primary" onclick="run()">标定并计产</button>
  </div>
</div>

<div id="result"></div>

<script>
const DEFAULT_RECORDS = [
  [23.5, 2.0, 55, 100],
  [27.8, 3.5, 58, 120],
  [24.9, 4.0, 60, 150],
  [23.9, 5.0, 62, 150],
  [34.2, 4.5, 61, 200],
  [44.1, 3.0, 57, 250],
];

function addRow(vals) {
  const tb = document.querySelector('#rectab tbody');
  const tr = document.createElement('tr');
  const v = vals || ['', '', '', ''];
  tr.innerHTML = v.map(x => `<td><input value="${x}"></td>`).join('')
    + `<td><button class="small" onclick="this.closest('tr').remove()">删除</button></td>`;
  tb.appendChild(tr);
}
DEFAULT_RECORDS.forEach(r => addRow(r));

const num = id => parseFloat(document.getElementById(id).value);
const opt = id => {
  const s = document.getElementById(id).value.trim();
  return s === '' ? null : parseFloat(s);
};

function buildPayload() {
  const records = [...document.querySelectorAll('#rectab tbody tr')].map(tr => {
    const c = [...tr.querySelectorAll('input')].map(i => parseFloat(i.value));
    return {
      measured_rate_m3d: c[0],
      total_dp_pa: c[1] * 1e6,
      temperature_c: c[2],
      speed_rpm: c[3],
    };
  }).filter(r => !Object.values(r).some(Number.isNaN));

  const etam = opt('etam'), etat = opt('etat'), mf = opt('mf');
  const power = (etam === null && etat === null && mf === null) ? null : {
    motor_efficiency: etam ?? 0.85,
    transmission_efficiency: etat ?? 0.95,
    friction_torque_nm: mf ?? 0.0,
  };
  const pkw = opt('s_p'), pin = opt('s_pin'), pout = opt('s_pout');
  return {
    geometry: {
      eccentricity_m: num('ecc') / 1e3,
      rotor_diameter_m: num('dia') / 1e3,
      stator_lead_m: num('lead') / 1e3,
      stages: num('stages'),
    },
    viscosity: {
      water_cut: num('wc') / 100,
      inversion_point: num('inv') / 100,
      t1_c: num('t1'), mu1_pas: num('mu1') / 1e3,
      t2_c: num('t2'), mu2_pas: num('mu2') / 1e3,
    },
    power,
    records,
    alpha_grid: [0.6, 0.8, 1.0],
    snapshot: {
      speed_rpm: num('s_n'),
      temperature_c: num('s_t'),
      intake_pressure_pa: pin === null ? null : pin * 1e6,
      discharge_pressure_pa: pout === null ? null : pout * 1e6,
      electrical_power_w: pkw === null ? null : pkw * 1e3,
    },
  };
}

async function run() {
  const box = document.getElementById('result');
  box.innerHTML = '<div class="meta">计算中…</div>';
  try {
    const resp = await fetch('/api/estimate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(buildPayload()),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || resp.statusText);
    const r = data.result, c = data.calibration;
    const check = r.load_check_ok === null ? '未校核'
      : r.load_check_ok ? '<span class="ok">通过</span>' : '<span class="warn">报警</span>';
    const src = r.dp_source === 'measured' ? '实测压力' : '电参数反推（降级）';
    box.innerHTML = `
      <div class="card">
        <h2>计产结果</h2>
        <div class="kpis">
          <div class="kpi"><div class="v">${r.rate_m3d.toFixed(1)}</div><div class="l">产液量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${r.theoretical_rate_m3d.toFixed(1)}</div><div class="l">理论排量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${r.slippage_m3d.toFixed(1)}</div><div class="l">漏失量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${(r.volumetric_efficiency * 100).toFixed(1)}%</div><div class="l">容积效率</div></div>
          <div class="kpi"><div class="v">${(r.dp_pa / 1e6).toFixed(2)}</div><div class="l">泵压差 (MPa)</div></div>
        </div>
        <div class="meta">
          压差来源：${src} ｜ 负载校核：${check}<br>
          标定系数：k_dp = ${c.k_dp.toExponential(3)}，k_sh = ${c.k_sh.toFixed(4)}，α = ${c.alpha}，β = ${c.beta}
        </div>
      </div>`;
  } catch (e) {
    box.innerHTML = `<div class="err">计算失败：${e.message}</div>`;
  }
}
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/estimate":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            response, status = compute(payload), 200
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            response, status = {"error": str(exc)}, 400
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")


def serve(port: int = 8000) -> None:
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"电潜螺杆泵数字计产界面已启动：http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


# ════════════════════════════════════════════════════════════════
# 演示：标定 → 计产 → 校核 → 降级
# ════════════════════════════════════════════════════════════════


def demo() -> None:
    """端到端演示（合成数据），实际使用时替换为现场数据即可。"""
    geometry = PumpGeometry(
        eccentricity_m=0.004,
        rotor_diameter_m=0.040,
        stator_lead_m=0.200,
        stages=24,
    )
    print(f"每转理论排量 q = {geometry.displacement_per_rev_m3 * 1e3:.4f} L/r")
    print(f"150 r/min 理论排量 Qt = {geometry.theoretical_rate_m3d(150):.1f} m3/d\n")

    # 高含水井：油相黏温随便给个量级正确的值即可
    oil = ArrheniusViscosity.from_two_points(50.0, 1.0, 80.0, 0.12)
    viscosity = EmulsionViscosity(oil_model=oil, water_cut=0.90)

    # 合成"单量测试数据"（真值系数 + 0.5% 计量噪声）
    # 注意：高含水井液黏度约 0.0006 Pa·s，k_dp 量级须与之匹配
    k_dp_true, k_sh_true = 4.0e-10, 0.008
    rng = random.Random(42)
    records = []
    for dp_mpa, t_c, n in [
        (2.0, 55.0, 100.0),
        (3.5, 58.0, 120.0),
        (4.0, 60.0, 150.0),
        (5.0, 62.0, 150.0),
        (4.5, 61.0, 200.0),
        (3.0, 57.0, 250.0),
    ]:
        mu = viscosity.viscosity_pas(t_c)
        qs = k_dp_true * dp_mpa * MPA / mu + k_sh_true * n
        qt = geometry.theoretical_rate_m3d(n)
        q_meas = (qt - qs) * (1.0 + rng.gauss(0.0, 0.005))
        records.append(TestRecord(q_meas, dp_mpa * MPA, t_c, n))

    slippage = SlippageCalibrator(geometry, viscosity).fit(
        records, alpha_grid=(0.8, 0.9, 1.0)
    )
    print("── 标定结果 ──")
    print(f"k_dp = {slippage.k_dp:.3e}  (真值 {k_dp_true:.3e})")
    print(f"k_sh = {slippage.k_sh:.4f}  (真值 {k_sh_true:.4f})")
    print(f"alpha = {slippage.alpha}\n")

    power = PowerModel(
        geometry=geometry,
        motor_efficiency=0.85,
        transmission_efficiency=0.95,
        friction_torque_nm=25.0,
    )
    model = DigitalMeteringModel(slippage, power)

    def electric_power_for(dp_pa: float, n: float) -> float:
        m = power.hydraulic_torque_nm(dp_pa) + power.friction_torque_nm
        return m * (2.0 * math.pi * n / 60.0) / (0.85 * 0.95)

    snapshots = {
        "正常工况（压力+电参齐全）": WellSnapshot(
            speed_rpm=150.0,
            temperature_c=60.0,
            intake_pressure_pa=3.0 * MPA,
            discharge_pressure_pa=7.2 * MPA,
            electrical_power_w=electric_power_for(4.2 * MPA, 150.0),
        ),
        "泵磨损（功率异常升高）": WellSnapshot(
            speed_rpm=150.0,
            temperature_c=60.0,
            intake_pressure_pa=3.0 * MPA,
            discharge_pressure_pa=7.2 * MPA,
            electrical_power_w=electric_power_for(4.2 * MPA, 150.0) * 1.4,
        ),
        "压力计失效（电参降级计产）": WellSnapshot(
            speed_rpm=150.0,
            temperature_c=60.0,
            electrical_power_w=electric_power_for(4.2 * MPA, 150.0),
        ),
    }

    print("── 实时计产 ──")
    for name, snap in snapshots.items():
        result = model.estimate(snap)
        check = {True: "通过", False: "报警", None: "未校核"}[result.load_check_ok]
        print(f"[{name}]")
        print(
            f"  产液量 {result.rate_m3d:.1f} m3/d"
            f"（理论 {result.theoretical_rate_m3d:.1f}，"
            f"漏失 {result.slippage_m3d:.1f}，"
            f"ηv = {result.volumetric_efficiency:.1%}）"
        )
        print(
            f"  压差 {result.dp_pa / MPA:.2f} MPa"
            f"（来源: {result.dp_source}），负载校核: {check}\n"
        )


if __name__ == "__main__":
    # Windows 中文控制台（GBK）编不了 ³/η 等字符，强制 UTF-8 输出
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    if len(sys.argv) >= 2 and sys.argv[1] == "web":
        serve(int(sys.argv[2]) if len(sys.argv) > 2 else 8000)
    elif len(sys.argv) >= 2 and sys.argv[1] == "demo":
        demo()
    else:
        print(__doc__.split("═")[0])
        print("用法：")
        print("  python3 espcp_all_in_one.py demo        # 端到端演示")
        print("  python3 espcp_all_in_one.py web [端口]  # 网页界面")
