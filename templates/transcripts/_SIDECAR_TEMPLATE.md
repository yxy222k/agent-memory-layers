---
id: tr-YYYYMMDD-001
date: "YYYY-MM-DD"
source: lab                       # lab | field | ticket | sim
valid_run: true                   # 若确认属未接好光纤/忘开光源等废操作，蒸馏前轻筛改标 false（不删文件）
software_version: ""
asset_sns: []                     # 例：[SLD-1310-03, SPEC-01, PROBE-A2]
referenced_ids: []                # 本次工作引用过的记忆条目 ID（供脚本统计真实使用频次）
---

# 原始记录 / 实验伴生卡：（简短客观标题）

## 1. 多模态与原始数据指针
- **测量装置现场照片**：`<NAS或LFS路径>/YYYYMMDD_setup.jpg`
  - 画面关键事实速记：（例：1310nm SLD 经环形器接探头 A2，法兰已扭力扳手锁紧，光纤弯曲半径 >30mm）
- **上位机软件截图**：`<NAS或LFS路径>/YYYYMMDD_gui.png`
  - 界面关键读数速记：（例：软件 v3.4.2，积分时间 500us，峰值 48200 counts 未饱和，开启默认温度补偿表）
- **原始数据包**：`<NAS或LFS路径>/YYYYMMDD_raw.hdf5`（SHA256 前8位：`____`）

## 2. 实验过程与原始观测流水（不做主观修饰）
（按时间顺序记录操作参数、现象与原始数值，原样保留异常波动与失败尝试）
