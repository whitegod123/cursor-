"""端到端演示：从单量测试数据标定到实时计产。

模拟一口电潜螺杆泵稠油井的完整流程：
  1. 定义泵几何参数（铭牌/图纸）
  2. 建立黏温模型（化验室黏温曲线）
  3. 用 6 次单量测试数据标定漏失模型
  4. 配置扭矩-功率校核模型
  5. 对若干实时数据快照计产（含压力计失效降级场景）

运行：python examples/demo_metering.py
"""

import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from espcp_metering import (
    DigitalMeteringModel,
    PowerModel,
    PumpGeometry,
    SlippageCalibrator,
    TestRecord,
    ViscosityTable,
    WellSnapshot,
)

MPA = 1.0e6


def main() -> None:
    # ── 1. 泵几何参数（GLB120 类单头泵示例）────────────────────
    geometry = PumpGeometry(
        eccentricity_m=0.004,     # 偏心距 4 mm
        rotor_diameter_m=0.040,   # 转子直径 40 mm
        stator_lead_m=0.200,      # 定子导程 200 mm
        stages=24,
    )
    print(f"每转理论排量 q = {geometry.displacement_per_rev_m3 * 1e3:.4f} L/r")
    print(f"150 r/min 理论排量 Qt = {geometry.theoretical_rate_m3d(150):.1f} m3/d\n")

    # ── 2. 黏温模型（化验室实测黏温曲线）──────────────────────
    viscosity = ViscosityTable(
        temperatures_c=[40.0, 50.0, 60.0, 70.0, 80.0],
        viscosities_pas=[2.50, 1.00, 0.45, 0.22, 0.12],
    )

    # ── 3. 单量测试数据标定漏失模型 ───────────────────────────
    # 演示用：以"真值"系数正向生成测试数据并叠加 0.5% 计量噪声，
    # 实际使用时把 records 换成现场单量测试记录即可。
    # 注意：产液量的计量噪声会放大映射到漏失量上（漏失仅占总量的
    # 小部分），因此单量测试的精度直接决定标定质量。
    k_dp_true, k_sh_true = 1.5e-7, 0.008
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

    # ── 4. 扭矩-功率校核模型 ─────────────────────────────────
    power = PowerModel(
        geometry=geometry,
        motor_efficiency=0.85,
        transmission_efficiency=0.95,
        friction_torque_nm=25.0,   # 台架空载试验标定
        check_threshold=0.15,
    )
    model = DigitalMeteringModel(slippage, power)

    # ── 5. 实时计产 ──────────────────────────────────────────
    def electric_power_for(dp_pa: float, n: float) -> float:
        """演示辅助：由压差正向合成一致的电功率读数。"""
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
    main()
