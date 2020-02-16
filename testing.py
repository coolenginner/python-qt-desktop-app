from PyQt5 import QtGui, QtCore,QtWidgets
import sys
from PyQt5.QtCore import Qt

class aspect_label(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(aspect_label, self).__init__(parent)
        self.setFrameStyle(QtWidgets.QFrame.StyledPanel)
        self.pixmap = QtGui.QPixmap(r'')
        self.setAlignment(QtCore.Qt.AlignLeft)

    def setPixmap(self,pixmap):
        self.pixmap=pixmap

    def paintEvent(self, event):
        size = self.size()
        painter = QtGui.QPainter(self)
        point = QtCore.QPoint(0,0)
        scaledPix = self.pixmap.scaled(size, Qt.KeepAspectRatio, transformMode = Qt.SmoothTransformation)
        # start painting the label from left upper corner
        point.setX((size.width() - scaledPix.width())/2)
        point.setY((size.height() - scaledPix.height())/2)
#        print (point.x(), ' ', point.y())
        painter.drawPixmap(point, scaledPix)

