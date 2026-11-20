# 最小闭环示例：1310nm 低相干干涉测量台架（`interferometry-mini`）

> 注：本目录下所有数值与器件编号均为教学演示构造的脱敏样例，用于展示**双轴记忆系统**如何跑通一次完整的「现场流水 → 排故归因 → 四向反哺」闭环。

## 这组文件演示了什么故事

1. **原始事实落盘（`transcripts/20261112-lab-sld-low-current-drift.md`）**
   测高反硅片时为避免光谱仪 `#SPEC-01` 触碰饱和阈值，操作员将 `#SLD-1310-03` 驱动电流从 `180 mA` 下调至 `45 mA`，随即出现等效光程慢漂与跳变；伴生卡记录了现场光路照、上位机截图与 `.hdf5` 路径。
2. **排故归因与负结果留存（`4_anomalies/resolved/anom-20261112-001.md`）**
   起初怀疑相位解包裹滤波发散，尝试加大滑动窗口证实无效且抹平台阶（记录为 `refuted` 负结果避坑）；后对照光谱发现 `45 mA` 下 SLD 中心波长红移 `2.4 nm` 且随温控微振，解算却写死了标称 `1310.0 nm`。
3. **离线蒸馏触发向 1 / 2 / 3 层的连锁反哺**
   - **反哺第一层（`1_theory/interferometry-phase-dispersion.md`）**：在相位解算机理页的「建模假设与失效边界」追加实测边界（低电流段中心波长恒定假设失效，给出定量灵敏度 $\Delta L / L = -\Delta \lambda / \lambda_0$）。
   - **反哺第二层（`2_calibration/`）**：在 `sops/sld-intake-calibration.md` 新增「全电流梯度中心波长漂移必测项」，并更新 `assets/SLD-1310-03.md` 的禁用电流下限（`< 90 mA` 禁用于精密相位测量，高反样品改调光谱仪积分档位或加固定衰减片）。
   - **反哺注入索引（`MEMORY.md`）**：提炼为一行高频排故路由与过载保护提醒。

## 试跑检索与蒸馏脚本

在仓库根目录可直接用本示例验证工具链：

```bash
./scripts/search.sh "过载阈值" examples/interferometry-mini
./scripts/dream-worktree.sh start examples/interferometry-mini
./scripts/dream-worktree.sh clean
```
