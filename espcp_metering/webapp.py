"""电潜螺杆泵数字计产模型的网页界面（纯标准库，零第三方依赖）。

启动：

    python3 -m espcp_metering.webapp          # 默认 http://127.0.0.1:8000
    python3 -m espcp_metering.webapp 8080     # 指定端口

页面提供泵参数、黏度参数、标定记录录入与实时计产，
后端为无状态 JSON API（POST /api/estimate），每次请求携带全部
参数完成"标定 + 计产"，便于嵌入其他系统。
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from espcp_metering.calibration import SlippageCalibrator, TestRecord
from espcp_metering.geometry import PumpGeometry
from espcp_metering.metering import DigitalMeteringModel, WellSnapshot
from espcp_metering.power import PowerModel
from espcp_metering.viscosity import ArrheniusViscosity, EmulsionViscosity

MPA = 1.0e6


def compute(payload: dict[str, Any]) -> dict[str, Any]:
    """无状态计算入口：payload（SI 单位）→ 标定结果 + 计产结果。

    payload 结构见页面 JS 的 buildPayload()，压力 Pa、黏度 Pa·s、功率 W。
    """
    g = payload["geometry"]
    geometry = PumpGeometry(
        eccentricity_m=float(g["eccentricity_m"]),
        rotor_diameter_m=float(g["rotor_diameter_m"]),
        stator_lead_m=float(g["stator_lead_m"]),
        stages=int(g["stages"]),
    )

    v = payload["viscosity"]
    oil = ArrheniusViscosity.from_two_points(
        float(v["t1_c"]), float(v["mu1_pas"]), float(v["t2_c"]), float(v["mu2_pas"])
    )
    viscosity = EmulsionViscosity(
        oil_model=oil,
        water_cut=float(v["water_cut"]),
        inversion_point=float(v.get("inversion_point", 0.6)),
    )

    records = [
        TestRecord(
            measured_rate_m3d=float(r["measured_rate_m3d"]),
            total_dp_pa=float(r["total_dp_pa"]),
            temperature_c=float(r["temperature_c"]),
            speed_rpm=float(r["speed_rpm"]),
        )
        for r in payload["records"]
    ]
    alpha_grid = tuple(payload.get("alpha_grid", (0.6, 0.8, 1.0)))
    slippage = SlippageCalibrator(geometry, viscosity).fit(records, alpha_grid=alpha_grid)

    power = None
    p = payload.get("power")
    if p:
        power = PowerModel(
            geometry=geometry,
            motor_efficiency=float(p.get("motor_efficiency", 0.85)),
            transmission_efficiency=float(p.get("transmission_efficiency", 0.95)),
            friction_torque_nm=float(p.get("friction_torque_nm", 0.0)),
        )

    model = DigitalMeteringModel(slippage, power)
    s = payload["snapshot"]

    def _opt(key: str) -> float | None:
        value = s.get(key)
        return None if value in (None, "") else float(value)

    result = model.estimate(
        WellSnapshot(
            speed_rpm=float(s["speed_rpm"]),
            temperature_c=float(s["temperature_c"]),
            intake_pressure_pa=_opt("intake_pressure_pa"),
            discharge_pressure_pa=_opt("discharge_pressure_pa"),
            electrical_power_w=_opt("electrical_power_w"),
        )
    )
    return {
        "calibration": {
            "k_dp": slippage.k_dp,
            "k_sh": slippage.k_sh,
            "alpha": slippage.alpha,
            "beta": slippage.beta,
        },
        "result": {
            "rate_m3d": result.rate_m3d,
            "theoretical_rate_m3d": result.theoretical_rate_m3d,
            "slippage_m3d": result.slippage_m3d,
            "volumetric_efficiency": result.volumetric_efficiency,
            "dp_pa": result.dp_pa,
            "dp_source": result.dp_source,
            "load_check_ok": result.load_check_ok,
        },
    }


PAGE = """<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>电潜螺杆泵数字计产</title>
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --line: #334155;
    --text: #e2e8f0; --muted: #94a3b8; --accent: #38bdf8;
    --ok: #4ade80; --warn: #f87171;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0; padding: 24px; background: var(--bg); color: var(--text);
    font: 15px/1.6 system-ui, "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  h1 { font-size: 22px; margin: 0 0 4px; }
  .sub { color: var(--muted); margin-bottom: 20px; font-size: 13px; }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 16px; }
  .card { background: var(--card); border: 1px solid var(--line); border-radius: 12px; padding: 16px 18px; }
  .card h2 { font-size: 15px; margin: 0 0 12px; color: var(--accent); }
  label { display: block; font-size: 12px; color: var(--muted); margin: 8px 0 2px; }
  input {
    width: 100%; padding: 7px 10px; border-radius: 8px; border: 1px solid var(--line);
    background: #0b1220; color: var(--text); font-size: 14px;
  }
  input:focus { outline: 1px solid var(--accent); }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .row3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  th, td { padding: 4px 6px; text-align: center; }
  th { color: var(--muted); font-weight: normal; font-size: 12px; }
  td input { padding: 5px 6px; font-size: 13px; }
  button {
    cursor: pointer; border: none; border-radius: 8px; font-size: 14px;
    padding: 8px 14px; background: #334155; color: var(--text);
  }
  button:hover { filter: brightness(1.15); }
  .primary {
    background: var(--accent); color: #082f49; font-weight: 600;
    padding: 12px 28px; font-size: 16px; width: 100%; margin-top: 16px;
  }
  .small { padding: 4px 10px; font-size: 12px; }
  #result { margin-top: 20px; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 12px; }
  .kpi { background: #0b1220; border: 1px solid var(--line); border-radius: 10px; padding: 12px; text-align: center; }
  .kpi .v { font-size: 24px; font-weight: 700; color: var(--accent); }
  .kpi .l { font-size: 12px; color: var(--muted); }
  .ok { color: var(--ok); } .warn { color: var(--warn); }
  .err { color: var(--warn); margin-top: 12px; white-space: pre-wrap; }
  .meta { color: var(--muted); font-size: 13px; margin-top: 10px; }
</style>
</head>
<body>
<h1>电潜螺杆泵产液量数字计产</h1>
<div class="sub">机理约束 + 数据标定 | 理论排量 − 漏失修正 | 电参数校核与降级</div>

<div class="grid">
  <div class="card">
    <h2>1. 泵结构参数（铭牌）</h2>
    <div class="row">
      <div><label>偏心距 e (mm)</label><input id="ecc" value="4.0"></div>
      <div><label>转子直径 D (mm)</label><input id="dia" value="40.0"></div>
    </div>
    <div class="row">
      <div><label>定子导程 T (mm)</label><input id="lead" value="200.0"></div>
      <div><label>级数</label><input id="stages" value="24"></div>
    </div>
  </div>

  <div class="card">
    <h2>2. 井液黏度（高含水乳化液模型）</h2>
    <div class="row">
      <div><label>含水率 (%)</label><input id="wc" value="90"></div>
      <div><label>转相点 (%)</label><input id="inv" value="60"></div>
    </div>
    <label>油相黏温两点（低含水井才重要）</label>
    <div class="row">
      <div><label>T1 (°C)</label><input id="t1" value="50"></div>
      <div><label>μ1 (mPa·s)</label><input id="mu1" value="1000"></div>
    </div>
    <div class="row">
      <div><label>T2 (°C)</label><input id="t2" value="80"></div>
      <div><label>μ2 (mPa·s)</label><input id="mu2" value="120"></div>
    </div>
  </div>

  <div class="card">
    <h2>3. 扭矩-功率模型（可选，用于校核/降级）</h2>
    <div class="row3">
      <div><label>电机效率</label><input id="etam" value="0.85"></div>
      <div><label>传动效率</label><input id="etat" value="0.95"></div>
      <div><label>摩擦扭矩 (N·m)</label><input id="mf" value="25"></div>
    </div>
    <div class="meta">三项留空则不启用电参数校核与压差降级。</div>
  </div>

  <div class="card" style="grid-column: 1 / -1;">
    <h2>4. 单量测试标定记录（建议 ≥ 5 条，覆盖不同压差与转速）</h2>
    <table id="rectab">
      <thead><tr>
        <th>实测产液量 (m³/d)</th><th>泵压差 (MPa)</th><th>井温 (°C)</th><th>转速 (r/min)</th><th></th>
      </tr></thead>
      <tbody></tbody>
    </table>
    <button class="small" onclick="addRow()" style="margin-top:8px;">+ 添加记录</button>
  </div>

  <div class="card" style="grid-column: 1 / -1;">
    <h2>5. 实时数据（当前时刻）</h2>
    <div class="row3">
      <div><label>转速 (r/min) *</label><input id="s_n" value="150"></div>
      <div><label>井温 (°C) *</label><input id="s_t" value="60"></div>
      <div><label>电功率 (kW)</label><input id="s_p" value=""></div>
    </div>
    <div class="row">
      <div><label>泵吸入口压力 (MPa)</label><input id="s_pin" value="3.0"></div>
      <div><label>泵排出口压力 (MPa)</label><input id="s_pout" value="7.2"></div>
    </div>
    <div class="meta">压力缺失且填了电功率时，自动走电参数降级通道反推压差。</div>
    <button class="primary" onclick="run()">标定并计产</button>
  </div>
</div>

<div id="result"></div>

<script>
const DEFAULT_RECORDS = [
  [23.5, 2.0, 55, 100],
  [27.8, 3.5, 58, 120],
  [24.9, 4.0, 60, 150],
  [23.9, 5.0, 62, 150],
  [34.2, 4.5, 61, 200],
  [44.1, 3.0, 57, 250],
];

function addRow(vals) {
  const tb = document.querySelector('#rectab tbody');
  const tr = document.createElement('tr');
  const v = vals || ['', '', '', ''];
  tr.innerHTML = v.map(x => `<td><input value="${x}"></td>`).join('')
    + `<td><button class="small" onclick="this.closest('tr').remove()">删除</button></td>`;
  tb.appendChild(tr);
}
DEFAULT_RECORDS.forEach(r => addRow(r));

const num = id => parseFloat(document.getElementById(id).value);
const opt = id => {
  const s = document.getElementById(id).value.trim();
  return s === '' ? null : parseFloat(s);
};

function buildPayload() {
  const records = [...document.querySelectorAll('#rectab tbody tr')].map(tr => {
    const c = [...tr.querySelectorAll('input')].map(i => parseFloat(i.value));
    return {
      measured_rate_m3d: c[0],
      total_dp_pa: c[1] * 1e6,
      temperature_c: c[2],
      speed_rpm: c[3],
    };
  }).filter(r => !Object.values(r).some(Number.isNaN));

  const etam = opt('etam'), etat = opt('etat'), mf = opt('mf');
  const power = (etam === null && etat === null && mf === null) ? null : {
    motor_efficiency: etam ?? 0.85,
    transmission_efficiency: etat ?? 0.95,
    friction_torque_nm: mf ?? 0.0,
  };
  const pkw = opt('s_p'), pin = opt('s_pin'), pout = opt('s_pout');
  return {
    geometry: {
      eccentricity_m: num('ecc') / 1e3,
      rotor_diameter_m: num('dia') / 1e3,
      stator_lead_m: num('lead') / 1e3,
      stages: num('stages'),
    },
    viscosity: {
      water_cut: num('wc') / 100,
      inversion_point: num('inv') / 100,
      t1_c: num('t1'), mu1_pas: num('mu1') / 1e3,
      t2_c: num('t2'), mu2_pas: num('mu2') / 1e3,
    },
    power,
    records,
    alpha_grid: [0.6, 0.8, 1.0],
    snapshot: {
      speed_rpm: num('s_n'),
      temperature_c: num('s_t'),
      intake_pressure_pa: pin === null ? null : pin * 1e6,
      discharge_pressure_pa: pout === null ? null : pout * 1e6,
      electrical_power_w: pkw === null ? null : pkw * 1e3,
    },
  };
}

async function run() {
  const box = document.getElementById('result');
  box.innerHTML = '<div class="meta">计算中…</div>';
  try {
    const resp = await fetch('/api/estimate', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(buildPayload()),
    });
    const data = await resp.json();
    if (!resp.ok) throw new Error(data.error || resp.statusText);
    const r = data.result, c = data.calibration;
    const check = r.load_check_ok === null ? '未校核'
      : r.load_check_ok ? '<span class="ok">通过</span>' : '<span class="warn">报警</span>';
    const src = r.dp_source === 'measured' ? '实测压力' : '电参数反推（降级）';
    box.innerHTML = `
      <div class="card">
        <h2>计产结果</h2>
        <div class="kpis">
          <div class="kpi"><div class="v">${r.rate_m3d.toFixed(1)}</div><div class="l">产液量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${r.theoretical_rate_m3d.toFixed(1)}</div><div class="l">理论排量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${r.slippage_m3d.toFixed(1)}</div><div class="l">漏失量 (m³/d)</div></div>
          <div class="kpi"><div class="v">${(r.volumetric_efficiency * 100).toFixed(1)}%</div><div class="l">容积效率</div></div>
          <div class="kpi"><div class="v">${(r.dp_pa / 1e6).toFixed(2)}</div><div class="l">泵压差 (MPa)</div></div>
        </div>
        <div class="meta">
          压差来源：${src} ｜ 负载校核：${check}<br>
          标定系数：k_dp = ${c.k_dp.toExponential(3)}，k_sh = ${c.k_sh.toFixed(4)}，α = ${c.alpha}，β = ${c.beta}
        </div>
      </div>`;
  } catch (e) {
    box.innerHTML = `<div class="err">计算失败：${e.message}</div>`;
  }
}
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        if self.path in ("/", "/index.html"):
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/estimate":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            response, status = compute(payload), 200
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            response, status = {"error": str(exc)}, 400
        body = json.dumps(response, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write(f"{self.address_string()} - {fmt % args}\n")


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"电潜螺杆泵数字计产界面已启动：http://127.0.0.1:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
