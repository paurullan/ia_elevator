#!/usr/bin/env python 
# -*- coding: utf-8 -*-

__version__ = "0.0.1"

from igu import MainWindow

import sys

from PyQt4.QtGui import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    sys.exit()

