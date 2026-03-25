#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel

from baramFlow.base.xml_helper import Vector
from libbaram.pfloat import PFloat
from widgets.pfloat_line_edit import PFloatLineEdit


class VectorWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)

        self._x = PFloatLineEdit('0')
        self._y = PFloatLineEdit('0')
        self._z = PFloatLineEdit('0')

        layout = QHBoxLayout(self)
        layout.addWidget(QLabel('('))
        layout.addWidget(self._x)
        layout.addWidget(QLabel(','))
        layout.addWidget(self._y)
        layout.addWidget(QLabel(','))
        layout.addWidget(self._z)
        layout.addWidget(QLabel(')'))
        layout.setContentsMargins(0, 0, 0, 0)

    def setVector(self, vector):
        self._x.setText(vector.x)
        self._y.setText(vector.y)
        self._z.setText(vector.z)

    def vector(self, name):
        return Vector(
            str(PFloat(self._x.text(), name)), str(PFloat(self._y.text(), name)), str(PFloat(self._z.text(), name)))
