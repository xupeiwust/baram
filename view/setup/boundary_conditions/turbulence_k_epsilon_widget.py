#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum, auto

from PySide6.QtWidgets import QWidget

from .turbulence_k_epsilon_widget_ui import Ui_turbulenceKEpsilonWidget


class SpecificationMethod(Enum):
    K_AND_EPSILON = 0
    INTENSITY_AND_VISCOSITY_RATIO = auto()


class TurbulenceKEpsilonWidget(QWidget):
    def __init__(self, parent):
        super().__init__()
        self._ui = Ui_turbulenceKEpsilonWidget()

        self._parent = parent

        self._ui.setupUi(self)
        self._connectSignalsSlots()

        self._specificationMethodChanged(0)

    def _connectSignalsSlots(self):
        self._ui.specificationMethod.currentIndexChanged.connect(self._specificationMethodChanged)

    def _specificationMethodChanged(self, index):
        self._ui.kAndEpsilon.setVisible(
            index == SpecificationMethod.K_AND_EPSILON.value)
        self._ui.intensityAndViscocityRatio.setVisible(
            index == SpecificationMethod.INTENSITY_AND_VISCOSITY_RATIO.value)
