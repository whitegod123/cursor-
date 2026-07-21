"""扭矩-功率模型（校核层）。

不进入计产主公式，承担两个职责：

1. 负载校核：电参数折算的泵轴扭矩与压差折算的水力扭矩对比，
   偏差超阈值即提示泵磨损、卡阻或传感器异常；
2. 压差备用估计：井下压力计失效时，由电功率反推泵压差，
   维持计产链不中断（降级运行）。

扭矩平衡（容积泵通式，参考杨永华等 2011）：

    M_shaft = M_hydraulic + M_friction
    M_hydraulic = Δp · q / (2π)        （q 为每转排量）

电功率到泵轴功率的传递：

    P_shaft = P_electric · η_motor · η_transmission
    M_shaft = P_shaft / ω,  ω = 2π·n/60
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from espcp_metering.geometry import PumpGeometry


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

    Attributes:
        geometry: 泵几何参数（提供每转排量）
        motor_efficiency: 潜油电机效率（含电缆损耗，0~1）
        transmission_efficiency: 保护器/传动效率（0~1）
        friction_torque_nm: 泵内摩擦扭矩 [N·m]（台架空载试验或
            低压差测试点标定）
        check_threshold: 负载校核报警阈值（相对不平衡度）
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
        """由泵压差计算水力扭矩 [N·m]。"""
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
        """压力计失效时的备用通道：由电功率反推泵压差 [Pa]。

        Δp = (M_shaft − M_friction) · 2π / q
        """
        m_shaft = self.shaft_torque_nm(electrical_power_w, speed_rpm)
        m_hydraulic = max(m_shaft - self.friction_torque_nm, 0.0)
        return m_hydraulic * 2.0 * math.pi / self.geometry.displacement_per_rev_m3
