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

        self._ui.originX.setText(motionFunction.centerX)
        self._ui.originY.setText(motionFunction.centerY)
        self._ui.originZ.setText(motionFunction.centerZ)
        self._ui.axisX.setText(motionFunction.axisX)
        self._ui.axisY.setText(motionFunction.axisY)
        self._ui.axisZ.setText(motionFunction.axisZ)
        self._ui.speed.setText(motionFunction.omega)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.centerX = self._ui.originX.text()
        self._mf.centerY = self._ui.originY.text()
        self._mf.centerZ = self._ui.originZ.text()
        self._mf.axisX = self._ui.axisX.text()
        self._mf.axisY = self._ui.axisY.text()
        self._mf.axisZ = self._ui.axisZ.text()
        self._mf.omega = self._ui.speed.text()
        self.accept()


class RotatingOscillationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_RotatingOscillationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.originX.setText(motionFunction.centerX)
        self._ui.originY.setText(motionFunction.centerY)
        self._ui.originZ.setText(motionFunction.centerZ)
        self._ui.amplitudeX.setText(motionFunction.angularAmplitudeX)
        self._ui.amplitudeY.setText(motionFunction.angularAmplitudeY)
        self._ui.amplitudeZ.setText(motionFunction.angularAmplitudeZ)
        self._ui.speed.setText(motionFunction.omega)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.centerX = self._ui.originX.text()
        self._mf.centerY = self._ui.originY.text()
        self._mf.centerZ = self._ui.originZ.text()
        self._mf.angularAmplitudeX = self._ui.amplitudeX.text()
        self._mf.angularAmplitudeY = self._ui.amplitudeY.text()
        self._mf.angularAmplitudeZ = self._ui.amplitudeZ.text()
        self._mf.omega = self._ui.speed.text()
        self.accept()


class LinearTranslationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_LinearTranslationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.velocityX.setText(motionFunction.velocityX)
        self._ui.velocityY.setText(motionFunction.velocityY)
        self._ui.velocityZ.setText(motionFunction.velocityZ)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.velocityX = self._ui.velocityX.text()
        self._mf.velocityY = self._ui.velocityY.text()
        self._mf.velocityZ = self._ui.velocityZ.text()
        self.accept()


class LinearOscillationDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_LinearOscillationDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.amplitudeX.setText(motionFunction.linearAmplitudeX)
        self._ui.amplitudeY.setText(motionFunction.linearAmplitudeY)
        self._ui.amplitudeZ.setText(motionFunction.linearAmplitudeZ)
        self._ui.frequency.setText(motionFunction.frequency)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.linearAmplitudeX = self._ui.amplitudeX.text()
        self._mf.linearAmplitudeY = self._ui.amplitudeY.text()
        self._mf.linearAmplitudeZ = self._ui.amplitudeZ.text()
        self._mf.frequency = self._ui.frequency.text()
        self.accept()


class ManualPositionDialog(QDialog):
    def __init__(self, parent, motionFunction: MotionFunction):
        super().__init__(parent)
        self._ui = Ui_ManualPositionDialog()
        self._ui.setupUi(self)
        self._mf = motionFunction

        self._ui.cogX.setText(motionFunction.centerX)
        self._ui.cogY.setText(motionFunction.centerY)
        self._ui.cogZ.setText(motionFunction.centerZ)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._mf.centerX = self._ui.cogX.text()
        self._mf.centerY = self._ui.cogY.text()
        self._mf.centerZ = self._ui.cogZ.text()
        self.accept()


MOTION_FUNCTION_DIALOGS = {
    FunctionType.ROTATION: RotationDialog,
    FunctionType.ROTATING_OSCILLATION: RotatingOscillationDialog,
    FunctionType.LINEAR_TRANSLATION: LinearTranslationDialog,
    FunctionType.LINEAR_OSCILLATION: LinearOscillationDialog,
    FunctionType.MANUAL_POSITION: ManualPositionDialog,
}
