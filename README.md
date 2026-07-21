# espcp-metering：电潜螺杆泵产液量数字计产模型

面向电潜螺杆泵（ESPCP）采油井的产液量软计量（虚拟计量）Python 实现。
利用井下压力、温度、电参数等实时生产数据与单量测试数据，按
"机理约束 + 数据标定"路线连续估算单井产液量，减少对地面单量设备的依赖。

## 模型体系

| 模块 | 模型 | 定位 |
| --- | --- | --- |
| `geometry.py` | 几何排量模型：Qt = 4·e·D·T·n | 基础 |
| `leakage.py` | 排量-漏失机理模型（压差 + 剪切缝隙流动） | 核心·机理骨架 |
| `calibration.py` | 容积效率标定：Qs = k_dp·Δp^α/μ^β + k_sh·n，系数由单量测试数据最小二乘标定 | 核心·数据标定 |
| `viscosity.py` | 黏温修正：Arrhenius 式 / 实测黏温曲线插值 / 水黏度解析式 / 油水乳化液模型 | 修正 |
| `power.py` | 扭矩-功率模型：电参数负载校核、压力计失效时反推压差 | 校核/备用 |
| `metering.py` | 数字计产主模型（整合以上四者） | 主入口 |

计产主线：

```text
转速 n ──────────────┐
                     ├→ 理论排量 Qt = q·n ──┐
泵结构参数 ──────────┘                      ├→ Q = Qt − Qs → 产液量
吸入/排出压力 → Δp ──┐                      │
井温 T → 黏温模型 ───┴→ 漏失 Qs（标定式）───┘
                                            ↑
电参数 → 扭矩-功率模型 → 负载校核 ──────────┘
         （压力缺失时降级反推 Δp）
```

## 快速开始

```bash
pip install -r requirements.txt      # 仅测试需要 pytest，运行时零依赖
python examples/demo_metering.py     # 端到端演示：标定 → 计产 → 校核/降级
python -m pytest tests/ -v           # 单元测试
python -m espcp_metering.webapp      # 网页界面 http://127.0.0.1:8000
```

## 网页界面

`python -m espcp_metering.webapp [端口]` 启动后浏览器打开，页面提供：

- 泵结构参数、井液黏度（高含水乳化液）、扭矩-功率模型配置；
- 单量测试标定记录表格录入（现场单位：MPa、mPa·s、kW）；
- 实时数据计产：产液量、理论排量、漏失量、容积效率、压差来源
  （实测 / 电参数降级）与负载校核结果。

后端为无状态 JSON API（`POST /api/estimate`，SI 单位），可直接对接
SCADA 或生产数据库做批量计产。

最小使用示例：

```python
from espcp_metering import (
    DigitalMeteringModel, PumpGeometry, SlippageCalibrator,
    TestRecord, ViscosityTable, WellSnapshot,
)

geometry = PumpGeometry(eccentricity_m=0.004, rotor_diameter_m=0.040,
                        stator_lead_m=0.200, stages=24)
viscosity = ViscosityTable([50.0, 80.0], [1.0, 0.12])

records = [  # 单量测试数据：实测产液量、泵压差、井温、转速
    TestRecord(measured_rate_m3d=24.1, total_dp_pa=3.5e6,
               temperature_c=58.0, speed_rpm=120.0),
    TestRecord(measured_rate_m3d=30.5, total_dp_pa=4.0e6,
               temperature_c=60.0, speed_rpm=150.0),
    # ... 建议覆盖不同压差与转速
]
slippage = SlippageCalibrator(geometry, viscosity).fit(records)

model = DigitalMeteringModel(slippage)
result = model.estimate(WellSnapshot(
    speed_rpm=150.0, temperature_c=60.0,
    intake_pressure_pa=3.0e6, discharge_pressure_pa=7.2e6,
))
print(result.rate_m3d, result.volumetric_efficiency)
```

## 高含水油田用法

含水率超过转相点（默认 0.6）后井液为水包油，混合液黏度接近水黏度，
不需要化验黏温曲线，直接用 `EmulsionViscosity` 包裹油相模型即可：

```python
from espcp_metering import ArrheniusViscosity, EmulsionViscosity

oil = ArrheniusViscosity.from_two_points(50.0, 1.0, 80.0, 0.12)  # 油相（低含水井才重要）
liquid = EmulsionViscosity(oil_model=oil, water_cut=0.90)         # 化验含水率，月度更新即可
# 含水率更新：liquid = liquid.with_water_cut(0.93)
# 把 liquid 作为 viscosity_model 传给 SlippageCalibrator / CalibratedSlippageModel
```

注意：高含水下井液黏度低，漏失量占比显著增大，单量测试标定的质量
更加关键；低黏度缝隙流可能进入湍流区，标定时建议启用
`alpha_grid=(0.6, 0.8, 1.0)` 网格搜索。

## 单位约定

一律使用 SI 单位：长度 m、压力 Pa、黏度 Pa·s、功率 W、温度 °C（输入）、
转速 r/min、流量 m³/d（输出）。

## 主要参考文献

- 郑磊, 吴晓东, 等. 全金属螺杆泵间隙漏失模型. 石油科学通报, 2018, 3(3): 320–331.
- Zheng L., et al. Analytical Model for the Flow in Progressing Cavity Pump with
  the Metallic Stator and Rotor in Clearance Fit. Math. Probl. Eng., 2018.
- New Approach for Modeling Progressive Cavity Pumps Performance. SPE 84137, 2003.
- Pessoa P.A.S., et al. A Simplified Model for the Flow in a Progressive Cavity
  Pump. COBEM, 2009.
- Paladino E., et al. A computational model for the flow within rigid stator
  progressing cavity pumps. J. Pet. Sci. Eng., 2011, 78(1): 178–192.
- 杨永华, 等. 地面驱动螺杆泵负载扭矩波动机制. 中国石油大学学报(自然科学版),
  2011, 35(5): 120–124.
