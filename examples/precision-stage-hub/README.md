# 最小闭环示例：精密闭环运动台架（`precision-stage-hub`）

> 本目录所有型号、序列号与读数均为教学构造的通用机电控制样例，用于完整演示 **Hub 多机控制面 + 正交双轴产品记忆 + 四向排故反哺 + 租户物理隔离**。

## 这组示例演示了什么闭环

1. **原始事实落盘（`products/motion-stage/transcripts/20261018-lab-pfm-ripple-aliasing.md`）**
   主控固件升级至 `v2.4.0` 默认开启电源板轻载节能模式（DC-DC 切入 PFM 脉冲跳频档）后，线性运动台 `#STAGE-X02` 在静默保位段出现 `38 Hz`、`±0.42 um` 周期性位置抖动，表象酷似伺服环微分增益过高引发自激。
2. **排故归因与负结果留存（`4_anomalies/resolved/anom-20261018-001.md`）**
   曾尝试将反馈滑动均值窗口由 `4` 点扩至 `32` 点平滑噪声，实测无法消除混叠基波，反而引入 `1.4 ms` 相位滞后导致阶跃超调恶化至 `18%`（作为 `refuted` 负结果留档避坑）；排他实验证实系 PFM `20.038 kHz` 纹波经模拟前端有限高频 PSRR 混叠进 `20 kHz` ADC 采样环。
3. **四向跨层反哺**
   - **反哺 `1_theory/`**：在 `adc-psrr-aliasing.md` 补充高频供电纹波跨奈奎斯特混叠定量判据；
   - **反哺 `2_calibration/`**：在 `sops/sensor-rail-intake.md` 新增供电轨频谱纹波必检项，并在 `assets/SENS-24B-07.md` 标明禁用开关电源直供模拟参考轨；
   - **反哺 `MEMORY.md` 与 `0_control/INDEX.md`**：提炼为一行高频排故路由。

## 直接运行工具链验证

在仓库根目录执行：

```bash
python3 scripts/aml.py check --repo examples/precision-stage-hub
python3 scripts/aml.py start --repo examples/precision-stage-hub --host lab-bench-01 --agent demo
python3 scripts/aml.py search --repo examples/precision-stage-hub --product motion-stage "过载"
python3 scripts/aml.py search --repo examples/precision-stage-hub --product motion-stage --tenant site-east "验收"
python3 scripts/aml.py dream stats --repo examples/precision-stage-hub
```
