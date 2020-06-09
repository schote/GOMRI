# This Python file uses the following encoding: utf-8
from PySide2.QtWidgets import QApplication
from PySide2.QtQuick import QQuickView
from PySide2.QtCore import QUrl


if __name__ == "__main__":

    app = QApplication([])
    view = QQuickView()
    url = QUrl("view.qml")

    view.setSource(url)
    view.show()
    app.exec_()
