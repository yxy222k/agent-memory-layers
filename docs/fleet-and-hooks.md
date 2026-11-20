# 跨机多工具协同与生命周期钩子（Fleet & Hooks）

当你同时在台式工作站、实验室工控机、笔记本和远程服务器上使用多种 AI 编程/工程助手（Claude Code、Codex、Antigravity、Gemini CLI、Kimi Code 或任意支持 Markdown 指令的客户端）时，`scripts/aml.py` 无需部署任何服务端进程，仅靠 **纯 Git + Python 3 标准库** 即可让所有客户端共享同一个私有记忆中枢。

---

## 一、 为什么在线自动同步不会引发多机 Git 冲突

传统共享笔记方案一旦开启多机自动 `pull / commit / push`，两个会话同时改同一份 `MEMORY.md` 就会触发合并冲突。

`agent-memory-layers` 从写入协议上根除了冲突源：
1. **固化层在线只读**：`0_control/`、`MEMORY.md`、`1_theory/`、`2_calibration/`、`3_skills/` 与 `4_anomalies/resolved/` 在日常任务会话中不直接覆写。
2. **捕获层唯一文件追加**：在线会话通过 `aml capture` 生成 `<YYYYMMDD-HHMMSS>-<host>-<agent>-<slug>.md` 独立文件，仅落入 `inbox/`、`transcripts/` 或 `4_anomalies/open/`。
3. **受限自动提交（`aml sync`）**：回合结束钩子（`Stop`）只暂存上述安全追加目录，自动执行机密扫描后提交推送，带随机退避与安全 `pull --rebase --autostash` 恢复；跨层合并统一留给离线 Dreaming 在隔离工作树中完成。

---

## 二、 初始化私有总控仓库（Hub 模式）

```bash
# 1. 创建私有空仓库并克隆到本地（例如 ~/memory-hub）
git clone git@<your-git-host>:<you>/memory-hub.git ~/memory-hub

# 2. 使用模板一键生成 Hub 控制面与首批产品线双轴目录（--private 开启防误推公开仓保护）
python3 scripts/aml.py init ~/memory-hub --mode hub --products motion-stage,power-module --private

# 3. 将 scripts/ 拷入私有仓以便各机器离线独立调用，首次提交推送
cp -r scripts ~/memory-hub/
git -C ~/memory-hub add .
git -C ~/memory-hub commit -m "chore: initialize private engineering memory hub"
git -C ~/memory-hub push -u origin main
```

在 `~/memory-hub/aml.json` 中配置本机代码工作区与产品线的自动映射：

```json
{
  "workspace_routes": {
    "~/repos/motion-stage-fw": "motion-stage",
    "~/repos/power-module-hw": "power-module"
  }
}
```

---

## 三、 在每台机器上接入 AI 工具（`aml install`）

`aml.py install` 会自动探测真实可用的 Python 3.9+ 解释器（在 Windows 下自动优先锁定 `py -3` 并跳过 `WindowsApps` 占位存根），将本机身份保存在仓库外的 `~/.aml/identity.json`，幂等注入 `<!-- aml:begin -->` 启动协议块，并为支持生命周期钩子的工具配置自动拉取与回合结束自动同步：

```bash
# Claude Code（写入 ~/.claude/CLAUDE.md 并配置 ~/.claude/settings.json SessionStart + Stop 钩子）
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool claude

# Codex（写入 ~/.codex/AGENTS.md 并配置 ~/.codex/hooks.json）
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool codex

# Antigravity（写入 ~/.gemini/GEMINI.md 并配置 ~/.gemini/config/hooks.json PreInvocation + Stop 钩子）
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool antigravity

# Gemini CLI / Kimi Code
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool gemini
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool kimi

# 任意支持全局 Markdown 指令文件的桌面/IDE Agent
python3 ~/memory-hub/scripts/aml.py install --repo ~/memory-hub --tool generic --target ~/.my-agent/AGENTS.md
```

Windows 终端也可直接调用纯 ASCII + CRLF 封装脚本 `scripts\aml.cmd install ...`。如需卸载，执行对应的 `aml.py uninstall --repo ~/memory-hub --tool <tool>`，仅移除注入块与钩子，不触碰任何记忆文件。

---

## 四、 工作区感知的渐进式上下文加载

每次新会话启动时，`aml start --cwd <当前工作目录>` 按最小上下文原则动态组装清单：

| 会话打开位置 | 自动注入（`READ-ON-START`） | 按需检索（`READ-ON-DEMAND`） |
|---|---|---|
| **命中 `workspace_routes`**（如 `~/repos/motion-stage-fw`） | `0_control/rules.md` + `0_control/hosts/<host>/env.md` + `products/motion-stage/{AGENTS.md,MEMORY.md}` | 该产品的 `1_theory` / `2_calibration` / `3_skills` / `4_anomalies` / `transcripts` 及 `0_control/shared_skills/` |
| **未打开工作区 / 跨项目讨论** | `0_control/rules.md` + `0_control/hosts/<host>/env.md` + `0_control/INDEX.md` | 聊到具体产品时再挂载对应 `products/<slug>/MEMORY.md` |
| **单项目嵌入模式（`standalone`）** | `AGENTS.md` + `MEMORY.md` | 本目录 `1_theory` / `2_calibration` / `3_skills` / `4_anomalies` / `transcripts` |

---

## 五、 隐私防护与静态加密建议

1. **`pre-push` 防泄密守卫**：`aml init` 与 `aml install` 会自动配置 `core.hooksPath = scripts/git-hooks`。当 `aml.json` 中 `"private_instance": true` 时，向 `blocked_public_remotes` 列表中的公开仓库推送会被立即阻断；同时每次推送前自动扫描疑似私钥、API Token 与内嵌口令 URL。
2. **可选端到端静态加密（`git-crypt`）**：若私有托管平台本身不可完全信任，可在仓库启用 `git-crypt` 加密 Markdown 正文。`aml start` 与 `aml sync` 内置了 `\x00GITCRYPT` 锁状态检测——一旦发现未解锁，立即中止自动提交，防止将明文误写入加密分支。注意文件名与 Git Commit Message 仍对托管端可见，应保持脱敏。
