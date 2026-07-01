import ctypes
import ctypes.wintypes
import asyncio
import base64
import csv
import hashlib
import html
import imaplib
import ipaddress
import json
import math
import os
import platform
import random
import re
import secrets
import shutil
import smtplib
import socket
import ssl
import struct
import subprocess
import sys
import tempfile
import time
import traceback
import uuid
import webbrowser
import zipfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
try:
    import winreg
except ImportError:
    winreg = None
from dataclasses import dataclass
from datetime import datetime, timedelta
from email.header import decode_header
from email.message import EmailMessage
from email.parser import BytesParser
from email.policy import default
from email.utils import parsedate_to_datetime
from pathlib import Path
from _kaoyan_data import REDBOOK_WORDS, MATH_FORMULAS
from urllib.parse import quote
from xml.sax.saxutils import escape as xml_escape

import httpx
import psutil
from PIL import Image
from PySide6.QtCore import QAbstractNativeEventFilter, QEvent, QObject, QEasingCurve, QPoint, QPropertyAnimation, QRect, QRectF, QSize, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QAction, QColor, QCursor, QFont, QIcon, QKeyEvent, QPainter, QPainterPath, QPen, QPixmap, QShortcut, QTextCursor, QTransform
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QFileDialog,
    QFontComboBox,
    QFormLayout,
    QAbstractScrollArea,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QRubberBand,
    QScrollArea,
    QSlider,
    QSpinBox,
    QSystemTrayIcon,
    QTabWidget,
    QTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

BASE = Path(__file__).resolve().parent
APP_VERSION = "1.1.1"
DEFAULT_UPDATE_REPO = "xmj-debug/nuomi-desktop-pet"
ASSET = BASE / "assets" / "codex-pet.png"
DOG_FRAME_DIR = BASE / "assets" / "dog_frames"
CONFIG = BASE / "pet-config.json"
TODOS = BASE / "pet-todos.json"
CHAT = BASE / "pet-chat-history.json"
STUDY = BASE / "pet-study.json"
CALENDAR = BASE / "pet-calendar.json"
MAIL_STATE = BASE / "pet-mail-state.json"
PET_MEMORY = BASE / "pet-memory.json"
CLIPBOARD_HISTORY = BASE / "pet-clipboard-history.json"
WORDBOOK = BASE / "pet-wordbook.json"
BACKUP_DIR = BASE / "backups"
UPDATE_DIR = BASE / "updates"
UPDATE_LOCK = BASE / "pet-update.lock"
UPDATE_LOG = BASE / "pet-update.log"
SCREENSHOTS = BASE / "screenshots"
WATCHDOG = BASE / "nuomi_watchdog.py"
SHUTDOWN_FLAG = BASE / "pet-shutdown.flag"
RESTORE_FLAG = BASE / "pet-restore.flag"
RUNTIME_LOG = BASE / "pet-runtime.log"
STARTER_SCRIPT = BASE / "start_ai_moe_pet.bat"
LOCAL_TESSDATA_DIR = BASE / "tools" / "tessdata"
LOCAL_TESSERACT_EXE = BASE / "runtime" / "tesseract" / "tesseract.exe"
ENGLISH_WORD_SOURCE_CANDIDATES = [
    Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "Desktop" / "1.txt",
    Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "1.txt",
    Path("C:/Users/Administrator.DESKTOP-LP0BNPO/OneDrive/Desktop/1.txt"),
]
STARTUP_DIR = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
STARTUP_BAT = STARTUP_DIR / "NuomiDesktopPet.vbs"
ASSISTANT_TOOLBOX_ROOT = Path(os.environ.get("USERPROFILE", "")) / "OneDrive" / "文档" / "New project 3"
ASSISTANT_TOOLBOX_SERVER = ASSISTANT_TOOLBOX_ROOT / "server.js"
ASSISTANT_TOOLBOX_URL = "http://localhost:4173"
ASSISTANT_TOOLBOX_BAT = ASSISTANT_TOOLBOX_ROOT / "open_assistant_toolbox.bat"
BUNDLED_NODE_EXE = (
    Path(os.environ.get("USERPROFILE", ""))
    / ".cache"
    / "codex-runtimes"
    / "codex-primary-runtime"
    / "dependencies"
    / "node"
    / "bin"
    / "node.exe"
)
CLAUDE_CODE_EXE = Path(os.environ.get("USERPROFILE", "")) / ".local" / "bin" / "claude.exe"
CLAUDE_CODE_SETTINGS = Path(os.environ.get("USERPROFILE", "")) / ".claude" / "settings.deepseek.json"
CLAUDE_CHINESE_SYSTEM_PROMPT = (
    "全程使用简体中文与用户交流。命令、代码、配置键、错误原文和文件路径可以保留英文，"
    "但必须紧接着用清楚、简短的中文解释。执行修改前先说明准备做什么；遇到风险操作必须先询问。"
)
CLAUDE_TASK_TEMPLATES = [
    (
        "项目体检",
        "请先阅读项目结构和关键文件，用中文列出最值得处理的问题，按严重程度排序；"
        "然后修复能够安全确认的问题，并运行合适的检查。",
    ),
    (
        "修复报错",
        "请检查当前项目的报错、日志和最近改动，找出根因后直接修复。"
        "完成后用中文说明改了什么，并运行相关测试。",
    ),
    (
        "运行测试",
        "请识别这个项目使用的测试或检查命令，运行它们，修复失败项，"
        "最后用中文总结仍然存在的风险。",
    ),
    (
        "解释项目",
        "请先浏览项目结构，再用适合初学者理解的中文说明：项目做什么、从哪里启动、"
        "主要模块如何协作，以及修改功能通常要看哪些文件。",
    ),
    (
        "优化界面",
        "请检查当前界面的中文文案、布局、交互和异常状态，优先修复英文提示、文字溢出、"
        "按钮含义不清和常用操作步骤过多的问题。",
    ),
    (
        "代码审查",
        "请审查当前项目或最近改动，优先查找会导致崩溃、数据丢失、功能回退和安全问题的缺陷，"
        "确认后直接修复并补充必要检查。",
    ),
]
LEGACY_AIMOEPET_DIR = Path(os.environ.get("APPDATA", "")) / "AiMoePet"
LEGACY_AIMOEPET_VBS = LEGACY_AIMOEPET_DIR / "Start-AiMoePet-Hidden.vbs"
RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
LEGACY_RUN_VALUE_NAMES = ("AiMoePet", "NuomiDesktopPet")
SCREENSHOTS.mkdir(exist_ok=True)

BACKUP_DATA_FILES = [
    CONFIG,
    TODOS,
    CHAT,
    STUDY,
    CALENDAR,
    MAIL_STATE,
    PET_MEMORY,
    CLIPBOARD_HISTORY,
    WORDBOOK,
]
SECRET_CONFIG_KEYS = {"AiApiKey", "MailPassword", "GmailPassword"}
GITHUB_BACKUP_BLOCKED_NAMES = {
    path.name.casefold()
    for path in BACKUP_DATA_FILES
}
GITHUB_BACKUP_BLOCKED_NAMES.update(
    {
        "pet-notes.txt",
        "pet-shutdown.flag",
        "pet-update.lock",
        "toolbox-server.err.log",
        "toolbox-server.out.log",
    }
)
GITHUB_BACKUP_BLOCKED_DIRS = {
    "backups",
    "updates",
    "dist",
    "migration-test",
    "screenshots",
    ".claude",
    ".agents",
    ".codex",
    "__pycache__",
}

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
VK_SPACE = 0x20
VK_A = 0x41
VK_H = 0x48

user32 = ctypes.windll.user32 if sys.platform.startswith("win") else None
kernel32 = ctypes.windll.kernel32 if sys.platform.startswith("win") else None
if kernel32 is not None:
    kernel32.CreateMutexW.restype = ctypes.wintypes.HANDLE
ERROR_ALREADY_EXISTS = 183
SINGLE_INSTANCE_MUTEX = None


class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.wintypes.UINT), ("dwTime", ctypes.wintypes.DWORD)]


def seconds_since_last_input():
    if user32 is None or kernel32 is None:
        return 0
    info = LASTINPUTINFO()
    info.cbSize = ctypes.sizeof(LASTINPUTINFO)
    if not user32.GetLastInputInfo(ctypes.byref(info)):
        return 0
    elapsed_ms = kernel32.GetTickCount() - info.dwTime
    return max(0, elapsed_ms / 1000)


def foreground_window_info():
    if user32 is None:
        return {}
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        return {}
    pid = ctypes.wintypes.DWORD()
    try:
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    except Exception:
        pid = ctypes.wintypes.DWORD()
    rect = ctypes.wintypes.RECT()
    if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
        rect = None
    title = ""
    try:
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = buf.value
    except Exception:
        pass
    proc_name = ""
    try:
        if pid.value:
            proc_name = psutil.Process(pid.value).name()
    except Exception:
        pass
    return {"hwnd": int(hwnd), "pid": int(pid.value), "rect": rect, "title": title, "process_name": proc_name}


def foreground_window_fullscreen(exclude_hwnds=None, exclude_pids=None):
    info = foreground_window_info()
    if not info:
        return False
    if info.get("hwnd") in set(exclude_hwnds or []):
        return False
    if info.get("pid") in set(exclude_pids or []):
        return False
    rect = info.get("rect")
    if not rect:
        return False
    app = QApplication.instance()
    if not app:
        return False
    center = QPoint((rect.left + rect.right) // 2, (rect.top + rect.bottom) // 2)
    screen = app.screenAt(center) or app.primaryScreen()
    if not screen:
        return False
    geo = screen.geometry()
    width = rect.right - rect.left
    height = rect.bottom - rect.top
    return width >= geo.width() - 8 and height >= geo.height() - 8 and rect.left <= geo.left() + 8 and rect.top <= geo.top() + 8


def rect_intersection_area(a, b):
    inter = a.intersected(b)
    if inter.isNull():
        return 0
    return max(0, inter.width()) * max(0, inter.height())


def screen_available_geometry_for_rect(rect):
    app = QApplication.instance()
    fallback = QRect(0, 0, 1280, 720)
    if not app:
        return fallback
    points = [rect.center(), rect.topLeft(), rect.topRight(), rect.bottomLeft(), rect.bottomRight(), QCursor.pos()]
    for point in points:
        screen = app.screenAt(point)
        if screen:
            return screen.availableGeometry()
    screens = app.screens()
    if not screens:
        screen = app.primaryScreen()
        return screen.availableGeometry() if screen else fallback
    best = max(screens, key=lambda item: rect_intersection_area(rect, item.availableGeometry()))
    if rect_intersection_area(rect, best.availableGeometry()) <= 0:
        best = app.primaryScreen() or best
    return best.availableGeometry()


def clamp_window_position(pos, size):
    width = max(1, int(size.width()))
    height = max(1, int(size.height()))
    bounds = screen_available_geometry_for_rect(QRect(pos, QSize(width, height)))
    max_x = max(bounds.left(), bounds.right() - width + 1)
    max_y = max(bounds.top(), bounds.bottom() - height + 1)
    return QPoint(
        min(max(int(pos.x()), bounds.left()), max_x),
        min(max(int(pos.y()), bounds.top()), max_y),
    )


def default_window_position(size):
    app = QApplication.instance()
    screen = (app.screenAt(QCursor.pos()) or app.primaryScreen()) if app else None
    bounds = screen.availableGeometry() if screen else QRect(0, 0, 1280, 720)
    width = max(1, int(size.width()))
    height = max(1, int(size.height()))
    return clamp_window_position(
        QPoint(bounds.right() - width - 72, bounds.bottom() - height - 72),
        QSize(width, height),
    )


DEFAULT_CONFIG = {
    "PetName": "糯米",
    "PetSize": 230,
    "TextFontFamily": "Microsoft YaHei UI",
    "BubbleFontSize": 13,
    "BubbleFontBold": False,
    "BubbleFontItalic": False,
    "DesktopLabelFontSize": 11,
    "DialogFontSize": 14,
    "MenuFontSize": 12,
    "BubbleBackgroundColor": "#111827",
    "BubbleTextColor": "#f8fafc",
    "BubbleBorderColor": "#fbbf24",
    "BubbleBorderWidth": 2,
    "BubbleBorderRadius": 16,
    "BubbleWidth": 0,
    "BubbleHeight": 0,
    "BubbleOffsetX": 0,
    "BubbleOffsetY": -8,
    "Opacity": 1.0,
    "Topmost": True,
    "AutoStart": True,
    "FocusMinutes": 50,
    "RestMinutes": 10,
    "Subject": "高数",
    "AiEndpoint": "https://api.openai.com/v1/chat/completions",
    "AiApiKey": "",
    "AiModel": "gpt-4.1-mini",
    "TesseractPath": "",
    "TessdataPath": "",
    "OcrLanguage": "chi_sim+eng",
    "ExamDate": "2026-12-26",
    "PetImagePath": "",
    "MailHost": "",
    "MailPort": 993,
    "MailUser": "",
    "MailPassword": "",
    "MailAccounts": [],
    "GmailUser": "",
    "GmailPassword": "",
    "MailKeywords": "考试,学校,老师,作业,面试,账单,验证码,OpenAI,Codex,VPN",
    "VoiceEnabled": False,
    "VoiceEngine": "edge",
    "VoiceVolume": 70,
    "VoiceName": "",
    "VoiceRate": -1,
    "AmbientVoiceCooldownMinutes": 15,
    "FullscreenReminderOnly": True,
    "OneCoreVoice": "Microsoft Yaoyao",
    "OneCorePitchPercent": 8,
    "EdgeVoice": "zh-CN-XiaoxiaoNeural",
    "EdgePitchHz": 8,
    "UpdateRepo": DEFAULT_UPDATE_REPO,
    "ChatVoiceReplies": True,
    "ClipboardHistoryEnabled": True,
    "WeatherCity": "上海",
    "WindowLeft": -1,
    "WindowTop": -1,
    "ShowStatus": False,
    "BubbleEnabled": True,
    "LockPetPosition": True,
    "WatchdogEnabled": True,
    "QuietMode": False,
    "AutoQuietFullscreen": True,
    "AutoHideFullscreen": True,
    "AutoHideGames": True,
    "ActionPackPath": "",
    "SystemHealthWatchEnabled": True,
    "CpuAlertPercent": 90,
    "MemoryAlertPercent": 90,
    "DiskAlertPercent": 90,
    "BatteryAlertsEnabled": True,
    "BatteryLowPercent": 20,
    "BatteryFullPercent": 95,
    "HealthAlertCooldownMinutes": 15,
    "ClaudeLastProject": str(BASE),
    "ClaudeRecentProjects": [],
    "ClaudeSessionMode": "new",
    "ClaudePermissionMode": "default",
    "ClaudeEffort": "medium",
    "ClaudeAlwaysChinese": True,
    "ClaudeSafeMode": False,
    "AiFeatureEnabled": True,
    "TodayFeatureEnabled": True,
    "TodoFeatureEnabled": True,
    "CalendarFeatureEnabled": True,
    "WeatherFeatureEnabled": True,
    "MailFeatureEnabled": True,
    "StudyFeatureEnabled": True,
    "FormulaFeatureEnabled": True,
    "OcrFeatureEnabled": True,
    "TranslateFeatureEnabled": True,
    "FileSearchFeatureEnabled": True,
    "PerformanceFeatureEnabled": True,
    "DesktopOrganizerFeatureEnabled": True,
    "BackupFeatureEnabled": True,
    "ClaudeFeatureEnabled": True,
    "ToolboxFeatureEnabled": True,
    "DiagnosticsFeatureEnabled": True,
    "ActionLabFeatureEnabled": True,
    "NotebookFeatureEnabled": True,
    "BatteryFeatureEnabled": True,
    "OnlineUpdateFeatureEnabled": True,
    "GithubUploadFeatureEnabled": True,
    "word_popup_enabled": True,
}

TEXT_STYLE_KEYS = (
    "TextFontFamily",
    "BubbleFontSize",
    "BubbleFontBold",
    "BubbleFontItalic",
    "DesktopLabelFontSize",
    "DialogFontSize",
    "MenuFontSize",
)
BUBBLE_COLOR_KEYS = (
    "BubbleBackgroundColor",
    "BubbleTextColor",
    "BubbleBorderColor",
)
BUBBLE_FRAME_KEYS = (
    "BubbleBorderWidth",
    "BubbleBorderRadius",
    "BubbleWidth",
    "BubbleHeight",
    "BubbleOffsetX",
    "BubbleOffsetY",
)
STYLE_PREVIEW_KEYS = TEXT_STYLE_KEYS + BUBBLE_COLOR_KEYS + BUBBLE_FRAME_KEYS

FEATURE_SWITCH_GROUPS = [
    (
        "日常助手",
        [
            ("AiFeatureEnabled", "和糯米聊聊", "AI 聊天窗口、Alt+Space 快捷键。", True),
            ("TodayFeatureEnabled", "今日看板", "汇总待办、日程、天气、邮件和电脑状态。", True),
            ("BubbleEnabled", "气泡显示", "桌宠说话气泡、单词气泡和提示气泡总开关。", True),
            ("LockPetPosition", "锁定桌宠位置", "自动散步和随机动作不再把桌宠挪走，手动拖动仍会保存。", True),
            ("TodoFeatureEnabled", "提醒事项", "待办、到期提醒和自然语言提醒入口。", True),
            ("CalendarFeatureEnabled", "日程", "本地日程添加、查看今日和本周。", True),
            ("WeatherFeatureEnabled", "天气", "天气刷新和天气提示。", True),
            ("MailFeatureEnabled", "邮件", "未读邮件查看和邮件提醒入口。", True),
        ],
    ),
    (
        "学习考研",
        [
            ("StudyFeatureEnabled", "考研 / 学习统计", "考研倒计时、学习统计和番茄记录。", True),
            ("word_popup_enabled", "考研单词", "单击气泡换词、随机单词弹出。", True),
            ("FormulaFeatureEnabled", "数学公式", "考研数学公式速查。", True),
            ("OcrFeatureEnabled", "截图 OCR", "Ctrl+Shift+A 截图识别和截图提问。", True),
        ],
    ),
    (
        "工具箱",
        [
            ("TranslateFeatureEnabled", "翻译", "独立翻译窗口。", True),
            ("FileSearchFeatureEnabled", "文件搜索", "按名称和类型查找文件。", True),
            ("PerformanceFeatureEnabled", "清理 / 性能", "临时文件扫描、磁盘空间和进程查看。", True),
            ("DesktopOrganizerFeatureEnabled", "桌面整理", "扫描桌面并按类别整理。", True),
            ("DiagnosticsFeatureEnabled", "诊断中心", "AI、邮箱、OCR、VPN、启动项诊断。", True),
            ("ActionLabFeatureEnabled", "动作实验室", "测试桌宠动作和状态。", True),
            ("NotebookFeatureEnabled", "词库 / 笔记", "词库和本地笔记入口。", True),
            ("BatteryFeatureEnabled", "电池工具", "电池状态窗口和电池报告入口。", True),
            ("BackupFeatureEnabled", "备份 / 迁移", "本地备份、整机迁移包和恢复。", True),
            ("ToolboxFeatureEnabled", "核心工具箱", "打开外部工具箱服务。", True),
            ("ClaudeFeatureEnabled", "Claude Code", "中文 Claude Code 启动器。", True),
        ],
    ),
    (
        "系统提醒",
        [
            ("SystemHealthWatchEnabled", "电脑异常检测", "CPU、内存、磁盘等异常提醒。", True),
            ("BatteryAlertsEnabled", "电池提醒", "低电量、充满和电源状态提醒。", True),
            ("AutoQuietFullscreen", "全屏自动安静", "全屏视频或游戏时减少打扰。", True),
            ("AutoHideFullscreen", "全屏游戏自动隐藏", "全屏游戏时自动隐藏桌宠。", True),
            ("AutoHideGames", "游戏前台自动隐藏", "检测到游戏窗口在前台时隐藏桌宠。", True),
            ("WatchdogEnabled", "自恢复守护", "异常退出后自动拉起糯米。", True),
        ],
    ),
    (
        "高级 / 敏感",
        [
            ("VoiceEnabled", "语音播报", "桌宠气泡和提醒的语音朗读。", False),
            ("ChatVoiceReplies", "AI 回复朗读", "AI 聊天回复自动朗读。", False),
            ("ClipboardHistoryEnabled", "剪贴板记录", "记录文字剪贴板历史。", False),
            ("AutoStart", "开机自启", "登录 Windows 后自动启动糯米。", False),
            ("OnlineUpdateFeatureEnabled", "联网检查更新", "连接 GitHub 检查更新包。", False),
            ("GithubUploadFeatureEnabled", "手动上传到 GitHub", "把程序代码提交并推送到 GitHub。", False),
        ],
    ),
]

FEATURE_SWITCH_ITEMS = [
    {"key": key, "label": label, "description": description, "safe": safe}
    for _group, items in FEATURE_SWITCH_GROUPS
    for key, label, description, safe in items
]
FEATURE_SWITCH_LABELS = {item["key"]: item["label"] for item in FEATURE_SWITCH_ITEMS}
FEATURE_SWITCH_KEYS = tuple(item["key"] for item in FEATURE_SWITCH_ITEMS)


def feature_enabled(config, key):
    config = config or {}
    return bool(config.get(key, DEFAULT_CONFIG.get(key, True)))


def feature_label(key):
    return FEATURE_SWITCH_LABELS.get(key, key)


def feature_display_label(key, config=None):
    if key == "AiFeatureEnabled":
        name = str((config or {}).get("PetName") or DEFAULT_CONFIG["PetName"]).strip() or DEFAULT_CONFIG["PetName"]
        return f"和{name}聊聊"
    return feature_label(key)


def safe_enable_feature_config(config):
    for item in FEATURE_SWITCH_ITEMS:
        if item["safe"]:
            config[item["key"]] = True


def reset_feature_config_defaults(config):
    for key in FEATURE_SWITCH_KEYS:
        config[key] = DEFAULT_CONFIG.get(key, True)


SETTING_SECRET_WORDS = (
    "api key",
    "apikey",
    "api密钥",
    "密钥",
    "密码",
    "邮箱密码",
    "mailpassword",
    "gmailpassword",
    "aipassword",
    "token",
    "令牌",
)
SETTING_ACTION_WORDS = (
    "设置",
    "修改",
    "更改",
    "改成",
    "改为",
    "设为",
    "调成",
    "调整",
    "打开",
    "开启",
    "启用",
    "关闭",
    "关掉",
    "禁用",
    "停用",
    "恢复默认",
    "安全全开启",
    "一键全开启",
    "移动",
    "以后",
    "从现在起",
    "上移",
    "下移",
    "左移",
    "右移",
    "向上",
    "向下",
    "向左",
    "向右",
)
SETTING_ON_WORDS = ("开启", "打开", "启用", "允许", "恢复", "显示", "开一下", "打开一下", "全开启")
SETTING_OFF_WORDS = ("关闭", "关掉", "关了", "禁用", "停用", "取消", "不要", "别", "禁止")
SETTING_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
SETTING_COLOR_NAMES = {
    "黑色": "#111827",
    "白色": "#ffffff",
    "蓝色": "#2563eb",
    "浅蓝": "#38bdf8",
    "绿色": "#16a34a",
    "红色": "#dc2626",
    "粉色": "#ec4899",
    "紫色": "#7c3aed",
    "黄色": "#fbbf24",
    "橙色": "#f97316",
    "灰色": "#475569",
    "透明黑": "#111827",
}

NATURAL_BOOL_SETTINGS = [
    ("BubbleEnabled", "气泡显示", ("气泡", "对话框", "说话框", "聊天气泡")),
    ("Topmost", "窗口置顶", ("置顶", "窗口置顶", "桌宠置顶", "总在最前")),
    ("LockPetPosition", "锁定桌宠位置", ("锁定位置", "固定位置", "桌宠位置固定", "别乱跑", "不要乱跑")),
    ("ShowStatus", "桌面状态标签", ("状态标签", "桌面标签", "状态小标签")),
    ("VoiceEnabled", "语音播报", ("语音播报", "朗读气泡", "桌宠朗读")),
    ("ChatVoiceReplies", "AI 回复朗读", ("AI回复朗读", "聊天回复朗读", "自动朗读回复")),
    ("ClipboardHistoryEnabled", "剪贴板记录", ("剪贴板记录", "剪贴板历史")),
    ("QuietMode", "安静模式", ("安静模式", "勿扰模式")),
    ("AutoQuietFullscreen", "全屏自动安静", ("全屏自动安静", "全屏安静", "全屏减少打扰")),
    ("AutoHideFullscreen", "全屏游戏自动隐藏", ("全屏游戏自动隐藏", "游戏全屏隐藏", "全屏隐藏桌宠")),
    ("AutoHideGames", "游戏前台自动隐藏", ("游戏前台自动隐藏", "检测游戏隐藏", "游戏隐藏桌宠")),
    ("AutoStart", "开机自启", ("开机自启", "开机自动启动", "登录自动启动")),
    ("WatchdogEnabled", "自恢复守护", ("自恢复守护", "守护进程", "异常重启")),
    ("SystemHealthWatchEnabled", "电脑异常检测", ("电脑异常检测", "系统异常检测", "电脑状态提醒", "CPU提醒")),
    ("BatteryAlertsEnabled", "电池提醒", ("电池提醒", "低电量提醒", "充满提醒")),
    ("FullscreenReminderOnly", "全屏仅提醒发声", ("全屏仅提醒发声", "全屏只提醒", "全屏只允许提醒")),
    ("word_popup_enabled", "考研单词", ("单词弹窗", "考研单词", "单词气泡", "单词功能", "词汇弹窗")),
    ("AiFeatureEnabled", "AI 聊天", ("AI聊天", "聊天功能", "问问", "问我", "问糯米")),
    ("TodayFeatureEnabled", "今日看板", ("今日看板", "今日功能")),
    ("TodoFeatureEnabled", "提醒事项", ("提醒事项", "待办功能", "提醒功能")),
    ("CalendarFeatureEnabled", "日程", ("日程功能", "日历功能")),
    ("WeatherFeatureEnabled", "天气", ("天气功能", "天气卡片")),
    ("MailFeatureEnabled", "邮件", ("邮件功能", "邮箱功能")),
    ("StudyFeatureEnabled", "考研 / 学习统计", ("考研功能", "学习统计", "番茄记录")),
    ("FormulaFeatureEnabled", "数学公式", ("数学公式", "公式速查", "公式功能")),
    ("OcrFeatureEnabled", "截图 OCR", ("截图OCR", "OCR功能", "截图识别")),
    ("TranslateFeatureEnabled", "翻译", ("翻译功能", "翻译窗口")),
    ("FileSearchFeatureEnabled", "文件搜索", ("文件搜索", "搜索文件")),
    ("PerformanceFeatureEnabled", "清理 / 性能", ("清理功能", "性能工具", "进程查看")),
    ("DesktopOrganizerFeatureEnabled", "桌面整理", ("桌面整理", "整理桌面")),
    ("BackupFeatureEnabled", "备份 / 迁移", ("备份功能", "迁移功能")),
    ("ClaudeFeatureEnabled", "Claude Code", ("Claude功能", "Claude Code", "启动Claude")),
    ("ToolboxFeatureEnabled", "核心工具箱", ("工具箱", "核心工具箱")),
    ("DiagnosticsFeatureEnabled", "诊断中心", ("诊断中心", "诊断功能")),
    ("ActionLabFeatureEnabled", "动作实验室", ("动作实验室", "动作功能")),
    ("NotebookFeatureEnabled", "词库 / 笔记", ("词库", "笔记本", "单词本")),
    ("BatteryFeatureEnabled", "电池工具", ("电池工具", "电池窗口")),
    ("OnlineUpdateFeatureEnabled", "联网检查更新", ("联网检查更新", "检查联网更新", "在线更新")),
    ("GithubUploadFeatureEnabled", "手动上传到 GitHub", ("上传GitHub", "GitHub上传", "手动上传")),
    ("ClaudeAlwaysChinese", "Claude 中文模式", ("Claude中文", "Claude一直中文", "Claude中文界面")),
    ("ClaudeSafeMode", "Claude 安全模式", ("Claude安全模式", "Claude保守模式")),
    ("BubbleFontBold", "气泡粗体", ("气泡粗体", "气泡文字加粗", "文字加粗")),
    ("BubbleFontItalic", "气泡斜体", ("气泡斜体", "气泡文字斜体", "文字斜体")),
]

NATURAL_NUMBER_SETTINGS = [
    ("PetSize", "桌宠大小", ("桌宠大小", "宠物大小", "角色大小", "桌宠尺寸"), 120, 360, "px"),
    ("BubbleFontSize", "气泡字号", ("气泡字号", "气泡字体大小", "气泡文字大小"), 10, 24, "px"),
    ("DesktopLabelFontSize", "桌面标签字号", ("桌面标签字号", "状态标签字号", "小标签字号"), 9, 20, "px"),
    ("DialogFontSize", "弹窗字号", ("弹窗字号", "窗口字号", "对话窗口字号"), 11, 22, "px"),
    ("MenuFontSize", "菜单字号", ("菜单字号", "右键菜单字号", "快捷菜单字号"), 10, 22, "px"),
    ("BubbleBorderWidth", "气泡边框宽度", ("气泡边框宽度", "气泡描边宽度", "气泡边框"), 1, 8, "px"),
    ("BubbleBorderRadius", "气泡圆角", ("气泡圆角", "气泡圆角大小"), 4, 32, "px"),
    ("BubbleWidth", "气泡宽度", ("气泡宽度", "对话框宽度", "气泡框宽度"), 0, 680, "px_auto"),
    ("BubbleHeight", "气泡高度", ("气泡高度", "对话框高度", "气泡框高度"), 0, 360, "px_auto"),
    ("BubbleOffsetX", "气泡横向位置", ("气泡横向位置", "气泡X", "气泡x", "气泡左右偏移"), -1200, 1200, "signed_px"),
    ("BubbleOffsetY", "气泡纵向位置", ("气泡纵向位置", "气泡Y", "气泡y", "气泡上下偏移"), -1200, 1200, "signed_px"),
    ("FocusMinutes", "专注时长", ("专注时长", "番茄时长", "学习时长"), 5, 180, "分钟"),
    ("RestMinutes", "休息时长", ("休息时长", "番茄休息"), 1, 60, "分钟"),
    ("VoiceVolume", "语音音量", ("语音音量", "朗读音量", "声音音量"), 0, 100, "%"),
    ("VoiceRate", "语速", ("语速", "朗读速度"), -5, 5, ""),
    ("AmbientVoiceCooldownMinutes", "主动说话间隔", ("主动说话间隔", "语音冷却", "冒泡说话间隔"), 0, 120, "分钟"),
    ("OneCorePitchPercent", "离线语音音调", ("离线语音音调", "瑶瑶音调", "OneCore音调"), -20, 20, "%"),
    ("EdgePitchHz", "在线语音音调", ("在线语音音调", "晓晓音调", "Edge音调"), -50, 50, "Hz"),
    ("CpuAlertPercent", "CPU 提醒阈值", ("CPU阈值", "CPU提醒阈值", "CPU占用提醒"), 50, 100, "%"),
    ("MemoryAlertPercent", "内存提醒阈值", ("内存阈值", "内存提醒阈值", "内存占用提醒"), 50, 100, "%"),
    ("DiskAlertPercent", "磁盘提醒阈值", ("磁盘阈值", "磁盘提醒阈值", "磁盘占用提醒"), 70, 100, "%"),
    ("BatteryLowPercent", "低电量阈值", ("低电量阈值", "低电量提醒阈值"), 5, 40, "%"),
    ("BatteryFullPercent", "充满提醒阈值", ("充满阈值", "满电提醒阈值", "充满提醒阈值"), 80, 100, "%"),
    ("HealthAlertCooldownMinutes", "异常提醒间隔", ("异常提醒间隔", "电脑异常提醒间隔", "健康提醒间隔"), 3, 120, "分钟"),
]


def _setting_clean_value(value):
    return str(value or "").strip().strip("“”\"' ，,。.!！；;：:")


def _setting_first_number(text):
    match = SETTING_NUMBER_RE.search(str(text or ""))
    return float(match.group(0)) if match else None


def _setting_number_for_alias(text, alias, allow_global=False):
    raw = str(text or "")
    start = raw.find(alias)
    while start >= 0:
        window = raw[start : start + len(alias) + 28]
        number = _setting_first_number(window)
        if number is not None:
            return number
        start = raw.find(alias, start + len(alias))
    if allow_global:
        numbers = SETTING_NUMBER_RE.findall(raw)
        if len(numbers) == 1:
            return float(numbers[0])
    return None


def _setting_bool_value(text, aliases):
    raw = str(text or "")
    windows = []
    for alias in aliases:
        start = raw.find(alias)
        while start >= 0:
            windows.append(raw[max(0, start - 12) : start + len(alias) + 20])
            start = raw.find(alias, start + len(alias))
    source = "\n".join(windows) if windows else raw
    if any(word in source for word in SETTING_OFF_WORDS):
        return False
    if any(word in source for word in SETTING_ON_WORDS):
        return True
    return None


def _setting_clamped_int(number, low, high):
    return max(low, min(high, int(round(number))))


def _setting_number_display(value, unit):
    if unit == "px_auto":
        return "自动" if int(value) <= 0 else f"{int(value)}px"
    if unit == "signed_px":
        return f"{int(value):+d}px"
    return f"{int(value)}{unit}" if unit else str(int(value))


def _setting_color_from_text(text):
    raw = str(text or "")
    match = re.search(r"#[0-9a-fA-F]{3,8}", raw)
    if match:
        return normalize_color(match.group(0), "")
    for name, color in SETTING_COLOR_NAMES.items():
        if name in raw:
            return color
    return ""


def _setting_date_from_text(text):
    raw = str(text or "")
    match = re.search(r"(\d{4})\s*[年\-/.]\s*(\d{1,2})\s*[月\-/.]\s*(\d{1,2})", raw)
    if not match:
        match = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?", raw)
        if not match:
            return ""
        year = datetime.now().year
        month = int(match.group(1))
        day = int(match.group(2))
    else:
        year = int(match.group(1))
        month = int(match.group(2))
        day = int(match.group(3))
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _setting_text_after_patterns(text, patterns):
    raw = str(text or "")
    for pattern in patterns:
        match = re.search(pattern, raw, flags=re.IGNORECASE)
        if match:
            value = _setting_clean_value(match.group(1))
            if value:
                return value
    return ""


def _setting_apply_bubble_size_pair(raw, add_change):
    if "气泡" not in raw and "对话框" not in raw and "说话框" not in raw:
        return
    if any(word in raw for word in ("自动大小", "自动调节", "自动宽高", "大小自动")):
        add_change("BubbleWidth", 0, "气泡宽度", "自动")
        add_change("BubbleHeight", 0, "气泡高度", "自动")
        return
    match = re.search(r"(\d{2,3})\s*[xX×*]\s*(\d{2,3})", raw)
    if not match:
        return
    width = _setting_clamped_int(float(match.group(1)), 0, 680)
    height = _setting_clamped_int(float(match.group(2)), 0, 360)
    add_change("BubbleWidth", width, "气泡宽度", _setting_number_display(width, "px_auto"))
    add_change("BubbleHeight", height, "气泡高度", _setting_number_display(height, "px_auto"))


def _setting_apply_bubble_direction(raw, config, add_change):
    if "气泡" not in raw and "对话框" not in raw and "说话框" not in raw:
        return
    if not any(word in raw for word in ("向上", "往上", "上移", "向下", "往下", "下移", "向左", "往左", "左移", "向右", "往右", "右移")):
        return
    amount = _setting_first_number(raw)
    if amount is None:
        amount = 20
    amount = int(round(amount))
    x = clamp_int(config.get("BubbleOffsetX"), -1200, 1200, DEFAULT_CONFIG["BubbleOffsetX"])
    y = clamp_int(config.get("BubbleOffsetY"), -1200, 1200, DEFAULT_CONFIG["BubbleOffsetY"])
    if any(word in raw for word in ("向上", "往上", "上移")):
        y -= amount
    if any(word in raw for word in ("向下", "往下", "下移")):
        y += amount
    if any(word in raw for word in ("向左", "往左", "左移")):
        x -= amount
    if any(word in raw for word in ("向右", "往右", "右移")):
        x += amount
    x = _setting_clamped_int(x, -1200, 1200)
    y = _setting_clamped_int(y, -1200, 1200)
    add_change("BubbleOffsetX", x, "气泡横向位置", _setting_number_display(x, "signed_px"))
    add_change("BubbleOffsetY", y, "气泡纵向位置", _setting_number_display(y, "signed_px"))


def parse_natural_setting_changes(text, config, pet_name=None):
    raw = str(text or "").strip()
    lowered = raw.lower()
    intent_words = SETTING_ACTION_WORDS + SETTING_ON_WORDS + SETTING_OFF_WORDS
    if not raw or not any(word.lower() in lowered for word in intent_words):
        return {"handled": False}

    draft = dict(config or {})
    notes = []
    blocked = []
    noops = []

    def add_change(key, value, label, display=None):
        old = draft.get(key, DEFAULT_CONFIG.get(key))
        if old == value:
            noops.append(f"{label} 已经是 {display if display is not None else value}")
            return
        draft[key] = value
        notes.append(f"{label}：{display if display is not None else value}")

    if any(word in lowered for word in SETTING_SECRET_WORDS):
        blocked.append("密钥、密码和令牌类设置请在设置窗口里手动修改，避免聊天误改或泄露。")

    if ("功能" in raw or "开关" in raw) and any(word in raw for word in ("安全全开启", "一键全开启", "全开启")):
        before = {key: draft.get(key, DEFAULT_CONFIG.get(key)) for key in FEATURE_SWITCH_KEYS}
        safe_enable_feature_config(draft)
        if any(draft.get(key) != value for key, value in before.items()):
            notes.append("功能开关：已安全全开启普通功能")
        else:
            noops.append("功能开关已经是安全全开启状态")

    if ("功能" in raw or "开关" in raw) and "恢复默认" in raw:
        reset_feature_config_defaults(draft)
        notes.append("功能开关：已恢复默认")

    name_value = _setting_text_after_patterns(
        raw,
        [
            r"(?:把)?(?:桌宠|宠物|你的|你)?(?:名字|昵称)\s*(?:改成|改为|设为|设置为|叫做|叫成|叫)\s*([^\s，。！!；;]+)",
            r"(?:以后|从现在起).{0,6}(?:你|桌宠|宠物)?(?:就)?叫\s*([^\s，。！!；;]+)",
        ],
    )
    if name_value:
        add_change("PetName", name_value[:16], "桌宠名字", name_value[:16])

    city_value = _setting_text_after_patterns(
        raw,
        [r"(?:天气城市|天气位置|默认城市)\s*(?:改成|改为|设为|设置为|调成)\s*([^\s，。！!；;]+)"],
    )
    if city_value:
        add_change("WeatherCity", city_value[:24], "天气城市", city_value[:24])

    subject_value = _setting_text_after_patterns(
        raw,
        [r"(?:学习科目|专注科目|复习科目|科目)\s*(?:改成|改为|设为|设置为|调成)\s*([^\s，。！!；;]+)"],
    )
    if subject_value:
        add_change("Subject", subject_value[:24], "学习科目", subject_value[:24])

    font_value = _setting_text_after_patterns(
        raw,
        [r"(?:文字字体|界面字体|字体)\s*(?:改成|改为|设为|设置为|调成)\s*([A-Za-z0-9_\-\u4e00-\u9fff ]{2,64})"],
    )
    if font_value:
        add_change("TextFontFamily", font_value[:64], "界面字体", font_value[:64])

    mail_keywords_value = _setting_text_after_patterns(
        raw,
        [r"(?:邮件关键词|邮箱关键词|邮件提醒关键词)\s*(?:改成|改为|设为|设置为)\s*([^\n。！!；;]+)"],
    )
    if mail_keywords_value:
        keywords = [
            item.strip()
            for item in re.split(r"[,，、\s]+", mail_keywords_value)
            if item.strip()
        ]
        if keywords:
            value = ",".join(keywords[:30])
            add_change("MailKeywords", value, "邮件关键词", value)

    model_value = _setting_text_after_patterns(
        raw,
        [r"(?:AI模型|聊天模型|模型)\s*(?:改成|改为|设为|设置为)\s*([A-Za-z0-9_.:/-]+)"],
    )
    if model_value:
        add_change("AiModel", model_value[:80], "AI 模型", model_value[:80])

    if any(alias in raw for alias in ("考研日期", "考试日期", "考试时间")):
        date_value = _setting_date_from_text(raw)
        if date_value:
            add_change("ExamDate", date_value, "考研日期", date_value)

    if any(alias in raw for alias in ("语音引擎", "声音引擎", "朗读引擎", "语音模式")):
        if any(word in raw for word in ("在线", "晓晓", "edge", "Edge")):
            add_change("VoiceEngine", "edge", "语音引擎", "在线晓晓")
        elif any(word in raw for word in ("离线", "瑶瑶", "onecore", "OneCore")):
            add_change("VoiceEngine", "onecore", "语音引擎", "离线瑶瑶")
        elif "windows" in lowered or "传统" in raw:
            add_change("VoiceEngine", "windows", "语音引擎", "Windows 传统语音")

    if "OCR" in raw.upper() or "识别语言" in raw:
        if any(word in raw for word in ("中英", "中文英文", "中文和英文", "英文中文", "英中")):
            add_change("OcrLanguage", "chi_sim+eng", "OCR 语言", "中文+英文")
        elif any(word in raw for word in ("英文", "英语", "eng")):
            add_change("OcrLanguage", "eng", "OCR 语言", "英文")
        elif any(word in raw for word in ("中文", "简体", "汉字")):
            add_change("OcrLanguage", "chi_sim", "OCR 语言", "中文")

    voice_aliases = {
        "晓晓": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-XiaoxiaoNeural", "晓晓"),
        "小小": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-XiaoxiaoNeural", "晓晓"),
        "晓伊": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-XiaoyiNeural", "晓伊"),
        "晓双": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-XiaoshuangNeural", "晓双"),
        "云希": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-YunxiNeural", "云希"),
        "云健": ("VoiceEngine", "edge", "EdgeVoice", "zh-CN-YunjianNeural", "云健"),
        "瑶瑶": ("VoiceEngine", "onecore", "OneCoreVoice", "Microsoft Yaoyao", "瑶瑶"),
        "耀耀": ("VoiceEngine", "onecore", "OneCoreVoice", "Microsoft Yaoyao", "瑶瑶"),
        "慧慧": ("VoiceEngine", "onecore", "OneCoreVoice", "Microsoft Huihui", "慧慧"),
        "康康": ("VoiceEngine", "onecore", "OneCoreVoice", "Microsoft Kangkang", "康康"),
    }
    if any(word in raw for word in ("声音", "语音", "音色", "朗读")):
        for alias, (engine_key, engine, voice_key, voice_id, voice_label) in voice_aliases.items():
            if alias not in raw:
                continue
            add_change(engine_key, engine, "语音引擎", "在线神经语音" if engine == "edge" else "离线 OneCore")
            add_change(voice_key, voice_id, "语音角色", voice_label)
            break

    color_targets = [
        ("BubbleTextColor", "气泡文字颜色", ("气泡文字颜色", "气泡字体颜色", "文字颜色")),
        ("BubbleBorderColor", "气泡边框颜色", ("气泡边框颜色", "气泡描边颜色", "边框颜色")),
        ("BubbleBackgroundColor", "气泡背景颜色", ("气泡背景", "气泡底色", "气泡颜色", "对话框颜色")),
    ]
    for key, label, aliases in color_targets:
        if any(alias in raw for alias in aliases):
            color = _setting_color_from_text(raw)
            if color:
                add_change(key, color, label, color)
            break

    _setting_apply_bubble_size_pair(raw, add_change)
    _setting_apply_bubble_direction(raw, draft, add_change)

    matched_numeric = [
        (key, label, aliases, low, high, unit)
        for key, label, aliases, low, high, unit in NATURAL_NUMBER_SETTINGS
        if any(alias in raw for alias in aliases)
    ]
    for key, label, aliases, low, high, unit in matched_numeric:
        number = None
        for alias in aliases:
            if alias in raw:
                number = _setting_number_for_alias(raw, alias, allow_global=len(matched_numeric) == 1)
                if number is not None:
                    break
        if number is None:
            continue
        if key == "Opacity":
            percent = number * 100 if number <= 1 else number
            percent = _setting_clamped_int(percent, 45, 100)
            add_change(key, percent / 100, label, f"{percent}%")
        else:
            value = _setting_clamped_int(number, low, high)
            add_change(key, value, label, _setting_number_display(value, unit))

    if any(alias in raw for alias in ("透明度", "不透明度")):
        number = _setting_first_number(raw)
        if number is not None:
            percent = number * 100 if number <= 1 else number
            percent = _setting_clamped_int(percent, 45, 100)
            add_change("Opacity", percent / 100, "透明度", f"{percent}%")

    for key, label, aliases in NATURAL_BOOL_SETTINGS:
        dynamic_aliases = tuple(aliases)
        if key == "AiFeatureEnabled":
            current_name = _setting_clean_value(pet_name) or DEFAULT_CONFIG["PetName"]
            dynamic_aliases = dynamic_aliases + (f"问{current_name}", f"问问{current_name}", f"和{current_name}聊聊")
        if not any(alias in raw for alias in dynamic_aliases):
            continue
        value = _setting_bool_value(raw, dynamic_aliases)
        if value is None:
            continue
        add_change(key, bool(value), label, "开启" if value else "关闭")

    changed_keys = {
        key
        for key in set(draft) | set(config or {})
        if draft.get(key, DEFAULT_CONFIG.get(key)) != (config or {}).get(key, DEFAULT_CONFIG.get(key))
    }
    handled = bool(notes or blocked or noops)
    return {
        "handled": handled,
        "config": draft,
        "changed_keys": changed_keys,
        "notes": notes,
        "blocked": blocked,
        "noops": noops,
    }

CHINA_HOLIDAYS_2026 = [
    {"name": "元旦", "start": "2026-01-01", "end": "2026-01-03", "days": 3},
    {"name": "春节", "start": "2026-02-15", "end": "2026-02-23", "days": 9},
    {"name": "清明节", "start": "2026-04-04", "end": "2026-04-06", "days": 3},
    {"name": "劳动节", "start": "2026-05-01", "end": "2026-05-05", "days": 5},
    {"name": "端午节", "start": "2026-06-19", "end": "2026-06-21", "days": 3},
    {"name": "中秋节", "start": "2026-09-25", "end": "2026-09-27", "days": 3},
    {"name": "国庆节", "start": "2026-10-01", "end": "2026-10-07", "days": 7},
]

EXTRA_MATH_FORMULAS = [
    (
        "常用等价无穷小",
        "x→0:\n"
        "sin x ~ x\n"
        "tan x ~ x\n"
        "arcsin x ~ x\n"
        "arctan x ~ x\n"
        "1-cos x ~ x^2/2\n"
        "ln(1+x) ~ x\n"
        "e^x-1 ~ x\n"
        "(1+x)^a-1 ~ ax",
    ),
    (
        "洛必达法则",
        "0/0 或 ∞/∞ 型:\n"
        "lim f(x)/g(x)=lim f'(x)/g'(x)\n"
        "使用前先确认分子分母同趋于 0 或同趋于无穷，且右侧极限存在。",
    ),
    (
        "导数运算法则",
        "(u±v)'=u'±v'\n"
        "(uv)'=u'v+uv'\n"
        "(u/v)'=(u'v-uv')/v^2\n"
        "(f[g(x)])'=f'[g(x)]g'(x)\n"
        "(ln|u|)'=u'/u",
    ),
    (
        "常用导数",
        "(a^x)'=a^x ln a\n"
        "(log_a x)'=1/(x ln a)\n"
        "(arcsin x)'=1/sqrt(1-x^2)\n"
        "(arccos x)'=-1/sqrt(1-x^2)\n"
        "(arctan x)'=1/(1+x^2)",
    ),
    (
        "不定积分技巧",
        "第一换元法: ∫f(g(x))g'(x)dx=∫f(u)du\n"
        "第二换元法: x=φ(t)\n"
        "分部积分: ∫u dv=uv-∫v du\n"
        "有理函数积分常用拆分为部分分式。",
    ),
    (
        "常用积分",
        "∫1/(1+x^2) dx=arctan x+C\n"
        "∫1/sqrt(1-x^2) dx=arcsin x+C\n"
        "∫sec^2 x dx=tan x+C\n"
        "∫csc^2 x dx=-cot x+C\n"
        "∫sec x tan x dx=sec x+C\n"
        "∫csc x cot x dx=-csc x+C",
    ),
    (
        "中值定理",
        "罗尔定理: f(a)=f(b) => ∃ξ, f'(ξ)=0\n"
        "拉格朗日中值定理: f(b)-f(a)=f'(ξ)(b-a)\n"
        "柯西中值定理: [f(b)-f(a)]/[g(b)-g(a)]=f'(ξ)/g'(ξ)",
    ),
    (
        "偏导与极值",
        "驻点: f_x=0, f_y=0\n"
        "A=f_xx, B=f_xy, C=f_yy, D=AC-B^2\n"
        "D>0 且 A>0 为极小值\n"
        "D>0 且 A<0 为极大值\n"
        "D<0 不是极值",
    ),
    (
        "二重积分换元",
        "直角坐标: ∬_D f(x,y) dxdy\n"
        "极坐标: x=r cosθ, y=r sinθ, dxdy=r drdθ\n"
        "一般换元: dxdy=|J| dudv",
    ),
    (
        "矩阵秩",
        "r(A)=r(A^T)\n"
        "r(AB)≤min(r(A),r(B))\n"
        "r(A+B)≤r(A)+r(B)\n"
        "A 可逆 => r(AB)=r(B), r(BA)=r(B)\n"
        "n 阶方阵 A 可逆 ⇔ r(A)=n ⇔ |A|≠0",
    ),
    (
        "线性方程组",
        "Ax=b 有解 ⇔ r(A)=r(A,b)\n"
        "唯一解 ⇔ r(A)=r(A,b)=n\n"
        "无穷多解 ⇔ r(A)=r(A,b)<n\n"
        "齐次 Ax=0 有非零解 ⇔ r(A)<n",
    ),
    (
        "特征值与特征向量",
        "|λE-A|=0\n"
        "Aα=λα\n"
        "tr(A)=λ1+...+λn\n"
        "|A|=λ1λ2...λn\n"
        "A 可对角化 ⇔ 有 n 个线性无关特征向量",
    ),
    (
        "正交与二次型",
        "正交矩阵: Q^TQ=E, Q^-1=Q^T\n"
        "二次型: f=x^T A x\n"
        "正定: 所有顺序主子式 >0\n"
        "实对称矩阵可正交对角化。",
    ),
    (
        "随机变量数字特征",
        "E(aX+b)=aE(X)+b\n"
        "D(aX+b)=a^2D(X)\n"
        "D(X)=E(X^2)-[E(X)]^2\n"
        "Cov(X,Y)=E(XY)-E(X)E(Y)\n"
        "ρ=Cov(X,Y)/sqrt(DX DY)",
    ),
    (
        "常见分布",
        "0-1分布: E(X)=p, D(X)=p(1-p)\n"
        "二项分布 B(n,p): E(X)=np, D(X)=np(1-p)\n"
        "泊松分布 P(λ): E(X)=D(X)=λ\n"
        "正态分布 N(μ,σ^2): 标准化 Z=(X-μ)/σ",
    ),
]


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def save_json(path: Path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


_EXAM_WORD_CACHE = None
_REDBOOK_MEANING_CACHE = None


def reset_exam_word_cache():
    global _EXAM_WORD_CACHE
    _EXAM_WORD_CACHE = None


def redbook_meaning_lookup():
    global _REDBOOK_MEANING_CACHE
    if _REDBOOK_MEANING_CACHE is None:
        _REDBOOK_MEANING_CACHE = {str(word).strip().lower(): meaning for word, meaning, _freq in REDBOOK_WORDS}
    return _REDBOOK_MEANING_CACHE


def normalize_exam_word(value):
    word = re.sub(r"\s+", " ", str(value or "")).strip()
    word = word.strip(" \t\r\n\"'“”‘’.,;:：，；()[]{}<>")
    if not re.fullmatch(r"[A-Za-z][A-Za-z'\-]*(?: [A-Za-z][A-Za-z'\-]*){0,4}", word):
        return ""
    return word


def clean_word_meaning(value):
    meaning = re.sub(r"/[^/]+/", " ", str(value or ""))
    meaning = re.sub(r"^\s*[-—:：,，;；\t]+", "", meaning)
    meaning = re.sub(
        r"\s+\b(?:n|v|adj|adv|prep|conj|pron|num|art|vt|vi|abbr|phr|pl|interj)\.?(?:&(?:n|v|adj|adv)\.?)?\s*",
        "；",
        meaning,
        flags=re.IGNORECASE,
    )
    meaning = re.sub(r"\s+", " ", meaning).strip(" .;；")
    return meaning


def build_wordbook_item(word, meaning="", source="import"):
    word = normalize_exam_word(word)
    if not word:
        return None
    meaning = clean_word_meaning(meaning)
    if not meaning:
        meaning = redbook_meaning_lookup().get(word.lower(), "待补充")
    return {
        "word": word,
        "meaning": meaning,
        "source": source,
        "updated_at": datetime.now().isoformat(timespec="seconds"),
    }


def wordbook_key(item):
    return str(item.get("word", "")).strip().lower()


def sanitize_wordbook_items(items, source="manual"):
    result = []
    seen = set()
    for item in items or []:
        if not isinstance(item, dict):
            continue
        built = build_wordbook_item(item.get("word", ""), item.get("meaning", ""), item.get("source") or source)
        if not built:
            continue
        key = wordbook_key(built)
        if key in seen:
            continue
        seen.add(key)
        result.append(built)
    return result


def load_wordbook():
    items = load_json(WORDBOOK, [])
    return sanitize_wordbook_items(items if isinstance(items, list) else [])


def save_wordbook(items):
    save_json(WORDBOOK, sanitize_wordbook_items(items)[:2000])
    reset_exam_word_cache()


def ensure_wordbook_migrated(config=None):
    config = config or load_json(CONFIG, {})
    legacy = sanitize_wordbook_items(config.get("notebook_words", []), source="legacy")
    if not legacy:
        return load_wordbook()
    current = load_wordbook()
    known = {wordbook_key(item) for item in current}
    merged = current + [item for item in legacy if wordbook_key(item) not in known]
    if len(merged) != len(current):
        save_wordbook(merged)
    return merged


def merge_wordbook_entries(incoming):
    current = ensure_wordbook_migrated()
    by_key = {wordbook_key(item): item for item in current}
    incoming_order = []
    seen_incoming = set()
    added = 0
    duplicate = 0
    for raw in incoming or []:
        if not isinstance(raw, dict):
            continue
        item = build_wordbook_item(raw.get("word", ""), raw.get("meaning", ""), raw.get("source") or "import")
        if not item:
            continue
        key = wordbook_key(item)
        if not key:
            continue
        if key in seen_incoming:
            duplicate += 1
            continue
        seen_incoming.add(key)
        if key in by_key:
            duplicate += 1
            merged = dict(by_key[key])
            if item.get("meaning") and item.get("meaning") != "待补充":
                merged["meaning"] = item["meaning"]
            merged["source"] = item.get("source") or merged.get("source") or "import"
            merged["updated_at"] = datetime.now().isoformat(timespec="seconds")
            incoming_order.append(merged)
        else:
            added += 1
            incoming_order.append(item)
    remaining = [item for item in current if wordbook_key(item) not in seen_incoming]
    save_wordbook(incoming_order + remaining)
    return {"added": added, "duplicate": duplicate, "total": len(incoming_order)}


def decode_text_bytes(raw):
    for encoding in ("utf-8-sig", "utf-8", "gb18030", "gbk"):
        try:
            return raw.decode(encoding)
        except Exception:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_word_row(cells):
    cells = [str(cell or "").strip() for cell in cells if str(cell or "").strip()]
    if not cells:
        return None, False
    if len(cells) >= 2:
        item = build_wordbook_item(cells[0], " ".join(cells[1:]), source="import")
        return item, bool(item)
    return parse_word_line(cells[0])


def parse_word_line(line):
    text = re.sub(r"\s+", " ", str(line or "").replace("\u3000", " ")).strip()
    if not text:
        return None, False
    text = re.sub(r"^\s*\d+[.)、]\s*", "", text)
    if not text:
        return None, False
    pieces = re.split(r"[\t,，;；]", text, maxsplit=1)
    if len(pieces) == 2:
        item = build_wordbook_item(pieces[0], pieces[1], source="import")
        return item, bool(item)
    item = build_wordbook_item(text, "", source="import")
    if item and normalize_exam_word(text) == item["word"]:
        return item, True
    match = re.match(r"^([A-Za-z][A-Za-z'\-]*(?: [A-Za-z][A-Za-z'\-]*){0,4})\s+(.+)$", text)
    if not match:
        return None, True
    item = build_wordbook_item(match.group(1), match.group(2), source="import")
    return item, bool(item)


def parse_delimited_word_text(text):
    items = []
    failed = 0
    for line in (text or "").splitlines():
        item, attempted = parse_word_line(line)
        if item:
            items.append(item)
        elif attempted:
            failed += 1
    return items, failed


def parse_csv_word_text(text):
    items = []
    failed = 0
    for row in csv.reader((text or "").splitlines()):
        item, attempted = parse_word_row(row)
        if item:
            items.append(item)
        elif attempted:
            failed += 1
    return items, failed


def xml_local_name(tag):
    return str(tag).rsplit("}", 1)[-1]


def element_text(element):
    return "".join(child.text or "" for child in element.iter() if xml_local_name(child.tag) == "t")


def parse_xlsx_word_file(path):
    items = []
    failed = 0
    with zipfile.ZipFile(path, "r") as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [element_text(si) for si in root.iter() if xml_local_name(si.tag) == "si"]
        sheet_name = next(
            (name for name in archive.namelist() if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")),
            None,
        )
        if not sheet_name:
            return [], 0
        root = ET.fromstring(archive.read(sheet_name))
        for row in root.iter():
            if xml_local_name(row.tag) != "row":
                continue
            cells = []
            for cell in row:
                if xml_local_name(cell.tag) != "c":
                    continue
                cell_type = cell.attrib.get("t", "")
                value = ""
                if cell_type == "s":
                    raw = next((child.text for child in cell if xml_local_name(child.tag) == "v"), "")
                    try:
                        value = shared[int(raw)]
                    except Exception:
                        value = ""
                elif cell_type == "inlineStr":
                    value = element_text(cell)
                else:
                    value = next((child.text for child in cell if xml_local_name(child.tag) == "v"), "") or ""
                cells.append(value)
            item, attempted = parse_word_row(cells[:2])
            if item:
                items.append(item)
            elif attempted:
                failed += 1
    return items, failed


def parse_docx_word_file(path):
    with zipfile.ZipFile(path, "r") as archive:
        if "word/document.xml" not in archive.namelist():
            return [], 0
        root = ET.fromstring(archive.read("word/document.xml"))
    lines = []
    for paragraph in root.iter():
        if xml_local_name(paragraph.tag) == "p":
            text = element_text(paragraph).strip()
            if text:
                lines.append(text)
    return parse_delimited_word_text("\n".join(lines))


def parse_wordbook_file(path):
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return parse_csv_word_text(decode_text_bytes(path.read_bytes()))
    if suffix == ".txt":
        return parse_delimited_word_text(decode_text_bytes(path.read_bytes()))
    if suffix == ".xlsx":
        return parse_xlsx_word_file(path)
    if suffix == ".docx":
        return parse_docx_word_file(path)
    return [], 0


def parse_exam_word_line(line):
    match = re.match(r"^\s*\d+[.)、]\s*([A-Za-z][A-Za-z'\- ]*)\s*(.*)$", line or "")
    if not match:
        return None
    word = re.sub(r"\s+", " ", match.group(1)).strip()
    rest = re.sub(r"/[^/]+/", " ", match.group(2)).strip()
    chinese_match = re.search(r"[\u4e00-\u9fff].*$", rest)
    meaning = chinese_match.group(0).strip() if chinese_match else rest
    meaning = re.sub(r"^[a-zA-Z.&\s]+", "", meaning).strip(" .;；:：")
    meaning = re.sub(
        r"\s+\b(?:n|v|adj|adv|prep|conj|pron|num|art|vt|vi|abbr|phr|pl|interj)\.?(?:&(?:n|v|adj|adv)\.?)?\s*",
        "；",
        meaning,
        flags=re.IGNORECASE,
    ).strip("； ")
    meaning = re.sub(r"\s+", " ", meaning)
    if not word or not meaning:
        return None
    return {"word": word, "meaning": meaning}


def load_external_exam_words():
    seen = set()
    words = []
    for path in ENGLISH_WORD_SOURCE_CANDIDATES:
        try:
            if not path.exists():
                continue
            for line in path.read_text(encoding="utf-8-sig").splitlines():
                item = parse_exam_word_line(line)
                if not item:
                    continue
                key = item["word"].lower()
                if key in seen:
                    continue
                seen.add(key)
                words.append(item)
            if words:
                return words
        except Exception:
            continue
    return []


def exam_word_entries():
    global _EXAM_WORD_CACHE
    if _EXAM_WORD_CACHE is None:
        wordbook = ensure_wordbook_migrated()
        if wordbook:
            _EXAM_WORD_CACHE = [{"word": item["word"], "meaning": item["meaning"]} for item in wordbook]
        else:
            external = load_external_exam_words()
            if external:
                _EXAM_WORD_CACHE = external
            else:
                _EXAM_WORD_CACHE = [{"word": word, "meaning": meaning} for word, meaning, _freq in REDBOOK_WORDS]
    return _EXAM_WORD_CACHE


def math_formula_entries():
    items = []
    seen = set()
    for name, formula in list(MATH_FORMULAS) + EXTRA_MATH_FORMULAS:
        key = str(name).strip()
        if not key or key in seen:
            continue
        seen.add(key)
        items.append((key, str(formula).strip()))
    return items


def normalize_clipboard_text(text):
    value = (text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if len(value) > 4000:
        value = value[:4000] + "\n..."
    return value


def looks_sensitive_clipboard(text):
    value = (text or "").strip()
    if not value:
        return True
    lowered = value.lower()
    if any(mark in lowered for mark in ("password=", "authorization:", "bearer ", "api_key", "apikey", "secret_key")):
        return True
    if re.search(r"\bsk-[A-Za-z0-9_\-]{20,}\b", value):
        return True
    if len(value) >= 32 and re.fullmatch(r"[A-Fa-f0-9]{32,}", value):
        return True
    if len(value) >= 24 and re.fullmatch(r"[A-Za-z0-9_\-+/=]{24,}", value) and " " not in value:
        return True
    return False


def clipboard_preview(text, limit=90):
    value = " ".join((text or "").split())
    if len(value) <= limit:
        return value
    return value[:limit - 1] + "…"


def load_clipboard_history():
    items = load_json(CLIPBOARD_HISTORY, [])
    return items if isinstance(items, list) else []


def save_clipboard_history(items):
    save_json(CLIPBOARD_HISTORY, items[:80])


def add_clipboard_record(text):
    value = normalize_clipboard_text(text)
    if not value or looks_sensitive_clipboard(value):
        return False
    items = [item for item in load_clipboard_history() if item.get("text") != value]
    items.insert(
        0,
        {
            "id": str(time.time()),
            "text": value,
            "created_at": datetime.now().isoformat(timespec="seconds"),
        },
    )
    save_clipboard_history(items)
    return True


_CODEX_PROCESS_CACHE = {"checked_at": 0.0, "value": "Unknown"}
_VPN_STATUS_CACHE = {"checked_at": 0.0, "value": "Unknown"}


def detect_codex_process_cached(ttl=20):
    now = time.time()
    if now - float(_CODEX_PROCESS_CACHE.get("checked_at", 0.0)) < ttl:
        return _CODEX_PROCESS_CACHE.get("value", "Unknown")
    try:
        value = "Connected" if any(
            "codex" in (proc.info.get("name") or "").lower()
            for proc in psutil.process_iter(["name"])
        ) else "Disconnected"
    except Exception:
        value = "Unknown"
    _CODEX_PROCESS_CACHE["checked_at"] = now
    _CODEX_PROCESS_CACHE["value"] = value
    return value


def detect_vpn_status_cached(ttl=15):
    now = time.time()
    if now - float(_VPN_STATUS_CACHE.get("checked_at", 0.0)) < ttl:
        return _VPN_STATUS_CACHE.get("value", "Unknown")
    value = detect_vpn_status()
    _VPN_STATUS_CACHE["checked_at"] = now
    _VPN_STATUS_CACHE["value"] = value
    return value


def focus_dashboard_text(pet):
    if getattr(pet, "focus_active", False):
        return pet.focus_status_text()
    focus = int(pet.config.get("FocusMinutes", 50))
    rest = int(pet.config.get("RestMinutes", 10))
    subject = pet.config.get("Subject", "高数")
    return f"{subject} {focus} 分钟；休息 {rest} 分钟"


def config_for_backup(include_secrets=False):
    config = load_json(CONFIG, {})
    if not include_secrets:
        for key in SECRET_CONFIG_KEYS:
            if key in config:
                config[key] = ""
        for account in config.get("MailAccounts", []) or []:
            if isinstance(account, dict):
                account["Password"] = ""
    return config


def create_backup_archive(target_path, include_secrets=False, include_clipboard=True):
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "app": "AI萌宠桌面管家",
        "version": 1,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "include_secrets": bool(include_secrets),
        "include_clipboard": bool(include_clipboard),
        "files": [],
    }
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in BACKUP_DATA_FILES:
            if path == CLIPBOARD_HISTORY and not include_clipboard:
                continue
            if path == CONFIG:
                payload = json.dumps(config_for_backup(include_secrets), ensure_ascii=False, indent=2)
                archive.writestr(f"data/{path.name}", payload)
                manifest["files"].append(path.name)
                continue
            if path.exists():
                archive.write(path, f"data/{path.name}")
                manifest["files"].append(path.name)
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return target


def restore_backup_archive(source_path, restore_secrets=False):
    source = Path(source_path)
    allowed = {path.name: path for path in BACKUP_DATA_FILES}
    restored = []
    current_config = load_json(CONFIG, {})
    with zipfile.ZipFile(source, "r") as archive:
        names = set(archive.namelist())
        for name in sorted(names):
            if not name.startswith("data/"):
                continue
            filename = Path(name).name
            if filename not in allowed:
                continue
            raw = archive.read(name)
            target = allowed[filename]
            if target == CONFIG and not restore_secrets:
                try:
                    incoming = json.loads(raw.decode("utf-8-sig"))
                except Exception:
                    incoming = {}
                for key in SECRET_CONFIG_KEYS:
                    if current_config.get(key):
                        incoming[key] = current_config.get(key)
                current_accounts = {
                    (item.get("Host", "").lower(), item.get("User", "").lower()): item.get("Password", "")
                    for item in current_config.get("MailAccounts", []) or []
                    if isinstance(item, dict)
                }
                for item in incoming.get("MailAccounts", []) or []:
                    if not isinstance(item, dict):
                        continue
                    key = (item.get("Host", "").lower(), item.get("User", "").lower())
                    if current_accounts.get(key):
                        item["Password"] = current_accounts[key]
                raw = json.dumps(incoming, ensure_ascii=False, indent=2).encode("utf-8")
            target.write_bytes(raw)
            restored.append(filename)
    return restored


def portable_requirements_text():
    return "\n".join(
        [
            "PySide6",
            "psutil",
            "httpx",
            "pillow",
            "SpeechRecognition",
        ]
    ) + "\n"


def portable_start_here_bat():
    return (
        "@echo off\r\n"
        "setlocal\r\n"
        "cd /d \"%~dp0\"\r\n"
        "powershell.exe -NoProfile -ExecutionPolicy Bypass -File \"%~dp0Install-Nuomi.ps1\"\r\n"
        "pause\r\n"
    )


def portable_starter_bat():
    return (
        "@echo off\r\n"
        "set \"SCRIPT_DIR=%~dp0\"\r\n"
        "set \"PY=%SCRIPT_DIR%runtime\\python312\\pythonw.exe\"\r\n"
        "if not exist \"%PY%\" set \"PY=%LOCALAPPDATA%\\Programs\\Python\\Python312\\pythonw.exe\"\r\n"
        "if exist \"%SCRIPT_DIR%pet-shutdown.flag\" del \"%SCRIPT_DIR%pet-shutdown.flag\"\r\n"
        "start \"\" \"%PY%\" \"%SCRIPT_DIR%nuomi_watchdog.py\"\r\n"
    )


def portable_install_ps1():
    return r'''$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Log = Join-Path $Root "nuomi-install.log"
function Write-NuomiLog($Text) {
  $line = "[" + (Get-Date -Format "yyyy-MM-dd HH:mm:ss") + "] " + $Text
  Add-Content -LiteralPath $Log -Value $line -Encoding UTF8
  Write-Host $Text
}

Write-NuomiLog "Nuomi portable install started."
$portablePyBase = Join-Path $Root "runtime\python312"
$portablePython = Join-Path $portablePyBase "python.exe"
$portablePythonw = Join-Path $portablePyBase "pythonw.exe"
$systemPyBase = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312"
$systemPython = Join-Path $systemPyBase "python.exe"
$systemPythonw = Join-Path $systemPyBase "pythonw.exe"

if (Test-Path -LiteralPath $portablePythonw) {
  $python = $portablePython
  $pythonw = $portablePythonw
  Write-NuomiLog "Using bundled portable Python runtime."
} else {
  $python = $systemPython
  $pythonw = $systemPythonw
}

if (!(Test-Path -LiteralPath $pythonw)) {
  $installer = Join-Path $Root "python-3.12.10-amd64.exe"
  if (Test-Path -LiteralPath $installer) {
    Write-NuomiLog "Python not found. Installing bundled Python 3.12..."
    Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1" -Wait
    $python = $systemPython
    $pythonw = $systemPythonw
  }
}

if (!(Test-Path -LiteralPath $pythonw)) {
  Write-NuomiLog "Python was not found. Install Python 3.12, then run START_HERE.bat again."
  exit 1
}

Write-NuomiLog "Checking Python dependencies..."
& $python -c "import PySide6, psutil, httpx, PIL" 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-NuomiLog "Dependencies missing. Installing from requirements..."
  & $python -m pip install --upgrade pip
  $wheelhouse = Join-Path $Root "wheelhouse"
  if (Test-Path -LiteralPath $wheelhouse) {
    & $python -m pip install --no-index --find-links $wheelhouse -r (Join-Path $Root "requirements-nuomi.txt")
  } else {
    & $python -m pip install -r (Join-Path $Root "requirements-nuomi.txt")
  }
}

Write-NuomiLog "Checking GitHub for a newer Nuomi version..."
& $python (Join-Path $Root "ai_moe_pet.py") --update-before-start
if ($LASTEXITCODE -ne 0) {
  Write-NuomiLog "Online update check failed. The bundled version will still start."
}

$portableTessBase = Join-Path $Root "runtime\tesseract"
$portableTesseract = Join-Path $portableTessBase "tesseract.exe"
$tessInstaller = Join-Path $Root "tools\tesseract-ocr-w64-setup-5.5.0.20241111.exe"
$tessdata = Join-Path $Root "tools\tessdata"
if (!(Test-Path -LiteralPath $portableTesseract) -and (Test-Path -LiteralPath $tessInstaller)) {
  Write-NuomiLog "Installing bundled Tesseract OCR runtime..."
  New-Item -ItemType Directory -Force -Path $portableTessBase | Out-Null
  & $tessInstaller /S "/D=$portableTessBase"
}
if (Test-Path -LiteralPath $portableTesseract) {
  Write-NuomiLog "Tesseract OCR is available in portable runtime."
} else {
  Write-NuomiLog "Tesseract OCR runtime was not installed. OCR can be configured later in Settings."
}

$configPath = Join-Path $Root "pet-config.json"
if (Test-Path -LiteralPath $configPath) {
  try {
    $cfg = Get-Content -LiteralPath $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
    if (Test-Path -LiteralPath $portableTesseract) {
      $cfg | Add-Member -NotePropertyName "TesseractPath" -NotePropertyValue $portableTesseract -Force
    }
    if (Test-Path -LiteralPath $tessdata) {
      $cfg | Add-Member -NotePropertyName "TessdataPath" -NotePropertyValue $tessdata -Force
    }
    if (-not $cfg.OcrLanguage) {
      $cfg | Add-Member -NotePropertyName "OcrLanguage" -NotePropertyValue "chi_sim+eng" -Force
    }
    $cfg | ConvertTo-Json -Depth 30 | Set-Content -LiteralPath $configPath -Encoding UTF8
    Write-NuomiLog "OCR configuration updated."
  } catch {
    Write-NuomiLog "Could not update OCR configuration: $_"
  }
}

$startup = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
New-Item -ItemType Directory -Force -Path $startup | Out-Null
$startupVbs = Join-Path $startup "NuomiDesktopPet.vbs"
$starter = Join-Path $Root "start_ai_moe_pet.bat"
$vbs = "Set shell = CreateObject(""WScript.Shell"")`r`nshell.Run Chr(34) & ""$starter"" & Chr(34), 0, False`r`n"
[System.IO.File]::WriteAllText($startupVbs, $vbs, [System.Text.Encoding]::Default)

$old = @("AiMoePet.lnk","AiMoePet.bat","AiMoePet.cmd","AiMoePet.vbs","NuomiDesktopPet.bat","NuomiDesktopPet.cmd")
foreach ($name in $old) {
  $path = Join-Path $startup $name
  if (Test-Path -LiteralPath $path) { Remove-Item -LiteralPath $path -Force }
}

Write-NuomiLog "Starting Nuomi..."
Start-Process -FilePath $starter -WorkingDirectory $Root -WindowStyle Hidden
Write-NuomiLog "Done. Nuomi will also start automatically after reboot."
'''


def portable_readme_text(include_secrets=False):
    secret_note = (
        "This package includes AI Key and mail authorization code, so AI and mail can work directly on the new laptop."
        if include_secrets
        else "This package does not include AI Key or mail authorization code. Fill them in Settings on the new laptop."
    )
    return (
        "Nuomi Desktop Pet migration package\n\n"
        "How to use:\n"
        "1. Extract this zip to the new laptop. Recommended path: D:\\NuomiDesktopPet.\n"
        "2. Double-click START_HERE.bat.\n"
        "3. It will use the bundled Python runtime, check GitHub Releases for the newest version, repair autostart, and launch Nuomi.\n\n"
        "Included:\n"
        "- Main app, watchdog, launch scripts\n"
        "- Bundled Python runtime and Python installer fallback\n"
        "- Bundled Tesseract OCR installer and Chinese/English OCR language data\n"
        "- Nuomi assets and action pack\n"
        "- Settings, memory, chat history, study records, todos, calendar, mail state\n"
        "- Clipboard history if selected during export\n\n"
        "Online updates:\n"
        f"- Release source: https://github.com/{DEFAULT_UPDATE_REPO}/releases\n"
        "- START_HERE checks for a newer release before the first launch.\n"
        "- Later, open Settings > Advanced > Backup / Migration and click Check online update.\n"
        "- Program updates never overwrite pet-config.json, mail credentials, chat history, clipboard history, or study data.\n\n"
        "OCR:\n"
        "- START_HERE.bat installs the bundled Tesseract runtime into runtime\\tesseract when needed.\n"
        "- Chinese and English OCR data are included under tools\\tessdata.\n\n"
        f"Sensitive data: {secret_note}\n\n"
        "If launch fails, open nuomi-install.log in this folder.\n"
    )

def create_portable_package(target_path, include_secrets=False, include_clipboard=True):
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "app": "NuomiDesktopPet",
        "package_type": "portable_migration",
        "version": 1,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(BASE),
        "include_secrets": bool(include_secrets),
        "include_clipboard": bool(include_clipboard),
        "include_python_runtime": False,
        "include_tesseract_installer": (BASE / "tools" / "tesseract-ocr-w64-setup-5.5.0.20241111.exe").exists(),
        "include_tessdata": LOCAL_TESSDATA_DIR.exists(),
        "files": [],
    }
    data_names = {path.name for path in BACKUP_DATA_FILES}
    skip_dirs = {
        "__pycache__",
        "backups",
        "screenshots",
        "updates",
        "dist",
        "migration-test",
        ".git",
        ".agents",
        ".codex",
        ".claude",
    }
    skip_files = {"pet-runtime.log", "pet-shutdown.flag", "python-install.log", "start_ai_moe_pet.bat"}
    python_runtime = Path(sys.prefix)

    def should_skip(path):
        rel_parts = set(path.relative_to(BASE).parts)
        if rel_parts & skip_dirs:
            return True
        if path.name in skip_files or path.suffix.lower() in {".pyc", ".pyo"}:
            return True
        if path.name.startswith("ui_audit_"):
            return True
        if path.name in data_names:
            return True
        return False

    def should_skip_runtime(path):
        parts = {part.lower() for part in path.parts}
        if "__pycache__" in parts:
            return True
        if path.suffix.lower() in {".pyc", ".pyo"}:
            return True
        return False

    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in BASE.rglob("*"):
            if not path.is_file() or should_skip(path):
                continue
            rel = path.relative_to(BASE).as_posix()
            archive.write(path, rel)
            manifest["files"].append(rel)

        if python_runtime.exists():
            manifest["include_python_runtime"] = True
            for path in python_runtime.rglob("*"):
                if not path.is_file() or should_skip_runtime(path):
                    continue
                rel = "runtime/python312/" + path.relative_to(python_runtime).as_posix()
                archive.write(path, rel)
                manifest["files"].append(rel)

        for path in BACKUP_DATA_FILES:
            if path == CLIPBOARD_HISTORY and not include_clipboard:
                continue
            if path == CONFIG:
                payload = json.dumps(config_for_backup(include_secrets), ensure_ascii=False, indent=2)
                archive.writestr(path.name, payload)
                manifest["files"].append(path.name)
                continue
            if path.exists():
                archive.write(path, path.name)
                manifest["files"].append(path.name)

        archive.writestr("requirements-nuomi.txt", portable_requirements_text())
        archive.writestr("start_ai_moe_pet.bat", portable_starter_bat())
        archive.writestr("START_HERE.bat", portable_start_here_bat())
        archive.writestr("Install-Nuomi.ps1", portable_install_ps1())
        archive.writestr("MIGRATION_README.txt", portable_readme_text(include_secrets))
        manifest["files"].extend(
            [
                "requirements-nuomi.txt",
                "start_ai_moe_pet.bat",
                "START_HERE.bat",
                "Install-Nuomi.ps1",
                "MIGRATION_README.txt",
            ]
        )
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return target


def version_tuple(value):
    numbers = [int(part) for part in re.findall(r"\d+", str(value or ""))]
    return tuple((numbers + [0, 0, 0])[:3])


def update_repo_name(config=None):
    selected = str((config or {}).get("UpdateRepo", DEFAULT_UPDATE_REPO)).strip()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", selected):
        return DEFAULT_UPDATE_REPO
    return selected


def update_public_files(include_assets=False):
    paths = []
    for name in ("ai_moe_pet.py", "_kaoyan_data.py", "nuomi_watchdog.py", "README.md"):
        path = BASE / name
        if path.is_file():
            paths.append(path)
    if include_assets and (BASE / "assets").exists():
        paths.extend(path for path in (BASE / "assets").rglob("*") if path.is_file())
    health_check = BASE / "tools" / "pet_health_check.py"
    if health_check.is_file():
        paths.append(health_check)
    return sorted(set(paths), key=lambda item: item.relative_to(BASE).as_posix())


def update_package_bytes(path, rel, version):
    raw = path.read_bytes()
    if rel == "ai_moe_pet.py" and str(version) != APP_VERSION:
        text = raw.decode("utf-8")
        updated = re.sub(
            r'^APP_VERSION\s*=\s*"[^"]+"',
            f'APP_VERSION = "{version}"',
            text,
            count=1,
            flags=re.MULTILINE,
        )
        raw = updated.encode("utf-8")
    return raw


def create_update_package(target_path, version=APP_VERSION, include_assets=False):
    target = Path(target_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    entries = []
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in update_public_files(include_assets=include_assets):
            rel = path.relative_to(BASE).as_posix()
            raw = update_package_bytes(path, rel, version)
            archive.writestr(rel, raw)
            entries.append(
                {
                    "path": rel,
                    "size": len(raw),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                }
            )
        manifest = {
            "app": "NuomiDesktopPet",
            "package_type": "online_update",
            "version": str(version),
            "include_assets": bool(include_assets),
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "files": entries,
        }
        archive.writestr("update-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    return target


def latest_github_release(repo=None):
    repo = repo or DEFAULT_UPDATE_REPO
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"NuomiDesktopPet/{APP_VERSION}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    release = None
    errors = []
    for attempt in range(3):
        try:
            response = httpx.get(
                url,
                headers=headers,
                follow_redirects=True,
                timeout=httpx.Timeout(connect=15, read=30, write=15, pool=15),
            )
            response.raise_for_status()
            release = response.json()
            break
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
            if attempt < 2:
                time.sleep(1.5 * (attempt + 1))
    if release is None:
        raise RuntimeError("GitHub 最新版本查询失败；" + "；".join(errors))
    assets = release.get("assets", []) or []
    update_assets = [
        item
        for item in assets
        if str(item.get("name", "")).lower().startswith("nuomi-update-")
        and str(item.get("name", "")).lower().endswith(".zip")
    ]
    if not update_assets:
        raise RuntimeError("最新版没有找到 nuomi-update-*.zip")
    asset = sorted(update_assets, key=lambda item: item.get("created_at", ""), reverse=True)[0]
    return {
        "repo": repo,
        "version": str(release.get("tag_name", "")).lstrip("vV") or "0.0.0",
        "name": str(release.get("name", "") or release.get("tag_name", "")),
        "notes": str(release.get("body", "") or ""),
        "url": str(release.get("html_url", "")),
        "asset_name": str(asset.get("name", "")),
        "asset_url": str(asset.get("browser_download_url", "")),
        "asset_api_url": str(asset.get("url", "")),
        "asset_size": int(asset.get("size", 0) or 0),
        "asset_digest": str(asset.get("digest", "") or ""),
    }


def validate_and_extract_update(archive_path, stage_dir):
    archive_path = Path(archive_path)
    stage_dir = Path(stage_dir)
    protected = {path.name.casefold() for path in BACKUP_DATA_FILES}
    protected.update(
        {
            "pet-runtime.log",
            "pet-update.log",
            "pet-shutdown.flag",
            "pet-update.lock",
            "start_ai_moe_pet.bat",
            "install-nuomi.ps1",
            "start_here.bat",
        }
    )
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if "update-manifest.json" not in names:
            raise RuntimeError("更新包缺少 update-manifest.json")
        manifest = json.loads(archive.read("update-manifest.json").decode("utf-8-sig"))
        files = manifest.get("files", [])
        expected = {str(item.get("path", "")).replace("\\", "/") for item in files}
        actual = set(names) - {"update-manifest.json"}
        if not expected or actual != expected:
            raise RuntimeError("更新包文件清单不一致")
        required = {"ai_moe_pet.py", "_kaoyan_data.py", "nuomi_watchdog.py"}
        if not required.issubset(expected):
            raise RuntimeError("更新包缺少桌宠核心文件")
        for item in files:
            rel = str(item.get("path", "")).replace("\\", "/")
            path = Path(rel)
            if (
                not rel
                or path.is_absolute()
                or ".." in path.parts
                or path.parts[0].casefold() in {"runtime", "updates", "backups", ".git"}
                or path.name.casefold() in protected
            ):
                raise RuntimeError(f"更新包包含不允许覆盖的路径：{rel}")
            raw = archive.read(rel)
            if len(raw) != int(item.get("size", -1)):
                raise RuntimeError(f"更新文件大小校验失败：{rel}")
            if hashlib.sha256(raw).hexdigest().lower() != str(item.get("sha256", "")).lower():
                raise RuntimeError(f"更新文件哈希校验失败：{rel}")
            destination = stage_dir / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        (stage_dir / "update-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return manifest


def download_latest_update(config=None):
    repo = update_repo_name(config)
    release = latest_github_release(repo)
    if version_tuple(release["version"]) <= version_tuple(APP_VERSION):
        return {"available": False, "release": release, "current_version": APP_VERSION}
    UPDATE_DIR.mkdir(exist_ok=True)
    download = UPDATE_DIR / release["asset_name"]
    temp_download = download.with_suffix(download.suffix + ".part")
    errors = []
    downloaded = False
    timeout = httpx.Timeout(connect=20, read=120, write=30, pool=20)
    asset_api_url = release.get("asset_api_url", "")
    asset_size = int(release.get("asset_size", 0) or 0)
    if asset_api_url and asset_size > 0:
        try:
            chunk_size = 4 * 1024 * 1024
            temp_download.unlink(missing_ok=True)
            with temp_download.open("wb") as handle:
                for start in range(0, asset_size, chunk_size):
                    end = min(asset_size - 1, start + chunk_size - 1)
                    chunk = None
                    chunk_errors = []
                    for attempt in range(3):
                        try:
                            response = httpx.get(
                                asset_api_url,
                                headers={
                                    "Accept": "application/octet-stream",
                                    "User-Agent": f"NuomiDesktopPet/{APP_VERSION}",
                                    "X-GitHub-Api-Version": "2022-11-28",
                                    "Range": f"bytes={start}-{end}",
                                },
                                follow_redirects=True,
                                timeout=timeout,
                            )
                            response.raise_for_status()
                            content_type = response.headers.get("content-type", "").lower()
                            if "application/json" in content_type:
                                raise RuntimeError("GitHub 返回了资源元数据而不是更新文件")
                            chunk = response.content
                            expected = end - start + 1
                            if response.status_code == 206 and len(chunk) != expected:
                                raise RuntimeError(f"分块大小不完整：{len(chunk)}/{expected}")
                            if response.status_code == 200 and len(chunk) == asset_size and start == 0:
                                handle.write(chunk)
                                start = asset_size
                                break
                            if response.status_code != 206:
                                raise RuntimeError(f"GitHub 不支持分块下载：HTTP {response.status_code}")
                            break
                        except Exception as exc:
                            chunk = None
                            chunk_errors.append(f"{type(exc).__name__}: {exc}")
                            if attempt < 2:
                                time.sleep(1.5 * (attempt + 1))
                    if chunk is None:
                        raise RuntimeError(
                            f"分块 {start}-{end} 下载失败；" + "；".join(chunk_errors)
                        )
                    if response.status_code == 200 and len(chunk) == asset_size and start == 0:
                        break
                    handle.write(chunk)
            downloaded = True
        except Exception as exc:
            errors.append(f"{asset_api_url}: {type(exc).__name__}: {exc}")
    if not downloaded:
        source_url = release["asset_url"]
        temp_download.unlink(missing_ok=True)
        try:
            with httpx.stream(
                "GET",
                source_url,
                headers={
                    "Accept": "application/octet-stream",
                    "User-Agent": f"NuomiDesktopPet/{APP_VERSION}",
                },
                follow_redirects=True,
                timeout=timeout,
            ) as response:
                response.raise_for_status()
                content_type = response.headers.get("content-type", "").lower()
                if "application/json" in content_type:
                    raise RuntimeError("GitHub 返回了资源元数据而不是更新文件")
                with temp_download.open("wb") as handle:
                    for chunk in response.iter_bytes(1024 * 1024):
                        handle.write(chunk)
            downloaded = temp_download.stat().st_size > 0
        except Exception as exc:
            errors.append(f"{source_url}: {type(exc).__name__}: {exc}")
    if not downloaded:
        temp_download.unlink(missing_ok=True)
        raise RuntimeError("GitHub 更新包下载失败；" + "；".join(errors))
    if release["asset_size"] and temp_download.stat().st_size != release["asset_size"]:
        temp_download.unlink(missing_ok=True)
        raise RuntimeError("更新包下载大小不完整")
    digest = release.get("asset_digest", "")
    if digest.lower().startswith("sha256:"):
        expected_digest = digest.split(":", 1)[1].strip().lower()
        actual_digest = hashlib.sha256(temp_download.read_bytes()).hexdigest().lower()
        if actual_digest != expected_digest:
            temp_download.unlink(missing_ok=True)
            raise RuntimeError("更新包与 GitHub SHA-256 摘要不一致")
    temp_download.replace(download)
    stage = UPDATE_DIR / f"staged-{release['version']}"
    if stage.exists():
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    manifest = validate_and_extract_update(download, stage)
    if version_tuple(manifest.get("version")) != version_tuple(release["version"]):
        shutil.rmtree(stage, ignore_errors=True)
        raise RuntimeError("Release 版本与更新包版本不一致")
    return {
        "available": True,
        "release": release,
        "current_version": APP_VERSION,
        "stage": str(stage),
    }


def append_update_log(message):
    try:
        with UPDATE_LOG.open("a", encoding="utf-8") as handle:
            handle.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def apply_staged_update(stage_dir, target_root=None):
    stage = Path(stage_dir).resolve()
    target_root = Path(target_root).resolve() if target_root else BASE
    manifest_path = stage / "update-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    files = [str(item.get("path", "")).replace("\\", "/") for item in manifest.get("files", [])]
    rollback = target_root / "updates" / f"rollback-{datetime.now():%Y%m%d-%H%M%S}"
    replaced = []
    try:
        for rel in files:
            source = stage / rel
            target = target_root / rel
            if not source.is_file():
                raise RuntimeError(f"暂存更新文件缺失：{rel}")
            if target.exists():
                backup = rollback / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(target, backup)
            target.parent.mkdir(parents=True, exist_ok=True)
            temp_target = target.with_name(target.name + ".nuomi-new")
            shutil.copy2(source, temp_target)
            os.replace(temp_target, target)
            replaced.append(rel)
        append_update_log(f"updated to {manifest.get('version')} ({len(replaced)} files)")
        return str(manifest.get("version", ""))
    except Exception:
        for rel in reversed(replaced):
            backup = rollback / rel
            target = BASE / rel
            try:
                if backup.exists():
                    shutil.copy2(backup, target)
            except Exception:
                pass
        raise


def schedule_staged_update(stage_dir):
    UPDATE_LOCK.write_text(str(stage_dir), encoding="utf-8")
    creation_flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            "--wait-and-apply-update",
            str(os.getpid()),
            str(stage_dir),
        ],
        cwd=str(BASE),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=creation_flags,
    )


def run_update_cli():
    args = sys.argv[1:]
    if "--update-before-start" in args:
        try:
            result = download_latest_update(load_config())
            if result.get("available"):
                version = apply_staged_update(result["stage"])
                append_update_log(f"pre-start update applied: {version}")
            else:
                append_update_log("pre-start update: already current")
            return 0
        except Exception as exc:
            append_update_log(f"pre-start update failed: {type(exc).__name__}: {exc}")
            return 1
    if "--wait-and-apply-update" in args:
        index = args.index("--wait-and-apply-update")
        try:
            pid = int(args[index + 1])
            stage = args[index + 2]
        except (ValueError, IndexError):
            return 2
        try:
            for _ in range(60):
                if not psutil.pid_exists(pid):
                    break
                time.sleep(0.5)
            version = apply_staged_update(stage)
            append_update_log(f"interactive update applied: {version}")
            return_code = 0
        except Exception as exc:
            append_update_log(f"interactive update failed: {type(exc).__name__}: {exc}")
            return_code = 1
        finally:
            UPDATE_LOCK.unlink(missing_ok=True)
            try:
                subprocess.Popen(
                    [str(BASE / "start_ai_moe_pet.bat")],
                    cwd=str(BASE),
                    shell=True,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
            except Exception:
                pass
        return return_code
    return None


def append_runtime_log(message):
    try:
        with RUNTIME_LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"[{datetime.now().isoformat(timespec='seconds')}] {message}\n")
    except Exception:
        pass


def install_exception_logger():
    def handle_exception(exc_type, exc, tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc, tb)
            return
        detail = "".join(traceback.format_exception(exc_type, exc, tb)).strip()
        append_runtime_log("uncaught exception:\n" + detail)
        try:
            sys.__excepthook__(exc_type, exc, tb)
        except Exception:
            pass

    sys.excepthook = handle_exception


class WheelValueGuard(QObject):
    guarded_types = (QSpinBox, QComboBox, QDateTimeEdit, QFontComboBox)

    def eventFilter(self, obj, event):
        if event.type() != QEvent.Type.Wheel or not isinstance(obj, self.guarded_types):
            return super().eventFilter(obj, event)
        if event.modifiers() & Qt.ControlModifier:
            return super().eventFilter(obj, event)
        if isinstance(obj, QComboBox):
            try:
                if obj.view().isVisible():
                    return super().eventFilter(obj, event)
            except Exception:
                pass
        self.scroll_parent_area(obj, event)
        event.accept()
        return True

    def scroll_parent_area(self, widget, event):
        parent = widget.parent()
        while parent is not None and not isinstance(parent, QAbstractScrollArea):
            parent = parent.parent()
        if parent is None:
            return
        bar = parent.verticalScrollBar()
        if bar is None or bar.maximum() <= bar.minimum():
            return
        pixel_delta = event.pixelDelta().y()
        if pixel_delta:
            amount = pixel_delta
        else:
            step = max(20, bar.singleStep() * 3)
            amount = int(event.angleDelta().y() / 120 * step)
        if amount:
            bar.setValue(bar.value() - amount)


WHEEL_VALUE_GUARD = None


def install_wheel_value_guard(app):
    global WHEEL_VALUE_GUARD
    if WHEEL_VALUE_GUARD is None:
        WHEEL_VALUE_GUARD = WheelValueGuard(app)
        app.installEventFilter(WHEEL_VALUE_GUARD)


def git_command(args, timeout=120, check=True):
    completed = subprocess.run(
        ["git", *args],
        cwd=str(BASE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform.startswith("win") else 0,
    )
    if check and completed.returncode != 0:
        output = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(output or f"git {' '.join(args)} 失败")
    return completed


def gh_command(args, timeout=120, check=True):
    gh = shutil.which("gh")
    if not gh:
        raise RuntimeError("没有找到 GitHub CLI（gh）。代码可以推送，但另一台电脑要检测更新，需要安装并登录 gh 后发布 Release。")
    completed = subprocess.run(
        [gh, *args],
        cwd=str(BASE),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if sys.platform.startswith("win") else 0,
    )
    if check and completed.returncode != 0:
        output = (completed.stderr or completed.stdout or "").strip()
        raise RuntimeError(output or f"gh {' '.join(args)} 失败")
    return completed


def github_repo_from_remote(remote_url):
    value = str(remote_url or "").strip()
    patterns = [
        r"github\.com[:/](?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
        r"^https?://github\.com/(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+?)(?:\.git)?/?$",
    ]
    for pattern in patterns:
        match = re.search(pattern, value)
        if match:
            return f"{match.group('owner')}/{match.group('repo')}"
    return ""


def next_github_release_version(repo):
    versions = [version_tuple(APP_VERSION)]
    result = gh_command(
        ["release", "list", "--repo", repo, "--limit", "30", "--json", "tagName"],
        timeout=60,
        check=False,
    )
    if result.returncode == 0:
        try:
            for item in json.loads(result.stdout or "[]"):
                tag = str(item.get("tagName", "")).lstrip("vV")
                if tag:
                    versions.append(version_tuple(tag))
        except Exception:
            pass
    major, minor, patch = max(versions)
    return f"{major}.{minor}.{patch + 1}"


def publish_github_update_release(repo, branch, commit_hash):
    version = next_github_release_version(repo)
    UPDATE_DIR.mkdir(exist_ok=True)
    package = UPDATE_DIR / f"nuomi-update-{version}.zip"
    create_update_package(package, version=version, include_assets=True)
    tag = f"v{version}"
    notes = (
        f"糯米手动上传发布。\n\n"
        f"- 分支：{branch}\n"
        f"- 提交：{commit_hash}\n"
        f"- 更新包：{package.name}\n"
        f"- 另一台电脑可在备份 / 迁移里点击“检查联网更新”。"
    )
    gh_command(
        [
            "release",
            "create",
            tag,
            str(package),
            "--repo",
            repo,
            "--target",
            branch,
            "--title",
            f"糯米 {version}",
            "--notes",
            notes,
            "--latest",
        ],
        timeout=300,
    )
    return {
        "ok": True,
        "repo": repo,
        "version": version,
        "tag": tag,
        "package": str(package),
    }


def github_backup_is_blocked_path(value):
    path = str(value or "").replace("\\", "/").strip("/")
    if not path:
        return False
    parts = [part.casefold() for part in path.split("/") if part]
    if not parts:
        return False
    if parts[0] in GITHUB_BACKUP_BLOCKED_DIRS:
        return True
    name = parts[-1]
    if name in GITHUB_BACKUP_BLOCKED_NAMES:
        return True
    if name.endswith(".log") or name.endswith(".pyc"):
        return True
    if name.startswith("python-") and name.endswith(".exe"):
        return True
    if name.startswith("ui_audit_") and name.endswith(".png"):
        return True
    if len(parts) >= 2 and parts[0] == "tools" and name.endswith(".exe"):
        return True
    return False


def manual_github_backup(publish_update=False):
    if not (BASE / ".git").exists():
        raise RuntimeError("当前项目不是 Git 仓库，无法上传到 GitHub。")
    remote_result = git_command(["remote", "get-url", "--push", "origin"], timeout=20)
    remote_url = remote_result.stdout.strip()
    if not remote_url:
        raise RuntimeError("没有配置 GitHub 远程仓库 origin。")
    branch_result = git_command(["branch", "--show-current"], timeout=20)
    branch = branch_result.stdout.strip()
    if not branch:
        raise RuntimeError("当前不是普通分支，无法自动上传。")

    tracked_result = git_command(["ls-files"], timeout=30)
    blocked_tracked = [
        item for item in tracked_result.stdout.splitlines()
        if github_backup_is_blocked_path(item)
    ]
    if blocked_tracked:
        preview = "、".join(blocked_tracked[:6])
        more = f" 等 {len(blocked_tracked)} 个文件" if len(blocked_tracked) > 6 else ""
        raise RuntimeError(f"检测到敏感文件已经被 Git 跟踪：{preview}{more}。请先移出仓库后再上传。")

    name_ready = bool(git_command(["config", "user.name"], check=False, timeout=10).stdout.strip())
    mail_ready = bool(git_command(["config", "user.email"], check=False, timeout=10).stdout.strip())
    if not (name_ready and mail_ready):
        raise RuntimeError("Git 用户名或邮箱未配置，无法创建提交。请先配置 git user.name 和 user.email。")

    git_command(["add", "-A", "--", "."], timeout=120)
    staged_result = git_command(["diff", "--cached", "--name-only"], timeout=30)
    staged_files = [line.strip() for line in staged_result.stdout.splitlines() if line.strip()]
    blocked_staged = [item for item in staged_files if github_backup_is_blocked_path(item)]
    if blocked_staged:
        git_command(["restore", "--staged", "--", *blocked_staged], timeout=30, check=False)
        preview = "、".join(blocked_staged[:6])
        more = f" 等 {len(blocked_staged)} 个文件" if len(blocked_staged) > 6 else ""
        raise RuntimeError(f"本次上传被拦截：这些文件看起来像个人数据或敏感文件：{preview}{more}。")

    committed = False
    commit_message = f"糯米手动备份 {datetime.now():%Y-%m-%d %H:%M}"
    if staged_files:
        git_command(["commit", "-m", commit_message], timeout=120)
        committed = True
    commit_hash = git_command(["rev-parse", "--short", "HEAD"], timeout=20).stdout.strip()
    push_result = git_command(["push", "origin", branch], timeout=300)
    push_output = (push_result.stdout or push_result.stderr or "").strip()
    update_release = {"requested": bool(publish_update), "ok": False}
    if publish_update:
        release_repo = update_repo_name(load_config())
        origin_repo = github_repo_from_remote(remote_url)
        if origin_repo and release_repo == DEFAULT_UPDATE_REPO:
            release_repo = origin_repo
        try:
            update_release = publish_github_update_release(release_repo, branch, commit_hash)
            update_release["requested"] = True
        except Exception as exc:
            update_release = {
                "requested": True,
                "ok": False,
                "repo": release_repo,
                "error": str(exc),
            }
    append_runtime_log(f"github backup pushed branch={branch} commit={commit_hash} files={len(staged_files)}")
    return {
        "remote": remote_url,
        "branch": branch,
        "commit": commit_hash,
        "committed": committed,
        "files": staged_files,
        "push_output": push_output,
        "update_release": update_release,
    }


def pythonw_executable():
    current = Path(sys.executable)
    if current.name.lower() == "python.exe":
        candidate = current.with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    if current.name.lower() == "pythonw.exe" and current.exists():
        return str(current)
    candidate = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python" / "Python312" / "pythonw.exe"
    if candidate.exists():
        return str(candidate)
    return sys.executable


def process_cmdline_contains(text):
    needle = str(text).lower()
    for proc in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            cmdline = " ".join(proc.info.get("cmdline") or [])
        except Exception:
            cmdline = ""
        if needle in cmdline.lower():
            return True
    return False


def is_watchdog_running():
    return process_cmdline_contains(WATCHDOG.name)


def clear_shutdown_flag():
    try:
        if SHUTDOWN_FLAG.exists():
            SHUTDOWN_FLAG.unlink()
    except Exception:
        pass


def write_shutdown_flag():
    try:
        SHUTDOWN_FLAG.write_text(datetime.now().isoformat(timespec="seconds"), encoding="utf-8")
    except Exception:
        pass


def ensure_watchdog_running(config):
    if not config.get("WatchdogEnabled", True) or not sys.platform.startswith("win"):
        return False
    if not WATCHDOG.exists() or is_watchdog_running():
        return False
    clear_shutdown_flag()
    try:
        subprocess.Popen(
            [pythonw_executable(), str(WATCHDOG)],
            cwd=str(BASE),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=0x08000000 if sys.platform.startswith("win") else 0,
        )
        append_runtime_log("watchdog started by pet")
        return True
    except Exception as exc:
        append_runtime_log(f"watchdog start failed: {exc}")
        return False


def sync_watchdog(config):
    if config.get("WatchdogEnabled", True):
        return ensure_watchdog_running(config)
    write_shutdown_flag()
    return False


def startup_entry_payload():
    script = str(STARTER_SCRIPT)
    return (
        'Set shell = CreateObject("WScript.Shell")\r\n'
        f'shell.Run Chr(34) & "{script}" & Chr(34), 0, False\r\n'
    )


def legacy_aimoepet_payload():
    script = str(STARTER_SCRIPT)
    cwd = str(BASE)
    return (
        'Set shell = CreateObject("WScript.Shell")\r\n'
        f'shell.CurrentDirectory = "{cwd}"\r\n'
        f'shell.Run Chr(34) & "{script}" & Chr(34), 0, False\r\n'
    )


def remove_legacy_run_startup_values():
    removed = []
    if not sys.platform.startswith("win") or winreg is None:
        return removed
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY_PATH, 0, winreg.KEY_SET_VALUE) as key:
            for name in LEGACY_RUN_VALUE_NAMES:
                try:
                    winreg.DeleteValue(key, name)
                    removed.append(name)
                    append_runtime_log(f"legacy run startup value removed: {name}")
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    append_runtime_log(f"legacy run startup value remove failed: {name} {exc}")
    except OSError as exc:
        append_runtime_log(f"legacy run startup key open failed: {exc}")
    return removed


def cmd_text_encoding():
    return "mbcs" if sys.platform.startswith("win") else "utf-8"


def read_text_fallback(path):
    for encoding in (cmd_text_encoding(), "utf-8", "utf-8-sig"):
        try:
            return path.read_text(encoding=encoding, errors="ignore")
        except Exception:
            continue
    return ""


def repair_startup_entry(prune_duplicates=True):
    STARTUP_DIR.mkdir(parents=True, exist_ok=True)
    STARTUP_BAT.write_text(startup_entry_payload(), encoding=cmd_text_encoding())
    remove_legacy_run_startup_values()
    try:
        LEGACY_AIMOEPET_DIR.mkdir(parents=True, exist_ok=True)
        LEGACY_AIMOEPET_VBS.write_text(legacy_aimoepet_payload(), encoding=cmd_text_encoding())
    except Exception as exc:
        append_runtime_log(f"legacy AiMoePet launcher repair failed: {exc}")
    if prune_duplicates:
        for path in matching_startup_entries():
            try:
                if path.resolve() == STARTUP_BAT.resolve():
                    continue
                path.unlink()
                append_runtime_log(f"duplicate startup entry removed: {path}")
            except Exception as exc:
                append_runtime_log(f"duplicate startup entry remove failed: {path} {exc}")
    append_runtime_log(f"startup entry repaired: {STARTUP_BAT}")
    return STARTUP_BAT


def remove_startup_entries():
    removed = []
    for name in remove_legacy_run_startup_values():
        removed.append(f"HKCU Run\\{name}")
    for path in matching_startup_entries():
        try:
            path.unlink()
            removed.append(path)
            append_runtime_log(f"startup entry removed: {path}")
        except Exception as exc:
            append_runtime_log(f"startup entry remove failed: {path} {exc}")
    return removed


def startup_entry_installed():
    if not STARTUP_BAT.exists():
        return False
    content = read_text_fallback(STARTUP_BAT)
    return str(STARTER_SCRIPT) in content


def legacy_aimoepet_launcher_ok():
    if not LEGACY_AIMOEPET_VBS.exists():
        return False
    content = read_text_fallback(LEGACY_AIMOEPET_VBS)
    return str(STARTER_SCRIPT) in content and str(BASE) in content


def matching_startup_entries():
    if not STARTUP_DIR.exists():
        return []
    hits = []
    legacy_names = {
        "aimoepet.lnk",
        "aimoepet.bat",
        "aimoepet.cmd",
        "aimoepet.vbs",
        "nuomidesktoppet.bat",
        "nuomidesktoppet.cmd",
    }
    for path in STARTUP_DIR.iterdir():
        lower_name = path.name.lower()
        if lower_name in legacy_names:
            hits.append(path)
            continue
        if path.suffix.lower() not in {".bat", ".cmd", ".vbs"}:
            continue
        content = read_text_fallback(path).lower()
        if any(name.lower() in content for name in ("ai_moe_pet.py", "start_ai_moe_pet.bat", "nuomi_watchdog.py")):
            hits.append(path)
    return hits


def ensure_startup_entry(config):
    if not sys.platform.startswith("win") or not config.get("AutoStart", True):
        return False
    try:
        remove_legacy_run_startup_values()
        matches = matching_startup_entries()
        if not startup_entry_installed() or not legacy_aimoepet_launcher_ok() or len(matches) > 1:
            repair_startup_entry(prune_duplicates=True)
            return True
    except Exception as exc:
        append_runtime_log(f"startup ensure failed: {exc}")
    return False


def sync_startup_entry(config):
    if not sys.platform.startswith("win"):
        return False
    if config.get("AutoStart", True):
        return ensure_startup_entry(config)
    remove_startup_entries()
    return True


def acquire_single_instance():
    global SINGLE_INSTANCE_MUTEX
    if kernel32 is None:
        return True
    SINGLE_INSTANCE_MUTEX = kernel32.CreateMutexW(None, True, "Local\\AiMoePetDesktopPet")
    return kernel32.GetLastError() != ERROR_ALREADY_EXISTS


def request_existing_instance_restore():
    try:
        RESTORE_FLAG.write_text(datetime.now().isoformat(), encoding="utf-8")
    except Exception as exc:
        append_runtime_log(f"restore request write failed: {exc}")


def open_in_edge(url):
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", "msedge", url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except Exception:
        webbrowser.open(url)


def open_in_chrome(url):
    chrome_candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    try:
        chrome = next((str(path) for path in chrome_candidates if path.exists()), "chrome")
        subprocess.Popen(
            [chrome, url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=False,
        )
    except Exception:
        webbrowser.open(url)


def open_mail_url(provider, url=None):
    target = url or mail_inbox_url(provider)
    if provider == "gmail":
        open_in_chrome(target)
        return
    open_in_edge(target)


def unique_existing_paths(paths):
    unique = []
    seen = set()
    for path in paths:
        if not path:
            continue
        candidate = Path(path)
        key = str(candidate).casefold()
        if key in seen:
            continue
        seen.add(key)
        unique.append(candidate)
    return unique


def assistant_toolbox_root_candidates():
    candidates = [ASSISTANT_TOOLBOX_ROOT]
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        user = Path(userprofile)
        candidates.extend(
            [
                user / "OneDrive" / "文档" / "New project 3",
                user / "OneDrive" / "Documents" / "New project 3",
                user / "Documents" / "New project 3",
                user / "Desktop" / "New project 3",
            ]
        )
    candidates.extend([BASE, BASE.parent / "New project 3"])
    return unique_existing_paths(candidates)


def resolve_assistant_toolbox_root():
    for root in assistant_toolbox_root_candidates():
        if (root / "server.js").exists():
            return root
    return ASSISTANT_TOOLBOX_ROOT


def node_executable_candidates():
    candidates = []
    path_node = shutil.which("node")
    if path_node:
        candidates.append(Path(path_node))

    for env_name in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
        env_value = os.environ.get(env_name)
        if env_value:
            candidates.append(Path(env_value) / "nodejs" / "node.exe")

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        local_root = Path(local_app_data)
        candidates.extend(
            [
                local_root / "Programs" / "nodejs" / "node.exe",
                local_root / "nodejs" / "node.exe",
            ]
        )

    candidates.extend(
        [
            BUNDLED_NODE_EXE,
            BASE / "runtime" / "node" / "node.exe",
            BASE / "node" / "node.exe",
        ]
    )
    return unique_existing_paths(candidates)


def find_node_executable():
    for candidate in node_executable_candidates():
        if candidate.exists() and candidate.is_file():
            return str(candidate)
    return ""


def assistant_toolbox_running():
    try:
        response = httpx.get(f"{ASSISTANT_TOOLBOX_URL}/api/status", timeout=1.2)
        return response.status_code == 200
    except Exception:
        return False


def ensure_assistant_toolbox_server():
    if assistant_toolbox_running():
        return True, "工具箱服务已运行"
    toolbox_root = resolve_assistant_toolbox_root()
    toolbox_server = toolbox_root / "server.js"
    if not toolbox_server.exists():
        return False, f"找不到工具箱服务：{toolbox_server}"
    node = find_node_executable()
    if not node:
        return False, "找不到 Node.js，无法启动工具箱服务；请安装 Node 或保留 Codex 自带运行时"
    try:
        append_runtime_log(f"assistant toolbox start: node={node}; server={toolbox_server}")
        process = subprocess.Popen(
            [node, str(toolbox_server)],
            cwd=str(toolbox_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
        )
        for _ in range(20):
            time.sleep(0.25)
            if assistant_toolbox_running():
                return True, "工具箱服务已启动"
            if process.poll() is not None:
                append_runtime_log(f"assistant toolbox exited early: code={process.returncode}")
                break
        return False, "工具箱服务启动超时"
    except Exception as exc:
        append_runtime_log(f"assistant toolbox start failed: {exc}")
        return False, f"工具箱服务启动失败：{exc}"


def powershell_quote(value):
    return "'" + str(value).replace("'", "''") + "'"


def claude_code_profile():
    profile = {
        "installed": CLAUDE_CODE_EXE.exists(),
        "settings": CLAUDE_CODE_SETTINGS.exists(),
        "version": "",
        "provider": "未配置",
        "model": "未配置",
        "credential_ready": False,
    }
    if profile["installed"]:
        try:
            result = subprocess.run(
                [str(CLAUDE_CODE_EXE), "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=1.2,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform.startswith("win") else 0,
            )
            profile["version"] = (result.stdout or result.stderr or "").strip()
        except Exception:
            pass
    if profile["settings"]:
        settings = load_json(CLAUDE_CODE_SETTINGS, {})
        env = settings.get("env", {}) if isinstance(settings, dict) else {}
        if isinstance(env, dict):
            base_url = str(env.get("ANTHROPIC_BASE_URL", "")).strip()
            profile["provider"] = "DeepSeek" if "deepseek" in base_url.lower() else (base_url or "自定义接口")
            profile["model"] = str(
                env.get("ANTHROPIC_MODEL")
                or env.get("ANTHROPIC_DEFAULT_SONNET_MODEL")
                or "未配置"
            ).strip()
            profile["credential_ready"] = any(
                bool(str(value or "").strip())
                for key, value in env.items()
                if re.search(r"(key|token|secret)$", str(key), re.IGNORECASE)
            )
    return profile


def claude_project_candidates(config=None):
    config = config or {}
    candidates = []
    saved = config.get("ClaudeRecentProjects", [])
    if isinstance(saved, list):
        candidates.extend(saved)
    candidates.extend([config.get("ClaudeLastProject", ""), str(BASE)])
    projects_root = Path("D:/CodexProjects")
    if projects_root.exists():
        try:
            candidates.extend(str(path) for path in projects_root.iterdir() if path.is_dir())
        except OSError:
            pass
    result = []
    seen = set()
    for value in candidates:
        text = str(value or "").strip()
        if not text:
            continue
        normalized = os.path.normcase(os.path.abspath(os.path.expandvars(os.path.expanduser(text))))
        if normalized in seen or not Path(normalized).is_dir():
            continue
        seen.add(normalized)
        result.append(normalized)
    return result[:12]


def build_claude_code_args(
    prompt="",
    session_mode="new",
    permission_mode="default",
    effort="medium",
    always_chinese=True,
    safe_mode=False,
    session_name="",
):
    args = []
    if CLAUDE_CODE_SETTINGS.exists():
        args.extend(["--settings", str(CLAUDE_CODE_SETTINGS)])
    if session_mode == "continue":
        args.append("--continue")
    elif session_mode == "resume":
        args.append("--resume")
    if permission_mode in {"default", "acceptEdits", "auto", "dontAsk", "plan"}:
        args.extend(["--permission-mode", permission_mode])
    if effort in {"low", "medium", "high", "xhigh", "max"}:
        args.extend(["--effort", effort])
    if safe_mode:
        args.append("--safe-mode")
    if always_chinese:
        args.extend(["--append-system-prompt", CLAUDE_CHINESE_SYSTEM_PROMPT])
    if session_name:
        args.extend(["--name", session_name])
    text = str(prompt or "").strip()
    if text:
        args.append(text)
    return args


def launch_claude_code_terminal(
    prompt="",
    cwd=None,
    session_mode="new",
    permission_mode="default",
    effort="medium",
    always_chinese=True,
    safe_mode=False,
):
    if not CLAUDE_CODE_EXE.exists():
        return False, f"找不到 Claude Code：{CLAUDE_CODE_EXE}"
    working_dir = Path(cwd or BASE).expanduser()
    if not working_dir.is_dir():
        return False, f"项目文件夹不存在：{working_dir}"
    args = build_claude_code_args(
        prompt=prompt,
        session_mode=session_mode,
        permission_mode=permission_mode,
        effort=effort,
        always_chinese=always_chinese,
        safe_mode=safe_mode,
        session_name=f"糯米-{working_dir.name}",
    )
    try:
        if sys.platform.startswith("win"):
            quoted = " ".join(powershell_quote(item) for item in args)
            command = f"& {powershell_quote(CLAUDE_CODE_EXE)}"
            if quoted:
                command += f" {quoted}"
            script = (
                "$utf8 = New-Object System.Text.UTF8Encoding($false); "
                "[Console]::OutputEncoding = $utf8; $OutputEncoding = $utf8; "
                "$Host.UI.RawUI.WindowTitle = '糯米 Claude Code 中文助手'; "
                f"Set-Location -LiteralPath {powershell_quote(working_dir)}; "
                f"{command}"
            )
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", script],
                cwd=str(working_dir),
                creationflags=0,
            )
        else:
            subprocess.Popen([str(CLAUDE_CODE_EXE), *args], cwd=str(working_dir))
        return True, f"Claude Code 已启动：{working_dir.name}"
    except Exception as exc:
        return False, f"Claude Code 启动失败：{exc}"


def next_holiday_info(today=None):
    today = today or datetime.now().date()
    for item in CHINA_HOLIDAYS_2026:
        start = datetime.strptime(item["start"], "%Y-%m-%d").date()
        end = datetime.strptime(item["end"], "%Y-%m-%d").date()
        if today <= end:
            info = dict(item)
            info["days_until"] = max(0, (start - today).days)
            info["is_active"] = start <= today <= end
            return info
    return None


def next_holiday_text(today=None):
    info = next_holiday_info(today)
    if not info:
        return "暂无已公布的后续法定节假日"
    if info["is_active"]:
        return f"正在放 {info['name']}，共 {info['days']} 天"
    return f"{info['name']}还有 {info['days_until']} 天，放 {info['days']} 天"


def mail_signature(message):
    return "|".join(
        [
            str(message.get("account_user", "")),
            str(message.get("id", "")),
            str(message.get("date", "")),
            str(message.get("sender", "")),
            str(message.get("subject", "")),
        ]
    )[:500]


def normalized_mail_port(host, port):
    try:
        value = int(port)
    except Exception:
        value = 993
    if host.strip().lower() == "imap.qq.com":
        return 993
    if host.strip().lower() == "imap.gmail.com":
        return 993
    return value


def mail_provider_for(host, user=""):
    value = f"{host} {user}".lower()
    if "gmail.com" in value:
        return "gmail"
    if "qq.com" in value:
        return "qq"
    return "imap"


def mail_inbox_url(provider):
    if provider == "gmail":
        return "https://mail.google.com/mail/u/0/#inbox"
    if provider == "qq":
        return "https://mail.qq.com/"
    return "https://mail.google.com/mail/u/0/#inbox"


def mail_smtp_settings(provider):
    if provider == "gmail":
        return "smtp.gmail.com", 465
    if provider == "qq":
        return "smtp.qq.com", 465
    return "", 465


def split_mail_addresses(value):
    return [item.strip() for item in re.split(r"[,;，；\s]+", value or "") if item.strip()]


def mail_account_for_provider(config, provider):
    for account in mail_accounts_from_config(config):
        if account.get("provider") == provider:
            return account
    return None


def send_mail_via_account(account, to, subject, body, cc="", bcc=""):
    recipients = split_mail_addresses(to)
    cc_list = split_mail_addresses(cc)
    bcc_list = split_mail_addresses(bcc)
    if not recipients:
        return False, "请先填写收件人。"
    subject = (subject or "").strip()
    if not subject:
        return False, "请先填写邮件主题。"
    provider = account.get("provider") or mail_provider_for(account.get("host", ""), account.get("user", ""))
    smtp_host, smtp_port = mail_smtp_settings(provider)
    if not smtp_host:
        return False, "这个邮箱账号还没有配置 SMTP 发件服务器。"

    message = EmailMessage()
    message["From"] = account.get("user", "")
    message["To"] = ", ".join(recipients)
    if cc_list:
        message["Cc"] = ", ".join(cc_list)
    message["Subject"] = subject
    message.set_content(body or "")

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=25) as client:
            client.login(account.get("user", ""), account.get("password", ""))
            client.send_message(message, to_addrs=recipients + cc_list + bcc_list)
    except Exception as exc:
        return False, f"邮件发送失败：{exc}"
    return True, "邮件已发送。"


def mail_accounts_from_config(config):
    accounts = []
    seen = set()

    def add_account(label, provider, host, port, user, password):
        host = (host or "").strip()
        user = (user or "").strip()
        password = password or ""
        if not host or not user or not password:
            return
        provider = provider or mail_provider_for(host, user)
        key = (host.lower(), user.lower())
        if key in seen:
            return
        seen.add(key)
        accounts.append(
            {
                "label": label or user,
                "provider": provider,
                "host": host,
                "port": normalized_mail_port(host, port or 993),
                "user": user,
                "password": password,
            }
        )

    for item in config.get("MailAccounts", []) or []:
        if not isinstance(item, dict) or item.get("Enabled") is False:
            continue
        add_account(
            item.get("Label") or item.get("User"),
            item.get("Provider"),
            item.get("Host"),
            item.get("Port", 993),
            item.get("User"),
            item.get("Password"),
        )

    add_account(
        "QQ 邮箱" if mail_provider_for(config.get("MailHost", ""), config.get("MailUser", "")) == "qq" else "主邮箱",
        None,
        config.get("MailHost", ""),
        config.get("MailPort", 993),
        config.get("MailUser", ""),
        config.get("MailPassword", ""),
    )
    add_account(
        "Gmail",
        "gmail",
        "imap.gmail.com",
        993,
        config.get("GmailUser", ""),
        config.get("GmailPassword", ""),
    )
    return accounts


def mail_accounts_config(config):
    return [
        {
            "Label": account["label"],
            "Provider": account["provider"],
            "Host": account["host"],
            "Port": account["port"],
            "User": account["user"],
            "Password": account["password"],
            "Enabled": True,
        }
        for account in mail_accounts_from_config(config)
    ]


WEATHER_TRANSLATIONS = {
    "sunny": "晴",
    "clear": "晴",
    "partly cloudy": "局部多云",
    "cloudy": "多云",
    "overcast": "阴",
    "mist": "薄雾",
    "fog": "雾",
    "freezing fog": "冻雾",
    "patchy fog": "局部有雾",
    "patchy rain nearby": "附近有零星小雨",
    "patchy rain possible": "可能有零星小雨",
    "patchy freezing drizzle possible": "可能有冻毛毛雨",
    "patchy sleet possible": "可能有雨夹雪",
    "patchy snow possible": "可能有零星小雪",
    "patchy light drizzle": "局部小毛毛雨",
    "patchy light rain": "零星小雨",
    "light rain": "小雨",
    "moderate rain at times": "间歇性中雨",
    "moderate rain": "中雨",
    "heavy rain at times": "间歇性大雨",
    "heavy rain": "大雨",
    "light drizzle": "小毛毛雨",
    "freezing drizzle": "冻毛毛雨",
    "heavy freezing drizzle": "强冻毛毛雨",
    "light freezing rain": "小冻雨",
    "moderate or heavy freezing rain": "中到大冻雨",
    "thundery outbreaks possible": "可能有雷阵雨",
    "blowing snow": "风吹雪",
    "blizzard": "暴风雪",
    "patchy snow nearby": "附近有零星小雪",
    "patchy light snow": "零星小雪",
    "light snow": "小雪",
    "patchy moderate snow": "零星中雪",
    "moderate snow": "中雪",
    "patchy heavy snow": "零星大雪",
    "heavy snow": "大雪",
    "ice pellets": "冰粒",
    "light sleet": "小雨夹雪",
    "moderate or heavy sleet": "中到大雨夹雪",
    "light rain shower": "小阵雨",
    "moderate or heavy rain shower": "中到大阵雨",
    "torrential rain shower": "暴雨",
    "light sleet showers": "小雨夹雪阵雨",
    "moderate or heavy sleet showers": "中到大雨夹雪阵雨",
    "light snow showers": "小阵雪",
    "moderate or heavy snow showers": "中到大阵雪",
    "light showers of ice pellets": "小冰粒阵雨",
    "moderate or heavy showers of ice pellets": "中到大冰粒阵雨",
    "patchy light rain with thunder": "局部雷阵雨",
    "moderate or heavy rain with thunder": "中到大雷雨",
    "patchy light snow with thunder": "局部雷雪",
    "moderate or heavy snow with thunder": "中到大雷雪",
    "rain": "雨",
    "showers": "阵雨",
    "snow": "雪",
    "sleet": "雨夹雪",
    "drizzle": "毛毛雨",
    "humid": "潮湿",
}


def has_chinese(text):
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def normalize_weather_key(text):
    key = re.sub(r"[^a-z0-9]+", " ", str(text or "").lower())
    return re.sub(r"\s+", " ", key).strip()


def weather_intensity_prefix(words):
    if "torrential" in words:
        return "暴"
    if "heavy" in words:
        return "大"
    if "moderate" in words:
        return "中"
    if "light" in words:
        return "小"
    if "patchy" in words:
        return "零星"
    return ""


def fallback_weather_desc_zh(key):
    if not key:
        return "未知"
    words = set(key.split())
    prefix = weather_intensity_prefix(words)
    has_shower = "shower" in key or "showers" in key
    has_thunder = "thunder" in words or "thundery" in words

    if has_thunder:
        if "snow" in words:
            return f"{prefix}雷雪" if prefix else "雷雪"
        return f"{prefix}雷阵雨" if prefix else "雷阵雨"
    if "blizzard" in words:
        return "暴风雪"
    if "sleet" in words:
        base = "雨夹雪阵雨" if has_shower else "雨夹雪"
        return f"{prefix}{base}" if prefix else base
    if "snow" in words:
        base = "阵雪" if has_shower else "雪"
        return f"{prefix}{base}" if prefix else base
    if "pellets" in words or "ice" in words:
        base = "冰粒阵雨" if has_shower else "冰粒"
        return f"{prefix}{base}" if prefix else base
    if "freezing" in words and "rain" in words:
        return f"{prefix}冻雨" if prefix else "冻雨"
    if "drizzle" in words:
        base = "冻毛毛雨" if "freezing" in words else "毛毛雨"
        return f"{prefix}{base}" if prefix else base
    if "rain" in words or has_shower:
        base = "阵雨" if has_shower else "雨"
        return f"{prefix}{base}" if prefix else base
    if "fog" in words:
        return "雾"
    if "mist" in words:
        return "薄雾"
    if "overcast" in words:
        return "阴"
    if "cloudy" in words or "cloud" in words:
        return "多云"
    if "sunny" in words or "clear" in words:
        return "晴"
    if "humid" in words:
        return "潮湿"
    return "天气状况未知"


def weather_desc_zh(text):
    value = (text or "").strip()
    if not value:
        return "未知"
    if has_chinese(value):
        return value
    key = normalize_weather_key(value)
    return WEATHER_TRANSLATIONS.get(key) or fallback_weather_desc_zh(key)


def compact_inline_text(text, max_chars=22):
    value = re.sub(r"\s+", " ", str(text or "").replace("\n", " ")).strip()
    if max_chars <= 1:
        return value
    return value if len(value) <= max_chars else value[: max_chars - 1].rstrip() + "…"


def compact_card_detail(text, max_lines=2, max_chars=22):
    value = str(text or "").strip()
    if not value:
        return ""
    segments = []
    for raw_line in value.splitlines():
        line = re.sub(r"\s+", " ", raw_line).strip()
        if not line:
            continue
        parts = [part.strip() for part in re.split(r"(?<=[；;。])\s*", line) if part.strip()]
        segments.extend(parts or [line])
    if not segments:
        segments = [value]
    return "\n".join(compact_inline_text(segment, max_chars) for segment in segments[:max_lines])


def weather_card_text(text):
    value = str(text or "").strip()
    if not value:
        return "天气读取中"
    if value.startswith("天气查询失败"):
        return "天气查询失败\n点开重试"
    return compact_card_detail(value, max_lines=2, max_chars=18)


def format_minutes(minutes):
    minutes = int(minutes or 0)
    hours, mins = divmod(minutes, 60)
    if hours and mins:
        return f"{hours}小时{mins}分钟"
    if hours:
        return f"{hours}小时"
    return f"{mins}分钟"


def parse_local_minutes(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M")
    except Exception:
        return None


CN_NUMBERS = {
    "零": 0,
    "〇": 0,
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}


def parse_small_number(token):
    token = str(token or "").strip()
    if not token:
        return None
    if token.isdigit():
        return int(token)
    if token == "十":
        return 10
    if "十" in token:
        left, _, right = token.partition("十")
        tens = CN_NUMBERS.get(left, 1) if left else 1
        ones = CN_NUMBERS.get(right, 0) if right else 0
        return tens * 10 + ones
    return CN_NUMBERS.get(token)


def parse_natural_reminder(text, now=None):
    raw = (text or "").strip()
    if "提醒" not in raw:
        return None
    now = now or datetime.now()
    normalized = raw.replace("：", ":")
    normalized = (
        normalized
        .replace("明早", "明天早上")
        .replace("明晚", "明天晚上")
        .replace("明儿", "明天")
        .replace("后早", "后天早上")
        .replace("后晚", "后天晚上")
    )
    num = r"(?:\d{1,2}|[零〇一二两三四五六七八九十]{1,3})"

    target = None
    match = re.search(rf"({num})\s*分钟后", normalized)
    if match:
        value = parse_small_number(match.group(1))
        if value is not None:
            target = now + timedelta(minutes=value)
    match = re.search(rf"({num})\s*小时后", normalized)
    if match:
        value = parse_small_number(match.group(1))
        if value is not None:
            target = now + timedelta(hours=value)
    match = re.search(rf"({num})\s*天后", normalized)
    if match:
        value = parse_small_number(match.group(1))
        if value is not None:
            target = now + timedelta(days=value)

    day = now.date()
    explicit_weekday = False
    if "后天" in normalized:
        day = (now + timedelta(days=2)).date()
    elif "明天" in normalized or "明日" in normalized:
        day = (now + timedelta(days=1)).date()
    elif "今天" in normalized or "今晚" in normalized:
        day = now.date()

    weekday_match = re.search(r"(下周|下星期|下礼拜)?\s*(?:周|星期|礼拜)\s*([一二三四五六日天])", normalized)
    if weekday_match:
        weekday_map = {"一": 0, "二": 1, "三": 2, "四": 3, "五": 4, "六": 5, "日": 6, "天": 6}
        weekday = weekday_map.get(weekday_match.group(2))
        if weekday is not None:
            days = (weekday - now.weekday()) % 7
            if weekday_match.group(1) and days == 0:
                days = 7
            day = (now + timedelta(days=days)).date()
            explicit_weekday = True

    date_match = re.search(r"(\d{1,2})\s*月\s*(\d{1,2})\s*[日号]?", normalized)
    if date_match:
        month = int(date_match.group(1))
        day_num = int(date_match.group(2))
        year = now.year
        try:
            candidate = datetime(year, month, day_num).date()
            if candidate < now.date() - timedelta(days=1):
                candidate = datetime(year + 1, month, day_num).date()
            day = candidate
            explicit_weekday = False
        except ValueError:
            pass

    time_match = re.search(rf"(凌晨|早上|上午|中午|下午|晚上|今晚)?\s*({num})\s*(?:点|:)\s*(半|{num})?\s*(?:分)?", normalized)
    if time_match:
        period = time_match.group(1) or ""
        hour = parse_small_number(time_match.group(2))
        minute_token = time_match.group(3)
        minute = 30 if minute_token == "半" else parse_small_number(minute_token) if minute_token else 0
        if hour is not None and minute is not None:
            if period in {"下午", "晚上", "今晚"} and hour < 12:
                hour += 12
            if period == "中午" and hour < 11:
                hour += 12
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                target = datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute)

    if target is None:
        return None
    if target < now - timedelta(minutes=1):
        target = target + timedelta(days=7 if explicit_weekday else 1)

    title = normalized
    cleanup_patterns = [
        r"请?帮?我?提醒(?:我|一下)?",
        r"记得提醒(?:我)?",
        r"提醒(?:我|一下)?",
        rf"{num}\s*分钟后",
        rf"{num}\s*小时后",
        rf"{num}\s*天后",
        r"(今天|明天|明日|后天|今晚)",
        r"(下周|下星期|下礼拜)?\s*(?:周|星期|礼拜)\s*[一二三四五六日天]",
        r"\d{1,2}\s*月\s*\d{1,2}\s*[日号]?",
        rf"(凌晨|早上|上午|中午|下午|晚上|今晚)?\s*{num}\s*(?:点|:)\s*(?:半|{num})?\s*(?:分)?",
        r"到时候",
        r"的时候",
    ]
    for pattern in cleanup_patterns:
        title = re.sub(pattern, "", title)
    title = title.strip(" ，,。.!！:：的在")
    if not title:
        title = "提醒事项"
    return {"title": title[:80], "remind_at": target.strftime("%Y-%m-%d %H:%M")}


def parse_time_text_without_trigger(text, now=None):
    raw = (text or "").strip()
    if not raw:
        return None
    return parse_natural_reminder(raw, now=now) or parse_natural_reminder("提醒我" + raw, now=now)


def next_time_at(hour, minute=0, day_offset=0, now=None):
    now = now or datetime.now()
    day = now.date() + timedelta(days=day_offset)
    target = datetime.combine(day, datetime.min.time()).replace(hour=hour, minute=minute)
    if day_offset == 0 and target <= now + timedelta(minutes=1):
        target += timedelta(days=1)
    return target


def next_weekday_time(weekday, hour, minute=0, now=None):
    now = now or datetime.now()
    days = (weekday - now.weekday()) % 7
    target = next_time_at(hour, minute, days, now=now)
    if target <= now + timedelta(minutes=1):
        target += timedelta(days=7)
    return target


def build_todo_item(title, remind_at=""):
    return {
        "id": str(time.time()),
        "title": title,
        "done": False,
        "reminded": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "remind_at": remind_at,
    }


def study_breakdown(logs, target_date):
    study = {}
    rest = 0
    for item in logs:
        at = item.get("at", "")
        if not at.startswith(target_date.isoformat()):
            continue
        minutes = int(item.get("minutes", 0) or 0)
        if item.get("mode", "学习") == "休息":
            rest += minutes
            continue
        subject = item.get("subject", "学习") or "学习"
        study[subject] = study.get(subject, 0) + minutes
    return study, rest


def consecutive_study_days(logs):
    days = set()
    for item in logs:
        if item.get("mode", "学习") != "学习":
            continue
        if int(item.get("minutes", 0) or 0) <= 0:
            continue
        try:
            days.add(datetime.fromisoformat(item.get("at", "")).date())
        except Exception:
            continue
    count = 0
    day = datetime.now().date()
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


def total_study_minutes(logs, target_date):
    study, _rest = study_breakdown(logs, target_date)
    return sum(study.values())


def study_day_summary(target_date):
    logs = load_json(STUDY, [])
    minutes = total_study_minutes(logs, target_date)
    if minutes <= 0:
        return ""
    label = "今天" if target_date == datetime.now().date() else "昨天"
    return f"{label}学习了{format_minutes(minutes)}。"


def study_streak_text():
    days = consecutive_study_days(load_json(STUDY, []))
    if days >= 3:
        return f"已经连续学习{days}天了。"
    return ""


def exam_days_left(config):
    try:
        exam = datetime.strptime(config.get("ExamDate", "2026-12-26"), "%Y-%m-%d").date()
    except ValueError:
        return None
    return (exam - datetime.now().date()).days


def exam_event_text(config):
    days = exam_days_left(config)
    if days is None:
        return ""
    if days == 100:
        return "距离考研还有100天。我会陪你的。"
    if days == 30:
        return "距离考研还有30天，稳住节奏。"
    if days == 7:
        return "最后一周了，先睡好。"
    if days == 1:
        return "明天考试。今晚别硬熬。"
    if days == 0:
        return "今天考试。你已经走到这里了。"
    if days == -1:
        return "你做到了。今天不学习也没关系。"
    return ""


def next_todo_preview():
    todos = load_json(TODOS, [])
    upcoming = []
    pending_count = 0
    now = datetime.now()
    for todo in todos:
        if todo.get("done"):
            continue
        pending_count += 1
        at = parse_local_minutes(todo.get("remind_at", ""))
        if at:
            upcoming.append((at, todo.get("title", "")))
    if not upcoming:
        return f"待办 {pending_count} 项" if pending_count else "暂无提醒事项"
    at, title = sorted(upcoming, key=lambda item: item[0])[0]
    if at <= now:
        return f"现在该做：{title}"
    delta = at - now
    if delta.days:
        return f"下一项：{title}，还有 {delta.days} 天"
    return f"下一项：{title}，还有 {max(1, int(delta.total_seconds() // 60))} 分钟"


def exam_countdown_text(config):
    days = exam_days_left(config)
    if days is None:
        return "考研日期未设置"
    if days == 0:
        return "今天考研"
    if days < 0:
        return "考研已经结束"
    return f"距离考研：{days}天"


def today_task_lines(limit=3):
    todos = load_json(TODOS, [])
    pending = []
    today = datetime.now().date()
    for todo in todos:
        if todo.get("done"):
            continue
        at = parse_local_minutes(todo.get("remind_at", ""))
        score = 0
        if at and at.date() == today:
            score = -1
        pending.append((score, at or datetime.max, todo.get("title", "")))
    pending.sort(key=lambda item: (item[0], item[1]))
    if not pending:
        return ["今天还没有任务"]
    return [f"□ {title}" for _score, _at, title in pending[:limit]]


def next_event_preview():
    events = load_json(CALENDAR, [])
    now = datetime.now()
    upcoming = []
    for event in events:
        at = parse_local_minutes(event.get("at", ""))
        if at and at >= now:
            upcoming.append((at, event.get("title", ""), event.get("kind", "")))
    if not upcoming:
        return next_holiday_text()
    at, title, kind = sorted(upcoming, key=lambda item: item[0])[0]
    prefix = "今天" if at.date() == now.date() else "明天" if at.date() == (now + timedelta(days=1)).date() else at.strftime("%m-%d")
    return f"{prefix} {at:%H:%M} {title or kind}"


def mail_dashboard_text():
    state = load_json(MAIL_STATE, {})
    unread = state.get("last_unread_count")
    if unread is None:
        return "邮件监控中"
    messages = state.get("last_mail_messages", [])
    if isinstance(messages, list):
        for message in messages[:5]:
            code = str(message.get("verification_code") or "").strip()
            if code:
                return f"未读邮件：{unread}封，验证码 {code}"
    return f"未读邮件：{unread}封"


def upcoming_todo_lines(limit=4):
    todos = load_json(TODOS, [])
    pending = []
    now = datetime.now()
    for todo in todos:
        if todo.get("done"):
            continue
        title = todo.get("title", "").strip() or "未命名事项"
        at = parse_local_minutes(todo.get("remind_at", ""))
        if at and at <= now:
            text = f"现在该做：{title}"
            rank = (0, at)
        elif at:
            delta = at - now
            if at.date() == now.date():
                text = f"今天 {at:%H:%M}：{title}"
            elif at.date() == (now + timedelta(days=1)).date():
                text = f"明天 {at:%H:%M}：{title}"
            elif delta.days > 0:
                text = f"{at:%m-%d %H:%M}：{title}"
            else:
                text = f"待提醒：{title}"
            rank = (1, at)
        else:
            text = f"待办：{title}"
            rank = (2, datetime.max)
        pending.append((rank, text))
    if not pending:
        return ["暂无待办，可以先处理一件小事。"]
    pending.sort(key=lambda item: item[0])
    return [text for _rank, text in pending[:limit]]


def upcoming_event_lines(limit=4, days=7):
    events = load_json(CALENDAR, [])
    now = datetime.now()
    end = now + timedelta(days=days)
    upcoming = []
    for event in events:
        at = parse_local_minutes(event.get("at", ""))
        if not at or at < now or at > end:
            continue
        title = event.get("title", "").strip() or event.get("kind", "").strip() or "日程"
        if at.date() == now.date():
            label = f"今天 {at:%H:%M}"
        elif at.date() == (now + timedelta(days=1)).date():
            label = f"明天 {at:%H:%M}"
        else:
            label = at.strftime("%m-%d %H:%M")
        upcoming.append((at, f"{label}：{title}"))
    if not upcoming:
        holiday = next_holiday_text()
        return [holiday] if holiday else ["近 7 天暂无日程。"]
    upcoming.sort(key=lambda item: item[0])
    return [text for _at, text in upcoming[:limit]]


def today_study_lines(config):
    logs = load_json(STUDY, [])
    today = datetime.now().date()
    study, rest = study_breakdown(logs, today)
    total = sum(study.values())
    lines = [exam_countdown_text(config)]
    if total:
        detail = "，".join(f"{subject}{format_minutes(minutes)}" for subject, minutes in sorted(study.items()))
        lines.append(f"今日学习：{format_minutes(total)}（{detail}）")
    else:
        lines.append("今日还没有学习记录。")
    if rest:
        lines.append(f"今日休息：{format_minutes(rest)}")
    streak = consecutive_study_days(logs)
    if streak:
        lines.append(f"连续学习：{streak} 天")
    return lines


def compact_health_lines(config):
    snapshot = system_health_snapshot(config)
    lines = [
        f"CPU {snapshot['cpu']:.0f}% / 内存 {snapshot['memory_percent']:.0f}% / 磁盘 {snapshot['disk_percent']:.0f}%",
        f"VPN：{snapshot['vpn']}，Codex：{snapshot['codex']}",
    ]
    lines.extend(battery_status_lines(config, snapshot.get("battery"))[:2])
    if snapshot["issues"]:
        lines.append("需要注意：" + "；".join(text for _key, text in snapshot["issues"]))
    else:
        lines.append("需要注意：暂无")
    return lines


def today_next_action_lines(pet, limit=5):
    config = getattr(pet, "config", {})
    lines = []

    for text in upcoming_todo_lines(limit=3):
        if text.startswith("现在该做"):
            lines.append(text)

    for text in upcoming_event_lines(limit=2, days=1):
        if text.startswith("今天") or text.startswith("明天"):
            lines.append("日程：" + text)

    state = load_json(MAIL_STATE, {})
    unread = state.get("last_unread_count")
    if isinstance(unread, int) and unread > 0:
        lines.append(f"邮件：有 {unread} 封未读，记得看一眼。")

    try:
        snapshot = system_health_snapshot(config)
        if snapshot["issues"]:
            lines.append("电脑：" + "；".join(text for _key, text in snapshot["issues"][:2]))
    except Exception:
        pass

    weather = getattr(pet, "weather_text", "")
    mood = weather_mood_text(weather)
    if mood:
        lines.append("天气：" + mood)

    if not lines:
        todo_text = next_todo_preview()
        if todo_text and todo_text != "暂无提醒事项":
            lines.append(todo_text)
    if not lines:
        event_text = next_event_preview()
        if event_text:
            lines.append("日程：" + event_text)
    if not lines:
        exam_text = exam_countdown_text(config)
        if exam_text:
            lines.append(exam_text)
    if not lines:
        lines.append("今天先从最小的一步开始。")
    return lines[:limit]


def today_dashboard_text(pet):
    text = (today_next_action_lines(pet, limit=1) or ["今日看板"])[0]
    return text if len(text) <= 32 else text[:31] + "…"


def load_pet_memory():
    memory = load_json(PET_MEMORY, {})
    memory.setdefault("memories", [])
    memory.setdefault("study_progress", {})
    memory["bond_level"] = "伙伴"
    return memory


def save_pet_memory(memory):
    memory["bond_level"] = "伙伴"
    save_json(PET_MEMORY, memory)


def remember_text(text, source="chat"):
    text = text.strip(" ，。！？!?\n\t")
    if not text:
        return ""
    memory = load_pet_memory()
    items = memory.setdefault("memories", [])
    if not any(item.get("text") == text for item in items):
        items.append(
            {
                "text": text[:120],
                "source": source,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        memory["memories"] = items[-80:]
        save_pet_memory(memory)
    return text


def record_study_progress(subject, topic):
    topic = topic.strip(" ，。！？!?\n\t")
    if not topic:
        return ""
    memory = load_pet_memory()
    progress = memory.setdefault("study_progress", {})
    subject_items = progress.setdefault(subject or "学习", {})
    subject_items[topic[:60]] = datetime.now().isoformat(timespec="seconds")
    save_pet_memory(memory)
    return topic


def infer_study_subject(text, mode=""):
    if "高数" in mode or "高数" in text or any(word in text for word in ("极限", "导数", "积分", "线代", "概率")):
        return "高数"
    if "408" in mode or "408" in text or any(word in text for word in ("线性表", "栈", "队列", "图", "树", "操作系统", "计网", "组成原理")):
        return "408"
    if "英语" in text or "单词" in text:
        return "英语"
    return "学习"


def extract_memory_and_progress(text, mode=""):
    notes = []
    for match in re.finditer(r"(?:记住|记得|帮我记住|你要记住)(?:一下|：|:)?\s*([^。！？!?\n]{2,80})", text):
        remembered = remember_text(match.group(1), "chat")
        if remembered:
            notes.append(f"已记住：{remembered}")

    study_patterns = [
        r"(?:今天|刚刚|我)?(?:已经)?(?:学完了|学完|复习完了|完成了|刷完了)\s*([^。！？!?\n]{2,40})",
        r"([^。！？!?\n]{2,40})(?:已经)?(?:学完了|复习完了|完成了)",
    ]
    for pattern in study_patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        topic = match.group(1).strip(" ，。了")
        if topic:
            subject = infer_study_subject(text, mode)
            recorded = record_study_progress(subject, topic)
            if recorded:
                notes.append(f"已记录到{subject}进度：{recorded}")
            break
    return notes


def ai_memory_context(config):
    memory = load_pet_memory()
    lines = [
        f"你现在也是用户的桌宠{config.get('PetName', '糯米')}，和用户的关系是伙伴。",
        "固定人格：有点呆，有点黏人，喜欢学习和小狐狸，讨厌熬夜，会轻轻监督但不说教。",
        "回答要像桌宠在身边说话：自然、亲近、短一点；不要说“您好，请问有什么可以帮助您”。",
        "如果用户说不想学了，先允许休息，再轻轻约一个很小的下一步，比如“休息十分钟我再来抓你”。",
    ]
    remembered = [item.get("text", "") for item in memory.get("memories", []) if item.get("text")]
    if remembered:
        lines.append("用户长期记忆：" + "；".join(remembered[-8:]))
    progress = memory.get("study_progress", {})
    progress_lines = []
    for subject, topics in progress.items():
        if isinstance(topics, dict) and topics:
            progress_lines.append(f"{subject}：" + "、".join(list(topics.keys())[-8:]))
    if progress_lines:
        lines.append("学习进度：" + "；".join(progress_lines))
    lines.append(f"默认天气城市：{config.get('WeatherCity', '上海')}。")
    return "\n".join(lines)


def yesterday_study_memory():
    logs = load_json(STUDY, [])
    yesterday = datetime.now().date() - timedelta(days=1)
    study, _rest = study_breakdown(logs, yesterday)
    if not study:
        memory = load_pet_memory()
        latest = []
        for subject, topics in memory.get("study_progress", {}).items():
            if not isinstance(topics, dict):
                continue
            for topic, at in topics.items():
                latest.append((at, subject, topic))
        if not latest:
            return ""
        _at, subject, topic = sorted(latest)[-1]
        return f"上次记到{subject}：{topic}。今天要不要继续下一小节？"
    subject = max(study.items(), key=lambda item: item[1])[0]
    return f"昨天学了{subject}，今天要不要继续？"


def time_greeting():
    hour = datetime.now().hour
    if hour < 5:
        return "还不睡吗？"
    if hour < 11:
        return "早呀。"
    if hour < 18:
        return "今天也在努力。"
    if hour < 23:
        return "今天辛苦了。"
    return "夜深了，记得休息。"


def seasonal_mood_text():
    month = datetime.now().month
    if month in (6, 7, 8):
        return "有点热……我想趴在凉一点的地方。"
    if month in (12, 1, 2):
        return "手会不会冷？我把围巾想象出来了。"
    if month in (3, 4, 5):
        return "天气慢慢变软了，适合开始一点新进度。"
    return "秋天很适合复习，我会安静陪你。"


def weather_mood_text(text):
    value = text or ""
    if any(word in value for word in ("雨", "雷", "阵雨", "小雨", "中雨", "大雨")):
        return "今天会下雨哦。我抱着小伞提醒你。"
    if "雪" in value:
        return "外面可能有雪，手会不会冷？"
    if any(word in value for word in ("热", "炎", "高温")):
        return "有点热……我先趴一会儿。"
    if any(word in value for word in ("冷", "寒", "低温")):
        return "今天有点冷，别让手冻僵。"
    return ""


COLLECTIBLES = {
    "glasses": {"name": "眼镜", "mark": "眼镜"},
    "cap": {"name": "学士帽", "mark": "学士帽"},
    "gold_bag": {"name": "金色书包", "mark": "金色书包"},
}


def earned_collectibles():
    logs = load_json(STUDY, [])
    streak = consecutive_study_days(logs)
    memory = load_pet_memory()
    progress = memory.get("study_progress", {})
    earned = []
    if streak >= 7:
        earned.append("glasses")
    if streak >= 30:
        earned.append("cap")
    math_topics = progress.get("高数", {})
    if isinstance(math_topics, dict):
        topic_text = " ".join(math_topics.keys())
        if "一轮" in topic_text or "第一轮" in topic_text or len(math_topics) >= 8:
            earned.append("gold_bag")
    return earned


def collectible_marks(keys):
    return " / ".join(COLLECTIBLES[key]["mark"] for key in keys if key in COLLECTIBLES)


LIFE_BEHAVIORS = [
    ("stretch", "伸懒腰", "今天感觉怎么样？"),
    ("sleep", "睡觉", "我先趴一会儿，有事叫我。"),
    ("sniff", "闻一闻", "你在看什么？"),
    ("peek", "好奇", "我来偷偷看一眼进度。"),
    ("happy", "开心", "和你待在桌面角落也挺好。"),
    ("attention", "提醒", "喝口水吧，脑子会清醒一点。"),
    ("study", "学习陪伴", "要不要把今天最小的一件事做掉？"),
    ("dream", "发呆", "我刚刚想了一下，先开始五分钟也算开始。"),
    ("stretch", "伸懒腰", "眼睛也休息一下。"),
    ("sniff", "闻一闻", "我闻到了任务列表的味道。"),
    ("happy", "开心", "你回来啦。"),
    ("attention", "提醒", "坐太久的话，肩膀放松一下。"),
    ("sleep", "睡觉", "我充会儿电。"),
    ("peek", "好奇", "今天有没有遇到难题？"),
    ("study", "学习陪伴", "408一点点啃，真的会变简单。"),
    ("dream", "发呆", "如果卡住了，可以把题截图给我。"),
    ("stretch", "伸懒腰", "我们换个姿势继续。"),
    ("happy", "开心", "我在呢。"),
    ("attention", "提醒", "番茄钟要不要来一轮？"),
    ("sniff", "闻一闻", "今天的天气也适合学一点点。"),
    ("peek", "好奇", "我看看你是不是在认真。"),
    ("dream", "发呆", "等你忙完，我们再聊。"),
    ("sleep", "睡觉", "安静陪读模式开启。"),
    ("happy", "开心", "伙伴满级，糯米待命。"),
]

GAME_PROCESS_HINTS = (
    "steam",
    "steamwebhelper",
    "epicgameslauncher",
    "riotclientservices",
    "leagueclient",
    "league of legends",
    "valorant",
    "cs2",
    "csgo",
    "dota2",
    "overwatch",
    "genshinimpact",
    "yuanshen",
    "starrail",
    "honkai",
    "minecraft",
    "roblox",
    "game",
)

GAME_TITLE_HINTS = (
    "steam",
    "epic games",
    "英雄联盟",
    "league of legends",
    "valorant",
    "原神",
    "崩坏",
    "星穹铁道",
    "minecraft",
)


def entertainment_running():
    hints = ("steam.exe", "bilibili", "youtube", "douyin", "epicgameslauncher.exe")
    try:
        for proc in psutil.process_iter(["name"]):
            name = (proc.info.get("name") or "").lower()
            if any(hint in name for hint in hints):
                return True
    except Exception:
        pass
    return False


def foreground_game_window(exclude_pids=None):
    info = foreground_window_info()
    if not info or info.get("pid") in set(exclude_pids or []):
        return False
    name = (info.get("process_name") or "").lower()
    title = (info.get("title") or "").lower()
    if any(hint in name for hint in GAME_PROCESS_HINTS):
        return True
    return any(hint.lower() in title for hint in GAME_TITLE_HINTS)


VPN_PROCESS_HINTS = (
    "protonvpn",
    "wireguard",
    "clash",
    "mihomo",
    "sing-box",
    "singbox",
    "openvpn",
    "tailscale",
    "zerotier",
    "v2ray",
    "nekobox",
)

VPN_INTERFACE_HINTS = (
    "proton",
    "wireguard",
    "wintun",
    "tun",
    "tap",
    "clash",
    "mihomo",
    "sing-box",
    "tailscale",
    "zerotier",
    "openvpn",
)


def interface_has_usable_ip(name, addrs):
    for addr in addrs:
        family = getattr(addr, "family", None)
        family_name = getattr(family, "name", str(family))
        if family_name not in ("AF_INET", "AF_INET6", "2", "23"):
            continue
        value = getattr(addr, "address", "")
        if not value:
            continue
        try:
            ip = ipaddress.ip_address(value.split("%")[0])
        except ValueError:
            continue
        if ip.is_loopback or ip.is_link_local or ip.is_multicast:
            continue
        if ip.version == 6:
            return True
        if ip.version == 4:
            return True
    return False


def detect_vpn_status():
    processes = set()
    try:
        for proc in psutil.process_iter(["name"]):
            name = (proc.info.get("name") or "").lower()
            if any(hint in name for hint in VPN_PROCESS_HINTS):
                processes.add(name)
    except Exception:
        pass

    active_interfaces = []
    try:
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for name, stat in stats.items():
            lowered = name.lower()
            if not any(hint in lowered for hint in VPN_INTERFACE_HINTS):
                continue
            if not getattr(stat, "isup", False):
                continue
            if interface_has_usable_ip(name, addrs.get(name, [])):
                active_interfaces.append(name)
    except Exception:
        pass

    if active_interfaces:
        return "已连接"
    if processes:
        return "客户端运行"
    return "未连接"


def load_config():
    data = load_json(CONFIG, {})
    merged = dict(DEFAULT_CONFIG)
    merged.update(data)
    return merged


def clamp_int(value, low, high, fallback):
    try:
        number = int(value)
    except Exception:
        number = fallback
    return max(low, min(high, number))


def text_font_family(config=None):
    config = config or {}
    family = str(config.get("TextFontFamily") or DEFAULT_CONFIG["TextFontFamily"]).strip()
    return family or DEFAULT_CONFIG["TextFontFamily"]


def qss_font_family(config=None):
    family = text_font_family(config)
    return family.replace("\\", "\\\\").replace('"', '\\"')


def normalize_color(value, fallback):
    color = QColor(str(value or "").strip())
    if color.isValid():
        return color.name()
    return fallback


def rgba_from_hex(value, alpha, fallback):
    color = QColor(normalize_color(value, fallback))
    return f"rgba({color.red()},{color.green()},{color.blue()},{alpha})"


def color_with_alpha(value, alpha, fallback):
    color = QColor(normalize_color(value, fallback))
    color.setAlpha(max(0, min(255, int(alpha))))
    return color


def readable_text_color(value):
    color = QColor(normalize_color(value, "#111827"))
    luminance = (color.red() * 299 + color.green() * 587 + color.blue() * 114) / 1000
    return "#0b1220" if luminance > 150 else "#f8fafc"


def bubble_colors(config=None):
    config = config or {}
    return {
        "background": normalize_color(config.get("BubbleBackgroundColor"), DEFAULT_CONFIG["BubbleBackgroundColor"]),
        "text": normalize_color(config.get("BubbleTextColor"), DEFAULT_CONFIG["BubbleTextColor"]),
        "border": normalize_color(config.get("BubbleBorderColor"), DEFAULT_CONFIG["BubbleBorderColor"]),
    }


def bubble_frame(config=None):
    config = config or {}
    return {
        "width": clamp_int(config.get("BubbleBorderWidth"), 1, 8, DEFAULT_CONFIG["BubbleBorderWidth"]),
        "radius": clamp_int(config.get("BubbleBorderRadius"), 4, 32, DEFAULT_CONFIG["BubbleBorderRadius"]),
    }


def text_font_sizes(config=None):
    config = config or {}
    return {
        "bubble": clamp_int(config.get("BubbleFontSize"), 10, 24, DEFAULT_CONFIG["BubbleFontSize"]),
        "desktop": clamp_int(config.get("DesktopLabelFontSize"), 9, 20, DEFAULT_CONFIG["DesktopLabelFontSize"]),
        "dialog": clamp_int(config.get("DialogFontSize"), 11, 22, DEFAULT_CONFIG["DialogFontSize"]),
        "menu": clamp_int(config.get("MenuFontSize"), 10, 22, DEFAULT_CONFIG["MenuFontSize"]),
    }


def bubble_text_flags(config=None):
    config = config or {}
    return {
        "bold": bool(config.get("BubbleFontBold", DEFAULT_CONFIG["BubbleFontBold"])),
        "italic": bool(config.get("BubbleFontItalic", DEFAULT_CONFIG["BubbleFontItalic"])),
    }


def bubble_padding(config=None):
    size = text_font_sizes(config)["bubble"]
    return max(5, size // 3), max(8, int(size * 0.72))


def bubble_tail_size(config=None):
    size = text_font_sizes(config)["bubble"]
    return max(18, int(size * 1.45)), max(12, int(size * 0.86))


def bubble_tail_tip_bounds(width, config=None):
    frame = bubble_frame(config)
    tail_width, _tail_height = bubble_tail_size(config)
    total_width = max(1, int(width))
    inset = int(frame["width"] / 2 + 0.5)
    min_tip = inset + frame["radius"] + tail_width
    max_tip = total_width - 1 - inset - frame["radius"] - tail_width
    if max_tip < min_tip:
        center = total_width // 2
        return center, center
    return min_tip, max_tip


def bubble_tail_tip_x(width, config=None, side="left", target_x=None):
    min_tip, max_tip = bubble_tail_tip_bounds(width, config)
    if target_x is not None:
        return min(max(int(round(target_x)), min_tip), max_tip)
    return min_tip if side == "left" else max_tip


def pet_bubble_anchor_x(target_rect, avoid_center=False, side_hint=1):
    center = target_rect.center().x()
    if not avoid_center:
        return center
    width = max(1, target_rect.width())
    margin = max(8, min(24, width // 5))
    left = target_rect.left() + margin
    right = target_rect.right() - margin
    if right <= left:
        return center
    shoulder_offset = max(18, min(72, int(width * 0.28)))
    side = -1 if side_hint < 0 else 1
    return min(max(center + side * shoulder_offset, left), right)


def bubble_font_qss(config=None):
    size = text_font_sizes(config)["bubble"]
    family = qss_font_family(config)
    flags = bubble_text_flags(config)
    weight = 700 if flags["bold"] else 400
    style = "italic" if flags["italic"] else "normal"
    return f'font:{style} {weight} {size}px "{family}";'


def bubble_offset(config=None):
    config = config or {}
    return (
        clamp_int(config.get("BubbleOffsetX"), -1200, 1200, DEFAULT_CONFIG["BubbleOffsetX"]),
        clamp_int(config.get("BubbleOffsetY"), -1200, 1200, DEFAULT_CONFIG["BubbleOffsetY"]),
    )


def bubble_manual_size(config=None):
    config = config or {}
    return (
        clamp_int(config.get("BubbleWidth"), 0, 680, DEFAULT_CONFIG["BubbleWidth"]),
        clamp_int(config.get("BubbleHeight"), 0, 360, DEFAULT_CONFIG["BubbleHeight"]),
    )


def update_saved_bubble_offset(config, x, y):
    config["BubbleOffsetX"] = int(x)
    config["BubbleOffsetY"] = int(y)
    saved = load_config()
    saved["BubbleOffsetX"] = int(x)
    saved["BubbleOffsetY"] = int(y)
    save_json(CONFIG, saved)


def update_saved_bubble_size(config, width, height):
    width = clamp_int(width, 140, 680, 260)
    height = clamp_int(height, 52, 360, 86)
    config["BubbleWidth"] = int(width)
    config["BubbleHeight"] = int(height)
    saved = load_config()
    saved["BubbleWidth"] = int(width)
    saved["BubbleHeight"] = int(height)
    save_json(CONFIG, saved)


def app_dialog_style(config=None):
    sizes = text_font_sizes(config)
    base = sizes["dialog"]
    title = base + 7
    hint = max(10, base - 2)
    family = qss_font_family(config)
    return f"""
QDialog{{
    background:#10141f;
    color:#e5e7eb;
    font:{base}px "{family}";
}}
QLabel#title{{
    color:#f8fafc;
    font-size:{title}px;
    font-weight:700;
    padding:0 0 2px 0;
}}
QLabel#hint{{
    color:#fcd34d;
    font-size:{hint}px;
    padding:0 0 4px 0;
}}
QLabel#sectionTitle{{
    color:#93c5fd;
    font-size:{base}px;
    font-weight:700;
    padding:10px 0 2px 0;
}}
QLabel#panel,QTextEdit#panel,QPlainTextEdit#panel{{
    background:rgba(21,27,38,185);
    color:#e5e7eb;
    border:1px solid rgba(148,163,184,80);
    border-radius:14px;
    padding:12px;
}}
QScrollArea{{
    background:transparent;
    border:0;
}}
QScrollArea > QWidget > QWidget{{
    background:transparent;
}}
QWidget#settingsTabPage{{
    background:transparent;
}}
QComboBox,QFontComboBox,QLineEdit,QPlainTextEdit,QTextEdit,QSpinBox,QDateTimeEdit{{
    background:rgba(18,24,34,218);
    color:#f8fafc;
    border:1px solid rgba(148,163,184,82);
    border-radius:12px;
    padding:9px 10px;
    selection-background-color:#0ea5e9;
}}
QComboBox:hover,QFontComboBox:hover,QLineEdit:hover,QPlainTextEdit:hover,QTextEdit:hover,QSpinBox:hover,QDateTimeEdit:hover{{
    border:1px solid rgba(129,140,248,155);
}}
QComboBox:focus,QFontComboBox:focus,QLineEdit:focus,QPlainTextEdit:focus,QTextEdit:focus,QSpinBox:focus,QDateTimeEdit:focus{{
    border:1px solid #60a5fa;
}}
QTextEdit{{
    background:rgba(2,6,23,190);
}}
QPlainTextEdit{{
    background:rgba(2,6,23,170);
}}
QComboBox QAbstractItemView,QFontComboBox QAbstractItemView{{
    background:#0f172a;
    color:#f8fafc;
    border:1px solid #334155;
    selection-background-color:#2563eb;
    selection-color:white;
}}
QPushButton{{
    background:rgba(31,41,55,225);
    color:#f8fafc;
    border:1px solid rgba(100,116,139,150);
    border-radius:11px;
    padding:8px 14px;
    min-height:18px;
}}
QPushButton:hover{{
    background:rgba(51,65,85,245);
    border:1px solid rgba(148,163,184,180);
}}
QPushButton#sendButton{{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0ea5e9,stop:1 #f59e0b);
    color:#0b1220;
    border:1px solid rgba(251,191,36,210);
    font-weight:700;
}}
QPushButton#sendButton:hover{{
    background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #38bdf8,stop:1 #fbbf24);
}}
QPushButton#ghostButton{{
    background:rgba(15,23,42,120);
    color:#cbd5e1;
}}
QPushButton#dangerButton{{
    background:rgba(127,29,29,190);
    border:1px solid rgba(248,113,113,180);
    color:#fee2e2;
}}
QPushButton#dangerButton:hover{{
    background:rgba(185,28,28,220);
}}
QTabWidget#settingsTabs::pane{{
    border:1px solid rgba(99,102,241,85);
    border-radius:14px;
    background:rgba(15,23,42,125);
    padding:10px;
}}
QTabBar::tab{{
    background:rgba(15,23,42,120);
    color:#cbd5e1;
    border:1px solid rgba(71,85,105,150);
    border-bottom:0;
    border-top-left-radius:10px;
    border-top-right-radius:10px;
    padding:8px 14px;
    margin-right:4px;
}}
QTabBar::tab:selected{{
    background:rgba(37,99,235,185);
    color:white;
    border-color:rgba(125,211,252,180);
}}
QTabBar::tab:hover{{
    background:rgba(51,65,85,210);
}}
QScrollBar:vertical{{
    background:rgba(15,23,42,180);
    width:10px;
    margin:2px;
}}
QScrollBar::handle:vertical{{
    background:#64748b;
    border-radius:5px;
    min-height:32px;
}}
QScrollBar::add-line:vertical,QScrollBar::sub-line:vertical{{
    height:0px;
}}
QListWidget{{
    background:rgba(2,6,23,165);
    color:#f8fafc;
    border:1px solid rgba(99,102,241,85);
    border-radius:14px;
    padding:8px;
}}
QListWidget::item{{
    background:rgba(30,41,59,195);
    border:1px solid rgba(71,85,105,150);
    border-radius:12px;
    padding:11px;
    margin:5px 2px;
}}
QListWidget::item:selected{{
    background:rgba(37,99,235,210);
    border:1px solid rgba(147,197,253,220);
}}
QCheckBox{{
    color:#e5e7eb;
    spacing:8px;
}}
QCheckBox::indicator{{
    width:18px;
    height:18px;
}}
"""


def bubble_style(config=None):
    colors = bubble_colors(config)
    frame = bubble_frame(config)
    pad_y, pad_x = bubble_padding(config)
    background = rgba_from_hex(colors["background"], 225, DEFAULT_CONFIG["BubbleBackgroundColor"])
    border = rgba_from_hex(colors["border"], 180, DEFAULT_CONFIG["BubbleBorderColor"])
    return (
        f"QLabel{{background:{background};color:{colors['text']};"
        f"border:{frame['width']}px solid {border};border-radius:{frame['radius']}px;"
        f"padding:{pad_y}px {pad_x}px;{bubble_font_qss(config)}}}"
    )


def bubble_text_style(config=None):
    colors = bubble_colors(config)
    frame = bubble_frame(config)
    pad_y, pad_x = bubble_padding(config)
    _tail_width, tail_height = bubble_tail_size(config)
    return (
        f"QLabel{{background:transparent;color:{colors['text']};"
        f"border:{frame['width']}px solid transparent;border-radius:{frame['radius']}px;"
        f"padding:{pad_y}px {pad_x}px {pad_y + tail_height}px {pad_x}px;{bubble_font_qss(config)}}}"
    )


def desktop_label_style(config=None, kind="status"):
    size = text_font_sizes(config)["desktop"]
    family = qss_font_family(config)
    if kind == "accessory":
        return (
            "QLabel{background:rgba(15,23,42,155);color:#f8fafc;"
            "border:1px solid rgba(226,232,240,90);border-radius:10px;"
            f'padding:3px 8px;font:{size}px "{family}";}}'
        )
    return (
        "QLabel{background:rgba(17,24,39,205);"
        "border:1px solid rgba(251,191,36,120);border-radius:14px;"
        f'padding:7px 10px;color:#f8fafc;font:{size}px "{family}";}}'
    )


def smart_menu_style(config=None):
    sizes = text_font_sizes(config)
    base = sizes["menu"]
    family = qss_font_family(config)
    title = base + 7
    section = max(10, base - 1)
    card = base + 1
    return f"""
QDialog#smartMenu{{
    background:rgba(15,23,42,232);
    border:1px solid rgba(148,163,184,95);
    border-radius:18px;
}}
QScrollArea#smartMenuScroll,QWidget#smartMenuContent{{
    background:transparent;
    border:none;
}}
QDialog#smartMenu QScrollBar:vertical{{
    background:rgba(15,23,42,80);
    width:8px;
    margin:4px 0 4px 0;
    border-radius:4px;
}}
QDialog#smartMenu QScrollBar::handle:vertical{{
    background:rgba(148,163,184,150);
    border-radius:4px;
    min-height:28px;
}}
QDialog#smartMenu QScrollBar::add-line:vertical,QDialog#smartMenu QScrollBar::sub-line:vertical{{
    height:0;
}}
QLabel#smartTitle{{
    color:#f8fafc;
    font:700 {title}px "{family}";
}}
QLabel#smartHint{{
    color:#bfdbfe;
    font:{base}px "{family}";
}}
QLabel#smartSection{{
    color:#93c5fd;
    font:700 {section}px "{family}";
    padding:2px 0 0 2px;
}}
QLabel#smartStatus,QLabel#smartCard{{
    color:#e5e7eb;
    background:rgba(30,41,59,170);
    border:1px solid rgba(71,85,105,135);
    border-radius:12px;
    padding:10px 12px;
    font:{base}px "{family}";
}}
QLabel#smartMetric{{
    color:#e5e7eb;
    background:rgba(17,24,39,188);
    border:1px solid rgba(148,163,184,92);
    border-radius:12px;
    padding:9px 10px;
    font:{base}px "{family}";
}}
QPushButton#smartMetricButton{{
    color:#e5e7eb;
    background:rgba(17,24,39,188);
    border:1px solid rgba(148,163,184,92);
    border-radius:12px;
    padding:8px 10px;
    text-align:left;
    font:{base}px "{family}";
}}
QPushButton#smartMetricButton:hover{{
    background:rgba(30,41,59,230);
    border:1px solid rgba(125,211,252,170);
}}
QLabel#smartMetricTitle{{
    color:#fbbf24;
    font:700 {section}px "{family}";
    padding:0 0 2px 0;
}}
QLabel#smartMetricDetail{{
    color:#e5e7eb;
    background:transparent;
    border:none;
    padding:0;
    font:{base}px "{family}";
}}
QPushButton#smartPrimary{{
    background:rgba(14,165,233,210);
    color:#08111f;
    border:1px solid rgba(125,211,252,210);
    border-radius:13px;
    padding:10px 12px;
    text-align:left;
    font:700 {card}px "{family}";
}}
QPushButton#smartPrimary:hover{{
    background:rgba(56,189,248,230);
}}
QPushButton#smartSecondary{{
    background:rgba(30,41,59,205);
    color:#f8fafc;
    border:1px solid rgba(71,85,105,175);
    border-radius:12px;
    padding:8px 10px;
    text-align:left;
    font:{base}px "{family}";
}}
QPushButton#smartSecondary:hover{{
    background:rgba(51,65,85,230);
}}
QPushButton#smartSmall{{
    background:rgba(15,23,42,180);
    color:#e2e8f0;
    border:1px solid rgba(71,85,105,145);
    border-radius:10px;
    padding:7px 9px;
    font:{base}px "{family}";
}}
QPushButton#smartSmall:hover{{
    background:rgba(51,65,85,220);
}}
"""


def set_active_text_config(config=None):
    global APP_DIALOG_STYLE
    APP_DIALOG_STYLE = app_dialog_style(config or DEFAULT_CONFIG)


def text_header(value):
    if not value:
        return ""
    pieces = []
    for chunk, enc in decode_header(value):
        if isinstance(chunk, bytes):
            pieces.append(chunk.decode(enc or "utf-8", errors="replace"))
        else:
            pieces.append(chunk)
    return "".join(pieces)


def mail_clean_text(value, limit=420):
    text = str(value or "")
    text = html.unescape(text)
    text = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", text)
    text = re.sub(r"(?s)<br\s*/?>", "\n", text)
    text = re.sub(r"(?s)</p\s*>", "\n", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text)
    text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    text = text.strip()
    if limit and len(text) > limit:
        return text[: max(0, limit - 1)].rstrip() + "…"
    return text


def mail_part_text(part):
    content_type = part.get_content_type()
    if content_type not in {"text/plain", "text/html"}:
        return ""
    disposition = str(part.get_content_disposition() or "").lower()
    if disposition == "attachment":
        return ""
    try:
        text = part.get_content()
    except Exception:
        payload = part.get_payload(decode=True)
        if not payload:
            return ""
        charset = part.get_content_charset() or "utf-8"
        text = payload.decode(charset, errors="replace")
    return mail_clean_text(text, limit=0) if content_type == "text/html" else mail_clean_text(text, limit=0)


def mail_body_preview(message, limit=420):
    plain_parts = []
    html_parts = []
    try:
        parts = message.walk() if message.is_multipart() else [message]
    except Exception:
        parts = [message]
    for part in parts:
        content_type = part.get_content_type()
        text = mail_part_text(part)
        if not text:
            continue
        if content_type == "text/plain":
            plain_parts.append(text)
        elif content_type == "text/html":
            html_parts.append(text)
    text = "\n".join(plain_parts or html_parts)
    return mail_clean_text(text, limit=limit)


def normalize_mail_code(value):
    code = re.sub(r"[\s\-_:：]", "", str(value or "").strip())
    if not re.fullmatch(r"[A-Za-z0-9]{4,10}", code):
        return ""
    if not any(ch.isdigit() for ch in code):
        return ""
    return code.upper()


def extract_mail_verification_code(subject, preview):
    text = f"{subject or ''}\n{preview or ''}"
    direct_keywords = (
        "验证码",
        "校验码",
        "动态码",
        "一次性代码",
        "验证代码",
    )
    lowered = text.lower()
    english_keyword = re.search(
        r"\b(?:verification code|security code|one[- ]time code|login code|otp|code)\b",
        lowered,
    )
    if not any(keyword in lowered for keyword in direct_keywords) and not english_keyword:
        return ""
    patterns = [
        r"(?:验证码|校验码|动态码|一次性代码|验证代码|verification code|security code|one[- ]time code|login code|otp|\bcode\b)\D{0,24}([A-Za-z0-9][A-Za-z0-9\s\-]{2,16}[A-Za-z0-9])",
        r"([A-Za-z0-9][A-Za-z0-9\s\-]{2,16}[A-Za-z0-9])\D{0,18}(?:验证码|校验码|动态码|verification code|security code|otp|\bcode\b)",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            code = normalize_mail_code(match.group(1))
            if code:
                return code
    for match in re.finditer(r"\b\d{4,8}\b", text):
        code = normalize_mail_code(match.group(0))
        if code:
            return code
    return ""


def mail_display_text(item):
    subject = str(item.get("subject") or "(无标题)")
    sender = str(item.get("sender") or "")
    date = str(item.get("date") or "")
    code = str(item.get("verification_code") or "").strip()
    preview = mail_clean_text(item.get("preview", ""), limit=220).replace("\n", " ")
    lines = [subject]
    if sender:
        lines.append(sender)
    if date:
        lines.append(date)
    if code:
        lines.append(f"验证码：{code}")
    if preview:
        lines.append(f"内容：{preview}")
    return "\n".join(lines)


def mail_date_sort_value(value):
    try:
        return parsedate_to_datetime(str(value)).timestamp()
    except Exception:
        return 0


MAIL_FETCH_TIMEOUT = 8
MAIL_CACHE_MAX_AGE_SECONDS = 10 * 60
MAIL_HEADER_QUERY = "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])"
MAIL_MESSAGE_PREVIEW_BYTES = 256 * 1024
MAIL_MESSAGE_QUERY = f"(BODY.PEEK[]<0.{MAIL_MESSAGE_PREVIEW_BYTES}>)"


def parse_iso_datetime(value):
    try:
        return datetime.fromisoformat(str(value))
    except Exception:
        return None


def parse_imap_unseen_count(data):
    raw = b" ".join(part for part in (data or []) if isinstance(part, bytes))
    match = re.search(rb"UNSEEN\s+(\d+)", raw, re.I)
    if not match:
        return None
    try:
        return int(match.group(1))
    except Exception:
        return None


def fetch_imap_headers_batch(client, mail_ids):
    if not mail_ids:
        return []
    id_text = ",".join(mid.decode("ascii", errors="ignore") if isinstance(mid, bytes) else str(mid) for mid in mail_ids)
    if not id_text:
        return []
    try:
        _status, msg_data = client.fetch(id_text, MAIL_MESSAGE_QUERY)
    except Exception:
        _status, msg_data = client.fetch(id_text, MAIL_HEADER_QUERY)
    parsed = []
    for item in msg_data or []:
        if not isinstance(item, tuple) or len(item) < 2 or not item[1]:
            continue
        meta = item[0] if isinstance(item[0], bytes) else b""
        match = re.match(rb"\s*(\d+)", meta)
        mid = match.group(1).decode("ascii", errors="ignore") if match else ""
        try:
            msg = BytesParser(policy=default).parsebytes(item[1])
        except Exception:
            continue
        parsed.append((mid, msg))
    order = {
        (mid.decode("ascii", errors="ignore") if isinstance(mid, bytes) else str(mid)): index
        for index, mid in enumerate(mail_ids)
    }
    parsed.sort(key=lambda item: order.get(item[0], -1), reverse=True)
    return parsed


def update_mail_cache(messages, total_unread, provider_filter=None):
    state = load_json(MAIL_STATE, {})
    unread_by_provider = state.get("last_unread_by_provider", {})
    if not isinstance(unread_by_provider, dict):
        unread_by_provider = {}

    if provider_filter:
        cached = state.get("last_mail_messages", [])
        if not isinstance(cached, list):
            cached = []
        messages = [
            message for message in cached
            if (message.get("provider") or "qq") != provider_filter
        ] + list(messages)
        unread_by_provider[provider_filter] = int(total_unread or 0)
        total_unread = sum(int(value or 0) for value in unread_by_provider.values())
    else:
        unread_by_provider = {}
        for message in messages:
            provider = message.get("provider") or "qq"
            unread_by_provider[provider] = int(message.get("account_unread_count", 0) or 0)

    state["last_unread_by_provider"] = unread_by_provider
    state["last_unread_count"] = int(total_unread or 0)
    state["last_mail_checked_at"] = datetime.now().isoformat(timespec="seconds")
    ordered = sorted(messages, key=lambda item: mail_date_sort_value(item.get("date", "")), reverse=True)
    state["last_mail_messages"] = [
        {
            key: message.get(key, "")
            for key in (
                "id",
                "subject",
                "sender",
                "date",
                "preview",
                "verification_code",
                "unread_count",
                "account_unread_count",
                "account_label",
                "account_user",
                "provider",
                "inbox_url",
            )
        }
        for message in ordered[:60]
    ]
    save_json(MAIL_STATE, state)


def cached_mail_messages(max_age=MAIL_CACHE_MAX_AGE_SECONDS):
    state = load_json(MAIL_STATE, {})
    checked = parse_iso_datetime(state.get("last_mail_checked_at", ""))
    if not checked or (datetime.now() - checked).total_seconds() > max_age:
        return []
    messages = state.get("last_mail_messages", [])
    return messages if isinstance(messages, list) else []


def mail_cache_age_seconds():
    state = load_json(MAIL_STATE, {})
    checked = parse_iso_datetime(state.get("last_mail_checked_at", ""))
    if not checked:
        return None
    return max(0, (datetime.now() - checked).total_seconds())


def fetch_unread_mail_account(account, limit=20):
    host = account.get("host", "").strip()
    user = account.get("user", "").strip()
    pwd = account.get("password", "")
    port = normalized_mail_port(host, account.get("port", 993))
    if not host or not user or not pwd:
        return [], "邮件未配置完整：需要 IMAP 主机、邮箱账号和授权码。", 0

    last_error = None
    for _ in range(1):
        client = None
        try:
            client = imaplib.IMAP4_SSL(host, port, timeout=MAIL_FETCH_TIMEOUT)
            client.login(user, pwd)
            unread_count = None
            try:
                _status, status_data = client.status("INBOX", "(UNSEEN)")
                unread_count = parse_imap_unseen_count(status_data)
            except Exception:
                unread_count = None
            client.select("INBOX", readonly=True)
            _status, ids = client.search(None, "UNSEEN")
            unread_ids = ids[0].split() if ids and ids[0] else []
            if unread_count is None:
                unread_count = len(unread_ids)
            mail_ids = unread_ids[-max(1, int(limit)):]
            messages = []
            provider = account.get("provider") or mail_provider_for(host, user)
            for mid, msg in fetch_imap_headers_batch(client, mail_ids):
                subject = text_header(msg.get("Subject", "")).strip() or "(无标题)"
                preview = mail_body_preview(msg)
                verification_code = extract_mail_verification_code(subject, preview)
                messages.append(
                    {
                        "id": mid,
                        "subject": subject,
                        "sender": text_header(msg.get("From", "")).strip(),
                        "date": text_header(msg.get("Date", "")).strip(),
                        "preview": preview,
                        "verification_code": verification_code,
                        "unread_count": unread_count,
                        "account_unread_count": unread_count,
                        "account_label": account.get("label") or user,
                        "account_user": user,
                        "provider": provider,
                        "inbox_url": mail_inbox_url(provider),
                    }
                )
            try:
                client.logout()
            except Exception:
                pass
            return messages, "", unread_count
        except Exception as exc:
            last_error = exc
            try:
                if client:
                    client.logout()
            except Exception:
                pass
    msg = str(last_error)
    if "10054" in msg or "handshake" in msg.lower() or "timed out" in msg.lower():
        label = account.get("label") or user or host
        return [], f"{label} 邮箱服务器暂时断开了 IMAP 连接。可以稍后刷新，或打开网页邮箱查看。", 0
    return [], f"邮件读取失败：{last_error}", 0


def fetch_unread_mail_result(config, limit=20, provider_filter=None):
    accounts = mail_accounts_from_config(config)
    if provider_filter:
        accounts = [account for account in accounts if account.get("provider") == provider_filter]
    if not accounts:
        return {"messages": [], "error": "邮件未配置完整：需要 IMAP 主机、邮箱账号和授权码。", "total_unread": 0}

    all_messages = []
    errors = []
    total_unread = 0
    per_account_limit = max(1, limit)
    max_workers = min(len(accounts), 4)
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_map = {
            executor.submit(fetch_unread_mail_account, account, per_account_limit): account
            for account in accounts
        }
        for future in as_completed(future_map):
            account = future_map[future]
            try:
                messages, error, unread_count = future.result()
            except Exception as exc:
                messages, error, unread_count = [], f"邮件读取失败：{exc}", 0
            if error:
                errors.append(f"{account.get('label') or account.get('user')}: {error}")
                continue
            total_unread += int(unread_count or 0)
            all_messages.extend(messages)
    for message in all_messages:
        message["unread_count"] = total_unread
    all_messages.sort(key=lambda item: mail_date_sort_value(item.get("date", "")), reverse=True)
    if all_messages:
        update_mail_cache(all_messages, total_unread, provider_filter=provider_filter)
        return {"messages": all_messages, "error": "", "total_unread": total_unread, "errors": errors}
    if not errors:
        update_mail_cache([], total_unread, provider_filter=provider_filter)
        return {"messages": [], "error": "", "total_unread": total_unread, "errors": []}
    if errors:
        return {"messages": [], "error": "\n".join(errors), "total_unread": total_unread, "errors": errors}
    return {"messages": [], "error": "", "total_unread": total_unread, "errors": []}


def fetch_unread_mail(config, limit=20, provider_filter=None):
    result = fetch_unread_mail_result(config, limit, provider_filter=provider_filter)
    return result.get("messages", []), result.get("error", "")


def tesseract_candidates():
    env_path = shutil.which("tesseract")
    candidates = [Path(env_path)] if env_path else []
    candidates.append(LOCAL_TESSERACT_EXE)
    program_files = [Path(os.environ.get("ProgramFiles", r"C:\Program Files"))]
    x86 = os.environ.get("ProgramFiles(x86)")
    if x86:
        program_files.append(Path(x86))
    candidates.extend(base / "Tesseract-OCR" / "tesseract.exe" for base in program_files)
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    if local:
        candidates.extend(
            [
                local / "Programs" / "Tesseract-OCR" / "tesseract.exe",
                local / "Tesseract-OCR" / "tesseract.exe",
            ]
        )
    return candidates


def detect_tesseract_path():
    for path in tesseract_candidates():
        try:
            if path and path.exists() and path.is_file():
                return str(path)
        except Exception:
            continue
    return ""


def configured_tesseract_path(config, persist=False):
    tesseract = str(config.get("TesseractPath", "") or "").strip()
    if tesseract and Path(tesseract).exists():
        return tesseract
    detected = detect_tesseract_path()
    if detected:
        config["TesseractPath"] = detected
        if persist:
            saved = load_config()
            saved["TesseractPath"] = detected
            save_json(CONFIG, saved)
        return detected
    return ""


def configured_tessdata_dir(config=None):
    config = config or {}
    configured = str(config.get("TessdataPath", "") or "").strip()
    candidates = []
    if configured:
        candidates.append(Path(configured))
    candidates.append(LOCAL_TESSDATA_DIR)
    tesseract = str(config.get("TesseractPath", "") or "").strip()
    if tesseract:
        candidates.append(Path(tesseract).parent / "tessdata")
    for path in candidates:
        try:
            if path.exists() and (path / "eng.traineddata").exists():
                return str(path)
        except Exception:
            continue
    return ""


def run_tesseract_ocr(config, image_path: Path):
    tesseract = configured_tesseract_path(config, persist=True)
    if not tesseract:
        return "", f"截图已保存：{image_path.name}。还没有配置 Tesseract 路径，暂时不能 OCR。"
    out_base = str(image_path.with_suffix(""))
    command = [tesseract, str(image_path), out_base, "-l", config.get("OcrLanguage", "chi_sim+eng")]
    tessdata = configured_tessdata_dir(config)
    if tessdata:
        command.extend(["--tessdata-dir", tessdata])
    try:
        subprocess.run(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
            check=False,
        )
    except Exception as exc:
        return "", f"OCR 调用失败：{exc}"
    txt = image_path.with_suffix(".txt")
    content = txt.read_text(encoding="utf-8", errors="ignore").strip() if txt.exists() else ""
    if not content:
        return "", f"截图已保存：{image_path.name}，但 OCR 没识别出文字。"
    return content, ""


def human_bytes(value):
    size = float(value or 0)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024 or unit == "TB":
            return f"{size:.1f}{unit}" if unit != "B" else f"{int(size)}B"
        size /= 1024


def battery_snapshot(provider=None):
    source = provider or getattr(psutil, "sensors_battery", None)
    if source is None:
        return {"available": False, "percent": None, "plugged": None, "seconds_left": None}
    try:
        battery = source()
    except Exception:
        battery = None
    if battery is None:
        return {"available": False, "percent": None, "plugged": None, "seconds_left": None}
    try:
        percent = max(0.0, min(100.0, float(battery.percent)))
    except Exception:
        percent = 0.0
    plugged = bool(getattr(battery, "power_plugged", False))
    seconds_left = getattr(battery, "secsleft", None)
    unknown_values = {
        getattr(psutil, "POWER_TIME_UNKNOWN", -1),
        getattr(psutil, "POWER_TIME_UNLIMITED", -2),
    }
    if plugged or seconds_left in unknown_values:
        seconds_left = None
    else:
        try:
            seconds_left = max(0, int(seconds_left))
        except Exception:
            seconds_left = None
    return {
        "available": True,
        "percent": percent,
        "plugged": plugged,
        "seconds_left": seconds_left,
    }


def battery_time_text(seconds):
    if seconds is None:
        return ""
    minutes = max(0, int(seconds) // 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"约 {hours} 小时 {minutes} 分钟"
    return f"约 {minutes} 分钟"


def battery_status_lines(config=None, snapshot=None):
    config = config or {}
    snapshot = snapshot or battery_snapshot()
    if not snapshot.get("available"):
        return ["当前设备未检测到电池。", "仍可打开 Windows 电源设置调整睡眠和屏幕策略。"]
    percent = float(snapshot.get("percent", 0))
    plugged = bool(snapshot.get("plugged"))
    if plugged and percent >= 99.5:
        state = "已充满"
    elif plugged:
        state = "正在充电"
    else:
        state = "正在使用电池"
    lines = [f"电量 {percent:.0f}% · {state}"]
    remaining = battery_time_text(snapshot.get("seconds_left"))
    if remaining:
        lines.append(f"预计剩余 {remaining}")
    if config.get("BatteryAlertsEnabled", True):
        lines.append(
            f"低电量 {int(config.get('BatteryLowPercent', 20))}% 提醒 · "
            f"充至 {int(config.get('BatteryFullPercent', 95))}% 提示拔电"
        )
    else:
        lines.append("电池提醒已关闭")
    return lines


def battery_alert_issues(config=None, snapshot=None):
    config = config or {}
    snapshot = snapshot or battery_snapshot()
    if not config.get("BatteryAlertsEnabled", True) or not snapshot.get("available"):
        return []
    percent = float(snapshot.get("percent", 0))
    plugged = bool(snapshot.get("plugged"))
    low = max(5, min(40, int(config.get("BatteryLowPercent", 20))))
    full = max(80, min(100, int(config.get("BatteryFullPercent", 95))))
    if not plugged and percent <= low:
        remaining = battery_time_text(snapshot.get("seconds_left"))
        suffix = f"，预计还能使用 {remaining}" if remaining else ""
        return [("battery_low", f"电池仅剩 {percent:.0f}%{suffix}，请及时接通电源")]
    if plugged and percent >= full:
        return [("battery_full", f"电池已充至 {percent:.0f}%，可以拔掉电源减少长期满电停留")]
    return []


def disk_usage_summary():
    parts = []
    for drive in ("C:\\", "D:\\"):
        try:
            total, used, free = shutil.disk_usage(drive)
            parts.append(f"{drive[0]}盘剩余 {human_bytes(free)} / {human_bytes(total)}")
        except Exception:
            continue
    return "；".join(parts) if parts else "磁盘空间读取失败"


def powershell_json(script, timeout=4):
    if not sys.platform.startswith("win"):
        return None
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=timeout,
            creationflags=0x08000000,
        )
        text = (completed.stdout or "").strip()
        if completed.returncode != 0 or not text:
            return None
        return json.loads(text)
    except Exception:
        return None


def as_list(value):
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def hardware_info_lines():
    lines = ["", "电脑硬件配置"]

    cpu_data = powershell_json(
        "Get-CimInstance Win32_Processor | "
        "Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | "
        "ConvertTo-Json -Compress"
    )
    cpu_name = ""
    cpu_cores = psutil.cpu_count(logical=False) or 0
    cpu_threads = psutil.cpu_count(logical=True) or 0
    cpu_clock = ""
    if isinstance(cpu_data, dict):
        cpu_name = str(cpu_data.get("Name") or "").strip()
        cpu_cores = int(cpu_data.get("NumberOfCores") or cpu_cores or 0)
        cpu_threads = int(cpu_data.get("NumberOfLogicalProcessors") or cpu_threads or 0)
        if cpu_data.get("MaxClockSpeed"):
            cpu_clock = f"{float(cpu_data.get('MaxClockSpeed')) / 1000:.2f}GHz"
    if not cpu_name:
        cpu_name = platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "未知 CPU")
    if not cpu_clock:
        try:
            freq = psutil.cpu_freq()
            if freq and freq.max:
                cpu_clock = f"{freq.max / 1000:.2f}GHz"
        except Exception:
            cpu_clock = ""
    lines.append(f"CPU：{cpu_name}（{cpu_cores} 核 / {cpu_threads} 线程{('，' + cpu_clock) if cpu_clock else ''}）")

    mem = psutil.virtual_memory()
    lines.append(f"内存：{human_bytes(mem.total)}（当前可用 {human_bytes(mem.available)}）")

    gpu_data = powershell_json(
        "Get-CimInstance Win32_VideoController | "
        "Select-Object Name,AdapterRAM | ConvertTo-Json -Compress"
    )
    gpu_lines = []
    for gpu in as_list(gpu_data):
        if not isinstance(gpu, dict):
            continue
        name = str(gpu.get("Name") or "").strip()
        if not name:
            continue
        ram = gpu.get("AdapterRAM") or 0
        ram_text = f" {human_bytes(ram)}" if isinstance(ram, (int, float)) and ram > 0 else ""
        gpu_lines.append(f"{name}{ram_text}")
    lines.append("显卡：" + ("；".join(gpu_lines[:3]) if gpu_lines else "未知"))

    disk_parts = []
    try:
        for partition in psutil.disk_partitions(all=False):
            mount = partition.mountpoint
            if not mount or not Path(mount).exists():
                continue
            try:
                usage = shutil.disk_usage(mount)
            except Exception:
                continue
            mount_label = mount.rstrip("\\")
            disk_parts.append(f"{mount_label} {human_bytes(usage.free)} 可用 / {human_bytes(usage.total)}")
    except Exception:
        pass
    lines.append("磁盘：" + ("；".join(disk_parts[:6]) if disk_parts else disk_usage_summary()))

    pc_data = powershell_json(
        "Get-CimInstance Win32_ComputerSystem | "
        "Select-Object Manufacturer,Model,SystemType | ConvertTo-Json -Compress"
    )
    if isinstance(pc_data, dict):
        vendor = " ".join(str(pc_data.get(key) or "").strip() for key in ("Manufacturer", "Model")).strip()
        if vendor:
            lines.append(f"设备：{vendor}")

    os_data = powershell_json(
        "Get-CimInstance Win32_OperatingSystem | "
        "Select-Object Caption,Version,BuildNumber | ConvertTo-Json -Compress"
    )
    if isinstance(os_data, dict) and os_data.get("Caption"):
        lines.append(f"系统：{os_data.get('Caption')} {os_data.get('Version')} Build {os_data.get('BuildNumber')}")
    else:
        lines.append(f"系统：{platform.platform()}")

    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M")
        lines.append(f"启动时间：{boot_time}")
    except Exception:
        pass
    lines.extend(["", "电池 / 电源", *battery_status_lines(DEFAULT_CONFIG)])
    return lines


def system_health_snapshot(config=None):
    config = config or {}
    cpu = psutil.cpu_percent(interval=None)
    mem = psutil.virtual_memory()
    disk_path = BASE.anchor or str(BASE)
    try:
        disk = shutil.disk_usage(disk_path)
        disk_percent = (disk.used / disk.total * 100) if disk.total else 0
    except Exception:
        disk = None
        disk_percent = 0
    try:
        vpn = detect_vpn_status_cached()
    except Exception:
        vpn = "Unknown"
    codex = detect_codex_process_cached()
    cpu_limit = int(config.get("CpuAlertPercent", 90))
    mem_limit = int(config.get("MemoryAlertPercent", 90))
    disk_limit = int(config.get("DiskAlertPercent", 90))
    battery = battery_snapshot()
    issues = []
    if cpu >= cpu_limit:
        issues.append(("cpu", f"CPU 占用 {cpu:.0f}%（阈值 {cpu_limit}%）"))
    if mem.percent >= mem_limit:
        issues.append(("memory", f"内存占用 {mem.percent:.0f}%（阈值 {mem_limit}%）"))
    if disk_percent >= disk_limit:
        free_text = human_bytes(disk.free) if disk else "未知"
        issues.append(("disk", f"{disk_path} 磁盘占用 {disk_percent:.0f}%（剩余 {free_text}）"))
    issues.extend(battery_alert_issues(config, battery))
    return {
        "cpu": cpu,
        "memory_percent": mem.percent,
        "memory_available": mem.available,
        "disk_path": disk_path,
        "disk_percent": disk_percent,
        "disk_free": disk.free if disk else 0,
        "vpn": vpn,
        "codex": codex,
        "battery": battery,
        "issues": issues,
    }


def system_health_lines(config=None):
    snapshot = system_health_snapshot(config)
    lines = ["", "自动异常检测"]
    lines.append(f"自动检测：{'开启' if (config or {}).get('SystemHealthWatchEnabled', True) else '关闭'}")
    lines.append(
        "当前状态："
        f"CPU {snapshot['cpu']:.0f}% / "
        f"内存 {snapshot['memory_percent']:.0f}% / "
        f"{snapshot['disk_path']} 磁盘 {snapshot['disk_percent']:.0f}%"
    )
    lines.append(f"VPN：{snapshot['vpn']}，Codex：{snapshot['codex']}")
    lines.extend(battery_status_lines(config, snapshot.get("battery")))
    if snapshot["issues"]:
        lines.append("需要注意：" + "；".join(text for _key, text in snapshot["issues"]))
    else:
        lines.append("需要注意：暂无")
    return lines


def cleanup_target_definitions():
    local = Path(os.environ.get("LOCALAPPDATA", ""))
    windir = Path(os.environ.get("WINDIR", "C:\\Windows"))
    targets = [
        {
            "id": "user_temp",
            "label": "用户临时文件",
            "path": Path(tempfile.gettempdir()),
            "min_age_hours": 2,
            "note": "常见软件残留的临时文件，跳过最近 2 小时内改动的文件。",
        },
        {
            "id": "windows_temp",
            "label": "Windows 临时文件",
            "path": windir / "Temp",
            "min_age_hours": 24,
            "note": "系统临时目录，权限不足或正在使用的文件会自动跳过。",
        },
        {
            "id": "pip_cache",
            "label": "Python pip 缓存",
            "path": local / "pip" / "Cache",
            "min_age_hours": 24,
            "note": "Python 包下载缓存，删除后需要时会重新下载。",
        },
        {
            "id": "edge_cache",
            "label": "Edge 浏览器缓存",
            "path": local / "Microsoft" / "Edge" / "User Data" / "Default" / "Cache",
            "min_age_hours": 24,
            "note": "只处理缓存目录，不碰 Cookie、登录状态和收藏夹。",
        },
        {
            "id": "edge_code_cache",
            "label": "Edge Code Cache",
            "path": local / "Microsoft" / "Edge" / "User Data" / "Default" / "Code Cache",
            "min_age_hours": 24,
            "note": "网页脚本缓存，浏览器打开时部分文件可能被锁定。",
        },
        {
            "id": "chrome_cache",
            "label": "Chrome 浏览器缓存",
            "path": local / "Google" / "Chrome" / "User Data" / "Default" / "Cache",
            "min_age_hours": 24,
            "note": "只处理缓存目录，不碰 Cookie、登录状态和收藏夹。",
        },
        {
            "id": "codex_pycache",
            "label": "糯米项目 Python 缓存",
            "path": BASE / "__pycache__",
            "min_age_hours": 0,
            "note": "当前桌宠项目的 Python 编译缓存，可安全重建。",
        },
    ]
    return [item for item in targets if item["path"] and item["path"].exists()]


def scan_cleanup_target(target, max_files=8000):
    root = Path(target["path"])
    cutoff = time.time() - float(target.get("min_age_hours", 0)) * 3600
    total = 0
    count = 0
    skipped = 0
    files = []
    truncated = False
    if not root.exists() or not root.is_dir():
        return {**target, "bytes": 0, "count": 0, "skipped": 0, "files": [], "truncated": False}
    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        safe_dirnames = []
        for dirname in dirnames:
            path = Path(dirpath) / dirname
            try:
                if path.is_symlink():
                    continue
            except Exception:
                continue
            safe_dirnames.append(dirname)
        dirnames[:] = safe_dirnames
        for filename in filenames:
            path = Path(dirpath) / filename
            try:
                if path.is_symlink() or not path.is_file():
                    continue
                stat = path.stat()
                if stat.st_mtime > cutoff:
                    continue
                total += stat.st_size
                count += 1
                files.append(str(path))
                if len(files) >= max_files:
                    truncated = True
                    break
            except Exception:
                skipped += 1
        if truncated:
            break
    return {**target, "bytes": total, "count": count, "skipped": skipped, "files": files, "truncated": truncated}


def delete_cleanup_files(items):
    deleted = 0
    freed = 0
    skipped = 0
    roots = []
    for item in items:
        root = Path(item.get("path", ""))
        if root.exists():
            roots.append(root)
        for file_path in item.get("files", []):
            path = Path(file_path)
            try:
                if not path.exists() or not path.is_file() or path.is_symlink():
                    continue
                size = path.stat().st_size
                path.unlink()
                deleted += 1
                freed += size
            except Exception:
                skipped += 1
    for root in roots:
        try:
            for dirpath, _dirnames, _filenames in os.walk(root, topdown=False, followlinks=False):
                path = Path(dirpath)
                if path == root:
                    continue
                try:
                    path.rmdir()
                except Exception:
                    pass
        except Exception:
            pass
    return deleted, freed, skipped


def large_file_roots():
    user = Path(os.environ.get("USERPROFILE", str(Path.home())))
    candidates = [
        user / "Downloads",
        user / "Desktop",
        user / "Documents",
        Path("D:\\CodexProjects"),
    ]
    return [path for path in candidates if path.exists() and path.is_dir()]


DESKTOP_ORGANIZE_CATEGORIES = [
    ("图片", {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic", ".ico"}),
    ("文档", {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".epub"}),
    ("表格演示", {".xls", ".xlsx", ".csv", ".ppt", ".pptx"}),
    ("音视频", {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"}),
    ("压缩包", {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"}),
    ("安装包", {".exe", ".msi", ".msix", ".apk"}),
    ("代码脚本", {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".ps1", ".bat", ".cmd", ".sh", ".cpp", ".c", ".h", ".cs", ".java", ".go", ".rs", ".sql"}),
    ("快捷方式", {".lnk", ".url"}),
]


def desktop_roots():
    user = Path(os.environ.get("USERPROFILE", str(Path.home())))
    one_drive = Path(os.environ.get("OneDrive", user / "OneDrive"))
    candidates = [one_drive / "Desktop", user / "Desktop"]
    roots = []
    seen = set()
    for path in candidates:
        try:
            if not path.exists() or not path.is_dir():
                continue
            key = str(path.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            roots.append(path)
        except Exception:
            continue
    return roots


def desktop_file_category(path):
    suffix = path.suffix.lower()
    for label, extensions in DESKTOP_ORGANIZE_CATEGORIES:
        if suffix in extensions:
            return label
    return "其他"


def is_exam_word_source(path):
    try:
        target = path.resolve()
    except Exception:
        return False
    for candidate in ENGLISH_WORD_SOURCE_CANDIDATES:
        try:
            if candidate.exists() and candidate.resolve() == target:
                return True
        except Exception:
            continue
    return False


def unique_destination_path(path):
    if not path.exists():
        return path
    stem = path.stem
    suffix = path.suffix
    parent = path.parent
    for index in range(1, 1000):
        candidate = parent / f"{stem} ({index}){suffix}"
        if not candidate.exists():
            return candidate
    return parent / f"{stem}-{int(time.time())}{suffix}"


def desktop_organize_plan():
    plan = []
    skipped = 0
    for root in desktop_roots():
        target_root = root / "桌面整理"
        try:
            entries = list(root.iterdir())
        except Exception:
            continue
        for path in entries:
            try:
                if path.name.lower() == "desktop.ini" or path.name.startswith("~$"):
                    skipped += 1
                    continue
                if path == target_root or target_root in path.parents:
                    skipped += 1
                    continue
                if is_exam_word_source(path):
                    skipped += 1
                    continue
                if not path.is_file() or path.is_symlink():
                    skipped += 1
                    continue
                category = desktop_file_category(path)
                dest_dir = target_root / category
                dest = unique_destination_path(dest_dir / path.name)
                stat = path.stat()
                plan.append(
                    {
                        "path": str(path),
                        "dest": str(dest),
                        "category": category,
                        "bytes": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                    }
                )
            except Exception:
                skipped += 1
    plan.sort(key=lambda item: (item["category"], Path(item["path"]).name.lower()))
    return plan, skipped


def apply_desktop_organize(items):
    moved = 0
    skipped = 0
    for item in items:
        try:
            src = Path(item.get("path", ""))
            dest = Path(item.get("dest", ""))
            if not src.exists() or not src.is_file():
                skipped += 1
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            final_dest = unique_destination_path(dest)
            shutil.move(str(src), str(final_dest))
            moved += 1
        except Exception:
            skipped += 1
    return moved, skipped


def find_large_files(min_size=50 * 1024 * 1024, limit=40):
    found = []
    for root in large_file_roots():
        for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
            dirnames[:] = [name for name in dirnames if not (Path(dirpath) / name).is_symlink()]
            for filename in filenames:
                path = Path(dirpath) / filename
                try:
                    if path.is_symlink() or not path.is_file():
                        continue
                    stat = path.stat()
                    if stat.st_size >= min_size:
                        found.append(
                            {
                                "path": str(path),
                                "bytes": stat.st_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                            }
                        )
                except Exception:
                    continue
    found.sort(key=lambda item: item["bytes"], reverse=True)
    return found[:limit]


def top_resource_processes(limit=12):
    rows = []
    for proc in psutil.process_iter(["pid", "name", "memory_info", "cpu_percent", "exe"]):
        try:
            info = proc.info
            mem = getattr(info.get("memory_info"), "rss", 0)
            rows.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "",
                    "memory": mem,
                    "cpu": float(info.get("cpu_percent") or 0),
                    "exe": info.get("exe") or "",
                }
            )
        except Exception:
            continue
    rows.sort(key=lambda item: (item["memory"], item["cpu"]), reverse=True)
    return rows[:limit]


class CleanupScanWorker(QThread):
    result = Signal(list, str)

    def run(self):
        try:
            items = [scan_cleanup_target(target) for target in cleanup_target_definitions()]
            self.result.emit(items, "")
        except Exception as exc:
            self.result.emit([], str(exc))


class CleanupDeleteWorker(QThread):
    result = Signal(int, int, int, str)

    def __init__(self, items):
        super().__init__()
        self.items = items

    def run(self):
        try:
            deleted, freed, skipped = delete_cleanup_files(self.items)
            self.result.emit(deleted, freed, skipped, "")
        except Exception as exc:
            self.result.emit(0, 0, 0, str(exc))


class LargeFileWorker(QThread):
    result = Signal(list, str)

    def run(self):
        try:
            self.result.emit(find_large_files(), "")
        except Exception as exc:
            self.result.emit([], str(exc))


class DesktopOrganizeScanWorker(QThread):
    result = Signal(list, int, str)

    def run(self):
        try:
            plan, skipped = desktop_organize_plan()
            self.result.emit(plan, skipped, "")
        except Exception as exc:
            self.result.emit([], 0, str(exc))


class DesktopOrganizeMoveWorker(QThread):
    result = Signal(int, int, str)

    def __init__(self, items):
        super().__init__()
        self.items = items

    def run(self):
        try:
            moved, skipped = apply_desktop_organize(self.items)
            self.result.emit(moved, skipped, "")
        except Exception as exc:
            self.result.emit(0, 0, str(exc))


FILE_KIND_EXTENSIONS = {
    "文档": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".md", ".csv"},
    "图片": {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg", ".heic"},
    "视频": {".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm"},
    "音频": {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"},
    "压缩包": {".zip", ".rar", ".7z", ".tar", ".gz", ".iso"},
    "代码": {".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".toml", ".yaml", ".yml", ".ps1", ".bat", ".cmd", ".cpp", ".c", ".h", ".cs", ".java", ".go", ".rs"},
    "程序": {".exe", ".msi", ".bat", ".cmd", ".ps1", ".lnk"},
}

TEXT_SEARCH_EXTENSIONS = FILE_KIND_EXTENSIONS["代码"] | {".txt", ".md", ".csv", ".log", ".ini", ".cfg"}
SKIP_SEARCH_DIRS = {
    "$recycle.bin",
    "system volume information",
    "windows",
    "program files",
    "program files (x86)",
    "appdata",
    "node_modules",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
}


def file_search_roots():
    user = Path(os.environ.get("USERPROFILE", str(Path.home())))
    one_drive = Path(os.environ.get("OneDrive", user / "OneDrive"))
    roots = {
        "常用位置": [
            Path("D:\\CodexProjects"),
            user / "Downloads",
            user / "Desktop",
            user / "Documents",
            one_drive / "文档",
            one_drive / "Desktop",
        ],
        "D盘项目": [Path("D:\\CodexProjects")],
        "下载": [user / "Downloads"],
        "桌面": [user / "Desktop", one_drive / "Desktop"],
        "文档": [user / "Documents", one_drive / "文档"],
        "D盘": [Path("D:\\")],
        "用户目录": [user],
    }
    cleaned = {}
    for label, paths in roots.items():
        unique = []
        seen = set()
        for path in paths:
            try:
                if not path.exists() or not path.is_dir():
                    continue
                resolved = str(path.resolve()).lower()
                if resolved in seen:
                    continue
                seen.add(resolved)
                unique.append(path)
            except Exception:
                continue
        if unique:
            cleaned[label] = unique
    return cleaned


def file_kind_matches(path, kind):
    if not kind or kind == "全部":
        return True
    return path.suffix.lower() in FILE_KIND_EXTENSIONS.get(kind, set())


def file_content_matches(path, needle):
    if path.suffix.lower() not in TEXT_SEARCH_EXTENSIONS:
        return False
    try:
        if path.stat().st_size > 2 * 1024 * 1024:
            return False
        text = path.read_text(encoding="utf-8", errors="ignore")
        return needle in text.lower()
    except Exception:
        return False


class FileSearchWorker(QThread):
    result = Signal(list, str, bool)
    progress = Signal(str)

    def __init__(self, query, roots, kind="全部", include_content=False, limit=500):
        super().__init__()
        self.query = query.strip()
        self.roots = roots
        self.kind = kind
        self.include_content = include_content
        self.limit = limit
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def run(self):
        if not self.query:
            self.result.emit([], "先输入要找的文件名或关键词。", False)
            return
        needle = self.query.lower()
        terms = [term for term in re.split(r"\s+", needle) if term]
        results = []
        truncated = False
        try:
            for root in self.roots:
                if self.cancelled:
                    break
                self.progress.emit(f"正在搜索：{root}")
                for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
                    if self.cancelled:
                        break
                    kept = []
                    for dirname in dirnames:
                        lowered = dirname.lower()
                        if lowered in SKIP_SEARCH_DIRS:
                            continue
                        path = Path(dirpath) / dirname
                        try:
                            if path.is_symlink():
                                continue
                        except Exception:
                            continue
                        kept.append(dirname)
                    dirnames[:] = kept
                    for filename in filenames:
                        if self.cancelled:
                            break
                        path = Path(dirpath) / filename
                        try:
                            if path.is_symlink() or not path.is_file():
                                continue
                            if not file_kind_matches(path, self.kind):
                                continue
                            lowered_name = filename.lower()
                            name_match = all(term in lowered_name for term in terms)
                            content_match = self.include_content and not name_match and file_content_matches(path, needle)
                            if not name_match and not content_match:
                                continue
                            stat = path.stat()
                            results.append(
                                {
                                    "name": filename,
                                    "path": str(path),
                                    "bytes": stat.st_size,
                                    "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                                    "match": "内容" if content_match else "文件名",
                                }
                            )
                            if len(results) >= self.limit:
                                truncated = True
                                self.cancelled = True
                                break
                        except Exception:
                            continue
                    if self.cancelled:
                        break
            results.sort(key=lambda item: (item["match"] != "文件名", item["name"].lower()))
            self.result.emit(results, "", truncated)
        except Exception as exc:
            self.result.emit(results, str(exc), truncated)


class Bubble(QLabel):
    def __init__(self, config=None, owner=None):
        super().__init__()
        self.owner = owner
        self.config = config or DEFAULT_CONFIG
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setWordWrap(True)
        self.setMouseTracking(True)
        self.setToolTip("拖动移动桌宠和气泡；拖右下角调整大小；双击打开外观调试器")
        self.setMinimumWidth(0)
        self.setMaximumWidth(360)
        self.apply_font_config(self.config)
        self.hide()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)
        self._click_cb = None
        self._press_global = None
        self._drag_start_pos = QPoint()
        self._owner_start_pos = QPoint()
        self._resize_start_size = None
        self._resize_changed = False
        self._dragging_bubble = False
        self._resizing_bubble = False
        self.tail_side = "right"
        self.tail_tip_x = 0
        self.avoid_pet_center_tail = False

    def apply_font_config(self, config):
        self.config = config or DEFAULT_CONFIG
        self.setStyleSheet(bubble_text_style(self.config))
        self.setTextFormat(Qt.PlainText)
        self.apply_saved_size()
        self.update()

    def wrap_friendly_text(self, text):
        value = str(text or "")
        return re.sub(
            r"([A-Za-z0-9_./:@?#%=&+-]{18})(?=[A-Za-z0-9_./:@?#%=&+-])",
            lambda match: match.group(1) + "\u200b",
            value,
        )

    def resize_handle_hit(self, pos):
        margin = max(16, text_font_sizes(self.config)["bubble"] + 4)
        return pos.x() >= self.width() - margin and pos.y() >= self.height() - margin

    def apply_saved_size(self):
        width, height = bubble_manual_size(self.config)
        if width:
            self.setMinimumWidth(max(140, width))
            self.setMaximumWidth(max(140, width))
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(680)
        if height:
            self.setMinimumHeight(max(52, height))
            self.setMaximumHeight(max(52, height))
        else:
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)
        if width or height:
            self.resize(width or max(self.width(), self.sizeHint().width()), height or max(self.height(), self.sizeHint().height()))

    def fitted_message_size(self, text, forced_width=0, forced_height=0):
        size = text_font_sizes(self.config)["bubble"]
        pad_y, pad_x = bubble_padding(self.config)
        _tail_width, tail_height = bubble_tail_size(self.config)
        frame = bubble_frame(self.config)
        border_extra = frame["width"] * 2 + 6
        min_total_width = max(96, int(size * 5.2))
        max_total_width = 520
        max_total_height = 420
        min_total_height = max(38, int(size * 2.35))
        metrics = self.fontMetrics()
        lines = str(text or "").splitlines() or [""]
        longest_line = max((metrics.horizontalAdvance(line) for line in lines), default=0)
        max_text_width = max(48, max_total_width - pad_x * 2 - border_extra)
        min_text_width = max(28, min_total_width - pad_x * 2 - border_extra)
        if forced_width:
            text_width = max(32, forced_width - pad_x * 2 - border_extra)
        else:
            natural_width = longest_line
            if len(str(text or "")) > 26 or "\n" in str(text or ""):
                natural_width = min(max(natural_width, int(size * 16.0)), int(size * 18.5))
            text_width = min(max_text_width, max(min_text_width, natural_width))
        bounds = metrics.boundingRect(
            QRect(0, 0, max(32, text_width), max_total_height * 4),
            Qt.TextWordWrap | Qt.TextExpandTabs,
            str(text or ""),
        )
        total_width = forced_width or bounds.width() + pad_x * 2 + border_extra
        total_height = forced_height or bounds.height() + pad_y * 2 + tail_height + border_extra
        return (
            min(max_total_width, max(min_total_width, int(total_width))),
            min(max_total_height, max(min_total_height, int(total_height))),
        )

    def paintEvent(self, event):
        frame = bubble_frame(self.config)
        colors = bubble_colors(self.config)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        pen_width = frame["width"]
        inset = pen_width / 2 + 0.5
        tail_width, tail_height = bubble_tail_size(self.config)
        rect = self.rect().adjusted(int(inset), int(inset), -int(inset), -int(inset + tail_height))
        brush = color_with_alpha(colors["background"], 232, DEFAULT_CONFIG["BubbleBackgroundColor"])
        pen = QPen(color_with_alpha(colors["border"], 210, DEFAULT_CONFIG["BubbleBorderColor"]), pen_width)
        tip_x = bubble_tail_tip_x(
            self.width(),
            self.config,
            self.tail_side,
            self.tail_tip_x if self.tail_tip_x > 0 else None,
        )
        half = max(8, tail_width // 2)
        body_path = QPainterPath()
        body_path.addRoundedRect(QRectF(rect), frame["radius"], frame["radius"])
        bottom = rect.bottom()
        tail_path = QPainterPath()
        tail_path.moveTo(tip_x - half, bottom - 1)
        tail_path.quadTo(tip_x - max(2, half // 3), bottom + max(3, tail_height // 4), tip_x, bottom + tail_height)
        tail_path.quadTo(tip_x + max(2, half // 3), bottom + max(3, tail_height // 4), tip_x + half, bottom - 1)
        tail_path.closeSubpath()
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.drawPath(body_path.united(tail_path).simplified())
        painter.end()
        super().paintEvent(event)

    def say(self, text, ms=5200, fixed_size=None, avoid_pet_center_tail=False):
        if self.owner is not None:
            if hasattr(self.owner, "should_suppress_bubble") and self.owner.should_suppress_bubble():
                if hasattr(self.owner, "hide_bubble_now"):
                    self.owner.hide_bubble_now()
                else:
                    self._click_cb = None
                    self.hide()
                return
            if not self.owner.isVisible():
                return
        self._click_cb = None
        self.avoid_pet_center_tail = bool(avoid_pet_center_tail)
        wrapped = self.wrap_friendly_text(text)
        self.setText(wrapped)
        width, height = bubble_manual_size(self.config)
        if fixed_size:
            width, height = fixed_size
        chosen_width, chosen_height = self.fitted_message_size(wrapped, width, height)
        self.setMinimumSize(chosen_width, chosen_height)
        self.setMaximumSize(chosen_width, chosen_height)
        self.resize(chosen_width, chosen_height)
        if self.owner is not None and hasattr(self.owner, "position_bubble"):
            self.owner.position_bubble()
        if self._click_cb:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.OpenHandCursor)
        self.show()
        self.raise_()
        self.timer.start(ms)

    def set_click_callback(self, cb):
        self._click_cb = cb

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._press_global = event.globalPosition().toPoint()
            self._drag_start_pos = self.pos()
            if self.owner is not None and hasattr(self.owner, "pos"):
                self._owner_start_pos = self.owner.pos()
            self._resize_start_size = (self.width(), self.height())
            self._resize_changed = False
            self._dragging_bubble = False
            self._resizing_bubble = self.resize_handle_hit(event.position().toPoint())
            self.setCursor(Qt.SizeFDiagCursor if self._resizing_bubble else Qt.ClosedHandCursor)
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._press_global is None:
            self.setCursor(Qt.SizeFDiagCursor if self.resize_handle_hit(event.position().toPoint()) else (Qt.PointingHandCursor if self._click_cb else Qt.OpenHandCursor))
            super().mouseMoveEvent(event)
            return
        if self._press_global is not None and (event.buttons() & Qt.LeftButton):
            delta = event.globalPosition().toPoint() - self._press_global
            if self._resizing_bubble:
                if delta.manhattanLength() < QApplication.startDragDistance():
                    event.accept()
                    return
                start_w, start_h = self._resize_start_size or (self.width(), self.height())
                width = max(140, min(680, start_w + delta.x()))
                height = max(52, min(360, start_h + delta.y()))
                self._resize_changed = True
                self.config["BubbleWidth"] = width
                self.config["BubbleHeight"] = height
                self.setMinimumSize(width, height)
                self.setMaximumSize(width, height)
                self.resize(width, height)
                self.update()
                if self.owner is not None and hasattr(self.owner, "position_bubble"):
                    self.owner.position_bubble()
                event.accept()
                return
            if self._dragging_bubble or delta.manhattanLength() >= QApplication.startDragDistance():
                self._dragging_bubble = True
                if self.owner is not None and hasattr(self.owner, "move"):
                    target = self._owner_start_pos + delta
                    if hasattr(self.owner, "clamped_pos"):
                        target = self.owner.clamped_pos(target)
                    if hasattr(self.owner, "position_save_anchor"):
                        self.owner.position_save_anchor = None
                    self.owner.move(target)
                    if hasattr(self.owner, "position_bubble"):
                        self.owner.position_bubble()
                else:
                    self.move(self._drag_start_pos + delta)
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            dragged = self._dragging_bubble
            resized = self._resizing_bubble
            self._press_global = None
            self._resize_start_size = None
            self._dragging_bubble = False
            self._resizing_bubble = False
            self.setCursor(Qt.PointingHandCursor if self._click_cb else Qt.OpenHandCursor)
            if resized and self._resize_changed:
                self._resize_changed = False
                if self.owner is not None and hasattr(self.owner, "save_bubble_size"):
                    self.owner.save_bubble_size()
                event.accept()
                return
            self._resize_changed = False
            if dragged:
                if self.owner is not None and hasattr(self.owner, "save_window_position"):
                    self.owner.save_window_position()
                event.accept()
                return
            if self._click_cb:
                self._click_cb()
                event.accept()
                return
            if self.owner is not None and hasattr(self.owner, "open_word_popup"):
                self.owner.open_word_popup()
                event.accept()
                return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton and self.owner is not None and hasattr(self.owner, "open_appearance_debug"):
            self.timer.stop()
            self.owner.open_appearance_debug()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


APP_DIALOG_STYLE = app_dialog_style(DEFAULT_CONFIG)


class PetSprite(QLabel):
    clicked = Signal()
    right_clicked = Signal()
    double_clicked = Signal()
    head_touched = Signal()
    body_touched = Signal()
    long_pressed = Signal()
    resize_requested = Signal(int)
    drag_started = Signal(QPoint)
    drag_moved = Signal(QPoint)
    drag_finished = Signal()

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.setAlignment(Qt.AlignCenter)
        self.setMouseTracking(True)
        self.down_at = None
        self.down_global = QPoint()
        self.sprite_dragging = False
        self.long_press_fired = False
        self.pose_scale = 1.0
        self.pose_squash = 1.0
        self.pose_angle = 0.0
        self.source_pixmap = QPixmap()
        self.canvas_side = 0
        self.animations = {}
        self.current_action = "idle"
        self.current_frame = 0
        self.press_timer = QTimer(self)
        self.press_timer.setSingleShot(True)
        self.press_timer.timeout.connect(self.fire_long_pressed)
        self.load_image()

    def fire_long_pressed(self):
        self.long_press_fired = True
        self.long_pressed.emit()

    def load_image(self):
        custom_path = self.config.get("PetImagePath", "")
        custom_name = Path(custom_path).name.lower() if custom_path else ""
        has_action_pack = bool(self.config.get("ActionPackPath", ""))
        use_default_frames = has_action_pack or not custom_path or custom_name in {"codex-pet.png", "codex-pet-dog.png"}
        self.animations = self.load_sprite_frames() if use_default_frames else {}
        if self.animations:
            self.set_animation_frame("idle", 0)
            return
        path = custom_path or str(ASSET)
        if not Path(path).exists():
            path = str(ASSET)
        self.source_pixmap = QPixmap(path)
        self.reset_pose()

    def load_sprite_frames(self):
        animations = {}
        frame_dir = Path(self.config.get("ActionPackPath", "") or DOG_FRAME_DIR)
        if not frame_dir.exists():
            frame_dir = DOG_FRAME_DIR
        action_names = (
            "idle",
            "sit",
            "blink",
            "look_left",
            "look_center",
            "look_right",
            "happy",
            "surprised",
            "angry",
            "sniff",
            "sniff_right",
            "stretch",
            "sleep",
            "study",
            "walk_left",
            "walk_right",
        )

        def frame_index(path):
            prefix = f"{action}_"
            suffix = path.stem[len(prefix):] if path.stem.startswith(prefix) else ""
            return int(suffix) if suffix.isdigit() else 9999

        for action in action_names:
            frames = []
            prefix = f"{action}_"
            paths = [
                path
                for path in frame_dir.glob(f"{action}_*.png")
                if path.stem.startswith(prefix) and path.stem[len(prefix):].isdigit()
            ]
            for path in sorted(paths, key=frame_index):
                pixmap = QPixmap(str(path))
                if not pixmap.isNull():
                    frames.append(pixmap)
            if frames:
                animations[action] = frames
        if "sit" not in animations and "idle" in animations:
            animations["sit"] = animations["idle"]
        if "blink" not in animations and "idle" in animations:
            animations["blink"] = animations["idle"]
        for look_action in ("look_left", "look_center", "look_right"):
            if look_action not in animations and "idle" in animations:
                animations[look_action] = animations["idle"]
        if "study" not in animations and "idle" in animations:
            animations["study"] = animations["idle"]
        if "surprised" not in animations and "happy" in animations:
            animations["surprised"] = animations["happy"]
        if "angry" not in animations and "surprised" in animations:
            animations["angry"] = animations["surprised"]
        if "stretch" not in animations and "sniff" in animations:
            animations["stretch"] = animations["sniff"]
        if "sniff_right" not in animations and "sniff" in animations:
            mirror = QTransform().scale(-1, 1)
            animations["sniff_right"] = [frame.transformed(mirror, Qt.SmoothTransformation) for frame in animations["sniff"]]
        if "walk_left" not in animations and "sniff" in animations:
            animations["walk_left"] = animations["sniff"]
        if "walk_right" not in animations and "walk_left" in animations:
            mirror = QTransform().scale(-1, 1)
            animations["walk_right"] = [frame.transformed(mirror, Qt.SmoothTransformation) for frame in animations["walk_left"]]
        return animations

    def has_animation(self, action):
        return bool(self.animations.get(action))

    def frame_count(self, action):
        return len(self.animations.get(action, []))

    def set_animation_frame(self, action, index=0):
        frames = self.animations.get(action) or self.animations.get("idle")
        if not frames:
            return False
        self.current_action = action if action in self.animations else "idle"
        self.current_frame = index % len(frames)
        self.source_pixmap = frames[self.current_frame]
        self.reset_pose()
        return True

    def show_idle(self):
        if self.animations:
            self.set_animation_frame("idle", 0)
        else:
            self.reset_pose()

    def reset_pose(self):
        self.pose_scale = 1.0
        self.pose_squash = 1.0
        self.pose_angle = 0.0
        self.render_image()

    def render_image(self):
        size = int(self.config.get("PetSize", 230))
        display_w = max(80, int(size * self.pose_scale))
        display_h = max(70, int(size * self.pose_scale * self.pose_squash))
        mode = Qt.KeepAspectRatio if self.animations else Qt.IgnoreAspectRatio
        pix = self.source_pixmap.scaled(display_w, display_h, mode, Qt.SmoothTransformation)
        if abs(self.pose_angle) > 0.1:
            pix = pix.transformed(QTransform().rotate(self.pose_angle), Qt.SmoothTransformation)
        self.setPixmap(pix)
        # Keep a stable oversized canvas while actions play. Small pets used to
        # crop tall/rotated frames because the parent window resized one frame late.
        base_side = max(300, int(size * 1.95), pix.width() + 72, pix.height() + 72)
        self.canvas_side = max(self.canvas_side, base_side)
        self.setFixedSize(self.canvas_side, self.canvas_side)
        self.updateGeometry()
        window = self.window()
        if window is not self and hasattr(window, "adjustSize"):
            window.adjustSize()

    def set_pet_size(self, size):
        self.config["PetSize"] = max(120, min(380, int(size)))
        self.canvas_side = 0
        self.render_image()

    def set_pose_scale(self, scale):
        self.set_pose(scale=scale, squash=self.pose_squash, angle=self.pose_angle)

    def set_pose(self, scale=1.0, squash=1.0, angle=0.0):
        self.pose_scale = max(0.72, min(1.22, float(scale)))
        self.pose_squash = max(0.72, min(1.18, float(squash)))
        self.pose_angle = max(-22.0, min(22.0, float(angle)))
        self.render_image()

    def mousePressEvent(self, event):
        self.down_at = event.position().toPoint()
        self.down_global = event.globalPosition().toPoint()
        self.sprite_dragging = False
        self.long_press_fired = False
        if event.button() == Qt.LeftButton:
            self.press_timer.start(650)
            event.accept()
            return
        if event.button() == Qt.RightButton:
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.down_at and (event.buttons() & Qt.LeftButton):
            current = event.position().toPoint()
            if self.sprite_dragging or (current - self.down_at).manhattanLength() > 8:
                if not self.sprite_dragging:
                    self.press_timer.stop()
                    self.sprite_dragging = True
                    self.drag_started.emit(event.globalPosition().toPoint())
                self.drag_moved.emit(event.globalPosition().toPoint())
                event.accept()
                return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.press_timer.stop()
        if self.long_press_fired:
            self.long_press_fired = False
            event.accept()
            return
        if self.sprite_dragging:
            self.sprite_dragging = False
            self.drag_finished.emit()
            event.accept()
            return
        pos = event.position().toPoint()
        if self.down_at and (pos - self.down_at).manhattanLength() < 6:
            if event.type() == event.Type.MouseButtonRelease:
                if event.button() == Qt.RightButton:
                    self.right_clicked.emit()
                    event.accept()
                    return
                if event.button() == Qt.LeftButton:
                    if pos.y() < self.height() * 0.42:
                        self.head_touched.emit()
                    else:
                        self.body_touched.emit()
                    event.accept()
                    return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        self.right_clicked.emit()
        event.accept()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta and (event.modifiers() & Qt.ControlModifier):
            self.resize_requested.emit(12 if delta > 0 else -12)
            event.accept()
            return
        super().wheelEvent(event)


class AiWorker(QThread):
    delta = Signal(str)
    done = Signal(str)

    def __init__(self, config, mode, question):
        super().__init__()
        self.config = config
        self.mode = mode
        self.question = question
        self.cancelled = False

    def cancel(self):
        self.cancelled = True

    def run(self):
        key = self.config.get("AiApiKey", "")
        if not key:
            self.done.emit("AI 还没有配置 API Key。请在设置里填写。")
            return
        prompts = {
            "代码解释": "你是严谨的代码讲解助手，用中文解释代码意图、关键逻辑、风险和改进点。",
            "408答疑": "你是考研 408 答疑助手，用中文分步骤解释概念、题型和易错点。",
            "高数答疑": "你是考研高数答疑助手，用中文分步骤推导。",
            "翻译": "你是翻译助手，先准确翻译，再补充术语说明。",
        }
        body = {
            "model": self.config.get("AiModel", "gpt-4.1-mini"),
            "stream": True,
            "thinking": {"type": "disabled"},
            "max_tokens": 1200,
            "temperature": 0.3,
            "messages": [
                {"role": "system", "content": prompts.get(self.mode, "你是友好的 AI 桌宠助手。") + "\n" + ai_memory_context(self.config)},
                {"role": "user", "content": self.question},
            ],
        }
        headers = {"Authorization": f"Bearer {key}"}
        chunks = []
        try:
            with httpx.stream(
                "POST",
                self.config.get("AiEndpoint"),
                json=body,
                headers=headers,
                timeout=httpx.Timeout(45.0, connect=8.0, read=20.0, write=20.0, pool=8.0),
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if self.cancelled:
                        self.done.emit("已取消生成。")
                        return
                    if not line or not line.startswith("data:"):
                        continue
                    data = line[5:].strip()
                    if data == "[DONE]":
                        break
                    try:
                        part = json.loads(data)["choices"][0]["delta"].get("content", "")
                    except Exception:
                        part = ""
                    if part:
                        chunks.append(part)
                        self.delta.emit(part)
            self.done.emit("".join(chunks))
        except Exception as exc:
            self.done.emit(f"AI 调用失败：{exc}")


class VoiceInputWorker(QThread):
    result = Signal(str, str)

    def run(self):
        script = (
            "$OutputEncoding=[System.Text.Encoding]::UTF8; "
            "Add-Type -AssemblyName System.Speech; "
            "try { "
            "$culture=[System.Globalization.CultureInfo]::GetCultureInfo('zh-CN'); "
            "$r=New-Object System.Speech.Recognition.SpeechRecognitionEngine($culture); "
            "$r.SetInputToDefaultAudioDevice(); "
            "$r.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar)); "
            "$res=$r.Recognize([TimeSpan]::FromSeconds(8)); "
            "if ($res -and $res.Text) { [Console]::Out.Write($res.Text) } "
            "else { [Console]::Error.Write('没有识别到语音。') } "
            "} catch { [Console]::Error.Write($_.Exception.Message) }"
        )
        try:
            proc = subprocess.run(
                ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=15,
                check=False,
            )
            text = proc.stdout.strip()
            error = proc.stderr.strip()
            self.result.emit(text, error)
        except Exception as exc:
            self.result.emit("", str(exc))


class OcrWorker(QThread):
    result = Signal(object)

    def __init__(self, config, image_path):
        super().__init__()
        self.config = dict(config)
        self.image_path = Path(image_path)

    def run(self):
        try:
            content, error = run_tesseract_ocr(self.config, self.image_path)
            self.result.emit({"ok": True, "path": str(self.image_path), "content": content, "error": error})
        except Exception as exc:
            self.result.emit({"ok": False, "path": str(self.image_path), "content": "", "error": f"OCR 失败：{exc}"})


DETACHED_WORKERS = []


def disconnect_worker_signal(worker, signal_name):
    signal = getattr(worker, signal_name, None)
    if signal is None:
        return
    try:
        signal.disconnect()
    except Exception:
        pass


def keep_worker_alive(worker):
    if worker is None or worker in DETACHED_WORKERS:
        return
    DETACHED_WORKERS.append(worker)

    def cleanup():
        try:
            DETACHED_WORKERS.remove(worker)
        except ValueError:
            pass
        try:
            worker.deleteLater()
        except Exception:
            pass

    try:
        worker.finished.connect(cleanup)
    except Exception:
        pass


def detach_running_worker(worker, signal_names=(), cancel=False):
    if worker is None or not worker.isRunning():
        return False
    for signal_name in signal_names:
        disconnect_worker_signal(worker, signal_name)
    keep_worker_alive(worker)
    if cancel and hasattr(worker, "cancel"):
        try:
            worker.cancel()
        except Exception:
            pass
    return True


class PromptEdit(QPlainTextEdit):
    send_requested = Signal()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter) and not (event.modifiers() & Qt.ShiftModifier):
            self.send_requested.emit()
            return
        super().keyPressEvent(event)


class AiDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker = None
        self.voice_worker = None
        self.ocr_worker = None
        self.tts_worker = None
        self.pending_delta = ""
        self.pending_reminder_note = ""
        self.voice_auto_send = False
        self.force_speak_answer = False
        self.delta_timer = QTimer(self)
        self.delta_timer.setInterval(45)
        self.delta_timer.timeout.connect(self.flush_delta)
        self.setWindowTitle(config.get("PetName", "糯米"))
        self.resize(620, 500)
        self.setMinimumSize(480, 360)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel(f"{config.get('PetName', '糯米')}")
        title.setObjectName("title")
        layout.addWidget(title)
        hint = QLabel("有什么想问的吗？也可以直接用下面的快捷入口。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        quick = QGridLayout()
        quick_items = [
            ("截图提问", self.capture_to_input),
            ("解释代码", lambda: self.quick_mode("代码解释", "把代码贴进来，我帮你解释逻辑、问题和改法。")),
            ("翻译", lambda: self.quick_mode("翻译", "把要翻译的文字贴进来。")),
            ("学习助手", lambda: self.quick_mode("408答疑", "今天想复习哪一块？比如线性表、栈和队列、高数极限。")),
        ]
        for index, (label, fn) in enumerate(quick_items):
            button = QPushButton(label)
            button.setObjectName("ghostButton")
            button.setMinimumHeight(34)
            button.clicked.connect(fn)
            quick.addWidget(button, index // 2, index % 2)
        layout.addLayout(quick)
        top = QHBoxLayout()
        self.mode = QComboBox()
        self.mode.addItems(["普通问答", "代码解释", "408答疑", "高数答疑", "翻译"])
        self.search = QLineEdit()
        self.search.setPlaceholderText("搜索历史关键词")
        search_btn = QPushButton("搜索")
        search_btn.setObjectName("ghostButton")
        search_btn.clicked.connect(self.refresh_history)
        top.addWidget(self.mode)
        top.addWidget(self.search)
        top.addWidget(search_btn)
        layout.addLayout(top)
        self.history = QTextEdit()
        self.history.setReadOnly(True)
        self.history.setObjectName("panel")
        self.history.setPlaceholderText("对话会显示在这里。")
        self.history.setMinimumHeight(170)
        self.history.setMaximumHeight(280)
        layout.addWidget(self.history)
        self.input = PromptEdit()
        self.input.setObjectName("panel")
        self.input.setPlaceholderText("请问：比如“解释一下二叉树的后序遍历”或“这段代码哪里错了？”")
        self.input.setMaximumHeight(120)
        self.input.setMinimumHeight(76)
        self.input.send_requested.connect(self.send)
        layout.addWidget(self.input)
        buttons = QHBoxLayout()
        send = QPushButton("发送 Enter")
        send.setObjectName("sendButton")
        screenshot = QPushButton("截图识别")
        voice = QPushButton("语音输入")
        voice_chat = QPushButton("语音聊天")
        cancel = QPushButton("取消生成")
        clear = QPushButton("清空历史")
        screenshot.setObjectName("ghostButton")
        voice.setObjectName("ghostButton")
        voice_chat.setObjectName("sendButton")
        cancel.setObjectName("dangerButton")
        clear.setObjectName("ghostButton")
        send.clicked.connect(self.send)
        screenshot.clicked.connect(self.capture_to_input)
        voice.clicked.connect(self.voice_input)
        voice_chat.clicked.connect(self.voice_chat)
        cancel.clicked.connect(self.cancel)
        clear.clicked.connect(lambda: (save_json(CHAT, []), self.refresh_history()))
        buttons.addStretch(1)
        buttons.addWidget(screenshot)
        buttons.addWidget(voice)
        buttons.addWidget(voice_chat)
        buttons.addWidget(send)
        buttons.addWidget(cancel)
        buttons.addWidget(clear)
        layout.addLayout(buttons)
        self.refresh_history()

    def pet_name(self):
        return str(self.config.get("PetName") or DEFAULT_CONFIG["PetName"])

    def quick_mode(self, mode, placeholder):
        idx = self.mode.findText(mode)
        if idx >= 0:
            self.mode.setCurrentIndex(idx)
        self.input.setPlaceholderText(placeholder)
        self.input.setFocus()

    def refresh_history(self):
        items = load_json(CHAT, [])
        keyword = self.search.text().strip()
        if keyword:
            items = [x for x in items if keyword in x.get("question", "") or keyword in x.get("answer", "")]
        lines = []
        for item in items[-30:]:
            lines.append(f"[{item.get('mode')}] Q: {item.get('question')}\nA: {item.get('answer')}\n")
        self.history.setPlainText("\n".join(lines))

    def save_chat_turn(self, question, answer, notes=None, reminder_note=""):
        items = load_json(CHAT, [])
        items.append(
            {
                "id": str(time.time()),
                "mode": self.mode.currentText(),
                "question": question,
                "answer": answer,
                "memory_notes": notes or [],
                "reminder_note": reminder_note,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        save_json(CHAT, items)

    def send(self):
        question = self.input.toPlainText().strip()
        if not question:
            return
        if self.worker and self.worker.isRunning():
            return
        self.history.append(f"\n[{self.mode.currentText()}] Q: {question}\nA: ")
        self.pending_reminder_note = ""
        parent = self.parent()
        if parent and hasattr(parent, "try_apply_natural_settings"):
            setting_answer = parent.try_apply_natural_settings(question) or ""
            if setting_answer:
                self.history.insertPlainText(setting_answer)
                self.save_chat_turn(question, setting_answer)
                self.input.clear()
                return
        if parent and hasattr(parent, "try_add_natural_reminder"):
            self.pending_reminder_note = parent.try_add_natural_reminder(question) or ""
            if self.pending_reminder_note:
                self.history.append(f"\n{self.pet_name()}记下提醒：{self.pending_reminder_note}\n")
        self.pending_delta = ""
        self.delta_timer.start()
        self.worker = AiWorker(self.config, self.mode.currentText(), question)
        self.worker.delta.connect(self.buffer_delta)
        self.worker.done.connect(lambda answer: self.finish_answer(question, answer))
        self.worker.finished.connect(lambda: setattr(self, "worker", None))
        self.worker.start()

    def cancel(self):
        if self.worker:
            self.worker.cancel()

    def capture_to_input(self):
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.input.setPlainText("上一张截图正在 OCR 识别，请稍等。")
            return
        self.hide()
        QApplication.processEvents()
        snip = SnipDialog()
        if snip.exec() != QDialog.Accepted or snip.selected.width() < 8 or snip.selected.height() < 8:
            self.show()
            return
        rect = snip.selected
        screen_geo = QApplication.primaryScreen().geometry()
        shot = QApplication.primaryScreen().grabWindow(
            0,
            screen_geo.x() + rect.x(),
            screen_geo.y() + rect.y(),
            rect.width(),
            rect.height(),
        )
        self.show()
        path = SCREENSHOTS / f"ai-screenshot-{datetime.now():%Y%m%d-%H%M%S}.png"
        shot.save(str(path))
        self.input.setPlainText(f"截图已保存，正在 OCR 识别...\n截图路径：{path}")
        self.ocr_worker = OcrWorker(self.config, path)
        self.ocr_worker.result.connect(self.apply_captured_ocr)
        self.ocr_worker.finished.connect(lambda: setattr(self, "ocr_worker", None))
        self.ocr_worker.start()

    def apply_captured_ocr(self, result):
        content = result.get("content", "")
        error = result.get("error", "")
        path = result.get("path", "")
        if content:
            self.input.setPlainText("请解释这段截图 OCR 内容：\n" + content)
        else:
            self.input.setPlainText(error + f"\n截图路径：{path}")

    def voice_input(self):
        if self.voice_worker and self.voice_worker.isRunning():
            return
        self.voice_auto_send = False
        self.input.setPlaceholderText("正在听你说话，最多 8 秒...")
        self.voice_worker = VoiceInputWorker()
        self.voice_worker.result.connect(self.apply_voice_text)
        self.voice_worker.finished.connect(lambda: setattr(self, "voice_worker", None))
        self.voice_worker.start()

    def voice_chat(self):
        if self.worker and self.worker.isRunning():
            return
        if self.voice_worker and self.voice_worker.isRunning():
            return
        self.voice_auto_send = True
        self.input.setPlaceholderText("我在听，说完后会自动发送...")
        self.history.append(f"\n{self.pet_name()}正在听你说话...")
        self.voice_worker = VoiceInputWorker()
        self.voice_worker.result.connect(self.apply_voice_text)
        self.voice_worker.finished.connect(lambda: setattr(self, "voice_worker", None))
        self.voice_worker.start()

    def apply_voice_text(self, text, error):
        self.input.setPlaceholderText("请问：比如“解释一下二叉树的后序遍历”或“这段代码哪里错了？”")
        if text:
            if self.voice_auto_send:
                self.input.setPlainText(text)
                self.force_speak_answer = True
                self.voice_auto_send = False
                self.send()
            else:
                current = self.input.toPlainText().strip()
                self.input.setPlainText((current + "\n" if current else "") + text)
        elif error:
            self.voice_auto_send = False
            QMessageBox.information(self, "语音输入", f"语音识别不可用或未识别到内容：{error}")
        else:
            self.voice_auto_send = False

    def buffer_delta(self, text):
        self.pending_delta += text

    def flush_delta(self):
        if self.pending_delta:
            self.history.insertPlainText(self.pending_delta)
            self.pending_delta = ""

    def finish_answer(self, question, answer):
        self.flush_delta()
        self.delta_timer.stop()
        notes = extract_memory_and_progress(question, self.mode.currentText())
        if notes:
            note_text = "\n".join(f"{self.pet_name()}记下了：{note}" for note in notes)
            self.history.append("\n" + note_text)
            parent = self.parent()
            if parent and hasattr(parent, "refresh_growth_state"):
                parent.refresh_growth_state(show_new=True)
        self.save_chat_turn(question, answer, notes, self.pending_reminder_note)
        if self.force_speak_answer or self.config.get("ChatVoiceReplies", True):
            self.speak_reply(answer)
        self.force_speak_answer = False
        self.input.clear()

    def speak_reply(self, text):
        speech = clean_tts_text(text)
        if not speech:
            return
        parent = self.parent()
        if parent and hasattr(parent, "speak"):
            parent.speak(speech, kind="interaction")
            return
        if self.tts_worker and self.tts_worker.isRunning():
            return
        self.tts_worker = TtsWorker(
            speech,
            self.config,
        )
        self.tts_worker.finished.connect(lambda: setattr(self, "tts_worker", None))
        self.tts_worker.start()

    def closeEvent(self, event):
        self.delta_timer.stop()
        detach_running_worker(self.worker, ("delta", "done", "finished"), cancel=True)
        detach_running_worker(self.voice_worker, ("result", "finished"))
        detach_running_worker(self.ocr_worker, ("result", "finished"))
        detach_running_worker(self.tts_worker, ("finished",))
        self.worker = None
        self.voice_worker = None
        self.ocr_worker = None
        self.tts_worker = None
        super().closeEvent(event)


class SnipDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setWindowOpacity(0.28)
        self.setStyleSheet("background:#000000;")
        self.origin = QPoint()
        self.selected = QRect()
        self.band = QRubberBand(QRubberBand.Rectangle, self)
        self.setCursor(Qt.CrossCursor)
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

    def mousePressEvent(self, event):
        self.origin = event.position().toPoint()
        self.band.setGeometry(QRect(self.origin, self.origin))
        self.band.show()

    def mouseMoveEvent(self, event):
        self.band.setGeometry(QRect(self.origin, event.position().toPoint()).normalized())

    def mouseReleaseEvent(self, event):
        self.selected = QRect(self.origin, event.position().toPoint()).normalized()
        self.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("日历同步 / 本地日程")
        self.resize(600, 560)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        self.events = load_json(CALENDAR, [])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("日历 / 日程")
        title.setObjectName("title")
        layout.addWidget(title)
        hint = QLabel("可以直接写：明天下午3点高数复习；也可以点下面的快捷时间。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        form = QFormLayout()
        self.title = QLineEdit()
        self.title.setPlaceholderText("例如：明天下午3点高数复习 / 周六10点考试")
        self.when = QDateTimeEdit()
        self.when.setCalendarPopup(True)
        self.when.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.when.setDateTime(datetime.now())
        self.kind = QComboBox()
        self.kind.addItems(["学习", "考试", "约会", "放假", "其他"])
        form.addRow("标题", self.title)
        form.addRow("时间", self.when)
        form.addRow("类型", self.kind)
        layout.addLayout(form)
        quick = QGridLayout()
        quick.setHorizontalSpacing(8)
        quick.setVerticalSpacing(8)
        quick_items = [
            ("1小时后", lambda: self.set_when_delta(hours=1)),
            ("今晚8点", lambda: self.set_when_at(20, 0, 0)),
            ("明早9点", lambda: self.set_when_at(9, 0, 1)),
            ("明天下午3点", lambda: self.set_when_at(15, 0, 1)),
            ("周一9点", lambda: self.set_when_weekday(0, 9, 0)),
            ("周六10点", lambda: self.set_when_weekday(5, 10, 0)),
        ]
        for index, (label, handler) in enumerate(quick_items):
            button = QPushButton(label)
            button.setObjectName("ghostButton")
            button.clicked.connect(handler)
            quick.addWidget(button, index // 3, index % 3)
        layout.addLayout(quick)
        row = QHBoxLayout()
        add = QPushButton("添加日程")
        today = QPushButton("查看今日")
        week = QPushButton("查看本周")
        add.setObjectName("sendButton")
        today.setObjectName("ghostButton")
        week.setObjectName("ghostButton")
        add.clicked.connect(self.add_event)
        today.clicked.connect(lambda: self.refresh(1))
        week.clicked.connect(lambda: self.refresh(7))
        row.addStretch(1)
        row.addWidget(add)
        row.addWidget(today)
        row.addWidget(week)
        layout.addLayout(row)
        self.list = QListWidget()
        layout.addWidget(self.list)
        self.refresh(7)

    def set_when_datetime(self, value):
        self.when.setDateTime(value)

    def set_when_delta(self, minutes=0, hours=0, days=0):
        self.set_when_datetime(datetime.now() + timedelta(minutes=minutes, hours=hours, days=days))

    def set_when_at(self, hour, minute=0, day_offset=0):
        self.set_when_datetime(next_time_at(hour, minute, day_offset))

    def set_when_weekday(self, weekday, hour, minute=0):
        self.set_when_datetime(next_weekday_time(weekday, hour, minute))

    def parse_title_time(self, text):
        parsed = parse_time_text_without_trigger(text)
        if parsed:
            return parsed["title"], parsed["remind_at"]
        return text, None

    def add_event(self):
        raw_title = self.title.text().strip()
        title, parsed_at = self.parse_title_time(raw_title)
        if not title:
            QMessageBox.warning(self, "缺少标题", "先写一个日程标题。")
            return
        self.events.append(
            {
                "title": title,
                "at": parsed_at or self.when.dateTime().toString("yyyy-MM-dd HH:mm"),
                "kind": self.kind.currentText(),
            }
        )
        self.title.clear()
        save_json(CALENDAR, self.events)
        self.refresh(7)

    def refresh(self, days):
        self.list.clear()
        shown = 0
        start = datetime.now()
        end = start + timedelta(days=days)
        for event in sorted(self.events, key=lambda x: x.get("at", "")):
            try:
                at = datetime.strptime(event.get("at", ""), "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            if start.date() <= at.date() <= end.date():
                delta = at - start
                self.list.addItem(f"{event.get('kind')}  {event.get('at')}\n{event.get('title')}\n倒计时 {max(0, delta.days)} 天")
                shown += 1
        if shown == 0:
            self.list.addItem("这段时间没有日程。")


class MailWorker(QThread):
    result = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = config

    def run(self):
        try:
            result = fetch_unread_mail_result(self.config, limit=8)
            messages = result.get("messages", [])
            error = result.get("error", "")
            total_unread = int(result.get("total_unread", 0) or 0)
        except Exception as exc:
            self.result.emit(f"邮件读取失败：{exc}")
            return
        if error:
            self.result.emit(error)
            return
        unread = total_unread
        keywords = [x.strip() for x in self.config.get("MailKeywords", "").split(",") if x.strip()]
        state = load_json(MAIL_STATE, {})
        state["last_unread_count"] = unread
        state["last_mail_checked_at"] = datetime.now().isoformat(timespec="seconds")
        known = set(state.get("known_mail_signatures", []))
        current = [mail_signature(msg) for msg in messages]
        if not known:
            state["known_mail_signatures"] = current[:200]
            save_json(MAIL_STATE, state)
            self.result.emit(f"邮件监控已开启，当前未读 {unread} 封")
            return

        new_messages = [msg for msg in messages if mail_signature(msg) not in known]
        state["known_mail_signatures"] = (current + list(known))[:200]
        save_json(MAIL_STATE, state)
        if not new_messages:
            self.result.emit("")
            return

        alerts = [f"收到新邮件：未读 {unread} 封"]
        for msg in new_messages[:3]:
            subject = msg.get("subject", "")
            sender = msg.get("sender", "")
            date = msg.get("date", "")
            preview = msg.get("preview", "")
            code = msg.get("verification_code", "")
            haystack = f"{subject}\n{preview}".lower()
            if any(k.lower() in haystack for k in keywords):
                alerts.append(f"关键词邮件：{subject}")
            else:
                alerts.append(f"{sender} | {subject}")
            if code:
                alerts.append(f"验证码：{code}")
            elif preview:
                alerts.append("内容：" + mail_clean_text(preview, limit=120))
            if date:
                alerts.append(date)
        self.result.emit("\n".join(alerts))


class MailListWorker(QThread):
    result = Signal(list, str)

    def __init__(self, config, provider_filter=None):
        super().__init__()
        self.config = config
        self.provider_filter = provider_filter

    def run(self):
        try:
            messages, error = fetch_unread_mail(self.config, limit=20, provider_filter=self.provider_filter)
        except Exception as exc:
            messages, error = [], f"邮件读取失败：{exc}"
        self.result.emit(messages, error)


class MailSendWorker(QThread):
    result = Signal(bool, str)

    def __init__(self, account, to, subject, body, cc="", bcc=""):
        super().__init__()
        self.account = account
        self.to = to
        self.subject = subject
        self.body = body
        self.cc = cc
        self.bcc = bcc

    def run(self):
        ok, message = send_mail_via_account(self.account, self.to, self.subject, self.body, self.cc, self.bcc)
        self.result.emit(ok, message)


class MailComposeDialog(QDialog):
    def __init__(self, config, provider, parent=None):
        super().__init__(parent)
        self.config = config
        self.provider = provider
        self.account = mail_account_for_provider(config, provider)
        self.worker = None
        label = "Gmail" if provider == "gmail" else "QQ 邮箱"
        self.setWindowTitle(f"写{label}邮件")
        self.resize(560, 520)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel(f"写{label}邮件")
        title.setObjectName("title")
        layout.addWidget(title)
        sender = self.account.get("user", "") if self.account else "未配置"
        hint = QLabel(f"发件账号：{sender}")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        form = QFormLayout()
        form.setSpacing(10)
        self.to = QLineEdit()
        self.cc = QLineEdit()
        self.bcc = QLineEdit()
        self.subject = QLineEdit()
        form.addRow("收件人", self.to)
        form.addRow("抄送", self.cc)
        form.addRow("密送", self.bcc)
        form.addRow("主题", self.subject)
        layout.addLayout(form)

        self.body = QPlainTextEdit()
        self.body.setPlaceholderText("写邮件正文...")
        layout.addWidget(self.body)

        buttons = QHBoxLayout()
        self.send_btn = QPushButton("发送")
        self.send_btn.setObjectName("sendButton")
        cancel = QPushButton("取消")
        cancel.setObjectName("ghostButton")
        self.send_btn.clicked.connect(self.send)
        cancel.clicked.connect(self.close)
        buttons.addWidget(self.send_btn)
        buttons.addStretch(1)
        buttons.addWidget(cancel)
        layout.addLayout(buttons)

        if not self.account:
            self.send_btn.setEnabled(False)
            QMessageBox.warning(self, "邮箱未配置", f"还没有配置可用于发送的{label}账号。")

    def send(self):
        if not self.account or self.worker:
            return
        to = self.to.text().strip()
        subject = self.subject.text().strip()
        body = self.body.toPlainText()
        if not to or not subject:
            QMessageBox.warning(self, "缺少内容", "请至少填写收件人和主题。")
            return
        confirm = QMessageBox.question(
            self,
            "确认发送",
            f"确定从 {self.account.get('user')} 发送到 {to} 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if confirm != QMessageBox.Yes:
            return
        self.send_btn.setEnabled(False)
        self.send_btn.setText("发送中...")
        self.worker = MailSendWorker(self.account, to, subject, body, self.cc.text(), self.bcc.text())
        self.worker.result.connect(self.send_finished)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def send_finished(self, ok, message):
        if ok:
            QMessageBox.information(self, "发送成功", message)
            self.accept()
            return
        QMessageBox.warning(self, "发送失败", message)

    def worker_finished(self):
        self.worker = None
        self.send_btn.setEnabled(True)
        self.send_btn.setText("发送")

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.send_btn.setText("发送中，请稍等...")
            event.ignore()
            return
        super().closeEvent(event)


class MailDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.messages = []
        self.worker = None
        self.closing = False
        self.loaded_providers = set()
        self.loading_provider = ""
        self.setWindowTitle("邮件提醒")
        self.resize(620, 520)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("邮箱")
        title.setObjectName("title")
        hint = QLabel("这里显示最近未读邮件。滚轮只会滚动列表；选中邮件后可打开对应邮箱网页。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        self.messages_by_provider = {"qq": [], "gmail": []}
        self.mail_tabs = QTabWidget()
        self.mail_tabs.setObjectName("settingsTabs")
        self.qq_list = QListWidget()
        self.gmail_list = QListWidget()
        self.mail_tabs.addTab(self.build_mail_panel("QQ 邮箱", self.qq_list), "QQ邮箱")
        self.mail_tabs.addTab(self.build_mail_panel("Gmail", self.gmail_list), "Gmail")
        self.mail_tabs.currentChanged.connect(self.ensure_current_provider_loaded)
        layout.addWidget(self.mail_tabs)
        button_area = QVBoxLayout()
        top_buttons = QHBoxLayout()
        bottom_buttons = QHBoxLayout()
        refresh = QPushButton("刷新")
        open_mail = QPushButton("打开所选邮件")
        copy_content = QPushButton("复制验证码/内容")
        compose_qq = QPushButton("写 QQ 邮件")
        compose_gmail = QPushButton("写 Gmail")
        open_qq = QPushButton("打开 QQ 邮箱")
        open_gmail = QPushButton("打开 Gmail")
        close = QPushButton("关闭")
        refresh.setObjectName("ghostButton")
        open_mail.setObjectName("sendButton")
        copy_content.setObjectName("ghostButton")
        compose_qq.setObjectName("ghostButton")
        compose_gmail.setObjectName("ghostButton")
        open_qq.setObjectName("ghostButton")
        open_gmail.setObjectName("ghostButton")
        close.setObjectName("ghostButton")
        refresh.clicked.connect(lambda: self.load_mail(self.current_provider(), force=True))
        open_mail.clicked.connect(self.open_selected)
        copy_content.clicked.connect(self.copy_selected_content)
        compose_qq.clicked.connect(lambda: self.open_compose("qq"))
        compose_gmail.clicked.connect(lambda: self.open_compose("gmail"))
        open_qq.clicked.connect(lambda: open_mail_url("qq"))
        open_gmail.clicked.connect(lambda: open_mail_url("gmail"))
        close.clicked.connect(self.close)
        top_buttons.addWidget(refresh)
        top_buttons.addWidget(open_mail)
        top_buttons.addWidget(copy_content)
        top_buttons.addStretch(1)
        bottom_buttons.addWidget(compose_qq)
        bottom_buttons.addWidget(compose_gmail)
        bottom_buttons.addWidget(open_qq)
        bottom_buttons.addWidget(open_gmail)
        bottom_buttons.addStretch(1)
        bottom_buttons.addWidget(close)
        button_area.addLayout(top_buttons)
        button_area.addLayout(bottom_buttons)
        layout.addLayout(button_area)
        self.load_mail(self.current_provider())

    def build_mail_panel(self, title, mail_list):
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(8)
        mail_list.setWordWrap(True)
        mail_list.setTextElideMode(Qt.ElideNone)
        mail_list.setSpacing(6)
        section_title = QLabel(title)
        section_title.setObjectName("subtitle")
        panel_layout.addWidget(section_title)
        panel_layout.addWidget(mail_list)
        return panel

    def current_provider(self):
        return "gmail" if self.mail_tabs.currentIndex() == 1 else "qq"

    def current_list(self):
        return self.gmail_list if self.current_provider() == "gmail" else self.qq_list

    def current_messages(self):
        return self.messages_by_provider.get(self.current_provider(), [])

    def ensure_current_provider_loaded(self):
        provider = self.current_provider()
        if provider not in self.loaded_providers:
            self.load_mail(provider)

    def load_mail(self, provider=None, force=False):
        if self.closing:
            return
        provider = provider or self.current_provider()
        cached = cached_mail_messages() if not force else []
        if cached:
            self.render_mail(cached, "")
            cache_age = mail_cache_age_seconds()
            age_text = f"{int(cache_age // 60)} 分钟前" if cache_age is not None and cache_age >= 60 else "刚刚"
            self.current_list().addItem(f"显示缓存（{age_text}），点“刷新”获取最新邮件。")
            return
        else:
            target = self.gmail_list if provider == "gmail" else self.qq_list
            target.clear()
            target.addItem(f"正在读取 {'Gmail' if provider == 'gmail' else 'QQ 邮箱'}...")
        if self.worker and self.worker.isRunning():
            self.current_list().addItem("邮件正在刷新，稍等一下。")
            return
        self.loading_provider = provider
        self.worker = MailListWorker(self.config, provider_filter=provider)
        self.worker.result.connect(lambda messages, error, target=provider: self.render_mail(messages, error, target))
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def render_mail(self, messages, error, provider=None):
        if self.closing:
            return
        provider = provider or ""
        if error:
            target = self.gmail_list if provider == "gmail" else self.qq_list
            target.clear()
            target.addItem(error)
            return
        if provider:
            self.messages_by_provider[provider] = []
            for item in messages:
                target = "gmail" if (item.get("provider") or provider) == "gmail" else "qq"
                self.messages_by_provider[target].append(item)
            self.loaded_providers.add(provider)
            if provider == "gmail":
                self.render_provider_list("gmail", self.gmail_list, "Gmail")
            else:
                self.render_provider_list("qq", self.qq_list, "QQ 邮箱")
        else:
            self.messages_by_provider = {"qq": [], "gmail": []}
            for item in messages:
                target = "gmail" if (item.get("provider") or "qq") == "gmail" else "qq"
                self.messages_by_provider[target].append(item)
            self.loaded_providers.update(provider for provider, items in self.messages_by_provider.items() if items)
            self.render_provider_list("qq", self.qq_list, "QQ 邮箱")
            self.render_provider_list("gmail", self.gmail_list, "Gmail")
        self.messages = self.messages_by_provider.get("qq", []) + self.messages_by_provider.get("gmail", [])

    def render_provider_list(self, provider, mail_list, label):
        items = self.messages_by_provider.get(provider, [])
        if not items:
            mail_list.addItem(f"{label} 没有未读邮件。")
            return
        unread = items[0].get("account_unread_count", len(items))
        mail_list.addItem(f"{label} 未读邮件：{unread}（显示最近 {len(items)} 封）")
        for item in items:
            text = mail_display_text(item)
            widget_item = QListWidgetItem(text)
            line_count = text.count("\n") + 1
            widget_item.setSizeHint(QSize(0, min(190, max(82, line_count * 21 + 18))))
            mail_list.addItem(widget_item)

    def worker_finished(self):
        self.worker = None
        self.loading_provider = ""
        if not self.closing and self.current_provider() not in self.loaded_providers:
            QTimer.singleShot(0, self.ensure_current_provider_loaded)

    def closeEvent(self, event):
        self.closing = True
        detach_running_worker(self.worker, ("result", "finished"))
        self.worker = None
        super().closeEvent(event)

    def selected_message(self):
        mail_list = self.current_list()
        messages = self.current_messages()
        idx = mail_list.currentRow()
        msg_idx = idx - 1
        if msg_idx < 0 or msg_idx >= len(messages):
            return None
        return messages[msg_idx]

    def copy_selected_content(self):
        message = self.selected_message()
        if not message:
            QMessageBox.information(self, "复制邮件内容", "请先选中一封邮件。")
            return
        code = str(message.get("verification_code") or "").strip()
        preview = mail_clean_text(message.get("preview", ""), limit=600)
        text = code or preview or str(message.get("subject") or "")
        if not text:
            QMessageBox.information(self, "复制邮件内容", "这封邮件没有可复制的正文预览。")
            return
        QApplication.clipboard().setText(text)
        QMessageBox.information(self, "已复制", "已复制验证码。" if code else "已复制邮件内容预览。")

    def open_selected(self):
        message = self.selected_message()
        if not message:
            self.open_default_inbox()
            return
        subject = message.get("subject", "")
        open_mail_url(self.current_provider(), message.get("inbox_url"))
        copy_text = message.get("verification_code") or subject
        QApplication.clipboard().setText(copy_text)
        QMessageBox.information(
            self,
            "已打开邮箱",
            "已复制验证码。进入网页邮箱后可直接粘贴。"
            if message.get("verification_code")
            else "已复制邮件标题。进入网页邮箱后可直接粘贴搜索。",
        )

    def open_default_inbox(self):
        open_mail_url(self.current_provider())

    def open_compose(self, provider):
        MailComposeDialog(self.config, provider, self).exec()


EDGE_TTS_VOICES = (
    ("晓晓：自然温柔女声", "zh-CN-XiaoxiaoNeural"),
    ("晓伊：活泼清亮女声", "zh-CN-XiaoyiNeural"),
    ("晓双：可爱少女声", "zh-CN-XiaoshuangNeural"),
    ("云希：清朗青年男声", "zh-CN-YunxiNeural"),
    ("云健：沉稳有力男声", "zh-CN-YunjianNeural"),
)

ONECORE_TTS_VOICES = (
    ("瑶瑶：温柔可爱女声（推荐）", "Microsoft Yaoyao"),
    ("慧慧：自然亲切女声", "Microsoft Huihui"),
    ("康康：清晰男声", "Microsoft Kangkang"),
)

TTS_VOICES_CACHE = None
EDGE_TTS_FAST_ADDRESS = None
EDGE_TTS_HOST = "speech.platform.bing.com"
EDGE_TTS_PATH = "/consumer/speech/synthesize/readaloud/edge/v1"
EDGE_TTS_TOKEN = "6A5AA1D4EAFF4E9FB37E23D68491D6F4"
EDGE_TTS_CHROMIUM_VERSION = "143.0.3650.75"
EDGE_TTS_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/{EDGE_TTS_CHROMIUM_VERSION} Safari/537.36 "
    f"Edg/{EDGE_TTS_CHROMIUM_VERSION}"
)
WEBSOCKET_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


def edge_tts_available():
    try:
        import edge_tts  # noqa: F401
        return True
    except Exception:
        return False


def edge_voice_name(config=None):
    selected = str((config or {}).get("EdgeVoice", DEFAULT_CONFIG["EdgeVoice"])).strip()
    return selected or DEFAULT_CONFIG["EdgeVoice"]


def onecore_voice_name(config=None):
    selected = str((config or {}).get("OneCoreVoice", DEFAULT_CONFIG["OneCoreVoice"])).strip()
    return selected or DEFAULT_CONFIG["OneCoreVoice"]


def play_audio_with_mci(path, volume=70, media_type="mpegvideo"):
    if not sys.platform.startswith("win"):
        return False
    alias = f"nuomi_tts_{os.getpid()}_{int(time.time() * 1000)}"
    mci = ctypes.windll.winmm.mciSendStringW
    safe_path = str(path).replace('"', '""')
    opened = False
    try:
        if mci(f'open "{safe_path}" type {media_type} alias {alias}', None, 0, None) != 0:
            return False
        opened = True
        mci(f"setaudio {alias} volume to {max(0, min(1000, int(volume) * 10))}", None, 0, None)
        return mci(f"play {alias} wait", None, 0, None) == 0
    finally:
        if opened:
            mci(f"close {alias}", None, 0, None)


def play_mp3_with_mci(path, volume=70):
    return play_audio_with_mci(path, volume, "mpegvideo")


def play_wav_with_mci(path, volume=70):
    return play_audio_with_mci(path, volume, "waveaudio")


def edge_tts_timestamp():
    return datetime.utcnow().strftime("%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)")


def edge_tts_sec_ms_gec():
    windows_epoch = 11644473600
    unix_time = int(time.time())
    rounded_time = unix_time - (unix_time % 300)
    ticks = (rounded_time + windows_epoch) * 10_000_000
    value = f"{ticks}{EDGE_TTS_TOKEN}".encode("ascii")
    return hashlib.sha256(value).hexdigest().upper()


def websocket_send_frame(sock, payload, opcode=0x1):
    payload = payload if isinstance(payload, bytes) else str(payload).encode("utf-8")
    header = bytearray([0x80 | (opcode & 0x0F)])
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length <= 0xFFFF:
        header.append(0x80 | 126)
        header.extend(struct.pack("!H", length))
    else:
        header.append(0x80 | 127)
        header.extend(struct.pack("!Q", length))
    mask = secrets.token_bytes(4)
    header.extend(mask)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    sock.sendall(bytes(header) + masked)


def socket_recv_exact(sock, length):
    chunks = []
    remaining = length
    while remaining:
        chunk = sock.recv(remaining)
        if not chunk:
            raise ConnectionError("在线语音连接意外断开")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def websocket_receive_message(sock):
    message_opcode = None
    chunks = []
    while True:
        first, second = socket_recv_exact(sock, 2)
        finished = bool(first & 0x80)
        opcode = first & 0x0F
        masked = bool(second & 0x80)
        length = second & 0x7F
        if length == 126:
            length = struct.unpack("!H", socket_recv_exact(sock, 2))[0]
        elif length == 127:
            length = struct.unpack("!Q", socket_recv_exact(sock, 8))[0]
        mask = socket_recv_exact(sock, 4) if masked else b""
        payload = socket_recv_exact(sock, length) if length else b""
        if masked:
            payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))

        if opcode == 0x8:
            return 0x8, payload
        if opcode == 0x9:
            websocket_send_frame(sock, payload, 0xA)
            continue
        if opcode == 0xA:
            continue
        if opcode in (0x1, 0x2):
            message_opcode = opcode
            chunks = [payload]
        elif opcode == 0x0 and message_opcode is not None:
            chunks.append(payload)
        else:
            continue
        if finished:
            return message_opcode, b"".join(chunks)


def edge_tts_websocket():
    global EDGE_TTS_FAST_ADDRESS
    connection_id = uuid.uuid4().hex
    query = (
        f"TrustedClientToken={EDGE_TTS_TOKEN}"
        f"&ConnectionId={connection_id}"
        f"&Sec-MS-GEC={edge_tts_sec_ms_gec()}"
        f"&Sec-MS-GEC-Version=1-{EDGE_TTS_CHROMIUM_VERSION}"
    )
    path = f"{EDGE_TTS_PATH}?{query}"
    key = base64.b64encode(secrets.token_bytes(16)).decode("ascii")
    muid = secrets.token_hex(16).upper()
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {EDGE_TTS_HOST}\r\n"
        "Connection: Upgrade\r\n"
        "Pragma: no-cache\r\n"
        "Cache-Control: no-cache\r\n"
        f"User-Agent: {EDGE_TTS_USER_AGENT}\r\n"
        "Upgrade: websocket\r\n"
        "Origin: chrome-extension://jdiccldimpdaibmpdkjnbmckianbfold\r\n"
        "Sec-WebSocket-Version: 13\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        "Accept-Encoding: gzip, deflate, br, zstd\r\n"
        "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8\r\n"
        f"Cookie: muid={muid};\r\n"
        "\r\n"
    )
    context = ssl.create_default_context()
    resolved = []
    try:
        for info in socket.getaddrinfo(EDGE_TTS_HOST, 443, type=socket.SOCK_STREAM):
            address = info[4][0]
            if address not in resolved:
                resolved.append(address)
    except OSError:
        resolved = []
    candidates = []
    if EDGE_TTS_FAST_ADDRESS:
        candidates.append(EDGE_TTS_FAST_ADDRESS)
    for address in reversed(resolved):
        if address not in candidates:
            candidates.append(address)
    if EDGE_TTS_HOST not in candidates:
        candidates.append(EDGE_TTS_HOST)

    sock = None
    connection_errors = []
    for address in candidates:
        raw_socket = None
        try:
            raw_socket = socket.create_connection((address, 443), timeout=8)
            sock = context.wrap_socket(raw_socket, server_hostname=EDGE_TTS_HOST)
            EDGE_TTS_FAST_ADDRESS = address
            break
        except OSError as exc:
            connection_errors.append(f"{address}: {type(exc).__name__}")
            if raw_socket:
                raw_socket.close()
    if sock is None:
        raise ConnectionError("在线语音连接失败：" + ", ".join(connection_errors))
    sock.settimeout(30)
    try:
        sock.sendall(request.encode("ascii"))
        response = bytearray()
        while b"\r\n\r\n" not in response:
            response.extend(sock.recv(4096))
            if len(response) > 65536:
                raise ConnectionError("在线语音握手响应异常")
        headers, remainder = bytes(response).split(b"\r\n\r\n", 1)
        status_line = headers.split(b"\r\n", 1)[0]
        if b" 101 " not in status_line:
            raise ConnectionError(status_line.decode("latin-1", errors="replace"))
        expected_accept = base64.b64encode(
            hashlib.sha1((key + WEBSOCKET_GUID).encode("ascii")).digest()
        )
        if b"sec-websocket-accept: " + expected_accept.lower() not in headers.lower():
            raise ConnectionError("在线语音握手校验失败")
        if remainder:
            raise ConnectionError("在线语音握手包含未处理数据")
        return sock
    except Exception:
        sock.close()
        raise


def save_edge_tts_audio_stdlib(text, output_path, voice, rate, pitch):
    request_id = uuid.uuid4().hex
    rate_value = max(-100, min(100, int(rate) * 8))
    pitch_value = max(-100, min(100, int(pitch)))
    timestamp = edge_tts_timestamp()
    config_message = (
        f"X-Timestamp:{timestamp}\r\n"
        "Content-Type:application/json; charset=utf-8\r\n"
        "Path:speech.config\r\n\r\n"
        '{"context":{"synthesis":{"audio":{"metadataoptions":'
        '{"sentenceBoundaryEnabled":"false","wordBoundaryEnabled":"false"},'
        '"outputFormat":"audio-24khz-48kbitrate-mono-mp3"}}}}\r\n'
    )
    ssml = (
        "<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' "
        "xml:lang='zh-CN'>"
        f"<voice name='{xml_escape(str(voice))}'>"
        f"<prosody pitch='{pitch_value:+d}Hz' rate='{rate_value:+d}%' volume='+0%'>"
        f"{xml_escape(str(text))}</prosody></voice></speak>"
    )
    ssml_message = (
        f"X-RequestId:{request_id}\r\n"
        "Content-Type:application/ssml+xml\r\n"
        f"X-Timestamp:{timestamp}Z\r\n"
        "Path:ssml\r\n\r\n"
        f"{ssml}"
    )
    audio_parts = []
    sock = edge_tts_websocket()
    try:
        websocket_send_frame(sock, config_message)
        websocket_send_frame(sock, ssml_message)
        while True:
            opcode, payload = websocket_receive_message(sock)
            if opcode == 0x8:
                break
            if opcode == 0x1:
                message = payload.decode("utf-8", errors="replace")
                if "Path:turn.end" in message:
                    break
                continue
            if opcode != 0x2 or len(payload) < 2:
                continue
            header_length = struct.unpack("!H", payload[:2])[0]
            header_end = 2 + header_length
            if header_end > len(payload):
                continue
            headers = payload[2:header_end].decode("utf-8", errors="replace")
            if "Path:audio" in headers and header_end < len(payload):
                audio_parts.append(payload[header_end:])
    finally:
        try:
            websocket_send_frame(sock, b"", 0x8)
        except Exception:
            pass
        sock.close()
    if not audio_parts:
        raise RuntimeError("在线语音没有返回音频")
    Path(output_path).write_bytes(b"".join(audio_parts))


async def save_edge_tts_audio(text, output_path, voice, rate, pitch):
    if edge_tts_available():
        import edge_tts

        communicate = edge_tts.Communicate(
            text,
            voice=voice,
            rate=f"{max(-100, min(100, int(rate) * 8)):+d}%",
            pitch=f"{max(-100, min(100, int(pitch))):+d}Hz",
        )
        await communicate.save(str(output_path))
        return
    await asyncio.to_thread(
        save_edge_tts_audio_stdlib,
        text,
        output_path,
        voice,
        rate,
        pitch,
    )


def installed_tts_voices():
    global TTS_VOICES_CACHE
    if TTS_VOICES_CACHE is not None:
        return TTS_VOICES_CACHE
    voices = []
    if not sys.platform.startswith("win"):
        TTS_VOICES_CACHE = voices
        return voices
    script = (
        "Add-Type -AssemblyName System.Speech; "
        "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
        "$s.GetInstalledVoices() | ForEach-Object { "
        "$v=$_.VoiceInfo; "
        "[Console]::Out.WriteLine($v.Name + \"`t\" + $v.Culture.Name + \"`t\" + $v.Gender) "
        "}"
    )
    try:
        proc = subprocess.run(
            ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=8,
            check=False,
        )
        for line in proc.stdout.splitlines():
            parts = line.split("\t")
            if not parts or not parts[0].strip():
                continue
            voices.append(
                {
                    "name": parts[0].strip(),
                    "culture": parts[1].strip() if len(parts) > 1 else "",
                    "gender": parts[2].strip() if len(parts) > 2 else "",
                }
            )
    except Exception:
        pass
    TTS_VOICES_CACHE = voices
    return voices


def preferred_tts_voice_name(config=None):
    selected = str((config or {}).get("VoiceName", "")).strip()
    if selected:
        return selected
    voices = installed_tts_voices()
    sweet_hints = ("xiaoxiao", "huihui", "yaoyao", "xiaoyi", "hanhan", "tingting")
    for hint in sweet_hints:
        for voice in voices:
            if hint in voice["name"].lower():
                return voice["name"]
    for voice in voices:
        if voice.get("culture", "").lower().startswith("zh") and voice.get("gender", "").lower() == "female":
            return voice["name"]
    for voice in voices:
        if voice.get("gender", "").lower() == "female":
            return voice["name"]
    return voices[0]["name"] if voices else ""


def clean_tts_text(text, limit=900):
    value = str(text or "").strip()
    if not value:
        return ""
    value = re.sub(r"```.*?```", "这里有一段代码。", value, flags=re.S)
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"https?://\S+", "链接", value)
    value = re.sub(r"[*_#>\[\]{}]", " ", value)
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) > limit:
        value = value[:limit].rstrip() + "。后面内容先省略。"
    return value


class TtsVoiceListWorker(QThread):
    result = Signal(object)

    def run(self):
        try:
            self.result.emit({"ok": True, "voices": installed_tts_voices()})
        except Exception as exc:
            self.result.emit({"ok": False, "voices": [], "error": str(exc)})


def voice_policy_allows(config, kind="ambient", context_busy=False, last_ambient_at=0.0, now=None):
    config = config or {}
    kind = str(kind or "ambient").lower()
    if not config.get("VoiceEnabled", False):
        return False
    if context_busy and config.get("FullscreenReminderOnly", True) and kind != "reminder":
        return False
    if config.get("QuietMode", False) and kind != "reminder":
        return False
    if kind == "ambient":
        cooldown = max(0, int(config.get("AmbientVoiceCooldownMinutes", 15))) * 60
        current = time.time() if now is None else float(now)
        if current - float(last_ambient_at or 0.0) < cooldown:
            return False
    return True


class TtsWorker(QThread):
    def __init__(self, text, config=None):
        super().__init__()
        self.text = text
        self.config = dict(config or {})
        self.volume = max(0, min(100, int(self.config.get("VoiceVolume", 70))))
        self.rate = max(-10, min(10, int(self.config.get("VoiceRate", -1))))

    def run(self):
        if not self.text.strip():
            return
        engine = str(self.config.get("VoiceEngine", DEFAULT_CONFIG["VoiceEngine"])).lower()
        if engine == "edge":
            if self.speak_edge() or self.speak_onecore():
                return
        elif engine == "onecore" and self.speak_onecore():
            return
        self.speak_windows()

    def speak_edge(self):
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as handle:
                tmp = Path(handle.name)
            asyncio.run(
                save_edge_tts_audio(
                    self.text,
                    tmp,
                    edge_voice_name(self.config),
                    self.rate,
                    self.config.get("EdgePitchHz", DEFAULT_CONFIG["EdgePitchHz"]),
                )
            )
            return tmp.exists() and tmp.stat().st_size > 0 and play_mp3_with_mci(tmp, self.volume)
        except Exception as exc:
            append_runtime_log(f"edge tts fallback: {type(exc).__name__}: {exc}")
            return False
        finally:
            if tmp:
                try:
                    tmp.unlink(missing_ok=True)
                except Exception:
                    pass

    def speak_onecore(self):
        if not sys.platform.startswith("win"):
            return False
        text_path = None
        wav_path = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".txt") as handle:
                handle.write(self.text)
                text_path = Path(handle.name)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as handle:
                wav_path = Path(handle.name)
            safe_text = str(text_path).replace("'", "''")
            safe_wav = str(wav_path).replace("'", "''")
            safe_voice = onecore_voice_name(self.config).replace("'", "''")
            speaking_rate = max(0.5, min(2.0, 1.0 + self.rate * 0.06))
            pitch_percent = max(-30, min(30, int(self.config.get("OneCorePitchPercent", 8))))
            audio_pitch = max(0.7, min(1.3, 1.0 + pitch_percent / 100.0))
            script = (
                "Add-Type -AssemblyName System.Runtime.WindowsRuntime; "
                "$voiceType=[Windows.Media.SpeechSynthesis.SpeechSynthesizer,"
                "Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime]; "
                "$streamType=[Windows.Media.SpeechSynthesis.SpeechSynthesisStream,"
                "Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime]; "
                "$s=New-Object Windows.Media.SpeechSynthesis.SpeechSynthesizer; "
                f"$v=$voiceType::AllVoices | Where-Object {{ $_.DisplayName -eq '{safe_voice}' }} | Select-Object -First 1; "
                "if ($v) { $s.Voice=$v }; "
                f"$s.Options.SpeakingRate={speaking_rate:.2f}; "
                f"$s.Options.AudioPitch={audio_pitch:.2f}; "
                f"$s.Options.AudioVolume={self.volume / 100.0:.2f}; "
                f"$t=Get-Content -LiteralPath '{safe_text}' -Raw -Encoding UTF8; "
                "$op=$s.SynthesizeTextToStreamAsync($t); "
                "$m=[System.WindowsRuntimeSystemExtensions].GetMethods() | "
                "Where-Object { $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 } | "
                "Select-Object -First 1; "
                "$task=$m.MakeGenericMethod($streamType).Invoke($null,@($op)); "
                "$task.Wait(); $stream=$task.Result; "
                "$net=[System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream); "
                f"$file=[System.IO.File]::Create('{safe_wav}'); "
                "$net.CopyTo($file); $file.Close(); $net.Close(); $stream.Dispose(); $s.Dispose()"
            )
            proc = subprocess.run(
                ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
                check=False,
            )
            return proc.returncode == 0 and wav_path.stat().st_size > 1000 and play_wav_with_mci(wav_path, self.volume)
        except Exception as exc:
            append_runtime_log(f"onecore tts fallback: {type(exc).__name__}: {exc}")
            return False
        finally:
            for path in (text_path, wav_path):
                if path:
                    try:
                        path.unlink(missing_ok=True)
                    except Exception:
                        pass

    def speak_windows(self):
        tmp = None
        try:
            with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8", suffix=".txt") as handle:
                handle.write(self.text)
                tmp = handle.name
            safe_tmp = tmp.replace("'", "''")
            safe_voice = preferred_tts_voice_name(self.config).replace("'", "''")
            script = (
                "Add-Type -AssemblyName System.Speech; "
                "$s=New-Object System.Speech.Synthesis.SpeechSynthesizer; "
                f"if ('{safe_voice}') {{ try {{ $s.SelectVoice('{safe_voice}') }} catch {{ }} }} "
                f"$s.Volume={self.volume}; "
                f"$s.Rate={self.rate}; "
                f"$t=Get-Content -LiteralPath '{safe_tmp}' -Raw -Encoding UTF8; "
                "$s.Speak($t)"
            )
            subprocess.run(
                ["powershell.exe", "-NoProfile", "-WindowStyle", "Hidden", "-Command", script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=30,
                check=False,
            )
        except Exception:
            pass
        finally:
            if tmp:
                try:
                    Path(tmp).unlink(missing_ok=True)
                except Exception:
                    pass


class WeatherWorker(QThread):
    result = Signal(str)

    def __init__(self, city):
        super().__init__()
        self.city = city or "上海"

    def run(self):
        try:
            url = f"https://wttr.in/{quote(self.city)}?format=j1&lang=zh"
            response = httpx.get(
                url,
                headers={"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.2"},
                timeout=12,
            )
            response.raise_for_status()
            data = response.json()
            current = data["current_condition"][0]
            desc = weather_desc_zh(current["weatherDesc"][0]["value"])
            temp = current["temp_C"]
            tomorrow = data.get("weather", [{}])[1] if len(data.get("weather", [])) > 1 else {}
            tomorrow_desc = ""
            if tomorrow:
                hourly = tomorrow.get("hourly", [])
                desc_item = ""
                if hourly:
                    middle = hourly[min(len(hourly) // 2, len(hourly) - 1)]
                    desc_item = weather_desc_zh(middle.get("weatherDesc", [{}])[0].get("value", ""))
                tomorrow_desc = f"；明天 {tomorrow.get('mintempC')}~{tomorrow.get('maxtempC')}°C {desc_item}"
            self.result.emit(f"{self.city} {temp}°C {desc}{tomorrow_desc}")
        except Exception as exc:
            self.result.emit(f"天气查询失败：{exc}")


class AssistantToolboxWorker(QThread):
    result = Signal(bool, str)

    def run(self):
        try:
            ok, message = ensure_assistant_toolbox_server()
        except Exception as exc:
            ok, message = False, f"核心工具箱启动失败：{exc}"
        self.result.emit(ok, message)


class StartupMaintenanceWorker(QThread):
    result = Signal(str)

    def __init__(self, config):
        super().__init__()
        self.config = dict(config or {})

    def run(self):
        try:
            configured_tesseract_path(self.config, persist=True)
            sync_startup_entry(self.config)
            sync_watchdog(self.config)
            self.result.emit("startup maintenance finished")
        except Exception as exc:
            self.result.emit(f"startup maintenance failed: {type(exc).__name__}: {exc}")


class WeatherDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker = None
        self.setWindowTitle("天气")
        self.resize(520, 320)
        self.setMinimumSize(420, 280)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("天气查询")
        title.setObjectName("title")
        hint = QLabel("默认上海，可改成任意城市。")
        hint.setObjectName("hint")
        layout.addWidget(title)
        layout.addWidget(hint)
        row = QHBoxLayout()
        self.city = QLineEdit(config.get("WeatherCity", "上海"))
        refresh = QPushButton("查询")
        save = QPushButton("设为默认")
        refresh.setObjectName("sendButton")
        save.setObjectName("ghostButton")
        refresh.clicked.connect(self.refresh)
        save.clicked.connect(self.save_city)
        row.addWidget(self.city)
        row.addWidget(refresh)
        row.addWidget(save)
        layout.addLayout(row)
        self.result = QTextEdit()
        self.result.setObjectName("panel")
        self.result.setReadOnly(True)
        self.result.setLineWrapMode(QTextEdit.WidgetWidth)
        self.result.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.result.setPlainText("点击查询获取天气。")
        self.result.setMinimumHeight(120)
        self.result.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.result, 1)
        self.refresh()

    def refresh(self):
        if self.worker and self.worker.isRunning():
            self.result.setPlainText("天气正在查询，稍等一下。")
            return
        self.result.setPlainText("正在查询天气...")
        self.worker = WeatherWorker(self.city.text().strip() or "上海")
        self.worker.result.connect(self.set_result)
        self.worker.finished.connect(lambda: setattr(self, "worker", None))
        self.worker.start()

    def set_result(self, text):
        self.result.setPlainText(str(text or ""))
        parent = self.parent()
        if parent is not None and hasattr(parent, "set_weather"):
            parent.set_weather(text, show_bubble=False)

    def save_city(self):
        self.config["WeatherCity"] = self.city.text().strip() or "上海"
        save_json(CONFIG, self.config)
        self.result.setPlainText(f"默认城市已保存：{self.config['WeatherCity']}")

    def closeEvent(self, event):
        detach_running_worker(self.worker, ("result", "finished"))
        self.worker = None
        super().closeEvent(event)


class TodoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("提醒事项")
        self.resize(560, 620)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        self.todos = load_json(TODOS, [])
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("提醒事项")
        title.setObjectName("title")
        hint = QLabel("可以直接写：10分钟后喝水 / 明早9点背单词；也可以点下面的快捷时间。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        form = QFormLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("例如：10分钟后喝水 / 明早9点背单词 / 极限复习")
        self.remind_enabled = QCheckBox("开启提醒")
        self.remind_enabled.setChecked(True)
        self.remind_at = QDateTimeEdit()
        self.remind_at.setCalendarPopup(True)
        self.remind_at.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.remind_at.setDateTime(datetime.now() + timedelta(hours=1))
        form.addRow("事项", self.input)
        form.addRow(self.remind_enabled)
        form.addRow("提醒时间", self.remind_at)
        layout.addLayout(form)
        quick = QGridLayout()
        quick.setHorizontalSpacing(8)
        quick.setVerticalSpacing(8)
        quick_items = [
            ("10分钟后", lambda: self.set_reminder_delta(minutes=10)),
            ("30分钟后", lambda: self.set_reminder_delta(minutes=30)),
            ("1小时后", lambda: self.set_reminder_delta(hours=1)),
            ("今晚8点", lambda: self.set_reminder_at(20, 0, 0)),
            ("明早9点", lambda: self.set_reminder_at(9, 0, 1)),
            ("明天下午3点", lambda: self.set_reminder_at(15, 0, 1)),
            ("后天9点", lambda: self.set_reminder_at(9, 0, 2)),
            ("不提醒", self.disable_reminder),
        ]
        for index, (label, handler) in enumerate(quick_items):
            button = QPushButton(label)
            button.setObjectName("ghostButton")
            button.clicked.connect(handler)
            quick.addWidget(button, index // 4, index % 4)
        layout.addLayout(quick)

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self.pick)
        layout.addWidget(self.list)

        row = QHBoxLayout()
        add = QPushButton("添加")
        test = QPushButton("测试提醒")
        edit = QPushButton("保存修改")
        done = QPushButton("完成/取消")
        delete = QPushButton("删除")
        close = QPushButton("关闭")
        add.setObjectName("sendButton")
        test.setObjectName("ghostButton")
        edit.setObjectName("ghostButton")
        done.setObjectName("ghostButton")
        delete.setObjectName("dangerButton")
        close.setObjectName("ghostButton")
        add.clicked.connect(self.add)
        test.clicked.connect(self.test_reminder)
        edit.clicked.connect(self.edit)
        done.clicked.connect(self.toggle)
        delete.clicked.connect(self.delete)
        close.clicked.connect(self.close)
        for button in (add, test, edit, done, delete):
            row.addWidget(button)
        row.addStretch(1)
        row.addWidget(close)
        layout.addLayout(row)
        self.refresh()

    def todo_remind_text(self, todo):
        remind_at = todo.get("remind_at", "")
        if not remind_at:
            return "无提醒"
        at = parse_local_minutes(remind_at)
        if not at:
            return "提醒时间格式异常"
        delta = at - datetime.now()
        if delta.total_seconds() <= 0:
            return f"提醒：{remind_at}"
        if delta.days > 0:
            return f"提醒：{remind_at}（还有 {delta.days} 天）"
        return f"提醒：{remind_at}（还有 {max(1, int(delta.total_seconds() // 60))} 分钟）"

    def refresh(self):
        self.list.clear()
        active = sorted(self.todos, key=lambda item: (item.get("done", False), item.get("remind_at", "9999")))
        self.todos = active
        for todo in self.todos:
            prefix = "✓" if todo.get("done") else "□"
            title = todo.get("title", "")
            self.list.addItem(f"{prefix} {title}\n{self.todo_remind_text(todo)}")

    def save(self):
        save_json(TODOS, self.todos)
        self.refresh()

    def pick(self, row):
        if 0 <= row < len(self.todos):
            todo = self.todos[row]
            self.input.setText(todo.get("title", ""))
            remind_at = todo.get("remind_at", "")
            self.remind_enabled.setChecked(bool(remind_at))
            parsed = parse_local_minutes(remind_at) if remind_at else None
            self.remind_at.setDateTime(parsed or datetime.now() + timedelta(hours=1))

    def set_reminder_datetime(self, value):
        self.remind_enabled.setChecked(True)
        self.remind_at.setDateTime(value)

    def set_reminder_delta(self, minutes=0, hours=0, days=0):
        self.set_reminder_datetime(datetime.now() + timedelta(minutes=minutes, hours=hours, days=days))

    def set_reminder_at(self, hour, minute=0, day_offset=0):
        self.set_reminder_datetime(next_time_at(hour, minute, day_offset))

    def disable_reminder(self):
        self.remind_enabled.setChecked(False)

    def parse_input_title_time(self, text):
        parsed = parse_time_text_without_trigger(text)
        if parsed:
            return parsed["title"], parsed["remind_at"]
        return text, None

    def build_payload(self, title, existing=None, remind_at_override=None):
        todo = dict(existing or {})
        todo["title"] = title
        todo.setdefault("id", str(time.time()))
        todo.setdefault("done", False)
        todo.setdefault("created_at", datetime.now().isoformat(timespec="seconds"))
        todo["reminded"] = False
        if remind_at_override is not None:
            todo["remind_at"] = remind_at_override
        else:
            todo["remind_at"] = self.remind_at.dateTime().toString("yyyy-MM-dd HH:mm") if self.remind_enabled.isChecked() else ""
        return todo

    def add(self):
        raw_title = self.input.text().strip()
        title, parsed_remind_at = self.parse_input_title_time(raw_title)
        if not title:
            return
        self.todos.append(self.build_payload(title, remind_at_override=parsed_remind_at))
        self.input.clear()
        self.remind_enabled.setChecked(True)
        self.remind_at.setDateTime(datetime.now() + timedelta(hours=1))
        self.save()

    def edit(self):
        row = self.list.currentRow()
        raw_title = self.input.text().strip()
        title, parsed_remind_at = self.parse_input_title_time(raw_title)
        if 0 <= row < len(self.todos) and title:
            self.todos[row] = self.build_payload(title, self.todos[row], parsed_remind_at)
            self.save()

    def test_reminder(self):
        text = "测试提醒：如果你看到这条，提醒功能正常。"
        parent = self.parent()
        if parent is not None and hasattr(parent, "notify_due_reminder"):
            parent.notify_due_reminder("提醒事项测试", text, QSystemTrayIcon.Information)
        else:
            QMessageBox.information(self, "提醒事项测试", text)

    def toggle(self):
        row = self.list.currentRow()
        if 0 <= row < len(self.todos):
            self.todos[row]["done"] = not self.todos[row].get("done", False)
            self.save()

    def delete(self):
        row = self.list.currentRow()
        if 0 <= row < len(self.todos):
            self.todos.pop(row)
            self.input.clear()
            self.save()


class StudyDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.logs = load_json(STUDY, [])
        self.setWindowTitle("学习统计")
        self.resize(560, 600)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("学习统计")
        title.setObjectName("title")
        hint = QLabel("记录学习或休息时长，今日统计会按科目汇总。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        form = QFormLayout()
        self.subject = QComboBox()
        self.subject.setEditable(True)
        self.subject.addItems(["高数", "408", "英语", "政治", "专业课"])
        self.subject.setCurrentText(config.get("Subject", "高数"))
        self.minutes = QSpinBox()
        self.minutes.setRange(1, 600)
        self.minutes.setValue(int(config.get("FocusMinutes", 50)))
        self.mode = QComboBox()
        self.mode.addItems(["学习", "休息"])
        form.addRow("科目", self.subject)
        form.addRow("分钟", self.minutes)
        form.addRow("类型", self.mode)
        layout.addLayout(form)

        row = QHBoxLayout()
        add = QPushButton("记录")
        focus = QPushButton("记一轮番茄")
        rest = QPushButton("记一次休息")
        close = QPushButton("关闭")
        add.setObjectName("sendButton")
        focus.setObjectName("ghostButton")
        rest.setObjectName("ghostButton")
        close.setObjectName("ghostButton")
        add.clicked.connect(self.add_log)
        focus.clicked.connect(self.add_focus)
        rest.clicked.connect(self.add_rest)
        close.clicked.connect(self.close)
        row.addWidget(add)
        row.addWidget(focus)
        row.addWidget(rest)
        row.addStretch(1)
        row.addWidget(close)
        layout.addLayout(row)

        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setObjectName("panel")
        layout.addWidget(self.summary)
        self.refresh()

    def append_log(self, subject, minutes, mode):
        self.logs.append(
            {
                "at": datetime.now().isoformat(timespec="seconds"),
                "subject": subject,
                "minutes": int(minutes),
                "mode": mode,
            }
        )
        save_json(STUDY, self.logs)
        self.refresh()

    def add_log(self):
        subject = self.subject.currentText().strip() or "学习"
        self.append_log(subject, self.minutes.value(), self.mode.currentText())

    def add_focus(self):
        subject = self.subject.currentText().strip() or self.config.get("Subject", "高数")
        self.append_log(subject, int(self.config.get("FocusMinutes", 50)), "学习")

    def add_rest(self):
        self.append_log("休息", int(self.config.get("RestMinutes", 10)), "休息")

    def refresh(self):
        today = datetime.now().date()
        study, rest = study_breakdown(self.logs, today)
        total = sum(study.values())
        lines = [f"今日学习：{format_minutes(total)}", f"今日休息：{format_minutes(rest)}"]
        lines.append(f"连续学习：{consecutive_study_days(self.logs)} 天")
        lines.append("")
        if study:
            lines.append("科目明细：")
            for subject, minutes in sorted(study.items(), key=lambda item: item[0]):
                lines.append(f"- {subject}：{format_minutes(minutes)}")
        else:
            lines.append("今天还没有学习记录。")
        lines.append("")
        lines.append("最近记录：")
        for item in self.logs[-12:][::-1]:
            lines.append(
                f"- {item.get('at', '')[:16]}  {item.get('mode', '学习')}  "
                f"{item.get('subject', '')}  {format_minutes(item.get('minutes', 0))}"
            )
        self.summary.setPlainText("\n".join(lines))


class ClaudeProfileWorker(QThread):
    result = Signal(object)

    def run(self):
        try:
            self.result.emit(claude_code_profile())
        except Exception as exc:
            self.result.emit({"error": str(exc), "installed": False})


class ClaudeCodeLauncherDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.profile_worker = None
        self.setWindowTitle("Claude Code 中文启动器")
        self.resize(720, 650)
        self.setMinimumSize(620, 560)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("Claude Code 中文启动器")
        title.setObjectName("title")
        layout.addWidget(title)

        hint = QLabel(
            "选择项目和工作方式后启动。糯米会默认要求 AI 全程使用简体中文，"
            "英文命令和报错会附带中文解释。"
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        status_row = QHBoxLayout()
        self.status = QLabel()
        self.status.setObjectName("hint")
        self.status.setWordWrap(True)
        refresh = QPushButton("检查环境")
        refresh.setObjectName("ghostButton")
        refresh.clicked.connect(self.refresh_status)
        status_row.addWidget(self.status, 1)
        status_row.addWidget(refresh)
        layout.addLayout(status_row)

        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(10)

        self.project = QComboBox()
        self.project.setEditable(True)
        self.project.addItems(claude_project_candidates(config))
        last_project = str(config.get("ClaudeLastProject") or BASE)
        self.project.setCurrentText(last_project)
        self.project.lineEdit().setPlaceholderText("选择包含代码的项目文件夹")
        project_row = QWidget()
        project_layout = QHBoxLayout(project_row)
        project_layout.setContentsMargins(0, 0, 0, 0)
        project_layout.setSpacing(8)
        browse = QPushButton("浏览")
        browse.setObjectName("ghostButton")
        browse.clicked.connect(self.choose_project)
        open_folder = QPushButton("打开文件夹")
        open_folder.setObjectName("ghostButton")
        open_folder.clicked.connect(self.open_project_folder)
        project_layout.addWidget(self.project, 1)
        project_layout.addWidget(browse)
        project_layout.addWidget(open_folder)
        form.addRow("项目文件夹", project_row)

        self.session_mode = QComboBox()
        self.session_mode.addItem("新建会话", "new")
        self.session_mode.addItem("继续当前项目上次会话", "continue")
        self.session_mode.addItem("从历史会话中选择", "resume")
        self.set_combo_data(self.session_mode, config.get("ClaudeSessionMode", "new"))
        form.addRow("会话方式", self.session_mode)

        self.permission_mode = QComboBox()
        self.permission_mode.addItem("标准确认（推荐）", "default")
        self.permission_mode.addItem("只制定计划，不修改文件", "plan")
        self.permission_mode.addItem("自动接受文件修改", "acceptEdits")
        self.permission_mode.addItem("自动判断是否需要确认", "auto")
        self.permission_mode.addItem("尽量少询问（慎用）", "dontAsk")
        self.set_combo_data(self.permission_mode, config.get("ClaudePermissionMode", "default"))
        form.addRow("权限方式", self.permission_mode)

        self.effort = QComboBox()
        self.effort.addItem("快速", "low")
        self.effort.addItem("平衡（推荐）", "medium")
        self.effort.addItem("深入", "high")
        self.effort.addItem("很深入", "xhigh")
        self.effort.addItem("最高", "max")
        self.set_combo_data(self.effort, config.get("ClaudeEffort", "medium"))
        form.addRow("思考强度", self.effort)
        layout.addLayout(form)

        quick_title = QLabel("常用任务")
        quick_title.setObjectName("hint")
        layout.addWidget(quick_title)
        quick = QGridLayout()
        quick.setHorizontalSpacing(8)
        quick.setVerticalSpacing(8)
        for index, (label, prompt) in enumerate(CLAUDE_TASK_TEMPLATES):
            button = QPushButton(label)
            button.setObjectName("ghostButton")
            button.clicked.connect(lambda _checked=False, text=prompt: self.apply_template(text))
            quick.addWidget(button, index // 3, index % 3)
        layout.addLayout(quick)

        prompt_title = QLabel("想让它做什么")
        prompt_title.setObjectName("hint")
        layout.addWidget(prompt_title)
        self.prompt = QPlainTextEdit()
        self.prompt.setPlaceholderText(
            "可以留空直接进入对话，也可以写：帮我检查这个项目为什么运行失败，并直接修复。"
        )
        self.prompt.setMinimumHeight(120)
        layout.addWidget(self.prompt, 1)

        options = QHBoxLayout()
        self.always_chinese = QCheckBox("始终使用简体中文")
        self.always_chinese.setChecked(bool(config.get("ClaudeAlwaysChinese", True)))
        self.safe_mode = QCheckBox("安全模式（配置异常时使用）")
        self.safe_mode.setChecked(bool(config.get("ClaudeSafeMode", False)))
        options.addWidget(self.always_chinese)
        options.addWidget(self.safe_mode)
        options.addStretch(1)
        layout.addLayout(options)

        note = QLabel("说明：Claude Code 自带的命令名可能仍是英文，但回答、操作说明和错误解释会优先显示中文。")
        note.setObjectName("hint")
        note.setWordWrap(True)
        layout.addWidget(note)

        footer = QHBoxLayout()
        close = QPushButton("取消")
        close.setObjectName("ghostButton")
        close.clicked.connect(self.reject)
        launch = QPushButton("启动 Claude Code")
        launch.setObjectName("sendButton")
        launch.clicked.connect(self.launch)
        footer.addStretch(1)
        footer.addWidget(close)
        footer.addWidget(launch)
        layout.addLayout(footer)

        self.refresh_status()

    def set_combo_data(self, combo, value):
        index = combo.findData(value)
        combo.setCurrentIndex(index if index >= 0 else 0)

    def refresh_status(self):
        if self.profile_worker and self.profile_worker.isRunning():
            return
        self.status.setText("环境状态：正在检查 Claude Code...")
        self.profile_worker = ClaudeProfileWorker()
        self.profile_worker.result.connect(self.render_status)
        self.profile_worker.finished.connect(lambda: setattr(self, "profile_worker", None))
        self.profile_worker.start()

    def render_status(self, profile):
        if profile.get("error"):
            self.status.setText(f"环境状态：检查失败：{profile.get('error')}")
            return
        if not profile["installed"]:
            self.status.setText("环境状态：未找到 Claude Code，请先安装或修复 Claude Code。")
            return
        version = profile["version"] or "版本未知"
        settings = "DeepSeek 配置已加载" if profile["settings"] else "未找到 DeepSeek 配置"
        credential = "凭据已配置" if profile["credential_ready"] else "凭据未配置"
        self.status.setText(
            f"环境状态：{version} | {settings} | 接口 {profile['provider']} | "
            f"模型 {profile['model']} | {credential}"
        )

    def closeEvent(self, event):
        detach_running_worker(self.profile_worker, ("result", "finished"))
        self.profile_worker = None
        super().closeEvent(event)

    def choose_project(self):
        start = self.project.currentText().strip() or str(BASE)
        path = QFileDialog.getExistingDirectory(self, "选择 Claude Code 项目文件夹", start)
        if not path:
            return
        if self.project.findText(path) < 0:
            self.project.insertItem(0, path)
        self.project.setCurrentText(path)

    def project_path(self):
        text = self.project.currentText().strip()
        if not text:
            return None
        return Path(os.path.abspath(os.path.expandvars(os.path.expanduser(text))))

    def open_project_folder(self):
        path = self.project_path()
        if path is None or not path.is_dir():
            QMessageBox.information(self, "项目文件夹", "请先选择一个存在的项目文件夹。")
            return
        try:
            os.startfile(str(path))
        except Exception as exc:
            QMessageBox.information(self, "项目文件夹", f"打开失败：{exc}")

    def apply_template(self, text):
        self.prompt.setPlainText(text)
        self.prompt.setFocus()

    def save_preferences(self, project):
        recent = [str(project)]
        for path in claude_project_candidates(self.config):
            if os.path.normcase(path) != os.path.normcase(str(project)):
                recent.append(path)
        self.config["ClaudeLastProject"] = str(project)
        self.config["ClaudeRecentProjects"] = recent[:8]
        self.config["ClaudeSessionMode"] = self.session_mode.currentData()
        self.config["ClaudePermissionMode"] = self.permission_mode.currentData()
        self.config["ClaudeEffort"] = self.effort.currentData()
        self.config["ClaudeAlwaysChinese"] = self.always_chinese.isChecked()
        self.config["ClaudeSafeMode"] = self.safe_mode.isChecked()
        save_json(CONFIG, self.config)

    def launch(self):
        project = self.project_path()
        if project is None or not project.is_dir():
            QMessageBox.information(self, "Claude Code", "项目文件夹不存在，请重新选择。")
            return
        self.save_preferences(project)
        ok, message = launch_claude_code_terminal(
            prompt=self.prompt.toPlainText(),
            cwd=project,
            session_mode=self.session_mode.currentData(),
            permission_mode=self.permission_mode.currentData(),
            effort=self.effort.currentData(),
            always_chinese=self.always_chinese.isChecked(),
            safe_mode=self.safe_mode.isChecked(),
        )
        if not ok:
            QMessageBox.information(self, "Claude Code", message)
            self.refresh_status()
            return
        parent = self.parent()
        self.accept()
        if parent is not None and hasattr(parent, "bubble"):
            QTimer.singleShot(0, lambda: parent.bubble.say(message + "，已启用中文说明。"))


class TodayBoardDialog(QDialog):
    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        pet_name = str(pet.config.get("PetName") or DEFAULT_CONFIG["PetName"])
        self.setWindowTitle("今日看板")
        self.resize(660, 640)
        self.setMinimumSize(560, 520)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("今日看板")
        title.setObjectName("title")
        layout.addWidget(title)

        next_lines = today_next_action_lines(pet)
        headline = QLabel("现在最该注意：" + (next_lines[0] if next_lines else "今天先从最小的一步开始。"))
        headline.setObjectName("hint")
        headline.setWordWrap(True)
        layout.addWidget(headline)

        sections = QGridLayout()
        sections.setHorizontalSpacing(10)
        sections.setVerticalSpacing(10)
        section_items = [
            ("下一步行动", next_lines),
            ("待办 / 日程", upcoming_todo_lines(4) + [""] + upcoming_event_lines(4)),
            ("天气 / 邮件", [weather_card_text(getattr(pet, "weather_text", f"{pet.config.get('WeatherCity', '上海')} 天气读取中")), mail_dashboard_text()]),
            ("电脑状态", compact_health_lines(pet.config)),
            ("电池 / 电源", battery_status_lines(pet.config)),
            ("考研 / 学习", today_study_lines(pet.config)),
        ]
        for index, (name, lines) in enumerate(section_items):
            sections.addWidget(self.make_section(name, lines), index // 2, index % 2)
        layout.addLayout(sections)

        actions_title = QLabel("快捷动作")
        actions_title.setObjectName("hint")
        layout.addWidget(actions_title)

        actions = QGridLayout()
        actions.setHorizontalSpacing(8)
        actions.setVerticalSpacing(8)
        action_items = [
            ("添加提醒", pet.open_todos),
            ("打开日程", pet.open_calendar),
            ("查看邮件", pet.open_mail),
            ("电脑诊断", pet.open_diagnostics),
            ("桌面整理", pet.open_desktop_organizer),
            (f"和{pet_name}聊聊", pet.open_ai),
        ]
        for index, (label, fn) in enumerate(action_items):
            button = QPushButton(label)
            button.setObjectName("ghostButton" if index else "sendButton")
            button.clicked.connect(lambda _checked=False, action=fn: self.run_pet_action(action))
            actions.addWidget(button, index // 3, index % 3)
        layout.addLayout(actions)

        close = QPushButton("关闭")
        close.setObjectName("ghostButton")
        close.clicked.connect(self.close)
        footer = QHBoxLayout()
        footer.addStretch(1)
        footer.addWidget(close)
        layout.addLayout(footer)

    def make_section(self, title, lines):
        panel = QTextEdit()
        panel.setReadOnly(True)
        panel.setObjectName("panel")
        panel.setLineWrapMode(QTextEdit.WidgetWidth)
        panel.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        panel.setMinimumHeight(104)
        panel.setMaximumHeight(150)
        content = [title, ""]
        content.extend(line for line in lines if str(line).strip())
        panel.setPlainText("\n".join(content))
        return panel

    def run_pet_action(self, action):
        self.accept()
        QTimer.singleShot(0, action)


class TranslateDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker = None
        self.pending_delta = ""
        self.delta_timer = QTimer(self)
        self.delta_timer.setInterval(45)
        self.delta_timer.timeout.connect(self.flush_delta)
        self.setWindowTitle("翻译")
        self.resize(640, 560)
        self.setMinimumSize(500, 420)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("翻译")
        title.setObjectName("title")
        hint = QLabel("输入文本后选择方向。会优先直译，再给出更自然的表达。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        top = QHBoxLayout()
        self.direction = QComboBox()
        self.direction.addItems(
            [
                "自动识别",
                "中文 → 英文",
                "英文 → 中文",
                "中文 → 日文",
                "日文 → 中文",
                "英文 → 日文",
                "日文 → 英文",
                "润色中文",
                "润色英文",
                "润色日文",
            ]
        )
        translate = QPushButton("翻译")
        translate.setObjectName("sendButton")
        copy = QPushButton("复制结果")
        cancel = QPushButton("取消")
        copy.setObjectName("ghostButton")
        cancel.setObjectName("dangerButton")
        translate.clicked.connect(self.translate)
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.output.toPlainText()))
        cancel.clicked.connect(self.cancel)
        top.addWidget(self.direction)
        top.addStretch(1)
        top.addWidget(translate)
        top.addWidget(copy)
        top.addWidget(cancel)
        layout.addLayout(top)
        self.input = QPlainTextEdit()
        self.input.setPlaceholderText("把要翻译的文字贴到这里")
        self.input.setMinimumHeight(135)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setMinimumHeight(190)
        layout.addWidget(self.input, 2)
        layout.addWidget(self.output, 3)

    def translate(self):
        text = self.input.toPlainText().strip()
        if not text:
            self.output.setPlainText("先输入要翻译的文本。")
            return
        if self.worker and self.worker.isRunning():
            return
        direction = self.direction.currentText()
        prompt = (
            f"翻译方向：{direction}\n"
            "要求：先给准确译文，再给一个更自然的表达；如果有术语或歧义，简单说明。\n\n"
            f"文本：\n{text}"
        )
        self.output.clear()
        self.pending_delta = ""
        self.worker = AiWorker(self.config, "翻译", prompt)
        self.worker.delta.connect(self.queue_delta)
        self.worker.done.connect(self.finish)
        self.worker.finished.connect(lambda: setattr(self, "worker", None))
        self.delta_timer.start()
        self.worker.start()

    def queue_delta(self, text):
        self.pending_delta += text

    def flush_delta(self):
        if not self.pending_delta:
            return
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(self.pending_delta)
        self.pending_delta = ""

    def finish(self, final_text):
        self.flush_delta()
        self.delta_timer.stop()
        if not self.output.toPlainText().strip():
            self.output.setPlainText(final_text)

    def cancel(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()

    def closeEvent(self, event):
        self.delta_timer.stop()
        detach_running_worker(self.worker, ("delta", "done", "finished"), cancel=True)
        self.worker = None
        super().closeEvent(event)


class ClipboardDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("剪贴板记录")
        self.resize(560, 520)
        self.setMinimumSize(440, 340)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        self.items = []
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("剪贴板记录")
        title.setObjectName("title")
        hint = QLabel("只记录本机文字剪贴板；疑似密钥、密码、长 token 会自动跳过。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        row = QHBoxLayout()
        copy = QPushButton("复制选中")
        delete = QPushButton("删除")
        clear = QPushButton("清空")
        close = QPushButton("关闭")
        copy.setObjectName("sendButton")
        delete.setObjectName("ghostButton")
        clear.setObjectName("dangerButton")
        close.setObjectName("ghostButton")
        copy.clicked.connect(self.copy_selected)
        delete.clicked.connect(self.delete_selected)
        clear.clicked.connect(self.clear_all)
        close.clicked.connect(self.close)
        row.addWidget(copy)
        row.addWidget(delete)
        row.addWidget(clear)
        row.addStretch(1)
        row.addWidget(close)
        layout.addLayout(row)
        self.refresh()

    def refresh(self):
        self.items = load_clipboard_history()
        self.list.clear()
        if not self.items:
            self.list.addItem("还没有剪贴板记录。复制一些文字后会出现在这里。")
            return
        for item in self.items:
            at = item.get("created_at", "")[:16].replace("T", " ")
            self.list.addItem(f"{at}\n{clipboard_preview(item.get('text', ''), 120)}")

    def copy_selected(self):
        row = self.list.currentRow()
        if 0 <= row < len(self.items):
            text = self.items[row].get("text", "")
            parent = self.parent()
            if parent and hasattr(parent, "clipboard_ignore_once"):
                parent.clipboard_ignore_once = normalize_clipboard_text(text)
            QApplication.clipboard().setText(text)
            self.refresh()

    def delete_selected(self):
        row = self.list.currentRow()
        if 0 <= row < len(self.items):
            self.items.pop(row)
            save_clipboard_history(self.items)
            self.refresh()

    def clear_all(self):
        save_clipboard_history([])
        self.refresh()


class ActionLabDialog(QDialog):
    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        self.setWindowTitle("动作测试")
        self.resize(430, 360)
        self.setMinimumSize(360, 300)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("动作测试")
        title.setObjectName("title")
        hint = QLabel("用来快速检查糯米的状态、动作速度和素材效果。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        actions = [
            ("开心", lambda: pet.react("开心", "嘿嘿~")),
            ("惊讶", lambda: pet.react("惊讶", "Σ( ° △ °|||)︴")),
            ("睡觉", lambda: pet.react("睡觉", "Zzz...")),
            ("学习", pet.dog_reading),
            ("伸懒腰", pet.dog_stretch),
            ("闻一闻", pet.dog_sniff),
            ("左走", lambda: pet.short_walk_direction(-1)),
            ("右走", lambda: pet.short_walk_direction(1)),
            ("呼吸", pet.next_breath),
        ]
        for index, (label, fn) in enumerate(actions):
            button = QPushButton(label)
            button.setObjectName("ghostButton")
            button.clicked.connect(fn)
            grid.addWidget(button, index // 3, index % 3)
        layout.addLayout(grid)

        close = QPushButton("关闭")
        close.setObjectName("sendButton")
        close.clicked.connect(self.close)
        layout.addWidget(close)


class OnlineUpdateWorker(QThread):
    result = Signal(object)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = dict(config or {})

    def run(self):
        try:
            self.result.emit({"ok": True, **download_latest_update(self.config)})
        except Exception as exc:
            self.result.emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


class GitHubBackupWorker(QThread):
    result = Signal(object)

    def __init__(self, publish_update=False, parent=None):
        super().__init__(parent)
        self.publish_update = bool(publish_update)

    def run(self):
        try:
            self.result.emit({"ok": True, **manual_github_backup(publish_update=self.publish_update)})
        except Exception as exc:
            self.result.emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


class BackupExportWorker(QThread):
    result = Signal(object)

    def __init__(self, mode, path, include_secrets=False, include_clipboard=True):
        super().__init__()
        self.mode = mode
        self.path = path
        self.include_secrets = include_secrets
        self.include_clipboard = include_clipboard

    def run(self):
        try:
            if self.mode == "portable":
                target = create_portable_package(
                    self.path,
                    include_secrets=self.include_secrets,
                    include_clipboard=self.include_clipboard,
                )
            else:
                target = create_backup_archive(
                    self.path,
                    include_secrets=self.include_secrets,
                    include_clipboard=self.include_clipboard,
                )
            self.result.emit({"ok": True, "mode": self.mode, "target": str(target)})
        except Exception as exc:
            self.result.emit({"ok": False, "mode": self.mode, "error": f"{type(exc).__name__}: {exc}"})


class BackupRestoreWorker(QThread):
    result = Signal(object)

    def __init__(self, path, restore_secrets=False):
        super().__init__()
        self.path = path
        self.restore_secrets = restore_secrets

    def run(self):
        try:
            restored = restore_backup_archive(self.path, restore_secrets=self.restore_secrets)
            self.result.emit({"ok": True, "restored": restored})
        except Exception as exc:
            self.result.emit({"ok": False, "error": f"{type(exc).__name__}: {exc}"})


class FeatureSwitchDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.checks = {}
        self.setWindowTitle("功能开关")
        self.resize(720, 680)
        self.setMinimumSize(580, 520)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)

        title = QLabel("功能开关")
        title.setObjectName("title")
        root.addWidget(title)

        hint = QLabel("关闭后会停用对应后台行为，并从右键快捷菜单隐藏入口。设置、功能开关、隐藏和退出会一直保留。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        root.addWidget(hint)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        panel = QWidget()
        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(10)

        for group_name, items in FEATURE_SWITCH_GROUPS:
            section = QLabel(group_name)
            section.setObjectName("sectionTitle")
            panel_layout.addWidget(section)
            for key, label, description, _safe in items:
                row = QFrame()
                row.setObjectName("panel")
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(12, 10, 12, 10)
                row_layout.setSpacing(10)
                display_label = feature_display_label(key, config)
                text = QLabel(f"<b>{display_label}</b><br><span style='color:#94a3b8'>{description}</span>")
                text.setWordWrap(True)
                check = QCheckBox("开启")
                check.setChecked(feature_enabled(config, key))
                self.checks[key] = check
                row_layout.addWidget(text, 1)
                row_layout.addWidget(check)
                panel_layout.addWidget(row)
        panel_layout.addStretch(1)
        scroll.setWidget(panel)
        root.addWidget(scroll, 1)

        actions = QHBoxLayout()
        safe_all = QPushButton("安全全开启")
        defaults = QPushButton("恢复默认")
        cancel = QPushButton("取消")
        save = QPushButton("保存")
        safe_all.setObjectName("sendButton")
        defaults.setObjectName("ghostButton")
        cancel.setObjectName("ghostButton")
        save.setObjectName("sendButton")
        safe_all.clicked.connect(self.safe_enable_all)
        defaults.clicked.connect(self.restore_defaults)
        cancel.clicked.connect(self.reject)
        save.clicked.connect(self.save)
        actions.addWidget(safe_all)
        actions.addWidget(defaults)
        actions.addStretch(1)
        actions.addWidget(cancel)
        actions.addWidget(save)
        root.addLayout(actions)

    def safe_enable_all(self):
        for item in FEATURE_SWITCH_ITEMS:
            if item["safe"]:
                self.checks[item["key"]].setChecked(True)

    def restore_defaults(self):
        for key, check in self.checks.items():
            check.setChecked(bool(DEFAULT_CONFIG.get(key, True)))

    def save(self):
        for key, check in self.checks.items():
            self.config[key] = check.isChecked()
        save_json(CONFIG, self.config)
        parent = self.parent()
        if parent is not None and hasattr(parent, "apply_feature_switch_changes"):
            parent.apply_feature_switch_changes()
        self.accept()


class BackupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("备份 / 迁移")
        self.resize(700, 500)
        self.setMinimumSize(560, 420)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)

        title = QLabel("备份 / 迁移")
        title.setObjectName("title")
        hint = QLabel(
            f"当前版本 {APP_VERSION}。可打包迁移到另一台电脑，也可从 GitHub 联网更新程序；"
            "个人设置和密钥不会被在线更新覆盖。"
        )
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        self.include_clipboard = QCheckBox("导出时包含剪贴板记录")
        self.include_clipboard.setChecked(True)
        self.include_secrets = QCheckBox("导出时包含 AI Key / 邮箱授权码（敏感）")
        self.include_secrets.setChecked(False)
        self.restore_secrets = QCheckBox("导入时覆盖 AI Key / 邮箱授权码")
        self.restore_secrets.setChecked(False)
        layout.addWidget(self.include_clipboard)
        layout.addWidget(self.include_secrets)
        layout.addWidget(self.restore_secrets)

        self.status = QLabel("备份文件会保存到 backups 文件夹，也可以自己选择位置。")
        self.status.setObjectName("panel")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        row = QHBoxLayout()
        export_btn = QPushButton("导出备份")
        portable_btn = QPushButton("导出整机迁移包")
        self.export_btn = export_btn
        self.portable_btn = portable_btn
        self.update_btn = QPushButton("检查联网更新")
        import_btn = QPushButton("导入备份")
        folder_btn = QPushButton("打开文件夹")
        close_btn = QPushButton("关闭")
        self.import_btn = import_btn
        export_btn.setObjectName("sendButton")
        portable_btn.setObjectName("sendButton")
        self.update_btn.setObjectName("sendButton")
        import_btn.setObjectName("ghostButton")
        folder_btn.setObjectName("ghostButton")
        close_btn.setObjectName("ghostButton")
        export_btn.clicked.connect(self.export_backup)
        portable_btn.clicked.connect(self.export_portable_package)
        self.update_btn.clicked.connect(self.check_online_update)
        import_btn.clicked.connect(self.import_backup)
        folder_btn.clicked.connect(self.open_backup_folder)
        close_btn.clicked.connect(self.close)
        row.addWidget(export_btn)
        row.addWidget(portable_btn)
        row.addWidget(self.update_btn)
        row.addWidget(import_btn)
        row.addWidget(folder_btn)
        row.addStretch(1)
        row.addWidget(close_btn)
        layout.addLayout(row)

        github_row = QHBoxLayout()
        self.github_backup_btn = QPushButton("手动上传到 GitHub")
        self.github_backup_btn.setObjectName("sendButton")
        self.github_backup_btn.clicked.connect(self.upload_github_backup)
        github_hint = QLabel("上传程序代码到 GitHub 仓库；不会上传 pet-config.json、聊天记录、邮箱状态、备份包和截图。")
        github_hint.setObjectName("hint")
        github_hint.setWordWrap(True)
        self.publish_update_release = QCheckBox("同时发布联网更新包（另一台电脑可检测到）")
        self.publish_update_release.setChecked(True)
        github_row.addWidget(self.github_backup_btn)
        github_row.addWidget(github_hint, 1)
        layout.addLayout(github_row)
        layout.addWidget(self.publish_update_release)
        self.update_btn.setVisible(feature_enabled(load_config(), "OnlineUpdateFeatureEnabled"))
        self.github_backup_btn.setVisible(feature_enabled(load_config(), "GithubUploadFeatureEnabled"))
        github_hint.setVisible(feature_enabled(load_config(), "GithubUploadFeatureEnabled"))
        self.publish_update_release.setVisible(feature_enabled(load_config(), "GithubUploadFeatureEnabled"))
        self.update_worker = None
        self.github_backup_worker = None
        self.backup_export_worker = None
        self.backup_restore_worker = None

    def check_online_update(self):
        if not feature_enabled(load_config(), "OnlineUpdateFeatureEnabled"):
            QMessageBox.information(self, "功能已关闭", "联网检查更新已在功能开关里关闭。")
            return
        if self.update_worker and self.update_worker.isRunning():
            return
        self.update_btn.setEnabled(False)
        self.status.setText(f"正在连接 GitHub 检查更新：{update_repo_name(load_config())}")
        self.update_worker = OnlineUpdateWorker(load_config(), self)
        self.update_worker.result.connect(self.online_update_finished)
        self.update_worker.start()

    def online_update_finished(self, result):
        self.update_btn.setEnabled(True)
        if not result.get("ok"):
            self.status.setText("联网更新检查失败：" + result.get("error", "未知错误"))
            return
        release = result.get("release", {})
        if not result.get("available"):
            self.status.setText(f"当前已是最新版：{APP_VERSION}")
            QMessageBox.information(self, "无需更新", f"当前版本 {APP_VERSION} 已是最新版。")
            return
        version = release.get("version", "")
        self.status.setText(f"版本 {version} 已下载并校验，等待安装。")
        reply = QMessageBox.question(
            self,
            "安装在线更新",
            f"已下载糯米 {version}。\n\n安装时桌宠会自动重启，个人设置和邮箱配置不会被覆盖。现在安装吗？",
        )
        if reply != QMessageBox.Yes:
            return
        try:
            schedule_staged_update(result["stage"])
        except Exception as exc:
            self.status.setText(f"无法启动更新安装：{exc}")
            return
        self.status.setText("正在重启并安装更新……")
        QApplication.quit()

    def upload_github_backup(self):
        if self.github_backup_worker and self.github_backup_worker.isRunning():
            return
        if not feature_enabled(load_config(), "GithubUploadFeatureEnabled"):
            QMessageBox.information(self, "功能已关闭", "手动上传到 GitHub 已在功能开关里关闭。")
            return
        reply = QMessageBox.question(
            self,
            "手动上传到 GitHub",
            "将把当前程序代码提交并推送到 GitHub origin。\n\n"
            "不会上传 pet-config.json、聊天记录、剪贴板、邮箱状态、备份包、截图等个人数据。\n\n"
            "如果勾选“同时发布联网更新包”，还会用 GitHub CLI 发布 Release；另一台电脑就是通过这个 Release 检测更新。\n\n"
            "现在开始上传吗？",
        )
        if reply != QMessageBox.Yes:
            return
        self.github_backup_btn.setEnabled(False)
        publish_update = self.publish_update_release.isChecked()
        self.status.setText(
            "正在手动上传到 GitHub：检查敏感文件、创建提交并推送到远程仓库"
            + ("，并发布联网更新包……" if publish_update else "……")
        )
        self.github_backup_worker = GitHubBackupWorker(publish_update=publish_update, parent=self)
        self.github_backup_worker.result.connect(self.github_backup_finished)
        self.github_backup_worker.start()

    def github_backup_finished(self, result):
        self.github_backup_btn.setEnabled(True)
        if not result.get("ok"):
            error = result.get("error", "未知错误")
            self.status.setText("GitHub 手动上传失败：" + error)
            QMessageBox.warning(self, "GitHub 上传失败", error)
            return
        files = result.get("files", [])
        branch = result.get("branch", "")
        commit_hash = result.get("commit", "")
        if result.get("committed"):
            summary = f"已上传到 GitHub：分支 {branch}，提交 {commit_hash}，包含 {len(files)} 个文件。"
        else:
            summary = f"GitHub 已检查：没有新的本地改动，远程分支 {branch} 已是提交 {commit_hash}。"
        update_release = result.get("update_release") or {}
        if update_release.get("requested"):
            if update_release.get("ok"):
                summary += (
                    f"\n\n已发布联网更新包：{update_release.get('tag')} "
                    f"({update_release.get('repo')})。另一台电脑现在可以检查更新。"
                )
            else:
                summary += (
                    "\n\n注意：代码已经上传，但联网更新包没有发布成功。"
                    "另一台电脑暂时检测不到这次更新。\n原因："
                    + update_release.get("error", "未知错误")
                )
        self.status.setText(summary)
        QMessageBox.information(self, "GitHub 上传完成", summary)

    def export_backup(self):
        if self.backup_task_running():
            return
        BACKUP_DIR.mkdir(exist_ok=True)
        default_name = BACKUP_DIR / f"nuomi-backup-{datetime.now():%Y%m%d-%H%M%S}.zip"
        path, _ = QFileDialog.getSaveFileName(self, "导出糯米备份", str(default_name), "Zip backup (*.zip)")
        if not path:
            return
        self.start_backup_export("backup", path)

    def export_portable_package(self):
        if self.backup_task_running():
            return
        BACKUP_DIR.mkdir(exist_ok=True)
        if not self.include_secrets.isChecked():
            reply = QMessageBox.question(
                self,
                "敏感配置未包含",
                "当前没有勾选“包含 AI Key / 邮箱授权码”。\n\n"
                "迁移包会包含程序、Python、动作包、记忆、学习记录、待办和日程，"
                "但新电脑上 AI 与 QQ 邮箱需要重新填写密钥/授权码。\n\n"
                "继续导出吗？",
            )
            if reply != QMessageBox.Yes:
                return
        default_name = BACKUP_DIR / f"nuomi-portable-{datetime.now():%Y%m%d-%H%M%S}.zip"
        path, _ = QFileDialog.getSaveFileName(self, "导出糯米整机迁移包", str(default_name), "Portable package (*.zip)")
        if not path:
            return
        self.start_backup_export("portable", path)

    def start_backup_export(self, mode, path):
        self.set_backup_buttons_enabled(False)
        title = "整机迁移包" if mode == "portable" else "备份"
        self.status.setText(f"正在导出{title}，窗口可继续响应，请稍等...")
        self.backup_export_worker = BackupExportWorker(
            mode,
            path,
            include_secrets=self.include_secrets.isChecked(),
            include_clipboard=self.include_clipboard.isChecked(),
        )
        self.backup_export_worker.result.connect(self.backup_export_finished)
        self.backup_export_worker.finished.connect(lambda: setattr(self, "backup_export_worker", None))
        self.backup_export_worker.start()

    def backup_export_finished(self, result):
        self.set_backup_buttons_enabled(True)
        mode = result.get("mode", "backup")
        if not result.get("ok"):
            title = "迁移包导出失败" if mode == "portable" else "备份失败"
            error = result.get("error", "未知错误")
            self.status.setText(title + "：" + error)
            QMessageBox.warning(self, title, error)
            return
        target = result.get("target", "")
        if mode == "portable":
            self.status.setText(f"已导出整机迁移包：{target}\n新电脑解压后双击 START_HERE.bat。")
            QMessageBox.information(self, "迁移包完成", "糯米整机迁移包已导出。\n新电脑解压后双击 START_HERE.bat。")
        else:
            self.status.setText(f"已导出：{target}")
            QMessageBox.information(self, "备份完成", "糯米的备份已经导出。")

    def import_backup(self):
        if self.backup_task_running():
            return
        path, _ = QFileDialog.getOpenFileName(self, "导入糯米备份", str(BACKUP_DIR), "Zip backup (*.zip)")
        if not path:
            return
        reply = QMessageBox.question(self, "确认导入", "导入会覆盖当前糯米数据。要继续吗？")
        if reply != QMessageBox.Yes:
            return
        self.start_backup_restore(path)

    def backup_task_running(self):
        workers = [self.backup_export_worker, self.backup_restore_worker]
        return any(worker is not None and worker.isRunning() for worker in workers)

    def set_backup_buttons_enabled(self, enabled):
        self.export_btn.setEnabled(enabled)
        self.portable_btn.setEnabled(enabled)
        self.import_btn.setEnabled(enabled)

    def start_backup_restore(self, path):
        self.set_backup_buttons_enabled(False)
        self.status.setText("正在导入备份，窗口可继续响应，请稍等...")
        self.backup_restore_worker = BackupRestoreWorker(path, restore_secrets=self.restore_secrets.isChecked())
        self.backup_restore_worker.result.connect(self.backup_restore_finished)
        self.backup_restore_worker.finished.connect(lambda: setattr(self, "backup_restore_worker", None))
        self.backup_restore_worker.start()

    def backup_restore_finished(self, result):
        self.set_backup_buttons_enabled(True)
        if not result.get("ok"):
            error = result.get("error", "未知错误")
            self.status.setText("导入失败：" + error)
            QMessageBox.warning(self, "导入失败", error)
            return
        restored = result.get("restored", [])
        self.status.setText("已恢复：" + "、".join(restored))
        parent = self.parent()
        if parent and hasattr(parent, "reload_after_restore"):
            parent.reload_after_restore()
        QMessageBox.information(self, "导入完成", "糯米数据已恢复。")

    def open_backup_folder(self):
        BACKUP_DIR.mkdir(exist_ok=True)
        try:
            os.startfile(str(BACKUP_DIR))
        except Exception as exc:
            QMessageBox.information(self, "备份文件夹", f"{BACKUP_DIR}\n{exc}")

    def closeEvent(self, event):
        active_workers = [
            self.update_worker,
            self.github_backup_worker,
            self.backup_export_worker,
            self.backup_restore_worker,
        ]
        if any(worker is not None and worker.isRunning() for worker in active_workers):
            self.status.setText("任务正在运行，完成后再关闭这个窗口。")
            event.ignore()
            return
        super().closeEvent(event)


class DiagnosticWorker(QThread):
    result = Signal(str)

    def __init__(self, task, config):
        super().__init__()
        self.task = task
        self.config = dict(config)

    def run(self):
        try:
            if self.task == "ai":
                self.result.emit(self.test_ai())
            elif self.task == "mail":
                self.result.emit(self.test_mail())
            else:
                self.result.emit(self.status_text())
        except Exception as exc:
            self.result.emit(f"诊断失败：{exc}")

    def status_text(self):
        lines = ["糯米诊断中心", ""]
        lines.append(f"配置文件：{CONFIG}")
        lines.append(f"运行日志：{RUNTIME_LOG}")
        lines.append("")
        lines.append(f"AI：{'已配置' if self.config.get('AiEndpoint') and self.config.get('AiModel') and self.config.get('AiApiKey') else '未完整配置'}")
        mail_accounts = mail_accounts_from_config(self.config)
        lines.append(f"邮箱：{'已配置 ' + str(len(mail_accounts)) + ' 个账号' if mail_accounts else '未完整配置'}")
        tesseract = configured_tesseract_path(self.config)
        lines.append(f"OCR：{'可用' if tesseract and Path(tesseract).exists() else '未配置 Tesseract'}")
        lines.append(f"动作包：{self.config.get('ActionPackPath') or '使用内置动作包'}")
        lines.append(f"安静模式：{'开启' if self.config.get('QuietMode') else '关闭'}")
        lines.append(f"全屏自动安静：{'开启' if self.config.get('AutoQuietFullscreen', True) else '关闭'}")
        lines.append(f"全屏游戏自动隐藏：{'开启' if self.config.get('AutoHideFullscreen', True) else '关闭'}")
        lines.append(f"游戏前台自动隐藏：{'开启' if self.config.get('AutoHideGames', True) else '关闭'}")
        lines.append(f"自恢复：{'开启' if self.config.get('WatchdogEnabled', True) else '关闭'}")
        lines.append(f"watchdog：{'运行中' if is_watchdog_running() else '未运行'}")
        lines.append(f"开机启动：{'已安装' if startup_entry_installed() else '未安装或需修复'}")
        matches = matching_startup_entries()
        if matches:
            lines.append("相关启动项：" + "，".join(path.name for path in matches))
        lines.append(f"VPN：{detect_vpn_status_cached()}")
        codex = detect_codex_process_cached()
        lines.append(f"Codex：{codex}")
        lines.extend(system_health_lines(self.config))
        lines.extend(hardware_info_lines())
        return "\n".join(lines)

    def test_ai(self):
        endpoint = self.config.get("AiEndpoint", "").strip()
        key = self.config.get("AiApiKey", "")
        model = self.config.get("AiModel", "").strip()
        if not endpoint or not key or not model:
            return "AI 测试：未完整配置 API 地址、模型或 Key。"
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": "ping"}],
            "max_tokens": 8,
            "stream": False,
        }
        headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        response = httpx.post(endpoint, json=payload, headers=headers, timeout=20)
        if response.status_code >= 400:
            return f"AI 测试失败：HTTP {response.status_code}。Key 已隐藏。"
        return f"AI 测试通过：HTTP {response.status_code}，模型 {model}。"

    def test_mail(self):
        messages, error = fetch_unread_mail(self.config, limit=1)
        if error:
            return f"邮箱测试失败：{error}"
        unread = messages[0].get("unread_count", 0) if messages else 0
        return f"邮箱测试通过：最近未读 {unread} 封。"


class DiagnosticsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.worker = None
        self.setWindowTitle("糯米诊断中心")
        self.resize(620, 500)
        self.setMinimumSize(520, 380)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("糯米诊断中心")
        title.setObjectName("title")
        hint = QLabel("这里会检查 AI、邮箱、OCR、开机启动、自恢复和运行状态。敏感信息只判断是否存在，不会显示出来。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setObjectName("panel")
        layout.addWidget(self.output, 1)
        row = QHBoxLayout()
        refresh = QPushButton("刷新状态")
        ai = QPushButton("测试 AI")
        mail = QPushButton("测试邮箱")
        startup = QPushButton("修复开机启动")
        log_btn = QPushButton("打开日志")
        close = QPushButton("关闭")
        refresh.setObjectName("sendButton")
        ai.setObjectName("ghostButton")
        mail.setObjectName("ghostButton")
        startup.setObjectName("ghostButton")
        log_btn.setObjectName("ghostButton")
        close.setObjectName("ghostButton")
        refresh.clicked.connect(lambda: self.run_task("status"))
        ai.clicked.connect(lambda: self.run_task("ai"))
        mail.clicked.connect(lambda: self.run_task("mail"))
        startup.clicked.connect(self.repair_startup)
        log_btn.clicked.connect(self.open_log)
        close.clicked.connect(self.close)
        for button in (refresh, ai, mail, startup, log_btn):
            row.addWidget(button)
        row.addStretch(1)
        row.addWidget(close)
        layout.addLayout(row)
        self.run_task("status")

    def run_task(self, task):
        if self.worker and self.worker.isRunning():
            return
        self.output.setPlainText("正在诊断，稍等一下……")
        self.worker = DiagnosticWorker(task, self.config)
        self.worker.result.connect(self.output.setPlainText)
        self.worker.finished.connect(lambda: setattr(self, "worker", None))
        self.worker.start()

    def repair_startup(self):
        try:
            path = repair_startup_entry()
        except Exception as exc:
            QMessageBox.warning(self, "修复失败", str(exc))
            return
        self.output.setPlainText(f"已修复开机启动：\n{path}\n\n下次登录 Windows 时会先启动 watchdog，再由它拉起糯米。")

    def open_log(self):
        try:
            if not RUNTIME_LOG.exists():
                RUNTIME_LOG.write_text("", encoding="utf-8")
            os.startfile(str(RUNTIME_LOG))
        except Exception as exc:
            QMessageBox.information(self, "运行日志", f"{RUNTIME_LOG}\n{exc}")

    def closeEvent(self, event):
        detach_running_worker(self.worker, ("result", "finished"))
        self.worker = None
        super().closeEvent(event)


class BatteryReportWorker(QThread):
    result = Signal(object)

    def __init__(self, target):
        super().__init__()
        self.target = str(target)

    def run(self):
        target = Path(self.target)
        try:
            completed = subprocess.run(
                ["powercfg", "/batteryreport", "/output", str(target)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=25,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
        except Exception as exc:
            self.result.emit({"ok": False, "error": f"生成失败：{exc}", "target": str(target)})
            return
        if completed.returncode != 0 or not target.exists():
            self.result.emit(
                {
                    "ok": False,
                    "error": "Windows 没有生成电池报告；台式机或无电池设备可能不支持。",
                    "target": str(target),
                }
            )
            return
        self.result.emit({"ok": True, "target": str(target)})


class BatteryDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = dict(config or {})
        self.status_text = ""
        self.setWindowTitle("电池 / 电源")
        self.resize(580, 390)
        self.setMinimumSize(500, 340)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("电池 / 电源")
        title.setObjectName("title")
        layout.addWidget(title)

        self.status = QLabel()
        self.status.setObjectName("panel")
        self.status.setWordWrap(True)
        self.status.setMinimumHeight(125)
        layout.addWidget(self.status)

        self.updated = QLabel()
        self.updated.setObjectName("hint")
        layout.addWidget(self.updated)
        layout.addStretch(1)

        actions = QHBoxLayout()
        refresh = QPushButton("刷新")
        refresh.setObjectName("sendButton")
        report = QPushButton("生成电池报告")
        self.report_btn = report
        self.report_worker = None
        settings = QPushButton("电源设置")
        copy = QPushButton("复制状态")
        close = QPushButton("关闭")
        for button in (report, settings, copy, close):
            button.setObjectName("ghostButton")
        refresh.clicked.connect(self.refresh)
        report.clicked.connect(self.generate_report)
        settings.clicked.connect(self.open_power_settings)
        copy.clicked.connect(lambda: QApplication.clipboard().setText(self.status_text))
        close.clicked.connect(self.close)
        for button in (refresh, report, settings, copy):
            actions.addWidget(button)
        actions.addStretch(1)
        actions.addWidget(close)
        layout.addLayout(actions)

        self.timer = QTimer(self)
        self.timer.setInterval(15_000)
        self.timer.timeout.connect(self.refresh)
        self.timer.start()
        self.refresh()

    def refresh(self):
        snapshot = battery_snapshot()
        lines = battery_status_lines(self.config, snapshot)
        self.status_text = "\n".join(lines)
        self.status.setText(self.status_text)
        self.updated.setText(f"更新时间：{datetime.now():%H:%M:%S}")

    def open_power_settings(self):
        try:
            os.startfile("ms-settings:powersleep")
        except Exception as exc:
            QMessageBox.information(self, "电源设置", f"无法打开 Windows 电源设置：{exc}")

    def generate_report(self):
        if self.report_worker and self.report_worker.isRunning():
            return
        BACKUP_DIR.mkdir(exist_ok=True)
        target = BACKUP_DIR / f"battery-report-{datetime.now():%Y%m%d-%H%M%S}.html"
        self.report_btn.setEnabled(False)
        self.updated.setText("正在生成电池报告，窗口可继续响应...")
        self.report_worker = BatteryReportWorker(target)
        self.report_worker.result.connect(self.battery_report_finished)
        self.report_worker.finished.connect(lambda: setattr(self, "report_worker", None))
        self.report_worker.start()

    def battery_report_finished(self, result):
        self.report_btn.setEnabled(True)
        if not result.get("ok"):
            QMessageBox.information(self, "电池报告", result.get("error", "生成失败"))
            return
        target = result.get("target", "")
        try:
            os.startfile(target)
        except Exception:
            pass
        QMessageBox.information(self, "电池报告", f"报告已保存：\n{target}")

    def closeEvent(self, event):
        if self.report_worker and self.report_worker.isRunning():
            self.updated.setText("电池报告正在生成，完成后再关闭这个窗口。")
            event.ignore()
            return
        super().closeEvent(event)


class PerformanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scan_worker = None
        self.delete_worker = None
        self.large_worker = None
        self.desktop_scan_worker = None
        self.desktop_move_worker = None
        self.cleanup_items = []
        self.large_files = []
        self.desktop_plan = []
        self.setWindowTitle("糯米清理 / 性能中心")
        self.resize(720, 560)
        self.setMinimumSize(580, 420)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("清理 / 性能中心")
        title.setObjectName("title")
        hint = QLabel("先扫描、再勾选、最后确认。这里只清理缓存和临时文件，不碰注册表和系统关键目录。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        self.summary = QLabel(f"{disk_usage_summary()}\n点“扫描可清理空间”开始。")
        self.summary.setObjectName("panel")
        self.summary.setWordWrap(True)
        layout.addWidget(self.summary)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        row1 = QHBoxLayout()
        scan = QPushButton("扫描可清理空间")
        clean = QPushButton("清理所选")
        large = QPushButton("查找大文件")
        processes = QPushButton("资源占用")
        desktop = QPushButton("扫描桌面整理")
        self.scan_btn = scan
        self.clean_btn = clean
        self.large_btn = large
        self.desktop_scan_btn = desktop
        scan.setObjectName("sendButton")
        clean.setObjectName("dangerButton")
        large.setObjectName("ghostButton")
        processes.setObjectName("ghostButton")
        desktop.setObjectName("ghostButton")
        scan.clicked.connect(self.scan_cleanup)
        clean.clicked.connect(self.clean_selected)
        large.clicked.connect(self.find_large)
        processes.clicked.connect(self.show_processes)
        desktop.clicked.connect(self.scan_desktop_organize)
        for button in (scan, clean, large, processes, desktop):
            row1.addWidget(button)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        organize = QPushButton("整理所选桌面文件")
        open_location = QPushButton("打开所选位置")
        storage = QPushButton("Windows 存储设置")
        startup = QPushButton("启动项设置")
        disk_cleanup = QPushButton("系统磁盘清理")
        taskmgr = QPushButton("任务管理器")
        close = QPushButton("关闭")
        self.desktop_organize_btn = organize
        organize.setObjectName("sendButton")
        for button in (open_location, storage, startup, disk_cleanup, taskmgr, close):
            button.setObjectName("ghostButton")
        organize.clicked.connect(self.organize_selected_desktop_files)
        open_location.clicked.connect(self.open_selected_location)
        storage.clicked.connect(lambda: self.open_uri("ms-settings:storagesense"))
        startup.clicked.connect(lambda: self.open_uri("ms-settings:startupapps"))
        disk_cleanup.clicked.connect(self.open_disk_cleanup)
        taskmgr.clicked.connect(lambda: subprocess.Popen(["taskmgr"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL))
        close.clicked.connect(self.close)
        row2.addWidget(organize)
        for button in (open_location, storage, startup, disk_cleanup, taskmgr):
            row2.addWidget(button)
        row2.addStretch(1)
        row2.addWidget(close)
        layout.addLayout(row2)

    def set_busy(self, text):
        self.summary.setText(text)
        self.list.clear()
        self.list.addItem(text)
        self.set_task_buttons_enabled(False)

    def set_task_buttons_enabled(self, enabled):
        for button in (
            getattr(self, "scan_btn", None),
            getattr(self, "clean_btn", None),
            getattr(self, "large_btn", None),
            getattr(self, "desktop_scan_btn", None),
            getattr(self, "desktop_organize_btn", None),
        ):
            if button is not None:
                button.setEnabled(bool(enabled))

    def scan_cleanup(self):
        if self.scan_worker and self.scan_worker.isRunning():
            return
        self.set_busy("糯米正在闻缓存味道……")
        self.scan_worker = CleanupScanWorker()
        self.scan_worker.result.connect(self.render_cleanup)
        self.scan_worker.finished.connect(lambda: setattr(self, "scan_worker", None))
        self.scan_worker.start()

    def render_cleanup(self, items, error):
        self.set_task_buttons_enabled(True)
        self.list.clear()
        if error:
            self.summary.setText(f"扫描失败：{error}")
            return
        self.cleanup_items = items
        total = sum(item.get("bytes", 0) for item in items)
        self.summary.setText(f"{disk_usage_summary()}\n预计可清理：{human_bytes(total)}。建议只勾选你看得懂的项。")
        if not items:
            self.list.addItem("没有找到可扫描的缓存目录。")
            return
        for item in items:
            suffix = "；已截断扫描" if item.get("truncated") else ""
            text = (
                f"{item.get('label')}  {human_bytes(item.get('bytes', 0))}\n"
                f"{item.get('path')}\n"
                f"{item.get('count', 0)} 个文件，跳过 {item.get('skipped', 0)} 个{suffix}\n"
                f"{item.get('note', '')}"
            )
            widget_item = QListWidgetItem(text)
            widget_item.setData(Qt.UserRole, item)
            widget_item.setCheckState(Qt.Checked if item.get("bytes", 0) > 0 else Qt.Unchecked)
            self.list.addItem(widget_item)

    def selected_cleanup_items(self):
        selected = []
        for row in range(self.list.count()):
            item = self.list.item(row)
            data = item.data(Qt.UserRole)
            if isinstance(data, dict) and data.get("files") and item.checkState() == Qt.Checked:
                selected.append(data)
        return selected

    def clean_selected(self):
        items = self.selected_cleanup_items()
        if not items:
            QMessageBox.information(self, "清理所选", "先扫描并勾选要清理的缓存项。")
            return
        total = sum(item.get("bytes", 0) for item in items)
        names = "、".join(item.get("label", "") for item in items)
        reply = QMessageBox.question(
            self,
            "确认清理",
            f"准备清理：{names}\n预计释放：{human_bytes(total)}\n\n只会删除扫描出来的缓存/临时文件，锁定文件会跳过。继续吗？",
        )
        if reply != QMessageBox.Yes:
            return
        self.set_busy("正在清理，糯米会避开被占用的文件……")
        self.delete_worker = CleanupDeleteWorker(items)
        self.delete_worker.result.connect(self.finish_cleanup)
        self.delete_worker.finished.connect(lambda: setattr(self, "delete_worker", None))
        self.delete_worker.start()

    def finish_cleanup(self, deleted, freed, skipped, error):
        self.set_task_buttons_enabled(True)
        if error:
            self.summary.setText(f"清理失败：{error}")
            return
        self.summary.setText(f"清理完成：删除 {deleted} 个文件，释放 {human_bytes(freed)}，跳过 {skipped} 个。")
        self.list.clear()
        self.list.addItem("清理完成。可以再次扫描看看还剩多少。")

    def find_large(self):
        if self.large_worker and self.large_worker.isRunning():
            return
        self.set_busy("正在查找 Downloads、Desktop、Documents 和 D:\\CodexProjects 里的大文件……")
        self.large_worker = LargeFileWorker()
        self.large_worker.result.connect(self.render_large_files)
        self.large_worker.finished.connect(lambda: setattr(self, "large_worker", None))
        self.large_worker.start()

    def render_large_files(self, files, error):
        self.set_task_buttons_enabled(True)
        self.list.clear()
        self.large_files = files
        if error:
            self.summary.setText(f"查找失败：{error}")
            return
        if not files:
            self.summary.setText("没有找到 50MB 以上的大文件。")
            self.list.addItem("挺干净的。")
            return
        self.summary.setText(f"找到 {len(files)} 个 50MB 以上文件。这里只展示，不自动删除。")
        for file in files:
            item = QListWidgetItem(f"{human_bytes(file['bytes'])}  {file['modified']}\n{file['path']}")
            item.setData(Qt.UserRole, file)
            self.list.addItem(item)

    def scan_desktop_organize(self):
        if self.desktop_scan_worker and self.desktop_scan_worker.isRunning():
            return
        self.set_busy("正在扫描桌面文件，先生成归类预览……")
        self.desktop_scan_worker = DesktopOrganizeScanWorker()
        self.desktop_scan_worker.result.connect(self.render_desktop_plan)
        self.desktop_scan_worker.finished.connect(lambda: setattr(self, "desktop_scan_worker", None))
        self.desktop_scan_worker.start()

    def render_desktop_plan(self, plan, skipped, error):
        self.set_task_buttons_enabled(True)
        self.list.clear()
        self.desktop_plan = plan
        if error:
            self.summary.setText(f"桌面扫描失败：{error}")
            return
        if not plan:
            self.summary.setText(f"桌面没有可整理的文件。已跳过 {skipped} 项文件夹/系统文件/保留文件。")
            self.list.addItem("没有需要整理的桌面文件。")
            return
        total = sum(item.get("bytes", 0) for item in plan)
        categories = {}
        for item in plan:
            categories[item.get("category", "其他")] = categories.get(item.get("category", "其他"), 0) + 1
        category_text = "，".join(f"{name}{count}个" for name, count in sorted(categories.items()))
        self.summary.setText(
            f"找到 {len(plan)} 个桌面文件，合计 {human_bytes(total)}。\n"
            f"将移动到桌面/桌面整理 下的分类文件夹：{category_text}。已跳过 {skipped} 项。"
        )
        for item in plan:
            text = (
                f"{item.get('category')}  {human_bytes(item.get('bytes', 0))}  {item.get('modified')}\n"
                f"{item.get('path')}\n"
                f"→ {item.get('dest')}"
            )
            widget_item = QListWidgetItem(text)
            widget_item.setData(Qt.UserRole, item)
            widget_item.setCheckState(Qt.Checked)
            self.list.addItem(widget_item)

    def selected_desktop_plan_items(self):
        selected = []
        for row in range(self.list.count()):
            item = self.list.item(row)
            data = item.data(Qt.UserRole)
            if isinstance(data, dict) and data.get("dest") and item.checkState() == Qt.Checked:
                selected.append(data)
        return selected

    def organize_selected_desktop_files(self):
        items = self.selected_desktop_plan_items()
        if not items:
            QMessageBox.information(self, "整理桌面", "先点“扫描桌面整理”，再勾选要移动的桌面文件。")
            return
        reply = QMessageBox.question(
            self,
            "确认整理桌面",
            f"准备移动 {len(items)} 个桌面文件到“桌面整理”分类文件夹。\n\n"
            "只移动勾选的文件，不移动文件夹；重名文件会自动加序号。继续吗？",
        )
        if reply != QMessageBox.Yes:
            return
        self.set_busy("正在整理桌面文件……")
        self.desktop_move_worker = DesktopOrganizeMoveWorker(items)
        self.desktop_move_worker.result.connect(self.finish_desktop_organize)
        self.desktop_move_worker.finished.connect(lambda: setattr(self, "desktop_move_worker", None))
        self.desktop_move_worker.start()

    def finish_desktop_organize(self, moved, skipped, error):
        self.set_task_buttons_enabled(True)
        if error:
            self.summary.setText(f"整理失败：{error}")
            return
        self.summary.setText(f"桌面整理完成：移动 {moved} 个文件，跳过 {skipped} 个。")
        self.list.clear()
        self.list.addItem("整理完成。分类文件夹在桌面的“桌面整理”里。")

    def show_processes(self):
        self.list.clear()
        rows = top_resource_processes()
        self.summary.setText("按内存占用排序。糯米只展示，不直接结束进程。")
        for row in rows:
            item = QListWidgetItem(f"{row['name']}  PID {row['pid']}  内存 {human_bytes(row['memory'])}  CPU {row['cpu']:.1f}%\n{row['exe']}")
            item.setData(Qt.UserRole, row)
            self.list.addItem(item)

    def open_selected_location(self):
        item = self.list.currentItem()
        if not item:
            return
        data = item.data(Qt.UserRole)
        path_text = ""
        if isinstance(data, dict):
            path_text = data.get("path") or data.get("exe") or ""
        if not path_text:
            return
        path = Path(path_text)
        target = path if path.is_dir() else path.parent
        if target.exists():
            try:
                subprocess.Popen(["explorer", str(target)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as exc:
                QMessageBox.information(self, "打开位置", str(exc))

    def open_uri(self, uri):
        try:
            os.startfile(uri)
        except Exception:
            webbrowser.open(uri)

    def open_disk_cleanup(self):
        try:
            subprocess.Popen(["cleanmgr"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as exc:
            QMessageBox.information(self, "系统磁盘清理", str(exc))

    def active_worker_labels(self):
        workers = [
            (self.scan_worker, "清理扫描"),
            (self.delete_worker, "清理文件"),
            (self.large_worker, "大文件扫描"),
            (self.desktop_scan_worker, "桌面整理扫描"),
            (self.desktop_move_worker, "桌面文件移动"),
        ]
        return [label for worker, label in workers if worker is not None and worker.isRunning()]

    def closeEvent(self, event):
        active = self.active_worker_labels()
        if active:
            self.summary.setText("正在运行：" + "、".join(active) + "。完成后再关闭这个窗口。")
            event.ignore()
            return
        super().closeEvent(event)


class FileSearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.closing = False
        self.results = []
        self.roots = file_search_roots()
        self.setWindowTitle("糯米找文件")
        self.resize(740, 560)
        self.setMinimumSize(600, 420)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(12)
        title = QLabel("找文件")
        title.setObjectName("title")
        hint = QLabel("默认搜常用位置和文件名。需要更深一点时再选 D盘/用户目录，内容搜索只扫小文本文件。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        layout.addWidget(title)
        layout.addWidget(hint)

        top = QGridLayout()
        top.setHorizontalSpacing(8)
        top.setVerticalSpacing(8)
        self.query = QLineEdit()
        self.query.setPlaceholderText("输入文件名关键词，比如 论文 pdf、截图、ai_moe_pet")
        self.scope = QComboBox()
        self.scope.addItems(list(self.roots.keys()))
        self.kind = QComboBox()
        self.kind.addItems(["全部"] + list(FILE_KIND_EXTENSIONS.keys()))
        self.include_content = QCheckBox("同时搜索文本内容")
        self.include_content.setChecked(False)
        top.addWidget(self.query, 0, 0, 1, 3)
        top.addWidget(self.scope, 0, 3)
        top.addWidget(self.kind, 0, 4)
        top.addWidget(self.include_content, 1, 0, 1, 2)
        layout.addLayout(top)

        self.status = QLabel("输入关键词后点搜索。")
        self.status.setObjectName("panel")
        self.status.setWordWrap(True)
        layout.addWidget(self.status)

        self.list = QListWidget()
        layout.addWidget(self.list, 1)

        row = QHBoxLayout()
        search = QPushButton("搜索")
        stop = QPushButton("停止")
        open_file = QPushButton("打开文件")
        open_folder = QPushButton("打开位置")
        copy_path = QPushButton("复制路径")
        close = QPushButton("关闭")
        self.search_btn = search
        self.stop_btn = stop
        self.stop_btn.setEnabled(False)
        search.setObjectName("sendButton")
        stop.setObjectName("dangerButton")
        for button in (open_file, open_folder, copy_path, close):
            button.setObjectName("ghostButton")
        search.clicked.connect(self.search)
        stop.clicked.connect(self.stop)
        open_file.clicked.connect(self.open_selected_file)
        open_folder.clicked.connect(self.open_selected_folder)
        copy_path.clicked.connect(self.copy_selected_path)
        close.clicked.connect(self.close)
        for button in (search, stop, open_file, open_folder, copy_path):
            row.addWidget(button)
        row.addStretch(1)
        row.addWidget(close)
        layout.addLayout(row)
        self.query.returnPressed.connect(self.search)

    def search(self):
        if self.worker and self.worker.isRunning():
            return
        query = self.query.text().strip()
        if not query:
            self.status.setText("先输入要找的文件名或关键词。")
            return
        roots = self.roots.get(self.scope.currentText(), [])
        if not roots:
            self.status.setText("这个范围暂时没有可搜索的目录。")
            return
        self.list.clear()
        self.results = []
        self.status.setText("糯米正在翻文件夹……")
        self.search_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.worker = FileSearchWorker(query, roots, self.kind.currentText(), self.include_content.isChecked())
        self.worker.progress.connect(self.status.setText)
        self.worker.result.connect(self.render_results)
        self.worker.finished.connect(self.search_worker_finished)
        self.worker.start()

    def stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancel()
            self.stop_btn.setEnabled(False)
            self.status.setText("正在停止搜索……")

    def render_results(self, results, error, truncated):
        self.list.clear()
        self.results = results
        if error:
            self.status.setText(f"搜索出错：{error}")
            return
        suffix = "，结果太多已截断到前 500 个" if truncated else ""
        self.status.setText(f"找到 {len(results)} 个结果{suffix}。")
        if not results:
            self.list.addItem("没有找到。换个关键词或扩大搜索范围试试。")
            return
        for result in results:
            item = QListWidgetItem(
                f"{result['name']}  {human_bytes(result['bytes'])}  {result['modified']}  匹配：{result['match']}\n{result['path']}"
            )
            item.setData(Qt.UserRole, result)
            self.list.addItem(item)

    def selected_result(self):
        item = self.list.currentItem()
        if not item:
            return None
        data = item.data(Qt.UserRole)
        return data if isinstance(data, dict) else None

    def open_selected_file(self):
        result = self.selected_result()
        if not result:
            return
        path = result.get("path", "")
        try:
            os.startfile(path)
        except Exception as exc:
            QMessageBox.information(self, "打开文件", str(exc))

    def open_selected_folder(self):
        result = self.selected_result()
        if not result:
            return
        path = Path(result.get("path", ""))
        if not path.exists():
            return
        try:
            subprocess.Popen(["explorer", "/select,", str(path)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            subprocess.Popen(["explorer", str(path.parent)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def copy_selected_path(self):
        result = self.selected_result()
        if not result:
            return
        QApplication.clipboard().setText(result.get("path", ""))
        self.status.setText("路径已复制。")

    def search_worker_finished(self):
        self.worker = None
        self.search_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

    def closeEvent(self, event):
        self.closing = True
        detach_running_worker(self.worker, ("progress", "result", "finished"), cancel=True)
        self.worker = None
        super().closeEvent(event)


class PetSmartMenu(QDialog):
    def __init__(self, pet):
        super().__init__(pet)
        self.pet = pet
        self.setObjectName("smartMenu")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(smart_menu_style(pet.config))
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(0)
        self.scroll = None
        content = QWidget()
        content.setObjectName("smartMenuContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(10)
        pet_name = str(pet.config.get("PetName") or DEFAULT_CONFIG["PetName"])

        title = QLabel(pet_name)
        title.setObjectName("smartTitle")
        memory = yesterday_study_memory()
        hint = QLabel(memory or time_greeting())
        hint.setObjectName("smartHint")
        layout.addWidget(title)
        layout.addWidget(hint)

        task_text = "\n".join(today_task_lines())
        weather = weather_card_text(getattr(pet, "weather_text", "上海 天气读取中"))
        metrics = QGridLayout()
        metrics.setHorizontalSpacing(8)
        metrics.setVerticalSpacing(8)
        cards = [
            ("考研", exam_countdown_text(pet.config), pet.study_summary, {}),
            ("今日", today_dashboard_text(pet), pet.open_today_board, {}),
            ("任务", task_text, pet.open_todos, {}),
            ("日程", next_event_preview(), pet.open_calendar, {}),
            ("天气", weather, pet.open_weather, {"max_lines": 3, "max_chars": 18, "reserve_lines": 4}),
            ("邮件", mail_dashboard_text(), pet.open_mail, {}),
        ]
        card_features = ["StudyFeatureEnabled", "TodayFeatureEnabled", "TodoFeatureEnabled", "CalendarFeatureEnabled", "WeatherFeatureEnabled", "MailFeatureEnabled"]
        visible_index = 0
        for index, (card_title, detail, fn, card_options) in enumerate(cards):
            if not feature_enabled(pet.config, card_features[index]):
                continue
            index = visible_index
            visible_index += 1
            metrics.addWidget(self.make_card_button(card_title, detail, fn, **card_options), index // 2, index % 2)
        layout.addLayout(metrics)

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setVerticalSpacing(8)
        primary = [
            ("工具箱", "工具箱", pet.open_core_toolbox),
            ("Claude", "中文启动", pet.open_claude_code),
            ("问问", f"和{pet_name}聊聊", pet.open_ai),
            ("截图", "OCR 提问", pet.ocr_screenshot),
            ("文件", "快速查找", pet.open_file_search),
            ("清理", "空间/性能", pet.open_performance),
            ("整理", "桌面归类", pet.open_desktop_organizer),
            ("单词", "弹出词汇", pet.open_word_popup),
            ("公式", "数学速查", pet.open_formula_search),
        ]
        primary_features = [
            "ToolboxFeatureEnabled",
            "ClaudeFeatureEnabled",
            "AiFeatureEnabled",
            "OcrFeatureEnabled",
            "FileSearchFeatureEnabled",
            "PerformanceFeatureEnabled",
            "DesktopOrganizerFeatureEnabled",
            "word_popup_enabled",
            "FormulaFeatureEnabled",
        ]
        visible_index = 0
        for index, (label, hint_text, fn) in enumerate(primary):
            if not feature_enabled(pet.config, primary_features[index]):
                continue
            index = visible_index
            visible_index += 1
            grid.addWidget(self.make_button(label, hint_text, fn, "smartPrimary"), index // 3, index % 3)
        layout.addLayout(grid)

        section = QLabel("常用")
        section.setObjectName("smartSection")
        layout.addWidget(section)

        tools = QGridLayout()
        tools.setHorizontalSpacing(8)
        tools.setVerticalSpacing(8)
        bubble_action_label = "关气泡" if pet.config.get("BubbleEnabled", True) else "开气泡"
        tool_items = [
            ("翻译", pet.open_translate),
            ("剪贴板", pet.open_clipboard),
            ("动作", pet.open_action_lab),
            ("诊断", pet.open_diagnostics),
            ("词库", pet.open_notebook),
            ("电池", pet.open_battery),
            (bubble_action_label, pet.toggle_bubble_enabled),
            ("单词开关", pet.toggle_word_popup),
        ]
        tool_features = [
            "TranslateFeatureEnabled",
            "ClipboardHistoryEnabled",
            "ActionLabFeatureEnabled",
            "DiagnosticsFeatureEnabled",
            "NotebookFeatureEnabled",
            "BatteryFeatureEnabled",
            None,
            "word_popup_enabled",
        ]
        visible_index = 0
        for index, (label, fn) in enumerate(tool_items):
            feature_key = tool_features[index]
            if feature_key is not None and not feature_enabled(pet.config, feature_key):
                continue
            index = visible_index
            visible_index += 1
            tools.addWidget(self.make_button(label, "", fn, "smartSecondary"), index // 4, index % 4)
        layout.addLayout(tools)

        small = QGridLayout()
        small.setHorizontalSpacing(8)
        small.setVerticalSpacing(8)
        secondary = [
            ("功能", pet.open_feature_switch),
            ("设置", pet.open_settings),
            ("说明", pet.open_help),
            ("收起", pet.hide_to_tray),
            ("重启", pet.restart_pet),
            ("退出", pet.exit_pet),
        ]
        for index, (label, fn) in enumerate(secondary):
            small.addWidget(self.make_button(label, "", fn, "smartSmall"), index // 3, index % 3)
        layout.addLayout(small)

        screen = QApplication.screenAt(QCursor.pos()) or QApplication.primaryScreen()
        bounds = screen.availableGeometry() if screen else QRect(0, 0, 1280, 720)
        max_height = max(260, bounds.height() - 28)
        max_width = max(300, min(560, bounds.width() - 28))
        content_hint = content.sizeHint()
        preferred_width = min(max_width, max(420, content_hint.width() + 24))
        natural_height = content_hint.height() + 18
        preferred_height = min(max_height, max(360, natural_height))
        if natural_height <= max_height:
            outer.addWidget(content)
        else:
            self.scroll = QScrollArea()
            self.scroll.setObjectName("smartMenuScroll")
            self.scroll.setWidgetResizable(True)
            self.scroll.setFrameShape(QFrame.NoFrame)
            self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            self.scroll.setWidget(content)
            self.scroll.verticalScrollBar().setSingleStep(max(48, text_font_sizes(self.pet.config)["menu"] * 4))
            self.scroll.verticalScrollBar().setPageStep(max(160, preferred_height - 72))
            outer.addWidget(self.scroll)
            self.scroll.setMinimumHeight(max(220, preferred_height - 16))
            self.scroll.setMaximumHeight(max(220, preferred_height - 16))
        self.setFixedSize(preferred_width, preferred_height)

    def make_button(self, label, hint, fn, role):
        button = QPushButton(f"{label}\n{hint}" if hint else label)
        button.setObjectName(role)
        if role == "smartPrimary":
            button.setMinimumWidth(112)
            button.setMinimumHeight(60)
        elif role == "smartSecondary":
            button.setMinimumWidth(104)
            button.setMinimumHeight(44)
        else:
            button.setMinimumWidth(104)
            button.setMinimumHeight(40)
        button.clicked.connect(lambda: self.run(fn))
        return button

    def make_card_button(self, title, detail, fn, max_lines=2, max_chars=22, reserve_lines=0):
        full_detail = str(detail or "").strip()
        detail_text = compact_card_detail(full_detail, max_lines=max_lines, max_chars=max_chars)
        button = QPushButton()
        button.setObjectName("smartMetricButton")
        if full_detail:
            button.setToolTip(full_detail)
        inner = QVBoxLayout(button)
        inner.setContentsMargins(10, 8, 10, 8)
        inner.setSpacing(3)
        title_label = QLabel(title)
        title_label.setObjectName("smartMetricTitle")
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        detail_label = QLabel(detail_text)
        detail_label.setObjectName("smartMetricDetail")
        detail_label.setWordWrap(True)
        detail_label.setTextFormat(Qt.PlainText)
        detail_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        detail_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        inner.addWidget(title_label)
        if detail_text:
            inner.addWidget(detail_label)
        inner.addStretch(1)
        button.setMinimumWidth(156)
        line_count = 1 + max(1, len(detail_text.splitlines()) if detail_text else 0)
        line_count = max(line_count, int(reserve_lines or 0))
        line_height = max(16, int(text_font_sizes(self.pet.config)["menu"] * 1.38))
        button.setMinimumHeight(max(88, line_height * line_count + 34))
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        button.clicked.connect(lambda: self.run(fn))
        return button

    def make_card(self, title, detail):
        card = QLabel(f"<span style='color:#fbbf24;font-weight:700'>{title}</span><br>{str(detail).replace(chr(10), '<br>')}")
        card.setObjectName("smartMetric")
        card.setWordWrap(True)
        card.setMinimumWidth(152)
        return card

    def run(self, fn):
        self.accept()
        def invoke():
            try:
                fn()
            except Exception as exc:
                append_runtime_log(f"smart menu action failed: {type(exc).__name__}: {exc}")
                QMessageBox.warning(self.pet, "功能打开失败", f"这个功能刚才没有正常打开：\n{exc}")

        QTimer.singleShot(0, invoke)


class WordPopupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("考研英语词汇")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setStyleSheet(APP_DIALOG_STYLE)
        self.resize(340, 245)
        self.setMinimumSize(300, 210)
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)

        title = QLabel("考研英语词汇 · 单击换一批")
        title.setObjectName("hint")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.word_card = QPushButton()
        self.word_card.setObjectName("wordBatchButton")
        self.word_card.setMinimumHeight(168)
        self.word_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.word_card.clicked.connect(self.refresh_words)
        self.word_card.setStyleSheet(
            "QPushButton#wordBatchButton{"
            "background:rgba(15,23,42,220);color:#f8fafc;"
            "border:1px solid rgba(251,191,36,150);border-radius:10px;"
            "padding:12px 14px;text-align:left;font-weight:700;font-size:14px;}"
            "QPushButton#wordBatchButton:hover{border-color:#fbbf24;background:rgba(30,41,59,235);}"
        )
        layout.addWidget(self.word_card, 1)
        self.refresh_words()

    def refresh_words(self):
        words = exam_word_entries()
        if not words:
            self.word_card.setText("考研词汇库没有可用单词。")
            return
        count = min(random.randint(5, 10), len(words))
        picked = random.sample(words, count)
        lines = [f"{item['word']}  {item['meaning']}" for item in picked]
        self.word_card.setText("\n".join(lines))
        self.hide_timer.start(45_000)

    def showEvent(self, event):
        super().showEvent(event)
        self.hide_timer.start(45_000)


class HelpDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("使用说明")
        self.resize(560, 520)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(self)
        title = QLabel("使用说明")
        title.setObjectName("title")
        layout.addWidget(title)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setPlainText(
            "桌宠操作\n"
            "- 左键点击：弹出/更换考研词汇\n"
            "- 右键点击：打开快捷菜单\n"
            "- 双击：打开 AI 助手\n"
            "- 拖拽：移动桌宠\n"
            "- 摸头 / 戳身体 / 连续点击：触发不同动作反馈\n"
            "- 凌晨 1 点后：糯米会进入睡觉语气\n"
            "- 菜单“动作”可快速测试糯米各种动作\n"
            "- 菜单里的“变大一点 / 变小一点”：调整大小\n\n"
            "今日看板\n"
            "- 快捷菜单“今日”会汇总下一步行动、待办、日程、天气、邮件、电脑状态和考研信息\n\n"
            "快捷键\n"
            "- Alt + Space：打开 AI 助手\n"
            "- Ctrl + Shift + A：区域截图 OCR\n"
            "- Ctrl + Shift + H：收起到托盘 / 显示桌宠\n\n"
            "AI 助手\n"
            "- Enter 发送，Shift + Enter 换行\n"
            "- 可选普通问答、代码解释、408、高数、翻译\n\n"
            "- 对糯米说“记住……”，会保存到长期记忆\n"
            "- 说“我今天学完了线性表”，会记录到学习进度\n\n"
            "陪读模式\n"
            "- 点“开始学习”会进入陪读番茄钟\n"
            "- 学习结束后自动写入学习统计，并进入休息提醒\n\n"
            "邮件\n"
            "- 菜单“查看邮件”可看 QQ 邮箱未读邮件\n"
            "- 选中邮件后点“打开所选邮件”，会打开 QQ 邮箱并复制标题，方便搜索\n\n"
            "天气\n"
            "- 默认上海，可在设置或天气窗口里修改城市\n\n"
            "待办提醒\n"
            "- 菜单“提醒事项”可添加事项，并设置具体提醒时间\n"
            "- 到时间后桌宠会自动弹气泡提醒，完成事项后不再提醒\n\n"
            "翻译\n"
            "- 菜单“翻译”可打开独立翻译窗口，支持自动识别、中英日互译和润色\n\n"
            "剪贴板\n"
            "- 菜单“剪贴板”可查看最近复制过的文字\n"
            "- 疑似密钥、密码、长 token 会自动跳过\n\n"
            "- 可在设置的高级页关闭自动记录\n\n"
            "备份 / 迁移\n"
            "- 设置的高级页可导出或导入糯米数据备份\n"
            "- 默认不导出 AI Key 和邮箱授权码\n\n"
            "语音\n"
            "- “和糯米聊聊”里可以点“语音聊天”，说完后自动发送并朗读回复\n"
            "- 在设置里可以选择甜美女声、调整音量和语速"
        )
        text.append(
            "\n诊断 / 自恢复\n"
            "- 右键菜单“诊断”可以检查 AI、邮箱、OCR、VPN、Codex、开机启动和 watchdog\n"
            "- 设置 > 高级 可以开启或关闭自恢复守护、安静模式、全屏自动安静、全屏游戏/游戏窗口自动隐藏\n"
            "- “修复开机启动”会把启动项改成先启动 watchdog，再拉起糯米\n\n"
            "动作包\n"
            "- 设置 > 外观 可以选择动作包文件夹\n"
            "- 文件名示例：idle_0.png、walk_left_0.png、sleep_0.png、study_0.png\n\n"
            "自然语言提醒\n"
            "- 可以在 AI 窗口说：10分钟后提醒我喝水\n"
            "- 也可以说：明天下午3点提醒我背单词，糯米会自动写进提醒事项\n\n"
            "清理 / 性能中心\n"
            "- 右键菜单“清理”可以扫描临时文件、浏览器缓存、pip 缓存和糯米 Python 缓存\n"
            "- 清理前必须勾选并确认；大文件和资源占用只展示，不自动删除或结束进程\n"
            "- 可以快速打开 Windows 存储设置、启动项设置、系统磁盘清理和任务管理器\n\n"
            "电池 / 电源\n"
            "- 右键菜单“电池”显示电量、充电状态和预计剩余时间\n"
            "- 低电量会作为必要提醒；充到设定阈值后提示拔电，阈值可在设置 > 高级调整\n"
            "- 可生成 Windows 电池报告，报告只保存在本机 backups 文件夹\n\n"
            "桌面整理\n"
            "- 右键菜单“整理”会先扫描桌面文件并生成归类预览\n"
            "- 勾选后确认才会移动文件；只移动文件，不移动文件夹\n"
            "- 文件会进入桌面“桌面整理”下的图片、文档、压缩包、代码脚本等分类文件夹\n\n"
            "找文件\n"
            "- 右键菜单“文件”可以按文件名搜索常用位置、D盘项目、下载、桌面、文档、D盘或用户目录\n"
            "- 可以按文档、图片、视频、压缩包、代码、程序等类型筛选\n"
            "- 内容搜索只查小文本/代码文件，避免长时间占用硬盘\n"
        )
        layout.addWidget(text)
        close = QPushButton("知道了")
        close.setObjectName("sendButton")
        close.clicked.connect(self.close)
        layout.addWidget(close)


class AppearanceDebugDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.preview_target = parent if parent is not None and hasattr(parent, "apply_text_styles") else None
        self.saved = False
        self.original_style_config = {key: config.get(key, DEFAULT_CONFIG[key]) for key in STYLE_PREVIEW_KEYS}
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(lambda: self.apply_live_preview(show_bubble=True))
        self.setWindowTitle("外观调试器")
        self.resize(860, 620)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(12)
        title = QLabel("外观调试器")
        title.setObjectName("title")
        hint = QLabel("专门调字体、气泡颜色、边框和位置。改动会实时预览，保存后才固化。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        root.addWidget(title)
        root.addWidget(hint)

        body = QHBoxLayout()
        body.setSpacing(14)
        root.addLayout(body, 1)

        controls = QWidget()
        controls.setObjectName("settingsTabPage")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(10)
        form = QFormLayout()
        form.setSpacing(9)
        controls_layout.addLayout(form)

        self.text_font = QFontComboBox()
        self.text_font.setCurrentFont(QFont(text_font_family(config)))
        sizes = text_font_sizes(config)
        flags = bubble_text_flags(config)
        self.bubble_bold = QCheckBox("气泡粗体")
        self.bubble_bold.setChecked(flags["bold"])
        self.bubble_italic = QCheckBox("气泡斜体")
        self.bubble_italic.setChecked(flags["italic"])
        self.bubble_font_size = self.make_spin(10, 24, sizes["bubble"])
        self.desktop_label_font_size = self.make_spin(9, 20, sizes["desktop"])
        self.dialog_font_size = self.make_spin(11, 22, sizes["dialog"])
        self.menu_font_size = self.make_spin(10, 22, sizes["menu"])
        frame = bubble_frame(config)
        self.bubble_border_width = self.make_spin(1, 8, frame["width"])
        self.bubble_border_radius = self.make_spin(4, 32, frame["radius"])
        manual_width, manual_height = bubble_manual_size(config)
        self.bubble_width = self.make_spin(0, 680, manual_width)
        self.bubble_width.setSpecialValueText("自动")
        self.bubble_height = self.make_spin(0, 360, manual_height)
        self.bubble_height.setSpecialValueText("自动")
        offset_x, offset_y = bubble_offset(config)
        self.bubble_offset_x = self.make_spin(-420, 420, offset_x)
        self.bubble_offset_y = self.make_spin(-280, 260, offset_y)

        self.color_buttons = {}
        self.bubble_bg_color = self.make_color_button("BubbleBackgroundColor")
        self.bubble_text_color = self.make_color_button("BubbleTextColor")
        self.bubble_border_color = self.make_color_button("BubbleBorderColor")

        form.addRow(self.section_label("字体"))
        form.addRow("文本字体", self.text_font)
        form.addRow("气泡字号", self.bubble_font_size)
        form.addRow(self.bubble_bold)
        form.addRow(self.bubble_italic)
        form.addRow("桌面标签", self.desktop_label_font_size)
        form.addRow("弹窗字号", self.dialog_font_size)
        form.addRow("右键菜单", self.menu_font_size)
        form.addRow(self.section_label("气泡"))
        form.addRow("背景", self.bubble_bg_color)
        form.addRow("文字", self.bubble_text_color)
        form.addRow("边框颜色", self.bubble_border_color)
        form.addRow("边框粗细", self.bubble_border_width)
        form.addRow("圆角大小", self.bubble_border_radius)
        form.addRow("气泡宽度", self.bubble_width)
        form.addRow("气泡高度", self.bubble_height)
        form.addRow("横向位置", self.bubble_offset_x)
        form.addRow("垂直距离", self.bubble_offset_y)

        for text, handler in (
            ("恢复默认字体", self.reset_font_defaults),
            ("恢复默认气泡", self.reset_bubble_defaults),
            ("显示气泡预览", lambda: self.apply_live_preview(show_bubble=True)),
            ("重置气泡位置", self.reset_bubble_position),
        ):
            button = QPushButton(text)
            button.setObjectName("ghostButton")
            button.clicked.connect(handler)
            controls_layout.addWidget(button)
        controls_layout.addStretch(1)

        self.preview_panel = QWidget()
        self.preview_panel.setObjectName("fontPreviewPanel")
        self.preview_panel.setMinimumWidth(420)
        preview_layout = QVBoxLayout(self.preview_panel)
        preview_layout.setContentsMargins(18, 18, 18, 18)
        preview_layout.setSpacing(14)
        self.preview_info = QLabel()
        self.preview_info.setWordWrap(True)
        self.preview_bubble = QLabel("气泡预览：这里会显示背景、文字、边框粗细和圆角。")
        self.preview_bubble.setWordWrap(True)
        self.preview_bubble.setMinimumHeight(86)
        self.preview_status = QLabel("桌面标签预览：徐多多  待机")
        self.preview_status.setAlignment(Qt.AlignCenter)
        self.preview_status.setWordWrap(True)
        self.preview_status.setMinimumHeight(48)
        self.preview_dialog = QLabel("弹窗预览：设置、邮箱、AI 对话和输入框会跟随这个字号。")
        self.preview_dialog.setWordWrap(True)
        self.preview_dialog.setMinimumHeight(64)
        self.preview_menu = QPushButton("右键菜单预览")
        self.preview_menu.setObjectName("smartSecondary")
        position_hint = QLabel("气泡位置：用“横向位置 / 垂直距离”微调；拖动气泡会带着桌宠一起移动。")
        position_hint.setObjectName("hint")
        position_hint.setWordWrap(True)
        for widget in (self.preview_info, self.preview_bubble, self.preview_status, self.preview_dialog, self.preview_menu, position_hint):
            preview_layout.addWidget(widget)
        preview_layout.addStretch(1)

        controls_scroll = QScrollArea()
        controls_scroll.setWidgetResizable(True)
        controls_scroll.setFrameShape(QFrame.NoFrame)
        controls_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        controls_scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        controls_scroll.setMinimumWidth(310)
        controls_scroll.setMaximumWidth(340)
        controls_scroll.setWidget(controls)

        body.addWidget(controls_scroll)
        body.addWidget(self.preview_panel, 1)

        actions = QHBoxLayout()
        actions.addStretch(1)
        cancel = QPushButton("取消")
        cancel.setObjectName("ghostButton")
        cancel.clicked.connect(self.reject)
        save = QPushButton("保存调试设置")
        save.setObjectName("sendButton")
        save.clicked.connect(self.save)
        actions.addWidget(cancel)
        actions.addWidget(save)
        root.addLayout(actions)

        self.connect_preview_controls()
        self.apply_live_preview(show_bubble=False)

    def make_spin(self, low, high, value):
        spin = QSpinBox()
        spin.setRange(low, high)
        spin.setSuffix(" px")
        spin.setValue(value)
        return spin

    def section_label(self, text):
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def make_color_button(self, key):
        button = QPushButton()
        self.color_buttons[key] = button
        self.set_color_button(key, self.config.get(key, DEFAULT_CONFIG[key]))
        button.clicked.connect(lambda _checked=False, color_key=key: self.pick_color(color_key))
        return button

    def color_value(self, key):
        return str(self.color_buttons[key].property("color") or DEFAULT_CONFIG[key])

    def set_color_button(self, key, value):
        color = normalize_color(value, DEFAULT_CONFIG[key])
        button = self.color_buttons[key]
        button.setProperty("color", color)
        button.setText(color)
        button.setStyleSheet(
            f"QPushButton{{background:{color};color:{readable_text_color(color)};"
            "border:1px solid rgba(148,163,184,150);border-radius:10px;"
            "padding:8px 14px;text-align:left;font-weight:700;}}"
        )

    def pick_color(self, key):
        color = QColorDialog.getColor(QColor(self.color_value(key)), self, "选择气泡颜色")
        if color.isValid():
            self.set_color_button(key, color.name())
            self.schedule_preview()

    def connect_preview_controls(self):
        self.text_font.currentFontChanged.connect(self.schedule_preview)
        self.bubble_bold.stateChanged.connect(self.schedule_preview)
        self.bubble_italic.stateChanged.connect(self.schedule_preview)
        for widget in (
            self.bubble_font_size,
            self.desktop_label_font_size,
            self.dialog_font_size,
            self.menu_font_size,
            self.bubble_border_width,
            self.bubble_border_radius,
            self.bubble_width,
            self.bubble_height,
            self.bubble_offset_x,
            self.bubble_offset_y,
        ):
            widget.valueChanged.connect(self.schedule_preview)

    def draft_config(self):
        draft = dict(self.config)
        draft.update(
            {
                "TextFontFamily": self.text_font.currentFont().family(),
                "BubbleFontSize": self.bubble_font_size.value(),
                "BubbleFontBold": self.bubble_bold.isChecked(),
                "BubbleFontItalic": self.bubble_italic.isChecked(),
                "DesktopLabelFontSize": self.desktop_label_font_size.value(),
                "DialogFontSize": self.dialog_font_size.value(),
                "MenuFontSize": self.menu_font_size.value(),
                "BubbleBackgroundColor": self.color_value("BubbleBackgroundColor"),
                "BubbleTextColor": self.color_value("BubbleTextColor"),
                "BubbleBorderColor": self.color_value("BubbleBorderColor"),
                "BubbleBorderWidth": self.bubble_border_width.value(),
                "BubbleBorderRadius": self.bubble_border_radius.value(),
                "BubbleWidth": self.bubble_width.value(),
                "BubbleHeight": self.bubble_height.value(),
                "BubbleOffsetX": self.bubble_offset_x.value(),
                "BubbleOffsetY": self.bubble_offset_y.value(),
            }
        )
        return draft

    def schedule_preview(self, *_args):
        self.apply_live_preview(show_bubble=False)
        self.preview_timer.start(180)

    def apply_live_preview(self, show_bubble=False):
        draft = self.draft_config()
        sizes = text_font_sizes(draft)
        flags = bubble_text_flags(draft)
        frame = bubble_frame(draft)
        manual_width, manual_height = bubble_manual_size(draft)
        size_label = (
            f"{manual_width or '自动'} x {manual_height or '自动'}"
            if manual_width or manual_height else "自动"
        )
        self.preview_info.setText(
            f"{text_font_family(draft)} | 气泡 {sizes['bubble']}px | 桌面 {sizes['desktop']}px | "
            f"弹窗 {sizes['dialog']}px | 菜单 {sizes['menu']}px | 边框 {frame['width']}px | 圆角 {frame['radius']}px | 大小 {size_label}"
            f" | 位置 X {draft.get('BubbleOffsetX', 0)} / Y {draft.get('BubbleOffsetY', 0)}"
            f" | {'粗体' if flags['bold'] else '常规'} / {'斜体' if flags['italic'] else '正体'}"
        )
        self.preview_panel.setStyleSheet(
            "QWidget#fontPreviewPanel{"
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0b2a4a,stop:1 #123f70);"
            "border:2px solid rgba(56,189,248,190);"
            "border-radius:16px;}"
        )
        self.preview_bubble.setStyleSheet(bubble_style(draft))
        self.preview_bubble.setMinimumSize(manual_width or 0, manual_height or 86)
        self.preview_bubble.setMaximumSize(manual_width or 16777215, manual_height or 16777215)
        self.preview_status.setStyleSheet(desktop_label_style(draft))
        family = qss_font_family(draft)
        self.preview_dialog.setStyleSheet(
            "QLabel{background:rgba(21,27,38,185);color:#e5e7eb;"
            "border:1px solid rgba(148,163,184,80);border-radius:12px;"
            f"padding:10px;font:{sizes['dialog']}px \"{family}\";}}"
        )
        self.preview_menu.setStyleSheet(smart_menu_style(draft))
        self.setStyleSheet(app_dialog_style(draft))
        if self.preview_target is not None:
            self.preview_target.config.update(draft)
            self.preview_target.apply_text_styles(draft)
            if self.preview_target.bubble.isVisible():
                self.preview_target.position_bubble()
            if show_bubble:
                self.preview_target.bubble.say("气泡预览：拖动我会带着桌宠一起移动；位置用左侧数值微调。", 4200)

    def reset_font_defaults(self):
        self.text_font.setCurrentFont(QFont(DEFAULT_CONFIG["TextFontFamily"]))
        self.bubble_font_size.setValue(DEFAULT_CONFIG["BubbleFontSize"])
        self.bubble_bold.setChecked(DEFAULT_CONFIG["BubbleFontBold"])
        self.bubble_italic.setChecked(DEFAULT_CONFIG["BubbleFontItalic"])
        self.desktop_label_font_size.setValue(DEFAULT_CONFIG["DesktopLabelFontSize"])
        self.dialog_font_size.setValue(DEFAULT_CONFIG["DialogFontSize"])
        self.menu_font_size.setValue(DEFAULT_CONFIG["MenuFontSize"])

    def reset_bubble_defaults(self):
        for key in BUBBLE_COLOR_KEYS:
            self.set_color_button(key, DEFAULT_CONFIG[key])
        self.bubble_border_width.setValue(DEFAULT_CONFIG["BubbleBorderWidth"])
        self.bubble_border_radius.setValue(DEFAULT_CONFIG["BubbleBorderRadius"])
        self.bubble_width.setValue(DEFAULT_CONFIG["BubbleWidth"])
        self.bubble_height.setValue(DEFAULT_CONFIG["BubbleHeight"])
        self.bubble_offset_x.setValue(DEFAULT_CONFIG["BubbleOffsetX"])
        self.bubble_offset_y.setValue(DEFAULT_CONFIG["BubbleOffsetY"])
        self.schedule_preview()

    def reset_bubble_position(self):
        if self.preview_target is None:
            return
        update_saved_bubble_offset(self.preview_target.config, DEFAULT_CONFIG["BubbleOffsetX"], DEFAULT_CONFIG["BubbleOffsetY"])
        self.bubble_offset_x.setValue(DEFAULT_CONFIG["BubbleOffsetX"])
        self.bubble_offset_y.setValue(DEFAULT_CONFIG["BubbleOffsetY"])
        if self.preview_target.bubble.isVisible():
            self.preview_target.position_bubble()
        self.preview_target.bubble.say("气泡位置已重置。可用横向/垂直数值微调。", 3600)

    def restore_preview(self):
        self.preview_timer.stop()
        if self.saved:
            return
        restored = dict(self.config)
        restored.update(self.original_style_config)
        set_active_text_config(restored)
        if self.preview_target is not None:
            self.preview_target.config.update(restored)
            self.preview_target.apply_text_styles(restored)

    def reject(self):
        self.restore_preview()
        super().reject()

    def save(self):
        self.config.update(self.draft_config())
        save_json(CONFIG, self.config)
        set_active_text_config(self.config)
        if self.preview_target is not None:
            self.preview_target.config.update(self.config)
            self.preview_target.apply_text_styles(self.config)
        self.saved = True
        self.preview_timer.stop()
        self.accept()


class SettingsDialog(QDialog):
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self._font_saved = False
        self.preview_target = parent if parent is not None and hasattr(parent, "apply_text_styles") else None
        self.original_font_config = {
            key: config.get(key, DEFAULT_CONFIG[key])
            for key in STYLE_PREVIEW_KEYS
        }
        self.font_preview_timer = QTimer(self)
        self.font_preview_timer.setSingleShot(True)
        self.font_preview_timer.timeout.connect(lambda: self.apply_live_font_preview(show_bubble=True))
        pet_name = config.get("PetName", "糯米")
        self.setWindowTitle(f"{pet_name}的设置")
        self.resize(640, 660)
        self.setMinimumSize(560, 500)
        self.setSizeGripEnabled(True)
        self.setStyleSheet(APP_DIALOG_STYLE)
        main = QVBoxLayout(self)
        main.setContentsMargins(18, 18, 18, 18)
        main.setSpacing(12)
        title = QLabel(f"{pet_name}的设置")
        title.setObjectName("title")
        hint = QLabel("平时只需要调外观和日常偏好；账号、接口、OCR 都收在后面的连接配置里。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        main.addWidget(title)
        main.addWidget(hint)

        self.name = QLineEdit(config.get("PetName", "糯米"))
        self.pet_path = QLineEdit(config.get("PetImagePath", ""))
        pick = QPushButton("选择角色图")
        pick.setObjectName("ghostButton")
        pick.clicked.connect(self.pick_pet)
        pet_row = QHBoxLayout()
        pet_row.addWidget(self.pet_path)
        pet_row.addWidget(pick)
        self.action_pack = QLineEdit(config.get("ActionPackPath", ""))
        pick_action_pack = QPushButton("选择动作包")
        pick_action_pack.setObjectName("ghostButton")
        pick_action_pack.clicked.connect(self.pick_action_pack)
        action_pack_row = QHBoxLayout()
        action_pack_row.addWidget(self.action_pack)
        action_pack_row.addWidget(pick_action_pack)
        self.size = QSpinBox()
        self.size.setRange(120, 360)
        self.size.setValue(int(config.get("PetSize", 230)))
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(45, 100)
        self.opacity.setValue(int(float(config.get("Opacity", 1)) * 100))
        self.show_status = QCheckBox("显示桌面状态小标签")
        self.show_status.setChecked(bool(config.get("ShowStatus", False)))
        self.ai_endpoint = QLineEdit(config.get("AiEndpoint", ""))
        self.ai_model = QLineEdit(config.get("AiModel", ""))
        self.ai_key = QLineEdit(config.get("AiApiKey", ""))
        self.ai_key.setEchoMode(QLineEdit.Password)
        self.tesseract = QLineEdit(config.get("TesseractPath", ""))
        detect_tesseract_btn = QPushButton("自动检测")
        detect_tesseract_btn.setObjectName("ghostButton")
        detect_tesseract_btn.clicked.connect(self.detect_tesseract)
        pick_tesseract_btn = QPushButton("选择文件")
        pick_tesseract_btn.setObjectName("ghostButton")
        pick_tesseract_btn.clicked.connect(self.pick_tesseract)
        tesseract_row = QHBoxLayout()
        tesseract_row.addWidget(self.tesseract)
        tesseract_row.addWidget(detect_tesseract_btn)
        tesseract_row.addWidget(pick_tesseract_btn)
        self.exam = QLineEdit(config.get("ExamDate", "2026-12-26"))
        self.mail_host = QLineEdit(config.get("MailHost", ""))
        self.mail_port = QSpinBox()
        self.mail_port.setRange(1, 65535)
        self.mail_port.setValue(int(config.get("MailPort", 993)))
        self.mail_user = QLineEdit(config.get("MailUser", ""))
        self.mail_pwd = QLineEdit(config.get("MailPassword", ""))
        self.mail_pwd.setEchoMode(QLineEdit.Password)
        self.gmail_user = QLineEdit(config.get("GmailUser", ""))
        self.gmail_pwd = QLineEdit(config.get("GmailPassword", ""))
        self.gmail_pwd.setEchoMode(QLineEdit.Password)
        self.mail_keywords = QLineEdit(config.get("MailKeywords", ""))
        self.voice_enabled = QCheckBox("开启语音播报")
        self.voice_enabled.setChecked(bool(config.get("VoiceEnabled", False)))
        self.voice_engine = QComboBox()
        self.voice_engine.addItem("晓晓 在线神经女声（推荐）", "edge")
        self.voice_engine.addItem("瑶瑶 离线自然女声（断网备用）", "onecore")
        self.voice_engine.addItem("Windows 传统语音（最后备用）", "windows")
        engine_index = self.voice_engine.findData(
            str(config.get("VoiceEngine", DEFAULT_CONFIG["VoiceEngine"])).lower()
        )
        self.voice_engine.setCurrentIndex(max(0, engine_index))
        self.onecore_voice = QComboBox()
        for label, voice_id in ONECORE_TTS_VOICES:
            self.onecore_voice.addItem(label, voice_id)
        current_onecore_voice = onecore_voice_name(config)
        onecore_voice_index = self.onecore_voice.findData(current_onecore_voice)
        if onecore_voice_index < 0:
            self.onecore_voice.addItem(current_onecore_voice, current_onecore_voice)
            onecore_voice_index = self.onecore_voice.findData(current_onecore_voice)
        self.onecore_voice.setCurrentIndex(max(0, onecore_voice_index))
        self.onecore_pitch = QSpinBox()
        self.onecore_pitch.setRange(-20, 20)
        self.onecore_pitch.setSuffix("%")
        self.onecore_pitch.setValue(int(config.get("OneCorePitchPercent", DEFAULT_CONFIG["OneCorePitchPercent"])))
        self.edge_voice = QComboBox()
        for label, voice_id in EDGE_TTS_VOICES:
            self.edge_voice.addItem(label, voice_id)
        current_edge_voice = edge_voice_name(config)
        edge_voice_index = self.edge_voice.findData(current_edge_voice)
        if edge_voice_index < 0:
            self.edge_voice.addItem(current_edge_voice, current_edge_voice)
            edge_voice_index = self.edge_voice.findData(current_edge_voice)
        self.edge_voice.setCurrentIndex(max(0, edge_voice_index))
        self.edge_pitch = QSpinBox()
        self.edge_pitch.setRange(-50, 50)
        self.edge_pitch.setSuffix(" Hz")
        self.edge_pitch.setValue(int(config.get("EdgePitchHz", DEFAULT_CONFIG["EdgePitchHz"])))
        self.voice_volume = QSlider(Qt.Horizontal)
        self.voice_volume.setRange(0, 100)
        self.voice_volume.setValue(int(config.get("VoiceVolume", 70)))
        self.chat_voice_replies = QCheckBox("AI 聊天回复自动朗读")
        self.chat_voice_replies.setChecked(bool(config.get("ChatVoiceReplies", True)))
        self.voice_name = QComboBox()
        current_voice = str(config.get("VoiceName", "")).strip()
        self.voice_name.addItem("自动选择中文女声", "")
        if current_voice:
            self.voice_name.addItem(current_voice, current_voice)
            self.voice_name.setCurrentIndex(1)
        self.voice_options_loaded = False
        self.load_voice_btn = QPushButton("加载 Windows 离线声音")
        self.load_voice_btn.setObjectName("ghostButton")
        self.load_voice_btn.clicked.connect(self.load_voice_options)
        self.voice_list_worker = None
        self.voice_rate = QSpinBox()
        self.voice_rate.setRange(-5, 5)
        self.voice_rate.setValue(int(config.get("VoiceRate", -1)))
        self.ambient_voice_cooldown = QSpinBox()
        self.ambient_voice_cooldown.setRange(0, 120)
        self.ambient_voice_cooldown.setSuffix(" 分钟")
        self.ambient_voice_cooldown.setSpecialValueText("不限制")
        self.ambient_voice_cooldown.setValue(
            int(config.get("AmbientVoiceCooldownMinutes", DEFAULT_CONFIG["AmbientVoiceCooldownMinutes"]))
        )
        self.fullscreen_reminder_only = QCheckBox("全屏视频或游戏时仅允许到期提醒发声")
        self.fullscreen_reminder_only.setChecked(
            bool(config.get("FullscreenReminderOnly", DEFAULT_CONFIG["FullscreenReminderOnly"]))
        )
        self.voice_preview = QPushButton("试听声音")
        self.voice_preview.setObjectName("ghostButton")
        self.voice_preview.clicked.connect(self.test_voice)
        self.preview_tts_worker = None
        self.clipboard_enabled = QCheckBox("记录文字剪贴板历史")
        self.clipboard_enabled.setChecked(bool(config.get("ClipboardHistoryEnabled", True)))
        self.quiet_mode = QCheckBox("安静模式：只保留必要提醒")
        self.quiet_mode.setChecked(bool(config.get("QuietMode", False)))
        self.auto_quiet_fullscreen = QCheckBox("检测到全屏应用时自动安静")
        self.auto_quiet_fullscreen.setChecked(bool(config.get("AutoQuietFullscreen", True)))
        self.auto_hide_fullscreen = QCheckBox("全屏游戏时自动隐藏桌宠")
        self.auto_hide_fullscreen.setChecked(bool(config.get("AutoHideFullscreen", True)))
        self.auto_hide_games = QCheckBox("游戏窗口在前台时自动隐藏桌宠")
        self.auto_hide_games.setChecked(bool(config.get("AutoHideGames", True)))
        self.auto_start = QCheckBox("开机自动启动糯米")
        self.auto_start.setChecked(bool(config.get("AutoStart", True)))
        self.watchdog_enabled = QCheckBox("自恢复守护：异常退出后自动拉起糯米")
        self.watchdog_enabled.setChecked(bool(config.get("WatchdogEnabled", True)))
        self.health_watch_enabled = QCheckBox("自动检测电脑异常并提醒")
        self.health_watch_enabled.setChecked(bool(config.get("SystemHealthWatchEnabled", True)))
        self.cpu_alert = QSpinBox()
        self.cpu_alert.setRange(50, 100)
        self.cpu_alert.setSuffix("%")
        self.cpu_alert.setValue(int(config.get("CpuAlertPercent", 90)))
        self.memory_alert = QSpinBox()
        self.memory_alert.setRange(50, 100)
        self.memory_alert.setSuffix("%")
        self.memory_alert.setValue(int(config.get("MemoryAlertPercent", 90)))
        self.disk_alert = QSpinBox()
        self.disk_alert.setRange(70, 100)
        self.disk_alert.setSuffix("%")
        self.disk_alert.setValue(int(config.get("DiskAlertPercent", 90)))
        self.battery_alerts_enabled = QCheckBox("启用笔记本低电量和充满提示")
        self.battery_alerts_enabled.setChecked(bool(config.get("BatteryAlertsEnabled", True)))
        self.battery_low = QSpinBox()
        self.battery_low.setRange(5, 40)
        self.battery_low.setSuffix("%")
        self.battery_low.setValue(int(config.get("BatteryLowPercent", 20)))
        self.battery_full = QSpinBox()
        self.battery_full.setRange(80, 100)
        self.battery_full.setSuffix("%")
        self.battery_full.setValue(int(config.get("BatteryFullPercent", 95)))
        self.health_cooldown = QSpinBox()
        self.health_cooldown.setRange(3, 120)
        self.health_cooldown.setSuffix(" 分钟")
        self.health_cooldown.setValue(int(config.get("HealthAlertCooldownMinutes", 15)))
        self.weather_city = QLineEdit(config.get("WeatherCity", "上海"))
        qq_btn = QPushButton("启用 QQ 邮箱")
        qq_btn.setObjectName("ghostButton")
        qq_btn.clicked.connect(self.use_qq_mail)
        gmail_btn = QPushButton("启用 Google 邮箱")
        gmail_btn.setObjectName("ghostButton")
        gmail_btn.clicked.connect(self.use_gmail_mail)
        qq_save_btn = QPushButton("保存 QQ 邮箱设置")
        qq_save_btn.setObjectName("sendButton")
        qq_save_btn.clicked.connect(self.save)
        gmail_save_btn = QPushButton("保存 Google 邮箱设置")
        gmail_save_btn.setObjectName("sendButton")
        gmail_save_btn.clicked.connect(self.save)
        backup_btn = QPushButton("备份 / 迁移糯米数据")
        backup_btn.setObjectName("ghostButton")
        backup_btn.clicked.connect(self.open_backup)
        self.backup_btn = backup_btn
        feature_switch_btn = QPushButton("功能开关")
        feature_switch_btn.setObjectName("sendButton")
        feature_switch_btn.clicked.connect(self.open_feature_switch)
        diagnostics_btn = QPushButton("诊断中心 / 修复启动")
        diagnostics_btn.setObjectName("ghostButton")
        diagnostics_btn.clicked.connect(self.open_diagnostics)
        self.diagnostics_btn = diagnostics_btn
        backup_btn.setVisible(feature_enabled(config, "BackupFeatureEnabled"))
        diagnostics_btn.setVisible(feature_enabled(config, "DiagnosticsFeatureEnabled"))

        tabs = QTabWidget()
        tabs.setObjectName("settingsTabs")
        tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        appearance = QWidget()
        appearance_form = QFormLayout(appearance)
        appearance_form.setSpacing(10)
        appearance_form.addRow(self.make_section_label("角色外观"))
        appearance_form.addRow("名字", self.name)
        appearance_form.addRow("角色图片", pet_row)
        appearance_form.addRow("动作包文件夹", action_pack_row)
        appearance_form.addRow("大小", self.size)
        appearance_form.addRow("透明度", self.opacity)
        appearance_form.addRow(self.show_status)
        appearance_form.addRow("默认天气城市", self.weather_city)
        appearance_form.addRow(self.make_section_label("外观调试"))
        self.appearance_debug_summary = QLabel()
        self.appearance_debug_summary.setObjectName("panel")
        self.appearance_debug_summary.setWordWrap(True)
        self.refresh_appearance_debug_summary()
        open_appearance_debug_btn = QPushButton("打开外观调试器")
        open_appearance_debug_btn.setObjectName("sendButton")
        open_appearance_debug_btn.clicked.connect(self.open_appearance_debug)
        appearance_form.addRow(self.appearance_debug_summary)
        appearance_form.addRow(open_appearance_debug_btn)
        tabs.addTab(self.make_settings_tab(appearance), "外观")

        ai_tab = QWidget()
        ai_form = QFormLayout(ai_tab)
        ai_form.setSpacing(10)
        ai_form.addRow("API 地址", self.ai_endpoint)
        ai_form.addRow("模型", self.ai_model)
        ai_form.addRow("API Key", self.ai_key)
        tabs.addTab(self.make_settings_tab(ai_tab), "AI")

        mail_tab = QWidget()
        mail_layout = QVBoxLayout(mail_tab)
        mail_layout.setContentsMargins(0, 0, 0, 0)
        mail_layout.setSpacing(10)
        mail_accounts_tabs = QTabWidget()
        mail_accounts_tabs.setObjectName("settingsTabs")

        qq_mail_tab = QWidget()
        qq_form = QFormLayout(qq_mail_tab)
        qq_form.setSpacing(10)
        qq_form.addRow("IMAP 主机", self.mail_host)
        qq_form.addRow("IMAP 端口", self.mail_port)
        qq_form.addRow("QQ 邮箱账号", self.mail_user)
        qq_form.addRow("QQ 邮箱授权码", self.mail_pwd)
        qq_form.addRow(qq_btn)
        qq_form.addRow(qq_save_btn)

        gmail_mail_tab = QWidget()
        gmail_form = QFormLayout(gmail_mail_tab)
        gmail_form.setSpacing(10)
        gmail_form.addRow("Google 邮箱账号", self.gmail_user)
        gmail_form.addRow("Google 应用专用密码", self.gmail_pwd)
        gmail_form.addRow(gmail_btn)
        gmail_form.addRow(gmail_save_btn)

        mail_accounts_tabs.addTab(qq_mail_tab, "QQ邮箱")
        mail_accounts_tabs.addTab(gmail_mail_tab, "Google邮箱")
        mail_layout.addWidget(mail_accounts_tabs)
        mail_keywords_form = QFormLayout()
        mail_keywords_form.setSpacing(10)
        mail_keywords_form.addRow("提醒关键词", self.mail_keywords)
        mail_layout.addLayout(mail_keywords_form)
        tabs.addTab(self.make_settings_tab(mail_tab), "邮件")

        ocr_tab = QWidget()
        ocr_form = QFormLayout(ocr_tab)
        ocr_form.setSpacing(10)
        ocr_form.addRow("Tesseract 路径", tesseract_row)
        tabs.addTab(self.make_settings_tab(ocr_tab), "OCR")

        advanced = QWidget()
        advanced_form = QFormLayout(advanced)
        advanced_form.setSpacing(10)
        advanced_form.addRow("考研日期", self.exam)
        advanced_form.addRow(self.voice_enabled)
        advanced_form.addRow(self.chat_voice_replies)
        advanced_form.addRow("语音引擎", self.voice_engine)
        advanced_form.addRow("断网备用声音", self.onecore_voice)
        advanced_form.addRow("温柔音调", self.onecore_pitch)
        advanced_form.addRow("在线女生", self.edge_voice)
        advanced_form.addRow("神经声音音调", self.edge_pitch)
        advanced_form.addRow("离线备用声音", self.voice_name)
        advanced_form.addRow(self.load_voice_btn)
        advanced_form.addRow("语音音量", self.voice_volume)
        advanced_form.addRow("语速", self.voice_rate)
        advanced_form.addRow("自动闲聊语音间隔", self.ambient_voice_cooldown)
        advanced_form.addRow(self.fullscreen_reminder_only)
        advanced_form.addRow(self.voice_preview)
        advanced_form.addRow(self.clipboard_enabled)
        advanced_form.addRow(self.quiet_mode)
        advanced_form.addRow(self.auto_quiet_fullscreen)
        advanced_form.addRow(self.auto_hide_fullscreen)
        advanced_form.addRow(self.auto_hide_games)
        advanced_form.addRow(self.auto_start)
        advanced_form.addRow(self.watchdog_enabled)
        advanced_form.addRow(self.health_watch_enabled)
        advanced_form.addRow("CPU 提醒阈值", self.cpu_alert)
        advanced_form.addRow("内存提醒阈值", self.memory_alert)
        advanced_form.addRow("磁盘提醒阈值", self.disk_alert)
        advanced_form.addRow(self.battery_alerts_enabled)
        advanced_form.addRow("低电量提醒阈值", self.battery_low)
        advanced_form.addRow("充满提示阈值", self.battery_full)
        advanced_form.addRow("同类提醒冷却", self.health_cooldown)
        advanced_form.addRow(feature_switch_btn)
        advanced_form.addRow(diagnostics_btn)
        advanced_form.addRow(backup_btn)
        advanced_form.addRow(QLabel("VPN、Codex、自启动等由桌宠自动检测和维护。"))
        tabs.addTab(self.make_settings_tab(advanced), "高级")

        main.addWidget(tabs, 1)
        save = QPushButton("保存")
        save.setObjectName("sendButton")
        save.clicked.connect(self.save)
        main.addWidget(save)
        self.refresh_appearance_debug_summary()

    def make_section_label(self, text):
        label = QLabel(text)
        label.setObjectName("sectionTitle")
        return label

    def make_settings_tab(self, widget):
        widget.setObjectName("settingsTabPage")
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setSizeAdjustPolicy(QAbstractScrollArea.AdjustIgnored)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        scroll.setMinimumSize(0, 0)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        scroll.setWidget(widget)
        return scroll

    def appearance_debug_summary_text(self):
        sizes = text_font_sizes(self.config)
        flags = bubble_text_flags(self.config)
        colors = bubble_colors(self.config)
        frame = bubble_frame(self.config)
        manual_width, manual_height = bubble_manual_size(self.config)
        bubble_size = (
            f"{manual_width or '自动'} x {manual_height or '自动'}"
            if manual_width or manual_height else "自动"
        )
        return (
            f"当前：{text_font_family(self.config)}；气泡 {sizes['bubble']}px，桌面标签 {sizes['desktop']}px，"
            f"弹窗 {sizes['dialog']}px，右键菜单 {sizes['menu']}px。\n"
            f"气泡文字：{'粗体' if flags['bold'] else '常规'}，{'斜体' if flags['italic'] else '正体'}。\n"
            f"气泡背景 {colors['background']}，文字 {colors['text']}，边框 {colors['border']}，"
            f"边框 {frame['width']}px，圆角 {frame['radius']}px，大小 {bubble_size}。\n"
            "打开调试器后可以用横向/垂直数值微调气泡；拖动气泡会带着桌宠一起移动。"
        )

    def refresh_appearance_debug_summary(self):
        if hasattr(self, "appearance_debug_summary"):
            self.appearance_debug_summary.setText(self.appearance_debug_summary_text())

    def open_appearance_debug(self):
        target = self.parent() if self.parent() is not None and hasattr(self.parent(), "apply_text_styles") else self.preview_target
        dialog = AppearanceDebugDialog(self.config, target)
        if dialog.exec():
            self.config.update(dialog.config)
            self.original_font_config = {
                key: self.config.get(key, DEFAULT_CONFIG[key])
                for key in STYLE_PREVIEW_KEYS
            }
            self.refresh_appearance_debug_summary()

    def make_color_button(self, key):
        button = QPushButton()
        button.setObjectName("ghostButton")
        self.color_buttons[key] = button
        self.set_color_button(key, self.config.get(key, DEFAULT_CONFIG[key]))
        button.clicked.connect(lambda _checked=False, color_key=key: self.pick_color(color_key))
        return button

    def color_value(self, key):
        button = self.color_buttons[key]
        return str(button.property("color") or DEFAULT_CONFIG[key])

    def set_color_button(self, key, value):
        color = normalize_color(value, DEFAULT_CONFIG[key])
        button = self.color_buttons[key]
        button.setProperty("color", color)
        button.setText(color)
        button.setStyleSheet(
            f"QPushButton{{background:{color};color:{readable_text_color(color)};"
            "border:1px solid rgba(148,163,184,140);border-radius:10px;"
            "padding:8px 14px;text-align:left;font-weight:700;}}"
        )

    def pick_color(self, key):
        current = QColor(self.color_value(key))
        color = QColorDialog.getColor(current, self, "选择气泡颜色")
        if color.isValid():
            self.set_color_button(key, color.name())
            self.schedule_font_preview()

    def connect_font_preview_controls(self):
        self.text_font.currentFontChanged.connect(self.schedule_font_preview)
        for widget in (
            self.bubble_font_size,
            self.desktop_label_font_size,
            self.dialog_font_size,
            self.menu_font_size,
            self.bubble_border_width,
            self.bubble_border_radius,
        ):
            widget.valueChanged.connect(self.schedule_font_preview)

    def draft_font_config(self):
        draft = dict(self.config)
        draft.update(
            {
                "TextFontFamily": self.text_font.currentFont().family(),
                "BubbleFontSize": self.bubble_font_size.value(),
                "DesktopLabelFontSize": self.desktop_label_font_size.value(),
                "DialogFontSize": self.dialog_font_size.value(),
                "MenuFontSize": self.menu_font_size.value(),
                "BubbleBackgroundColor": self.color_value("BubbleBackgroundColor"),
                "BubbleTextColor": self.color_value("BubbleTextColor"),
                "BubbleBorderColor": self.color_value("BubbleBorderColor"),
                "BubbleBorderWidth": self.bubble_border_width.value(),
                "BubbleBorderRadius": self.bubble_border_radius.value(),
            }
        )
        return draft

    def schedule_font_preview(self, *_args):
        self.apply_live_font_preview(show_bubble=False)
        self.font_preview_timer.start(180)

    def apply_live_font_preview(self, show_bubble=False):
        draft = self.draft_font_config()
        sizes = text_font_sizes(draft)
        family = text_font_family(draft)
        colors = bubble_colors(draft)
        frame = bubble_frame(draft)
        self.font_preview_info.setText(
            f"当前：{family} | 气泡 {sizes['bubble']}px / 桌面标签 {sizes['desktop']}px / "
            f"弹窗 {sizes['dialog']}px / 右键菜单 {sizes['menu']}px | "
            f"气泡色 {colors['background']} / 字 {colors['text']} / 边框 {frame['width']}px / 圆角 {frame['radius']}px"
        )
        self.font_preview_panel.setStyleSheet(
            "QWidget#fontPreviewPanel{"
            "background:qlineargradient(x1:0,y1:0,x2:1,y2:1,stop:0 #0b2a4a,stop:1 #123f70);"
            "border:2px solid rgba(56,189,248,190);"
            "border-radius:16px;"
            "}"
        )
        self.font_preview_bubble.setStyleSheet(bubble_style(draft))
        self.font_preview_status.setStyleSheet(desktop_label_style(draft))
        dialog_family = qss_font_family(draft)
        self.font_preview_dialog.setStyleSheet(
            "QLabel{background:rgba(21,27,38,185);color:#e5e7eb;"
            "border:1px solid rgba(148,163,184,80);border-radius:12px;"
            f"padding:10px;font:{sizes['dialog']}px \"{dialog_family}\";}}"
        )
        self.font_preview_menu.setStyleSheet(smart_menu_style(draft))
        self.setStyleSheet(app_dialog_style(draft))
        if self.preview_target is not None:
            self.preview_target.apply_text_styles(draft)
            if show_bubble:
                self.preview_target.bubble.say("气泡预览：拖动我会带着桌宠一起移动。", 4200)

    def reset_font_defaults(self):
        self.text_font.setCurrentFont(QFont(DEFAULT_CONFIG["TextFontFamily"]))
        self.bubble_font_size.setValue(DEFAULT_CONFIG["BubbleFontSize"])
        self.desktop_label_font_size.setValue(DEFAULT_CONFIG["DesktopLabelFontSize"])
        self.dialog_font_size.setValue(DEFAULT_CONFIG["DialogFontSize"])
        self.menu_font_size.setValue(DEFAULT_CONFIG["MenuFontSize"])

    def reset_bubble_colors(self):
        for key in BUBBLE_COLOR_KEYS:
            self.set_color_button(key, DEFAULT_CONFIG[key])
        self.bubble_border_width.setValue(DEFAULT_CONFIG["BubbleBorderWidth"])
        self.bubble_border_radius.setValue(DEFAULT_CONFIG["BubbleBorderRadius"])
        self.schedule_font_preview()

    def reset_bubble_position(self):
        if self.preview_target is not None:
            update_saved_bubble_offset(
                self.preview_target.config,
                DEFAULT_CONFIG["BubbleOffsetX"],
                DEFAULT_CONFIG["BubbleOffsetY"],
            )
            if self.preview_target.bubble.isVisible():
                self.preview_target.position_bubble()
            self.preview_target.bubble.say("气泡位置已重置。可在外观调试器里用数值微调。", 4200)

    def restore_font_preview(self):
        self.font_preview_timer.stop()
        if self._font_saved:
            return
        restored = dict(self.config)
        restored.update(self.original_font_config)
        set_active_text_config(restored)
        if self.preview_target is not None:
            self.preview_target.apply_text_styles(restored)

    def reject(self):
        self.restore_font_preview()
        super().reject()

    def closeEvent(self, event):
        for worker in (getattr(self, "voice_list_worker", None), getattr(self, "preview_tts_worker", None)):
            detach_running_worker(worker, ("result", "finished") if isinstance(worker, TtsVoiceListWorker) else ("finished",))
        self.voice_list_worker = None
        self.preview_tts_worker = None
        super().closeEvent(event)

    def load_voice_options(self):
        if self.voice_list_worker and self.voice_list_worker.isRunning():
            return
        current_voice = self.selected_voice_name()
        self.load_voice_btn.setEnabled(False)
        self.load_voice_btn.setText("正在加载声音...")
        self.voice_list_worker = TtsVoiceListWorker()
        self.voice_list_worker.result.connect(lambda result, current=current_voice: self.voice_options_loaded_result(result, current))
        self.voice_list_worker.finished.connect(lambda: setattr(self, "voice_list_worker", None))
        self.voice_list_worker.start()

    def voice_options_loaded_result(self, result, current_voice=""):
        self.voice_name.blockSignals(True)
        self.voice_name.clear()
        voices = result.get("voices", [])
        auto_voice = str(self.config.get("VoiceName", "")).strip()
        if not auto_voice:
            sweet_hints = ("xiaoxiao", "huihui", "yaoyao", "xiaoyi", "hanhan", "tingting")
            for hint in sweet_hints:
                auto_voice = next((voice["name"] for voice in voices if hint in voice.get("name", "").lower()), "")
                if auto_voice:
                    break
        if not auto_voice:
            auto_voice = next(
                (
                    voice["name"]
                    for voice in voices
                    if voice.get("culture", "").lower().startswith("zh")
                    and voice.get("gender", "").lower() == "female"
                ),
                "",
            )
        self.voice_name.addItem(f"自动甜美女声（{auto_voice or '系统默认'}）", "")
        for voice in voices:
            label = f"{voice['name']}（{voice.get('culture') or '未知'}，{voice.get('gender') or '未知'}）"
            self.voice_name.addItem(label, voice["name"])
        if current_voice:
            index = self.voice_name.findData(current_voice)
            if index < 0:
                self.voice_name.addItem(current_voice, current_voice)
                index = self.voice_name.findData(current_voice)
            self.voice_name.setCurrentIndex(max(0, index))
        self.voice_name.blockSignals(False)
        self.voice_options_loaded = bool(result.get("ok"))
        self.load_voice_btn.setEnabled(True)
        self.load_voice_btn.setText("重新加载 Windows 离线声音" if self.voice_options_loaded else "加载 Windows 离线声音")
        if not result.get("ok"):
            QMessageBox.information(self, "Windows 离线声音", result.get("error", "没有读取到可用声音。"))

    def selected_voice_name(self):
        data = self.voice_name.currentData()
        return str(data or "").strip()

    def selected_voice_engine(self):
        return str(self.voice_engine.currentData() or DEFAULT_CONFIG["VoiceEngine"])

    def selected_onecore_voice(self):
        return str(self.onecore_voice.currentData() or DEFAULT_CONFIG["OneCoreVoice"])

    def selected_edge_voice(self):
        return str(self.edge_voice.currentData() or DEFAULT_CONFIG["EdgeVoice"])

    def test_voice(self):
        if self.preview_tts_worker and self.preview_tts_worker.isRunning():
            return
        config = dict(self.config)
        config.update(
            {
                "VoiceEngine": self.selected_voice_engine(),
                "OneCoreVoice": self.selected_onecore_voice(),
                "OneCorePitchPercent": self.onecore_pitch.value(),
                "EdgeVoice": self.selected_edge_voice(),
                "EdgePitchHz": self.edge_pitch.value(),
                "VoiceName": self.selected_voice_name(),
                "VoiceVolume": self.voice_volume.value(),
                "VoiceRate": self.voice_rate.value(),
            }
        )
        self.preview_tts_worker = TtsWorker(
            "你好呀，我是糯米。这个声音听起来是不是自然多了？以后我就这样陪你聊天。",
            config,
        )
        self.preview_tts_worker.finished.connect(lambda: setattr(self, "preview_tts_worker", None))
        self.preview_tts_worker.start()

    def pick_pet(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择角色图片", str(BASE), "Images (*.png *.jpg *.jpeg)")
        if path:
            self.pet_path.setText(path)

    def pick_action_pack(self):
        path = QFileDialog.getExistingDirectory(self, "选择动作包文件夹", str(DOG_FRAME_DIR))
        if path:
            self.action_pack.setText(path)

    def pick_tesseract(self):
        start = self.tesseract.text().strip()
        start_dir = str(Path(start).parent) if start else r"C:\Program Files"
        path, _ = QFileDialog.getOpenFileName(self, "选择 tesseract.exe", start_dir, "Tesseract executable (tesseract.exe)")
        if path:
            self.tesseract.setText(path)

    def detect_tesseract(self):
        path = detect_tesseract_path()
        if path:
            self.tesseract.setText(path)
            QMessageBox.information(self, "Tesseract", f"已找到：\n{path}")
        else:
            QMessageBox.information(
                self,
                "Tesseract",
                "这台电脑暂时没有找到 tesseract.exe。\n\n"
                "安装 Tesseract OCR 后，再点“自动检测”或手动选择 tesseract.exe。",
            )

    def use_qq_mail(self):
        self.mail_host.setText("imap.qq.com")
        self.mail_port.setValue(993)
        if not self.mail_keywords.text().strip():
            self.mail_keywords.setText(DEFAULT_CONFIG["MailKeywords"])

    def use_gmail_mail(self):
        if self.mail_user.text().strip().lower().endswith("@gmail.com") and not self.gmail_user.text().strip():
            self.gmail_user.setText(self.mail_user.text().strip())
        if not self.mail_keywords.text().strip():
            self.mail_keywords.setText(DEFAULT_CONFIG["MailKeywords"])

    def open_backup(self):
        if not feature_enabled(self.config, "BackupFeatureEnabled"):
            QMessageBox.information(self, "功能已关闭", "备份 / 迁移已在功能开关里关闭。")
            return
        BackupDialog(self.parent() or self).exec()

    def open_feature_switch(self):
        target = self.parent() if self.parent() is not None and hasattr(self.parent(), "apply_feature_switch_changes") else self
        if FeatureSwitchDialog(self.config, target).exec():
            self.refresh_feature_controls()

    def refresh_feature_controls(self):
        pairs = [
            (self.voice_enabled, "VoiceEnabled"),
            (self.chat_voice_replies, "ChatVoiceReplies"),
            (self.clipboard_enabled, "ClipboardHistoryEnabled"),
            (self.auto_quiet_fullscreen, "AutoQuietFullscreen"),
            (self.auto_hide_fullscreen, "AutoHideFullscreen"),
            (self.auto_hide_games, "AutoHideGames"),
            (self.auto_start, "AutoStart"),
            (self.watchdog_enabled, "WatchdogEnabled"),
            (self.health_watch_enabled, "SystemHealthWatchEnabled"),
            (self.battery_alerts_enabled, "BatteryAlertsEnabled"),
        ]
        for check, key in pairs:
            check.setChecked(feature_enabled(self.config, key))
        if hasattr(self, "backup_btn"):
            self.backup_btn.setVisible(feature_enabled(self.config, "BackupFeatureEnabled"))
        if hasattr(self, "diagnostics_btn"):
            self.diagnostics_btn.setVisible(feature_enabled(self.config, "DiagnosticsFeatureEnabled"))

    def open_diagnostics(self):
        if not feature_enabled(self.config, "DiagnosticsFeatureEnabled"):
            QMessageBox.information(self, "功能已关闭", "诊断中心已在功能开关里关闭。")
            return
        DiagnosticsDialog(self.config, self.parent() or self).exec()

    def save(self):
        mail_host = self.mail_host.text().strip()
        mail_port = normalized_mail_port(mail_host, self.mail_port.value())
        mail_user = self.mail_user.text().strip()
        mail_password = self.mail_pwd.text()
        gmail_user = self.gmail_user.text().strip()
        gmail_password = self.gmail_pwd.text()
        next_config = dict(self.config)
        next_config.update(
            {
                "MailHost": mail_host,
                "MailPort": mail_port,
                "MailUser": mail_user,
                "MailPassword": mail_password,
                "GmailUser": gmail_user,
                "GmailPassword": gmail_password,
                "MailAccounts": [],
            }
        )
        self.config.update(
            {
                "PetName": self.name.text(),
                "PetImagePath": self.pet_path.text(),
                "ActionPackPath": self.action_pack.text().strip(),
                "PetSize": self.size.value(),
                "Opacity": self.opacity.value() / 100,
                "ShowStatus": self.show_status.isChecked(),
                "AiEndpoint": self.ai_endpoint.text(),
                "AiModel": self.ai_model.text(),
                "AiApiKey": self.ai_key.text(),
                "TesseractPath": self.tesseract.text(),
                "ExamDate": self.exam.text(),
                "MailHost": mail_host,
                "MailPort": mail_port,
                "MailUser": mail_user,
                "MailPassword": mail_password,
                "GmailUser": gmail_user,
                "GmailPassword": gmail_password,
                "MailAccounts": mail_accounts_config(next_config),
                "MailKeywords": self.mail_keywords.text(),
                "VoiceEnabled": self.voice_enabled.isChecked(),
                "VoiceEngine": self.selected_voice_engine(),
                "VoiceVolume": self.voice_volume.value(),
                "VoiceName": self.selected_voice_name(),
                "VoiceRate": self.voice_rate.value(),
                "AmbientVoiceCooldownMinutes": self.ambient_voice_cooldown.value(),
                "FullscreenReminderOnly": self.fullscreen_reminder_only.isChecked(),
                "OneCoreVoice": self.selected_onecore_voice(),
                "OneCorePitchPercent": self.onecore_pitch.value(),
                "EdgeVoice": self.selected_edge_voice(),
                "EdgePitchHz": self.edge_pitch.value(),
                "ChatVoiceReplies": self.chat_voice_replies.isChecked(),
                "ClipboardHistoryEnabled": self.clipboard_enabled.isChecked(),
                "QuietMode": self.quiet_mode.isChecked(),
                "AutoQuietFullscreen": self.auto_quiet_fullscreen.isChecked(),
                "AutoHideFullscreen": self.auto_hide_fullscreen.isChecked(),
                "AutoHideGames": self.auto_hide_games.isChecked(),
                "AutoStart": self.auto_start.isChecked(),
                "WatchdogEnabled": self.watchdog_enabled.isChecked(),
                "SystemHealthWatchEnabled": self.health_watch_enabled.isChecked(),
                "CpuAlertPercent": self.cpu_alert.value(),
                "MemoryAlertPercent": self.memory_alert.value(),
                "DiskAlertPercent": self.disk_alert.value(),
                "BatteryAlertsEnabled": self.battery_alerts_enabled.isChecked(),
                "BatteryLowPercent": self.battery_low.value(),
                "BatteryFullPercent": self.battery_full.value(),
                "HealthAlertCooldownMinutes": self.health_cooldown.value(),
                "WeatherCity": self.weather_city.text().strip() or "上海",
            }
        )
        save_json(CONFIG, self.config)
        sync_startup_entry(self.config)
        sync_watchdog(self.config)
        self._font_saved = True
        self.font_preview_timer.stop()
        self.accept()


class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        set_active_text_config(self.config)
        self.drag_pos = QPoint()
        self.dragging = False
        self.state = "待机"
        self.mail_worker = None
        self.tts_worker = None
        self.ocr_worker = None
        self.pending_reminder_speech = ""
        self.last_ambient_voice_at = 0.0
        self.weather_worker = None
        self.startup_worker = None
        self.clipboard_last_text = ""
        self.clipboard_ignore_once = ""
        self.weather_text = f"{self.config.get('WeatherCity', '上海')} 天气读取中"
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.config.get("Topmost", True):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(float(self.config.get("Opacity", 1)))
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.bubble = Bubble(self.config, self)
        self.sprite = PetSprite(self.config)
        self.accessory = QLabel()
        self.accessory.setAlignment(Qt.AlignCenter)
        self.accessory.setStyleSheet(desktop_label_style(self.config, "accessory"))
        self.accessory.hide()
        self.status = QLabel()
        self.status.setStyleSheet(desktop_label_style(self.config))
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setWordWrap(True)
        self.update_desktop_label_bounds()
        self.status.setContextMenuPolicy(Qt.CustomContextMenu)
        self.status.customContextMenuRequested.connect(lambda _pos: self.open_menu())
        self.bubble.setContextMenuPolicy(Qt.CustomContextMenu)
        self.bubble.customContextMenuRequested.connect(lambda _pos: self.open_menu())
        self.layout.addWidget(self.accessory, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.sprite, alignment=Qt.AlignCenter)
        self.layout.addWidget(self.status, alignment=Qt.AlignCenter)
        self.sprite.clicked.connect(self.open_word_popup)
        self.sprite.right_clicked.connect(self.open_menu)
        self.sprite.double_clicked.connect(self.open_ai)
        self.sprite.head_touched.connect(self.head_touch_action)
        self.sprite.body_touched.connect(self.body_touch_action)
        self.sprite.long_pressed.connect(self.long_press_action)
        self.sprite.drag_started.connect(self.begin_sprite_drag)
        self.sprite.drag_moved.connect(self.move_sprite_drag)
        self.sprite.drag_finished.connect(self.end_sprite_drag)
        self.adjustSize()
        self.restore_window_position_from_config()
        self.anim = QPropertyAnimation(self, b"pos", self)
        self.anim.setDuration(1800)
        self.anim.setEasingCurve(QEasingCurve.InOutSine)
        self.pose_timer = QTimer(self)
        self.pose_timer.timeout.connect(self.advance_pose_frame)
        self.pose_frames = []
        self.pose_index = 0
        self.pose_base_pos = QPoint()
        self.position_save_anchor = None
        self.pose_keep_position = False
        self.pose_default_interval = 90
        self.pose_end_action = ""
        self.tick = QTimer(self)
        self.tick.timeout.connect(self.on_tick)
        self.tick.start(1000)
        self.monitor = QTimer(self)
        self.monitor.timeout.connect(self.update_status)
        self.monitor.start(15_000)
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.refresh_weather)
        if feature_enabled(self.config, "WeatherFeatureEnabled"):
            self.weather_timer.start(30 * 60 * 1000)
        self.mail_timer = QTimer(self)
        self.mail_timer.timeout.connect(self.check_mail)
        if feature_enabled(self.config, "MailFeatureEnabled"):
            self.mail_timer.start(5 * 60 * 1000)
        self.health_bad_counts = {}
        saved_health_alerts = load_pet_memory().get("health_last_alert", {})
        self.health_last_alert = (
            {str(key): float(value) for key, value in saved_health_alerts.items() if isinstance(value, (int, float))}
            if isinstance(saved_health_alerts, dict)
            else {}
        )
        self.health_timer = QTimer(self)
        self.health_timer.setInterval(60 * 1000)
        self.health_timer.timeout.connect(self.check_system_health)
        self.sync_health_timer()
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_due_reminders)
        self.reminder_timer.start(60 * 1000)
        self.restore_timer = QTimer(self)
        self.restore_timer.timeout.connect(self.check_restore_request)
        self.restore_timer.start(1000)
        self.auto_hidden_by_context = False
        self.auto_hide_reason = ""
        self.auto_visibility_timer = QTimer(self)
        self.auto_visibility_timer.setInterval(2000)
        self.auto_visibility_timer.timeout.connect(self.update_auto_visibility)
        self.auto_visibility_timer.start()
        self.random_timer = QTimer(self)
        self.random_timer.setSingleShot(True)
        self.random_timer.timeout.connect(self.random_pet_action)
        self.life_timer = QTimer(self)
        self.life_timer.setSingleShot(True)
        self.life_timer.timeout.connect(self.random_life_behavior)
        self.focus_timer = QTimer(self)
        self.focus_timer.setInterval(30 * 1000)
        self.focus_timer.timeout.connect(self.update_focus_session)
        self.look_timer = QTimer(self)
        self.look_timer.timeout.connect(self.track_mouse)
        self.look_timer.start(140)
        self.breath_timer = QTimer(self)
        self.breath_timer.setSingleShot(True)
        self.breath_timer.timeout.connect(self.next_breath)
        self.blink_timer = QTimer(self)
        self.blink_timer.setSingleShot(True)
        self.blink_timer.timeout.connect(self.random_blink)
        self.last_pet_action = ""
        self.touch_times = []
        self.look_angle = 0.0
        self.breath_scale = 1.0
        self.breath_squash = 1.0
        self.last_cursor_pos = QCursor.pos()
        self.last_cursor_time = time.time()
        self.last_scare_time = 0.0
        self.away_mode = False
        self.last_return_greet = 0.0
        self.focus_active = False
        self.focus_phase = "study"
        self.focus_started_at = None
        self.focus_total_minutes = 0
        self.focus_rest_minutes = 0
        self.focus_subject = ""
        self.focus_last_minute = -1
        self.idle_seconds = 0
        self.force_quit = False
        self.tray_notice_shown = False
        self.tray = None
        self.word_dialog = None
        self.toolbox_worker = None
        self.setup_tray()
        self.bubble.say(f"{self.config.get('PetName')} 已上线。")
        QApplication.clipboard().dataChanged.connect(self.capture_clipboard)
        self.update_status()
        self.refresh_growth_state(show_new=False)
        if feature_enabled(self.config, "WeatherFeatureEnabled"):
            self.refresh_weather(show_bubble=False)
        QTimer.singleShot(1800, self.daily_memory_greeting)
        QTimer.singleShot(2600, self.check_exam_event)
        QTimer.singleShot(4200, self.check_seasonal_event)
        QTimer.singleShot(3500, self.check_holiday_reminder)
        if feature_enabled(self.config, "MailFeatureEnabled"):
            QTimer.singleShot(8000, self.check_mail)
        QTimer.singleShot(12000, self.check_due_reminders)
        QTimer.singleShot(15000, self.check_system_health)
        self.schedule_random_action()
        self.schedule_life_behavior()
        self.schedule_blink()
        self.schedule_breath()

        # Word popup timer - shows random Redbook word every 4-8 minutes
        self._word_timer = QTimer(self)
        self._word_timer.timeout.connect(self._show_word_popup)
        if feature_enabled(self.config, "word_popup_enabled") and self.config.get("BubbleEnabled", True):
            self._word_timer.start(random.randint(240000, 480000))
        QTimer.singleShot(5000, self.run_startup_maintenance)

    def run_startup_maintenance(self):
        if self.startup_worker and self.startup_worker.isRunning():
            return
        self.startup_worker = StartupMaintenanceWorker(self.config)
        self.startup_worker.result.connect(append_runtime_log)
        self.startup_worker.finished.connect(lambda: setattr(self, "startup_worker", None))
        self.startup_worker.start()

    def foreground_fullscreen_active(self):
        exclude_hwnds = {int(self.winId())}
        if hasattr(self, "bubble"):
            exclude_hwnds.add(int(self.bubble.winId()))
        return foreground_window_fullscreen(exclude_hwnds=exclude_hwnds, exclude_pids={os.getpid()})

    def fullscreen_should_hide_bubble(self):
        return bool(self.config.get("AutoQuietFullscreen", True) and self.foreground_fullscreen_active())

    def should_suppress_bubble(self):
        if not self.config.get("BubbleEnabled", True):
            return True
        if getattr(self, "auto_hidden_by_context", False):
            return True
        if self.fullscreen_should_hide_bubble():
            return True
        return False

    def hide_bubble_now(self):
        self.bubble.set_click_callback(None)
        self.bubble.hide()
        if self.word_dialog is not None:
            self.word_dialog.hide()

    def is_quiet(self):
        if self.config.get("QuietMode", False):
            return True
        if self.fullscreen_should_hide_bubble():
            return True
        return False

    def voice_context_busy(self):
        if getattr(self, "auto_hidden_by_context", False):
            return True
        exclude_hwnds = {int(self.winId())}
        exclude_pids = {os.getpid()}
        return foreground_window_fullscreen(
            exclude_hwnds=exclude_hwnds,
            exclude_pids=exclude_pids,
        ) or foreground_game_window(exclude_pids=exclude_pids)

    def auto_hide_context_reason(self):
        reasons = []
        exclude_hwnds = {int(self.winId())}
        exclude_pids = {os.getpid()}
        is_fullscreen = foreground_window_fullscreen(exclude_hwnds=exclude_hwnds, exclude_pids=exclude_pids)
        is_game = foreground_game_window(exclude_pids=exclude_pids)
        if is_game and self.config.get("AutoHideFullscreen", True) and is_fullscreen:
            reasons.append("全屏游戏")
        elif is_game and self.config.get("AutoHideGames", True):
            reasons.append("游戏窗口")
        return " / ".join(reasons)

    def update_auto_visibility(self):
        reason = self.auto_hide_context_reason()
        if reason:
            if self.isVisible() and not self.dragging:
                self.save_window_position()
                self.auto_hidden_by_context = True
                self.auto_hide_reason = reason
                self.hide_bubble_now()
                self.hide()
                append_runtime_log(f"auto hidden by {reason}")
            elif self.auto_hidden_by_context:
                self.auto_hide_reason = reason
            return
        if self.auto_hidden_by_context:
            self.auto_hidden_by_context = False
            self.auto_hide_reason = ""
            self.restore_from_tray(say=False, activate=False)
        if self.fullscreen_should_hide_bubble():
            self.hide_bubble_now()

    def daily_memory_greeting(self):
        if self.is_quiet():
            return
        memory = load_pet_memory()
        today = datetime.now().date().isoformat()
        if memory.get("last_greeting_date") == today:
            return
        memory["last_greeting_date"] = today
        save_pet_memory(memory)
        if self.is_sleep_time():
            self.react("睡觉", "Zzz...怎么这么晚还在电脑前。")
            return
        if entertainment_running():
            self.react("提醒", "你不是说要学高数吗？先收个心。")
            return
        text = self.continuity_greeting_text()
        self.bubble.say(text)
        self.speak(text)

    def continuity_greeting_text(self):
        now = datetime.now()
        today_summary = study_day_summary(now.date())
        yesterday_summary = study_day_summary(now.date() - timedelta(days=1))
        streak = study_streak_text()
        pieces = []
        if now.hour >= 22 and today_summary:
            pieces.append(today_summary)
            pieces.append("今天辛苦了，别硬熬。")
        elif yesterday_summary:
            pieces.append(yesterday_summary)
            pieces.append("休息得怎么样？")
        else:
            remembered = yesterday_study_memory()
            if remembered:
                pieces.append(remembered)
        if streak:
            pieces.append(streak)
        if not pieces:
            pieces.append(time_greeting())
        return "\n".join(pieces)

    def check_daily_summary(self):
        if self.is_quiet():
            return
        now = datetime.now()
        if now.hour < 22:
            return
        memory = load_pet_memory()
        today = now.date().isoformat()
        if memory.get("last_evening_summary_date") == today:
            return
        text = study_day_summary(now.date())
        if not text:
            return
        memory["last_evening_summary_date"] = today
        save_pet_memory(memory)
        extra = study_streak_text()
        self.react("学习陪伴", text + ("\n" + extra if extra else "\n今天辛苦了。"))

    def check_exam_event(self):
        text = exam_event_text(self.config)
        if not text:
            return
        memory = load_pet_memory()
        days = exam_days_left(self.config)
        key = f"{datetime.now().date().isoformat()}:{days}"
        if memory.get("last_exam_event_key") == key:
            return
        memory["last_exam_event_key"] = key
        save_pet_memory(memory)
        self.react("开心" if days is not None and days < 0 else "提醒", text)

    def check_seasonal_event(self):
        if self.is_quiet():
            return
        if self.is_sleep_time() or self.focus_active:
            return
        memory = load_pet_memory()
        today = datetime.now().date().isoformat()
        if memory.get("last_season_event_date") == today:
            return
        memory["last_season_event_date"] = today
        save_pet_memory(memory)
        line = seasonal_mood_text()
        if line:
            self.bubble.say(line)
            if "热" in line or "趴" in line:
                self.dog_sleep()
            elif "冷" in line or "围巾" in line:
                self.dog_attention()
            else:
                self.dog_sniff()

    def check_weather_mood(self, text):
        if self.is_quiet():
            return
        line = weather_mood_text(text)
        if not line:
            return
        memory = load_pet_memory()
        key = f"{datetime.now().date().isoformat()}:{line}"
        if memory.get("last_weather_mood_key") == key:
            return
        memory["last_weather_mood_key"] = key
        save_pet_memory(memory)
        if "热" in line or "趴" in line:
            self.react("睡觉", line)
        else:
            self.react("提醒", line)

    def refresh_growth_state(self, show_new=True):
        earned = earned_collectibles()
        memory = load_pet_memory()
        old = set(memory.get("collectibles", []))
        new = [key for key in earned if key not in old]
        if earned:
            self.accessory.setText(collectible_marks(earned[-2:]))
            self.accessory.adjustSize()
            self.accessory.show()
        else:
            self.accessory.hide()
        memory["collectibles"] = earned
        save_pet_memory(memory)
        if show_new and new:
            names = "、".join(COLLECTIBLES[key]["name"] for key in new if key in COLLECTIBLES)
            if names:
                self.react("开心", f"获得收藏：{names}。这是你养出来的糯米。")

    def check_environment_mood(self):
        if self.is_quiet():
            return
        if not entertainment_running():
            return
        memory = load_pet_memory()
        today = datetime.now().date().isoformat()
        if memory.get("last_fun_warning_date") == today:
            return
        memory["last_fun_warning_date"] = today
        save_pet_memory(memory)
        self.react("提醒", "我看到摸鱼软件了。今天的任务先做一点点？")

    def check_sleep_mood(self):
        if self.is_quiet():
            return
        if not self.is_sleep_time() or self.focus_active or self.dragging:
            return
        memory = load_pet_memory()
        today = datetime.now().date().isoformat()
        if memory.get("last_sleep_hint_date") == today:
            return
        memory["last_sleep_hint_date"] = today
        save_pet_memory(memory)
        self.react("睡觉", "Zzz...夜深了，我先趴下。")

    def react(self, state, text, voice_kind="ambient"):
        if self.dragging:
            if voice_kind == "reminder":
                self.speak(text, kind="reminder")
            return
        self.state = state
        self.idle_seconds = 0
        self.bubble.say(text)
        self.speak(text, kind=voice_kind)
        if state == "开心":
            self.dog_happy()
        elif state == "生气":
            self.dog_recoil()
        elif state == "慌张":
            self.dog_panic()
        elif state == "惊讶":
            self.dog_panic()
        elif state == "提醒":
            self.dog_attention()
        elif state == "睡觉":
            self.dog_sleep()

    def idle_pose_allowed(self):
        return (
            self.isVisible()
            and not self.dragging
            and not self.pose_timer.isActive()
            and not self.focus_active
            and self.state in ("待机", "好奇", "发呆", "思考")
        )

    def apply_idle_pose(self):
        if not self.idle_pose_allowed():
            return
        look_action = "look_center"
        if self.look_angle <= -2.2:
            look_action = "look_left"
        elif self.look_angle >= 2.2:
            look_action = "look_right"
        if self.sprite.has_animation(look_action) and self.sprite.current_action != look_action:
            self.sprite.set_animation_frame(look_action, 0)
        self.sprite.set_pose(scale=self.breath_scale, squash=self.breath_squash, angle=self.look_angle)

    def track_mouse(self):
        if not self.isVisible():
            return
        cursor = QCursor.pos()
        now = time.time()
        dt = max(0.05, now - self.last_cursor_time)
        move = cursor - self.last_cursor_pos
        speed = ((move.x() * move.x() + move.y() * move.y()) ** 0.5) / dt
        self.last_cursor_pos = cursor
        self.last_cursor_time = now

        center = self.sprite.mapToGlobal(self.sprite.rect().center())
        dx = cursor.x() - center.x()
        dy = cursor.y() - center.y()
        distance = (dx * dx + dy * dy) ** 0.5
        if speed > 1800 and distance < 320 and now - self.last_scare_time > 8 and not self.is_quiet():
            self.last_scare_time = now
            self.react("惊讶", "Σ( ° △ °|||)︴")
            return
        if not self.idle_pose_allowed():
            return
        if distance < 280:
            self.look_angle = max(-10.0, min(10.0, dx / 22))
            if distance < 135 and now - self.last_return_greet > 20:
                self.state = "好奇"
                self.update_status()
        else:
            self.look_angle *= 0.72
            if abs(self.look_angle) < 0.4:
                self.look_angle = 0.0
        self.apply_idle_pose()

    def schedule_blink(self):
        self.blink_timer.start(random.randint(3_000, 12_000))

    def random_blink(self):
        try:
            if self.idle_pose_allowed():
                self.blink()
        finally:
            self.schedule_blink()

    def schedule_breath(self):
        self.breath_timer.start(random.randint(800, 1_600))

    def next_breath(self):
        try:
            if self.idle_pose_allowed():
                self.breath_scale = random.uniform(0.985, 1.025)
                self.breath_squash = random.uniform(0.975, 1.02)
                self.apply_idle_pose()
        finally:
            self.schedule_breath()

    def check_presence_reaction(self):
        if self.is_quiet():
            return
        idle = seconds_since_last_input()
        now = time.time()
        if idle >= 20 * 60 and self.state != "睡觉" and not self.focus_active:
            self.away_mode = True
            self.react("睡觉", "你不在的话，我先睡一下。")
            return
        if idle >= 10 * 60 and self.state not in ("睡觉", "趴下") and not self.focus_active:
            self.away_mode = True
            self.state = "趴下"
            self.update_status()
            self.dog_sleep()
            self.bubble.say("我先趴一会儿。")
            return
        if self.away_mode and idle < 8 and now - self.last_return_greet > 60:
            self.away_mode = False
            self.last_return_greet = now
            self.react("惊讶", "回来啦？")

    def speak(self, text, kind="ambient"):
        speech = clean_tts_text(text)
        if not speech:
            return
        now = time.time()
        if not voice_policy_allows(
            self.config,
            kind=kind,
            context_busy=self.voice_context_busy(),
            last_ambient_at=self.last_ambient_voice_at,
            now=now,
        ):
            return
        if self.tts_worker and self.tts_worker.isRunning():
            if kind == "reminder":
                self.pending_reminder_speech = speech
            return
        if kind == "ambient":
            self.last_ambient_voice_at = now
        self.tts_worker = TtsWorker(
            speech,
            self.config,
        )
        self.tts_worker.finished.connect(self.tts_finished)
        self.tts_worker.start()

    def tts_finished(self):
        self.tts_worker = None
        pending = self.pending_reminder_speech
        self.pending_reminder_speech = ""
        if pending:
            self.speak(pending, kind="reminder")

    def play_pose_sequence(self, frames, interval=90, keep_position=False, end_action=""):
        if self.dragging:
            return
        self.anim.stop()
        self.pose_timer.stop()
        self.pose_frames = frames
        self.pose_index = 0
        self.pose_base_pos = self.pos()
        self.position_save_anchor = QPoint(self.pose_base_pos) if self.config.get("LockPetPosition", True) else None
        self.pose_keep_position = keep_position
        self.pose_end_action = end_action or ""
        self.pose_default_interval = max(45, int(interval))
        self.pose_timer.setInterval(self.pose_default_interval)
        self.advance_pose_frame()
        if self.pose_frames:
            self.pose_timer.start()

    def advance_pose_frame(self):
        if self.pose_index >= len(self.pose_frames):
            self.pose_timer.stop()
            if self.pose_end_action and self.sprite.has_animation(self.pose_end_action):
                self.sprite.set_animation_frame(
                    self.pose_end_action,
                    max(0, self.sprite.frame_count(self.pose_end_action) - 1),
                )
            else:
                self.sprite.show_idle()
            if not self.pose_keep_position:
                self.move_pose_to(self.pose_base_pos, 120)
            if self.state not in ("提醒", "睡觉", "趴下"):
                self.state = "待机"
            self.update_status()
            return
        frame = self.pose_frames[self.pose_index]
        duration = self.pose_default_interval
        if isinstance(frame, dict):
            self.sprite.set_animation_frame(frame.get("action", "idle"), int(frame.get("frame", 0)))
            dx = int(frame.get("dx", 0))
            dy = int(frame.get("dy", 0))
            duration = max(45, int(frame.get("duration", duration)))
            self.move_pose_to(self.pose_base_pos + QPoint(dx, dy), duration)
        else:
            scale, squash, angle, dx, dy = frame
            self.sprite.set_pose(scale, squash, angle)
            self.move_pose_to(self.pose_base_pos + QPoint(dx, dy), duration)
        self.pose_timer.setInterval(duration)
        self.pose_index += 1

    def move_pose_to(self, pos, duration=90):
        target = self.clamped_pos(pos)
        if duration < 80 or (target - self.pos()).manhattanLength() < 2:
            self.move(target)
            return
        self.anim.stop()
        self.anim.setDuration(max(70, min(260, int(duration * 0.82))))
        self.anim.setEasingCurve(QEasingCurve.OutCubic)
        self.anim.setStartValue(self.pos())
        self.anim.setEndValue(target)
        self.anim.start()

    def play_sprite_sequence(self, action, frames=None, interval=120, offsets=None, keep_position=False, durations=None, end_action=""):
        if not self.sprite.has_animation(action):
            return False
        frames = frames or list(range(len(self.sprite.animations.get(action, []))))
        offsets = offsets or [(0, 0)] * len(frames)
        sequence = []
        for index, frame_index in enumerate(frames):
            dx, dy = offsets[index] if index < len(offsets) else (0, 0)
            duration = durations[index] if durations and index < len(durations) else interval
            sequence.append({"action": action, "frame": frame_index, "dx": dx, "dy": dy, "duration": duration})
        self.play_pose_sequence(sequence, interval=interval, keep_position=keep_position, end_action=end_action)
        return True

    def action_frames(self, action):
        count = self.sprite.frame_count(action)
        return list(range(count)) if count else []

    def dog_happy(self):
        frames = self.action_frames("happy")
        if frames:
            offsets = []
            for index in range(len(frames)):
                progress = index / max(1, len(frames) - 1)
                bounce = -int(math.sin(progress * math.pi) * random.randint(18, 28))
                side = int(math.sin(progress * math.pi * 2) * 5)
                offsets.append((side, bounce))
            durations = [random.randint(95, 145) for _ in frames]
        if frames and self.play_sprite_sequence(
            "happy",
            frames=frames,
            offsets=offsets,
            durations=durations,
            interval=random.randint(105, 155),
        ):
            return
        self.play_pose_sequence(
            [
                (1.03, 0.98, -9, -4, -4),
                (1.08, 0.94, 10, 5, -12),
                (1.02, 1.03, -8, -4, -2),
                (1.09, 0.95, 11, 5, -14),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=85,
        )

    def dog_recoil(self):
        frames = self.action_frames("angry")
        if frames:
            offsets = []
            for index in range(len(frames)):
                progress = index / max(1, len(frames) - 1)
                offsets.append((-int(math.sin(progress * math.pi) * 24), int(math.sin(progress * math.pi) * 5)))
        if frames and self.play_sprite_sequence(
            "angry",
            frames=frames,
            offsets=offsets,
            interval=random.randint(145, 215),
        ):
            return
        self.play_pose_sequence(
            [
                (0.92, 0.86, -13, -20, 8),
                (0.9, 0.82, 12, -28, 10),
                (1.04, 0.95, -6, -10, -5),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=95,
        )

    def dog_panic(self):
        frames = self.action_frames("surprised")
        if frames:
            offsets = []
            for index in range(len(frames)):
                progress = index / max(1, len(frames) - 1)
                offsets.append((int(math.sin(progress * math.pi * 4) * 7), -int(math.sin(progress * math.pi) * 18)))
        if frames and self.play_sprite_sequence(
            "surprised",
            frames=frames,
            offsets=offsets,
            interval=random.randint(105, 165),
        ):
            return
        self.play_pose_sequence(
            [
                (1.02, 0.9, -12, -10, 4),
                (1.12, 0.92, 12, 12, -18),
                (0.98, 1.06, -8, -7, 4),
                (1.1, 0.94, 9, 8, -15),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=80,
        )

    def dog_attention(self):
        frames = self.action_frames("surprised")
        if frames:
            offsets = [(0, -int(math.sin(index / max(1, len(frames) - 1) * math.pi) * 10)) for index in range(len(frames))]
        if frames and self.play_sprite_sequence(
            "surprised",
            frames=frames,
            offsets=offsets,
            interval=random.randint(130, 200),
        ):
            return
        self.play_pose_sequence(
            [
                (0.98, 0.86, 0, 0, 7),
                (1.12, 0.94, -5, 0, -18),
                (1.07, 0.98, 6, 0, -10),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=90,
        )

    def dog_sleep(self):
        frames = self.action_frames("sleep")
        if frames and self.play_sprite_sequence(
            "sleep",
            frames=frames,
            interval=random.randint(260, 390),
            durations=[random.randint(260, 430) for _ in frames],
            end_action="sleep",
        ):
            return
        self.play_pose_sequence(
            [
                (0.98, 0.9, -4, 0, 6),
                (0.94, 0.8, -8, 0, 16),
                (0.9, 0.74, -10, 0, 20),
                (0.9, 0.74, -10, 0, 20),
                (0.92, 0.78, -7, 0, 14),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=220,
        )

    def dog_sniff(self):
        self.state = "闻一闻"
        self.update_status()
        direction = random.choice([-1, 1])
        action = "sniff_right" if direction > 0 and self.sprite.has_animation("sniff_right") else "sniff"
        frames = self.action_frames(action)
        if frames:
            offsets = []
            for index in range(len(frames)):
                progress = index / max(1, len(frames) - 1)
                reach = math.sin(progress * math.pi)
                offsets.append((direction * int(38 * reach), int(3 * abs(math.sin(progress * math.pi * 2)))))
        if frames and self.play_sprite_sequence(
            action,
            frames=frames,
            offsets=offsets,
            interval=random.randint(130, 215),
            keep_position=True,
        ):
            return
        self.play_pose_sequence(
            [
                (0.98, 0.84, direction * -9, direction * 8, 12),
                (0.96, 0.78, direction * -14, direction * 17, 16),
                (0.98, 0.82, direction * -8, direction * 26, 12),
                (1.0, 0.9, direction * 6, direction * 18, 7),
                (1.0, 1.0, 0, direction * 8, 0),
            ],
            interval=120,
        )

    def dog_stretch(self):
        self.state = "伸懒腰"
        self.update_status()
        frames = self.action_frames("stretch")
        if frames and self.play_sprite_sequence(
            "stretch",
            frames=frames,
            offsets=[(0, int(math.sin(index / max(1, len(frames) - 1) * math.pi) * 8)) for index in range(len(frames))],
            interval=random.randint(150, 240),
        ):
            return
        self.play_pose_sequence(
            [
                (1.0, 0.88, 0, 0, 9),
                (1.12, 0.78, -7, -8, 18),
                (1.15, 0.74, 7, 8, 20),
                (1.02, 0.94, 0, 0, 4),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=120,
        )

    def dog_reading(self):
        self.state = "学习陪伴"
        self.update_status()
        frames = self.action_frames("study")
        if frames and self.play_sprite_sequence(
            "study",
            frames=frames,
            offsets=[(0, -int(math.sin(index / max(1, len(frames) - 1) * math.pi) * 3)) for index in range(len(frames))],
            interval=random.randint(220, 330),
            end_action="study",
        ):
            return
        self.play_pose_sequence(
            [
                (1.0, 0.96, -2, 0, 2),
                (1.02, 0.94, 2, 0, 0),
                (1.0, 0.96, -2, 0, 2),
                (1.0, 1.0, 0, 0, 0),
            ],
            interval=240,
        )

    def choose_pet_action(self, actions):
        choices = [item for item in actions if item[0] != self.last_pet_action]
        if not choices:
            choices = actions
        name, state, fn, lines = random.choice(choices)
        self.last_pet_action = name
        return state, fn, lines

    def perform_pet_action(self, actions, say_chance=0.25):
        if self.dragging:
            return
        state, fn, lines = self.choose_pet_action(actions)
        self.state = state
        self.idle_seconds = 0
        self.update_status()
        if lines and random.random() < say_chance:
            self.bubble.say(random.choice(lines))
        fn()

    def random_touch_action(self):
        self.random_timer.stop()
        self.perform_pet_action(
            [
                ("happy", "开心", self.dog_happy, ["嘿嘿，摸到我啦。", "我在！"]),
                ("sniff", "闻一闻", self.dog_sniff, ["我闻闻今天有什么任务。"]),
                ("attention", "好奇", self.dog_attention, ["嗯？叫我吗？"]),
                ("stretch", "伸懒腰", self.dog_stretch, ["伸个懒腰。"]),
                ("walk", "散步", self.short_walk, []),
            ],
            say_chance=0.18,
        )
        self.schedule_random_action()

    def register_touch(self):
        now = time.time()
        self.touch_times = [item for item in self.touch_times if now - item < 2.4]
        self.touch_times.append(now)
        memory = load_pet_memory()
        memory["touch_count"] = int(memory.get("touch_count", 0)) + 1
        save_pet_memory(memory)
        return len(self.touch_times)

    def is_sleep_time(self):
        hour = datetime.now().hour
        return hour >= 1 or hour < 6

    def head_touch_action(self):
        self.open_word_popup()
        self.schedule_random_action()

    def body_touch_action(self):
        self.open_word_popup()
        self.schedule_random_action()

    def long_press_action(self):
        self.react("慌张", "啊——抱起来了吗？")

    def on_pet_click(self):
        self.open_word_popup()

    def schedule_random_action(self):
        self.random_timer.start(random.randint(70_000, 180_000))

    def schedule_life_behavior(self, min_minutes=30, max_minutes=90):
        self.life_timer.start(random.randint(min_minutes * 60_000, max_minutes * 60_000))

    def perform_named_pose(self, action):
        mapping = {
            "stretch": self.dog_stretch,
            "sleep": self.dog_sleep,
            "sniff": self.dog_sniff,
            "peek": self.peek_around,
            "happy": self.dog_happy,
            "attention": self.dog_attention,
            "study": self.study_nudge,
            "dream": self.daydream,
        }
        mapping.get(action, self.blink)()

    def random_life_behavior(self):
        try:
            if self.is_quiet() or self.dragging or not self.isVisible() or self.pose_timer.isActive() or self.focus_active:
                return
            action, state, line = random.choice(LIFE_BEHAVIORS)
            self.state = state
            self.idle_seconds = 0
            self.update_status()
            self.bubble.say(line, 6500)
            self.speak(line, kind="ambient")
            self.perform_named_pose(action)
        finally:
            self.schedule_life_behavior()

    def random_pet_action(self):
        try:
            if not self.is_quiet() and not self.dragging and self.isVisible() and not self.pose_timer.isActive():
                self.perform_pet_action(
                    [
                        ("blink", "待机", self.blink, []),
                        ("stretch", "伸懒腰", self.dog_stretch, ["伸个懒腰，继续陪你。"]),
                        ("sniff", "闻一闻", self.dog_sniff, []),
                        ("happy", "开心", self.dog_happy, []),
                        ("peek", "好奇", self.peek_around, ["我看看你在忙什么。"]),
                        ("walk", "散步", self.short_walk, []),
                        ("study", "学习陪伴", self.study_nudge, ["要不要记一轮番茄？"]),
                        ("dream", "发呆", self.daydream, []),
                    ],
                    say_chance=0.22,
                )
        finally:
            self.schedule_random_action()

    def blink(self):
        frames = self.action_frames("blink")
        if frames and self.idle_pose_allowed():
            if self.play_sprite_sequence(
                "blink",
                frames=frames,
                offsets=[(0, 0)] * len(frames),
                durations=[random.randint(55, 95) for _ in frames],
                interval=random.randint(60, 100),
                keep_position=True,
            ):
                return
        effect = QGraphicsOpacityEffect(self.sprite)
        effect.setOpacity(1.0)
        self.sprite.setGraphicsEffect(effect)
        self.blink_anim = QPropertyAnimation(effect, b"opacity", self)
        self.blink_anim.setDuration(260)
        self.blink_anim.setKeyValueAt(0.0, 1.0)
        self.blink_anim.setKeyValueAt(0.45, 0.38)
        self.blink_anim.setKeyValueAt(1.0, 1.0)
        self.blink_anim.finished.connect(lambda: self.sprite.setGraphicsEffect(None))
        self.blink_anim.start()

    def stretch(self):
        self.dog_stretch()
        self.bubble.say(random.choice(["伸个懒腰，继续陪你。", "活动一下，脑子会更清醒。"]))

    def peek_around(self):
        self.state = "好奇"
        self.update_status()
        self.dog_sniff()
        if random.random() < 0.5:
            self.bubble.say(random.choice(["我看看你在忙什么。", "有问题可以直接问我。"]))

    def short_walk(self):
        self.short_walk_direction(random.choice([-1, 1]))

    def short_walk_direction(self, direction):
        self.state = "散步"
        self.update_status()
        keep_final_position = not self.config.get("LockPetPosition", True)
        step = random.randint(34, 62)
        action = "walk_right" if direction > 0 else "walk_left"
        interval = random.randint(135, 225)
        frames = self.action_frames(action)
        if frames:
            offsets = []
            durations = []
            for index in range(len(frames)):
                progress = index / max(1, len(frames) - 1)
                ease = 0.5 - math.cos(progress * math.pi) * 0.5
                foot_lift = -int(abs(math.sin(progress * math.pi * 2)) * 5)
                offsets.append((direction * int(step * ease), foot_lift))
                durations.append(random.randint(105, 155))
        if frames and self.play_sprite_sequence(
            action,
            frames=frames,
            offsets=offsets,
            durations=durations,
            interval=interval,
            keep_position=keep_final_position,
        ):
            return
        self.play_pose_sequence(
            [
                (1.0, 0.96, -7, direction * int(step * 0.15), -4),
                (1.04, 0.92, 8, direction * int(step * 0.32), -9),
                (0.98, 1.04, -6, direction * int(step * 0.52), 0),
                (1.04, 0.92, 7, direction * int(step * 0.75), -8),
                (1.0, 1.0, 0, direction * step, 0),
            ],
            interval=random.randint(90, 145),
            keep_position=keep_final_position,
        )

    def study_nudge(self):
        if self.idle_seconds < 60:
            self.dog_reading()
            return
        self.state = "学习陪伴"
        self.update_status()
        self.dog_reading()
        self.bubble.say(random.choice(["学一点点也算前进。", "要不要记一轮番茄？", "今天的高数还可以再摸一下。"]))

    def daydream(self):
        self.state = random.choice(["发呆", "思考", "待机"])
        self.update_status()
        self.dog_sniff()
        if random.random() < 0.35:
            self.bubble.say(random.choice(["我在想下一步怎么帮你。", "先把最小的一件事做掉也不错。"]))

    def window_size_for_restore(self):
        size = self.frameGeometry().size()
        if size.width() <= 1 or size.height() <= 1:
            size = self.sizeHint()
        return QSize(max(1, size.width()), max(1, size.height()))

    def clamped_pos(self, pos):
        return clamp_window_position(pos, self.window_size_for_restore())

    def ensure_safe_window_position(self, save=False):
        target = self.clamped_pos(self.pos())
        if target != self.pos():
            self.move(target)
        if save:
            self.save_window_position()
        return target

    def restore_window_position_from_config(self):
        saved_left = int(self.config.get("WindowLeft", -1))
        saved_top = int(self.config.get("WindowTop", -1))
        size = self.window_size_for_restore()
        has_saved = not (saved_left == -1 and saved_top == -1)
        target = QPoint(saved_left, saved_top) if has_saved else default_window_position(size)
        safe = clamp_window_position(target, size)
        self.move(safe)
        if not has_saved or safe != target:
            self.config["WindowLeft"] = safe.x()
            self.config["WindowTop"] = safe.y()
            save_json(CONFIG, self.config)

    def begin_sprite_drag(self, global_pos):
        self.anim.stop()
        self.pose_timer.stop()
        self.sprite.show_idle()
        self.position_save_anchor = None
        self.dragging = True
        self.drag_pos = global_pos - self.frameGeometry().topLeft()
        self.state = "拖动"
        self.update_status()
        self.bubble.say("啊——慢一点。")

    def move_sprite_drag(self, global_pos):
        if self.dragging:
            self.move(self.clamped_pos(global_pos - self.drag_pos))

    def end_sprite_drag(self):
        if self.dragging:
            self.dragging = False
            self.state = "待机"
            self.update_status()
            self.ensure_safe_window_position(save=True)
            self.bubble.say("安全着陆。")
            self.dog_happy()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.anim.stop()
            self.position_save_anchor = None
            self.dragging = True
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.state = "拖动"
            self.update_status()
            self.bubble.say("啊——慢一点。")
            if self.windowHandle() and self.windowHandle().startSystemMove():
                event.accept()
                return

    def mouseMoveEvent(self, event):
        if self.dragging and (event.buttons() & Qt.LeftButton):
            self.move(self.clamped_pos(event.globalPosition().toPoint() - self.drag_pos))
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.open_menu()
            event.accept()
            return
        if self.dragging:
            self.dragging = False
            self.state = "待机"
            self.update_status()
            self.ensure_safe_window_position(save=True)
            self.bubble.say("安全着陆。")
            event.accept()

    def contextMenuEvent(self, event):
        self.open_menu()
        event.accept()

    def wheelEvent(self, event):
        event.ignore()

    def resize_pet(self, step):
        size = int(self.config.get("PetSize", 230)) + step
        size = max(120, min(380, size))
        self.config["PetSize"] = size
        self.sprite.config = self.config
        self.sprite.set_pet_size(size)
        self.update_desktop_label_bounds()
        save_json(CONFIG, self.config)
        self.adjustSize()
        self.ensure_safe_window_position(save=True)
        if self.bubble.isVisible():
            self.position_bubble()
        self.bubble.say(f"大小：{size}px")

    def tray_icon_source(self):
        custom_path = self.config.get("PetImagePath", "")
        candidates = [
            Path(custom_path) if custom_path else None,
            DOG_FRAME_DIR / "idle_0.png",
            ASSET,
        ]
        for path in candidates:
            if path and path.exists():
                return str(path)
        return ""

    def refresh_window_flags(self):
        was_visible = self.isVisible()
        flags = Qt.FramelessWindowHint | Qt.Tool
        if self.config.get("Topmost", True):
            flags |= Qt.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        if was_visible:
            self.show()
            self.raise_()

    def setup_tray(self):
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        icon_path = self.tray_icon_source()
        icon = QIcon(icon_path) if icon_path else self.windowIcon()
        self.tray = QSystemTrayIcon(icon, self)
        pet_name = str(self.config.get("PetName") or DEFAULT_CONFIG["PetName"])
        self.tray.setToolTip(f"{pet_name} - 双击显示/收起")
        menu = QMenu()
        show_action = QAction(f"显示{pet_name}", self)
        show_action.triggered.connect(self.restore_from_tray)
        hide_action = QAction("收起到托盘", self)
        hide_action.triggered.connect(self.hide_to_tray)
        ai_action = QAction(f"问问{pet_name}", self)
        ai_action.triggered.connect(self.open_ai)
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.open_settings)
        quit_action = QAction(f"退出{pet_name}", self)
        quit_action.triggered.connect(self.exit_pet)
        self.tray_show_action = show_action
        self.tray_ai_action = ai_action
        self.tray_quit_action = quit_action
        for action in (show_action, hide_action, ai_action, settings_action):
            menu.addAction(action)
        menu.addSeparator()
        menu.addAction(quit_action)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def refresh_tray_labels(self):
        if not self.tray:
            return
        pet_name = str(self.config.get("PetName") or DEFAULT_CONFIG["PetName"])
        self.tray.setToolTip(f"{pet_name} - 双击显示/收起")
        if hasattr(self, "tray_show_action"):
            self.tray_show_action.setText(f"显示{pet_name}")
        if hasattr(self, "tray_ai_action"):
            self.tray_ai_action.setText(f"问问{pet_name}")
        if hasattr(self, "tray_quit_action"):
            self.tray_quit_action.setText(f"退出{pet_name}")

    def on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.DoubleClick, QSystemTrayIcon.Trigger):
            if self.isVisible():
                self.hide_to_tray(show_notice=False)
            else:
                self.restore_from_tray()

    def restore_from_tray(self, *args, say=True, activate=True):
        self.auto_hidden_by_context = False
        self.auto_hide_reason = ""
        self.ensure_safe_window_position(save=True)
        self.show()
        self.raise_()
        if activate:
            self.activateWindow()
        if say:
            self.bubble.say("我回来啦。")

    def hide_to_tray(self, *args, show_notice=True):
        self.auto_hidden_by_context = False
        self.auto_hide_reason = ""
        self.save_window_position()
        self.bubble.hide()
        self.hide()
        if self.tray and show_notice and not self.tray_notice_shown:
            self.tray.showMessage(
                self.config.get("PetName", "糯米"),
                "我在托盘里。双击托盘图标，或按 Ctrl + Shift + H 可以叫我回来。",
                QSystemTrayIcon.Information,
                4200,
            )
            self.tray_notice_shown = True

    def toggle_visibility(self):
        if self.isVisible():
            self.hide_to_tray()
        else:
            self.restore_from_tray()

    def check_restore_request(self):
        if not RESTORE_FLAG.exists():
            return
        try:
            RESTORE_FLAG.unlink()
        except Exception:
            pass
        self.restore_from_tray()


    def open_notebook(self):
        if not self.require_feature("NotebookFeatureEnabled"):
            return
        dlg = QDialog(self)
        dlg.setWindowTitle("笔记本")
        dlg.resize(500, 440)
        dlg.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(dlg)
        tabs = QTabWidget()
        layout.addWidget(tabs)
        # Tab 1: Notes
        tab1 = QWidget()
        t1l = QVBoxLayout(tab1)
        notes = self.config.setdefault("notebook_content", "")
        text = QTextEdit()
        text.setPlainText(notes)
        t1l.addWidget(text)
        def save_notes():
            self.config["notebook_content"] = text.toPlainText()
            save_json(CONFIG, self.config)
            QMessageBox.information(dlg, "已保存", "笔记已保存。")
        btn = QPushButton("保存")
        btn.clicked.connect(save_notes)
        t1l.addWidget(btn)
        tabs.addTab(tab1, "笔记")
        # Tab 2: Wordbook
        tab2 = QWidget()
        t2l = QVBoxLayout(tab2)
        hint = QLabel("可手动添加或导入 TXT / CSV / XLSX / DOCX 单词表；没导入时会自动使用考研词汇库。")
        hint.setObjectName("hint")
        hint.setWordWrap(True)
        t2l.addWidget(hint)
        hf = QHBoxLayout()
        hf.addWidget(QLabel("单词:"))
        we = QLineEdit()
        hf.addWidget(we)
        hf.addWidget(QLabel("释义:"))
        me = QLineEdit()
        hf.addWidget(me)
        t2l.addLayout(hf)
        wl = QListWidget()
        t2l.addWidget(wl)
        state = {"words": ensure_wordbook_migrated(self.config)}
        def refresh_words():
            custom_words = load_wordbook()
            state["words"] = custom_words
            visible_words = custom_words or exam_word_entries()[:120]
            wl.clear()
            if not custom_words:
                wl.addItem("当前没有自定义词库，下面预览的是自动词库。")
            for w in visible_words:
                wl.addItem(f"{w['word']}  — {w['meaning']}")
        def add_word():
            w = we.text().strip()
            m = me.text().strip()
            item = build_wordbook_item(w, m, source="manual")
            if not item:
                QMessageBox.warning(dlg, "无法添加", "请填写英文单词。")
                return
            result = merge_wordbook_entries([item])
            we.clear()
            me.clear()
            refresh_words()
            if result["duplicate"]:
                QMessageBox.information(dlg, "已更新", "这个单词已存在，已移到前面并更新释义。")
        def del_word():
            row = wl.currentRow()
            if row >= 0 and row < len(state["words"]):
                del state["words"][row]
                save_wordbook(state["words"])
                refresh_words()
        def show_words_now():
            self.open_word_popup()
        def import_words():
            path, _ = QFileDialog.getOpenFileName(
                dlg,
                "导入单词文件",
                str(BASE),
                "Word files (*.txt *.csv *.xlsx *.docx)",
            )
            if not path:
                return
            try:
                items, failed = parse_wordbook_file(path)
                result = merge_wordbook_entries(items) if items else {"added": 0, "duplicate": 0, "total": 0}
            except Exception as exc:
                QMessageBox.warning(dlg, "导入失败", f"无法识别这个文件：{exc}")
                return
            refresh_words()
            QMessageBox.information(
                dlg,
                "导入完成",
                f"新增 {result['added']} 个，重复跳过 {result['duplicate']} 个，无法识别 {failed} 行。",
            )
        hb = QHBoxLayout()
        popup_btn = QPushButton("弹出一批")
        popup_btn.clicked.connect(show_words_now)
        hb.addWidget(popup_btn)
        import_btn = QPushButton("导入单词文件")
        import_btn.clicked.connect(import_words)
        hb.addWidget(import_btn)
        ab = QPushButton("添加")
        ab.clicked.connect(add_word)
        hb.addWidget(ab)
        db = QPushButton("删除")
        db.clicked.connect(del_word)
        hb.addWidget(db)
        t2l.addLayout(hb)
        refresh_words()
        tabs.addTab(tab2, "单词本")
        dlg.exec()

    def open_formula_search(self):
        if not self.require_feature("FormulaFeatureEnabled"):
            return
        dlg = QDialog(self)
        dlg.setWindowFlags(Qt.Dialog | Qt.WindowStaysOnTopHint)
        dlg.setWindowTitle("考研数学公式速查")
        dlg.resize(760, 560)
        dlg.setStyleSheet(APP_DIALOG_STYLE)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        formulas = math_formula_entries()

        header = QLabel("考研数学公式速查")
        header.setObjectName("title")
        layout.addWidget(header)
        hint = QLabel("输入关键词搜索，或在左侧点分类查看。")
        hint.setObjectName("hint")
        layout.addWidget(hint)

        se = QLineEdit()
        se.setPlaceholderText("搜索公式，如：积分、导数、泰勒、矩阵、概率、特征值、二次型")
        layout.addWidget(se)

        body = QHBoxLayout()
        body.setSpacing(10)
        layout.addLayout(body, 1)

        clb = QListWidget()
        clb.setMinimumWidth(210)
        clb.setMaximumWidth(260)
        body.addWidget(clb)

        ta = QPlainTextEdit()
        ta.setReadOnly(True)
        ta.setFont(QFont("Consolas", 12))
        ta.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        body.addWidget(ta, 1)

        state = {"updating": False, "visible": formulas}

        def render_formula(name, formula):
            ta.setPlainText(f"【{name}】\n\n{formula}")

        def fill_list(items):
            state["updating"] = True
            clb.clear()
            for name, _formula in items:
                clb.addItem(name)
            state["visible"] = items
            state["updating"] = False

        def do_search(text):
            q = (text or "").strip().lower()
            results = formulas if not q else [(n, f) for n, f in formulas if q in n.lower() or q in f.lower()]
            fill_list(results)
            if results:
                clb.setCurrentRow(0)
                render_formula(*results[0])
            else:
                ta.setPlainText(f"未找到与「{text.strip()}」相关的公式")

        def on_cat(row):
            if state["updating"] or row < 0 or row >= len(state["visible"]):
                return
            render_formula(*state["visible"][row])

        se.textChanged.connect(do_search)
        clb.currentRowChanged.connect(on_cat)
        fill_list(formulas)
        if formulas:
            clb.setCurrentRow(0)
            render_formula(*formulas[0])
        se.setFocus()
        dlg.exec()


    def open_word_popup(self):
        if not self.require_feature("word_popup_enabled"):
            return
        self.show_word_popup(force=True)

    def show_word_popup(self, force=False):
        if not feature_enabled(self.config, "word_popup_enabled") or self.should_suppress_bubble():
            return
        if self.word_dialog is not None:
            self.word_dialog.hide()
        if not force and random.random() < 0.35:
            self.bubble.set_click_callback(None)
            line = random.choice(
                [
                    "我在旁边陪你，累了就看一眼单词。",
                    "别急，今天背五个也算前进。",
                    "顺手复习一下，别让单词偷偷溜走。",
                    "我偶尔会冒出来报几个词，点我也能换。",
                ]
            )
            self.bubble.say(line, ms=9000)
        else:
            words = exam_word_entries()
            if not words:
                self.bubble.set_click_callback(None)
                self.bubble.say("考研词汇库没有可用单词。")
                return
            candidates = random.sample(words, min(len(words), 10))
            picked = []
            total_chars = len("考研英语词汇  单击换一批\n")
            for item in candidates:
                line = f"{item['word']}  {item['meaning']}"
                projected = total_chars + len(line) + 1
                if picked and (len(picked) >= 5 or (len(picked) >= 3 and projected > 230)):
                    break
                picked.append(item)
                total_chars = projected
            if not picked:
                picked = candidates[:1]
            word_lines = [f"{item['word']}  {item['meaning']}" for item in picked]
            text = "考研英语词汇  单击换一批\n" + "\n".join(word_lines)
            self.bubble.say(text, ms=30000, fixed_size=(440, 0), avoid_pet_center_tail=True)
            self.bubble.set_click_callback(lambda: self.show_word_popup(force=True))
            self.bubble.setCursor(Qt.PointingHandCursor)
        if hasattr(self, "_word_timer") and self._word_timer:
            self._word_timer.stop()
            self._word_timer.start(random.randint(240000, 480000))

    def _show_word_popup(self):
        self.show_word_popup(force=False)

    def toggle_word_popup(self):
        enabled = not self.config.get("word_popup_enabled", True)
        self.config["word_popup_enabled"] = enabled
        save_json(CONFIG, self.config)
        status = "已开启" if enabled else "已关闭"
        self.bubble.say(f"单词弹窗 {status}")
        if enabled:
            if self.config.get("BubbleEnabled", True):
                self._word_timer.start(30000)
        else:
            if self.word_dialog is not None:
                self.word_dialog.hide()
            self.bubble.set_click_callback(None)
            self._word_timer.stop()


    def restart_pet(self):
        self.save_window_position()
        self.force_quit = True
        self.bubble.hide()
        if self.tray:
            self.tray.hide()
        self.close()
        subprocess.Popen([sys.executable, __file__])
        QApplication.quit()

    def exit_pet(self):
        self.force_quit = True
        self.bubble.hide()
        if self.tray:
            self.tray.hide()
        self.close()
        QApplication.quit()

    def closeEvent(self, event):
        self.save_window_position()
        if self.startup_worker and self.startup_worker.isRunning():
            self.startup_worker.wait(1200)
        self.bubble.hide()
        write_shutdown_flag()
        super().closeEvent(event)

    def open_menu(self):
        try:
            menu = PetSmartMenu(self)
            menu.adjustSize()
            cursor = QCursor.pos()
            screen = QApplication.screenAt(cursor) or QApplication.primaryScreen()
            bounds = screen.availableGeometry() if screen else QRect(0, 0, 1280, 720)
            max_width = max(260, bounds.width() - 24)
            max_height = max(260, bounds.height() - 24)
            if menu.width() > max_width or menu.height() > max_height:
                menu.resize(min(menu.width(), max_width), min(menu.height(), max_height))
            max_x = max(bounds.left(), bounds.right() - menu.width() + 1)
            max_y = max(bounds.top(), bounds.bottom() - menu.height() + 1)
            x = min(max(cursor.x() + 12, bounds.left()), max_x)
            y = min(max(cursor.y() + 12, bounds.top()), max_y)
            menu.move(x, y)
            self._smart_menu = menu
            QTimer.singleShot(0, lambda m=menu: (m.raise_(), m.activateWindow()))
            menu.exec()
            self._smart_menu = None
        except Exception as exc:
            append_runtime_log(f"smart menu failed: {type(exc).__name__}: {exc}")
            self.open_fallback_menu()

    def open_fallback_menu(self):
        menu = QMenu(self)
        bubble_label = "关气泡" if self.config.get("BubbleEnabled", True) else "开气泡"
        actions = [
            ("功能开关", self.open_feature_switch),
            (bubble_label, self.toggle_bubble_enabled),
            ("单词开关", self.toggle_word_popup),
            ("设置", self.open_settings),
            ("重启", self.restart_pet),
            ("退出", self.exit_pet),
        ]
        for label, fn in actions:
            action = QAction(label, menu)
            action.triggered.connect(lambda _checked=False, callback=fn: callback())
            menu.addAction(action)
        menu.exec(QCursor.pos())

    def set_bubble_enabled(self, enabled, announce=True):
        enabled = bool(enabled)
        self.config["BubbleEnabled"] = enabled
        save_json(CONFIG, self.config)
        if enabled:
            if feature_enabled(self.config, "word_popup_enabled") and hasattr(self, "_word_timer") and self._word_timer:
                if not self._word_timer.isActive():
                    self._word_timer.start(30000)
            if announce:
                self.bubble.say("气泡已开启。")
            return
        if hasattr(self, "_word_timer") and self._word_timer:
            self._word_timer.stop()
        self.hide_bubble_now()

    def toggle_bubble_enabled(self):
        self.set_bubble_enabled(not self.config.get("BubbleEnabled", True))

    def close_current_bubble(self):
        self.set_bubble_enabled(False, announce=False)

    def feature_disabled_notice(self, key):
        self.bubble.say(f"{feature_display_label(key, self.config)} 已在功能开关里关闭。")

    def require_feature(self, key):
        if feature_enabled(self.config, key):
            return True
        self.feature_disabled_notice(key)
        return False

    def apply_feature_switch_changes(self):
        sync_startup_entry(self.config)
        sync_watchdog(self.config)
        self.sync_health_timer()
        if hasattr(self, "weather_timer"):
            if feature_enabled(self.config, "WeatherFeatureEnabled"):
                if not self.weather_timer.isActive():
                    self.weather_timer.start(30 * 60 * 1000)
            else:
                self.weather_timer.stop()
        if hasattr(self, "mail_timer"):
            if feature_enabled(self.config, "MailFeatureEnabled"):
                if not self.mail_timer.isActive():
                    self.mail_timer.start(5 * 60 * 1000)
            else:
                self.mail_timer.stop()
        if hasattr(self, "_word_timer") and self._word_timer:
            if feature_enabled(self.config, "word_popup_enabled") and self.config.get("BubbleEnabled", True):
                if not self._word_timer.isActive():
                    self._word_timer.start(30000)
            else:
                self._word_timer.stop()
                self.bubble.set_click_callback(None)
                if self.word_dialog is not None:
                    self.word_dialog.hide()
        if not self.config.get("BubbleEnabled", True):
            self.hide_bubble_now()
        if (
            getattr(self, "auto_hidden_by_context", False)
            and not feature_enabled(self.config, "AutoHideFullscreen")
            and not feature_enabled(self.config, "AutoHideGames")
        ):
            self.restore_from_tray(say=False, activate=False)
        self.update_status()

    def open_feature_switch(self):
        FeatureSwitchDialog(self.config, self).exec()

    def open_ai(self):
        if not self.require_feature("AiFeatureEnabled"):
            return
        AiDialog(self.config, self).exec()

    def open_today_board(self):
        if not self.require_feature("TodayFeatureEnabled"):
            return
        TodayBoardDialog(self).exec()

    def open_translate(self):
        if not self.require_feature("TranslateFeatureEnabled"):
            return
        TranslateDialog(self.config, self).exec()

    def open_clipboard(self):
        if not self.require_feature("ClipboardHistoryEnabled"):
            return
        ClipboardDialog(self).exec()

    def open_action_lab(self):
        if not self.require_feature("ActionLabFeatureEnabled"):
            return
        ActionLabDialog(self).exec()

    def open_diagnostics(self):
        if not self.require_feature("DiagnosticsFeatureEnabled"):
            return
        DiagnosticsDialog(self.config, self).exec()

    def open_performance(self):
        if not self.require_feature("PerformanceFeatureEnabled"):
            return
        PerformanceDialog(self).exec()

    def open_battery(self):
        if not self.require_feature("BatteryFeatureEnabled"):
            return
        BatteryDialog(self.config, self).exec()

    def open_desktop_organizer(self):
        if not self.require_feature("DesktopOrganizerFeatureEnabled"):
            return
        dlg = PerformanceDialog(self)
        dlg.scan_desktop_organize()
        dlg.exec()

    def open_file_search(self):
        if not self.require_feature("FileSearchFeatureEnabled"):
            return
        FileSearchDialog(self).exec()

    def open_core_toolbox(self):
        if not self.require_feature("ToolboxFeatureEnabled"):
            return
        if self.toolbox_worker and self.toolbox_worker.isRunning():
            self.bubble.say("核心工具箱正在打开，稍等一下。")
            return
        self.bubble.say("正在打开核心工具箱。")
        self.toolbox_worker = AssistantToolboxWorker(self)
        self.toolbox_worker.result.connect(self.finish_open_core_toolbox)
        self.toolbox_worker.finished.connect(lambda: setattr(self, "toolbox_worker", None))
        self.toolbox_worker.start()

    def finish_open_core_toolbox(self, ok, message):
        if not ok:
            QMessageBox.information(self, "核心工具箱", message)
            return
        open_in_edge(ASSISTANT_TOOLBOX_URL)
        self.bubble.say(message + "，已打开核心工具箱。")

    def open_claude_code(self):
        if not self.require_feature("ClaudeFeatureEnabled"):
            return
        ClaudeCodeLauncherDialog(self.config, self).exec()

    def open_calendar(self):
        if not self.require_feature("CalendarFeatureEnabled"):
            return
        CalendarDialog(self).exec()

    def open_mail(self):
        if not self.require_feature("MailFeatureEnabled"):
            return
        MailDialog(self.config, self).exec()

    def open_weather(self):
        if not self.require_feature("WeatherFeatureEnabled"):
            return
        WeatherDialog(self.config, self).exec()

    def open_help(self):
        HelpDialog(self).exec()

    def capture_clipboard(self):
        if not feature_enabled(self.config, "ClipboardHistoryEnabled"):
            return
        text = QApplication.clipboard().text()
        normalized = normalize_clipboard_text(text)
        if not normalized or normalized == self.clipboard_last_text:
            return
        if self.clipboard_ignore_once and normalized == self.clipboard_ignore_once:
            self.clipboard_ignore_once = ""
            self.clipboard_last_text = normalized
            return
        self.clipboard_last_text = normalized
        add_clipboard_record(normalized)

    def open_settings(self):
        dlg = SettingsDialog(self.config, self)
        if dlg.exec():
            self.reload_after_restore()

    def open_appearance_debug(self):
        dlg = AppearanceDebugDialog(self.config, self)
        if dlg.exec():
            self.config.update(dlg.config)
            self.apply_text_styles(self.config)

    def pet_visual_rect(self):
        if not hasattr(self, "sprite"):
            return self.frameGeometry()
        pixmap = self.sprite.pixmap()
        if pixmap is None or pixmap.isNull():
            top_left = self.sprite.mapToGlobal(self.sprite.rect().topLeft())
            return QRect(top_left, self.sprite.size())
        local_x = max(0, (self.sprite.width() - pixmap.width()) // 2)
        local_y = max(0, (self.sprite.height() - pixmap.height()) // 2)
        top_left = self.sprite.mapToGlobal(QPoint(local_x, local_y))
        return QRect(top_left, pixmap.size())

    def position_bubble(self):
        if not hasattr(self, "bubble"):
            return
        offset_x, offset_y = bubble_offset(self.config)
        width = max(self.bubble.width(), 1)
        height = max(self.bubble.height(), 1)
        target_rect = self.pet_visual_rect()
        avoid_center_tail = bool(getattr(self.bubble, "avoid_pet_center_tail", False))
        side_hint = -1 if offset_x < 0 else 1
        target_x = pet_bubble_anchor_x(target_rect, avoid_center_tail, side_hint)
        desired_x = target_x - width // 2 + offset_x
        desired_y = target_rect.top() + offset_y - height
        x = desired_x
        y = desired_y
        screen = QApplication.screenAt(target_rect.center()) or QApplication.primaryScreen()

        if screen:
            bounds = screen.availableGeometry()
            screen_left = bounds.left()
            screen_right = max(screen_left, bounds.right() - width + 1)
            min_tip, max_tip = bubble_tail_tip_bounds(width, self.config)
            aligned_left = target_x - max_tip
            aligned_right = target_x - min_tip
            valid_left = max(screen_left, aligned_left)
            valid_right = min(screen_right, aligned_right)
            if valid_left <= valid_right:
                x = min(max(desired_x, valid_left), valid_right)
            else:
                x = min(max(desired_x, screen_left), screen_right)
            screen_top = bounds.top()
            screen_bottom = max(screen_top, bounds.bottom() - height + 1)
            y = min(max(desired_y, screen_top), screen_bottom)

        local_tip_x = bubble_tail_tip_x(width, self.config, target_x=target_x - x)
        self.bubble.tail_tip_x = local_tip_x
        self.bubble.tail_side = "left" if local_tip_x <= width // 2 else "right"
        self.bubble.update()
        self.bubble.move(x, y)

    def position_word_dialog(self):
        if self.word_dialog is None:
            return
        width = max(self.word_dialog.width(), self.word_dialog.sizeHint().width(), 300)
        height = max(self.word_dialog.height(), self.word_dialog.sizeHint().height(), 210)
        pet_rect = self.frameGeometry().adjusted(-8, -8, 8, 8)
        screen = QApplication.screenAt(pet_rect.center()) or QApplication.primaryScreen()
        if not screen:
            return
        bounds = screen.availableGeometry()
        margin = 14

        def clamp_to_screen(candidate_x, candidate_y):
            return (
                min(max(candidate_x, bounds.left()), bounds.right() - width + 1),
                min(max(candidate_y, bounds.top()), bounds.bottom() - height + 1),
            )

        candidates = [
            (pet_rect.right() + margin, pet_rect.top()),
            (pet_rect.left() - width - margin, pet_rect.top()),
            (pet_rect.center().x() - width // 2, pet_rect.top() - height - margin),
            (pet_rect.center().x() - width // 2, pet_rect.bottom() + margin),
        ]
        for candidate_x, candidate_y in candidates:
            candidate_x, candidate_y = clamp_to_screen(candidate_x, candidate_y)
            if not QRect(candidate_x, candidate_y, width, height).intersects(pet_rect):
                self.word_dialog.move(candidate_x, candidate_y)
                return
        x, y = clamp_to_screen(pet_rect.right() + margin, pet_rect.top())
        self.word_dialog.move(x, y)

    def save_bubble_position(self):
        pet_rect = self.pet_visual_rect()
        offset_x = self.bubble.x() + self.bubble.width() // 2 - pet_rect.center().x()
        offset_y = self.bubble.y() + self.bubble.height() - pet_rect.top()
        update_saved_bubble_offset(self.config, offset_x, offset_y)

    def save_window_position(self):
        pos = self.pos()
        anchor = getattr(self, "position_save_anchor", None)
        if self.config.get("LockPetPosition", True) and isinstance(anchor, QPoint) and not self.dragging:
            pos = anchor
        safe = self.clamped_pos(pos)
        if safe != self.pos():
            self.move(safe)
        if self.config.get("LockPetPosition", True) and isinstance(anchor, QPoint) and not self.dragging:
            self.position_save_anchor = QPoint(safe)
        self.config["WindowLeft"] = safe.x()
        self.config["WindowTop"] = safe.y()
        save_json(CONFIG, self.config)

    def save_bubble_size(self):
        update_saved_bubble_size(self.config, self.bubble.width(), self.bubble.height())

    def moveEvent(self, event):
        super().moveEvent(event)
        if hasattr(self, "bubble") and self.bubble.isVisible() and not getattr(self.bubble, "_dragging_bubble", False):
            self.position_bubble()

    def update_desktop_label_bounds(self, style_config=None):
        style_config = style_config or self.config
        pet_size = int(self.config.get("PetSize", 230))
        font_size = text_font_sizes(style_config)["desktop"]
        self.status.setMinimumWidth(max(210, pet_size - 18, font_size * 18))
        self.status.setMaximumWidth(max(260, pet_size + 70, font_size * 34))

    def apply_text_styles(self, style_config=None):
        style_config = style_config or self.config
        set_active_text_config(style_config)
        self.bubble.apply_font_config(style_config)
        self.accessory.setStyleSheet(desktop_label_style(style_config, "accessory"))
        self.status.setStyleSheet(desktop_label_style(style_config))
        self.update_desktop_label_bounds(style_config)
        self.accessory.adjustSize()
        self.status.adjustSize()
        if self.bubble.isVisible():
            self.position_bubble()

    def reload_after_restore(self):
        self.config = load_config()
        self.apply_text_styles()
        sync_startup_entry(self.config)
        sync_watchdog(self.config)
        self.sprite.config = self.config
        self.sprite.load_image()
        self.setWindowOpacity(float(self.config.get("Opacity", 1)))
        self.adjustSize()
        self.refresh_growth_state(show_new=False)
        self.sync_health_timer()
        self.update_status()
        self.refresh_tray_labels()
        self.apply_feature_switch_changes()

    def apply_natural_setting_effects(self, changed_keys):
        changed_keys = set(changed_keys or [])
        style_keys = set(TEXT_STYLE_KEYS) | set(BUBBLE_COLOR_KEYS) | set(BUBBLE_FRAME_KEYS)
        sprite_keys = {"PetSize", "PetImagePath", "ActionPackPath"}
        if "Opacity" in changed_keys:
            self.setWindowOpacity(float(self.config.get("Opacity", 1)))
        if "Topmost" in changed_keys:
            self.refresh_window_flags()
        if sprite_keys & changed_keys:
            self.sprite.config = self.config
            self.sprite.load_image()
            self.adjustSize()
            self.ensure_safe_window_position(save=True)
        if style_keys & changed_keys:
            self.apply_text_styles(self.config)
        elif {"BubbleOffsetX", "BubbleOffsetY"} & changed_keys and self.bubble.isVisible():
            self.position_bubble()
        if "WeatherCity" in changed_keys:
            self.weather_text = f"{self.config.get('WeatherCity', '上海')} 天气读取中"
        self.refresh_tray_labels()
        self.apply_feature_switch_changes()
        if "WeatherCity" in changed_keys:
            self.refresh_weather(show_bubble=False)

    def try_apply_natural_settings(self, text):
        result = parse_natural_setting_changes(
            text,
            self.config,
            pet_name=str(self.config.get("PetName") or DEFAULT_CONFIG["PetName"]),
        )
        if not result.get("handled"):
            return ""
        changed_keys = set(result.get("changed_keys") or [])
        if changed_keys:
            self.config.update(result.get("config") or {})
            save_json(CONFIG, self.config)
            self.apply_natural_setting_effects(changed_keys)
        pet_name = str(self.config.get("PetName") or DEFAULT_CONFIG["PetName"])
        lines = []
        if result.get("notes"):
            lines.append(f"{pet_name}已帮你改好设置：")
            lines.extend(f"- {note}" for note in result["notes"])
        if result.get("noops") and not result.get("notes"):
            lines.append("这些设置本来就是这样：")
            lines.extend(f"- {note}" for note in result["noops"][:5])
        if result.get("blocked"):
            lines.append("这些项目没有通过聊天修改：")
            lines.extend(f"- {note}" for note in result["blocked"])
        if not lines:
            return ""
        answer = "\n".join(lines)
        if changed_keys and self.config.get("BubbleEnabled", True):
            self.bubble.say("设置已改好：\n" + "\n".join(result.get("notes", [])[:3]), ms=6500)
        return answer

    def open_todos(self):
        if not self.require_feature("TodoFeatureEnabled"):
            return
        TodoDialog(self).exec()

    def try_add_natural_reminder(self, text):
        parsed = parse_natural_reminder(text)
        if not parsed:
            return ""
        todos = load_json(TODOS, [])
        todos.append(build_todo_item(parsed["title"], parsed["remind_at"]))
        save_json(TODOS, todos)
        note = f"{parsed['title']}  {parsed['remind_at']}"
        self.bubble.say(f"已添加提醒：\n{note}")
        return note

    def study_summary(self):
        if not self.require_feature("StudyFeatureEnabled"):
            return
        StudyDialog(self.config, self).exec()

    def start_focus_session(self):
        if not self.require_feature("StudyFeatureEnabled"):
            return
        if self.focus_active:
            self.bubble.say(self.focus_status_text())
            self.dog_reading()
            return
        minutes = int(self.config.get("FocusMinutes", 50))
        subject = self.config.get("Subject", "高数")
        self.focus_active = True
        self.focus_phase = "study"
        self.focus_started_at = datetime.now()
        self.focus_total_minutes = minutes
        self.focus_rest_minutes = int(self.config.get("RestMinutes", 10))
        self.focus_subject = subject
        self.focus_last_minute = -1
        self.state = "学习陪伴"
        self.update_status()
        self.dog_reading()
        self.bubble.say(f"陪读开始：{subject} {minutes} 分钟。糯米坐好陪你。")
        self.speak("陪读开始。", kind="interaction")
        self.focus_timer.start()

    def focus_elapsed_minutes(self):
        if not self.focus_started_at:
            return 0
        return max(0, int((datetime.now() - self.focus_started_at).total_seconds() // 60))

    def focus_status_text(self):
        if not self.focus_active:
            return "当前没有陪读中的番茄钟。"
        elapsed = self.focus_elapsed_minutes()
        if self.focus_phase == "study":
            return f"陪读中：{self.focus_subject} {elapsed}/{self.focus_total_minutes} 分钟"
        return f"休息中：{elapsed}/{self.focus_rest_minutes} 分钟"

    def update_focus_session(self):
        if not self.focus_active:
            self.focus_timer.stop()
            return
        elapsed = self.focus_elapsed_minutes()
        self.update_status()
        if self.focus_phase == "study":
            if elapsed != self.focus_last_minute and elapsed > 0 and (elapsed in (1, 5, 15, 30) or elapsed % 10 == 0):
                self.focus_last_minute = elapsed
                self.state = "学习陪伴"
                self.dog_reading()
                self.bubble.say(f"已学习 {elapsed} 分钟。继续稳住。")
            if elapsed >= self.focus_total_minutes:
                self.finish_focus_study()
            return
        if elapsed != self.focus_last_minute and elapsed > 0 and (elapsed == 1 or elapsed % 5 == 0):
            self.focus_last_minute = elapsed
            self.bubble.say("休息一下，喝点水吧。")
        if elapsed >= self.focus_rest_minutes:
            self.focus_active = False
            self.focus_timer.stop()
            self.react("开心", "休息结束啦。下一轮想开始时再叫我。", voice_kind="reminder")

    def finish_focus_study(self):
        logs = load_json(STUDY, [])
        logs.append(
            {
                "at": datetime.now().isoformat(timespec="seconds"),
                "subject": self.focus_subject,
                "minutes": self.focus_total_minutes,
                "mode": "学习",
            }
        )
        save_json(STUDY, logs)
        memory = load_pet_memory()
        memory["last_focus_completed_at"] = datetime.now().isoformat(timespec="seconds")
        save_pet_memory(memory)
        self.focus_phase = "rest"
        self.focus_started_at = datetime.now()
        self.focus_last_minute = -1
        self.refresh_growth_state(show_new=True)
        self.react(
            "开心",
            f"这一轮结束啦，已记录 {self.focus_subject} {self.focus_total_minutes} 分钟。喝点水吧。",
            voice_kind="reminder",
        )

    def refresh_weather(self, show_bubble=False):
        if not feature_enabled(self.config, "WeatherFeatureEnabled"):
            return
        if self.weather_worker and self.weather_worker.isRunning():
            return
        city = self.config.get("WeatherCity", "上海") or "上海"
        if show_bubble:
            self.bubble.say(f"正在刷新 {city} 天气...")
        self.weather_worker = WeatherWorker(city)
        self.weather_worker.result.connect(lambda text: self.set_weather(text, show_bubble))
        self.weather_worker.start()

    def set_weather(self, text, show_bubble=False):
        self.weather_text = text
        self.update_status()
        if show_bubble:
            self.bubble.say(weather_card_text(text))
        self.check_weather_mood(text)

    def sync_health_timer(self):
        if self.config.get("SystemHealthWatchEnabled", True):
            if not self.health_timer.isActive():
                self.health_timer.start()
        else:
            self.health_timer.stop()

    def check_system_health(self):
        if not self.config.get("SystemHealthWatchEnabled", True):
            return
        snapshot = system_health_snapshot(self.config)
        active_keys = {key for key, _text in snapshot["issues"]}
        for key in list(self.health_bad_counts):
            if key not in active_keys:
                self.health_bad_counts[key] = 0

        now = time.time()
        cooldown = max(180, int(self.config.get("HealthAlertCooldownMinutes", 15)) * 60)
        alerts = []
        for key, text in snapshot["issues"]:
            self.health_bad_counts[key] = self.health_bad_counts.get(key, 0) + 1
            required_hits = 2 if key == "cpu" else 1
            if self.health_bad_counts[key] < required_hits:
                continue
            key_cooldown = max(cooldown, 60 * 60) if key == "battery_full" else cooldown
            if now - self.health_last_alert.get(key, 0) < key_cooldown:
                continue
            self.health_last_alert[key] = now
            alerts.append((key, text))

        if alerts:
            memory = load_pet_memory()
            memory["health_last_alert"] = self.health_last_alert
            save_pet_memory(memory)

        if not alerts:
            return
        message = "电脑状态提醒\n" + "\n".join(f"- {text}" for _key, text in alerts)
        if any(key == "battery_low" for key, _text in alerts):
            self.notify_due_reminder("低电量提醒", message, QSystemTrayIcon.Warning, 12000)
            return
        append_runtime_log(message.replace("\n", "；"))
        if self.tray and not self.isVisible():
            self.tray.showMessage(
                self.config.get("PetName", "糯米"),
                message,
                QSystemTrayIcon.Warning,
                9000,
            )
        self.state = "提醒"
        self.update_status()
        self.bubble.say(message, 12000)

    def notify_due_reminder(self, title, message, icon=QSystemTrayIcon.Information, duration=12000):
        text = str(message or "").strip()
        if not text:
            return
        append_runtime_log(f"{title}: {text.replace(chr(10), '；')}")
        if self.tray:
            self.tray.showMessage(
                title,
                text,
                icon,
                duration,
            )
        self.react("提醒", text, voice_kind="reminder")

    def update_status(self):
        icon = {
            "待机": "😺",
            "开心": "😺",
            "学习陪伴": "📚",
            "睡觉": "💤",
            "提醒": "😲",
            "惊讶": "😲",
            "趴下": "💤",
            "好奇": "👀",
            "闻一闻": "🐾",
            "散步": "🐾",
            "伸懒腰": "😺",
            "发呆": "💭",
            "思考": "💭",
        }.get(self.state, "😺")
        if self.focus_active:
            self.status.setText(f"{self.config.get('PetName', '糯米')}  {icon}  {self.focus_status_text()}")
        else:
            self.status.setText(f"{self.config.get('PetName', '糯米')}  {icon}  {self.state}")
        self.status.setVisible(bool(self.config.get("ShowStatus", False)))

    def on_tick(self):
        self.idle_seconds += 1
        if self.idle_seconds % 30 == 0:
            self.check_presence_reaction()
        if self.idle_seconds % 240 == 0:
            self.check_environment_mood()
        if self.idle_seconds % 300 == 0:
            self.check_sleep_mood()
            self.check_daily_summary()
            self.check_exam_event()
        if self.idle_seconds == 300:
            self.react("睡觉", "我先眯一会儿，有事叫我。")
        if self.idle_seconds % 7 == 0:
            self.sprite.setGraphicsEffect(None)

    def check_holiday_reminder(self):
        info = next_holiday_info()
        if not info:
            return
        state = load_json(MAIL_STATE, {})
        today = datetime.now().date().isoformat()
        key = f"{today}:{info['name']}"
        if state.get("holiday_reminder_key") == key:
            return
        state["holiday_reminder_key"] = key
        save_json(MAIL_STATE, state)
        self.react("提醒", f"节假日提醒：{next_holiday_text()}")

    def check_due_reminders(self):
        if feature_enabled(self.config, "CalendarFeatureEnabled"):
            self.check_calendar_reminders()
        if feature_enabled(self.config, "TodoFeatureEnabled"):
            self.check_todo_reminders()

    def check_calendar_reminders(self):
        events = load_json(CALENDAR, [])
        now = datetime.now()
        for ev in events:
            try:
                at = datetime.strptime(ev.get("at", ""), "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            delta = at - now
            if timedelta(minutes=0) <= delta <= timedelta(minutes=15) and not ev.get("reminded"):
                ev["reminded"] = True
                self.notify_due_reminder("日程提醒", f"{ev.get('at')} 有安排：{ev.get('title')}")
                save_json(CALENDAR, events)
                break

    def check_todo_reminders(self):
        todos = load_json(TODOS, [])
        now = datetime.now()
        due = []
        changed = False
        for todo in todos:
            if todo.get("done") or todo.get("reminded"):
                continue
            remind_at = todo.get("remind_at", "")
            if not remind_at:
                continue
            at = parse_local_minutes(remind_at)
            if not at or at > now:
                continue
            todo["reminded"] = True
            changed = True
            due.append(todo)
        if changed:
            save_json(TODOS, todos)
        if not due:
            return
        lines = ["提醒事项："]
        for todo in due[:3]:
            lines.append(f"- {todo.get('title', '')}")
        if len(due) > 3:
            lines.append(f"还有 {len(due) - 3} 项也到时间了")
        self.notify_due_reminder("提醒事项", "\n".join(lines), QSystemTrayIcon.Warning)

    def check_mail(self):
        if not feature_enabled(self.config, "MailFeatureEnabled"):
            return
        if self.mail_worker and self.mail_worker.isRunning():
            return
        self.mail_worker = MailWorker(self.config)
        self.mail_worker.result.connect(self.announce_mail)
        self.mail_worker.start()

    def announce_mail(self, text):
        if not text or not text.strip():
            return
        if self.is_quiet():
            return
        self.bubble.say(text, 9000)
        self.speak(text.splitlines()[0] if text else "", kind="ambient")

    def ocr_screenshot(self):
        if not self.require_feature("OcrFeatureEnabled"):
            return
        if self.ocr_worker and self.ocr_worker.isRunning():
            self.bubble.say("OCR 正在识别上一张截图，稍等一下。")
            return
        self.bubble.hide()
        self.hide()
        QApplication.processEvents()
        snip = SnipDialog()
        if snip.exec() != QDialog.Accepted or snip.selected.width() < 8 or snip.selected.height() < 8:
            self.show()
            self.bubble.say("截图已取消。")
            return
        rect = snip.selected
        screen_geo = QApplication.primaryScreen().geometry()
        shot = QApplication.primaryScreen().grabWindow(
            0,
            screen_geo.x() + rect.x(),
            screen_geo.y() + rect.y(),
            rect.width(),
            rect.height(),
        )
        self.show()
        path = SCREENSHOTS / f"screenshot-{datetime.now():%Y%m%d-%H%M%S}.png"
        shot.save(str(path))
        self.bubble.say("截图已保存，正在 OCR 识别。")
        self.ocr_worker = OcrWorker(self.config, path)
        self.ocr_worker.result.connect(self.ocr_screenshot_finished)
        self.ocr_worker.finished.connect(lambda: setattr(self, "ocr_worker", None))
        self.ocr_worker.start()

    def ocr_screenshot_finished(self, result):
        path = result.get("path", "")
        content = result.get("content", "")
        error = result.get("error", "")
        if error and "Tesseract" in error and ("没有配置" in error or "路径" in error):
            self.bubble.say(error)
            return
        dlg = AiDialog(self.config, self)
        if content.strip():
            dlg.input.setPlainText("请结合这张截图 OCR 出来的文字进行解释/总结：\n" + content)
        else:
            dlg.input.setPlainText(error or f"截图已保存到 {path}，但 OCR 没识别出文字。请检查 Tesseract 语言包或截图清晰度。")
        dlg.exec()

    def start_codex(self):
        subprocess.Popen(["codex"], shell=True)
        self.bubble.say("正在启动 Codex。")

    def restart_codex(self):
        for p in psutil.process_iter(["name"]):
            if "codex" in p.info["name"].lower():
                p.kill()
        self.start_codex()


class HotKeyFilter(QAbstractNativeEventFilter):
    def __init__(self, window):
        super().__init__()
        self.window = window
        self.registered = []

    def register(self):
        if user32 is None:
            return
        hwnd = int(self.window.winId())
        combos = [
            (101, MOD_ALT, VK_SPACE),
            (102, MOD_CONTROL | MOD_SHIFT, VK_A),
            (103, MOD_CONTROL | MOD_SHIFT, VK_H),
        ]
        for hotkey_id, modifiers, vk in combos:
            if user32.RegisterHotKey(hwnd, hotkey_id, modifiers, vk):
                self.registered.append(hotkey_id)

    def unregister(self):
        if user32 is None:
            return
        hwnd = int(self.window.winId())
        for hotkey_id in self.registered:
            user32.UnregisterHotKey(hwnd, hotkey_id)

    def nativeEventFilter(self, event_type, message):
        if user32 is None:
            return False, 0
        try:
            msg = ctypes.wintypes.MSG.from_address(int(message))
        except Exception:
            return False, 0
        if msg.message != WM_HOTKEY:
            return False, 0
        hotkey_id = int(msg.wParam)
        if hotkey_id == 101:
            self.window.open_ai()
        elif hotkey_id == 102:
            self.window.ocr_screenshot()
        elif hotkey_id == 103:
            self.window.toggle_visibility()
        return True, 0


def main():
    if not acquire_single_instance():
        request_existing_instance_restore()
        return
    clear_shutdown_flag()
    install_exception_logger()
    app = QApplication(sys.argv)
    install_wheel_value_guard(app)
    app.setQuitOnLastWindowClosed(False)
    win = PetWindow()
    win.show()
    hotkeys = HotKeyFilter(win)
    app.installNativeEventFilter(hotkeys)
    hotkeys.register()
    code = app.exec()
    hotkeys.unregister()
    sys.exit(code)


if __name__ == "__main__":
    update_exit_code = run_update_cli()
    if update_exit_code is None:
        main()
    else:
        sys.exit(update_exit_code)
