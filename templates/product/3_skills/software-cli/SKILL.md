---
name: software-cli
description: 核心控制/解算源码映射、可复现批处理 CLI 参数规范，以及大型商业闭源软件的脚本化开源替代方案。需要查源码、跑离线重放或构建自动化流水线时加载。
---

# 软件源码、CLI 规范与开源平替

## 1. 核心代码仓库与模块入口
| 模块 | 仓库路径 / 分支约定 | 核心入口文件 | 本地构建与回归自检命令 |
|---|---|---|---|
| 实时采集与控制服务 | `____` | `____` | `____` |
| 核心解算 / 估计算法库 | `____` | `____` | `____` |
| 上位机监控客户端 | `____` | `____` | `____` |

## 2. 离线可复现 CLI 调用铁律
```bash
# 铁律：离线重放或回归测试必须显式传入算法版本与对应硬件资产标定文件，严禁依赖隐式全局默认补偿表
# <replay-cli> --input <capture.hdf5> --calib <asset-id.json> --config-ver <vX.Y.Z> --out <metrics.json>
```

## 3. 商业闭源软件 → 可版本控制开源工具链映射
> 原则：单次交互建模可用商业 GUI；批量参数扫描、CI 回归与离线蒸馏复核一律采用可脚本化的开源方案。

| 工程场景 | 商业闭源工具（痛点：License 受限 / GUI 难自动化） | 脚本化开源替代方案 | 对标精度验证记录 |
|---|---|---|---|
| 多物理场 / 有限元 / 控制系统仿真 | COMSOL / ANSYS / Simulink | `FEniCSx` / `python-control` / `CasADi` | `transcripts/____.md` |
| 总线与工业以太网时序抓包分析 | 厂商专用协议分析仪 GUI | `tshark` / `scapy` / `python-can` 解析 `.pcapng` | `transcripts/____.md` |
| 大规模实验数据批处理与工程出图 | Origin / MATLAB | Python (`numpy` / `scipy` / `h5py` / `polars` / `matplotlib`) | `transcripts/____.md` |
