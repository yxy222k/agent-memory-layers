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
