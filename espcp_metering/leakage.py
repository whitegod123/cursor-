"""排量-漏失机理模型（核心层的机理骨架）。

实际流量 = 理论流量 - 漏失量：

    Q = Qt - Qs,   ηv = Q / Qt

漏失量按缝隙流动理论分解为两个分量（Zheng et al. 2018; SPE 84137;
Pessoa et al. 2009）：

* 压差漏失（Poiseuille 分量）：级间压差驱动的缝隙回流，
      qs_dp = (b·w³ / (12·μ·L)) · Δp_stage
  与间隙三次方成正比、与黏度成反比；
* 剪切漏失（Couette 分量）：转子啮合运动拖带的回流，
      qs_sh = (b·w / 2) · v_rel
  与转速成正比，与压差、黏度无关。

该机理式的作用有二：直接预测（已知间隙等结构参数时），以及
为 calibration.py 的数据标定提供函数结构（漏失 ∝ Δp/μ 与 ∝ n 两项）。
"""

from __future__ import annotations

from dataclasses import dataclass

from espcp_metering.geometry import PumpGeometry

SECONDS_PER_DAY = 86400.0


@dataclass(frozen=True)
class ClearanceGeometry:
    """密封缝隙的等效结构参数（全金属泵取配合间隙，橡胶泵取工况等效间隙）。

    Attributes:
        clearance_m: 等效径向间隙 w [m]
        seal_width_m: 密封线处缝隙的横向宽度 b [m]
        seal_length_m: 沿流动方向的密封长度 L [m]
        parallel_channels: 每级并联漏失通道数（横向+纵向，单头泵典型取 2）
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

    Attributes:
        geometry: 泵几何参数（提供级数和导程）
        clearance: 密封缝隙参数
        shear_coefficient: 剪切漏失修正系数（0~1，剪切分量占理论
            Couette 流量的比例；全金属泵实验表明剪切漏失影响甚微，
            默认取 0.1）
    """

    geometry: PumpGeometry
    clearance: ClearanceGeometry
    shear_coefficient: float = 0.1

    def pressure_slippage_m3d(self, total_dp_pa: float, viscosity_pas: float) -> float:
        """压差漏失分量 [m^3/d]。"""
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
        """剪切漏失分量 [m^3/d]，相对滑动速度近似取导程处的啮合线速度。"""
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
        """实际流量 Q = Qt − Qs [m^3/d]（下限截断为 0）。"""
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        return max(qt - self.slippage_m3d(total_dp_pa, viscosity_pas, speed_rpm), 0.0)

    def volumetric_efficiency(
        self, total_dp_pa: float, viscosity_pas: float, speed_rpm: float
    ) -> float:
        """容积效率 ηv = Q/Qt。"""
        qt = self.geometry.theoretical_rate_m3d(speed_rpm)
        if qt <= 0.0:
            return 0.0
        return self.actual_rate_m3d(total_dp_pa, viscosity_pas, speed_rpm) / qt
