#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qasync

from PySide6.QtWidgets import QDialog

from baramFlow.base.dynamic_mesh.restraint import Restraint, RestraintType

from .simple_damper_dialog_ui import Ui_SimpleDamperDialog
from .translational_spring_dialog_ui import Ui_TranslationalSpringDialog
from .rotational_spring_dialog_ui import Ui_RotationalSpringDialog


class SimpleDamperDialog(QDialog):
    def __init__(self, parent, restraint: Restraint):
        super().__init__(parent)
        self._ui = Ui_SimpleDamperDialog()
        self._ui.setupUi(self)
        self._restraint = restraint

        self._ui.dampingConstant.setText(restraint.dampingConstant)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._restraint.dampingConstant = self._ui.dampingConstant.text()
        self.accept()


class TranslationalSpringDialog(QDialog):
    def __init__(self, parent, restraint: Restraint):
        super().__init__(parent)
        self._ui = Ui_TranslationalSpringDialog()
        self._ui.setupUi(self)
        self._restraint = restraint

        self._ui.attachmentPointX.setText(restraint.attachmentPointX)
        self._ui.attachmentPointY.setText(restraint.attachmentPointY)
        self._ui.attachmentPointZ.setText(restraint.attachmentPointZ)
        self._ui.anchorPointX.setText(restraint.anchorPointX)
        self._ui.anchorPointY.setText(restraint.anchorPointY)
        self._ui.anchorPointZ.setText(restraint.anchorPointZ)
        self._ui.restLength.setText(restraint.restLength)
        self._ui.springConstant.setText(restraint.springConstant)
        self._ui.dampingConstant.setText(restraint.dampingConstant)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._restraint.attachmentPointX = self._ui.attachmentPointX.text()
        self._restraint.attachmentPointY = self._ui.attachmentPointY.text()
        self._restraint.attachmentPointZ = self._ui.attachmentPointZ.text()
        self._restraint.anchorPointX = self._ui.anchorPointX.text()
        self._restraint.anchorPointY = self._ui.anchorPointY.text()
        self._restraint.anchorPointZ = self._ui.anchorPointZ.text()
        self._restraint.restLength = self._ui.restLength.text()
        self._restraint.springConstant = self._ui.springConstant.text()
        self._restraint.dampingConstant = self._ui.dampingConstant.text()
        self.accept()


class RotationalSpringDialog(QDialog):
    def __init__(self, parent, restraint: Restraint):
        super().__init__(parent)
        self._ui = Ui_RotationalSpringDialog()
        self._ui.setupUi(self)
        self._restraint = restraint

        self._ui.axisX.setText(restraint.axisX)
        self._ui.axisY.setText(restraint.axisY)
        self._ui.axisZ.setText(restraint.axisZ)
        self._ui.springConstant.setText(restraint.springConstant)
        self._ui.dampingConstant.setText(restraint.dampingConstant)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._restraint.axisX = self._ui.axisX.text()
        self._restraint.axisY = self._ui.axisY.text()
        self._restraint.axisZ = self._ui.axisZ.text()
        self._restraint.springConstant = self._ui.springConstant.text()
        self._restraint.dampingConstant = self._ui.dampingConstant.text()
        self.accept()


RESTRAINT_DIALOGS = {
    RestraintType.SIMPLE_DAMPER: SimpleDamperDialog,
    RestraintType.TRANSLATIONAL_SPRING: TranslationalSpringDialog,
    RestraintType.ROTATIONAL_SPRING: RotationalSpringDialog,
}
