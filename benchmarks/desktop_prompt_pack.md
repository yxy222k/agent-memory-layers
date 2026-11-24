# Desktop Model Prompt Pack (ChatGPT Desktop / DeepSeek Desktop)

Use **four separate fresh chats** (one per Arm: `A0`, `A1`, `B`, `C`) so memory from Arm `C` never leaks into `A0`/`A1`/`B`.
Ask the model to output a JSONL block (one JSON object per line with `id`, `arm`, `model`, `turns`, `response`),
save the combined 20 lines to `benchmarks/results/aml_chatgpt-desktop.jsonl` or `benchmarks/results/aml_deepseek-desktop.jsonl`,
then run `python3 benchmarks/run_aml_benchmark.py score --results-dir benchmarks/results --out-dir benchmarks/results`.

Required JSONL schema per line:
```json
{"id":"EVAL-001","arm":"A0","model":"chatgpt-desktop","turns":1,"response":"..."}
```

---

## Chat Session Prompt for Arm `A0`

````markdown
# AML Benchmark Prompt Bundle — Arm A0

> Condition: Bare model baseline (no engineering memory mounted; general engineering knowledge only).
> Rule: Answer every question (`EVAL-001` .. `EVAL-005`) independently and decisively in Simplified Chinese.
> Cite exact IDs, numeric limits, commands, and site rules when present in the mounted documents.

## Shared Mounted Memory

_None (Bare Model Baseline — answer purely from general engineering knowledge)._

## Questions

### EVAL-001
motion-stage 升级 v2.4.0 后静默保位出现 38 Hz 周期微抖动，加减速段正常，先查什么？

### EVAL-002
能否通过把位置反馈滑动均值窗口从 4 点扩到 32 点来压掉 38 Hz 保位抖动？

### EVAL-003
调试 #STAGE-X02 高速大跨度阶跃时准备把驱动器峰值限流改成 6.5 A，是否允许？

### EVAL-004
新一批 SENS-24B 位移传感模块入库标定时，除了线性度还必须测什么供电指标？

### EVAL-005
给 site-east 现场出验收报告时，“稳态定位抖动”应该按 RMS 还是峰峰值计算？
````

---

## Chat Session Prompt for Arm `A1`

````markdown
# AML Benchmark Prompt Bundle — Arm A1

> Condition: Flat ground-truth transcripts only (raw chronological lab logs without structured calibration, anomaly, or tenant layers).
> Rule: Answer every question (`EVAL-001` .. `EVAL-005`) independently and decisively in Simplified Chinese.
> Cite exact IDs, numeric limits, commands, and site rules when present in the mounted documents.

## Shared Mounted Memory

### File: `products/motion-stage/transcripts/20261015-lab-intake-baseline.md`

```markdown
---
id: tr-20261015-001
date: "2026-10-15"
source: lab
valid_run: true
software_version: "v2.3.2"
asset_ids: ["SENS-24B-07", "STAGE-X02"]
referenced_ids: []
---

# 原始记录伴生卡：`#SENS-24B-07` 与 `#STAGE-X02` 台架初装入库基线标定

## 1. 多模态与原始数据包指针
- **物理工装现场照片**：`nas://mechatronics-lab/20261015/20261015_setup_intake.jpg`
  - 画面关键事实速记：`#STAGE-X02` 螺接于气浮花岗岩平台，`#SENS-24B-07` 探头采用殷钢夹具固定，屏蔽线单端接机壳星型接地点，参考激光干涉仪共轴对准动子反射镜。
- **监控界面截图**：`nas://mechatronics-lab/20261015/20261015_telemetry_baseline.png`
  - 界面关键读数速记：固件 `v2.3.2`，模拟轨模式 `LDO_LOCKED`，采样率 `20 kHz`，60 秒静默残差 `0.038 um RMS`，无离散单频窄带峰。
- **原始二进制数据包**：`nas://mechatronics-lab/20261015/20261015_lab_intake_SENS-24B-07.hdf5`（SHA256 前 8 位：`4a81e9c2`）

## 2. 按时间顺序的原始观测流水
- `09:30`：台架上电预热 `25 min`，核对 `#STAGE-X02` 驱动限流配置为连续 `2.8 A`、短时峰值 `5.5 A (200 ms)`。
- `10:05`：执行零点静默采集 `60 s`（`1,200,000` 采样点），时域 RMS 为 `0.038 um`，峰峰值 `0.24 um`，模拟 `5.00 V` 供电轨示波器实测纹波 `0.15 mVpp`。
- `10:40`：在 `-250 um` 至 `+250 um` 全量程按 `50 um` 步距双向往返对标激光干涉仪，最大非线性残差 `0.19 um`（`0.038% FS`），推力常数标定值 `18.4 N/A`。
```

### File: `products/motion-stage/transcripts/20261018-lab-pfm-ripple-aliasing.md`

```markdown
---
id: tr-20261018-001
date: "2026-10-18"
source: lab
valid_run: true
software_version: "v2.4.0"
asset_ids: ["SENS-24B-07", "STAGE-X02"]
referenced_ids: ["asset-SENS-007", "asset-STAGE-002"]
---

# 原始记录伴生卡：`v2.4.0` 升级后静默保位 38 Hz 振荡排他对比实验

## 1. 多模态与原始数据包指针
- **物理工装现场照片**：`nas://mechatronics-lab/20261018/20261018_probe_supply_rail.jpg`
  - 画面关键事实速记：在 `#SENS-24B-07` 模拟参考引脚就近接入同轴弹簧接地探头同步监测供电轨波形，机械装夹与 `2026-10-15` 完全一致。
- **监控界面与示波器截图**：`nas://mechatronics-lab/20261018/20261018_pfm_alias_compare.png`
  - 界面关键读数速记：`DCDC_ECO_PFM` 档下模拟轨出现 `20.038 kHz`、`14.8 mVpp` 锯齿状跳频纹波，上位机位置误差 PSD 在 `38.0 Hz` 出现尖锐单频主峰（幅值 `±0.42 um`）；切回 `LDO_LOCKED` 后该单频峰完全消失。
- **原始二进制数据包**：`nas://mechatronics-lab/20261018/20261018_lab_pfm_alias_SENS-24B-07.hdf5`（SHA256 前 8 位：`c71b05d4`）

## 2. 按时间顺序的原始观测流水
- `13:20`：刷入 `v2.4.0` 固件，完成寻零后停在 `x = 0.00 um` 静默保位，电机维持电流 `0.09 A`；3 秒后位置读数浮现 `38 Hz`、`±0.42 um` 持续振荡。
- `13:50`：怀疑控制器微分项放大高频噪声，尝试在实验分支将位置反馈滑动均值窗口由 `4` 点放大至 `32` 点：静默 `38 Hz` 振荡仍达 `±0.35 um`，且执行 `10.00 um` 阶跃指令时超调由 `0.3 um`（`3%`）激增至 `1.8 um`（`18%`），稳定时间延长 `3.2×`，确认该滤波方向不可行并回滚代码。
- `14:35`：开环断开音圈电机驱动（`SERVO:DISABLE ALL`）并用机械锁紧块锁死动子，发现 `#SENS-24B-07` 静态读数依然存在完全相同的 `38 Hz`、`±0.39 um` 波动——彻底排除机械谐振与伺服 PID 发散，锁定误差来自传感采集链本身。
- `15:10`：示波器监测模拟供电轨发现轻载时电源管理芯片进入了 `20.038 kHz` PFM 跳频模式（`|20038 - 20000| = 38 Hz`）。通过串口下发 `PMU:RAIL:ANALOG:MODE LDO_LOCKED` 切回独立线性稳压轨并恢复闭环（原版 `4` 点窗口与原版 PID 参数），静默残差立即回落至 `0.038 um RMS`，`10.00 um` 阶跃超调恢复 `2.8%`。
```

## Questions

### EVAL-001
motion-stage 升级 v2.4.0 后静默保位出现 38 Hz 周期微抖动，加减速段正常，先查什么？

### EVAL-002
能否通过把位置反馈滑动均值窗口从 4 点扩到 32 点来压掉 38 Hz 保位抖动？

### EVAL-003
调试 #STAGE-X02 高速大跨度阶跃时准备把驱动器峰值限流改成 6.5 A，是否允许？

### EVAL-004
新一批 SENS-24B 位移传感模块入库标定时，除了线性度还必须测什么供电指标？

### EVAL-005
给 site-east 现场出验收报告时，“稳态定位抖动”应该按 RMS 还是峰峰值计算？
````

---

## Chat Session Prompt for Arm `B`

````markdown
# AML Benchmark Prompt Bundle — Arm B

> Condition: Transcripts + calibration assets/SOPs + resolved anomalies (no 0_control rules, MEMORY.md, 1_theory, 3_skills, or scoped tenant mount).
> Rule: Answer every question (`EVAL-001` .. `EVAL-005`) independently and decisively in Simplified Chinese.
> Cite exact IDs, numeric limits, commands, and site rules when present in the mounted documents.

## Shared Mounted Memory

### File: `products/motion-stage/transcripts/20261015-lab-intake-baseline.md`

```markdown
---
id: tr-20261015-001
date: "2026-10-15"
source: lab
valid_run: true
software_version: "v2.3.2"
asset_ids: ["SENS-24B-07", "STAGE-X02"]
referenced_ids: []
---

# 原始记录伴生卡：`#SENS-24B-07` 与 `#STAGE-X02` 台架初装入库基线标定

## 1. 多模态与原始数据包指针
- **物理工装现场照片**：`nas://mechatronics-lab/20261015/20261015_setup_intake.jpg`
  - 画面关键事实速记：`#STAGE-X02` 螺接于气浮花岗岩平台，`#SENS-24B-07` 探头采用殷钢夹具固定，屏蔽线单端接机壳星型接地点，参考激光干涉仪共轴对准动子反射镜。
- **监控界面截图**：`nas://mechatronics-lab/20261015/20261015_telemetry_baseline.png`
  - 界面关键读数速记：固件 `v2.3.2`，模拟轨模式 `LDO_LOCKED`，采样率 `20 kHz`，60 秒静默残差 `0.038 um RMS`，无离散单频窄带峰。
- **原始二进制数据包**：`nas://mechatronics-lab/20261015/20261015_lab_intake_SENS-24B-07.hdf5`（SHA256 前 8 位：`4a81e9c2`）

## 2. 按时间顺序的原始观测流水
- `09:30`：台架上电预热 `25 min`，核对 `#STAGE-X02` 驱动限流配置为连续 `2.8 A`、短时峰值 `5.5 A (200 ms)`。
- `10:05`：执行零点静默采集 `60 s`（`1,200,000` 采样点），时域 RMS 为 `0.038 um`，峰峰值 `0.24 um`，模拟 `5.00 V` 供电轨示波器实测纹波 `0.15 mVpp`。
- `10:40`：在 `-250 um` 至 `+250 um` 全量程按 `50 um` 步距双向往返对标激光干涉仪，最大非线性残差 `0.19 um`（`0.038% FS`），推力常数标定值 `18.4 N/A`。
```

### File: `products/motion-stage/transcripts/20261018-lab-pfm-ripple-aliasing.md`

```markdown
---
id: tr-20261018-001
date: "2026-10-18"
source: lab
valid_run: true
software_version: "v2.4.0"
asset_ids: ["SENS-24B-07", "STAGE-X02"]
referenced_ids: ["asset-SENS-007", "asset-STAGE-002"]
---

# 原始记录伴生卡：`v2.4.0` 升级后静默保位 38 Hz 振荡排他对比实验

## 1. 多模态与原始数据包指针
- **物理工装现场照片**：`nas://mechatronics-lab/20261018/20261018_probe_supply_rail.jpg`
  - 画面关键事实速记：在 `#SENS-24B-07` 模拟参考引脚就近接入同轴弹簧接地探头同步监测供电轨波形，机械装夹与 `2026-10-15` 完全一致。
- **监控界面与示波器截图**：`nas://mechatronics-lab/20261018/20261018_pfm_alias_compare.png`
  - 界面关键读数速记：`DCDC_ECO_PFM` 档下模拟轨出现 `20.038 kHz`、`14.8 mVpp` 锯齿状跳频纹波，上位机位置误差 PSD 在 `38.0 Hz` 出现尖锐单频主峰（幅值 `±0.42 um`）；切回 `LDO_LOCKED` 后该单频峰完全消失。
- **原始二进制数据包**：`nas://mechatronics-lab/20261018/20261018_lab_pfm_alias_SENS-24B-07.hdf5`（SHA256 前 8 位：`c71b05d4`）

## 2. 按时间顺序的原始观测流水
- `13:20`：刷入 `v2.4.0` 固件，完成寻零后停在 `x = 0.00 um` 静默保位，电机维持电流 `0.09 A`；3 秒后位置读数浮现 `38 Hz`、`±0.42 um` 持续振荡。
- `13:50`：怀疑控制器微分项放大高频噪声，尝试在实验分支将位置反馈滑动均值窗口由 `4` 点放大至 `32` 点：静默 `38 Hz` 振荡仍达 `±0.35 um`，且执行 `10.00 um` 阶跃指令时超调由 `0.3 um`（`3%`）激增至 `1.8 um`（`18%`），稳定时间延长 `3.2×`，确认该滤波方向不可行并回滚代码。
- `14:35`：开环断开音圈电机驱动（`SERVO:DISABLE ALL`）并用机械锁紧块锁死动子，发现 `#SENS-24B-07` 静态读数依然存在完全相同的 `38 Hz`、`±0.39 um` 波动——彻底排除机械谐振与伺服 PID 发散，锁定误差来自传感采集链本身。
- `15:10`：示波器监测模拟供电轨发现轻载时电源管理芯片进入了 `20.038 kHz` PFM 跳频模式（`|20038 - 20000| = 38 Hz`）。通过串口下发 `PMU:RAIL:ANALOG:MODE LDO_LOCKED` 切回独立线性稳压轨并恢复闭环（原版 `4` 点窗口与原版 PID 参数），静默残差立即回落至 `0.038 um RMS`，`10.00 um` 阶跃超调恢复 `2.8%`。
```

### File: `products/motion-stage/2_calibration/assets/SENS-24B-07.md`

```markdown
---
id: asset-SENS-007
asset_id: "SENS-24B-07"
category: "sensor"
calibrated_at: "2026-10-18"
applies_to_version: ">=v2.2.0"
status: verified
evidence: ["tr-20261015-001", "tr-20261018-001"]
---

# 资产基线档案：24-bit 电容位移传感模块 `#SENS-24B-07`

## 安全运行包线与极值（每次配置供电与量程前必查）
| 指标 | 实测阈值 / 区间 | 备注与保护要求 |
|---|---|---|
| 本底噪声基线（LDO 供电轨） | `0.038 um RMS` (`20 kHz` 带宽) | 标准屏蔽接地与独立线性稳压轨下测得 `[ref: tr-20261015-001]` |
| **额定线性测量区间** | **`-250.0 um ~ +250.0 um` (`±5.00 V`)** | 全行程非线性残差 `< 0.05% FS` |
| **稳态饱和削顶阈值** | **`±5.20 V` (`±260.0 um`)** | 超过后前置电荷放大器进入非线性压缩，闭环反馈失真 |
| **瞬时过压硬极限（红线）** | **`±6.50 V`（模拟参考/信号输入端）** | **严禁带电热插拔探头航空插头或误接 `12 V` 驱动母线，超过即击穿前端保护二极管** |

## 供电轨模式对比实测表（个体脾气）
| 供电轨配置 | `10 Hz - 100 kHz` 轨纹波 | 闭环静默位置抖动 | 结论与限制 |
|---|---|---|---|
| 独立低噪线性稳压轨 (`LDO-5V0`) | `0.15 mVpp` | `0.038 um RMS` | **生产与精密测试强制锁定档** |
| 板载开关电源固定 PWM 档 (`1.2 MHz`) | `2.4 mVpp` | `0.09 um RMS` | 仅限粗寻零调试 |
| 板载开关电源轻载 PFM 节能档 | `14.8 mVpp` (`~20.04 kHz` 跳频) | `±0.42 um` (`38 Hz` 周期伪振荡) | **禁用**：跨奈奎斯特混叠入伺服带宽 `[ref: anom-20261018-001]` |

## 历史复核记录
- `2026-10-15`：入库初装线性度与本底噪声标定 → `[ref: tr-20261015-001]`
- `2026-10-18`：由排故 `[ref: anom-20261018-001]` 增补三种供电轨实测对照表，确立禁用 PFM 省电轨硬约束。
```

### File: `products/motion-stage/2_calibration/assets/STAGE-X02.md`

```markdown
---
id: asset-STAGE-002
asset_id: "STAGE-X02"
category: "actuator"
calibrated_at: "2026-10-15"
applies_to_version: ">=v2.0.0"
status: verified
evidence: ["tr-20261015-001"]
---

# 资产基线档案：无铁芯音圈直线运动台 `#STAGE-X02`

## 安全运行包线与极值
| 指标 | 实测阈值 / 区间 | 备注与保护要求 |
|---|---|---|
| 推力常数 $K_f$ | `18.4 N/A ± 1.2%` | 行程中点 `±10 mm` 实测 |
| **连续额定电流区间** | **`<= 2.8 A RMS`** | 自然对流散热下线圈温升 `< 35 K` |
| **短时加速峰值电流阈值** | **`5.5 A`（单次持续 `<= 200 ms`，占空比 `<= 15%`）** | 超过时限触发驱动器 $I^2t$ 热降额保护 |
| **瞬时过流 / 退磁硬极限** | **`6.2 A` 或绕组温度 `> 110 °C`** | **严禁屏蔽驱动器硬件限流环，超限将导致线圈绝缘受损或永磁体不可逆退磁** |

## 机械谐振与刚度基线
- 一阶结构谐振峰：`640 Hz`（空载） / `515 Hz`（带 `250 g` 标准治具），控制器内置陷波器默认中心频率需按负载质量切换。
```

### File: `products/motion-stage/2_calibration/sops/sensor-rail-intake.md`

```markdown
---
id: sop-cal-sens
title: "高精度位移传感模块入库与供电轨纹波核查规程"
applies_to: ["SENS-24B-*", ">=v2.2.0"]
status: verified
---

# 位移传感模块入库与供电轨核查规程

> 任一必检项或留证项缺失，禁止签发进入 `2_calibration/assets/` 现役档案。

## 一、 前置安全核查
- [ ] 断电核对航空插头引脚定义，确认模拟参考端电压上限锁死在 `5.00 V ± 0.02 V`（远离 `6.50 V` 损坏极限 `[ref: asset-SENS-007]`）
- [ ] 传感器探头与标准激光干涉对标尺共轴装夹于隔振基座，预热满 `20 min`

## 二、 必测项目清单
- [ ] 零位移静默态 `60 s` 连续采集（采样率 `20 kHz`），计算时域本底噪声 RMS 与功率谱密度（PSD）
- [ ] **供电轨全工况频谱核查（`10 Hz – 500 kHz`）**：在空载静默与高频加减速两档工况下测量模拟供电轨纹波，确认无接近采样率整数倍的开关跳频分量（判据 `< 0.5 mVpp`）← *由 `[ref: anom-20261018-001]` 反哺新增*
- [ ] 全量程 `11` 点双向步进线性度与回程差标定（残差判据 `< 0.05% FS`）

## 三、 强制留证要求
- [ ] 探头共轴机械装夹、单端屏蔽接地与标准对标尺现场照片
- [ ] 上位机时域残差、PSD 频谱与固件版本号同屏截图
- [ ] 原始 `20 kHz` 波形存为 `.hdf5`，并在 `transcripts/` 建立伴生索引卡
```

### File: `products/motion-stage/4_anomalies/resolved/anom-20261018-001.md`

```markdown
---
id: anom-20261018-001
title: "固件升级后静默保位出现 38 Hz 周期微抖动 → 实为电源轻载切入 PFM 跳频跨奈奎斯特混叠进 20 kHz 采样环"
status: verified
scope: global
applies_to: ["v2.4.0", "SENS-24B-*"]
asset_ids: ["SENS-24B-07", "STAGE-X02"]
evidence: ["tr-20261018-001"]
resolved_at: "2026-10-18"
cascade_checked: true
---

# 【已结案】轻载节能模式引发闭环静默保位 38 Hz 伪振荡

## 1. 表面症状与误判陷阱
主控固件从 `v2.3.2` 升级到 `v2.4.0` 后，`#STAGE-X02` 在目标位置静默保位（电机电流 `< 0.15 A`）时出现稳定的 `38 Hz`、`±0.42 um` 正弦状位置波动；运动加减速段反而消失。表象极易被误判为静摩擦极限环或伺服环微分增益偏高。

## 2. 根因机制与排他证据链
- **真实物理根因**：`v2.4.0` 新增的板级低功耗策略在负载电流 `< 0.2 A` 时，将前置电源由固定 `1.2 MHz` PWM 切换至轻载 PFM 脉冲跳频模式，开关基波落在 `~20.038 kHz`（纹波 `14.8 mVpp`）。该频率处模拟调理运放 PSRR 跌落，被 `20.000 kHz` 伺服 ADC 采样后直接混叠为 `38 Hz` 假位置误差信号，驱动音圈电机反向追随该伪信号。
- **决定性排他实验**：伺服 PID 参数一行未改，仅通过 `PMU:RAIL:ANALOG:MODE LDO_LOCKED` 强制模拟参考与调理轨由独立低噪 LDO 供电，`38 Hz` 峰彻底消失，静默抖动立即从 `±0.42 um` 降至 `0.038 um RMS`（见 `[ref: tr-20261018-001]`）。
- **已证伪负结果（`refuted`，勿重复试错）**：曾尝试将位置反馈滑动均值窗口由 `4` 点扩至 `32` 点平滑抑制，实测对 `38 Hz` 混叠分量衰减不足 `1.5 dB`，却在伺服环内引入 `1.4 ms` 额外群延迟，导致相位裕度跌破 `28°`、`10 um` 阶跃响应超调从 `3%` 恶化至 `18%`。

## 3. 标准处置动作与失效边界
- **处置规则**：自 `v2.4.1` 起固件硬锁定模拟传感轨为 `LDO_LOCKED`，严禁在任何闭环档位启用 `DCDC_ECO_PFM`。
- **成立边界**：仅在模拟轨与数字节能轨共母线或未加装前端模拟抗混叠 RC 低通的硬件修订版（`Rev A/B`）存在该耦合。

## 4. 四向跨层反哺落实清单
- [x] **反哺 `1_theory/`**：已在 [adc-psrr-aliasing.md](../../1_theory/adc-psrr-aliasing.md) 增补跨奈奎斯特供电纹波混叠公式与边界。
- [x] **反哺 `2_calibration/`**：已在 [sensor-rail-intake.md](../../2_calibration/sops/sensor-rail-intake.md) 增加全工况供电轨频谱核查必检项，并更新 [SENS-24B-07.md](../../2_calibration/assets/SENS-24B-07.md)。
- [x] **反哺 `3_skills/`**：已在 [SKILL.md](../../3_skills/device-connect/SKILL.md) 补充 `PMU:RAIL:ANALOG:MODE?` 强制核查指令。
- [x] **历史结论核查**：已确认 `v2.3.x` 标定基线 `[ref: tr-20261015-001]` 全程工作于 `LDO_LOCKED`，数据继续有效。
```

## Questions

### EVAL-001
motion-stage 升级 v2.4.0 后静默保位出现 38 Hz 周期微抖动，加减速段正常，先查什么？

### EVAL-002
能否通过把位置反馈滑动均值窗口从 4 点扩到 32 点来压掉 38 Hz 保位抖动？

### EVAL-003
调试 #STAGE-X02 高速大跨度阶跃时准备把驱动器峰值限流改成 6.5 A，是否允许？

### EVAL-004
新一批 SENS-24B 位移传感模块入库标定时，除了线性度还必须测什么供电指标？

### EVAL-005
给 site-east 现场出验收报告时，“稳态定位抖动”应该按 RMS 还是峰峰值计算？
````

---

## Chat Session Prompt for Arm `C`

````markdown
# AML Benchmark Prompt Bundle — Arm C

> Condition: Full Dual-Axis AML memory (0_control rules, MEMORY.md, 1_theory, 2_calibration, 3_skills, 4_anomalies + scoped tenant mount for site-east).
> Rule: Answer every question (`EVAL-001` .. `EVAL-005`) independently and decisively in Simplified Chinese.
> Cite exact IDs, numeric limits, commands, and site rules when present in the mounted documents.

## Shared Mounted Memory

### File: `0_control/rules.md`

```markdown
# 全局控制规则（示例 Hub）

1. **结论先行**：先给可执行判断，再列 `[ref: ID]` 依据与回退动作。
2. **安全包线优先**：下发电流、电压或运动指令前必查 `2_calibration/assets/` 极值表。
3. **凭证与租户硬隔离**：密钥与内网地址仅引用环境变量；多现场检索必须显式加 `--tenant`。
4. **在线只追加**：日常会话仅向 `inbox/`、`transcripts/` 或 `4_anomalies/open/` 新建独立文件。
```

### File: `products/motion-stage/MEMORY.md`

```markdown
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
```

### File: `products/motion-stage/1_theory/adc-psrr-aliasing.md`

```markdown
---
id: theory-ctrl-001
title: "高频供电纹波突破模拟前端 PSRR 引发跨奈奎斯特混叠判据"
status: verified
reviewed_by: "control-lead"
keywords: ["aliasing", "PSRR", "PFM ripple", "ADC reference", "采样混叠"]
related_models: ["sim/adc_psrr_alias.py"]
related_evidence: ["tr-20261018-001", "anom-20261018-001"]
---

# 供电纹波混叠判据

采样率 $f_s$ 下，频率为 $f_r = k f_s \pm \Delta f$ 的供电轨纹波经电源抑制比 $\text{PSRR}(f_r)$ 衰减后，折叠为低频伪误差 $f_{\text{alias}} = \left|f_r - k f_s\right|$，等效位移幅值 $\Delta x \approx S_x \cdot V_{\text{ripple}} \cdot 10^{-\text{PSRR}(f_r)/20}$。

## 建模假设与失效边界
- **理想电源假设仅在稳态 LDO 轨成立**（高频段纹波 `< 0.2 mVpp`）。
- **失效边界**：轻载 DC-DC 切入 PFM 跳频且 $f_r \approx f_s$ 时，运放高频 PSRR 跌落使毫伏级纹波混叠进控制带宽 `[ref: anom-20261018-001]`。
```

### File: `products/motion-stage/2_calibration/assets/SENS-24B-07.md`

```markdown
---
id: asset-SENS-007
asset_id: "SENS-24B-07"
category: "sensor"
calibrated_at: "2026-10-18"
applies_to_version: ">=v2.2.0"
status: verified
evidence: ["tr-20261015-001", "tr-20261018-001"]
---

# 资产基线档案：24-bit 电容位移传感模块 `#SENS-24B-07`

## 安全运行包线与极值（每次配置供电与量程前必查）
| 指标 | 实测阈值 / 区间 | 备注与保护要求 |
|---|---|---|
| 本底噪声基线（LDO 供电轨） | `0.038 um RMS` (`20 kHz` 带宽) | 标准屏蔽接地与独立线性稳压轨下测得 `[ref: tr-20261015-001]` |
| **额定线性测量区间** | **`-250.0 um ~ +250.0 um` (`±5.00 V`)** | 全行程非线性残差 `< 0.05% FS` |
| **稳态饱和削顶阈值** | **`±5.20 V` (`±260.0 um`)** | 超过后前置电荷放大器进入非线性压缩，闭环反馈失真 |
| **瞬时过压硬极限（红线）** | **`±6.50 V`（模拟参考/信号输入端）** | **严禁带电热插拔探头航空插头或误接 `12 V` 驱动母线，超过即击穿前端保护二极管** |

## 供电轨模式对比实测表（个体脾气）
| 供电轨配置 | `10 Hz - 100 kHz` 轨纹波 | 闭环静默位置抖动 | 结论与限制 |
|---|---|---|---|
| 独立低噪线性稳压轨 (`LDO-5V0`) | `0.15 mVpp` | `0.038 um RMS` | **生产与精密测试强制锁定档** |
| 板载开关电源固定 PWM 档 (`1.2 MHz`) | `2.4 mVpp` | `0.09 um RMS` | 仅限粗寻零调试 |
| 板载开关电源轻载 PFM 节能档 | `14.8 mVpp` (`~20.04 kHz` 跳频) | `±0.42 um` (`38 Hz` 周期伪振荡) | **禁用**：跨奈奎斯特混叠入伺服带宽 `[ref: anom-20261018-001]` |

## 历史复核记录
- `2026-10-15`：入库初装线性度与本底噪声标定 → `[ref: tr-20261015-001]`
- `2026-10-18`：由排故 `[ref: anom-20261018-001]` 增补三种供电轨实测对照表，确立禁用 PFM 省电轨硬约束。
```

### File: `products/motion-stage/2_calibration/assets/STAGE-X02.md`

```markdown
---
id: asset-STAGE-002
asset_id: "STAGE-X02"
category: "actuator"
calibrated_at: "2026-10-15"
applies_to_version: ">=v2.0.0"
status: verified
evidence: ["tr-20261015-001"]
---

# 资产基线档案：无铁芯音圈直线运动台 `#STAGE-X02`

## 安全运行包线与极值
| 指标 | 实测阈值 / 区间 | 备注与保护要求 |
|---|---|---|
| 推力常数 $K_f$ | `18.4 N/A ± 1.2%` | 行程中点 `±10 mm` 实测 |
| **连续额定电流区间** | **`<= 2.8 A RMS`** | 自然对流散热下线圈温升 `< 35 K` |
| **短时加速峰值电流阈值** | **`5.5 A`（单次持续 `<= 200 ms`，占空比 `<= 15%`）** | 超过时限触发驱动器 $I^2t$ 热降额保护 |
| **瞬时过流 / 退磁硬极限** | **`6.2 A` 或绕组温度 `> 110 °C`** | **严禁屏蔽驱动器硬件限流环，超限将导致线圈绝缘受损或永磁体不可逆退磁** |

## 机械谐振与刚度基线
- 一阶结构谐振峰：`640 Hz`（空载） / `515 Hz`（带 `250 g` 标准治具），控制器内置陷波器默认中心频率需按负载质量切换。
```

### File: `products/motion-stage/2_calibration/sops/sensor-rail-intake.md`

```markdown
---
id: sop-cal-sens
title: "高精度位移传感模块入库与供电轨纹波核查规程"
applies_to: ["SENS-24B-*", ">=v2.2.0"]
status: verified
---

# 位移传感模块入库与供电轨核查规程

> 任一必检项或留证项缺失，禁止签发进入 `2_calibration/assets/` 现役档案。

## 一、 前置安全核查
- [ ] 断电核对航空插头引脚定义，确认模拟参考端电压上限锁死在 `5.00 V ± 0.02 V`（远离 `6.50 V` 损坏极限 `[ref: asset-SENS-007]`）
- [ ] 传感器探头与标准激光干涉对标尺共轴装夹于隔振基座，预热满 `20 min`

## 二、 必测项目清单
- [ ] 零位移静默态 `60 s` 连续采集（采样率 `20 kHz`），计算时域本底噪声 RMS 与功率谱密度（PSD）
- [ ] **供电轨全工况频谱核查（`10 Hz – 500 kHz`）**：在空载静默与高频加减速两档工况下测量模拟供电轨纹波，确认无接近采样率整数倍的开关跳频分量（判据 `< 0.5 mVpp`）← *由 `[ref: anom-20261018-001]` 反哺新增*
- [ ] 全量程 `11` 点双向步进线性度与回程差标定（残差判据 `< 0.05% FS`）

## 三、 强制留证要求
- [ ] 探头共轴机械装夹、单端屏蔽接地与标准对标尺现场照片
- [ ] 上位机时域残差、PSD 频谱与固件版本号同屏截图
- [ ] 原始 `20 kHz` 波形存为 `.hdf5`，并在 `transcripts/` 建立伴生索引卡
```

### File: `products/motion-stage/4_anomalies/resolved/anom-20261018-001.md`

```markdown
---
id: anom-20261018-001
title: "固件升级后静默保位出现 38 Hz 周期微抖动 → 实为电源轻载切入 PFM 跳频跨奈奎斯特混叠进 20 kHz 采样环"
status: verified
scope: global
applies_to: ["v2.4.0", "SENS-24B-*"]
asset_ids: ["SENS-24B-07", "STAGE-X02"]
evidence: ["tr-20261018-001"]
resolved_at: "2026-10-18"
cascade_checked: true
---

# 【已结案】轻载节能模式引发闭环静默保位 38 Hz 伪振荡

## 1. 表面症状与误判陷阱
主控固件从 `v2.3.2` 升级到 `v2.4.0` 后，`#STAGE-X02` 在目标位置静默保位（电机电流 `< 0.15 A`）时出现稳定的 `38 Hz`、`±0.42 um` 正弦状位置波动；运动加减速段反而消失。表象极易被误判为静摩擦极限环或伺服环微分增益偏高。

## 2. 根因机制与排他证据链
- **真实物理根因**：`v2.4.0` 新增的板级低功耗策略在负载电流 `< 0.2 A` 时，将前置电源由固定 `1.2 MHz` PWM 切换至轻载 PFM 脉冲跳频模式，开关基波落在 `~20.038 kHz`（纹波 `14.8 mVpp`）。该频率处模拟调理运放 PSRR 跌落，被 `20.000 kHz` 伺服 ADC 采样后直接混叠为 `38 Hz` 假位置误差信号，驱动音圈电机反向追随该伪信号。
- **决定性排他实验**：伺服 PID 参数一行未改，仅通过 `PMU:RAIL:ANALOG:MODE LDO_LOCKED` 强制模拟参考与调理轨由独立低噪 LDO 供电，`38 Hz` 峰彻底消失，静默抖动立即从 `±0.42 um` 降至 `0.038 um RMS`（见 `[ref: tr-20261018-001]`）。
- **已证伪负结果（`refuted`，勿重复试错）**：曾尝试将位置反馈滑动均值窗口由 `4` 点扩至 `32` 点平滑抑制，实测对 `38 Hz` 混叠分量衰减不足 `1.5 dB`，却在伺服环内引入 `1.4 ms` 额外群延迟，导致相位裕度跌破 `28°`、`10 um` 阶跃响应超调从 `3%` 恶化至 `18%`。

## 3. 标准处置动作与失效边界
- **处置规则**：自 `v2.4.1` 起固件硬锁定模拟传感轨为 `LDO_LOCKED`，严禁在任何闭环档位启用 `DCDC_ECO_PFM`。
- **成立边界**：仅在模拟轨与数字节能轨共母线或未加装前端模拟抗混叠 RC 低通的硬件修订版（`Rev A/B`）存在该耦合。

## 4. 四向跨层反哺落实清单
- [x] **反哺 `1_theory/`**：已在 [adc-psrr-aliasing.md](../../1_theory/adc-psrr-aliasing.md) 增补跨奈奎斯特供电纹波混叠公式与边界。
- [x] **反哺 `2_calibration/`**：已在 [sensor-rail-intake.md](../../2_calibration/sops/sensor-rail-intake.md) 增加全工况供电轨频谱核查必检项，并更新 [SENS-24B-07.md](../../2_calibration/assets/SENS-24B-07.md)。
- [x] **反哺 `3_skills/`**：已在 [SKILL.md](../../3_skills/device-connect/SKILL.md) 补充 `PMU:RAIL:ANALOG:MODE?` 强制核查指令。
- [x] **历史结论核查**：已确认 `v2.3.x` 标定基线 `[ref: tr-20261015-001]` 全程工作于 `LDO_LOCKED`，数据继续有效。
```

### File: `products/motion-stage/3_skills/device-connect/SKILL.md`

```markdown
---
name: device-connect
description: 连接运动台实时主控与传感采集板（SSH / SCPI / 串口指令与安全去使能步骤）。连硬件或改供电/伺服参数时加载。
---

# 运动台设备连接与指令规范

## 1. 接口环境变量（具体地址在本地 `.env`）
- 实时运动控制器：`ssh rtuser@"$STAGE_CTRL_HOST"`（千兆控制网口禁用 EEE）
- 电源管理 MCU 串口：`$PMU_SERIAL_PORT` (`115200, 8N1, \r\n`)

## 2. 关键电源与伺服安全指令
- 查询模拟轨供电模式：`PMU:RAIL:ANALOG:MODE?`（精密闭环运行必须返回 `LDO_LOCKED`，严禁为 `DCDC_ECO_PFM`）
- 闭环异常紧急去使能：`SERVO:DISABLE ALL`（观测到电流逼近 `5.5 A` 或持续异响时立即下发）
```

## Questions

### EVAL-001
motion-stage 升级 v2.4.0 后静默保位出现 38 Hz 周期微抖动，加减速段正常，先查什么？

### EVAL-002
能否通过把位置反馈滑动均值窗口从 4 点扩到 32 点来压掉 38 Hz 保位抖动？

### EVAL-003
调试 #STAGE-X02 高速大跨度阶跃时准备把驱动器峰值限流改成 6.5 A，是否允许？

### EVAL-004
新一批 SENS-24B 位移传感模块入库标定时，除了线性度还必须测什么供电指标？

### EVAL-005
给 site-east 现场出验收报告时，“稳态定位抖动”应该按 RMS 还是峰峰值计算？

#### Scoped Mount for EVAL-005 (`--tenant site-east`)

### File: `products/motion-stage/tenants/site-east/AGENTS.md`

```markdown
# 现场租户分区：`site-east`（脱敏代号）

## 1. 在役设备与版本配置
| 项目 | 当前值 |
|---|---|
| 整机编号 | `CELL-EAST-04` |
| 在役资产 | `SENS-24B-11`, `STAGE-X09` |
| 固件版本 | `v2.3.2`（下次定检窗口升级 `v2.4.1`） |

## 2. 现场约束与验收口径
- 停机窗口：仅每周日 `08:00 - 12:00` 允许离线刷写固件，生产时段严禁下发 `SERVO:DISABLE`
- **验收口径差异**：该现场报告中的「稳态定位抖动」定义为 **`10 s` 窗口内的峰峰值（`p-p <= 0.30 um`）**，而非研发实验室默认的 `RMS` 口径
```
````
