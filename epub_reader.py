import os
import json
import base64
import subprocess
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextBrowser, QListWidget, QFileDialog,
                             QSplitter, QLabel, QMessageBox, QListWidgetItem,
                             QSlider, QProgressBar, QLineEdit, QAction,
                             QMenu, QStatusBar, QShortcut,
                             QTabWidget, QDialog, QFormLayout, QColorDialog,
                             QFontDialog, QDialogButtonBox, QFrame, QCheckBox,
                             QScrollArea, QGridLayout, QSizePolicy, QLayout)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QSettings, pyqtSignal, QRect
from PyQt5.QtGui import (QFont, QIcon, QColor, QPalette, QKeySequence,
                          QPixmap, QPainter, QFontDatabase, QImage)
from PyQt5.QtSvg import QSvgRenderer
from ebooklib import epub
from bs4 import BeautifulSoup
import warnings
from bs4 import XMLParsedAsHTMLWarning
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def create_app_icon():
    svg_data = '''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#89b4fa;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#74c7ec;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="cover" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1e1e2e;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#313244;stop-opacity:1" />
    </linearGradient>
    <linearGradient id="pages" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#cdd6f4;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#bac2de;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect x="20" y="20" width="216" height="216" rx="40" ry="40" fill="url(#bg)"/>
  <rect x="35" y="40" width="170" height="180" rx="8" ry="8" fill="url(#pages)"/>
  <rect x="50" y="35" width="160" height="180" rx="8" ry="8" fill="url(#cover)"/>
  <rect x="68" y="75" width="120" height="8" rx="4" ry="4" fill="#89b4fa" opacity="0.9"/>
  <rect x="68" y="95" width="100" height="6" rx="3" ry="3" fill="#a6adc8" opacity="0.7"/>
  <rect x="68" y="112" width="110" height="6" rx="3" ry="3" fill="#a6adc8" opacity="0.7"/>
  <rect x="68" y="129" width="90" height="6" rx="3" ry="3" fill="#a6adc8" opacity="0.7"/>
  <rect x="68" y="146" width="105" height="6" rx="3" ry="3" fill="#a6adc8" opacity="0.7"/>
  <rect x="68" y="163" width="80" height="6" rx="3" ry="3" fill="#a6adc8" opacity="0.7"/>
  <text x="128" y="210" text-anchor="middle" font-family="sans-serif" font-size="28" font-weight="bold" fill="#89b4fa">EPUB</text>
</svg>'''
    renderer = QSvgRenderer(bytes(svg_data, 'utf-8'))
    icon = QIcon()
    for s in [16, 24, 32, 48, 64, 128, 256]:
        pm = QPixmap(s, s)
        pm.fill(Qt.transparent)
        p = QPainter(pm)
        renderer.render(p)
        p.end()
        icon.addPixmap(pm)
    return icon


DEFAULT_PLACEHOLDER = None


def get_placeholder_cover(w=120, h=160):
    pm = QPixmap(w, h)
    p = QPainter(pm)
    p.fillRect(0, 0, w, h, QColor('#313244'))
    p.setPen(QColor('#89b4fa'))
    f = p.font()
    f.setPixelSize(28)
    f.setBold(True)
    p.setFont(f)
    p.drawText(pm.rect(), Qt.AlignCenter, 'EPUB')
    p.end()
    return pm


def extract_epub_cover(file_path):
    try:
        book = epub.read_epub(file_path)
        for item in book.get_items_of_type(1):
            if 'cover' in item.get_name().lower() or 'cover' in (item.get_id() or '').lower():
                data = item.get_content()
                img = QImage()
                img.loadFromData(data)
                if not img.isNull():
                    return QPixmap.fromImage(img)
        for item in book.get_items_of_type(1):
            mt = item.media_type or ''
            if mt.startswith('image/'):
                data = item.get_content()
                img = QImage()
                img.loadFromData(data)
                if not img.isNull():
                    pm = QPixmap.fromImage(img)
                    if pm.width() > 50 and pm.height() > 50:
                        return pm
    except Exception:
        pass
    return None


def extract_epub_meta(file_path):
    try:
        book = epub.read_epub(file_path)
        title = os.path.splitext(os.path.basename(file_path))[0]
        author = ''
        tm = book.get_metadata('DC', 'title')
        if tm:
            title = tm[0][0] or title
        am = book.get_metadata('DC', 'creator')
        if am:
            author = am[0][0] or ''
        spine = book.spine or []
        chapter_count = 0
        for sid in spine:
            iid = sid[0] if isinstance(sid, (tuple, list)) else sid
            it = book.get_item_with_id(iid)
            if it and it.get_type() == 9:
                chapter_count += 1
        return {'title': title, 'author': author, 'chapters': chapter_count}
    except Exception:
        return {'title': os.path.splitext(os.path.basename(file_path))[0], 'author': '', 'chapters': 0}


STYLESHEET_DARK = """
QMainWindow { background-color: #1e1e2e; }
QWidget { background-color: #1e1e2e; color: #cdd6f4; font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; }
QMenuBar { background-color: #181825; color: #cdd6f4; border-bottom: 1px solid #313244; padding: 4px; font-size: 14px; }
QMenuBar::item { padding: 6px 12px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #313244; }
QMenuBar::item:pressed { background-color: #45475a; }
QPushButton { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 14px; font-size: 13px; min-height: 20px; }
QPushButton:hover { background-color: #45475a; border-color: #585b70; }
QPushButton:pressed { background-color: #585b70; }
QPushButton:disabled { background-color: #1e1e2e; color: #585b70; border-color: #313244; }
QSplitter::handle { background-color: #313244; width: 2px; }
QListWidget { background-color: #181825; color: #cdd6f4; border: 1px solid #313244; border-radius: 8px; padding: 4px; font-size: 13px; outline: none; }
QListWidget::item { padding: 8px 12px; border-radius: 4px; margin: 1px 2px; }
QListWidget::item:selected { background-color: #89b4fa; color: #1e1e2e; }
QListWidget::item:hover { background-color: #313244; }
QTextBrowser { background-color: #1e1e2e; color: #cdd6f4; border: none; padding: 20px; }
QSlider::groove:horizontal { height: 6px; background: #313244; border-radius: 3px; }
QSlider::handle:horizontal { background: #89b4fa; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #89b4fa; border-radius: 3px; }
QProgressBar { background-color: #313244; border-radius: 4px; height: 6px; border: none; }
QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }
QLineEdit { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 10px; font-size: 13px; }
QLineEdit:focus { border-color: #89b4fa; }
QStatusBar { background-color: #181825; color: #a6adc8; font-size: 12px; border-top: 1px solid #313244; }
QLabel { color: #cdd6f4; background: transparent; }
QTabWidget::pane { border: 1px solid #313244; border-radius: 8px; background-color: #181825; }
QTabBar::tab { background-color: #313244; color: #cdd6f4; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #89b4fa; color: #1e1e2e; }
QScrollArea { border: none; background-color: #1e1e2e; }
QScrollBar:vertical { background: #181825; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #45475a; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #585b70; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background: #181825; height: 10px; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #45475a; border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #585b70; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
QMenu { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 8px; padding: 4px; }
QMenu::item { padding: 6px 24px; border-radius: 4px; }
QMenu::item:selected { background-color: #89b4fa; color: #1e1e2e; }
QMenu::item:disabled { color: #585b70; }
QMenu::separator { height: 1px; background: #45475a; margin: 4px 8px; }
QDialog { background-color: #1e1e2e; color: #cdd6f4; }
QCheckBox { color: #cdd6f4; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #45475a; background-color: #313244; }
QCheckBox::indicator:checked { background-color: #89b4fa; border-color: #89b4fa; }
"""

STYLESHEET_LIGHT = """
QMainWindow { background-color: #eff1f5; }
QWidget { background-color: #eff1f5; color: #4c4f69; font-family: 'Microsoft YaHei', 'Segoe UI', sans-serif; }
QMenuBar { background-color: #e6e9ef; color: #4c4f69; border-bottom: 1px solid #ccd0da; padding: 4px; font-size: 14px; }
QMenuBar::item { padding: 6px 12px; border-radius: 4px; }
QMenuBar::item:selected { background-color: #ccd0da; }
QMenuBar::item:pressed { background-color: #bcc0cc; }
QPushButton { background-color: #ccd0da; color: #4c4f69; border: 1px solid #bcc0cc; border-radius: 6px; padding: 6px 14px; font-size: 13px; min-height: 20px; }
QPushButton:hover { background-color: #bcc0cc; border-color: #acb0be; }
QPushButton:pressed { background-color: #acb0be; }
QPushButton:disabled { background-color: #eff1f5; color: #acb0be; border-color: #ccd0da; }
QSplitter::handle { background-color: #ccd0da; width: 2px; }
QListWidget { background-color: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 8px; padding: 4px; font-size: 13px; outline: none; }
QListWidget::item { padding: 8px 12px; border-radius: 4px; margin: 1px 2px; }
QListWidget::item:selected { background-color: #7287fd; color: #eff1f5; }
QListWidget::item:hover { background-color: #ccd0da; }
QTextBrowser { background-color: #eff1f5; color: #4c4f69; border: none; padding: 20px; }
QSlider::groove:horizontal { height: 6px; background: #ccd0da; border-radius: 3px; }
QSlider::handle:horizontal { background: #7287fd; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #7287fd; border-radius: 3px; }
QProgressBar { background-color: #ccd0da; border-radius: 4px; height: 6px; border: none; }
QProgressBar::chunk { background-color: #7287fd; border-radius: 4px; }
QLineEdit { background-color: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 6px; padding: 6px 10px; font-size: 13px; }
QLineEdit:focus { border-color: #7287fd; }
QStatusBar { background-color: #e6e9ef; color: #7c7f93; font-size: 12px; border-top: 1px solid #ccd0da; }
QLabel { color: #4c4f69; background: transparent; }
QTabWidget::pane { border: 1px solid #ccd0da; border-radius: 8px; background-color: #e6e9ef; }
QTabBar::tab { background-color: #ccd0da; color: #4c4f69; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #7287fd; color: #eff1f5; }
QScrollArea { border: none; background-color: #eff1f5; }
QScrollBar:vertical { background: #e6e9ef; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #bcc0cc; border-radius: 5px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: #acb0be; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal { background: #e6e9ef; height: 10px; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #bcc0cc; border-radius: 5px; min-width: 30px; }
QScrollBar::handle:horizontal:hover { background: #acb0be; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
QMenu { background-color: #ccd0da; color: #4c4f69; border: 1px solid #bcc0cc; border-radius: 8px; padding: 4px; }
QMenu::item { padding: 6px 24px; border-radius: 4px; }
QMenu::item:selected { background-color: #7287fd; color: #eff1f5; }
QMenu::item:disabled { color: #acb0be; }
QMenu::separator { height: 1px; background: #bcc0cc; margin: 4px 8px; }
QDialog { background-color: #eff1f5; color: #4c4f69; }
QCheckBox { color: #4c4f69; spacing: 8px; }
QCheckBox::indicator { width: 18px; height: 18px; border-radius: 4px; border: 2px solid #bcc0cc; background-color: #ccd0da; }
QCheckBox::indicator:checked { background-color: #7287fd; border-color: #7287fd; }
"""

DEFAULT_READING_PRESETS = {
    'dark': {'bg_color': '#1e1e2e', 'text_color': '#cdd6f4', 'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif', 'font_size': 16},
    'light': {'bg_color': '#eff1f5', 'text_color': '#4c4f69', 'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif', 'font_size': 16},
    'sepia': {'bg_color': '#f4ecd8', 'text_color': '#5b4636', 'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif', 'font_size': 16},
    'green': {'bg_color': '#c8e6c9', 'text_color': '#2e4a2e', 'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif', 'font_size': 16},
}


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('搜索')
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入搜索内容...')
        self.search_input.setMinimumHeight(36)
        row.addWidget(self.search_input)
        self.search_btn = QPushButton('搜索')
        self.search_btn.setDefault(True)
        self.search_btn.setMinimumHeight(36)
        row.addWidget(self.search_btn)
        layout.addLayout(row)
        self.result_label = QLabel('')
        layout.addWidget(self.result_label)
        nav = QHBoxLayout()
        self.prev_btn = QPushButton('< 上一个')
        nav.addWidget(self.prev_btn)
        nav.addStretch()
        self.next_btn = QPushButton('下一个 >')
        nav.addWidget(self.next_btn)
        layout.addLayout(nav)


class ReadingSettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle('阅读设置')
        self.setMinimumSize(480, 520)
        self.result_settings = {}
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.addWidget(QLabel('<b>预设方案</b>'))
        row = QHBoxLayout()
        for name, label in [('dark', '深色'), ('light', '浅色'), ('sepia', '护眼黄'), ('green', '护眼绿')]:
            b = QPushButton(label)
            b.clicked.connect(lambda _, n=name: self._apply_preset(n))
            row.addWidget(b)
        layout.addLayout(row)
        layout.addWidget(QFrame(frameShape=QFrame.HLine))
        form = QFormLayout()
        form.setSpacing(14)
        self.bg_color = current_settings.get('bg_color', '#1e1e2e')
        self.bg_btn = QPushButton()
        self.bg_btn.setFixedSize(60, 36)
        self._update_color_btn(self.bg_btn, self.bg_color)
        self.bg_btn.clicked.connect(self._pick_bg_color)
        r1 = QHBoxLayout()
        r1.addWidget(self.bg_btn)
        self.bg_label = QLabel(self.bg_color)
        r1.addWidget(self.bg_label)
        r1.addStretch()
        form.addRow('背景颜色:', r1)
        self.text_color = current_settings.get('text_color', '#cdd6f4')
        self.text_btn = QPushButton()
        self.text_btn.setFixedSize(60, 36)
        self._update_color_btn(self.text_btn, self.text_color)
        self.text_btn.clicked.connect(self._pick_text_color)
        r2 = QHBoxLayout()
        r2.addWidget(self.text_btn)
        self.text_label = QLabel(self.text_color)
        r2.addWidget(self.text_label)
        r2.addStretch()
        form.addRow('字体颜色:', r2)
        self.font_family = current_settings.get('font_family', 'Microsoft YaHei')
        self.font_btn = QPushButton(self.font_family.split(',')[0].strip())
        self.font_btn.setMinimumWidth(200)
        self.font_btn.clicked.connect(self._pick_font)
        form.addRow('阅读字体:', self.font_btn)
        r3 = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(10, 36)
        self.font_size_slider.setValue(current_settings.get('font_size', 16))
        self.font_size_slider.setFixedWidth(180)
        r3.addWidget(self.font_size_slider)
        self.fs_val = QLabel(f'{self.font_size_slider.value()}px')
        self.fs_val.setFixedWidth(45)
        r3.addWidget(self.fs_val)
        self.font_size_slider.valueChanged.connect(lambda v: self.fs_val.setText(f'{v}px'))
        r3.addStretch()
        form.addRow('字体大小:', r3)
        r4 = QHBoxLayout()
        self.lh_slider = QSlider(Qt.Horizontal)
        self.lh_slider.setRange(10, 30)
        self.lh_slider.setValue(int(current_settings.get('line_height', 1.8) * 10))
        self.lh_slider.setFixedWidth(180)
        r4.addWidget(self.lh_slider)
        self.lh_val = QLabel(f'{self.lh_slider.value() / 10:.1f}')
        self.lh_val.setFixedWidth(45)
        r4.addWidget(self.lh_val)
        self.lh_slider.valueChanged.connect(lambda v: self.lh_val.setText(f'{v / 10:.1f}'))
        r4.addStretch()
        form.addRow('行高:', r4)
        self.indent_cb = QCheckBox('段首缩进 2em')
        self.indent_cb.setChecked(current_settings.get('indent', True))
        form.addRow('排版:', self.indent_cb)
        self.justify_cb = QCheckBox('两端对齐')
        self.justify_cb.setChecked(current_settings.get('justify', True))
        form.addRow('', self.justify_cb)
        layout.addLayout(form)
        layout.addWidget(QFrame(frameShape=QFrame.HLine))
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _update_color_btn(self, btn, c):
        btn.setStyleSheet(f'background-color: {c}; border: 2px solid #666; border-radius: 6px;')

    def _apply_preset(self, n):
        p = DEFAULT_READING_PRESETS[n]
        self.bg_color, self.text_color = p['bg_color'], p['text_color']
        self._update_color_btn(self.bg_btn, self.bg_color)
        self._update_color_btn(self.text_btn, self.text_color)
        self.bg_label.setText(self.bg_color)
        self.text_label.setText(self.text_color)

    def _pick_bg_color(self):
        c = QColorDialog.getColor(QColor(self.bg_color), self, '选择背景颜色')
        if c.isValid():
            self.bg_color = c.name()
            self._update_color_btn(self.bg_btn, self.bg_color)
            self.bg_label.setText(self.bg_color)

    def _pick_text_color(self):
        c = QColorDialog.getColor(QColor(self.text_color), self, '选择字体颜色')
        if c.isValid():
            self.text_color = c.name()
            self._update_color_btn(self.text_btn, self.text_color)
            self.text_label.setText(self.text_color)

    def _pick_font(self):
        f, ok = QFontDialog.getFont(QFont(self.font_family.split(',')[0].strip()), self, '选择阅读字体')
        if ok:
            self.font_family = f.family()
            self.font_btn.setText(f.family())

    def _accept(self):
        self.result_settings = {
            'bg_color': self.bg_color, 'text_color': self.text_color,
            'font_family': self.font_family, 'font_size': self.font_size_slider.value(),
            'line_height': self.lh_slider.value() / 10,
            'indent': self.indent_cb.isChecked(), 'justify': self.justify_cb.isChecked(),
        }
        self.accept()


class BookCard(QFrame):
    clicked = pyqtSignal(str)
    remove_requested = pyqtSignal(str)
    open_folder_requested = pyqtSignal(str)

    def __init__(self, file_path, title, author, progress_pct, cover_pixmap, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.setFixedSize(170, 250)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            BookCard { background-color: transparent; border: none; }
            BookCard:hover { background-color: rgba(137,180,250,30); border-radius: 8px; }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 6)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignCenter)

        cover_label = QLabel()
        if cover_pixmap:
            scaled = cover_pixmap.scaled(120, 160, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            cover_label.setPixmap(scaled)
        else:
            cover_label.setPixmap(get_placeholder_cover(120, 160))
        cover_label.setAlignment(Qt.AlignCenter)
        cover_label.setFixedSize(120, 160)
        layout.addWidget(cover_label, 0, Qt.AlignCenter)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setMaximumHeight(36)
        title_label.setStyleSheet('font-size: 13px; font-weight: bold;')
        layout.addWidget(title_label)

        info = author if author else f'{progress_pct}%'
        if author and progress_pct > 0:
            info = f'{author} · {progress_pct}%'
        info_label = QLabel(info)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet('font-size: 11px; color: #888;')
        layout.addWidget(info_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.file_path)
        super().mousePressEvent(event)

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        open_act = menu.addAction('打开')
        open_act.triggered.connect(lambda: self.clicked.emit(self.file_path))
        folder_act = menu.addAction('打开所在文件夹')
        folder_act.triggered.connect(lambda: self.open_folder_requested.emit(self.file_path))
        menu.addSeparator()
        rm_act = menu.addAction('从书架移除')
        rm_act.triggered.connect(lambda: self.remove_requested.emit(self.file_path))
        menu.exec_(event.globalPos())


class BookshelfWidget(QWidget):
    book_open_requested = pyqtSignal(str)
    add_books_requested = pyqtSignal()
    book_remove_requested = pyqtSignal(str)
    book_open_folder_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.acceptDrops()
        self.cards = []
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        self.header = QWidget()
        h_layout = QHBoxLayout(self.header)
        h_layout.setContentsMargins(30, 20, 30, 10)
        self.header_label = QLabel('<h2 style="margin:0;">我的书架</h2>')
        h_layout.addWidget(self.header_label)
        h_layout.addStretch()
        self.add_btn = QPushButton('+ 添加书籍')
        self.add_btn.clicked.connect(self.add_books_requested.emit)
        h_layout.addWidget(self.add_btn)
        outer.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.grid_container = QWidget()
        self.grid_layout = QFlowLayout(self.grid_container, spacing=16)
        self.grid_layout.setContentsMargins(30, 10, 30, 30)
        self.scroll.setWidget(self.grid_container)
        outer.addWidget(self.scroll)

        self.empty_label = QLabel('')
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet('font-size: 16px; color: #888;')
        outer.addWidget(self.empty_label)
        self.empty_label.hide()

    def refresh(self, books_meta, get_progress_fn):
        for c in self.cards:
            self.grid_layout.removeWidget(c)
            c.deleteLater()
        self.cards = []
        has_books = bool(books_meta)
        self.scroll.setVisible(has_books)
        self.empty_label.setVisible(not has_books)
        if not has_books:
            self.empty_label.setText(
                '书架还是空的\n\n点击右上角「+ 添加书籍」\n或拖入 EPUB 文件开始阅读'
            )
            return
        for fp, meta in books_meta.items():
            progress = get_progress_fn(fp, meta.get('chapters', 0))
            card = BookCard(
                fp, meta.get('title', ''), meta.get('author', ''),
                progress, meta.get('cover'),
            )
            card.clicked.connect(self.book_open_requested.emit)
            card.remove_requested.connect(self.book_remove_requested.emit)
            card.open_folder_requested.connect(self.book_open_folder_requested.emit)
            self.grid_layout.addWidget(card)
            self.cards.append(card)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            fp = url.toLocalFile()
            if fp.lower().endswith('.epub') and os.path.isfile(fp):
                self.book_open_requested.emit(fp)


class QFlowLayout(QLayout):
    def __init__(self, parent=None, spacing=10):
        super().__init__(parent)
        self._items = []
        self._spacing = spacing

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations()

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        return size

    def _do_layout(self, rect, test_only):
        x, y, line_h = rect.x(), rect.y(), 0
        for item in self._items:
            w = item.sizeHint().width()
            h = item.sizeHint().height()
            if x + w > rect.right() and line_h > 0:
                x = rect.x()
                y += line_h + self._spacing
                line_h = 0
            if not test_only:
                item.setGeometry(QRect(x, y, w, h))
            x += w + self._spacing
            line_h = max(line_h, h)
        return y + line_h - rect.y()


class EPUBReader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_book = None
        self.current_chapter_index = 0
        self.chapters = []
        self.book_title = ''
        self.is_dark_theme = True
        self.bookmarks = {}
        self.search_results = []
        self.search_current_index = -1
        self.last_opened_dir = ''
        self.book_file_path = ''
        self.is_immersive = False
        self._search_dialog = None
        self.recent_files = []
        self.recent_menu = None
        self.books_meta = {}
        self._in_book = False

        self.reading_settings = {
            'bg_color': '#1e1e2e', 'text_color': '#cdd6f4',
            'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
            'font_size': 16, 'line_height': 1.8, 'indent': True, 'justify': True,
        }
        self.settings = QSettings('EPUBReader', 'EPUBReader')
        self.load_settings()
        self.init_ui()
        self.apply_theme()
        self.app_icon = create_app_icon()
        self.setWindowIcon(self.app_icon)
        QTimer.singleShot(100, self._startup)

    def _startup(self):
        if self.recent_files:
            last = self.recent_files[0]
            if os.path.isfile(last):
                self.load_epub(last)
                return
        self.show_bookshelf()

    def load_settings(self):
        self.is_dark_theme = self.settings.value('is_dark_theme', True, type=bool)
        self.last_opened_dir = self.settings.value('last_opened_dir', '', type=str)
        g = self.settings.value('geometry')
        if g:
            self.restoreGeometry(g)
        rs = self.settings.value('reading_settings')
        if rs:
            try:
                self.reading_settings = json.loads(rs)
            except Exception:
                pass
        rf = self.settings.value('recent_files')
        if rf:
            try:
                self.recent_files = json.loads(rf)
            except Exception:
                self.recent_files = []
        bm = self.settings.value('books_meta')
        if bm:
            try:
                self.books_meta = json.loads(bm)
            except Exception:
                self.books_meta = []

    def save_settings(self):
        self.settings.setValue('is_dark_theme', self.is_dark_theme)
        self.settings.setValue('last_opened_dir', self.last_opened_dir)
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('reading_settings', json.dumps(self.reading_settings))
        self.settings.setValue('recent_files', json.dumps(self.recent_files))
        meta_save = {k: {kk: vv for kk, vv in v.items() if kk != 'cover'} for k, v in self.books_meta.items()}
        self.settings.setValue('books_meta', json.dumps(meta_save))
        if self.book_file_path and self.current_chapter_index >= 0:
            self.settings.setValue(f'progress/{self.book_file_path}', self.current_chapter_index)

    def get_saved_progress(self, fp):
        return self.settings.value(f'progress/{fp}', -1, type=int)

    def _get_progress_pct(self, fp, total_chapters):
        if total_chapters <= 0:
            return 0
        p = self.get_saved_progress(fp)
        return int((p + 1) / total_chapters * 100) if p >= 0 else 0

    def init_ui(self):
        self.setWindowTitle('EPUB 阅读器')
        self.setMinimumSize(900, 600)
        self.resize(1300, 850)
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QVBoxLayout(central)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setup_menubar()

        self.bookshelf = BookshelfWidget()
        self.bookshelf.book_open_requested.connect(self.load_epub)
        self.bookshelf.add_books_requested.connect(self.add_file_to_shelf)
        self.bookshelf.book_remove_requested.connect(self.remove_from_shelf)
        self.bookshelf.book_open_folder_requested.connect(self.open_file_folder)
        self.main_layout.addWidget(self.bookshelf)

        self.reader_widget = QWidget()
        reader_outer = QVBoxLayout(self.reader_widget)
        reader_outer.setContentsMargins(0, 0, 0, 0)
        reader_outer.setSpacing(0)

        self.splitter = QSplitter(Qt.Horizontal)
        left = QTabWidget()
        left.setFixedWidth(280)
        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.toc_item_clicked)
        left.addTab(self.toc_list, '目录')
        self.bookmark_list = QListWidget()
        self.bookmark_list.itemClicked.connect(self.bookmark_clicked)
        left.addTab(self.bookmark_list, '书签')
        self.splitter.addWidget(left)
        rc = QWidget()
        rl = QVBoxLayout(rc)
        rl.setContentsMargins(0, 0, 0, 0)
        rl.setSpacing(0)
        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.anchorClicked.connect(self.on_anchor_clicked)
        rl.addWidget(self.text_browser)
        self.bottom_bar = QWidget()
        bl = QHBoxLayout(self.bottom_bar)
        bl.setContentsMargins(12, 4, 12, 4)
        self.prev_button = QPushButton('< 上一章')
        self.prev_button.clicked.connect(self.prev_chapter)
        self.prev_button.setEnabled(False)
        bl.addWidget(self.prev_button)
        self.chapter_label = QLabel('未加载')
        self.chapter_label.setAlignment(Qt.AlignCenter)
        bl.addWidget(self.chapter_label, 1)
        self.next_button = QPushButton('下一章 >')
        self.next_button.clicked.connect(self.next_chapter)
        self.next_button.setEnabled(False)
        bl.addWidget(self.next_button)
        rl.addWidget(self.bottom_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        rl.addWidget(self.progress_bar)
        self.splitter.addWidget(rc)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        reader_outer.addWidget(self.splitter)

        self.main_layout.addWidget(self.reader_widget)
        self.reader_widget.hide()

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('就绪')
        self.status_bar.addWidget(self.status_label, 1)
        self.setup_shortcuts()

    def show_bookshelf(self):
        self._in_book = False
        self.reader_widget.hide()
        self.bookshelf.show()
        self.refresh_bookshelf()
        self.setWindowTitle('EPUB 阅读器')
        self.status_label.setText(f'书架 · {len([f for f in self.recent_files if os.path.isfile(f)])} 本书')

    def refresh_bookshelf(self):
        valid = {}
        for fp in self.recent_files:
            if not os.path.isfile(fp):
                continue
            if fp not in self.books_meta:
                meta = extract_epub_meta(fp)
                cover = extract_epub_cover(fp)
                meta['cover'] = cover
                self.books_meta[fp] = meta
            valid[fp] = self.books_meta[fp]
        self.books_meta = valid
        self.bookshelf.refresh(valid, self._get_progress_pct)

    def remove_from_shelf(self, fp):
        fp = os.path.abspath(fp)
        if fp in self.recent_files:
            self.recent_files.remove(fp)
        self.books_meta.pop(fp, None)
        self._rebuild_recent_menu()
        self.save_settings()
        self.refresh_bookshelf()

    def open_file_folder(self, fp):
        folder = os.path.dirname(fp)
        if sys.platform == 'win32':
            subprocess.Popen(f'explorer "{folder}"')
        elif sys.platform == 'darwin':
            subprocess.Popen(['open', folder])
        else:
            subprocess.Popen(['xdg-open', folder])

    def setup_menubar(self):
        mb = self.menuBar()
        fm = mb.addMenu('文件(&F)')
        a = QAction('打开(&O)...', self)
        a.setShortcut(QKeySequence('Ctrl+O'))
        a.triggered.connect(self.open_epub_file)
        fm.addAction(a)
        a2 = QAction('添加到书架(&A)...', self)
        a2.triggered.connect(self.add_file_to_shelf)
        fm.addAction(a2)
        fm.addSeparator()
        self.recent_menu = fm.addMenu('最近打开(&R)')
        self._rebuild_recent_menu()
        fm.addSeparator()
        fm.addAction(QAction('清除历史(&C)', self, triggered=self.clear_recent_files))
        fm.addSeparator()
        fm.addAction(QAction('退出(&X)', self, shortcut=QKeySequence('Alt+F4'), triggered=self.close))

        vm = mb.addMenu('视图(&V)')
        vm.addAction(QAction('返回书架(&B)', self, shortcut=QKeySequence('Ctrl+H'), triggered=self.show_bookshelf))
        vm.addSeparator()
        vm.addAction(QAction('切换主题(&T)', self, triggered=self.toggle_theme))
        vm.addAction(QAction('阅读设置(&R)...', self, triggered=self.open_reading_settings))
        vm.addSeparator()
        vm.addAction(QAction('放大字体(&I)', self, shortcut=QKeySequence('Ctrl+='), triggered=self.font_size_up))
        vm.addAction(QAction('缩小字体(&D)', self, shortcut=QKeySequence('Ctrl+-'), triggered=self.font_size_down))
        vm.addSeparator()
        vm.addAction(QAction('侧栏(&S)', self, shortcut=QKeySequence('F4'), triggered=self.toggle_sidebar))
        vm.addSeparator()
        vm.addAction(QAction('全屏(&F)', self, shortcut=QKeySequence('F11'), triggered=self.toggle_fullscreen))
        vm.addAction(QAction('沉浸式阅读(&M)', self, shortcut=QKeySequence('F12'), triggered=self.toggle_immersive))

        nm = mb.addMenu('导航(&N)')
        nm.addAction(QAction('上一章(&P)', self, shortcut=QKeySequence('Left'), triggered=self.prev_chapter))
        nm.addAction(QAction('下一章(&N)', self, shortcut=QKeySequence('Right'), triggered=self.next_chapter))
        nm.addSeparator()
        nm.addAction(QAction('跳到首章(&H)', self, shortcut=QKeySequence('Home'), triggered=self.go_to_first_chapter))
        nm.addAction(QAction('跳到末章(&E)', self, shortcut=QKeySequence('End'), triggered=self.go_to_last_chapter))

        tm = mb.addMenu('工具(&T)')
        tm.addAction(QAction('搜索(&F)...', self, shortcut=QKeySequence('Ctrl+F'), triggered=self.open_search_dialog))
        tm.addSeparator()
        tm.addAction(QAction('添加书签(&B)', self, shortcut=QKeySequence('Ctrl+B'), triggered=self.add_bookmark))
        tm.addAction(QAction('清除所有书签(&C)', self, triggered=self.clear_all_bookmarks))

        hm = mb.addMenu('帮助(&H)')
        hm.addAction(QAction('快捷键(&K)', self, triggered=self.show_shortcuts_dialog))
        hm.addSeparator()
        hm.addAction(QAction('关于(&A)', self, triggered=self.show_about_dialog))

    def open_reading_settings(self):
        dlg = ReadingSettingsDialog(self, self.reading_settings)
        if dlg.exec_() == QDialog.Accepted:
            self.reading_settings = dlg.result_settings
            self.sync_browser_bg()
            if self.chapters:
                self.load_chapter(self.current_chapter_index)
            QTimer.singleShot(200, self.save_settings)

    def open_search_dialog(self):
        if self._search_dialog is None or not self._search_dialog.isVisible():
            self._search_dialog = SearchDialog(self)
            self._search_dialog.search_btn.clicked.connect(self._do_search)
            self._search_dialog.search_input.returnPressed.connect(self._do_search)
            self._search_dialog.prev_btn.clicked.connect(self._search_prev)
            self._search_dialog.next_btn.clicked.connect(self._search_next)
        self._search_dialog.show()
        self._search_dialog.search_input.setFocus()
        self._search_dialog.search_input.selectAll()

    def _do_search(self):
        if not self._search_dialog or not self.chapters:
            return
        q = self._search_dialog.search_input.text().strip()
        if not q:
            return
        self.search_results, self.search_current_index = [], -1
        for i, ch in enumerate(self.chapters):
            try:
                t = BeautifulSoup(ch['item'].get_content(), 'lxml').get_text()
                if q.lower() in t.lower():
                    self.search_results.append(i)
            except Exception:
                pass
        if self.search_results:
            self.search_current_index = 0
            self._search_dialog.result_label.setText(f'找到 {len(self.search_results)} 章')
            self.load_chapter(self.search_results[0])
            self.text_browser.find(q)
        else:
            self._search_dialog.result_label.setText('未找到')

    def _search_prev(self):
        if self.search_results and self.search_current_index > 0:
            self.search_current_index -= 1
            self.load_chapter(self.search_results[self.search_current_index])
            q = self._search_dialog.search_input.text().strip()
            if q:
                self.text_browser.find(q)

    def _search_next(self):
        if self.search_results and self.search_current_index < len(self.search_results) - 1:
            self.search_current_index += 1
            self.load_chapter(self.search_results[self.search_current_index])
            q = self._search_dialog.search_input.text().strip()
            if q:
                self.text_browser.find(q)

    def toggle_immersive(self):
        self.is_immersive = not self.is_immersive
        bg = self.reading_settings.get('bg_color', '#1e1e2e')
        if self.is_immersive:
            self.menuBar().hide()
            self.statusBar().hide()
            self.bottom_bar.hide()
            self.progress_bar.hide()
            left = self.splitter.widget(0)
            self._sidebar_was_visible = left.isVisible()
            left.hide()
            self.setStyleSheet('')
            self.text_browser.setStyleSheet(f'QTextBrowser {{ background-color: {bg}; border: none; padding: 30px 60px; }}')
            self.showFullScreen()
        else:
            self.menuBar().show()
            self.statusBar().show()
            self.bottom_bar.show()
            self.progress_bar.show()
            if getattr(self, '_sidebar_was_visible', True):
                self.splitter.widget(0).show()
            self.apply_theme()
            self.showNormal()

    def show_about_dialog(self):
        icon = self.windowIcon()
        if icon.isNull():
            icon = create_app_icon()
        msg = QMessageBox(self)
        msg.setIconPixmap(icon.pixmap(64, 64))
        msg.setWindowTitle('关于 EPUB 阅读器')
        msg.setText('<h2 style="margin-bottom:2px;">EPUB 阅读器 v1.0.0</h2><p style="color:#888;">一款简洁优雅的电子书阅读器</p>')
        msg.setInformativeText(
            '功能特性：\n'
            '  • 书架主页 — 一目了然管理书籍\n'
            '  • 暗色/亮色双主题 + 自定义配色\n'
            '  • 自定义字体/颜色/大小/行高\n'
            '  • 章节目录导航与书签\n'
            '  • 全文搜索\n'
            '  • 阅读进度自动保存\n'
            '  • 沉浸式全屏阅读模式\n'
            '  • 拖拽添加书籍到书架\n\n'
            '技术栈：PyQt5 · ebooklib · BeautifulSoup4\n\n'
            '━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
            '作者：AlanNiew\n\n'
            '特别感谢：\n'
            '  • PyQt5 开源社区\n'
            '  • ebooklib 项目贡献者\n'
            '  • BeautifulSoup4 开发团队\n'
            '  • Catppuccin 主题设计团队\n'
            '  • 所有开源软件的贡献者们\n\n'
            '━━━━━━━━━━━━━━━━━━━━━━━━\n\n'
            '如果您觉得这款软件对您有帮助，\n'
            '欢迎支持开发者继续维护和完善！\n\n'
            '感谢您的使用 ❤'
        )
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

    def show_shortcuts_dialog(self):
        shortcuts = [
            ('Ctrl+O', '打开文件'), ('Ctrl+H', '返回书架'), ('Ctrl+F', '搜索'),
            ('Ctrl+B', '添加书签'), ('Ctrl+=/-', '放大/缩小字体'),
            ('Left / Right', '上一章/下一章'), ('Home / End', '首章/末章'),
            ('F4', '切换侧栏'), ('F11', '全屏模式'), ('F12', '沉浸式阅读'),
            ('Esc', '退出全屏/沉浸'), ('Alt+F4', '退出程序'),
        ]
        rows = ''.join(f'<tr><td style="padding:4px 12px;"><code>{s}</code></td><td style="padding:4px 12px;">{d}</td></tr>' for s, d in shortcuts)
        dlg = QMessageBox(self)
        dlg.setWindowTitle('快捷键')
        dlg.setText(f'<h3>键盘快捷键</h3><table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;"><tr><th>快捷键</th><th>功能</th></tr>{rows}</table>')
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()

    def clear_all_bookmarks(self):
        self.bookmarks = {}
        self.bookmark_list.clear()
        if self.book_file_path:
            self.settings.remove(f'bookmarks/{self.book_file_path}')
        self.status_label.setText('已清除所有书签')

    def add_file_to_shelf(self):
        fps, _ = QFileDialog.getOpenFileNames(self, '添加EPUB文件到书架', self.last_opened_dir or '', 'EPUB文件 (*.epub);;所有文件 (*)')
        added = 0
        for fp in fps:
            if os.path.isfile(fp):
                self._add_to_shelf(fp)
                added += 1
        if added:
            self.refresh_bookshelf()
            self.save_settings()
            self.status_label.setText(f'已添加 {added} 本书到书架')

    def _add_to_shelf(self, fp):
        fp = os.path.abspath(fp)
        if fp in self.recent_files:
            self.recent_files.remove(fp)
        self.recent_files.insert(0, fp)
        self.recent_files = self.recent_files[:50]
        if fp not in self.books_meta:
            meta = extract_epub_meta(fp)
            meta['cover'] = extract_epub_cover(fp)
            self.books_meta[fp] = meta
        self._rebuild_recent_menu()

    def _rebuild_recent_menu(self):
        if not self.recent_menu:
            return
        self.recent_menu.clear()
        for i, fp in enumerate(self.recent_files[:10]):
            if not os.path.isfile(fp):
                continue
            a = QAction(f'{i + 1}. {os.path.basename(fp)}', self)
            a.setData(fp)
            a.triggered.connect(self._open_recent_file)
            self.recent_menu.addAction(a)
        if self.recent_menu.isEmpty():
            self.recent_menu.addAction('(空)').setEnabled(False)

    def _open_recent_file(self):
        a = self.sender()
        if a:
            fp = a.data()
            if fp and os.path.isfile(fp):
                self.load_epub(fp)

    def clear_recent_files(self):
        self.recent_files = []
        self.books_meta = {}
        self._rebuild_recent_menu()
        self.save_settings()
        self.refresh_bookshelf()
        self.status_label.setText('已清除所有历史')

    def setup_shortcuts(self):
        QShortcut(QKeySequence('Escape'), self, self.exit_fullscreen)

    def toggle_fullscreen(self):
        if self.isFullScreen() and not self.is_immersive:
            self.showNormal()
        else:
            self.showFullScreen()

    def exit_fullscreen(self):
        if self.is_immersive:
            self.toggle_immersive()
        elif self.isFullScreen():
            self.showNormal()

    def toggle_sidebar(self):
        left = self.splitter.widget(0)
        left.setVisible(not left.isVisible())

    def sync_browser_bg(self):
        bg = self.reading_settings.get('bg_color', '#1e1e2e')
        self.text_browser.setStyleSheet(f'QTextBrowser {{ background-color: {bg}; border: none; padding: 20px; }}')

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        d = DEFAULT_READING_PRESETS['dark' if self.is_dark_theme else 'light']
        self.reading_settings['bg_color'] = d['bg_color']
        self.reading_settings['text_color'] = d['text_color']
        self.apply_theme()
        if self._in_book and self.chapters:
            self.load_chapter(self.current_chapter_index)

    def apply_theme(self):
        self.setStyleSheet(STYLESHEET_DARK if self.is_dark_theme else STYLESHEET_LIGHT)
        if self._in_book:
            self.sync_browser_bg()

    def build_reading_html_style(self):
        s = self.reading_settings
        bg, tc = s.get('bg_color', '#1e1e2e'), s.get('text_color', '#cdd6f4')
        ff, fs, lh = s.get('font_family', 'serif'), s.get('font_size', 16), s.get('line_height', 1.8)
        ind = 'text-indent: 2em;' if s.get('indent', True) else ''
        jus = 'text-align: justify;' if s.get('justify', True) else ''
        tint = '#89b4fa' if self.is_dark_theme else '#7287fd'
        sbg = '#181825' if self.is_dark_theme else '#e6e9ef'
        bc = '#313244' if self.is_dark_theme else '#ccd0da'
        return f"""<style>
    body {{ font-family: {ff}; font-size: {fs}px; line-height: {lh}; margin: 30px 40px; color: {tc}; background-color: {bg}; }}
    p {{ margin-bottom: 1em; {jus} {ind} }}
    h1 {{ color: {tint}; font-size: 1.8em; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 2px solid {bc}; padding-bottom: 0.3em; }}
    h2 {{ font-size: 1.5em; margin-top: 1.3em; }} h3 {{ font-size: 1.2em; margin-top: 1.1em; }}
    a {{ color: {tint}; text-decoration: none; }} a:hover {{ text-decoration: underline; }}
    blockquote {{ border-left: 4px solid {tint}; margin: 1em 0; padding: 0.5em 1em; background-color: {sbg}; border-radius: 0 8px 8px 0; }}
    hr {{ border: none; border-top: 1px solid {bc}; margin: 2em 0; }}
    img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 1em auto; display: block; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
    th, td {{ border: 1px solid {bc}; padding: 8px 12px; }} th {{ background-color: {sbg}; }}
    code {{ background-color: {sbg}; padding: 2px 6px; border-radius: 4px; }}
    pre {{ background-color: {sbg}; padding: 1em; border-radius: 8px; overflow-x: auto; }}
    ul, ol {{ padding-left: 2em; }} li {{ margin-bottom: 0.3em; }}
</style>"""

    def font_size_up(self):
        self.reading_settings['font_size'] = min(36, self.reading_settings.get('font_size', 16) + 1)
        if self.chapters:
            self.load_chapter(self.current_chapter_index)
        QTimer.singleShot(200, self.save_settings)

    def font_size_down(self):
        self.reading_settings['font_size'] = max(10, self.reading_settings.get('font_size', 16) - 1)
        if self.chapters:
            self.load_chapter(self.current_chapter_index)
        QTimer.singleShot(200, self.save_settings)

    def open_epub_file(self):
        fp, _ = QFileDialog.getOpenFileName(self, '选择EPUB文件', self.last_opened_dir or '', 'EPUB文件 (*.epub);;所有文件 (*)')
        if fp:
            self.last_opened_dir = os.path.dirname(fp)
            self.load_epub(fp)

    def load_epub(self, file_path):
        try:
            self.current_book = epub.read_epub(file_path)
            self.current_chapter_index = 0
            self.chapters = []
            self.book_file_path = file_path
            self.bookmarks = {}
            meta = self.current_book.get_metadata('DC', 'title')
            self.book_title = meta[0][0] if meta else os.path.basename(file_path)
            self.toc_list.clear()
            self.bookmark_list.clear()
            self.build_chapters()
            self.populate_toc_list()
            p = self.get_saved_progress(file_path)
            idx = max(0, p) if p >= 0 else 0
            if self.chapters:
                self.load_chapter(idx)
                self.update_navigation_buttons()
            self.setWindowTitle(f'EPUB 阅读器 - {self.book_title}')
            self.status_label.setText(f'{self.book_title} | {len(self.chapters)} 章')
            self.load_bookmarks_for_book()
            self._add_to_shelf(file_path)
            self.save_settings()
            self.bookshelf.hide()
            self.reader_widget.show()
            self._in_book = True
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法加载EPUB文件:\n{str(e)}')

    def build_chapters(self):
        toc_map = {}
        for item in self.current_book.toc:
            if isinstance(item, tuple):
                sec, ch = item
                if hasattr(sec, 'href'):
                    toc_map[sec.href.split('#')[0]] = sec.title
                if ch:
                    for c in ch:
                        if hasattr(c, 'href'):
                            toc_map[c.href.split('#')[0]] = c.title
            elif hasattr(item, 'href'):
                toc_map[item.href.split('#')[0]] = item.title
        spine = [s[0] if isinstance(s, (tuple, list)) else s for s in (self.current_book.spine or [])]
        seen, items = set(), []
        for sid in spine:
            it = self.current_book.get_item_with_id(sid)
            if it and it.get_type() == 9 and sid not in seen:
                seen.add(sid)
                items.append(it)
        if not items:
            for it in self.current_book.get_items():
                if it.get_type() == 9:
                    n = it.get_name()
                    if n not in seen:
                        seen.add(n)
                        items.append(it)
        for it in items:
            name = it.get_name()
            title = None
            for h, t in toc_map.items():
                if h == name or name.endswith('/' + h) or h.endswith('/' + name):
                    title = t
                    break
            if not title:
                try:
                    soup = BeautifulSoup(it.get_content(), 'lxml')
                    title = (soup.title.string.strip() if soup.title and soup.title.string else None)
                    if not title:
                        hh = soup.find(['h1', 'h2', 'h3'])
                        title = hh.get_text(strip=True) if hh else os.path.splitext(name)[0]
                except Exception:
                    title = os.path.splitext(name)[0]
            self.chapters.append({'title': title, 'item': it})

    def populate_toc_list(self):
        for i, ch in enumerate(self.chapters):
            li = QListWidgetItem(ch['title'])
            li.setData(Qt.UserRole, i)
            self.toc_list.addItem(li)

    def resolve_image(self, src, cdir):
        if not self.current_book or not src or src.startswith('data:'):
            return src
        r = os.path.normpath(os.path.join(cdir, src)).replace('\\', '/')
        for it in self.current_book.get_items():
            n = it.get_name().replace('\\', '/')
            if n == r or n.endswith('/' + r):
                try:
                    d = it.get_content()
                    mt = it.media_type or 'image/png'
                    if not mt.startswith('image/'):
                        mt = 'image/png'
                    return f'data:{mt};base64,{base64.b64encode(d).decode("ascii")}'
                except Exception:
                    return None
        return None

    def load_chapter(self, index):
        if 0 <= index < len(self.chapters):
            self.current_chapter_index = index
            ch = self.chapters[index]
            try:
                soup = BeautifulSoup(ch['item'].get_content(), 'lxml')
                for t in soup(['script', 'style']):
                    t.decompose()
                cdir = os.path.dirname(ch['item'].get_name())
                for img in soup.find_all('img'):
                    s = img.get('src')
                    if s:
                        d = self.resolve_image(s, cdir)
                        if d:
                            img['src'] = d
                for img in soup.find_all('image'):
                    h = img.get('xlink:href') or img.get('href')
                    if h:
                        d = self.resolve_image(h, cdir)
                        if d:
                            img['xlink:href'] = d
                body = soup.find('body')
                hc = body.decode_contents() if body else str(soup)
                style = self.build_reading_html_style()
                self.sync_browser_bg()
                self.text_browser.setHtml(f'<html><head>{style}</head><body>{hc}</body></html>')
                self.text_browser.scrollToAnchor('')
                self.text_browser.verticalScrollBar().setValue(0)
                self.chapter_label.setText(f'第 {index + 1}/{len(self.chapters)} 章 · {ch["title"]}')
                self.toc_list.setCurrentRow(index)
                self.progress_bar.setValue(int((index + 1) / len(self.chapters) * 100))
                self.status_label.setText(f'{self.book_title} | 第 {index + 1}/{len(self.chapters)} 章 | {ch["title"]}')
                QTimer.singleShot(500, self.save_settings)
            except Exception as e:
                self.text_browser.setText(f'加载章节失败:\n{str(e)}')
            self.update_navigation_buttons()

    def on_anchor_clicked(self, url):
        href, frag = url.toString(), url.fragment()
        tf = href.split('#')[0] if '#' in href else href
        if not tf and frag:
            self.text_browser.scrollToAnchor(frag)
            return
        for i, ch in enumerate(self.chapters):
            n = ch['item'].get_name()
            if n == tf or n.endswith('/' + tf):
                self.load_chapter(i)
                if frag:
                    QTimer.singleShot(300, lambda f=frag: self.text_browser.scrollToAnchor(f))
                return

    def toc_item_clicked(self, item):
        idx = item.data(Qt.UserRole)
        if idx is not None:
            self.load_chapter(idx)

    def prev_chapter(self):
        if self.current_chapter_index > 0:
            self.load_chapter(self.current_chapter_index - 1)

    def next_chapter(self):
        if self.current_chapter_index < len(self.chapters) - 1:
            self.load_chapter(self.current_chapter_index + 1)

    def go_to_first_chapter(self):
        if self.chapters:
            self.load_chapter(0)

    def go_to_last_chapter(self):
        if self.chapters:
            self.load_chapter(len(self.chapters) - 1)

    def update_navigation_buttons(self):
        self.prev_button.setEnabled(self.current_chapter_index > 0)
        self.next_button.setEnabled(self.current_chapter_index < len(self.chapters) - 1)

    def add_bookmark(self):
        if not self.chapters:
            return
        ch = self.chapters[self.current_chapter_index]
        sp = self.text_browser.verticalScrollBar().value()
        k = f'{self.current_chapter_index}_{sp}'
        name = f'第{self.current_chapter_index + 1}章 - {ch["title"]}'
        self.bookmarks[k] = {'chapter_index': self.current_chapter_index, 'scroll_pos': sp, 'title': name}
        self.save_bookmarks_to_settings()
        li = QListWidgetItem(name)
        li.setData(Qt.UserRole, k)
        self.bookmark_list.addItem(li)
        self.status_label.setText(f'已添加书签: {name}')

    def bookmark_clicked(self, item):
        k = item.data(Qt.UserRole)
        if k in self.bookmarks:
            bm = self.bookmarks[k]
            self.load_chapter(bm['chapter_index'])
            QTimer.singleShot(300, lambda: self.text_browser.verticalScrollBar().setValue(bm['scroll_pos']))

    def save_bookmarks_to_settings(self):
        if self.book_file_path:
            self.settings.setValue(f'bookmarks/{self.book_file_path}', json.dumps(self.bookmarks))

    def load_bookmarks_for_book(self):
        self.bookmark_list.clear()
        self.bookmarks = {}
        if self.book_file_path:
            ds = self.settings.value(f'bookmarks/{self.book_file_path}', '', type=str)
            if ds:
                try:
                    for k, bm in json.loads(ds).items():
                        self.bookmarks[k] = bm
                        li = QListWidgetItem(bm['title'])
                        li.setData(Qt.UserRole, k)
                        self.bookmark_list.addItem(li)
                except Exception:
                    pass

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)
