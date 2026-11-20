# 记忆热索引（`motion-stage`）

> 硬上限 ≤ 200 行 / 25 KB。只放当前在役基线、安全红线与一句话导航。

## 0. 在役基线与安全包线
- 主控固件版本：`v2.4.1`（`20 kHz` 伺服采样环）
- 传感模块 `#SENS-24B-07`：线性区 `±5.00 V` | 削顶饱和 `±5.20 V` | **过压硬极限 `±6.50 V`** | **禁用 PFM 开关电源直供模拟轨** → [SENS-24B-07.md](2_calibration/assets/SENS-24B-07.md)
- 直线执行台 `#STAGE-X02`：连续额定电流 `2.8 A` | 短时峰值 `5.5 A (≤200 ms)` | **退磁/热损硬极限 `6.2 A`** → [STAGE-X02.md](2_calibration/assets/STAGE-X02.md)

## 1. 机理模型（`1_theory/`）
- 高频供电纹波突破模拟前端 PSRR 混叠入采样带宽判据 → [adc-psrr-aliasing.md](1_theory/adc-psrr-aliasing.md)

## 2. 标定规程（`2_calibration/sops/`）
- 位移传感模块入库与供电轨纹波核查规程 → [sensor-rail-intake.md](2_calibration/sops/sensor-rail-intake.md)

## 3. 高频排故陷阱与负结果（`4_anomalies/`）
- 【陷阱】轻载保位出现数十 Hz 伪振荡 → 先查模拟参考轨是否误切开关电源 PFM 档，勿盲改 PID `[ref: anom-20261018-001]` → [anom-20261018-001.md](4_anomalies/resolved/anom-20261018-001.md)
- 【负结果】靠放大反馈滑动窗口滤除混叠纹波 → 无效且引入相位滞后放大超调 `[ref: anom-20261018-001]`
