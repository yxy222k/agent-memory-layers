---
name: data-schema
description: 实验、台架与现场数据的存储格式选型硬规范（hdf5 / parquet / mcap / pcapng / csv / json）、元数据必填项与伴生索引卡约定。保存数据、写采集/解析脚本时必载。
---

# 数据存储格式选型与元数据规范

## 1. 格式选型硬规则（禁止混用）
| 数据形态 | 强制格式 | 原因与禁止事项 |
|---|---|---|
| 高采样率原始波形 / 多通道同步时序 / 多维张量 | **`.hdf5` / `.parquet` / `.mcap`** | 自带类型精度、无损压缩与层级元数据；**严禁存 `.csv`**（体积膨胀 5–10×、十进制文本截断丢失微弱相位/残差精度、易丢失采样率与硬件头信息） |
| 标定汇总表 / 小规模统计结果（`< 10,000` 行） | **`.csv`** | 便于速览；首行必须使用固定英文蛇形列名并带物理单位后缀（如 `position_err_um`、`supply_ripple_mv`） |
| 工业以太网 / 串口 / CAN 总线底层通信排故 | **`.pcapng` / `.blf`** | 保留微秒级硬件时间戳与原始帧字节，支撑协议层确定性重放 |
| 单次运行配置快照 / 资产标定参数表 | **`.json`** | 机器可读；顶层必含 `schema_version`、`software_version` 与 `asset_ids` |

## 2. 标准归档命名与根级必填元数据
文件命名：`YYYYMMDD_<scene>_<test-or-ticket>_<primary-asset-id>.<ext>`

二进制数据包根级 Attributes 必填项：
- `captured_at` (ISO-8601 含时区)
- `software_version`
- `asset_ids` (参与本次运行的传感器、执行器、主控唯一编号列表)
- `sample_rate_hz` 及关键激励/增益档位参数

## 3. 伴生索引卡（Sidecar）联动
任何大体积二进制文件落盘到 NAS / 对象存储 / Git LFS 后，必须在 `transcripts/` 同步生成一份轻量 `.md` 伴生索引卡（见 `transcripts/_SIDECAR_TEMPLATE.md`），否则文本检索与离线蒸馏无法索引该批实测证据。
