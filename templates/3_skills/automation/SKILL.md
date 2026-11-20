---
name: automation
description: 自动化办公工作流（lark cli 消息/文档推送、AI 友好浏览器操作约定、Git 与外部系统凭证的安全调用方式）。执行定时通知、蒸馏推送或自动化巡检时加载。
---

# 自动化办公与凭证安全规范

## 1. 凭证安全调用（严禁明文入库）
- **Git 仓库操作**：统一走本机 SSH Agent 或 `gh auth` / Git Credential Helper，禁止在远程 URL 中拼接 `https://<token>@github.com/...`。
- **Lark / 飞书与内部 API**：从环境变量读取（如 `$LARK_WEBHOOK_URL`、`$LARK_APP_ID`），配置保存在本机 `~/.zshrc` 或工作区 `.env`（已入 `.gitignore`）。

## 2. Lark CLI 常用推送约定
用于发送「离线蒸馏前 30 秒轻筛清单」与「排故结案提醒」：
```bash
# 示例：推送待确认的夜间蒸馏摘要（脱敏后发送，不含客户真名与核心配方）
# lark-cli message send --webhook "$LARK_WEBHOOK_URL" --file triage-list.md
```

## 3. 浏览器自动化约定
- 查公开文献、器件 Datasheet、开源文档优先用命令行检索或静态抓取。
- 涉及需要登录态的内部工单系统或仪器 Web 控制台时，复用已认证浏览器会话，不在脚本中硬编码账号密码。
