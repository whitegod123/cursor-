"""电潜螺杆泵（ESPCP）产液量数字计产模型。

模型体系（与论文章节对应）：

1. 几何排量模型      geometry.py    —— 理论排量 Qt = 4·e·D·T·n（基础）
2. 排量-漏失模型     leakage.py     —— 机理漏失（压差 + 剪切），提供标定的函数结构
   容积效率标定      calibration.py —— 用单量测试数据标定漏失系数（核心）
3. 黏温修正模型      viscosity.py   —— 井温 → 工况黏度（修正）
4. 扭矩-功率模型     power.py       —— 电参数负载校核 / 压差备用估计（校核）

主入口：metering.py 的 DigitalMeteringModel。
"""

from espcp_metering.geometry import PumpGeometry
from espcp_metering.viscosity import (
    ArrheniusViscosity,
    EmulsionViscosity,
    ViscosityTable,
    WaterViscosity,
)
from espcp_metering.leakage import ClearanceGeometry, MechanisticSlippageModel
from espcp_metering.calibration import (
    CalibratedSlippageModel,
    SlippageCalibrator,
    TestRecord,
)
from espcp_metering.power import PowerModel, TorqueBalance
from espcp_metering.metering import (
    DigitalMeteringModel,
    MeteringResult,
    WellSnapshot,
)

__all__ = [
    "PumpGeometry",
    "ArrheniusViscosity",
    "EmulsionViscosity",
    "ViscosityTable",
    "WaterViscosity",
    "ClearanceGeometry",
    "MechanisticSlippageModel",
    "CalibratedSlippageModel",
    "SlippageCalibrator",
    "TestRecord",
    "PowerModel",
    "TorqueBalance",
    "DigitalMeteringModel",
    "MeteringResult",
    "WellSnapshot",
]

__version__ = "0.1.0"
