import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from epub_reader import EPUBReader, create_app_icon


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName('EPUB 阅读器')
    app.setWindowIcon(create_app_icon())

    reader = EPUBReader()
    reader.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
