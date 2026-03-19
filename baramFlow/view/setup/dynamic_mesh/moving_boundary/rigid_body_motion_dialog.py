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
from .rigid_body_motion_ui import Ui_Dialog


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
        self._ui = Ui_Dialog()
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
            # Mass
            self._ui.lineEdit,
            # Center of Mass
            self._ui.lineEdit_43, self._ui.lineEdit_44, self._ui.lineEdit_45,
            # Center of Rotation
            self._ui.lineEdit_14, self._ui.lineEdit_15, self._ui.lineEdit_16,
            # Orientation tensor (3x3)
            self._ui.lineEdit_13, self._ui.lineEdit_9, self._ui.lineEdit_11,
            self._ui.lineEdit_10, self._ui.lineEdit_7, self._ui.lineEdit_6,
            self._ui.lineEdit_8, self._ui.lineEdit_5, self._ui.lineEdit_12,
            # Moment of Inertia tensor (3x3)
            self._ui.lineEdit_28, self._ui.lineEdit_29, self._ui.lineEdit_30,
            self._ui.lineEdit_31, self._ui.lineEdit_32, self._ui.lineEdit_33,
            self._ui.lineEdit_34, self._ui.lineEdit_35, self._ui.lineEdit_36,
            # Direction (line constraint)
            self._ui.lineEdit_17, self._ui.lineEdit_18, self._ui.lineEdit_19,
            # Normal (plane constraint)
            self._ui.lineEdit_20, self._ui.lineEdit_21, self._ui.lineEdit_22,
            # Axis (rotation constraint)
            self._ui.lineEdit_23, self._ui.lineEdit_24, self._ui.lineEdit_25,
            # Limit angle
            self._ui.lineEdit_27, self._ui.lineEdit_26,
            # Integration coefficients
            self._ui.lineEdit_37, self._ui.lineEdit_38,
            # Off-centering coefficients
            self._ui.lineEdit_39, self._ui.lineEdit_40,
            # Acceleration factors
            self._ui.lineEdit_41, self._ui.lineEdit_42,
        ]
        for field in fields:
            field.setValidator(validator)

    def _setupSolverComboBox(self):
        for st in _SOLVER_TYPES:
            self._ui.comboBox.addItem(_SOLVER_TYPE_NAMES[st])

    def _connectSignals(self):
        # Solver type combo box -> stacked widget
        self._ui.comboBox.currentIndexChanged.connect(self._solverTypeChanged)

        # Translational constraint radio buttons
        self._ui.radioButton.toggled.connect(self._translationalConstraintChanged)
        self._ui.radioButton_2.toggled.connect(self._translationalConstraintChanged)
        self._ui.radioButton_3.toggled.connect(self._translationalConstraintChanged)
        self._ui.radioButton_4.toggled.connect(self._translationalConstraintChanged)

        # Rotational constraint radio buttons
        self._ui.radioButton_5.toggled.connect(self._rotationalConstraintChanged)
        self._ui.radioButton_6.toggled.connect(self._rotationalConstraintChanged)
        self._ui.radioButton_7.toggled.connect(self._rotationalConstraintChanged)

        # Ok / Cancel
        self._ui.pushButton.clicked.connect(self._accept)
        self._ui.pushButton_2.clicked.connect(self.reject)

    # ------------------------------------------------------------------ load
    def _load(self):
        m = self._model

        # Mass
        self._ui.lineEdit.setText(m.mass)

        # Center of Mass
        self._ui.lineEdit_43.setText(m.centerOfMassX)
        self._ui.lineEdit_44.setText(m.centerOfMassY)
        self._ui.lineEdit_45.setText(m.centerOfMassZ)

        # Center of Rotation
        self._ui.lineEdit_14.setText(m.centerOfRotationX)
        self._ui.lineEdit_15.setText(m.centerOfRotationY)
        self._ui.lineEdit_16.setText(m.centerOfRotationZ)

        # Orientation tensor (row-major: 9 space-separated values)
        orientValues = (m.orientation or '1 0 0 0 1 0 0 0 1').split()
        if len(orientValues) == 9:
            orientFields = [
                self._ui.lineEdit_13, self._ui.lineEdit_9, self._ui.lineEdit_11,
                self._ui.lineEdit_10, self._ui.lineEdit_7, self._ui.lineEdit_6,
                self._ui.lineEdit_8, self._ui.lineEdit_5, self._ui.lineEdit_12,
            ]
            for field, val in zip(orientFields, orientValues):
                field.setText(val)

        # Moment of Inertia tensor (row-major: 9 space-separated values)
        moiValues = (m.momentOfInertia or '0 0 0 0 0 0 0 0 0').split()
        if len(moiValues) == 9:
            moiFields = [
                self._ui.lineEdit_28, self._ui.lineEdit_29, self._ui.lineEdit_30,
                self._ui.lineEdit_31, self._ui.lineEdit_32, self._ui.lineEdit_33,
                self._ui.lineEdit_34, self._ui.lineEdit_35, self._ui.lineEdit_36,
            ]
            for field, val in zip(moiFields, moiValues):
                field.setText(val)

        # Translational constraint
        radioMap = {
            TranslationalConstraintType.FREE: self._ui.radioButton,
            TranslationalConstraintType.FIXED: self._ui.radioButton_2,
            TranslationalConstraintType.LINE: self._ui.radioButton_3,
            TranslationalConstraintType.PLANE: self._ui.radioButton_4,
        }
        radioMap[m.translationalConstraintType].setChecked(True)

        # Direction (line constraint)
        self._ui.lineEdit_17.setText(m.directionX)
        self._ui.lineEdit_18.setText(m.directionY)
        self._ui.lineEdit_19.setText(m.directionZ)

        # Normal (plane constraint)
        self._ui.lineEdit_20.setText(m.normalX)
        self._ui.lineEdit_21.setText(m.normalY)
        self._ui.lineEdit_22.setText(m.normalZ)

        # Rotational constraint
        rotRadioMap = {
            RotationalConstraintType.FREE: self._ui.radioButton_5,
            RotationalConstraintType.FIXED: self._ui.radioButton_6,
            RotationalConstraintType.AXIS: self._ui.radioButton_7,
        }
        rotRadioMap[m.rotationalConstraintType].setChecked(True)

        # Axis (rotation constraint)
        self._ui.lineEdit_23.setText(m.axisX)
        self._ui.lineEdit_24.setText(m.axisY)
        self._ui.lineEdit_25.setText(m.axisZ)

        # Limit angle
        self._ui.groupBox_5.setChecked(m.limitAngle)
        self._ui.lineEdit_27.setText(m.clockwise)
        self._ui.lineEdit_26.setText(m.counterclockwise)

        # Solver
        solver = m.solver
        solverIndex = _SOLVER_TYPES.index(solver.solverType)
        self._ui.comboBox.setCurrentIndex(solverIndex)
        self._ui.stackedWidget.setCurrentIndex(_SOLVER_STACKED_INDEX[solver.solverType])

        self._ui.lineEdit_37.setText(solver.velocityIntegrationCoefficient)
        self._ui.lineEdit_38.setText(solver.positionIntegrationCoefficient)
        self._ui.lineEdit_39.setText(solver.offCenteringAccelerationCoefficient)
        self._ui.lineEdit_40.setText(solver.offCenteringVelocityCoefficient)

        # Acceleration factors
        self._ui.lineEdit_41.setText(m.accelerationRelaxationFactor)
        self._ui.lineEdit_42.setText(m.accelerationDampingFactor)

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
        # widget_2 holds direction vector (for Directional/LINE at row 2)
        self._ui.widget_2.setEnabled(self._ui.radioButton_3.isChecked())
        # widget_5 holds normal vector (for Planar/PLANE at row 3)
        self._ui.widget_5.setEnabled(self._ui.radioButton_4.isChecked())

    def _updateRotationalConstraintWidgets(self):
        axisSelected = self._ui.radioButton_7.isChecked()
        self._ui.widget_6.setEnabled(axisSelected)
        self._ui.groupBox_5.setEnabled(axisSelected)

    # --------------------------------------------------------- solver
    def _solverTypeChanged(self, index):
        if 0 <= index < len(_SOLVER_TYPES):
            solverType = _SOLVER_TYPES[index]
            self._ui.stackedWidget.setCurrentIndex(_SOLVER_STACKED_INDEX[solverType])

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
        if self._ui.radioButton.isChecked():
            return TranslationalConstraintType.FREE
        elif self._ui.radioButton_2.isChecked():
            return TranslationalConstraintType.FIXED
        elif self._ui.radioButton_3.isChecked():
            return TranslationalConstraintType.LINE
        elif self._ui.radioButton_4.isChecked():
            return TranslationalConstraintType.PLANE
        return TranslationalConstraintType.FREE

    def _selectedRotationalConstraintType(self) -> RotationalConstraintType:
        if self._ui.radioButton_5.isChecked():
            return RotationalConstraintType.FREE
        elif self._ui.radioButton_6.isChecked():
            return RotationalConstraintType.FIXED
        elif self._ui.radioButton_7.isChecked():
            return RotationalConstraintType.AXIS
        return RotationalConstraintType.FREE

    @qasync.asyncSlot()
    async def _accept(self):
        m = self._model

        # Mass
        m.mass = self._ui.lineEdit.text()

        # Center of Mass
        m.centerOfMassX = self._ui.lineEdit_43.text()
        m.centerOfMassY = self._ui.lineEdit_44.text()
        m.centerOfMassZ = self._ui.lineEdit_45.text()

        # Center of Rotation
        m.centerOfRotationX = self._ui.lineEdit_14.text()
        m.centerOfRotationY = self._ui.lineEdit_15.text()
        m.centerOfRotationZ = self._ui.lineEdit_16.text()

        # Orientation tensor
        orientFields = [
            self._ui.lineEdit_13, self._ui.lineEdit_9, self._ui.lineEdit_11,
            self._ui.lineEdit_10, self._ui.lineEdit_7, self._ui.lineEdit_6,
            self._ui.lineEdit_8, self._ui.lineEdit_5, self._ui.lineEdit_12,
        ]
        m.orientation = ' '.join(f.text() for f in orientFields)

        # Moment of Inertia tensor
        moiFields = [
            self._ui.lineEdit_28, self._ui.lineEdit_29, self._ui.lineEdit_30,
            self._ui.lineEdit_31, self._ui.lineEdit_32, self._ui.lineEdit_33,
            self._ui.lineEdit_34, self._ui.lineEdit_35, self._ui.lineEdit_36,
        ]
        m.momentOfInertia = ' '.join(f.text() for f in moiFields)

        # Translational constraint
        m.translationalConstraintType = self._selectedTranslationalConstraintType()

        m.directionX = self._ui.lineEdit_17.text()
        m.directionY = self._ui.lineEdit_18.text()
        m.directionZ = self._ui.lineEdit_19.text()

        m.normalX = self._ui.lineEdit_20.text()
        m.normalY = self._ui.lineEdit_21.text()
        m.normalZ = self._ui.lineEdit_22.text()

        # Rotational constraint
        m.rotationalConstraintType = self._selectedRotationalConstraintType()

        m.axisX = self._ui.lineEdit_23.text()
        m.axisY = self._ui.lineEdit_24.text()
        m.axisZ = self._ui.lineEdit_25.text()

        m.limitAngle = self._ui.groupBox_5.isChecked()
        m.clockwise = self._ui.lineEdit_27.text()
        m.counterclockwise = self._ui.lineEdit_26.text()

        # Restraints (update order)
        for i, r in enumerate(self._restraints):
            r.order = i + 1
        m.restraints = self._restraints

        # Solver
        solverIndex = self._ui.comboBox.currentIndex()
        solverType = _SOLVER_TYPES[solverIndex]
        m.solver = RigidBodySolver(
            solverType=solverType,
            velocityIntegrationCoefficient=self._ui.lineEdit_37.text(),
            positionIntegrationCoefficient=self._ui.lineEdit_38.text(),
            offCenteringAccelerationCoefficient=self._ui.lineEdit_39.text(),
            offCenteringVelocityCoefficient=self._ui.lineEdit_40.text(),
        )

        # Acceleration factors
        m.accelerationRelaxationFactor = self._ui.lineEdit_41.text()
        m.accelerationDampingFactor = self._ui.lineEdit_42.text()

        self.accept()
