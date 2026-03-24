#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qasync

from PySide6.QtWidgets import QDialog

from baramFlow.base.dynamic_mesh.motion_function import FunctionType, MotionFunction

from .rotation_dialog_ui import Ui_RotationDialog
from .rotating_oscillation_dialog_ui import Ui_RotatingOscillationDialog
from .linear_translation_dialog_ui import Ui_LinearTranslationDialog
from .linear_oscillation_dialog_ui import Ui_LinearOscillationDialog
from .manual_position_dialog_ui import Ui_ManualPositionDialog


class RotationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_RotationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.origin.setVector(motionFunction.center)
        self._ui.axis.setVector(motionFunction.axis)
        self._ui.speed.setText(motionFunction.omega)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.center = self._ui.origin.vector('Origin')
        self._mf.axis = self._ui.axis.vector('Axis')
        self._mf.omega = self._ui.speed.text()
        self.accept()


class RotatingOscillationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_RotatingOscillationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.origin.setVector(motionFunction.center)
        self._ui.amplitude.setVector(motionFunction.angularAmplitude)
        self._ui.speed.setText(motionFunction.omega)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.center = self._ui.origin.vector('Origin')
        self._mf.angularAmplitude = self._ui.amplitude.vector('Amplitude')
        self._mf.omega = self._ui.speed.text()
        self.accept()


class LinearTranslationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_LinearTranslationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.velocity.setVector(motionFunction.velocity)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.velocity = self._ui.velocity.vector('Velocity')
        self.accept()


class LinearOscillationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_LinearOscillationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.amplitude.setVector(motionFunction.linearAmplitude)
        self._ui.frequency.setText(motionFunction.frequency)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.linearAmplitude = self._ui.amplitude.vector('Amplitude')
        self._mf.frequency = self._ui.frequency.text()
        self.accept()


class ManualPositionDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_ManualPositionDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.cog.setVector(motionFunction.center)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.center = self._ui.cog.vector('Center of Gravity')
        self.accept()


MOTION_FUNCTION_DIALOGS = {
    FunctionType.ROTATION: RotationDialog,
    FunctionType.ROTATING_OSCILLATION: RotatingOscillationDialog,
    FunctionType.LINEAR_TRANSLATION: LinearTranslationDialog,
    FunctionType.LINEAR_OSCILLATION: LinearOscillationDialog,
    FunctionType.MANUAL_POSITION: ManualPositionDialog,
}
