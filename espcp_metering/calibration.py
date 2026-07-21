"""容积效率标定模型（核心层的数据标定部分）。

现场通常拿不到等效间隙等泵内结构参数，因此采用"机理约束 + 数据标定"：
保留机理模型的函数结构

    Qs = k_dp · Δp^α / μ^β  +  k_sh · n

层流缝隙流动理论给出 α = β = 1（漏失 ∝ Δp/μ），此时模型对系数
(k_dp, k_sh) 是线性的，用普通最小二乘即可标定；若数据充足，可在
α 上做一维网格搜索以吸收湍流/非牛顿效应（湍流时 α < 1，
Pessoa et al. 2009）。

标定数据来自单量测试：每条记录包含实测产液量、泵压差、井温、转速。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

from espcp_metering.geometry import PumpGeometry
from espcp_metering.viscosity import ViscosityModel


@dataclass(frozen=True)
class TestRecord:
    """一次单量测试记录。

    Attributes:
        measured_rate_m3d: 实测产液量 [m^3/d]
        total_dp_pa: 泵压差（排出口-吸入口）[Pa]
        temperature_c: 泵挂处井温 [°C]
        speed_rpm: 泵转速 [r/min]
    """

    measured_rate_m3d: float
    total_dp_pa: float
    temperature_c: float
    speed_rpm: float


@dataclass(frozen=True)
class CalibratedSlippageModel:
    """标定后的漏失模型：Qs = k_dp·Δp^α/μ^β + k_sh·n。"""

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
    fit() 可选地在 α 网格上搜索使残差平方和最小的指数。
    """

    def __init__(
        self, geometry: PumpGeometry, viscosity_model: ViscosityModel
    ) -> None:
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
