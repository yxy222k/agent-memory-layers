# 事实底座（Transcripts & Multimodal Sidecars）

原始事实层：实验室标定与测试伴生卡、现场排故流水、关键仿真对比记录。**只追加，不改写。**

本层是离线蒸馏核验「某条经验或模型假设是否成立」的唯一客观真值。文档记录设计意图，原始记录保存事实；一旦事后润色篡改原始记录，纠错就会退化为循环论证。

## 命名与分区约定
- 公共 / 研发台架记录：`transcripts/YYYYMMDD-<host-or-scene>-<slug>.md`（可通过 `aml capture --kind transcript` 自动生成）
- 特定客户现场记录：存入 `tenants/<代号>/transcripts/`（由 `aml search --tenant <代号>` 提供目录白名单物理隔离）

## 大体积二进制与多模态证据挂接
现场工装照片、监控界面截图、`.hdf5` / `.parquet` / `.mcap` 原始波形、`.pcapng` 抓包文件存入外部存储 / NAS / Git LFS，并在本目录落盘对应的轻量 **伴生索引卡（`_SIDECAR_TEMPLATE.md`）**。

## 历史记录迁入原则
从旧知识库或历史会话导入记录时**原样保留原文**并标注导入日期；历史记录中的错误判断与更正轨迹是宝贵的排故反例，不作美化删改。
