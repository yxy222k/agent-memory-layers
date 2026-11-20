# 记忆总索引（MEMORY.md）

> **硬上限：≤ 200 行 / 25 KB**。只放「当前状态快照 + 硬保护告警 + 一句话路由链接」，正文留在下层目录。
> 日常会话只读；增删与升降级统一由离线蒸馏（Dreaming）产出 Diff 经人工确认后合入。

## 0. 当前在役基线与硬保护告警
- 当前软件主版本：`v____`（跨版本差异总表 → `1_theory/version-matrix.md`）
- 在役核心器件基线与**过载红线**：
  - 光源 `#SLD-____`（额定/极限电流与波长漂移基线） → `2_calibration/assets/____.md`
  - 光谱仪 `#SPEC-____`（暗谱 counts / **饱和阈值** / **瞬时过载阈值**） → `2_calibration/assets/____.md`

## 1. 科学机理与仿真模型（`1_theory/`）
- 机理知识图谱总入口与模型假设边界 → `1_theory/index.md`
- （高频机理一句话索引） → `1_theory/____.md`

## 2. 标定规程与样品测量（`2_calibration/`）
- 新光源入库标定必检项（高低电流中心波长漂移等） → `2_calibration/sops/____.md`
- 光谱仪入库与定期复核规程（暗谱/饱和/过载/积分档位） → `2_calibration/sops/____.md`
- 样品测量留证规范（光路照片 + 上位机截图 + 数据伴生卡） → `2_calibration/sops/____.md`

## 3. 操作技能按需入口（`3_skills/`，需要时再读）
- 设备连接（OS / 协议 / 串口指令） → `3_skills/device-connect/SKILL.md`
- 软件与 CLI（源码位置 / 参数 / 闭源软件开源平替） → `3_skills/software-cli/SKILL.md`
- 数据存储（`csv` / `hdf5` / `pcap` / `json` 选型与模板） → `3_skills/data-schema/SKILL.md`
- 报告撰写（PPT 模板 / 精简文风 / 核心技术脱敏清单） → `3_skills/reporting/SKILL.md`
- 自动化办公（`lark cli` / 浏览器 / 环境变量凭证调用） → `3_skills/automation/SKILL.md`

## 4. 高频排故陷阱与悬而未决异常（`4_anomalies/`）
- 【高频陷阱】（症状表现 → 先查什么，别先动什么） → `4_anomalies/resolved/____.md`
- 【已证伪负结果】（某方案已试过不通，勿重复投入） → `4_anomalies/resolved/____.md`
- 【待破案异常】（当前悬而未决、可随时复现的现场列表） → `4_anomalies/open/`

## 5. 客户 / 项目现场分区（`tenants/`）
- 各现场特殊约束与术语口径映射 → `tenants/<代号>/AGENTS.md`

## 6. 原始事实底座（`transcripts/`）
- 实验原始流水、工单与多模态伴生索引卡（只追加不改写） → `transcripts/README.md`
