---
name: automation
description: 自动化通知推送（Webhook / Issue CLI）、定时蒸馏轻筛投递及外部系统凭证的零明文调用规范。配置定时巡检、推送蒸馏摘要或调用受控 Web 系统时加载。
---

# 自动化工作流与凭证安全调用

## 1. 凭证零明文原则
- **Git 与代码托管**：统一使用 SSH Agent、`gh auth` 或系统 Git Credential Manager；严禁在仓库配置或脚本中拼接 `https://<user>:<token>@...`。
- **消息通知与工单接口**：所有 Webhook URL、API Key 统一从本机环境变量读取（如 `$NOTIFY_WEBHOOK_URL`、`$ISSUE_API_TOKEN`），实际值仅存放在本机密钥环或已被 `.gitignore` 忽略的 `.env` 中。

## 2. 离线蒸馏轻筛清单推送示例
用于将 `aml dream triage` 生成的 30 秒前置确认清单推送至团队通知渠道（Slack / Teams / Discord / 企业 IM / GitHub Issue）：
```bash
# 示例：仅发送脱敏后的文件名与异常编号摘要，禁止外发客户真名与涉密参数
# python3 scripts/aml.py dream triage --repo .
# curl -sS -X POST "$NOTIFY_WEBHOOK_URL" -H "Content-Type: application/json" \
#   -d "$(jq -Rs '{text: .}' triage-list.md)"
```

## 3. 受控 Web 界面操作边界
- 公开技术规范、器件 Datasheet 与开源文档优先通过 CLI 或静态抓取读取。
- 访问内部工单台或仪器 Web 控制台时，复用本地已认证会话，不在任何自动化脚本中硬编码账号密码。
