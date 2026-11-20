# 主机环境约束：`lab-bench-01`

- OS：Ubuntu 24.04 LTS (`PREEMPT_RT` 实时内核 `6.8-rt`)
- Python 入口：`python3` (`3.12`)
- 实时控制网口：`enp3s0` 固定千兆全双工，已通过 `ethtool --set-eee enp3s0 eee off` 关闭节能以太网
- 原始波形归档盘：`/mnt/lab_nas/motion_stage/`
