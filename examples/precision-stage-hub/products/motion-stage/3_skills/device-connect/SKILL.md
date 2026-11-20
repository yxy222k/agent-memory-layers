---
name: device-connect
description: 连接运动台实时主控与传感采集板（SSH / SCPI / 串口指令与安全去使能步骤）。连硬件或改供电/伺服参数时加载。
---

# 运动台设备连接与指令规范

## 1. 接口环境变量（具体地址在本地 `.env`）
- 实时运动控制器：`ssh rtuser@"$STAGE_CTRL_HOST"`（千兆控制网口禁用 EEE）
- 电源管理 MCU 串口：`$PMU_SERIAL_PORT` (`115200, 8N1, \r\n`)

## 2. 关键电源与伺服安全指令
- 查询模拟轨供电模式：`PMU:RAIL:ANALOG:MODE?`（精密闭环运行必须返回 `LDO_LOCKED`，严禁为 `DCDC_ECO_PFM`）
- 闭环异常紧急去使能：`SERVO:DISABLE ALL`（观测到电流逼近 `5.5 A` 或持续异响时立即下发）
