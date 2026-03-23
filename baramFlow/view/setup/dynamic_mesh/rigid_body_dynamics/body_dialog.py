#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from uuid import UUID

import qasync

from PySide6.QtWidgets import QDialog, QMenu, QListWidgetItem

from baramFlow.base.dynamic_mesh.rigid_body_dynamics import Body, Joint, JointType
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.view.setup.dynamic_mesh.rigid_body_dynamics.joint_widget import JointWidget, JOINT_TYPE_NAMES
from baramFlow.view.setup.dynamic_mesh.rigid_body_dynamics.joint_dialogs import JOINT_DIALOGS
from baramFlow.view.widgets.multi_selector_dialog import MultiSelectorDialog
from widgets.async_message_box import AsyncMessageBox

from .body_dialog_ui import Ui_BodyDialog


class BodyDialog(QDialog):
    NONE_UUID = UUID(int=0)

    def __init__(self, parent, body: Body, existingBodies: list[tuple[UUID, str]]):
        """
        existingBodies: list of (uuid, name) tuples for all bodies except this one,
                        used for parent selection.
        """
        super().__init__(parent)

        self._ui = Ui_BodyDialog()
        self._ui.setupUi(self)

        self._body = body
        self._joints = [deepcopy(j) for j in body.joints]
        self._boundaries = list(body.boundaries)
        self._existingNames = {bName for bUuid, bName in existingBodies if bUuid != body.uuid}
        self._dialog = None

        # Name and Parent
        self._ui.name.setText(body.name)
        self._ui.parentCombo.addItem(self.tr('None'), self.NONE_UUID)
        for bUuid, bName in existingBodies:
            if bUuid != body.uuid:
                self._ui.parentCombo.addItem(bName, bUuid)
        idx = self._ui.parentCombo.findData(body.parent)
        if idx >= 0:
            self._ui.parentCombo.setCurrentIndex(idx)

        # Mass Properties
        self._ui.mass.setText(body.mass)
        self._ui.com.setVector(body.centerOfMass)
        self._ui.cor.setVector(body.centerOfRotation)

        # Orientation Tensor
        oriValues = body.orientation.split() if body.orientation.strip() else ['1','0','0','0','1','0','0','0','1']
        while len(oriValues) < 9:
            oriValues.append('0')
        oriEdits = [
            [self._ui.ori00, self._ui.ori01, self._ui.ori02],
            [self._ui.ori10, self._ui.ori11, self._ui.ori12],
            [self._ui.ori20, self._ui.ori21, self._ui.ori22],
        ]
        for i in range(3):
            for j in range(3):
                oriEdits[i][j].setText(oriValues[i * 3 + j])

        # Moment of Inertia Tensor
        moiValues = body.momentOfInertia.split() if body.momentOfInertia.strip() else ['1','0','0','0','1','0','0','0','1']
        while len(moiValues) < 9:
            moiValues.append('0')
        moiEdits = [
            [self._ui.moi00, self._ui.moi01, self._ui.moi02],
            [self._ui.moi10, self._ui.moi11, self._ui.moi12],
            [self._ui.moi20, self._ui.moi21, self._ui.moi22],
        ]
        for i in range(3):
            for j in range(3):
                moiEdits[i][j].setText(moiValues[i * 3 + j])

        # Mesh Deformation
        self._ui.deformationOffset.setText(body.deformationOffset)
        self._ui.deformationDistance.setText(body.deformationDistance)

        # Add Joint menu
        jointMenu = QMenu(self._ui.addJointButton)
        for jt in JointType:
            action = jointMenu.addAction(JOINT_TYPE_NAMES[jt])
            action.triggered.connect(lambda checked=False, jtype=jt: self._addJoint(jtype))
        self._ui.addJointButton.setMenu(jointMenu)

        self._setBoundaries(self._boundaries)
        self._connectSignalsSlots()
        self._loadJoints()

    def _connectSignalsSlots(self):
        self._ui.selectBoundariesButton.clicked.connect(self._selectBoundariesClicked)
        self._ui.jointList.customContextMenuRequested.connect(self._showJointContextMenu)
        self._ui.buttonBox.accepted.connect(self._accept)
        self._ui.buttonBox.rejected.connect(self.reject)

    @qasync.asyncSlot()
    async def _selectBoundariesClicked(self):
        boundaries = BoundaryDB.getBoundarySelectorItems()
        self._dialog = MultiSelectorDialog(self, self.tr("Select Boundaries"), boundaries, self._boundaries)
        self._dialog.accepted.connect(self._boundariesChanged)
        self._dialog.open()

    @qasync.asyncSlot()
    async def _boundariesChanged(self):
        self._setBoundaries(self._dialog.selectedItems())

    def _setBoundaries(self, boundaries):
        self._boundaries = boundaries
        self._ui.boundariesList.clear()
        for bcid in boundaries:
            self._ui.boundariesList.addItem(BoundaryDB.getBoundaryText(bcid))

    def _loadJoints(self):
        self._ui.jointList.clear()
        for j in self._joints:
            widget = JointWidget(j)
            item = QListWidgetItem()
            item.setSizeHint(widget.size())
            self._ui.jointList.addItem(item)
            self._ui.jointList.setItemWidget(item, widget)

    def _addJoint(self, jointType: JointType):
        joint = Joint(jointType=jointType)
        dialogClass = JOINT_DIALOGS.get(jointType)
        if dialogClass:
            dialog = dialogClass(self, joint)
            if not dialog.exec():
                return
        # Spherical has no dialog, just add directly
        self._joints.append(joint)
        widget = JointWidget(joint)
        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        self._ui.jointList.addItem(item)
        self._ui.jointList.setItemWidget(item, widget)

    def _showJointContextMenu(self, pos):
        row = self._ui.jointList.currentRow()
        if row < 0:
            return
        menu = QMenu(self)
        if row > 0:
            menu.addAction(self.tr('Move Up')).triggered.connect(lambda: self._moveJoint(row, row - 1))
        if row < self._ui.jointList.count() - 1:
            menu.addAction(self.tr('Move Down')).triggered.connect(lambda: self._moveJoint(row, row + 1))
        joint = self._joints[row]
        if joint.jointType != JointType.SPHERICAL:
            menu.addAction(self.tr('Edit')).triggered.connect(self._editJoint)
        menu.addAction(self.tr('Remove')).triggered.connect(self._removeJoint)
        menu.exec(self._ui.jointList.mapToGlobal(pos))

    def _moveJoint(self, fromRow, toRow):
        self._joints[fromRow], self._joints[toRow] = self._joints[toRow], self._joints[fromRow]
        self._loadJoints()
        self._ui.jointList.setCurrentRow(toRow)

    def _editJoint(self):
        row = self._ui.jointList.currentRow()
        if row < 0:
            return
        joint = self._joints[row]
        dialogClass = JOINT_DIALOGS.get(joint.jointType)
        if dialogClass:
            dialog = dialogClass(self, joint)
            if dialog.exec():
                widget = self._ui.jointList.itemWidget(self._ui.jointList.item(row))
                if isinstance(widget, JointWidget):
                    widget.load()

    def _removeJoint(self):
        row = self._ui.jointList.currentRow()
        if row >= 0:
            del self._joints[row]
            self._ui.jointList.takeItem(row)

    @qasync.asyncSlot()
    async def _accept(self):
        name = self._ui.name.text()
        if name in self._existingNames:
            await AsyncMessageBox().warning(self, self.tr('Warning'),
                                            self.tr('The name "{0}" is already in use.').format(name))
            return

        if not self._boundaries:
            await AsyncMessageBox().warning(self, self.tr('Warning'),
                                            self.tr('At least one boundary must be selected.'))
            return

        self._body.name = name
        self._body.parent = self._ui.parentCombo.currentData()

        self._body.mass = self._ui.mass.text()
        self._body.centerOfMass = self._ui.com.vector('Center of Mass')
        self._body.centerOfRotation = self._ui.cor.vector('Center of Rotation')

        oriEdits = [
            [self._ui.ori00, self._ui.ori01, self._ui.ori02],
            [self._ui.ori10, self._ui.ori11, self._ui.ori12],
            [self._ui.ori20, self._ui.ori21, self._ui.ori22],
        ]
        oriValues = []
        for i in range(3):
            for j in range(3):
                oriValues.append(oriEdits[i][j].text())
        self._body.orientation = ' '.join(oriValues)

        moiEdits = [
            [self._ui.moi00, self._ui.moi01, self._ui.moi02],
            [self._ui.moi10, self._ui.moi11, self._ui.moi12],
            [self._ui.moi20, self._ui.moi21, self._ui.moi22],
        ]
        moiValues = []
        for i in range(3):
            for j in range(3):
                moiValues.append(moiEdits[i][j].text())
        self._body.momentOfInertia = ' '.join(moiValues)

        self._body.boundaries = self._boundaries
        self._body.joints = self._joints
        self._body.deformationOffset = self._ui.deformationOffset.text()
        self._body.deformationDistance = self._ui.deformationDistance.text()

        self.accept()
