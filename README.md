<div align="center">

# EPUB Reader

一款简洁优雅的 EPUB 电子书阅读器，基于 Python 和 PyQt5 构建。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.7+](https://img.shields.io/badge/Python-3.7+-green.svg)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/GUI-PyQt5-41C884.svg)](https://www.riverbankcomputing.com/software/pyqt/)

</div>

---

## 特性

- 支持 EPUB 格式电子书阅读，按 spine 顺序正确加载章节
- 暗色 / 亮色双主题切换（Catppuccin 风格）
- 自定义阅读背景色、字体、字体颜色、大小、行高
- 4 种预设方案：深色、浅色、护眼黄、护眼绿
- EPUB 内嵌图片正确显示
- 章节目录导航与书签
- 弹出式搜索对话框
- 阅读进度自动保存 / 恢复
- 沉浸式全屏阅读模式
- 经典菜单栏界面（文件 / 视图 / 导航 / 工具 / 帮助）
- 丰富的键盘快捷键

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+O` | 打开文件 |
| `Ctrl+F` | 搜索 |
| `Ctrl+B` | 添加书签 |
| `Ctrl+=` / `Ctrl+-` | 放大 / 缩小字体 |
| `←` / `→` | 上一章 / 下一章 |
| `Home` / `End` | 跳到首章 / 末章 |
| `F4` | 切换侧栏 |
| `F11` | 全屏模式 |
| `F12` | 沉浸式阅读 |
| `Esc` | 退出全屏 / 沉浸 |

## 安装

```bash
git clone https://github.com/AlanNiew/epub-reader.git
cd epub-reader
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

1. 点击 **文件 → 打开** 或按 `Ctrl+O` 选择 `.epub` 文件
2. 左侧目录点击章节跳转，或用方向键翻页
3. **视图 → 阅读设置** 自定义阅读体验
4. 按 `F12` 进入沉浸式阅读

## 技术栈

- **GUI**: [PyQt5](https://www.riverbankcomputing.com/software/pyqt/)
- **EPUB 解析**: [ebooklib](https://github.com/aerkalov/ebooklib)
- **HTML 处理**: [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) + [lxml](https://lxml.de/)

## 项目结构

```
epub-reader/
├── main.py            # 程序入口
├── epub_reader.py     # 核心阅读器
├── requirements.txt   # Python 依赖
├── LICENSE            # MIT 许可证
└── README.md
```

## 系统要求

- Python 3.7+
- Windows / macOS / Linux

## License

[MIT](LICENSE) &copy; AlanNiew
