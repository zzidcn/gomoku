# 五子棋 Gomoku

一个用 Python + tkinter 实现的五子棋桌面小游戏，支持双人对战、悔棋、重新开始。

## 功能特性

- 🎮 15×15 标准棋盘
- ⚫⚪ 黑白双方轮流落子
- 🏆 自动判断胜负（五子连珠）
- ↩️ 支持悔棋
- 👁️ 鼠标悬停预览落子位置
- 🔴 最后落子位置标记

## 运行方式

### 方式一：直接运行源码

需要 Python 3.8+（tkinter 为内置库，无需额外安装）

```bash
python gomoku.py
```

### 方式二：运行打包好的 exe

直接双击 `dist/gomoku.exe` 即可，无需安装 Python。

## 打包方法

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name gomoku gomoku.py
```

打包完成后，可执行文件位于 `dist/gomoku.exe`。

## 游戏规则

1. 黑棋先手
2. 双方轮流在棋盘交叉点落子
3. 率先在横、竖、斜任意方向连成五子者获胜

## 项目结构

```
gomoku/
├── gomoku.py       # 游戏主程序
├── README.md       # 说明文档
└── dist/
    └── gomoku.exe  # 打包后的可执行文件
```
