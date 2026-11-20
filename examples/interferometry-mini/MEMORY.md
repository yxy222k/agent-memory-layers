# 记忆总索引（1310nm 干涉实验台示例）

> 硬上限 ≤ 200 行 / 25 KB。只放当前台架状态、硬保护红线与一句话导航。

## 0. 当前台架在役硬件与硬保护红线
- 当前上位机与解算版本：`v3.4.2`
- 光源 `#SLD-1310-03`：**精密测量禁止低于 `90 mA` 运行**（低电流中心波长漂移 >2nm）；极限电流 `220 mA` → `2_calibration/assets/SLD-1310-03.md`
- 光谱仪 `#SPEC-01`（InGaAs 1024px）：暗谱 `410 counts` | **饱和阈值 `58,000 counts`** | **瞬时过载硬红线 `64,500 counts`（严禁裸光直通）** → `2_calibration/assets/SPEC-01.md`

## 1. 科学机理与模型（`1_theory/`）
- 光源中心波长偏移与色散对干涉光程解算的定量耦合 → `1_theory/interferometry-phase-dispersion.md`

## 2. 标定与测量规程（`2_calibration/sops/`）
- 1310nm SLD 光源入库与复核标定规程（含高低电流波长漂移必检项） → `2_calibration/sops/sld-intake-calibration.md`

## 3. 高频排故陷阱与负结果（`4_anomalies/`）
- 【陷阱】高反样品调低光源电流后解算跳变 → 实为 SLD 低电流波长漂移，勿改解算滤波；应保持额定电流改调积分档位或加衰减片 `[ref: anom-20261112-001]` → `4_anomalies/resolved/anom-20261112-001.md`
- 【已证伪负结果】加大滑动均值窗口消除相位慢漂 → 证实无效且抹平真实台阶边缘 `[ref: anom-20261112-001]`
