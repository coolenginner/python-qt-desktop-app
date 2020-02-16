# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'label_combo.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_label_combo(object):
    def setupUi(self, label_combo):
        label_combo.setObjectName("label_combo")
        label_combo.resize(640, 480)
        self.gridLayout = QtWidgets.QGridLayout(label_combo)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(label_combo)
        self.label.setMinimumSize(QtCore.QSize(1, 1))
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap("weather.png"))
        self.label.setScaledContents(True)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(label_combo)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 1, 1, 1)

        self.retranslateUi(label_combo)
        QtCore.QMetaObject.connectSlotsByName(label_combo)

    def retranslateUi(self, label_combo):
        _translate = QtCore.QCoreApplication.translate
        label_combo.setWindowTitle(_translate("label_combo", "Form"))
        self.label_2.setText(_translate("label_combo", "20"))




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    label_combo = QtWidgets.QWidget()
    ui = Ui_label_combo()
    ui.setupUi(label_combo)
    label_combo.show()
    sys.exit(app.exec_())
