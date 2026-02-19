# Multi-Monitor Layout Switcher

Windows 多显示器布局快速切换工具。纯 Python 实现，通过 Win32 CCD API (`SetDisplayConfig`) 保存和恢复显示器配置。

## 使用方法

```bash
python monitor.py show              # 查看所有显示器状态
python monitor.py save <name>       # 保存当前布局
python monitor.py list              # 列出已保存的布局
python monitor.py apply <name>      # 应用已保存的布局
python monitor.py delete <name>     # 删除已保存的布局
```

## 快捷方式

项目包含两个 `.bat` 文件，可右键发送到桌面作为快捷方式：

- `切换Office.bat` — 切换到 office 布局
- `切换Movie.bat` — 切换到 movie 布局

## 依赖

- Python 3.6+
- Windows（使用 ctypes 调用 Win32 API，零第三方依赖）
