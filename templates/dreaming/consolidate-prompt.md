# 离线蒸馏 · 阶段二：跨层整理与反哺提示词（Consolidation）

你在隔离的 `git worktree` 分支中工作，可直接修改工作树内的记忆文件；外壳脚本会自动导出 `git diff` 交由人工审阅合并。

## 输入
- 经阶段一确认有效（`valid_run: true`）的新增 `transcripts/`
- `1_theory/`、`2_calibration/`、`3_skills/`、`4_anomalies/`、`MEMORY.md`
- 脚本注入的真实引用统计表（各条目 `[ref: <id>]` 累计次数与最近引用日期）
- 当前在役软件版本与硬件 SN 清单

## 执行动作（严格按顺序）

### 1. 排故结案驱动的四向连锁反哺（最高优先级）
对每一条新结案（或 `cascade_checked: false`）的 `4_anomalies/resolved/*.md`：
- **查 `1_theory/`**：实测根因是否突破了某篇机理/仿真页的理想化假设？若是，在该页「建模假设与成立边界」追加实测边界与反向链接。
- **查 `2_calibration/`**：是否暴露了某类器件入库 SOP 漏检项？若是，增补 `sops/` Checklist；若证明某支现役器件参数已漂移，将其旧档案改标 `status: stale` 并提示重标定。
- **查 `3_skills/`**：是否源于串口时序、CLI 参数误用或数据存储格式（如误用 `csv` 丢精度）？若是，修补对应 `SKILL.md` 的防呆规则。
- **查全库历史结论**：检索所有曾依赖该错误前提的旧记录，追加 `[corrected: <结案单ID>]` 或改标 `stale` / `refuted`，然后将该结案单标为 `cascade_checked: true`。

### 2. 从增量事实提炼草稿与对账纠错
- 将新增 `transcripts/` 中系统查不到、未来会复现的新异常或经验，提炼进 `4_anomalies/open/` 或对应目录（单次观察一律标 `hypothesis` / `open`，不强行脑补物理机制）。
- 核对已有新增条目与 `transcripts/` 原始数据是否一致；不一致处改写并标 `[corrected: <transcript-id>]`。

### 3. 版本/换件失效扫描与冲突标注
- 若软件版本或核心器件 SN 发生变更，检查全库 `applies_to`：不再适用的改标 `status: stale`，并从 `MEMORY.md` 移除。
- 若发现两条实测或机理结论互斥，**严禁私自折中删除**，统一标 `status: conflict`，并在 `change-log.md` 给出能裁决二者的最小实验设计。

### 4. 图谱维护与 `MEMORY.md` 升降级
- 修复 `1_theory/` 断链；确保 `1_theory/` 总体积小于底层记录，剔除冗余原文摘抄。
- 依据真实引用统计：被引用 ≥3 次的高价值条目提炼一句话升入 `MEMORY.md`；若 `MEMORY.md` 超过 200 行 / 25KB，优先将最久未被引用的条目下沉回原层。

## 硬约束
1. **不得删除任何历史条目**（过期标 `stale`，证伪负结果标 `refuted`）。
2. **不得新增无 `transcripts/` 或文献证据支撑的事实**。
3. **凭证、客户真名、核心机密配方零入库**；不得把单一租户的特殊约束写成全局规则（≥2 租户复现方可脱敏提议晋升）。
4. 最后在工作树根目录输出 `change-log.md`：列出本次修改摘要，以及**最需要人工拍板的 ≤5 个关键判断**。
