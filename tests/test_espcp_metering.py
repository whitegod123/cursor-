"""espcp_metering 单元测试。

运行：python -m pytest tests/ -v
"""

import math

import pytest

from espcp_metering import (
    ArrheniusViscosity,
    CalibratedSlippageModel,
    ClearanceGeometry,
    DigitalMeteringModel,
    EmulsionViscosity,
    MechanisticSlippageModel,
    PowerModel,
    PumpGeometry,
    SlippageCalibrator,
    TestRecord,
    ViscosityTable,
    WaterViscosity,
    WellSnapshot,
)

MPA = 1.0e6


@pytest.fixture
def geometry() -> PumpGeometry:
    # 典型采油螺杆泵：e=4mm, D=40mm, T=200mm, 24 级
    return PumpGeometry(
        eccentricity_m=0.004,
        rotor_diameter_m=0.040,
        stator_lead_m=0.200,
        stages=24,
    )


@pytest.fixture
def viscosity() -> ArrheniusViscosity:
    # 稠油：50°C 时 1.0 Pa·s，80°C 时 0.2 Pa·s
    return ArrheniusViscosity.from_two_points(50.0, 1.0, 80.0, 0.2)


class TestGeometry:
    def test_displacement_per_rev(self, geometry: PumpGeometry) -> None:
        expected = 4.0 * 0.004 * 0.040 * 0.200
        assert geometry.displacement_per_rev_m3 == pytest.approx(expected)

    def test_theoretical_rate_scales_with_speed(self, geometry: PumpGeometry) -> None:
        q100 = geometry.theoretical_rate_m3d(100.0)
        q200 = geometry.theoretical_rate_m3d(200.0)
        assert q200 == pytest.approx(2.0 * q100)
        # e=4mm/D=40mm/T=200mm 泵在 100 r/min 下理论排量约 18.4 m3/d
        assert q100 == pytest.approx(18.432, rel=1e-3)

    def test_invalid_parameters_rejected(self) -> None:
        with pytest.raises(ValueError):
            PumpGeometry(eccentricity_m=-0.004, rotor_diameter_m=0.04, stator_lead_m=0.2)
        with pytest.raises(ValueError):
            PumpGeometry(
                eccentricity_m=0.004,
                rotor_diameter_m=0.04,
                stator_lead_m=0.2,
                stages=0,
            )


class TestViscosity:
    def test_arrhenius_reproduces_calibration_points(
        self, viscosity: ArrheniusViscosity
    ) -> None:
        assert viscosity.viscosity_pas(50.0) == pytest.approx(1.0, rel=1e-9)
        assert viscosity.viscosity_pas(80.0) == pytest.approx(0.2, rel=1e-9)

    def test_arrhenius_monotonic_decreasing(
        self, viscosity: ArrheniusViscosity
    ) -> None:
        mus = [viscosity.viscosity_pas(t) for t in (40.0, 55.0, 70.0, 90.0)]
        assert all(a > b for a, b in zip(mus, mus[1:]))

    def test_table_interpolates_log_linearly(self) -> None:
        table = ViscosityTable([50.0, 80.0], [1.0, 0.2])
        mu_mid = table.viscosity_pas(65.0)
        assert mu_mid == pytest.approx(math.sqrt(1.0 * 0.2), rel=1e-9)

    def test_table_extrapolates_beyond_range(self) -> None:
        table = ViscosityTable([50.0, 80.0], [1.0, 0.2])
        assert table.viscosity_pas(90.0) < 0.2
        assert table.viscosity_pas(40.0) > 1.0


class TestWaterAndEmulsionViscosity:
    def test_water_viscosity_reference_points(self) -> None:
        water = WaterViscosity()
        # 20°C 约 1.0 mPa·s，60°C 约 0.47 mPa·s
        assert water.viscosity_pas(20.0) == pytest.approx(1.0e-3, rel=0.05)
        assert water.viscosity_pas(60.0) == pytest.approx(0.47e-3, rel=0.05)

    def test_water_viscosity_decreases_with_temperature(self) -> None:
        water = WaterViscosity()
        assert water.viscosity_pas(80.0) < water.viscosity_pas(40.0)

    def test_high_water_cut_close_to_water(
        self, viscosity: ArrheniusViscosity
    ) -> None:
        """高含水（水包油）时混合液黏度接近水而远低于油。"""
        emulsion = EmulsionViscosity(oil_model=viscosity, water_cut=0.9)
        mu_mix = emulsion.viscosity_pas(60.0)
        mu_water = WaterViscosity().viscosity_pas(60.0)
        mu_oil = viscosity.viscosity_pas(60.0)
        assert mu_water < mu_mix < 2.0 * mu_water
        assert mu_mix < 0.01 * mu_oil

    def test_high_water_cut_insensitive_to_water_cut(
        self, viscosity: ArrheniusViscosity
    ) -> None:
        """含水 85% 与 95% 的混合液黏度差别很小（<40%）。"""
        mu85 = EmulsionViscosity(viscosity, 0.85).viscosity_pas(60.0)
        mu95 = EmulsionViscosity(viscosity, 0.95).viscosity_pas(60.0)
        assert abs(mu85 - mu95) / mu95 < 0.4

    def test_low_water_cut_thickens_oil(self, viscosity: ArrheniusViscosity) -> None:
        """油包水（低含水）时乳化增稠，混合液黏度高于纯油。"""
        emulsion = EmulsionViscosity(oil_model=viscosity, water_cut=0.3)
        assert emulsion.viscosity_pas(60.0) > viscosity.viscosity_pas(60.0)

    def test_with_water_cut_returns_updated_model(
        self, viscosity: ArrheniusViscosity
    ) -> None:
        emulsion = EmulsionViscosity(oil_model=viscosity, water_cut=0.8)
        updated = emulsion.with_water_cut(0.92)
        assert updated.water_cut == 0.92
        assert updated.inversion_point == emulsion.inversion_point

    def test_invalid_water_cut_rejected(self, viscosity: ArrheniusViscosity) -> None:
        with pytest.raises(ValueError):
            EmulsionViscosity(oil_model=viscosity, water_cut=1.2)


class TestMechanisticSlippage:
    @pytest.fixture
    def model(self, geometry: PumpGeometry) -> MechanisticSlippageModel:
        clearance = ClearanceGeometry(
            clearance_m=0.0002, seal_width_m=0.010, seal_length_m=0.005
        )
        return MechanisticSlippageModel(geometry=geometry, clearance=clearance)

    def test_pressure_slippage_linear_in_dp(
        self, model: MechanisticSlippageModel
    ) -> None:
        q1 = model.pressure_slippage_m3d(2.0 * MPA, 0.5)
        q2 = model.pressure_slippage_m3d(4.0 * MPA, 0.5)
        assert q2 == pytest.approx(2.0 * q1)

    def test_pressure_slippage_inverse_in_viscosity(
        self, model: MechanisticSlippageModel
    ) -> None:
        q_thin = model.pressure_slippage_m3d(2.0 * MPA, 0.1)
        q_thick = model.pressure_slippage_m3d(2.0 * MPA, 1.0)
        assert q_thin == pytest.approx(10.0 * q_thick)

    def test_higher_viscosity_gives_higher_efficiency(
        self, model: MechanisticSlippageModel
    ) -> None:
        eta_thick = model.volumetric_efficiency(4.0 * MPA, 1.0, 100.0)
        eta_thin = model.volumetric_efficiency(4.0 * MPA, 0.05, 100.0)
        assert eta_thick > eta_thin

    def test_actual_rate_clamped_at_zero(
        self, model: MechanisticSlippageModel
    ) -> None:
        # 极端低黏度 + 高压差：漏失超过理论排量时截断为 0
        assert model.actual_rate_m3d(50.0 * MPA, 0.001, 10.0) == 0.0


class TestCalibration:
    def _make_records(
        self,
        geometry: PumpGeometry,
        viscosity: ArrheniusViscosity,
        k_dp: float,
        k_sh: float,
    ) -> list[TestRecord]:
        """用已知系数正向生成"完美"测试数据。"""
        records = []
        for dp_mpa, t_c, n in [
            (2.0, 60.0, 100.0),
            (4.0, 60.0, 100.0),
            (3.0, 70.0, 150.0),
            (5.0, 55.0, 200.0),
            (1.5, 65.0, 250.0),
        ]:
            mu = viscosity.viscosity_pas(t_c)
            qs = k_dp * (dp_mpa * MPA) / mu + k_sh * n
            qt = geometry.theoretical_rate_m3d(n)
            records.append(
                TestRecord(
                    measured_rate_m3d=qt - qs,
                    total_dp_pa=dp_mpa * MPA,
                    temperature_c=t_c,
                    speed_rpm=n,
                )
            )
        return records

    def test_recovers_known_coefficients(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> None:
        k_dp_true, k_sh_true = 2.0e-7, 0.01
        records = self._make_records(geometry, viscosity, k_dp_true, k_sh_true)
        model = SlippageCalibrator(geometry, viscosity).fit(records)
        assert model.k_dp == pytest.approx(k_dp_true, rel=1e-6)
        assert model.k_sh == pytest.approx(k_sh_true, rel=1e-6)

    def test_calibrated_model_predicts_test_points(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> None:
        records = self._make_records(geometry, viscosity, 2.0e-7, 0.01)
        model = SlippageCalibrator(geometry, viscosity).fit(records)
        for r in records:
            q_pred = model.actual_rate_m3d(r.total_dp_pa, r.temperature_c, r.speed_rpm)
            assert q_pred == pytest.approx(r.measured_rate_m3d, rel=1e-6)

    def test_negative_shear_clamped(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> None:
        # 剪切系数为 0 的数据加噪声后可能拟出负 k_sh，应被截为 0
        records = self._make_records(geometry, viscosity, 2.0e-7, 0.0)
        model = SlippageCalibrator(geometry, viscosity).fit(records)
        assert model.k_sh >= 0.0

    def test_alpha_grid_search_picks_true_exponent(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> None:
        # 用 α=0.8 生成数据，网格搜索应选中 0.8
        alpha_true = 0.8
        records = []
        for dp_mpa, t_c, n in [
            (2.0, 60.0, 100.0),
            (4.0, 60.0, 120.0),
            (3.0, 70.0, 150.0),
            (5.0, 55.0, 200.0),
        ]:
            mu = viscosity.viscosity_pas(t_c)
            qs = 5.0e-5 * (dp_mpa * MPA) ** alpha_true / mu
            qt = geometry.theoretical_rate_m3d(n)
            records.append(TestRecord(qt - qs, dp_mpa * MPA, t_c, n))
        model = SlippageCalibrator(geometry, viscosity).fit(
            records, alpha_grid=(0.6, 0.8, 1.0)
        )
        assert model.alpha == pytest.approx(0.8)

    def test_rejects_impossible_measurement(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> None:
        qt = geometry.theoretical_rate_m3d(100.0)
        bad = [
            TestRecord(qt * 1.1, 2.0 * MPA, 60.0, 100.0),
            TestRecord(qt * 0.9, 3.0 * MPA, 60.0, 100.0),
        ]
        with pytest.raises(ValueError, match="超过理论排量"):
            SlippageCalibrator(geometry, viscosity).fit(bad)


class TestPowerModel:
    @pytest.fixture
    def power(self, geometry: PumpGeometry) -> PowerModel:
        return PowerModel(
            geometry=geometry,
            motor_efficiency=0.85,
            transmission_efficiency=0.95,
            friction_torque_nm=20.0,
        )

    def test_dp_estimate_roundtrip(self, power: PowerModel) -> None:
        """压差 → 功率 → 压差 应还原。"""
        dp_true = 4.0 * MPA
        n = 150.0
        m_shaft = power.hydraulic_torque_nm(dp_true) + power.friction_torque_nm
        omega = 2.0 * math.pi * n / 60.0
        p_elec = m_shaft * omega / (0.85 * 0.95)
        assert power.estimate_dp_pa(p_elec, n) == pytest.approx(dp_true, rel=1e-9)

    def test_load_check_consistent_data_passes(self, power: PowerModel) -> None:
        dp, n = 4.0 * MPA, 150.0
        m_shaft = power.hydraulic_torque_nm(dp) + power.friction_torque_nm
        p_elec = m_shaft * (2.0 * math.pi * n / 60.0) / (0.85 * 0.95)
        assert power.load_check_ok(p_elec, n, dp)

    def test_load_check_flags_inconsistency(self, power: PowerModel) -> None:
        dp, n = 4.0 * MPA, 150.0
        m_shaft = power.hydraulic_torque_nm(dp) + power.friction_torque_nm
        p_elec = m_shaft * (2.0 * math.pi * n / 60.0) / (0.85 * 0.95)
        # 泵磨损后同样压差下功率大幅上升 → 校核应报警
        assert not power.load_check_ok(p_elec * 1.5, n, dp)


class TestDigitalMetering:
    @pytest.fixture
    def model(
        self, geometry: PumpGeometry, viscosity: ArrheniusViscosity
    ) -> DigitalMeteringModel:
        slippage = CalibratedSlippageModel(
            geometry=geometry,
            viscosity_model=viscosity,
            k_dp=2.0e-7,
            k_sh=0.01,
        )
        power = PowerModel(
            geometry=geometry,
            motor_efficiency=0.85,
            transmission_efficiency=0.95,
            friction_torque_nm=20.0,
        )
        return DigitalMeteringModel(slippage, power)

    def test_metering_with_measured_pressures(
        self, model: DigitalMeteringModel
    ) -> None:
        result = model.estimate(
            WellSnapshot(
                speed_rpm=150.0,
                temperature_c=60.0,
                intake_pressure_pa=3.0 * MPA,
                discharge_pressure_pa=7.0 * MPA,
            )
        )
        assert result.dp_source == "measured"
        assert result.dp_pa == pytest.approx(4.0 * MPA)
        assert 0.0 < result.rate_m3d < result.theoretical_rate_m3d
        assert result.volumetric_efficiency == pytest.approx(
            result.rate_m3d / result.theoretical_rate_m3d
        )
        assert result.load_check_ok is None  # 未提供电功率

    def test_power_fallback_when_pressure_missing(
        self, model: DigitalMeteringModel, geometry: PumpGeometry
    ) -> None:
        dp_true, n = 4.0 * MPA, 150.0
        power = PowerModel(
            geometry=geometry,
            motor_efficiency=0.85,
            transmission_efficiency=0.95,
            friction_torque_nm=20.0,
        )
        m_shaft = power.hydraulic_torque_nm(dp_true) + 20.0
        p_elec = m_shaft * (2.0 * math.pi * n / 60.0) / (0.85 * 0.95)

        result = model.estimate(
            WellSnapshot(
                speed_rpm=n,
                temperature_c=60.0,
                electrical_power_w=p_elec,
            )
        )
        assert result.dp_source == "power_fallback"
        assert result.dp_pa == pytest.approx(dp_true, rel=1e-9)

    def test_raises_when_no_dp_channel(self, model: DigitalMeteringModel) -> None:
        with pytest.raises(ValueError, match="泵压差不可用"):
            model.estimate(WellSnapshot(speed_rpm=150.0, temperature_c=60.0))

    def test_load_check_reported_with_full_data(
        self, model: DigitalMeteringModel, geometry: PumpGeometry
    ) -> None:
        dp, n = 4.0 * MPA, 150.0
        power = PowerModel(
            geometry=geometry,
            motor_efficiency=0.85,
            transmission_efficiency=0.95,
            friction_torque_nm=20.0,
        )
        m_shaft = power.hydraulic_torque_nm(dp) + 20.0
        p_elec = m_shaft * (2.0 * math.pi * n / 60.0) / (0.85 * 0.95)
        result = model.estimate(
            WellSnapshot(
                speed_rpm=n,
                temperature_c=60.0,
                intake_pressure_pa=3.0 * MPA,
                discharge_pressure_pa=7.0 * MPA,
                electrical_power_w=p_elec,
            )
        )
        assert result.load_check_ok is True
