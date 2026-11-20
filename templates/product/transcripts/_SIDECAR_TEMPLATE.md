---
id: tr-YYYYMMDD-001
date: "YYYY-MM-DD"
source: lab                       # lab | field | ticket | sim
valid_run: true                   # 若确认属接线未锁紧/未预热等无效操作，蒸馏前轻筛改标 false（保留文件不删）
software_version: ""
asset_ids: []                     # 例：["SENS-24B-07", "STAGE-X02"]
referenced_ids: []                # 本次任务实际参考过的记忆条目 ID（供 aml dream 统计真实引用频次）
---

# 原始记录伴生卡：（简短客观标题）

## 1. 多模态与原始数据包指针
- **物理工装现场照片**：`<NAS或LFS路径>/YYYYMMDD_setup.jpg`
  - 画面关键事实速记：（例：传感器 `#SENS-24B-07` 刚性装夹于花岗岩基座，屏蔽层单端接地，航空插头已锁紧）
- **控制 / 监控界面截图**：`<NAS或LFS路径>/YYYYMMDD_telemetry.png`
  - 界面关键读数速记：（例：固件 `v2.3.1`，采样率 `10 kHz`，稳态残差 RMS `____`）
- **原始二进制数据包**：`<NAS或LFS路径>/YYYYMMDD_raw.hdf5`（SHA256 前 8 位：`____`）

## 2. 按时间顺序的原始观测流水（不做主观润色）
- `HH:MM`：（记录工况参数、观测数值、异常跳变与尝试动作）
