"""黏温修正模型（修正层）。

把井下实测温度换算为泵内工况黏度，供漏失模型使用。
提供两种实现：

* ArrheniusViscosity —— Arrhenius/Andrade 型解析式 μ(T) = A·exp(B/T)，
  由两个标定点 (T1, μ1)、(T2, μ2) 确定，适合缺乏完整黏温曲线的井；
* ViscosityTable —— 实测黏温曲线的对数插值，点数够时优先使用。

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
