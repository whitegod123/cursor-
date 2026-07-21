"""数字计产主模型：整合四个运行特性子模型。

数据流：

    转速 n ──────────────┐
                         ├→ 理论排量 Qt = q·n ──┐
    泵结构参数 ──────────┘                       ├→ Q = Qt − Qs → 产液量
    吸入/排出压力 → Δp ──┐                       │
    井温 T → 黏温模型 ───┴→ 漏失 Qs（标定模型）──┘
                                                 ↑
    电参数 → 扭矩-功率模型 → 负载校核 ───────────┘
             （压力缺失时降级反推 Δp）
"""

from __future__ import annotations

from dataclasses import dataclass

from espcp_metering.calibration import CalibratedSlippageModel
from espcp_metering.power import PowerModel


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
