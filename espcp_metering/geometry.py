"""几何排量模型（基础层）。

单头单螺杆泵（1/2 头数比）的理论排量由型线几何直接确定：

    每转排量  q  = 4 * e * D * T          [m^3/r]
    理论流量  Qt = q * n                  [m^3/d]（n 为转速 r/min）

其中 e 为偏心距、D 为转子截面直径、T 为定子导程。
参考文献：Zheng et al., Math. Probl. Eng., 2018, Eq.(1)；
Nguyen et al., J. Pet. Sci. Eng., 2014（3-D vector approach）。
"""

from __future__ import annotations

from dataclasses import dataclass

MINUTES_PER_DAY = 1440.0


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
        """每转理论排量 q = 4·e·D·T [m^3/r]。"""
        return 4.0 * self.eccentricity_m * self.rotor_diameter_m * self.stator_lead_m

    def theoretical_rate_m3d(self, speed_rpm: float) -> float:
        """理论流量 Qt [m^3/d]，speed_rpm 为泵转速 [r/min]。"""
        if speed_rpm < 0.0:
            raise ValueError("转速不能为负")
        return self.displacement_per_rev_m3 * speed_rpm * MINUTES_PER_DAY

    def stage_differential_pressure_pa(self, total_dp_pa: float) -> float:
        """泵总压差平均分配到每一级的级压差 [Pa]。"""
        return total_dp_pa / self.stages
