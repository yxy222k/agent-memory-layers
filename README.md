# agent-memory-layers

<details name="lang">
<summary>🌐 <b>English</b> — Click to switch language in-place</summary>

> Unified engineering memory for hardware-software & R&D systems: **Fleet Control Plane × Dual-Axis Domain Matrix (4 Engineering Domains × 4 Processing Stages), conflict-free multi-agent sync, troubleshooting-driven evolution, and dual-gate offline dreaming**.

A zero-dependency Markdown + Python 3 stdlib memory kit. No server, no database, no vector store — one Git repository powers a single product repo (`standalone`) or your entire multi-machine, multi-agent engineering fleet (`hub`).

## Why Flat Agent Memory & Single-Axis Compression Break Down

1. **Tool-bound flat memory** locks your rules and lessons inside one laptop or one vendor (Claude Code, Codex, Antigravity, etc.) and mixes personal preferences, host compiler paths, and hardware calibration values in the same bucket.
2. **Single-axis compression** (`transcripts → notes → wiki → system prompt`) works for pure-text Q&A, but degrades rapidly in robotics, embedded/FPGA systems, industrial automation, autonomous systems, and precision instruments:
   - **First-principles governing equations** and **unit `#SENS-24B-07`'s zero-offset drift** differ in half-life by orders of magnitude.
   - **Bus commands, `.hdf5`/`.pcapng` schemas, and external redaction checklists** are procedural skills — they should cost `0 tokens` until invoked.
   - **Troubleshooting tickets** have no known mechanism while open (they only need reproducibility), yet once resolved they must cascade backward to revise model assumptions, add missing intake checks, and invalidate stale conclusions.

---

## Architecture: Control Plane × Orthogonal Dual-Axis Product Engine

Deploy inside a single repository (`--mode standalone`) or as one private **Fleet Memory Hub** (`--mode hub`) across all machines, AI coding tools, and product lines:

### Control Plane (`0_control/` + `inbox/`, Hub Mode)
- `0_control/rules.md` — Owner-authored immutable behavioral & safety guardrails (`<= 4 KB`).
- `0_control/hosts/<hostname>/env.md` — Per-machine OS, toolchain, interface & path facts shared by every AI tool on that host.
- `0_control/INDEX.md` — Cross-product routing snapshot loaded when no specific workspace is active; workspace-aware `aml start --cwd` automatically mounts the matching product when inside a code repo.
- `inbox/` — Collision-free append-only online capture dropzone (`<timestamp>-<host>-<tool>-<slug>.md`), eliminating multi-machine Git merge conflicts.

### Product Kernel: 4 Engineering Domains × 4 Processing Stages

| Domain (Horizontal) | Directory | Holds | Lifecycle & Review |
|---|---|---|---|
| **① Theory & Models** | `1_theory/` | Governing laws, literature maps, simulation assumptions & failure bounds | Multi-agent exploration (one file per agent) + human review |
| **② Calibration & Assets** | `2_calibration/` | **SOPs**: intake/verification checklists; **Assets**: per-SN operating envelopes & calibration curves | Human SOPs; strict multimodal evidence checklists |
| **③ Procedural Skills** | `3_skills/` | Device/bus protocols, CLI replay, binary schemas (`hdf5/parquet/pcapng`), report redaction, notifications | On-demand `SKILL.md` (`0 tokens` at rest); **zero plaintext secrets** |
| **④ Anomalies & Root Cause** | `4_anomalies/` | **Open**: minimal reproducible snapshots; **Resolved**: root causes, `refuted` dead-ends, 4-way cascade checklists | Low-friction capture online; resolved items update ① / ② / ③ offline |

| Stage (Vertical) | Location | Mechanical Constraint (`aml check`) |
|---|---|---|
| **④ Injected** | `AGENTS.md` + `MEMORY.md` (+ `0_control/`) | Loaded at session start; `MEMORY.md <= 200 lines / 25 KB`; **0 `stale` IDs allowed** |
| **③ Navigation** | `1_theory/` + `3_skills/` | Navigation map ratio `size(1_theory + MEMORY.md) / size(base) <= 0.30` |
| **② Judgments & Baselines** | `2_calibration/` + `4_anomalies/` | Enforces `id`, `applies_to` bounds, `evidence` links & 6-state machine (`verified / hypothesis / open / refuted / stale / conflict`) |
| **① Ground-Truth Facts** | `transcripts/` | Append-only logs & multimodal sidecars pointing to rig photos, telemetry screenshots & `.hdf5`/`.pcapng` archives |

---

## Five Core Engineering Rules

1. **Conflict-free online capture, strict offline promotion**: Live sessions never overwrite curated files; agents append uniquely named files to `inbox/`, `transcripts/`, or `4_anomalies/open/`, allowing `Stop` hooks to auto-commit & push across machines with zero rebase conflicts.
2. **Troubleshooting 4-way backward cascade**: Every `resolved` anomaly audits `1_theory/` assumptions, `2_calibration/` SOPs/assets, `3_skills/` pitfalls, and historical conclusions.
3. **Five-level priority chain**: Immutable safety/secret/overload guardrails rule top-down (`1. Guardrails > 2. Host env`), while engineering parameters resolve by specificity (`3. Tenant site rules > 4. Per-SN asset baselines > 5. Generic theory & SOPs`).
4. **Dual-gate worktree dreaming + zero-token `aml check`**: A 30-second pre-dream triage filters invalid runs; consolidation edits an isolated `git worktree`, runs `aml check`, and outputs a real `git diff` for human review.
5. **Physical tenant/product isolation & leak guards**: `aml search --product <p> --tenant <t>` enforces directory allowlists; `pre-push` blocks plaintext tokens and prevents pushing private instances to public remotes.

---

## Quick Start

### Mode A: Single-Product Repository (`standalone`)
```bash
python3 scripts/aml.py init /path/to/your-repo/memory --mode standalone
python3 scripts/aml.py check --repo /path/to/your-repo/memory
```

### Mode B: Multi-Host, Multi-Agent Fleet Hub (`hub`)
```bash
python3 scripts/aml.py init ~/memory-hub --mode hub --products motion-stage,edge-controller --private
cp -r scripts ~/memory-hub/
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool claude   # or codex | antigravity | gemini | kimi | generic
```

### Try the Worked Example (`examples/precision-stage-hub`)
```bash
python3 scripts/aml.py check --repo examples/precision-stage-hub
python3 scripts/aml.py start --repo examples/precision-stage-hub --host lab-bench-01 --agent demo
python3 scripts/aml.py search --repo examples/precision-stage-hub --product motion-stage --tenant site-east "验收"
python3 scripts/aml.py dream stats --repo examples/precision-stage-hub
```

## Documentation

- [`docs/architecture.md`](docs/architecture.md) — Control plane, orthogonal dual-axis matrix, 5-level priority chain & state machine
- [`docs/fleet-and-hooks.md`](docs/fleet-and-hooks.md) — Multi-machine Git sync, tool installers (`claude` / `codex` / `antigravity` / `generic`), workspace routing & `pre-push` guards
- [`docs/dreaming.md`](docs/dreaming.md) — Dual-gate offline consolidation, `inbox/` routing & L4→L1/L2/L3 cascade
- [`docs/metrics.md`](docs/metrics.md) — Zero-token `aml check` invariants, 5-arm ablation benchmark & health metrics

## License

[MIT](LICENSE)

</details>

<details name="lang" open>
<summary>🌐 <b>简体中文</b> — 点击上方 English 可原地切换语言</summary>

> 面向软硬件协同、装备与复杂研发系统的统一工程记忆架构：**跨机多工具控制面 × 正交双轴知识内核（业务四域 × 加工四阶）、多机零冲突自动同步、排故四向反哺、离线双闸门蒸馏**。

纯 Markdown + Python 3 标准库实现（零第三方依赖）。不需要服务端、数据库或向量库——一个 Git 仓库既可嵌入单个项目（`standalone`），也可作为统管你名下所有开发机、工控机、云服务器与各类 AI 客户端的全局记忆中枢（`hub`）。

## 为什么扁平 Agent 记忆与单维浓缩都不够用

1. **工具自带的扁平记忆**：绑死在单台机器或单一厂商客户端里，换电脑、换工具即失忆；且把「个人输出偏好」「本机工具链路径」与「硬件标定阈值」混堆在一起，多工具并发极易互相覆写。
2. **单维浓缩分层**（`流水 → 笔记 → Wiki → 常驻提示词`）：能应付纯文本问答，但在机器人、嵌入式/FPGA、精密装备、工业自动化、自动驾驶等工程研发中很快腐烂：
   - **第一性原理方程**与**单件传感器 `#SENS-24B-07` 的零偏漂移表**半衰期相差几个数量级；
   - **总线连接指令、`.hdf5`/`.pcapng` 数据结构、对外报告脱敏清单**属于操作技能，平时不该白占推理上下文；
   - **排故记录**在未破案时没有机理可写（只需保复现），一旦破案又必须反向修正模型假设、补齐入库标定漏项、推翻历史错误结论。

---

## 核心架构：跨机控制面 × 正交双轴产品内核

同一套协议支持 **单项目嵌入（`standalone`）** 与 **多机多产品总控（`hub`）** 两种部署形态：

### 第 0 层：跨机多工具控制面（`0_control/` + `inbox/`，Hub 模式）
- `0_control/rules.md` —— 负责人亲定的最高行为与硬件安全死红线（`<= 4 KB`）。
- `0_control/hosts/<hostname>/env.md` —— 按**物理主机**记录 OS、编译器、解释器与网口约束，同机上的 Claude Code / Codex / Antigravity 共享同一份环境事实。
- `0_control/INDEX.md` —— 全局产品线一句话进度与路由表；配合 `aml.json` 中的 `workspace_routes`，打开代码仓时自动挂载对应产品热索引，无工作区时加载全局路由表。
- `inbox/` —— 在线会话零冲突只追加暂存区（`<时间戳>-<主机>-<工具>-<简述>.md`），从根源消除多机自动同步的合并冲突。

### 产品双轴内核：业务四域 × 加工四阶

| 业务域（横轴） | 目录 | 承载内容 | 演化与审阅机制 |
|---|---|---|---|
| **① 科学机理与模型** | `1_theory/` | 物理/数学/控制定律、文献图谱、建模与仿真成立边界 | 前沿模型多 Agent 协同（一人一页）+ 人工共审 |
| **② 标定规程与资产档案** | `2_calibration/` | **SOP**：准入/定检必测清单；**Asset**：单序列号安全运行包线与实测曲线 | 人定规程；强 Checklist 多模态留证 |
| **③ 操作技能（Skill）** | `3_skills/` | 设备总线控制、源码与 CLI、二进制数据规范、报告脱敏、自动化通知 | 标准 `SKILL.md` 按需挂载（平时 `0 token`）；**凭证零明文** |
| **④ 异常与排故账本** | `4_anomalies/` | **Open**：最小可复现快照；**Resolved**：归因结论、`refuted` 负结果与四向反哺单 | 在线轻量抓复现；结案后离线反向更新 ① / ② / ③ |

| 加载阶（纵轴） | 位置 | 零 Token 机械守卫（`aml check`） |
|---|---|---|
| **④ 常驻注入阶** | `AGENTS.md` + `MEMORY.md`（及 `0_control/`） | 会话启动必载；硬卡 `MEMORY.md <= 200 行 / 25 KB`，**严禁残留任何 `stale` 条目** |
| **③ 结构导航阶** | `1_theory/` + `3_skills/` | 强制导航压缩比 `size(1_theory + MEMORY.md) / size(底层记录) <= 0.30` |
| **② 判断与基线** | `2_calibration/` + `4_anomalies/` | 强制校验 `id`、`applies_to` 边界、`evidence` 证据链与六态状态机（`verified / hypothesis / open / refuted / stale / conflict`） |
| **① 事实底座阶** | `transcripts/` | 只追加原始流水与多模态伴生索引卡（挂接工装照、界面截图与 `.hdf5`/`.pcapng`） |

---

## 五条核心工程铁律

1. **在线只追加零冲突、离线严晋升**：日常会话对已固化层严格只读，新发现一律生成唯一命名的追加文件落入 `inbox/`、`transcripts/` 或 `4_anomalies/open/`，`Stop` 钩子跨机自动提交推送永不撞车。
2. **排故四向反哺飞轮**：每张 `resolved` 结案单强制触发对 `1_theory/` 模型假设、`2_calibration/` 准入 SOP 与资产档案、`3_skills/` 操作防呆及全库历史结论的四向巡检。
3. **五级优先级裁决链**：安全与保密红线自顶向下不可突破（`1. 硬红线 > 2. 本机环境`），工程参数按特指度就近优先（`3. 客户现场口径 > 4. 单序列号实测基线 > 5. 通用机理与标准规程`）。
4. **隔离工作树双闸门蒸馏 + 机械校验**：先跑 30 秒前置轻筛剔除废实验，再在隔离 `git worktree` 中编辑并通过 `aml check` 校验，导出真实 `git diff` 交由人工审阅合入（告别手写 `.patch` 行号损坏）。
5. **产品/租户物理防串味与防误推守卫**：`aml search --product <p> --tenant <t>` 强制目录白名单检索；`pre-push` 自动拦截明文密钥及私有实例向公开模板仓的误推送。

---

## 快速开始

### 形态 A：嵌入单个项目仓库（`standalone`）
```bash
python3 scripts/aml.py init /path/to/your-repo/memory --mode standalone
python3 scripts/aml.py check --repo /path/to/your-repo/memory
```

### 形态 B：搭建多机多工具全局记忆中枢（`hub`）
```bash
python3 scripts/aml.py init ~/memory-hub --mode hub --products motion-stage,edge-controller --private
cp -r scripts ~/memory-hub/
# 一键注册客户端启动指令与自动同步钩子（支持 claude | codex | antigravity | gemini | kimi | generic）
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool claude
```
> Windows 环境可直接运行 `scripts\aml.cmd ...`，工具会自动锁定真实可用的 `py -3` 解释器并避开系统商店占位存根。

### 直接试跑完整闭环示例（`examples/precision-stage-hub`）
```bash
python3 scripts/aml.py check --repo examples/precision-stage-hub
python3 scripts/aml.py start --repo examples/precision-stage-hub --host lab-bench-01 --agent demo
python3 scripts/aml.py search --repo examples/precision-stage-hub --product motion-stage --tenant site-east "验收"
python3 scripts/aml.py dream stats --repo examples/precision-stage-hub
```

---

## 目录与文档导航

```text
docs/
  architecture.md             控制面 × 正交双轴架构、五级优先级链、状态机与多模态伴生卡
  fleet-and-hooks.md          多机多工具无服务端同步、客户端安装器、工作区自动路由与防泄密钩子
  dreaming.md                 离线双闸门蒸馏、inbox 分拣与 L4→L1/L2/L3 四向连锁反哺
  metrics.md                  零 Token 机械守卫（aml check）、五组消融评测与健康度指标
scripts/
  aml.py                      零依赖跨平台核心 CLI（init/install/start/capture/sync/search/dream/check）
  aml / aml.cmd               POSIX 与 Windows 命令行入口封装
  git-hooks/pre-push          防机密泄露与防私有库误推公开远端钩子
templates/
  hub/                        多机多产品总控层模板（0_control/ + inbox/ + aml.json）
  product/                    通用产品双轴记忆模板（1_theory .. 4_anomalies + transcripts + tenants + eval）
  dreaming/                   两阶段离线蒸馏提示词（triage + consolidate）
examples/
  precision-stage-hub/        精密闭环运动控制与供电纹波混叠端到端闭环示例
```

## 许可

[MIT](LICENSE)

</details>
