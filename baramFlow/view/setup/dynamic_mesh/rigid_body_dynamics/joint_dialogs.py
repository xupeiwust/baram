#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qasync

from PySide6.QtWidgets import QDialog

from baramFlow.base.dynamic_mesh.rigid_body_dynamics import Joint, JointType

from .prismatic_joint_dialog_ui import Ui_PrismaticJointDialog
from .revolute_joint_dialog_ui import Ui_RevoluteJointDialog


class PrismaticJointDialog(QDialog):
    def __init__(self, parent, joint: Joint):
        super().__init__(parent)
        self._ui = Ui_PrismaticJointDialog()
        self._ui.setupUi(self)
        self._joint = joint

        self._ui.directionX.setText(joint.directionX)
        self._ui.directionY.setText(joint.directionY)
        self._ui.directionZ.setText(joint.directionZ)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._joint.directionX = self._ui.directionX.text()
        self._joint.directionY = self._ui.directionY.text()
        self._joint.directionZ = self._ui.directionZ.text()
        self.accept()


class RevoluteJointDialog(QDialog):
    def __init__(self, parent, joint: Joint):
        super().__init__(parent)
        self._ui = Ui_RevoluteJointDialog()
        self._ui.setupUi(self)
        self._joint = joint

        self._ui.axisX.setText(joint.axisX)
        self._ui.axisY.setText(joint.axisY)
        self._ui.axisZ.setText(joint.axisZ)

        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _accept(self):
        self._joint.axisX = self._ui.axisX.text()
        self._joint.axisY = self._ui.axisY.text()
        self._joint.axisZ = self._ui.axisZ.text()
        self.accept()


JOINT_DIALOGS = {
    JointType.PRISMATIC: PrismaticJointDialog,
    JointType.REVOLUTE: RevoluteJointDialog,
}
