# 离线蒸馏 · 阶段二：隔离工作树跨层整理与四向反哺提示词（Consolidation）

你在 `aml dream start` 创建的隔离 `git worktree`（`.dream-worktree`）中工作。请直接编辑工作树内的 Markdown 文件，完成后由外部运行 `aml dream diff` 执行零 Token 机械校验并导出真实 `git diff` 供人工审阅合并（严禁手搓 `.patch` 行号）。

## 输入
- 经阶段一确认有效（`valid_run: true`）的新增 `inbox/` 与 `transcripts/`
- 目标产品的 `1_theory/`、`2_calibration/`、`3_skills/`、`4_anomalies/`、`MEMORY.md`（Hub 模式下含 `0_control/`）
- 工作树根目录下的真实引用频次表 `reference-stats.txt`

## 执行动作（严格按顺序）

### 0. 分拣全局 `inbox/`（仅 Hub 模式）
- 属于单台机器编译器、驱动、路径或网口配置的经验 → 合并入 `0_control/hosts/<host>/env.md`；
- 属于具体产品线的实验流水或异常 → 迁入对应 `products/<slug>/transcripts/` 或 `4_anomalies/open/`，并在工作树中移除已消化的 `inbox/` 原文件。

### 1. 排故结案驱动的四向连锁反哺（最高优先级）
对每一条新结案或 `cascade_checked: false` 的 `4_anomalies/resolved/*.md`：
- **向 `1_theory/` 巡检**：实测根因是否突破了某篇机理/仿真模型的理想化假设？若是，在该页「建模假设与成立边界」追加实测边界与反向引用 `[ref: <anom-id>]`。
- **向 `2_calibration/` 巡检**：是否暴露了入库/定期标定 SOP 漏检项？若是，增补 `sops/` 必检清单；若证实某件现役资产参数已漂移失准，将其旧档案改标 `status: stale` 并提示复标。
- **向 `3_skills/` 巡检**：是否源于通信时序、CLI 参数误用或数据存储选型错误（如高频波形误存 `.csv` 丢精度/丢时间戳）？若是，修补对应 `SKILL.md` 防呆规则。
- **向历史结论巡检**：检索全库曾依赖该错误前提的旧记录，追加 `[corrected: <anom-id>]` 或改标 `stale` / `refuted`，最后将该结案单更新为 `cascade_checked: true`。

### 2. 增量事实提炼与真值对账
- 将新增 `transcripts/` 中系统查不到、未来会复现的现象提炼进对应层（单次未归因观察一律标 `hypothesis` 或 `open`，严禁脑补未证实机理）。
- 对照 `transcripts/` 原始数据核验新增判断；与原始记录矛盾处改写并标 `[corrected: <tr-id>]`。

### 3. 版本/换件失效扫描与冲突标注
- 若在役软件版本或核心硬件资产 ID 发生切换，扫描全库 `applies_to` / `applies_to_version`：不再覆盖当前组合的改标 `status: stale`，并立即从 `MEMORY.md`（及 `0_control/INDEX.md`）移除。
- 若两条实测或模型结论互斥，**严禁私自折中删除**，统一标 `status: conflict`，并在 `change-log.md` 给出能裁决二者的最小排他实验设计。

### 4. 图谱瘦身与常驻索引升降级
- 修复断链，确保 `size(1_theory + MEMORY.md) / size(transcripts + 2_calibration + 4_anomalies) < 0.30`，剔除原文大段照搬。
- 依据 `reference-stats.txt`：被真实引用 `>= 3` 次的高价值条目提炼一句话升入 `MEMORY.md`；逼近 `200 行 / 25 KB` 上限时，将最久未引用的条目下沉回原目录。Hub 模式下同步刷新 `0_control/INDEX.md` 的项目一句话进度。

## 硬约束（提交前运行 `python3 scripts/aml.py check --repo .dream-worktree` 自检）
1. **不删历史**：过期标 `stale`，已证伪负结果标 `refuted`（保留供后续避坑引用）。
2. **无证据不立论**：所有 `verified` 条目必须具备 `applies_to` 边界与非空 `evidence` 锚点。
3. **零机密与租户硬隔离**：凭证、密钥、客户真名零入库；单一租户约束严禁写入全局层（`>= 2` 独立租户复现方可脱敏提议晋升）。
4. 在 `.dream-worktree/change-log.md` 输出变更摘要，以及**最需人工拍板的 `<= 5` 项关键判断**。
