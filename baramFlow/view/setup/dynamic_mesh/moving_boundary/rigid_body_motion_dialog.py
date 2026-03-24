#!/usr/bin/env python
# -*- coding: utf-8 -*-

from copy import deepcopy
from uuid import uuid4

import qasync

from PySide6.QtCore import Qt
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import QDialog, QListWidget, QListWidgetItem, QMenu, QToolButton, QVBoxLayout

from baramFlow.base.dynamic_mesh.moving_boundary import (
    RigidBodyMotion, TranslationalConstraintType, RotationalConstraintType,
)
from baramFlow.base.dynamic_mesh.rigid_body_solver import RigidBodySolver, SolverType
from baramFlow.base.dynamic_mesh.restraint import Restraint, RestraintType
from baramFlow.view.setup.dynamic_mesh.restraints.restraint_widget import RestraintWidget, RESTRAINT_TYPE_NAMES
from baramFlow.view.setup.dynamic_mesh.restraints.restraint_dialogs import RESTRAINT_DIALOGS
from .rigid_body_motion_dialog_ui import Ui_RigidBodyMotionDialog


_SOLVER_TYPE_NAMES = {
    SolverType.NEWMARK: 'Newmark',
    SolverType.CRANK_NICOLSON: 'Crank-Nicolson',
    SolverType.SYMPLECTIC: 'Symplectic',
}

# Map combo box index to solver type
_SOLVER_TYPES = [SolverType.NEWMARK, SolverType.CRANK_NICOLSON, SolverType.SYMPLECTIC]

# Newmark and Symplectic use integration coefficients (page 0),
# Crank-Nicolson uses off-centering coefficients (page 1)
_SOLVER_STACKED_INDEX = {
    SolverType.NEWMARK: 0,
    SolverType.CRANK_NICOLSON: 1,
    SolverType.SYMPLECTIC: 2,
}


class RigidBodyMotionDialog(QDialog):
    def __init__(self, parent, model: RigidBodyMotion):
        super().__init__(parent)
        self._ui = Ui_RigidBodyMotionDialog()
        self._ui.setupUi(self)

        self.setWindowTitle(self.tr('Rigid Body Motion'))

        self._model = model
        self._restraints: list[Restraint] = [deepcopy(r) for r in model.restraints]

        self._setupRestraintsList()
        self._setupValidators()
        self._setupSolverComboBox()
        self._connectSignals()
        self._load()

    # ------------------------------------------------------------------ setup
    def _setupRestraintsList(self):
        """Create a QListWidget inside the restraints scroll area."""
        self._restraintList = QListWidget()
        self._restraintList.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._restraintList.customContextMenuRequested.connect(self._showRestraintContextMenu)

        layout = QVBoxLayout(self._ui.scrollAreaWidgetContents)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._restraintList)

        # Add button
        addBtn = QToolButton()
        addBtn.setText(self.tr('Add Restraint'))
        addBtn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        addMenu = QMenu(addBtn)
        for rt in RestraintType:
            action = addMenu.addAction(RESTRAINT_TYPE_NAMES[rt])
            action.triggered.connect(lambda checked=False, rtype=rt: self._addRestraint(rtype))
        addBtn.setMenu(addMenu)
        layout.addWidget(addBtn)

    def _setupValidators(self):
        validator = QDoubleValidator()
        fields = [
            self._ui.mass,
            # Orientation tensor (3x3)
            self._ui.ori00, self._ui.ori01, self._ui.ori02,
            self._ui.ori10, self._ui.ori11, self._ui.ori12,
            self._ui.ori20, self._ui.ori21, self._ui.ori22,
            # Moment of Inertia tensor (3x3)
            self._ui.moi00, self._ui.moi01, self._ui.moi02,
            self._ui.moi10, self._ui.moi11, self._ui.moi12,
            self._ui.moi20, self._ui.moi21, self._ui.moi22,
            # Limit angle
            self._ui.clockwise, self._ui.counterclockwise,
            # Integration coefficients
            self._ui.velocityIntegrationCoefficient, self._ui.positionIntegrationCoefficient,
            # Off-centering coefficients
            self._ui.offCenteringAccelerationCoefficient, self._ui.offCenteringVelocityCoefficient,
            # Acceleration factors
            self._ui.accelerationRelaxationFactor, self._ui.accelerationDampingFactor,
        ]
        for field in fields:
            field.setValidator(validator)

    def _setupSolverComboBox(self):
        for st in _SOLVER_TYPES:
            self._ui.solverCombo.addItem(_SOLVER_TYPE_NAMES[st])

    def _connectSignals(self):
        # Solver type combo box -> stacked widget
        self._ui.solverCombo.currentIndexChanged.connect(self._solverTypeChanged)

        # Translational constraint radio buttons
        self._ui.translationalFreeRadio.toggled.connect(self._translationalConstraintChanged)
        self._ui.translationalFixedRadio.toggled.connect(self._translationalConstraintChanged)
        self._ui.translationalDirectionalRadio.toggled.connect(self._translationalConstraintChanged)
        self._ui.translationalPlanarRadio.toggled.connect(self._translationalConstraintChanged)

        # Rotational constraint radio buttons
        self._ui.rotationalFreeRadio.toggled.connect(self._rotationalConstraintChanged)
        self._ui.rotationalFixedRadio.toggled.connect(self._rotationalConstraintChanged)
        self._ui.rotationalAxisRadio.toggled.connect(self._rotationalConstraintChanged)

        # Ok / Cancel
        self._ui.okButton.clicked.connect(self._accept)
        self._ui.cancelButton.clicked.connect(self.reject)

    # ------------------------------------------------------------------ load
    def _load(self):
        m = self._model

        # Mass
        self._ui.mass.setText(m.mass)

        # Center of Mass
        self._ui.centerOfMass.setVector(m.centerOfMass)

        # Center of Rotation
        self._ui.centerOfRotation.setVector(m.centerOfRotation)

        # Orientation tensor (row-major: 9 space-separated values)
        orientValues = (m.orientation or '1 0 0 0 1 0 0 0 1').split()
        if len(orientValues) == 9:
            orientFields = [
                self._ui.ori00, self._ui.ori01, self._ui.ori02,
                self._ui.ori10, self._ui.ori11, self._ui.ori12,
                self._ui.ori20, self._ui.ori21, self._ui.ori22,
            ]
            for field, val in zip(orientFields, orientValues):
                field.setText(val)

        # Moment of Inertia tensor (row-major: 9 space-separated values)
        moiValues = (m.momentOfInertia or '0 0 0 0 0 0 0 0 0').split()
        if len(moiValues) == 9:
            moiFields = [
                self._ui.moi00, self._ui.moi01, self._ui.moi02,
                self._ui.moi10, self._ui.moi11, self._ui.moi12,
                self._ui.moi20, self._ui.moi21, self._ui.moi22,
            ]
            for field, val in zip(moiFields, moiValues):
                field.setText(val)

        # Translational constraint
        radioMap = {
            TranslationalConstraintType.FREE: self._ui.translationalFreeRadio,
            TranslationalConstraintType.FIXED: self._ui.translationalFixedRadio,
            TranslationalConstraintType.LINE: self._ui.translationalDirectionalRadio,
            TranslationalConstraintType.PLANE: self._ui.translationalPlanarRadio,
        }
        radioMap[m.translationalConstraintType].setChecked(True)

        # Direction (line constraint)
        self._ui.direction.setVector(m.direction)

        # Normal (plane constraint)
        self._ui.normal.setVector(m.normal)

        # Rotational constraint
        rotRadioMap = {
            RotationalConstraintType.FREE: self._ui.rotationalFreeRadio,
            RotationalConstraintType.FIXED: self._ui.rotationalFixedRadio,
            RotationalConstraintType.AXIS: self._ui.rotationalAxisRadio,
        }
        rotRadioMap[m.rotationalConstraintType].setChecked(True)

        # Axis (rotation constraint)
        self._ui.axis.setVector(m.axis)

        # Limit angle
        self._ui.limitAngleGroup.setChecked(m.limitAngle)
        self._ui.clockwise.setText(m.clockwise)
        self._ui.counterclockwise.setText(m.counterclockwise)

        # Solver
        solver = m.solver
        solverIndex = _SOLVER_TYPES.index(solver.solverType)
        self._ui.solverCombo.setCurrentIndex(solverIndex)
        self._ui.solverStack.setCurrentIndex(_SOLVER_STACKED_INDEX[solver.solverType])

        self._ui.velocityIntegrationCoefficient.setText(solver.velocityIntegrationCoefficient)
        self._ui.positionIntegrationCoefficient.setText(solver.positionIntegrationCoefficient)
        self._ui.offCenteringAccelerationCoefficient.setText(solver.offCenteringAccelerationCoefficient)
        self._ui.offCenteringVelocityCoefficient.setText(solver.offCenteringVelocityCoefficient)

        # Acceleration factors
        self._ui.accelerationRelaxationFactor.setText(m.accelerationRelaxationFactor)
        self._ui.accelerationDampingFactor.setText(m.accelerationDampingFactor)

        # Constraint visibility
        self._updateTranslationalConstraintWidgets()
        self._updateRotationalConstraintWidgets()

        # Restraints
        self._loadRestraints()

    # -------------------------------------------------------- constraint UIs
    def _translationalConstraintChanged(self):
        self._updateTranslationalConstraintWidgets()

    def _rotationalConstraintChanged(self):
        self._updateRotationalConstraintWidgets()

    def _updateTranslationalConstraintWidgets(self):
        self._ui.direction.setEnabled(self._ui.translationalDirectionalRadio.isChecked())
        self._ui.normal.setEnabled(self._ui.translationalPlanarRadio.isChecked())

    def _updateRotationalConstraintWidgets(self):
        axisSelected = self._ui.rotationalAxisRadio.isChecked()
        self._ui.axis.setEnabled(axisSelected)
        self._ui.limitAngleGroup.setEnabled(axisSelected)

    # --------------------------------------------------------- solver
    def _solverTypeChanged(self, index):
        if 0 <= index < len(_SOLVER_TYPES):
            solverType = _SOLVER_TYPES[index]
            self._ui.solverStack.setCurrentIndex(_SOLVER_STACKED_INDEX[solverType])

    # --------------------------------------------------------- restraints
    def _loadRestraints(self):
        self._restraintList.clear()
        for r in self._restraints:
            self._addRestraintItem(r)

    def _addRestraintItem(self, restraint: Restraint):
        widget = RestraintWidget(restraint)
        item = QListWidgetItem()
        item.setSizeHint(widget.sizeHint())
        self._restraintList.addItem(item)
        self._restraintList.setItemWidget(item, widget)

    def _addRestraint(self, restraintType: RestraintType):
        restraint = Restraint(
            uuid=uuid4(),
            order=len(self._restraints) + 1,
            restraintType=restraintType,
        )
        dialogClass = RESTRAINT_DIALOGS.get(restraintType)
        if dialogClass:
            dialog = dialogClass(self, restraint)
            if dialog.exec():
                self._restraints.append(restraint)
                self._addRestraintItem(restraint)

    def _showRestraintContextMenu(self, pos):
        row = self._restraintList.currentRow()
        if row < 0:
            return

        menu = QMenu(self)
        if row > 0:
            menu.addAction(self.tr('Move Up')).triggered.connect(lambda: self._moveRestraint(row, row - 1))
        if row < self._restraintList.count() - 1:
            menu.addAction(self.tr('Move Down')).triggered.connect(lambda: self._moveRestraint(row, row + 1))
        menu.addAction(self.tr('Edit')).triggered.connect(self._editRestraint)
        menu.addAction(self.tr('Remove')).triggered.connect(self._removeRestraint)
        menu.exec(self._restraintList.mapToGlobal(pos))

    def _moveRestraint(self, fromRow, toRow):
        self._restraints[fromRow], self._restraints[toRow] = \
            self._restraints[toRow], self._restraints[fromRow]
        self._loadRestraints()
        self._restraintList.setCurrentRow(toRow)

    def _editRestraint(self):
        row = self._restraintList.currentRow()
        if row < 0:
            return
        restraint = self._restraints[row]
        dialogClass = RESTRAINT_DIALOGS.get(restraint.restraintType)
        if dialogClass:
            dialog = dialogClass(self, restraint)
            if dialog.exec():
                widget = self._restraintList.itemWidget(self._restraintList.item(row))
                if isinstance(widget, RestraintWidget):
                    widget.load()

    def _removeRestraint(self):
        row = self._restraintList.currentRow()
        if row >= 0:
            del self._restraints[row]
            self._restraintList.takeItem(row)

    # ------------------------------------------------------------------ save
    def _selectedTranslationalConstraintType(self) -> TranslationalConstraintType:
        if self._ui.translationalFreeRadio.isChecked():
            return TranslationalConstraintType.FREE
        elif self._ui.translationalFixedRadio.isChecked():
            return TranslationalConstraintType.FIXED
        elif self._ui.translationalDirectionalRadio.isChecked():
            return TranslationalConstraintType.LINE
        elif self._ui.translationalPlanarRadio.isChecked():
            return TranslationalConstraintType.PLANE
        return TranslationalConstraintType.FREE

    def _selectedRotationalConstraintType(self) -> RotationalConstraintType:
        if self._ui.rotationalFreeRadio.isChecked():
            return RotationalConstraintType.FREE
        elif self._ui.rotationalFixedRadio.isChecked():
            return RotationalConstraintType.FIXED
        elif self._ui.rotationalAxisRadio.isChecked():
            return RotationalConstraintType.AXIS
        return RotationalConstraintType.FREE

    @qasync.asyncSlot()
    async def _accept(self):
        m = self._model

        # Mass
        m.mass = self._ui.mass.text()

        # Center of Mass
        m.centerOfMass = self._ui.centerOfMass.vector('Center of Mass')

        # Center of Rotation
        m.centerOfRotation = self._ui.centerOfRotation.vector('Center of Rotation')

        # Orientation tensor
        orientFields = [
            self._ui.ori00, self._ui.ori01, self._ui.ori02,
            self._ui.ori10, self._ui.ori11, self._ui.ori12,
            self._ui.ori20, self._ui.ori21, self._ui.ori22,
        ]
        m.orientation = ' '.join(f.text() for f in orientFields)

        # Moment of Inertia tensor
        moiFields = [
            self._ui.moi00, self._ui.moi01, self._ui.moi02,
            self._ui.moi10, self._ui.moi11, self._ui.moi12,
            self._ui.moi20, self._ui.moi21, self._ui.moi22,
        ]
        m.momentOfInertia = ' '.join(f.text() for f in moiFields)

        # Translational constraint
        m.translationalConstraintType = self._selectedTranslationalConstraintType()

        m.direction = self._ui.direction.vector('Direction')

        m.normal = self._ui.normal.vector('Normal')

        # Rotational constraint
        m.rotationalConstraintType = self._selectedRotationalConstraintType()

        m.axis = self._ui.axis.vector('Axis')

        m.limitAngle = self._ui.limitAngleGroup.isChecked()
        m.clockwise = self._ui.clockwise.text()
        m.counterclockwise = self._ui.counterclockwise.text()

        # Restraints (update order)
        for i, r in enumerate(self._restraints):
            r.order = i + 1
        m.restraints = self._restraints

        # Solver
        solverIndex = self._ui.solverCombo.currentIndex()
        solverType = _SOLVER_TYPES[solverIndex]
        m.solver = RigidBodySolver(
            solverType=solverType,
            velocityIntegrationCoefficient=self._ui.velocityIntegrationCoefficient.text(),
            positionIntegrationCoefficient=self._ui.positionIntegrationCoefficient.text(),
            offCenteringAccelerationCoefficient=self._ui.offCenteringAccelerationCoefficient.text(),
            offCenteringVelocityCoefficient=self._ui.offCenteringVelocityCoefficient.text(),
        )

        # Acceleration factors
        m.accelerationRelaxationFactor = self._ui.accelerationRelaxationFactor.text()
        m.accelerationDampingFactor = self._ui.accelerationDampingFactor.text()

        self.accept()
