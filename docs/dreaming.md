# 离线蒸馏（Dreaming）与机械校验闭环

白天调台架、跑实验、救现场故障时，注意力必须留在主任务上——在线阶段只通过 `aml capture` 做零摩擦追加留证；而把散乱记录去重纠错、把排故结论反向织回机理与标定规程的工作，统一交给**离线双闸门蒸馏（Dreaming）**。

---

## 一、 为什么必须坚持「双人工闸门 + 隔离工作树真 Diff」

工程与实验场景不能跑无人看管的全自动覆盖：
1. 实验台一天会产生不少「接插件没锁紧」「未预热即开采」的无效记录，不经筛选直接蒸馏只会提炼出伪规律；
2. 蒸馏一旦静默改错某条安全阈值或版本范围，后续所有机器上的所有会话都会盲目信任它；
3. 让大模型直接手写 `.patch` 文本极易算错行号导致 `git apply` 失败——让 Agent 在隔离的 `git worktree` 中正常编辑文件、再由 `aml dream diff` 跑静态校验并导出真实 `git diff`，才是零故障做法。

完整三步闭环：

```text
[阶段 1：30 秒前置轻筛]
python3 scripts/aml.py dream triage --repo <repo>
   → 扫描待分拣 inbox/、新增 transcripts/、open 异常与待反哺结案单，生成 triage-list.md
   → 负责人花 30 秒勾掉废实验（标 valid_run: false）、确认哪些异常已真正破案
   ↓
[阶段 2：隔离工作树蒸馏与四向反哺]
python3 scripts/aml.py dream start --repo <repo>
   → 自动拉起 .dream-worktree 分支并统计全库真实引用频次 reference-stats.txt
   → 离线整理 Agent 按 dreaming/consolidate-prompt.md 在 .dream-worktree 内直接修改文件
   ↓
[阶段 3：零 Token 机械守卫 + 人工审 Diff 合并]
python3 scripts/aml.py dream diff --repo <repo>
   → 自动运行 aml check（核验行数/压缩比/必填元数据/断链/stale 零残留/机密扫描）
   → 输出 change-log.md（<=5 条人工必审判断）与真实 git diff
   → 审阅通过后 git merge dream/YYYYMMDD，并运行 aml dream clean 清理临时工作树
```

---

## 二、 核心知识飞轮：第四层（排故）反向驱动前三层进化

本系统最关键的自进化机制，是每当 `4_anomalies/resolved/` 中有一条排故单完成归因（`cascade_checked: false`）时，离线蒸馏必须沿四个方向执行连锁巡检：

1. **向 `1_theory/` 巡检（修正模型边界）**
   实测根因是否突破了现有理论或仿真模型的理想化假设？（例如：原闭环模型假设模拟供电轨理想无纹波，实测轻载开关电源跳频混叠进采样环 → 在对应机理页补充混叠判据与成立边界 `[ref: <anom-id>]`）。
2. **向 `2_calibration/` 巡检（补齐 SOP 与刷新资产档案）**
   - 是否暴露了某类模块入库或定检 SOP 漏测的指标？（→ 提议增补 `2_calibration/sops/` 必检项）
   - 是否证实某件现役资产参数已漂移失准？（→ 将旧基线改标 `status: stale`，关联新复标记录）
3. **向 `3_skills/` 巡检（修补连接、CLI 与存储防呆）**
   事故是否源于指令时序、默认配置隐患，或数据误存为 `.csv` 丢失精度与时间戳？（→ 提议更新对应 `SKILL.md` 的防呆检查）
4. **向历史旧结论巡检（推翻与更正）**
   检索全库曾依赖该错误前提的旧判断，逐条追加 `[corrected: <anom-id>]` 或改标 `stale` / `refuted`，完成后将该结案单置为 `cascade_checked: true`。

在 **Hub 模式**下，蒸馏同时负责清空 `inbox/`：将跨工具发现的主机环境坑归入 `0_control/hosts/<host>/env.md`，将产品流水归入对应 `products/<slug>/`，并刷新 `0_control/INDEX.md` 的产品一句话进度。

---

## 三、 三个事件触发的专项扫描

1. **发版 / 换件失效扫描（必做）**
   软件发布新版本或台架更换核心传感器/执行器序列号后，全库扫描 `applies_to` / `applies_to_version`：不再适用的条目改标 `status: stale` 并从 `MEMORY.md` 移除（若遗漏，`aml check` 会直接报错拦截）。
2. **多租户共性抽象晋升（多现场交付启用）**
   同一物理现象或排查规律在 **`>= 2` 个独立现场分区（`tenants/*`）** 复现时，提取为候选全局规则。晋升产物必须是**脱敏后的通用机制与判据**，严禁把单一现场的原始配置或业务指标直接搬入公共层。
3. **实验结论冲突挂起**
   两条实测或模型结论互斥时，严禁模型私自删除其中一条，统一标 `status: conflict`，并在 `change-log.md` 给出能一锤定音的最小排他实验方案。

---

## 四、 推荐运行节奏

- **日常增量蒸馏**：每累计 `15–20` 次有效捕获会话，或每周固定跑一次。
- **事件即时触发**：重大排故结案、主版本发布、核心资产换件当天额外跑一次专项扫描。
- **月度真值抽检**：每月随机抽取 `10` 条 `status: verified` 条目，人工顺着 `evidence` 回查 `transcripts/` 伴生卡与原始数据包。一旦发现无据脑补，立即暂停定时蒸馏并收紧提示词。
