# 产品记忆热索引（MEMORY.md）

> **硬上限：`≤ 200 行` / `≤ 25 KB`**。只放「当前在役基线 + 安全包线告警 + 一句话路由链接」，细节留在下层目录。
> 日常会话只读；增删与升降级统一由离线蒸馏（Dreaming）在隔离工作树生成 `git diff` 并经 `aml check` 校验后合入。

## 0. 当前在役基线与硬件安全包线
- 当前软件 / 固件主版本：`v____`（跨版本口径差异表 → `1_theory/version-matrix.md`）
- 在役核心资产与**硬保护边界**：
  - 传感 / 采集单元 `#SENS-____`（零偏基线 / 线性上限 / **瞬时过载硬极限**） → `2_calibration/assets/____.md`
  - 执行 / 驱动单元 `#ACT-____`（额定区间 / 热降额门限 / 禁区告警） → `2_calibration/assets/____.md`

## 1. 科学机理与仿真模型（`1_theory/`）
- 系统机理图谱总入口与建模假设边界 → `1_theory/index.md`
- （高频控制方程 / 误差传递模型一句话索引） → `1_theory/____.md`

## 2. 标定规程与测试核查单（`2_calibration/`）
- 核心传感器 / 采集模块入库标定必检规程 → `2_calibration/sops/____.md`
- 执行机构 / 整机闭环定期复核与留证规程 → `2_calibration/sops/____.md`

## 3. 操作技能按需入口（`3_skills/`，需要时再读）
- 设备与总线连接（UART / CAN / Ethernet / SSH / 安全断连） → `3_skills/device-connect/SKILL.md`
- 源码映射、CLI 批处理与商业软件开源平替 → `3_skills/software-cli/SKILL.md`
- 数据存储规范（`hdf5` / `parquet` / `pcapng` / `csv` / `json`） → `3_skills/data-schema/SKILL.md`
- 技术报告撰写与对外脱敏自检单 → `3_skills/reporting/SKILL.md`
- 自动化通知与凭证安全调用 → `3_skills/automation/SKILL.md`

## 4. 高频排故陷阱、已证伪路径与待破案异常（`4_anomalies/`）
- 【高频陷阱】（表面症状 → 先查哪个物理/硬件环节，别先改什么参数） → `4_anomalies/resolved/____.md`
- 【已证伪负结果】（某方案已实测不通或引入副作用，避免重复投入） → `4_anomalies/resolved/____.md`
- 【待破案异常】（当前悬而未决、具备最小复现包的现场列表） → `4_anomalies/open/`

## 5. 客户 / 现场隔离分区（`tenants/`）
- 各交付现场特殊约束、网络条件与验收口径映射 → `tenants/<代号>/AGENTS.md`

## 6. 原始事实底座（`transcripts/`）
- 实验原始流水、现场工单与多模态伴生索引卡（只追加不改写） → `transcripts/README.md`
