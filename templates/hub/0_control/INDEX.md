# 全局产品线路由索引（Global Product Index）

> **加载时机**：当会话未打开特定项目工作区（或未命中 `aml.json` 中的 `workspace_routes`）时常驻挂载。
> **容量硬上限**：`≤ 4 KB`。每个产品仅保留「当前目标 + 在役版本/状态一句话 + 路径入口」，严禁在此堆放标定数值或排故细节。

| 产品代号 (`slug`) | 代码仓库路径 | 当前主版本与阶段目标 | 下一步关键验证 | 记忆入口 |
|---|---|---|---|---|
| `product-alpha` | `~/repos/product-alpha` | `v1.0.0` — 原型台架闭环联调 | 完成核心传感器入库标定基线 | `products/product-alpha/MEMORY.md` |
