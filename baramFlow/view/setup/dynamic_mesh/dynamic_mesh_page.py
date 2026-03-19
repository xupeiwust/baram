#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4, UUID

import qasync

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QListWidgetItem, QMenu, QWidget,
                                QVBoxLayout, QHBoxLayout, QMessageBox)

from baramFlow.base.dynamic_mesh.dynamic_mesh import DYNAMIC_MESH_PATH, DynamicMesh, MotionType
from baramFlow.base.dynamic_mesh.motion_definition import MotionDefinition
from baramFlow.coredb import coredb
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.cell_zone_db import CellZoneDB
from baramFlow.base.dynamic_mesh.moving_boundary import MovingBoundaryEntry, PointMotionType
from baramFlow.base.dynamic_mesh.rigid_body_dynamics import Body
from baramFlow.base.dynamic_mesh.rigid_body_solver import SolverType
from baramFlow.base.dynamic_mesh.restraint import Restraint, RestraintType

from baramFlow.services.dynamic_mesh.dynamic_mesh_service import DynamicMeshService
from baramFlow.view.setup.dynamic_mesh.motion_type_dialog import MotionTypeDialog
from baramFlow.view.setup.dynamic_mesh.moving_cell_zone.motion_definition_dialog import MotionDefinitionDialog
from baramFlow.view.setup.dynamic_mesh.moving_boundary.point_motion_dialog import (
    PointMotionDialog, POINT_MOTION_TYPE_NAMES,
)
from baramFlow.view.setup.dynamic_mesh.restraints.restraint_widget import RestraintWidget, RESTRAINT_TYPE_NAMES
from baramFlow.view.setup.dynamic_mesh.restraints.restraint_dialogs import RESTRAINT_DIALOGS
from baramFlow.view.setup.dynamic_mesh.rigid_body_dynamics.body_dialog import BodyDialog
from baramFlow.view.widgets.content_page import ContentPage

from widgets.async_message_box import AsyncMessageBox

from .dynamic_mesh_page_ui import Ui_DynamicMeshPage


MOTION_TYPE_NAMES = {
    MotionType.NONE: 'None',
    MotionType.MOVING_CELL_ZONE: 'Moving Cell Zone',
    MotionType.MOVING_BOUNDARY: 'Moving Boundary',
    MotionType.RIGID_BODY_DYNAMICS: 'Rigid Body Dynamics',
}


class DynamicMeshPage(ContentPage):
    def __init__(self, parent):
        super().__init__(parent)

        self._ui = Ui_DynamicMeshPage()
        self._ui.setupUi(self)

        self._dynamicMesh = DynamicMeshService().getDynamicMesh()  # self.__init__ is called again if another mesh is imported

        # Solver combo items
        self._ui.rbdSolverCombo.addItem('Newmark', SolverType.NEWMARK)
        self._ui.rbdSolverCombo.addItem('Crank-Nicolson', SolverType.CRANK_NICOLSON)
        self._ui.rbdSolverCombo.addItem('Symplectic', SolverType.SYMPLECTIC)

        # Add Restraint menu
        restraintMenu = QMenu(self._ui.addRestraintButton)
        for rt in RestraintType:
            action = restraintMenu.addAction(RESTRAINT_TYPE_NAMES[rt])
            action.triggered.connect(lambda checked=False, rtype=rt: self._addRbdRestraint(rtype))
        self._ui.addRestraintButton.setMenu(restraintMenu)

        self._connectSignalsSlots()

        self._updatePage()

    def _connectSignalsSlots(self):
        self._ui.changeTypeButton.clicked.connect(self._changeMotionType)

        # Moving Cell Zone
        self._ui.mdList.customContextMenuRequested.connect(self._showMdContextMenu)
        self._ui.mdList.itemDoubleClicked.connect(self._editMotionDefinition)
        self._ui.addMdButton.clicked.connect(self._addMotionDefinition)

        # Moving Boundary
        self._ui.mbList.itemDoubleClicked.connect(self._editBoundary)
        self._ui.editBoundaryButton.clicked.connect(self._editBoundary)
        self._ui.mbList.currentItemChanged.connect(
            lambda: self._ui.editBoundaryButton.setEnabled(self._ui.mbList.currentRow() >= 0))

        # Rigid Body Dynamics
        self._ui.rbdSolverCombo.currentIndexChanged.connect(self._rbdSolverChanged)
        self._ui.bodyList.itemDoubleClicked.connect(self._editBody)
        self._ui.addBodyButton.clicked.connect(self._addBody)
        self._ui.editBodyButton.clicked.connect(self._editBody)
        self._ui.removeBodyButton.clicked.connect(self._removeBody)
        self._ui.bodyList.currentItemChanged.connect(self._bodySelected)
        self._ui.rbdRestraintList.customContextMenuRequested.connect(self._showRbdRestraintMenu)

    def _updatePage(self):
        mt = self._dynamicMesh.motionType
        self._ui.motionTypeLabel.setText(MOTION_TYPE_NAMES[mt])
        if mt == MotionType.NONE:
            self._ui.stack.setCurrentWidget(self._ui.nonePage)
        elif mt == MotionType.MOVING_CELL_ZONE:
            self._ui.stack.setCurrentWidget(self._ui.movingCellZonePage)
            self._updateMotionDefinitions()
        elif mt == MotionType.MOVING_BOUNDARY:
            self._ui.stack.setCurrentWidget(self._ui.movingBoundaryPage)
            self._updateMovingBoundaries()
        elif mt == MotionType.RIGID_BODY_DYNAMICS:
            self._ui.stack.setCurrentWidget(self._ui.rigidBodyDynamicsPage)
            self._updateRigidBodyDynamics()

    @qasync.asyncSlot()
    async def _changeMotionType(self):
        dialog = MotionTypeDialog(self, self._dynamicMesh.motionType)
        if not dialog.exec():
            return

        newType = dialog.selectedType
        if newType == self._dynamicMesh.motionType:
            return

        confirm = await AsyncMessageBox().question(
            self, self.tr('Warning'),
            self.tr('Changing Motion Type will clear current configuration.\nContinue?'))
        if confirm != QMessageBox.StandardButton.Yes:
            return

        self._dynamicMesh.motionType=newType

        self._updatePage()

    # ── Moving Cell Zone ──

    def _updateMotionDefinitions(self):
        self._ui.mdList.clear()
        for md in self._dynamicMesh.motionDefinitions:
            self._addMdItem(md)

    def _addMotionDefinition(self):
        order = len(self._dynamicMesh.motionDefinitions) + 1
        md = MotionDefinition(name=f'Motion-{order}', order=order)
        dialog = MotionDefinitionDialog(self, md)
        if dialog.exec():
            self._dynamicMesh.motionDefinitions.append(md)
            self._addMdItem(md)

    def _addMdItem(self, md: MotionDefinition):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(0)
        nameLabel = QLabel(f'<b>{md.name}</b>')
        czText = ', '.join(CellZoneDB.getCellZoneText(z) for z in md.cellZones) if md.cellZones else self.tr('Entire Domain')
        czLabel = QLabel(czText)
        czLabel.setStyleSheet('color:grey')
        layout.addWidget(nameLabel)
        layout.addWidget(czLabel)
        widget.setFixedHeight(48)

        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        item.setData(Qt.ItemDataRole.UserRole, md.uuid)
        self._ui.mdList.addItem(item)
        self._ui.mdList.setItemWidget(item, widget)

    def _showMdContextMenu(self, pos):
        row = self._ui.mdList.currentRow()
        if row < 0:
            return
        menu = QMenu(self)
        if row > 0:
            menu.addAction(self.tr('Move Up')).triggered.connect(lambda: self._moveMd(row, row - 1))
        if row < self._ui.mdList.count() - 1:
            menu.addAction(self.tr('Move Down')).triggered.connect(lambda: self._moveMd(row, row + 1))
        menu.addAction(self.tr('Edit')).triggered.connect(self._editMotionDefinition)
        menu.addAction(self.tr('Remove')).triggered.connect(self._removeMd)
        menu.exec(self._ui.mdList.mapToGlobal(pos))

    def _moveMd(self, fromRow, toRow):
        mds = self._dynamicMesh.motionDefinitions
        mds[fromRow], mds[toRow] = mds[toRow], mds[fromRow]
        self._updateMotionDefinitions()
        self._ui.mdList.setCurrentRow(toRow)

    def _editMotionDefinition(self):
        row = self._ui.mdList.currentRow()
        if row < 0:
            return
        md = self._dynamicMesh.motionDefinitions[row]
        dialog = MotionDefinitionDialog(self, md)
        if dialog.exec():
            self._updateMotionDefinitions()

    def _removeMd(self):
        row = self._ui.mdList.currentRow()
        if row >= 0:
            del self._dynamicMesh.motionDefinitions[row]
            self._ui.mdList.takeItem(row)

    # ── Moving Boundary ──

    def _updateMovingBoundaries(self):
        self._ui.mbList.clear()
        for entry in self._dynamicMesh.movingBoundaries:
            self._addMbItem(entry)

    def _addMbItem(self, entry: MovingBoundaryEntry):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)

        name = BoundaryDB.getBoundaryName(entry.boundary)
        nameLabel = QLabel(f'<b>{name}</b>')
        typeLabel = QLabel(POINT_MOTION_TYPE_NAMES.get(entry.pointMotionType, ''))
        typeLabel.setStyleSheet('color:grey')

        layout.addWidget(nameLabel, 1)
        layout.addWidget(typeLabel)
        widget.setFixedHeight(40)

        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        item.setData(Qt.ItemDataRole.UserRole, entry.uuid)
        self._ui.mbList.addItem(item)
        self._ui.mbList.setItemWidget(item, widget)

    def _editBoundary(self):
        item = self._ui.mbList.currentItem()
        if item is None:
            return
        uuid = item.data(Qt.ItemDataRole.UserRole)
        entry = next(mb for mb in self._dynamicMesh.movingBoundaries if mb.uuid == uuid)
        dialog = PointMotionDialog(self, entry)
        if dialog.exec():
            self._updateMovingBoundaries()

    # ── Rigid Body Dynamics ──

    def _updateRigidBodyDynamics(self):
        rbd = self._dynamicMesh.rigidBodyDynamics

        # Solver
        idx = self._ui.rbdSolverCombo.findData(rbd.solver.solverType)
        if idx >= 0:
            self._ui.rbdSolverCombo.setCurrentIndex(idx)
        self._ui.rbdVelCoeff.setText(rbd.solver.velocityIntegrationCoefficient)
        self._ui.rbdPosCoeff.setText(rbd.solver.positionIntegrationCoefficient)
        self._ui.rbdAccOffCoeff.setText(rbd.solver.offCenteringAccelerationCoefficient)
        self._ui.rbdVelOffCoeff.setText(rbd.solver.offCenteringVelocityCoefficient)

        self._ui.rbdRelaxation.setText(rbd.accelerationRelaxationFactor)
        self._ui.rbdDamping.setText(rbd.accelerationDampingFactor)

        # Bodies
        self._ui.bodyList.clear()
        for body in rbd.bodies:
            self._addBodyItem(body)

        # Restraints
        self._ui.rbdRestraintList.clear()
        for r in rbd.restraints:
            self._addRbdRestraintItem(r)

    def _rbdSolverChanged(self, index):
        solverType = self._ui.rbdSolverCombo.itemData(index)
        if solverType == SolverType.NEWMARK:
            self._ui.rbdSolverStack.setCurrentIndex(0)
        elif solverType == SolverType.CRANK_NICOLSON:
            self._ui.rbdSolverStack.setCurrentIndex(1)
        elif solverType == SolverType.SYMPLECTIC:
            self._ui.rbdSolverStack.setCurrentIndex(2)
        else:
            self._ui.rbdSolverStack.setCurrentIndex(2)

    def _addBodyItem(self, body: Body):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 4, 8, 4)
        nameLabel = QLabel(f'<b>{body.name}</b>')
        massLabel = QLabel(f'{body.mass} kg')
        massLabel.setStyleSheet('color:grey')
        layout.addWidget(nameLabel, 1)
        layout.addWidget(massLabel)
        widget.setFixedHeight(40)

        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        item.setData(Qt.ItemDataRole.UserRole, body.uuid)
        self._ui.bodyList.addItem(item)
        self._ui.bodyList.setItemWidget(item, widget)

    def _bodySelected(self):
        enabled = self._ui.bodyList.currentRow() >= 0
        self._ui.editBodyButton.setEnabled(enabled)
        self._ui.removeBodyButton.setEnabled(enabled)

    def _addBody(self):
        body = Body(uuid=uuid4(), name='body', parent=UUID(int=0))
        existingBodies = [(b.uuid, b.name) for b in self._dynamicMesh.rigidBodyDynamics.bodies]
        dialog = BodyDialog(self, body, existingBodies)
        if dialog.exec():
            self._dynamicMesh.rigidBodyDynamics.bodies.append(body)
            self._addBodyItem(body)

    def _editBody(self):
        row = self._ui.bodyList.currentRow()
        if row < 0:
            return
        body = self._dynamicMesh.rigidBodyDynamics.bodies[row]
        existingBodies = [(b.uuid, b.name) for b in self._dynamicMesh.rigidBodyDynamics.bodies]
        dialog = BodyDialog(self, body, existingBodies)
        if dialog.exec():
            self._updateRigidBodyDynamics()

    @qasync.asyncSlot()
    async def _removeBody(self):
        row = self._ui.bodyList.currentRow()
        if row < 0:
            return

        body = self._dynamicMesh.rigidBodyDynamics.bodies[row]

        # Check if body is used as parent
        for b in self._dynamicMesh.rigidBodyDynamics.bodies:
            if b.parent == body.uuid:
                await AsyncMessageBox().warning(
                    self, self.tr('Warning'),
                    self.tr('Cannot remove body that is used as a parent.'))
                return

        confirm = await AsyncMessageBox().question(
            self, self.tr('Remove Body'),
            self.tr('Remove "{}"?').format(body.name))
        if confirm == QMessageBox.StandardButton.Yes:
            del self._dynamicMesh.rigidBodyDynamics.bodies[row]
            self._ui.bodyList.takeItem(row)

    def _addRbdRestraint(self, restraintType: RestraintType):
        order = self._ui.rbdRestraintList.count() + 1
        restraint = Restraint(uuid=uuid4(), order=order, restraintType=restraintType)
        dialogClass = RESTRAINT_DIALOGS.get(restraintType)
        if dialogClass:
            dialog = dialogClass(self, restraint)
            if not dialog.exec():
                return
        self._dynamicMesh.rigidBodyDynamics.restraints.append(restraint)
        self._addRbdRestraintItem(restraint)

    def _addRbdRestraintItem(self, restraint: Restraint):
        widget = RestraintWidget(restraint)
        item = QListWidgetItem()
        item.setSizeHint(widget.size())
        self._ui.rbdRestraintList.addItem(item)
        self._ui.rbdRestraintList.setItemWidget(item, widget)

    def _showRbdRestraintMenu(self, pos):
        row = self._ui.rbdRestraintList.currentRow()
        if row < 0:
            return
        menu = QMenu(self)
        if row > 0:
            menu.addAction(self.tr('Move Up')).triggered.connect(
                lambda: self._moveRbdRestraint(row, row - 1))
        if row < self._ui.rbdRestraintList.count() - 1:
            menu.addAction(self.tr('Move Down')).triggered.connect(
                lambda: self._moveRbdRestraint(row, row + 1))
        menu.addAction(self.tr('Edit')).triggered.connect(self._editRbdRestraint)
        menu.addAction(self.tr('Remove')).triggered.connect(self._removeRbdRestraint)
        menu.exec(self._ui.rbdRestraintList.mapToGlobal(pos))

    def _moveRbdRestraint(self, fromRow, toRow):
        rs = self._dynamicMesh.rigidBodyDynamics.restraints
        rs[fromRow], rs[toRow] = rs[toRow], rs[fromRow]
        self._updateRigidBodyDynamics()
        self._ui.rbdRestraintList.setCurrentRow(toRow)

    def _editRbdRestraint(self):
        row = self._ui.rbdRestraintList.currentRow()
        if row < 0:
            return
        restraint = self._dynamicMesh.rigidBodyDynamics.restraints[row]
        dialogClass = RESTRAINT_DIALOGS.get(restraint.restraintType)
        if dialogClass:
            dialog = dialogClass(self, restraint)
            if dialog.exec():
                widget = self._ui.rbdRestraintList.itemWidget(self._ui.rbdRestraintList.item(row))
                if isinstance(widget, RestraintWidget):
                    widget.load()

    def _removeRbdRestraint(self):
        row = self._ui.rbdRestraintList.currentRow()
        if row >= 0:
            del self._dynamicMesh.rigidBodyDynamics.restraints[row]
            self._ui.rbdRestraintList.takeItem(row)
