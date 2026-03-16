#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import QWidget

from baramFlow.base.dynamic_mesh.motion_function import MotionFunction, FunctionType

from .motion_function_widget_ui import Ui_MotionFunctionWidget


FUNCTION_TYPE_NAMES = {
    FunctionType.ROTATION: 'Rotation',
    FunctionType.ROTATING_OSCILLATION: 'Rotating Oscillation',
    FunctionType.LINEAR_TRANSLATION: 'Linear Translation',
    FunctionType.LINEAR_OSCILLATION: 'Linear Oscillation',
    FunctionType.MANUAL_POSITION: 'Manual Position',
}


class MotionFunctionWidget(QWidget):
    def __init__(self, motionFunction: MotionFunction):
        super().__init__()

        self._motionFunction = motionFunction

        self._ui = Ui_MotionFunctionWidget()
        self._ui.setupUi(self)

        self.setFixedHeight(48)
        self.load()

    @property
    def motionFunction(self) -> MotionFunction:
        return self._motionFunction

    def load(self):
        f = self._motionFunction
        self._ui.nameLabel.setText(FUNCTION_TYPE_NAMES.get(f.functionType, str(f.functionType.value)))

        detail = ''
        if f.functionType == FunctionType.ROTATION:
            detail = f'{f.omega} rpm'
        elif f.functionType == FunctionType.ROTATING_OSCILLATION:
            detail = f'{f.omega} rpm'
        elif f.functionType == FunctionType.LINEAR_TRANSLATION:
            detail = f'({f.velocityX}, {f.velocityY}, {f.velocityZ}) m/s'
        elif f.functionType == FunctionType.LINEAR_OSCILLATION:
            detail = f'{f.frequency} Hz'
        elif f.functionType == FunctionType.MANUAL_POSITION:
            detail = 'Manual Positions'

        self._ui.detailLabel.setText(detail)
