---
id: theory-interferometry-001
title: 频域低相干干涉中的中心波长漂移与 2π 周期跳变判据
status: verified
reviewed_by: "optics-lead"
keywords: ["low-coherence interferometry", "SWLI", "FD-OCT", "wavelength drift", "2pi ambiguity", "SLD中心波长漂移"]
related_models: ["sim/envelope_phase_solver.py"]
related_evidence: ["tr-20261112-001", "anom-20261112-001"]
---

# 频域低相干干涉中的中心波长漂移与周期跳变判据

## 核心控制方程与物理图景
包络-相位联合解算中，粗光程 $L_{\text{env}}$ 由包络群延迟决定，精光程由载波相位 $\phi$ 决定。当解算器采用固定标称中心波数 $k_0 = 2\pi / \lambda_0$，而实际光源质心漂移 $\Delta\lambda = \lambda_{\text{real}} - \lambda_0$ 时：

1. **相位测距比例误差**：
   $$\frac{\Delta L_{\phi}}{L} \approx -\frac{\Delta \lambda}{\lambda_0}$$
   在 $\lambda_0 = 1310\text{ nm}$、光程差 $L = 500\text{ }\mu\text{m}$ 下，$\Delta\lambda = +2.4\text{ nm}$ 即引入约 $-0.92\text{ }\mu\text{m}$ 的偏置。
2. **$2\pi$ 整数级次跳变门限**：
   级次整数 $m = \operatorname{round}\!\left(\frac{2 L_{\text{env}} - \phi / k_0}{\lambda_0 / 2}\right)$。一旦包络估计与失配相位之差跨过 $\pm \lambda_0 / 4$（约 $\pm 327.5\text{ nm}$），级次 $m$ 跳变 $\pm 1$，表现为光程读数突跳半个中心波长（`~655 nm`）。

## 建模假设与成立边界
- **假设 1（恒定 $\lambda_0$ 假设）**：仅当光源工作在额定超辐射稳定区（如 `#SLD-1310-03` 在 `140–190 mA`，$\left|\Delta\lambda\right| < 0.05\text{ nm}$）且总光程差满足 $\left|L \cdot \Delta\lambda / \lambda_0\right| \ll \lambda_0 / 4$ 时成立。
- **失效边界**：下调 SLD 电流压制光强会导致严重红移并跨过跳变门限（实测反例见 `[ref: anom-20261112-001]`）。

## 实测印证与已知反例
- 实测数据包与光谱质心对比：`transcripts/20261112-lab-sld-low-current-drift.md`
- 排故结案单：`4_anomalies/resolved/anom-20261112-001.md`
