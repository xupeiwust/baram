#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qasync

from PySide6.QtWidgets import QDialog

from baramFlow.base.dynamic_mesh.restraint import Restraint, RestraintType
from libbaram.pfloat import PFloat
from widgets.async_message_box import AsyncMessageBox

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
        try:
            dampingConstant = str(PFloat(self._ui.dampingConstant.text(), self.tr('Damping Constant')))
        except ValueError as e:
            await AsyncMessageBox().warning(self, self.tr('Warning'), str(e))
            return

        self._restraint.dampingConstant = dampingConstant
        self.accept()


class TranslationalSpringDialog(QDialog):
    def __init__(self, parent, restraint: Restraint):
        super().__init__(parent)
        self._ui = Ui_TranslationalSpringDialog()
        self._ui.setupUi(self)
        self._restraint = restraint

        self._ui.attachmentPoint.setVector(restraint.attachmentPoint)
        self._ui.anchorPoint.setVector(restraint.anchorPoint)
        self._ui.restLength.setText(restraint.restLength)
        self._ui.springConstant.setText(restraint.springConstant)
        self._ui.dampingConstant.setText(restraint.dampingConstant)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        try:
            attachmentPoint = self._ui.attachmentPoint.vector('Attachment Point')
            anchorPoint = self._ui.anchorPoint.vector('Anchor Point')
            restLength = str(PFloat(self._ui.restLength.text(), self.tr('Rest Length')))
            springConstant = str(PFloat(self._ui.springConstant.text(), self.tr('Spring Constant')))
            dampingConstant = str(PFloat(self._ui.dampingConstant.text(), self.tr('Damping Constant')))
        except ValueError as e:
            await AsyncMessageBox().warning(self, self.tr('Warning'), str(e))
            return

        self._restraint.attachmentPoint = attachmentPoint
        self._restraint.anchorPoint = anchorPoint
        self._restraint.restLength = restLength
        self._restraint.springConstant = springConstant
        self._restraint.dampingConstant = dampingConstant
        self.accept()


class RotationalSpringDialog(QDialog):
    def __init__(self, parent, restraint: Restraint):
        super().__init__(parent)
        self._ui = Ui_RotationalSpringDialog()
        self._ui.setupUi(self)
        self._restraint = restraint

        self._ui.axis.setVector(restraint.axis)
        self._ui.springConstant.setText(restraint.springConstant)
        self._ui.dampingConstant.setText(restraint.dampingConstant)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        try:
            axis = self._ui.axis.vector('Axis')
            springConstant = str(PFloat(self._ui.springConstant.text(), self.tr('Spring Constant')))
            dampingConstant = str(PFloat(self._ui.dampingConstant.text(), self.tr('Damping Constant')))
        except ValueError as e:
            await AsyncMessageBox().warning(self, self.tr('Warning'), str(e))
            return

        self._restraint.axis = axis
        self._restraint.springConstant = springConstant
        self._restraint.dampingConstant = dampingConstant
        self.accept()


RESTRAINT_DIALOGS = {
    RestraintType.SIMPLE_DAMPER: SimpleDamperDialog,
    RestraintType.TRANSLATIONAL_SPRING: TranslationalSpringDialog,
    RestraintType.ROTATIONAL_SPRING: RotationalSpringDialog,
}
