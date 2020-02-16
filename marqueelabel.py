from PyQt5 import QtWidgets,QtGui,QtCore,QtMultimedia

class marqueelabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super(marqueelabel, self).__init__(parent)
        self.px = 0
        self.py = 15
        
        self._direction = QtCore.Qt.RightToLeft #Qt.LeftToRight
        self.setWordWrap(True)
        self.timer = QtCore.QTimer(self, interval=20)
        self.timer.timeout.connect(self.update)
        self.timer.start()
        self._speed = 1
        self.textLength = 0
        self.fontPointSize = 0
        self.setAlignment(QtCore.Qt.AlignVCenter)
        self.setFixedHeight(self.fontMetrics().height())

    def set_height(self):
        self.setFixedHeight(self.fontMetrics().height())
        self.setAlignment(QtCore.Qt.AlignVCenter)

    def setFont(self, font, size=8):
#        newfont = QtGui.QFont(font, size, QtGui.QFont.Bold)
        newfont = QtGui.QFont(font)
        QtWidgets.QLabel.setFont(self, newfont)
        self.setFixedHeight(self.fontMetrics().height())


    def updateCoordinates(self):
#        self.px=-self.textLength-self._speed-5
        align = self.alignment()
        if align == QtCore.Qt.AlignTop:
            self.py = 10
        elif align == QtCore.Qt.AlignBottom:
            self.py = self.height() - 10
        elif align == QtCore.Qt.AlignVCenter:
            self.py = self.height() / 2
        self.fontPointSize = self.font().pointSize() / 2
        self.textLength = self.fontMetrics().width(self.text())

    def setAlignment(self, alignment):
        self.updateCoordinates()
        QtWidgets.QLabel.setAlignment(self, alignment)

    def resizeEvent(self, event):
        self.updateCoordinates()
        QtWidgets.QLabel.resizeEvent(self, event)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        if self._direction == QtCore.Qt.RightToLeft:
            self.px -= self.speed()
            if self.px <= -self.textLength:
                self.px = self.width()
        else:
            self.px += self.speed()
            if self.px >= self.width():
                self.px = -self.textLength
        painter.drawText(self.px, self.py + self.fontPointSize, self.text())
        painter.translate(self.px, 0)

    def speed(self):
        return self._speed

    def setSpeed(self, speed):
        self._speed = speed

    def setDirection(self, direction):
        self._direction = direction
        if self._direction == QtCore.Qt.RightToLeft:
            self.px = self.width() - self.textLength
        else:
            self.px = 0
        self.update()

    def pause(self):
        self.timer.stop()

    def unpause(self):
        self.timer.start()