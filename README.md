# agent-memory-layers

<details name="lang">
<summary>🌐 <b>English</b> — Click to switch language in-place</summary>

> Long-term engineering memory for hardware-software & precision instrumentation product lines: **4 Domain Areas × 4 Processing Stages, troubleshooting-driven evolution, and dual-gate offline dreaming**.

A plain-Markdown + Shell memory kit. No server, no database, no vector store — one Git repository is enough.

## Why Two Orthogonal Axes

Splitting memory purely by compression level (`transcripts → notes → wiki → injected context`, as in Anthropic's *The components of agent memory*) works well for pure-text tasks, but breaks down in real hardware/optics/instrumentation R&D:

- **First-principles physics equations** and **one specific spectrometer's dark counts** differ in half-life by orders of magnitude.
- **Serial port commands, `.hdf5` schemas, and slide redaction rules** are procedural skills — they should cost `0 tokens` until the moment you connect hardware, save data, or export a report.
- **Troubleshooting records** have no known mechanism while open (they only need reproducibility), yet once resolved they must cascade backward to revise simulation assumptions, add missing calibration checks, and invalidate stale conclusions.

v2 combines **4 Engineering Domains (horizontal)** with **4 Processing Stages (vertical)**:

### Horizontal: 4 Engineering Domains

| Domain | Directory | Holds | Authored & Reviewed By |
|---|---|---|---|
| **① Theory & Models** | `1_theory/` | Physics/math laws, literature maps, simulation assumptions & bounds | Frontier multi-agent exploration (one file per agent) + human review |
| **② Calibration & Assets** | `2_calibration/` | **SOPs**: intake/measurement checklists; **Assets**: per-SN baselines (drift tables, dark counts, overload thresholds) | Human SOPs; execution models follow strict checklists with photo/screenshot evidence |
| **③ Procedural Skills** | `3_skills/` | Device serial/IP setup, CLI/repos, data schemas (`csv/hdf5/pcap/json`), report redaction, office automation | On-demand `SKILL.md` modules; **zero plaintext credentials** |
| **④ Anomalies & Root Cause** | `4_anomalies/` | **Open**: reproducible anomaly snapshots; **Resolved**: root causes, negative results (`refuted`), cascade checklists | Lightweight capture in-session; resolved items trigger offline updates to ① / ② / ③ |

### Vertical: 4 Processing & Loading Stages

| Stage | Location | Hard Constraint |
|---|---|---|
| **④ Injected** | `AGENTS.md` + `MEMORY.md` | Loaded every session; **capped at ≤200 lines / 25KB** (software version, active hardware SNs, safety/redaction red lines, routing index) |
| **③ Navigation** | `1_theory/` + `3_skills/` | Cross-document synthesis wiki & on-demand skills; `1_theory/` must stay smaller than underlying records |
| **② Judgments & Baselines** | `2_calibration/` + `4_anomalies/` | Always carries evidence & `applies_to` bounds; separates `verified` / `hypothesis` / `refuted` / `stale` |
| **① Ground-Truth Facts** | `transcripts/` | Append-only logs & multimodal sidecars pointing to setup photos, GUI screenshots, and `.hdf5`/`.pcap` files |

---

## Four Core Engineering Rules

1. **Low-friction capture, strict promotion**: Open anomalies only require a minimal reproducible snapshot (never force premature mechanism guessing in-session); promoting to `verified` requires mechanism, version/SN bounds, and counterexamples.
2. **Troubleshooting drives cross-layer evolution**: Every `resolved` anomaly triggers a four-way offline audit across `1_theory/`, `2_calibration/`, `3_skills/`, and historical conclusions.
3. **Dual-confirmation offline dreaming**: A 30-second **pre-dream triage** filters out botched lab runs first; consolidation then edits an isolated `git worktree` and emits a real `git diff` for human review (avoiding brittle LLM-generated `.patch` line numbers).
4. **Physical tenant isolation & zero secrets**: Scoped search via `scripts/search.sh --tenant <code_name>`; credentials and internal IPs are referenced strictly via environment variables.

---

## Quick Start

```bash
cp -r templates/* <your-product-repo>/memory/
cp -r scripts <your-product-repo>/memory/scripts
```

See [`examples/interferometry-mini/`](examples/interferometry-mini/README.md) for a complete worked example (1310nm SLD low-current wavelength drift causing interferometric phase jumps, and how its resolution cascades across all layers).

## Docs

- [`docs/architecture.md`](docs/architecture.md) — Dual-axis architecture, two-stage write gates, state machine, and multimodal/security boundaries
- [`docs/dreaming.md`](docs/dreaming.md) — Dual-gate offline consolidation, L4→L1/L2/L3 cascade, and version sweeps
- [`docs/metrics.md`](docs/metrics.md) — 5-arm ablation evaluation and R&D / field-service health metrics

## License

MIT.

</details>

<details name="lang" open>
<summary>🌐 <b>简体中文</b> — 点击上方 English 可原地切换语言</summary>

> 面向软硬件结合 / 光电与精密测量研发产品线的长期记忆骨架：**业务四域 × 加工四阶、排故驱动演化、离线双闸门蒸馏**。

一个纯 Markdown + Shell 的工程记忆模板。不依赖服务端、数据库或向量库，一个 Git 仓库就够。

## 为什么需要双轴结构

随手攒的研发知识库，三个月后就没人翻了。单按信息浓缩度切分（`流水 → 笔记 → Wiki → 常驻提示词`）能解决纯软件场景的检索膨胀，但装不进真实的硬科技项目：

- **物理定律**和**某台光谱仪的暗谱 counts**半衰期差了几个数量级；
- **串口指令、`hdf5` 格式、对外 PPT 脱敏规范**是操作技能，平时不该占推理上下文；
- **排故记录**在破案前没有机理可写（只能保复现），破案后又必须反向推翻旧记忆、补齐漏掉的标定项。

因此 v2 采用**正交双轴矩阵**：

### 横轴：四个工程业务域（存什么、怎么演化）

| 域 | 目录 | 承载内容 | 生产与审阅机制 |
|---|---|---|---|
| **① 科学机理与模型** | `1_theory/` | 物理/数学定律、文献图谱、建模与仿真边界 | 最前沿大模型多 Agent 协同（一人一页）+ 人工共审 |
| **② 标定规程与器件档案** | `2_calibration/` | **SOP**：标定/验证/测量必检清单；**Asset**：单器件 SN 实测基线（漂移表、暗谱、过载阈值） | 人定规程；执行模型按强 Checklist 核查留证（含照片/截图） |
| **③ 操作技能（Skill）** | `3_skills/` | 连设备/串口、源码与 CLI、数据格式（`csv/hdf5/pcap/json`）、报告脱敏、自动化办公 | 标准 `SKILL.md` 按需挂载，平时 `0 token`；**凭证零明文入库** |
| **④ 异常与排故账本** | `4_anomalies/` | **Open**：随时可复现的待破案快照；**Resolved**：归因结论、负结果（`refuted`）与跨层反哺单 | 在线轻量抓复现；结案后由离线蒸馏反向更新 ① / ② / ③ |

### 纵轴：四个加工加载阶（控成本、防污染）

| 阶 | 位置 | 硬约束 |
|---|---|---|
| **④ 常驻注入** | `AGENTS.md` + `MEMORY.md` | 每次会话必载，**硬上限 ≤200 行 / 25KB**（当前软件版本 + 在役硬件 SN + 过载/保密红线 + 路由索引） |
| **③ 结构导航** | `1_theory/` + `3_skills/` | 跨文档综合图谱与按需挂载技能；`1_theory/` 总字数必须小于底层材料 |
| **② 判断与基线** | `2_calibration/` + `4_anomalies/` | 强制带证据与适用版本/硬件区间；区分 `verified` / `hypothesis` / `refuted`（负结果） / `stale`（过期） |
| **① 事实底座** | `transcripts/` | 原始记录与多模态伴生索引卡（指向光路照/截图/`hdf5`/`pcap`）；**只追加、不改写** |

---

## 四条核心工程规则

1. **宽进严升**：在线排故遇到未解异常，只保「可复现最小包」（不逼模型脑补物理机制）；升格 `verified` 或结案时，才强制要求机制解释、版本区间与反例边界。
2. **排故反哺前三层**：每条 `resolved` 排故单都是一次跨层巡检触发器——修正 `1_theory/` 理想化假设、补齐 `2_calibration/sops/` 漏检项、修补 `3_skills/` 防呆说明、推翻历史错误结论。
3. **离线双确认蒸馏（Cronjob）**：先跑 **30 秒蒸馏前轻筛**（剔除忘拧法兰等废实验），再在隔离 `git worktree` 中编辑并导出真实 `git diff` 交给人审阅合并（告别手搓 `.patch` 行号损坏）。
4. **物理防串味与凭证硬隔离**：多客户现场用 `scripts/search.sh --tenant <代号>` 限定检索路径；密码、Token 与敏感内网 IP 一律走环境变量引用，绝不入库。

---

## 快速开始

```bash
cp -r templates/* <your-product-repo>/memory/
cp -r scripts <your-product-repo>/memory/scripts
```

1. 填 `memory/AGENTS.md` 与 `memory/MEMORY.md`：写入**当前软件版本**、**在役核心硬件 SN** 与**探测器过载/对外脱敏红线**。
2. 在 `2_calibration/` 填入首批核心器件档案（暗谱、饱和与瞬时过载阈值、波长漂移表）与标定 SOP。
3. 查看完整闭环示范：[`examples/interferometry-mini/`](examples/interferometry-mini/README.md)（1310nm SLD 低电流中心波长漂移引发干涉跳点的全链路推演）。
4. 配置定时任务运行 `./scripts/dream-worktree.sh start`，配合 `templates/dreaming/` 下的两阶段提示词产出变更 Diff。

---

## 目录说明

```text
docs/
  architecture.md             双轴方法论、两阶段写入门槛、状态机与安全边界
  dreaming.md                 离线蒸馏：双确认闸门、L4→L1/L2/L3 连锁反哺、版本扫描
  metrics.md                  五组消融对照评测与研发/交付监控指标
scripts/
  search.sh                   带 --tenant 目录白名单隔离的检索封装
  dream-worktree.sh           隔离 git worktree 蒸馏 + 真实引用频次统计 + git diff 导出
templates/                    可直接复制到项目仓库 memory/ 的完整模板树
examples/
  interferometry-mini/        1310nm 干涉测量台架端到端闭环示例
```

## 和个人 Agent 记忆库（如 `agent-memory-nest`）的关系

个人工作台管「**Agent 怎么配合你日常办公**」；本仓库管「**某条产品线/实验台知道什么**」。两者不要混装：产品仓库放本套记忆库，个人库只留一句状态快照与路径指路。

## 许可

MIT。

</details>
