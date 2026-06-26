# Codex 桌宠

一个 Windows 桌面悬浮小宠物：始终置顶、可拖拽、右键功能菜单、便签、番茄钟、开机自启动和可视化设置。

当前版本：`1.1.1`

## 推荐启动

双击 `start_ai_moe_pet.bat` 启动 Python / PySide6 桌宠。

如果被系统拦截，也可以在 PowerShell 里运行：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -STA -File ".\codex_pet.ps1"
```

## 用法

- 左键拖动：移动桌宠。
- 左键点击：打开快捷菜单。
- 双击：打开 AI 助手。
- 右键点击：打开设置菜单。
- `Alt + Space`：呼出 AI 助手。
- `Ctrl + Shift + A`：OCR 区域截图。
- `Ctrl + Shift + H`：隐藏 / 显示桌宠。
- 便签内容会保存到 `pet-notes.txt`。
- 设置会保存到 `pet-config.json`。
- 默认开启当前用户的开机自启动，可在右键菜单的“设置”里关闭。

## 当前功能

- 桌面悬浮、无边框、始终置顶
- 开机恢复上次位置，并在显示器/缩放变化后自动夹回可用桌面
- 气泡尖角与主体一体化绘制，减少边框接缝和突兀感
- 参考小狗照片生成的红衣小狗卡通形象
- 左键打开快捷菜单
- 双击打开 AI 助手窗口
- 右键打开设置菜单
- 学习 50 分钟 / 休息 10 分钟番茄钟
- 待办事项
- 今日学习统计和连续学习成就基础版
- CPU / RAM / 磁盘健康检测与资源占用查看
- 笔记本电池状态、剩余续航、低电量提醒、充满提示和 Windows 电池报告
- VPN / Codex 进程状态基础检测
- AI 助手窗口、OpenAI-compatible API 调用、历史保存、搜索和删除
- OCR 区域截图、Tesseract 识别、AI 分析入口
- Codex 一键启动、重启、日志目录入口
- 摸鱼检测和考研倒计时提醒
- 日历 / 本地日程添加、今日/本周查看、临近提醒
- 邮件 IMAP 检查、未读统计、关键词提醒
- 触碰互动：摸头、戳身体、长按、拖拽触发不同状态
- 动画状态：待机、开心、生气、慌张、睡觉、提醒等状态机和轻量动作
- 快捷便签
- 状态气泡和轻微呼吸动画
- 自由设置名字、角色图片、大小、透明度、置顶、状态条、自启动、学习/休息时长、学习科目、AI 配置、OCR 配置和考研日期

## AI 配置

右键桌宠打开“设置”，填写：

- `AI API 地址`：OpenAI-compatible chat completions 地址，例如 `https://api.openai.com/v1/chat/completions`
- `AI 模型`：例如 `gpt-4.1-mini`、OpenRouter/DeepSeek/Gemini 兼容模型名
- `AI API Key`：你的服务商密钥

API Key 会保存在本地 `pet-config.json`，不要把这个文件发给别人。

## OCR 配置

OCR 使用 Tesseract。安装后可在设置里填写 `tesseract.exe` 的完整路径，语言默认 `chi_sim+eng`。

没有安装 Tesseract 时，OCR 仍会保存截图到 `screenshots/`，但不会识别文字。

## 邮件配置

新版 Python 桌宠支持 IMAP 邮箱检查。可在设置里填写：

- IMAP 主机：例如 QQ/163/Gmail/Outlook 的 IMAP 地址
- IMAP 端口：通常是 `993`
- 邮箱账号
- 邮箱授权码或应用专用密码
- 关键词：用逗号分隔

不要把含有 API Key 或邮箱授权码的 `pet-config.json` 发给别人。

## 迁移与在线更新

- 设置 > 高级 > 备份 / 迁移，可以导出数据备份或整机迁移包。
- 私人迁移到自己的电脑时，可以选择把 AI Key、QQ/Gmail 授权码一起放入本地迁移包。
- 迁移包解压后运行 `START_HERE.bat`，会先检查 GitHub Releases，再启动桌宠。
- 后续版本可在“备份 / 迁移”窗口点击“检查联网更新”，无需重新复制整机包。
- 日常更新采用小体积增量程序包，已有角色图片和动作资源不会重复下载。
- GitHub 更新包只包含程序和公开资源，不包含或覆盖任何个人配置、邮件、聊天、剪贴板与学习记录。

## 开源组件

- 系统与电池监控使用 [psutil](https://github.com/giampaolo/psutil)，桌宠直接调用其 Windows 电池接口，不额外启动硬件监控服务。

## 项目文档

- `docs/AI_DESKTOP_PET_REQUIREMENTS_V1.md`：完整 V1.0 需求文档
- `docs/ARCHITECTURE_V1.md`：架构设计和技术路线
- `docs/V1_BACKLOG.md`：开发优先级和任务拆分
