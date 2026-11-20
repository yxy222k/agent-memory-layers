# 在线零冲突捕获暂存区（Global Inbox）

当多台机器、多个 Agent 会话并发工作时，若遇到以下情况：
1. 当前未打开具体产品工作区，或经验横跨多个产品 / 涉及主机环境配置；
2. 激战排故中来不及判断该归入哪个产品子目录；

统一使用 `aml capture --kind inbox --title "..."`（或按 `YYYYMMDD-HHMMSS-<host>-<agent>-<slug>.md` 规则新建文件）落入本目录。

- **为什么零冲突**：在线会话永远只新建唯一命名的独立文件，不并发编辑共享索引，`Stop` 钩子自动 `commit + push` 不会产生合并冲突。
- **何时清空**：每次离线蒸馏（Dreaming）将已确认有效的条目分拣归入 `0_control/hosts/` 或对应 `products/<slug>/` 各层后，在隔离工作树中清理已归档文件。
