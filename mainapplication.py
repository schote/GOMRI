import sys
import os

from PySide2.QtCore import QObject, Signal, Property, QUrl
from PySide2.QtGui import QGuiApplication
from PySide2.QtQml import QQmlApplicationEngine

class Backend(QObject):
    textChanged = Signal(str)

    def __init__(self, parent=None):
        QObject.__init__(self, parent)
        self.m_text = ""

    @Property(str, notify=textChanged)
    def text(self):
        return self.m_text

    @text.setter
    def setText(self, text):
        if self.m_text == text:
            return
        self.m_text = text
        self.textChanged.emit(self.m_text)


if __name__ == '__main__':

    app = QGuiApplication(sys.argv)

    backend = Backend()
    backend.textChanged.connect(lambda text: print(text))

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("backend", backend)

    path = os.path.abspath(os.path.dirname(__file__))
    qml_file = os.path.join(path, 'view/view.qml')

    engine.load(QUrl.fromLocalFile(qml_file))

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec_())
