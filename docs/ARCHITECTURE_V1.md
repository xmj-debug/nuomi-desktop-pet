# AI 桌宠架构设计 V1.0

## 技术路线

当前原型采用 PowerShell + WPF，原因是当前机器没有 .NET SDK，Node 也无法正常执行。这个方案可以直接运行在 Windows 上，适合验证悬浮桌宠、设置、自启动、便签和番茄钟。

正式版建议迁移到 C# WPF 或 Tauri + React：

- C# WPF：优先推荐，最适合 Windows 悬浮窗、全局快捷键、系统监控、进程检测和开机启动。
- Tauri + React：适合更漂亮的 UI 和跨平台，但 OCR、全局快捷键、窗口穿透等能力需要 Rust 侧封装。
- Electron + React：开发快，但资源占用更高，不适合作为长期常驻桌宠的首选。

## 模块划分

### Pet Shell

负责桌宠主窗口：

- 透明悬浮窗
- 始终置顶
- 拖拽移动
- 动画状态
- 鼠标交互
- 快捷菜单

### Settings

负责用户配置：

- 外观设置
- 自启动设置
- 快捷键设置
- AI 服务配置
- 数据路径配置

### AI Service

负责统一封装 AI 调用：

- OpenAI-compatible API
- OpenRouter
- Gemini
- DeepSeek

建议内部统一为：

```text
ChatRequest -> ProviderAdapter -> ChatResponse
```

这样 UI 不需要关心具体服务商。

### OCR Service

负责截图和文字识别：

- 区域截图
- OCR 识别
- 识别结果编辑
- 一键发送给 AI 分析

PowerShell 原型阶段可先做截图入口和占位，正式版接 PaddleOCR 或 Tesseract。

### Study Service

负责学习记录：

- 番茄钟
- 学习时长
- 休息时长
- 科目统计
- 连续学习天数

### Todo Service

负责待办事项：

- 新增
- 编辑
- 删除
- 完成
- 按科目或标签归类

### System Monitor

负责系统状态：

- CPU
- 内存
- 网络上下行
- VPN 进程和连接状态
- Codex 状态

### Anti Distraction

负责摸鱼检测：

- 检测指定进程
- 检测浏览器标题或域名
- 触发桌宠提醒
- 记录摸鱼事件

## 数据设计

正式版建议使用 SQLite。

核心表：

```sql
settings(key text primary key, value text not null);
chat_sessions(id text primary key, title text, created_at text, updated_at text);
chat_messages(id text primary key, session_id text, role text, content text, created_at text);
todos(id text primary key, title text, subject text, done integer, created_at text, updated_at text);
study_logs(id text primary key, subject text, kind text, minutes integer, started_at text, ended_at text);
achievements(id text primary key, code text, title text, unlocked_at text);
events(id text primary key, type text, payload text, created_at text);
```

原型阶段使用 JSON 和 TXT 文件即可：

- `pet-config.json`
- `pet-notes.txt`
- `pet-history.json`
- `pet-todos.json`
- `pet-study.json`

## 快捷键

默认：

- AI 窗口：`Alt + Space`
- OCR 截图：`Ctrl + Shift + A`
- 隐藏桌宠：后续可配置

正式版应支持冲突检测，避免覆盖系统或其他软件快捷键。

## V1 开发顺序

1. 桌宠壳：悬浮、拖拽、置顶、自启动、设置。
2. 学习工具：番茄钟、便签、待办、学习统计。
3. 系统监控：CPU、内存、网络、VPN、Codex 状态。
4. AI 助手：AI 窗口、配置、历史记录、搜索和删除。
5. OCR：截图、识别、AI 分析。
6. 娱乐互动：摸鱼检测、成就系统、动作状态。

## 当前原型状态

已实现：

- Windows 悬浮桌宠
- 透明背景小狗角色
- 鼠标拖拽
- 始终置顶
- 自定义大小
- 自定义透明度
- 开机自启动
- 左键快捷菜单
- 双击 AI 窗口
- 右键设置
- 便签
- 学习 50 分钟 / 休息 10 分钟番茄钟
- 待办事项
- 今日学习统计基础版
- CPU / 内存状态基础监控
- VPN / Codex 进程状态基础检测
- AI 助手窗口雏形
- OpenAI-compatible AI 调用
- AI 历史保存、搜索和删除基础版
- OCR 区域截图
- Tesseract OCR 接入
- OCR 结果 AI 分析入口
- Codex 一键启动 / 重启 / 日志入口
- 网络速度监控
- 摸鱼检测
- 考研倒计时提醒
- 角色图片路径切换
- 呼吸动画

待实现：

- 全局快捷键自定义 UI
- 更准确的 VPN 连接状态
- 更完整的 Codex Connected / Reconnecting 细分状态
- PaddleOCR 内置安装包
- 更完整的成就系统
- 动作状态包
