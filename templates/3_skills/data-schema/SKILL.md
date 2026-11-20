---
name: data-schema
description: 实验与现场数据的存储格式选型规范（csv / hdf5 / pcap / json）、标准字段模板与文件命名约定。保存测量数据、写解析脚本或归档实验时加载。
---

# 数据存储选型与字段模板

## 1. 格式选型硬规则（禁止混用）
| 数据形态 | 强制格式 | 为什么（禁止事项） |
|---|---|---|
| 高频原始光谱 / 干涉波形 / 多维扫描矩阵 | **`.hdf5` (`.h5`)** | 自带层级元数据与无损压缩；**严禁存 `.csv`**（体积膨胀 10×、浮点截断丢相位精度、易丢采样率头信息） |
| 标定汇总表 / 小规模单点统计结果（<1万行） | **`.csv`** | 方便人眼与表格工具速览；首行必须固定英文蛇形列名并带单位后缀（如 `wavelength_nm`） |
| 工业相机/光谱仪底层网口或总线通信排查 | **`.pcap` / `.pcapng`** | 保留微秒级硬件时间戳与分包原始字节，供排故复现 |
| 单次实验环境配置 / 器件标定参数快照 | **`.json`** | 结构化机器可读，必须包含 `schema_version`、`software_version` 与 `asset_sns` |

## 2. 标准归档命名与必带元数据
文件命名：`YYYYMMDD_<scene>_<sample-or-ticket>_<primary-asset-sn>.<ext>`

`.hdf5` 根节点 Attributes 必填项：
- `captured_at` (ISO-8601)
- `software_version`
- `light_source_sn` / `spectrometer_sn` / `probe_sn`
- `integration_time_us` / `drive_current_ma`

## 3. 伴生索引卡联动
任何大体积 `.hdf5` / `.pcap` 落盘后，必须在 `transcripts/` 生成对应的轻量 `.md` 伴生索引卡（见 `transcripts/_SIDECAR_TEMPLATE.md`），否则记忆库无法检索该批数据。
