import os
import json
import base64
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextBrowser, QListWidget, QFileDialog,
                             QSplitter, QLabel, QMessageBox, QListWidgetItem,
                             QSlider, QProgressBar, QLineEdit, QAction,
                             QMenu, QStatusBar, QShortcut,
                             QTabWidget, QDialog, QFormLayout, QColorDialog,
                             QFontDialog, QDialogButtonBox, QFrame, QCheckBox)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QSettings
from PyQt5.QtGui import (QFont, QIcon, QColor, QPalette, QKeySequence,
                          QPixmap, QPainter, QFontDatabase)
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
    sizes = [16, 24, 32, 48, 64, 128, 256]
    icon = QIcon()
    for s in sizes:
        pixmap = QPixmap(s, s)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        icon.addPixmap(pixmap)
    return icon


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
QTextBrowser { background-color: #1e1e2e; color: #cdd6f4; border: 1px solid #313244; border-radius: 8px; padding: 20px; }
QSlider::groove:horizontal { height: 6px; background: #313244; border-radius: 3px; }
QSlider::handle:horizontal { background: #89b4fa; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #89b4fa; border-radius: 3px; }
QProgressBar { background-color: #313244; border-radius: 4px; height: 6px; text-align: center; border: none; }
QProgressBar::chunk { background-color: #89b4fa; border-radius: 4px; }
QLineEdit { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 6px 10px; font-size: 13px; }
QLineEdit:focus { border-color: #89b4fa; }
QStatusBar { background-color: #181825; color: #a6adc8; font-size: 12px; border-top: 1px solid #313244; }
QLabel { color: #cdd6f4; background: transparent; }
QTabWidget::pane { border: 1px solid #313244; border-radius: 8px; background-color: #181825; }
QTabBar::tab { background-color: #313244; color: #cdd6f4; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #89b4fa; color: #1e1e2e; }
QComboBox { background-color: #313244; color: #cdd6f4; border: 1px solid #45475a; border-radius: 6px; padding: 4px 8px; min-width: 60px; }
QComboBox:hover { border-color: #89b4fa; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #313244; color: #cdd6f4; selection-background-color: #89b4fa; selection-color: #1e1e2e; border: 1px solid #45475a; border-radius: 4px; }
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
QTextBrowser { background-color: #eff1f5; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 8px; padding: 20px; }
QSlider::groove:horizontal { height: 6px; background: #ccd0da; border-radius: 3px; }
QSlider::handle:horizontal { background: #7287fd; width: 16px; height: 16px; margin: -5px 0; border-radius: 8px; }
QSlider::sub-page:horizontal { background: #7287fd; border-radius: 3px; }
QProgressBar { background-color: #ccd0da; border-radius: 4px; height: 6px; text-align: center; border: none; }
QProgressBar::chunk { background-color: #7287fd; border-radius: 4px; }
QLineEdit { background-color: #e6e9ef; color: #4c4f69; border: 1px solid #ccd0da; border-radius: 6px; padding: 6px 10px; font-size: 13px; }
QLineEdit:focus { border-color: #7287fd; }
QStatusBar { background-color: #e6e9ef; color: #7c7f93; font-size: 12px; border-top: 1px solid #ccd0da; }
QLabel { color: #4c4f69; background: transparent; }
QTabWidget::pane { border: 1px solid #ccd0da; border-radius: 8px; background-color: #e6e9ef; }
QTabBar::tab { background-color: #ccd0da; color: #4c4f69; padding: 8px 16px; border-top-left-radius: 6px; border-top-right-radius: 6px; margin-right: 2px; }
QTabBar::tab:selected { background-color: #7287fd; color: #eff1f5; }
QComboBox { background-color: #ccd0da; color: #4c4f69; border: 1px solid #bcc0cc; border-radius: 6px; padding: 4px 8px; min-width: 60px; }
QComboBox:hover { border-color: #7287fd; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #ccd0da; color: #4c4f69; selection-background-color: #7287fd; selection-color: #eff1f5; border: 1px solid #bcc0cc; border-radius: 4px; }
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
    'dark': {
        'bg_color': '#1e1e2e',
        'text_color': '#cdd6f4',
        'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
        'font_size': 16,
    },
    'light': {
        'bg_color': '#eff1f5',
        'text_color': '#4c4f69',
        'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
        'font_size': 16,
    },
    'sepia': {
        'bg_color': '#f4ecd8',
        'text_color': '#5b4636',
        'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
        'font_size': 16,
    },
    'green': {
        'bg_color': '#c8e6c9',
        'text_color': '#2e4a2e',
        'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
        'font_size': 16,
    },
}


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('搜索')
        self.setMinimumWidth(420)
        self.setWindowFlags(self.windowFlags() | Qt.Tool)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        input_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入搜索内容...')
        self.search_input.setMinimumHeight(36)
        input_row.addWidget(self.search_input)
        self.search_btn = QPushButton('搜索')
        self.search_btn.setDefault(True)
        self.search_btn.setMinimumHeight(36)
        input_row.addWidget(self.search_btn)
        layout.addLayout(input_row)

        self.result_label = QLabel('')
        layout.addWidget(self.result_label)

        nav_row = QHBoxLayout()
        self.prev_btn = QPushButton('< 上一个')
        nav_row.addWidget(self.prev_btn)
        nav_row.addStretch()
        self.next_btn = QPushButton('下一个 >')
        nav_row.addWidget(self.next_btn)
        layout.addLayout(nav_row)


class ReadingSettingsDialog(QDialog):
    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.setWindowTitle('阅读设置')
        self.setMinimumSize(480, 520)
        self.result_settings = {}

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        preset_group = QLabel('<b>预设方案</b>')
        layout.addWidget(preset_group)
        preset_row = QHBoxLayout()
        self.preset_dark = QPushButton('深色')
        self.preset_dark.clicked.connect(lambda: self._apply_preset('dark'))
        preset_row.addWidget(self.preset_dark)
        self.preset_light = QPushButton('浅色')
        self.preset_light.clicked.connect(lambda: self._apply_preset('light'))
        preset_row.addWidget(self.preset_light)
        self.preset_sepia = QPushButton('护眼黄')
        self.preset_sepia.clicked.connect(lambda: self._apply_preset('sepia'))
        preset_row.addWidget(self.preset_sepia)
        self.preset_green = QPushButton('护眼绿')
        self.preset_green.clicked.connect(lambda: self._apply_preset('green'))
        preset_row.addWidget(self.preset_green)
        layout.addLayout(preset_row)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(14)

        self.bg_color = current_settings.get('bg_color', '#1e1e2e')
        self.bg_btn = QPushButton()
        self.bg_btn.setFixedSize(60, 36)
        self._update_color_btn(self.bg_btn, self.bg_color)
        self.bg_btn.clicked.connect(self._pick_bg_color)
        bg_row = QHBoxLayout()
        bg_row.addWidget(self.bg_btn)
        bg_row.addWidget(QLabel(self.bg_color))
        self.bg_label = bg_row.itemAt(1).widget()
        bg_row.addStretch()
        form.addRow('背景颜色:', bg_row)

        self.text_color = current_settings.get('text_color', '#cdd6f4')
        self.text_btn = QPushButton()
        self.text_btn.setFixedSize(60, 36)
        self._update_color_btn(self.text_btn, self.text_color)
        self.text_btn.clicked.connect(self._pick_text_color)
        text_row = QHBoxLayout()
        text_row.addWidget(self.text_btn)
        text_row.addWidget(QLabel(self.text_color))
        self.text_label = text_row.itemAt(1).widget()
        text_row.addStretch()
        form.addRow('字体颜色:', text_row)

        self.font_family = current_settings.get('font_family', 'Microsoft YaHei')
        self.font_btn = QPushButton(self.font_family.split(',')[0].strip())
        self.font_btn.setMinimumWidth(200)
        self.font_btn.clicked.connect(self._pick_font)
        form.addRow('阅读字体:', self.font_btn)

        font_size_row = QHBoxLayout()
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(10, 36)
        self.font_size_slider.setValue(current_settings.get('font_size', 16))
        self.font_size_slider.setFixedWidth(180)
        font_size_row.addWidget(self.font_size_slider)
        self.font_size_val = QLabel(f'{self.font_size_slider.value()}px')
        self.font_size_val.setFixedWidth(45)
        font_size_row.addWidget(self.font_size_val)
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_val.setText(f'{v}px'))
        font_size_row.addStretch()
        form.addRow('字体大小:', font_size_row)

        line_height_row = QHBoxLayout()
        self.line_height_slider = QSlider(Qt.Horizontal)
        self.line_height_slider.setRange(10, 30)
        default_lh = int(current_settings.get('line_height', 1.8) * 10)
        self.line_height_slider.setValue(default_lh)
        self.line_height_slider.setFixedWidth(180)
        line_height_row.addWidget(self.line_height_slider)
        self.line_height_val = QLabel(f'{default_lh / 10:.1f}')
        self.line_height_val.setFixedWidth(45)
        line_height_row.addWidget(self.line_height_val)
        self.line_height_slider.valueChanged.connect(
            lambda v: self.line_height_val.setText(f'{v / 10:.1f}'))
        line_height_row.addStretch()
        form.addRow('行高:', line_height_row)

        self.indent_check = QCheckBox('段首缩进 2em')
        self.indent_check.setChecked(current_settings.get('indent', True))
        form.addRow('排版:', self.indent_check)

        self.justify_check = QCheckBox('两端对齐')
        self.justify_check.setChecked(current_settings.get('justify', True))
        form.addRow('', self.justify_check)

        layout.addLayout(form)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.HLine)
        layout.addWidget(sep2)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self._on_accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _update_color_btn(self, btn, color):
        btn.setStyleSheet(f'background-color: {color}; border: 2px solid #666; border-radius: 6px;')

    def _apply_preset(self, name):
        p = DEFAULT_READING_PRESETS[name]
        self.bg_color = p['bg_color']
        self.text_color = p['text_color']
        self.font_family = p['font_family']
        self._update_color_btn(self.bg_btn, self.bg_color)
        self._update_color_btn(self.text_btn, self.text_color)
        self.bg_label.setText(self.bg_color)
        self.text_label.setText(self.text_color)
        self.font_btn.setText(self.font_family.split(',')[0].strip())

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
        initial = QFont(self.font_family.split(',')[0].strip())
        font, ok = QFontDialog.getFont(initial, self, '选择阅读字体')
        if ok:
            self.font_family = font.family()
            self.font_btn.setText(font.family())

    def _on_accept(self):
        self.result_settings = {
            'bg_color': self.bg_color,
            'text_color': self.text_color,
            'font_family': self.font_family,
            'font_size': self.font_size_slider.value(),
            'line_height': self.line_height_slider.value() / 10,
            'indent': self.indent_check.isChecked(),
            'justify': self.justify_check.isChecked(),
        }
        self.accept()


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

        self.reading_settings = {
            'bg_color': '#1e1e2e',
            'text_color': '#cdd6f4',
            'font_family': 'Noto Serif SC, Microsoft YaHei, SimSun, serif',
            'font_size': 16,
            'line_height': 1.8,
            'indent': True,
            'justify': True,
        }

        self.settings = QSettings('EPUBReader', 'EPUBReader')
        self.load_settings()

        self.init_ui()
        self.apply_theme()

        self.app_icon = create_app_icon()
        self.setWindowIcon(self.app_icon)

        if self.recent_files:
            last_file = self.recent_files[0]
            if os.path.isfile(last_file):
                QTimer.singleShot(100, lambda: self.load_epub(last_file))

    def load_settings(self):
        self.is_dark_theme = self.settings.value('is_dark_theme', True, type=bool)
        self.last_opened_dir = self.settings.value('last_opened_dir', '', type=str)
        geometry = self.settings.value('geometry')
        if geometry:
            self.restoreGeometry(geometry)
        rs = self.settings.value('reading_settings')
        if rs:
            try:
                self.reading_settings = json.loads(rs)
            except (json.JSONDecodeError, TypeError):
                pass
        rf = self.settings.value('recent_files')
        if rf:
            try:
                self.recent_files = json.loads(rf)
            except (json.JSONDecodeError, TypeError):
                self.recent_files = []

    def save_settings(self):
        self.settings.setValue('is_dark_theme', self.is_dark_theme)
        self.settings.setValue('last_opened_dir', self.last_opened_dir)
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('reading_settings', json.dumps(self.reading_settings))
        self.settings.setValue('recent_files', json.dumps(self.recent_files))
        if self.book_file_path and self.current_chapter_index >= 0:
            self.settings.setValue(f'progress/{self.book_file_path}', self.current_chapter_index)

    def get_saved_progress(self, file_path):
        return self.settings.value(f'progress/{file_path}', -1, type=int)

    def init_ui(self):
        self.setWindowTitle('EPUB 阅读器')
        self.setMinimumSize(900, 600)
        self.resize(1300, 850)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)

        self.setup_menubar()

        self.splitter = QSplitter(Qt.Horizontal)

        left_panel = QTabWidget()
        left_panel.setFixedWidth(280)

        self.toc_list = QListWidget()
        self.toc_list.itemClicked.connect(self.toc_item_clicked)
        left_panel.addTab(self.toc_list, '目录')

        self.bookmark_list = QListWidget()
        self.bookmark_list.itemClicked.connect(self.bookmark_clicked)
        left_panel.addTab(self.bookmark_list, '书签')

        self.splitter.addWidget(left_panel)

        reading_container = QWidget()
        reading_layout = QVBoxLayout()
        reading_layout.setContentsMargins(0, 0, 0, 0)
        reading_layout.setSpacing(0)
        reading_container.setLayout(reading_layout)

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(False)
        self.text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text_browser.anchorClicked.connect(self.on_anchor_clicked)
        reading_layout.addWidget(self.text_browser)

        self.bottom_bar = QWidget()
        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(12, 4, 12, 4)
        bottom_layout.setSpacing(8)
        self.bottom_bar.setLayout(bottom_layout)

        self.prev_button = QPushButton('< 上一章')
        self.prev_button.clicked.connect(self.prev_chapter)
        self.prev_button.setEnabled(False)
        bottom_layout.addWidget(self.prev_button)

        self.chapter_label = QLabel('未加载文件')
        self.chapter_label.setAlignment(Qt.AlignCenter)
        bottom_layout.addWidget(self.chapter_label, 1)

        self.next_button = QPushButton('下一章 >')
        self.next_button.clicked.connect(self.next_chapter)
        self.next_button.setEnabled(False)
        bottom_layout.addWidget(self.next_button)

        reading_layout.addWidget(self.bottom_bar)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        reading_layout.addWidget(self.progress_bar)

        self.splitter.addWidget(reading_container)
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.splitter)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_label = QLabel('就绪')
        self.status_bar.addWidget(self.status_label, 1)

        self.setup_shortcuts()

    def setup_menubar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('文件(&F)')
        open_action = QAction('打开(&O)...', self)
        open_action.setShortcut(QKeySequence('Ctrl+O'))
        open_action.triggered.connect(self.open_epub_file)
        file_menu.addAction(open_action)
        add_file_action = QAction('添加到书架(&A)...', self)
        add_file_action.triggered.connect(self.add_file_to_shelf)
        file_menu.addAction(add_file_action)
        file_menu.addSeparator()
        self.recent_menu = file_menu.addMenu('最近打开(&R)')
        self._rebuild_recent_menu()
        file_menu.addSeparator()
        clear_history = QAction('清除历史(&C)', self)
        clear_history.triggered.connect(self.clear_recent_files)
        file_menu.addAction(clear_history)
        file_menu.addSeparator()
        exit_action = QAction('退出(&X)', self)
        exit_action.setShortcut(QKeySequence('Alt+F4'))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        view_menu = menubar.addMenu('视图(&V)')
        self.theme_action = QAction('切换主题(&T)', self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
        reading_settings_action = QAction('阅读设置(&R)...', self)
        reading_settings_action.triggered.connect(self.open_reading_settings)
        view_menu.addAction(reading_settings_action)
        view_menu.addSeparator()
        font_zoom_in = QAction('放大字体(&I)', self)
        font_zoom_in.setShortcut(QKeySequence('Ctrl+='))
        font_zoom_in.triggered.connect(self.font_size_up)
        view_menu.addAction(font_zoom_in)
        font_zoom_out = QAction('缩小字体(&D)', self)
        font_zoom_out.setShortcut(QKeySequence('Ctrl+-'))
        font_zoom_out.triggered.connect(self.font_size_down)
        view_menu.addAction(font_zoom_out)
        view_menu.addSeparator()
        sidebar_action = QAction('侧栏(&S)', self)
        sidebar_action.setShortcut(QKeySequence('F4'))
        sidebar_action.triggered.connect(self.toggle_sidebar)
        view_menu.addAction(sidebar_action)
        view_menu.addSeparator()
        fullscreen_action = QAction('全屏(&F)', self)
        fullscreen_action.setShortcut(QKeySequence('F11'))
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        immersive_action = QAction('沉浸式阅读(&I)', self)
        immersive_action.setShortcut(QKeySequence('F12'))
        immersive_action.triggered.connect(self.toggle_immersive)
        view_menu.addAction(immersive_action)

        nav_menu = menubar.addMenu('导航(&N)')
        prev_action = QAction('上一章(&P)', self)
        prev_action.setShortcut(QKeySequence('Left'))
        prev_action.triggered.connect(self.prev_chapter)
        nav_menu.addAction(prev_action)
        next_action = QAction('下一章(&N)', self)
        next_action.setShortcut(QKeySequence('Right'))
        next_action.triggered.connect(self.next_chapter)
        nav_menu.addAction(next_action)
        nav_menu.addSeparator()
        first_action = QAction('跳到首章(&H)', self)
        first_action.setShortcut(QKeySequence('Home'))
        first_action.triggered.connect(self.go_to_first_chapter)
        nav_menu.addAction(first_action)
        last_action = QAction('跳到末章(&E)', self)
        last_action.setShortcut(QKeySequence('End'))
        last_action.triggered.connect(self.go_to_last_chapter)
        nav_menu.addAction(last_action)

        tools_menu = menubar.addMenu('工具(&T)')
        search_action = QAction('搜索(&F)...', self)
        search_action.setShortcut(QKeySequence('Ctrl+F'))
        search_action.triggered.connect(self.open_search_dialog)
        tools_menu.addAction(search_action)
        tools_menu.addSeparator()
        bookmark_action = QAction('添加书签(&B)', self)
        bookmark_action.setShortcut(QKeySequence('Ctrl+B'))
        bookmark_action.triggered.connect(self.add_bookmark)
        tools_menu.addAction(bookmark_action)
        clear_bookmarks = QAction('清除所有书签(&C)', self)
        clear_bookmarks.triggered.connect(self.clear_all_bookmarks)
        tools_menu.addAction(clear_bookmarks)

        help_menu = menubar.addMenu('帮助(&H)')
        shortcuts_action = QAction('快捷键(&K)', self)
        shortcuts_action.triggered.connect(self.show_shortcuts_dialog)
        help_menu.addAction(shortcuts_action)
        help_menu.addSeparator()
        about_action = QAction('关于(&A)', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

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
        if not self._search_dialog:
            return
        query = self._search_dialog.search_input.text().strip()
        if not query or not self.chapters:
            return
        self.search_results = []
        self.search_current_index = -1
        for i, chapter in enumerate(self.chapters):
            try:
                content = chapter['item'].get_content()
                soup = BeautifulSoup(content, 'lxml')
                text = soup.get_text()
                if query.lower() in text.lower():
                    self.search_results.append(i)
            except Exception:
                pass
        if self.search_results:
            self.search_current_index = 0
            self._search_dialog.result_label.setText(f'找到 {len(self.search_results)} 章')
            self.load_chapter(self.search_results[0])
            self.text_browser.find(query)
        else:
            self._search_dialog.result_label.setText('未找到')

    def _search_prev(self):
        if self.search_results and self.search_current_index > 0:
            self.search_current_index -= 1
            self.load_chapter(self.search_results[self.search_current_index])
            query = self._search_dialog.search_input.text().strip()
            if query:
                self.text_browser.find(query)

    def _search_next(self):
        if self.search_results and self.search_current_index < len(self.search_results) - 1:
            self.search_current_index += 1
            self.load_chapter(self.search_results[self.search_current_index])
            query = self._search_dialog.search_input.text().strip()
            if query:
                self.text_browser.find(query)

    def toggle_immersive(self):
        self.is_immersive = not self.is_immersive
        bg = self.reading_settings.get('bg_color', '#1e1e2e')
        if self.is_immersive:
            self.menuBar().hide()
            self.statusBar().hide()
            self.bottom_bar.hide()
            self.progress_bar.hide()
            left = self.splitter.widget(0)
            if left.isVisible():
                self._sidebar_was_visible = True
                left.hide()
            else:
                self._sidebar_was_visible = False
            self.setStyleSheet('')
            self.text_browser.setStyleSheet(
                f'QTextBrowser {{ background-color: {bg}; border: none; padding: 30px 60px; }}'
            )
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
        msg.setText(
            '<h2 style="margin-bottom:2px;">EPUB 阅读器 v1.0.0</h2>'
            '<p style="color:#888;">一款简洁优雅的电子书阅读器</p>'
        )
        msg.setInformativeText(
            '功能特性：\n'
            '  • 支持 EPUB 格式电子书阅读\n'
            '  • 暗色 / 亮色双主题 + 自定义配色\n'
            '  • 自定义字体/颜色/大小/行高\n'
            '  • 章节目录导航与书签\n'
            '  • 全文搜索\n'
            '  • 阅读进度自动保存\n'
            '  • 沉浸式全屏阅读模式\n\n'
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
            ('Ctrl+O', '打开文件'),
            ('Ctrl+F', '搜索'),
            ('Ctrl+B', '添加书签'),
            ('Ctrl+=', '放大字体'),
            ('Ctrl+-', '缩小字体'),
            ('Left / Right', '上一章 / 下一章'),
            ('Home / End', '首章 / 末章'),
            ('F4', '切换侧栏'),
            ('F11', '全屏模式'),
            ('F12', '沉浸式阅读'),
            ('Esc', '退出全屏/沉浸'),
            ('Alt+F4', '退出程序'),
        ]
        table_rows = ''.join(
            f'<tr><td style="padding:4px 12px;"><code>{sc}</code></td>'
            f'<td style="padding:4px 12px;">{desc}</td></tr>'
            for sc, desc in shortcuts
        )
        html = (
            '<h3>键盘快捷键</h3>'
            '<table border="1" cellpadding="4" cellspacing="0" style="border-collapse:collapse;">'
            '<tr><th style="padding:4px 12px;">快捷键</th>'
            '<th style="padding:4px 12px;">功能</th></tr>'
            f'{table_rows}</table>'
        )
        dlg = QMessageBox(self)
        dlg.setWindowTitle('快捷键')
        dlg.setText(html)
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()

    def clear_all_bookmarks(self):
        self.bookmarks = {}
        self.bookmark_list.clear()
        if self.book_file_path:
            self.settings.remove(f'bookmarks/{self.book_file_path}')
        self.status_label.setText('已清除所有书签')

    def add_file_to_shelf(self):
        start_dir = self.last_opened_dir if self.last_opened_dir else ''
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, '添加EPUB文件到书架', start_dir, 'EPUB文件 (*.epub);;所有文件 (*)'
        )
        for fp in file_paths:
            if os.path.isfile(fp):
                self._add_to_recent(fp)
        if file_paths:
            self.status_label.setText(f'已添加 {len(file_paths)} 个文件到书架')

    def _add_to_recent(self, file_path):
        file_path = os.path.abspath(file_path)
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        self.recent_files = self.recent_files[:20]
        self._rebuild_recent_menu()
        self.save_settings()

    def _rebuild_recent_menu(self):
        if not self.recent_menu:
            return
        self.recent_menu.clear()
        for i, fp in enumerate(self.recent_files):
            if not os.path.isfile(fp):
                continue
            title = os.path.basename(fp)
            action = QAction(f'{i + 1}. {title}', self)
            action.setData(fp)
            action.triggered.connect(self._open_recent_file)
            self.recent_menu.addAction(action)
        if self.recent_menu.isEmpty():
            empty = QAction('(空)', self)
            empty.setEnabled(False)
            self.recent_menu.addAction(empty)

    def _open_recent_file(self):
        action = self.sender()
        if action:
            fp = action.data()
            if fp and os.path.isfile(fp):
                self.load_epub(fp)

    def clear_recent_files(self):
        self.recent_files = []
        self._rebuild_recent_menu()
        self.save_settings()
        self.status_label.setText('已清除文件历史')

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
        if left.isVisible():
            left.hide()
        else:
            left.show()

    def sync_browser_bg(self):
        bg = self.reading_settings.get('bg_color', '#1e1e2e')
        self.text_browser.setStyleSheet(
            f'QTextBrowser {{ background-color: {bg}; border: none; padding: 20px; }}'
        )

    def toggle_theme(self):
        self.is_dark_theme = not self.is_dark_theme
        self._sync_reading_settings_to_theme()
        self.apply_theme()
        if self.chapters:
            self.load_chapter(self.current_chapter_index)

    def _sync_reading_settings_to_theme(self):
        if self.is_dark_theme:
            default = DEFAULT_READING_PRESETS['dark']
        else:
            default = DEFAULT_READING_PRESETS['light']
        self.reading_settings['bg_color'] = default['bg_color']
        self.reading_settings['text_color'] = default['text_color']

    def apply_theme(self):
        stylesheet = STYLESHEET_DARK if self.is_dark_theme else STYLESHEET_LIGHT
        self.setStyleSheet(stylesheet)
        self.sync_browser_bg()

    def build_reading_html_style(self):
        s = self.reading_settings
        bg = s.get('bg_color', '#1e1e2e')
        tc = s.get('text_color', '#cdd6f4')
        ff = s.get('font_family', 'serif')
        fs = s.get('font_size', 16)
        lh = s.get('line_height', 1.8)
        indent = 'text-indent: 2em;' if s.get('indent', True) else ''
        justify = 'text-align: justify;' if s.get('justify', True) else ''

        btn_tint = '#89b4fa' if self.is_dark_theme else '#7287fd'
        btn_bg = '#181825' if self.is_dark_theme else '#e6e9ef'
        border_c = '#313244' if self.is_dark_theme else '#ccd0da'

        return f"""<style>
    body {{
        font-family: {ff};
        font-size: {fs}px;
        line-height: {lh};
        margin: 30px 40px;
        color: {tc};
        background-color: {bg};
    }}
    p {{ margin-bottom: 1em; {justify} {indent} }}
    h1 {{ color: {btn_tint}; font-size: 1.8em; margin-top: 1.5em; margin-bottom: 0.5em; border-bottom: 2px solid {border_c}; padding-bottom: 0.3em; }}
    h2 {{ font-size: 1.5em; margin-top: 1.3em; margin-bottom: 0.4em; }}
    h3 {{ font-size: 1.2em; margin-top: 1.1em; }}
    a {{ color: {btn_tint}; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    blockquote {{ border-left: 4px solid {btn_tint}; margin: 1em 0; padding: 0.5em 1em; background-color: {btn_bg}; border-radius: 0 8px 8px 0; }}
    hr {{ border: none; border-top: 1px solid {border_c}; margin: 2em 0; }}
    img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 1em auto; display: block; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1em 0; }}
    th, td {{ border: 1px solid {border_c}; padding: 8px 12px; text-align: left; }}
    th {{ background-color: {btn_bg}; }}
    code {{ background-color: {btn_bg}; padding: 2px 6px; border-radius: 4px; font-size: 0.9em; }}
    pre {{ background-color: {btn_bg}; padding: 1em; border-radius: 8px; overflow-x: auto; }}
    ul, ol {{ padding-left: 2em; }}
    li {{ margin-bottom: 0.3em; }}
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
        start_dir = self.last_opened_dir if self.last_opened_dir else ''
        file_path, _ = QFileDialog.getOpenFileName(
            self, '选择EPUB文件', start_dir, 'EPUB文件 (*.epub);;所有文件 (*)'
        )
        if file_path:
            self.last_opened_dir = os.path.dirname(file_path)
            self.load_epub(file_path)

    def load_epub(self, file_path):
        try:
            self.current_book = epub.read_epub(file_path)
            self.current_chapter_index = 0
            self.chapters = []
            self.book_file_path = file_path
            self.bookmarks = {}

            metadata = self.current_book.get_metadata('DC', 'title')
            self.book_title = metadata[0][0] if metadata else os.path.basename(file_path)

            self.toc_list.clear()
            self.bookmark_list.clear()

            self.build_chapters()
            self.populate_toc_list()

            saved_progress = self.get_saved_progress(file_path)
            start_index = max(0, saved_progress) if saved_progress >= 0 else 0

            if self.chapters:
                self.load_chapter(start_index)
                self.update_navigation_buttons()

            self.setWindowTitle(f'EPUB 阅读器 - {self.book_title}')
            self.status_label.setText(f'已加载: {self.book_title} | {len(self.chapters)} 章')
            self.load_bookmarks_for_book()
            self._add_to_recent(file_path)

        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法加载EPUB文件:\n{str(e)}')

    def build_chapters(self):
        toc_map = {}
        for item in self.current_book.toc:
            if isinstance(item, tuple):
                section, children = item
                if hasattr(section, 'href'):
                    toc_map[section.href.split('#')[0]] = section.title
                if children:
                    for child in children:
                        if hasattr(child, 'href'):
                            toc_map[child.href.split('#')[0]] = child.title
            elif hasattr(item, 'href'):
                toc_map[item.href.split('#')[0]] = item.title

        spine_ids = [item[0] if isinstance(item, (tuple, list)) else item for item in (self.current_book.spine or [])]

        seen = set()
        ordered_items = []

        for item_id in spine_ids:
            item = self.current_book.get_item_with_id(item_id)
            if item and item.get_type() == 9 and item_id not in seen:
                seen.add(item_id)
                ordered_items.append(item)

        if not ordered_items:
            for item in self.current_book.get_items():
                if item.get_type() == 9:
                    item_name = item.get_name()
                    if item_name not in seen:
                        seen.add(item_name)
                        ordered_items.append(item)

        for item in ordered_items:
            item_name = item.get_name()
            title = None
            for href, t in toc_map.items():
                if href == item_name or item_name.endswith('/' + href) or href.endswith('/' + item_name):
                    title = t
                    break

            if title is None:
                try:
                    content = item.get_content()
                    soup = BeautifulSoup(content, 'lxml')
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()
                    else:
                        h = soup.find(['h1', 'h2', 'h3'])
                        title = h.get_text(strip=True) if h else os.path.splitext(item_name)[0]
                except Exception:
                    title = os.path.splitext(item_name)[0]

            self.chapters.append({
                'title': title,
                'item': item,
            })

    def populate_toc_list(self):
        for i, chapter in enumerate(self.chapters):
            list_item = QListWidgetItem(chapter['title'])
            list_item.setData(Qt.UserRole, i)
            self.toc_list.addItem(list_item)

    def resolve_image(self, src, chapter_dir):
        if not self.current_book or not src:
            return None
        if src.startswith('data:'):
            return src
        resolved = os.path.normpath(os.path.join(chapter_dir, src))
        resolved = resolved.replace('\\', '/')
        for item in self.current_book.get_items():
            item_name = item.get_name().replace('\\', '/')
            if item_name == resolved or item_name.endswith('/' + resolved):
                try:
                    img_bytes = item.get_content()
                    mime = item.media_type or 'image/png'
                    if not mime.startswith('image/'):
                        mime = 'image/png'
                    b64 = base64.b64encode(img_bytes).decode('ascii')
                    return f'data:{mime};base64,{b64}'
                except Exception:
                    return None
        return None

    def load_chapter(self, index):
        if 0 <= index < len(self.chapters):
            self.current_chapter_index = index
            chapter = self.chapters[index]

            try:
                content = chapter['item'].get_content()
                soup = BeautifulSoup(content, 'lxml')

                for tag in soup(['script', 'style']):
                    tag.decompose()

                chapter_dir = os.path.dirname(chapter['item'].get_name())

                for img_tag in soup.find_all('img'):
                    src = img_tag.get('src')
                    if not src:
                        continue
                    img_data = self.resolve_image(src, chapter_dir)
                    if img_data:
                        img_tag['src'] = img_data

                for img_tag in soup.find_all('image'):
                    href = img_tag.get('xlink:href') or img_tag.get('href')
                    if not href:
                        continue
                    img_data = self.resolve_image(href, chapter_dir)
                    if img_data:
                        img_tag['xlink:href'] = img_data

                body = soup.find('body')
                if body:
                    html_content = body.decode_contents()
                else:
                    html_content = str(soup)

                style = self.build_reading_html_style()
                full_html = f'<html><head>{style}</head><body>{html_content}</body></html>'

                self.sync_browser_bg()
                self.text_browser.setHtml(full_html)
                self.text_browser.scrollToAnchor('')
                self.text_browser.verticalScrollBar().setValue(0)

                self.chapter_label.setText(
                    f'第 {index + 1}/{len(self.chapters)} 章 · {chapter["title"]}'
                )
                self.toc_list.setCurrentRow(index)

                progress = int((index + 1) / len(self.chapters) * 100)
                self.progress_bar.setValue(progress)

                self.status_label.setText(
                    f'{self.book_title} | 第 {index + 1}/{len(self.chapters)} 章 | {chapter["title"]}'
                )

                QTimer.singleShot(500, self.save_settings)

            except Exception as e:
                self.text_browser.setText(f'加载章节失败:\n{str(e)}')

            self.update_navigation_buttons()

    def on_anchor_clicked(self, url):
        href = url.toString()
        fragment = url.fragment()
        target_file = href.split('#')[0] if '#' in href else href
        if not target_file and fragment:
            self.text_browser.scrollToAnchor(fragment)
            return
        for i, chapter in enumerate(self.chapters):
            item_name = chapter['item'].get_name()
            if item_name == target_file or item_name.endswith('/' + target_file):
                self.load_chapter(i)
                if fragment:
                    QTimer.singleShot(300, lambda f=fragment: self.text_browser.scrollToAnchor(f))
                return

    def toc_item_clicked(self, item):
        index = item.data(Qt.UserRole)
        if index is not None:
            self.load_chapter(index)

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
        chapter = self.chapters[self.current_chapter_index]
        scroll_pos = self.text_browser.verticalScrollBar().value()
        key = f'{self.current_chapter_index}_{scroll_pos}'
        bookmark_name = f'第{self.current_chapter_index + 1}章 - {chapter["title"]}'
        self.bookmarks[key] = {
            'chapter_index': self.current_chapter_index,
            'scroll_pos': scroll_pos,
            'title': bookmark_name,
        }
        self.save_bookmarks_to_settings()
        list_item = QListWidgetItem(bookmark_name)
        list_item.setData(Qt.UserRole, key)
        self.bookmark_list.addItem(list_item)
        self.status_label.setText(f'已添加书签: {bookmark_name}')

    def bookmark_clicked(self, item):
        key = item.data(Qt.UserRole)
        if key in self.bookmarks:
            bm = self.bookmarks[key]
            self.load_chapter(bm['chapter_index'])
            QTimer.singleShot(300, lambda: self.text_browser.verticalScrollBar().setValue(bm['scroll_pos']))

    def save_bookmarks_to_settings(self):
        if self.book_file_path:
            data = {}
            for key, bm in self.bookmarks.items():
                data[key] = bm
            self.settings.setValue(f'bookmarks/{self.book_file_path}', json.dumps(data))

    def load_bookmarks_for_book(self):
        self.bookmark_list.clear()
        self.bookmarks = {}
        if self.book_file_path:
            data_str = self.settings.value(f'bookmarks/{self.book_file_path}', '', type=str)
            if data_str:
                try:
                    data = json.loads(data_str)
                    for key, bm in data.items():
                        self.bookmarks[key] = bm
                        list_item = QListWidgetItem(bm['title'])
                        list_item.setData(Qt.UserRole, key)
                        self.bookmark_list.addItem(list_item)
                except (json.JSONDecodeError, KeyError):
                    pass

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)
