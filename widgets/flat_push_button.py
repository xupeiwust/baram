#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QPushButton, QStyle, QStyleOptionButton, QStylePainter
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter


class FlatPushButton(QPushButton):
    doubleClicked = Signal()

    _CHECKED_BG = QColor(76, 194, 255, 100)  # Dart mode highlight color of Windows

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        option = QStyleOptionButton()
        self.initStyleOption(option)
        if option.state & QStyle.StateFlag.State_On:
            rect = self.style().subElementRect(QStyle.SubElement.SE_PushButtonContents, option, self)
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(self._CHECKED_BG)
            painter.drawRoundedRect(rect, 4, 4)
            painter.end()
            sp = QStylePainter(self)
            sp.drawControl(QStyle.ControlElement.CE_PushButtonLabel, option)
        elif option.state & (QStyle.StateFlag.State_MouseOver | QStyle.StateFlag.State_Sunken):
            super().paintEvent(event)
        else:
            painter = QStylePainter(self)
            painter.drawControl(QStyle.ControlElement.CE_PushButtonLabel, option)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        super().mouseDoubleClickEvent(event)
        self.doubleClicked.emit()
