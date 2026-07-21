"""黏温修正模型（修正层）。

把井下实测温度换算为泵内工况黏度，供漏失模型使用。
提供两种实现：

* ArrheniusViscosity —— Arrhenius/Andrade 型解析式 μ(T) = A·exp(B/T)，
  由两个标定点 (T1, μ1)、(T2, μ2) 确定，适合缺乏完整黏温曲线的井；
* ViscosityTable —— 实测黏温曲线的对数插值，点数够时优先使用；
* WaterViscosity —— 纯水黏温解析式（Vogel 型），无需化验；
* EmulsionViscosity —— 油水混合液黏度：按含水率与转相点自动选择
  水包油（水为连续相）或油包水（油为连续相）关系式，
  高含水油田直接用它包裹油相模型即可。

温度单位统一使用摄氏度输入，内部换算为开尔文。
"""

from __future__ import annotations

import math
from bisect import bisect_left
from dataclasses import dataclass
from typing import Protocol, Sequence

KELVIN_OFFSET = 273.15


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
        cls,
        t1_c: float,
        mu1_pas: float,
        t2_c: float,
        mu2_pas: float,
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
      连续相为水，Brinkman 关系
          μm = μw / (1 − φo)^2.5，φo 为油的体积分数
      高含水下 μm 仅比水黏度高百分之几十，对含水率波动不敏感；
    * 含水率 < 转相点（油包水）：
      连续相为油，Guth–Simha 关系
          μm = μo · (1 + 2.5·fw + 14.1·fw²)
      黏度随含水率上升显著增大，在转相点附近达到峰值。

    转相点与原油性质有关，常见 0.5~0.7，缺资料时取默认 0.6；
    有条件时用现场乳化液化验数据修正 inversion_point。

    Attributes:
        oil_model: 油相黏温模型（ViscosityTable / ArrheniusViscosity）
        water_cut: 体积含水率 fw（0~1），用化验含水即可，不需实时测量
        water_model: 水相黏温模型，默认纯水解析式
        inversion_point: 转相点含水率
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
