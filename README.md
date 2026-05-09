# EPUB 阅读器

一个基于 Python 和 PyQt5 开发的功能丰富的 EPUB 电子书阅读器。

## 功能特性

- 打开和阅读 EPUB 格式电子书
- 暗色/亮色双主题切换（Catppuccin 风格）
- 按 spine 顺序正确加载章节
- 左侧目录导航 + 书签标签页
- 字体大小滑块调节 (10-30px)
- 章节内全文搜索
- 阅读进度条
- 阅读位置自动保存/恢复
- 书签功能（持久化保存）
- 键盘快捷键导航
- 全屏阅读模式 (F11)
- 侧栏开关 (F4)
- 美观的阅读排版样式
- 状态栏显示当前阅读信息

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| Ctrl+O | 打开文件 |
| Ctrl+B | 添加书签 |
| Ctrl+F | 搜索 |
| Left / Right | 上一章 / 下一章 |
| Home / End | 首章 / 末章 |
| F4 | 切换侧栏 |
| F11 | 全屏模式 |
| Esc | 退出全屏 |

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行程序

```bash
python main.py
```

## 技术栈

- **GUI框架**: PyQt5
- **EPUB处理**: ebooklib
- **HTML解析**: BeautifulSoup4 + lxml

## 项目结构

```
epub_reader/
├── main.py           # 程序入口
├── epub_reader.py    # 核心阅读器类
├── requirements.txt  # 依赖文件
└── README.md         # 项目说明
```

## 系统要求

- Python 3.7+
- Windows/macOS/Linux
