#!/usr/bin/env python
# -*- coding: utf-8 -*-

from coredb import coredb
from coredb.boundary_db import BoundaryDB, BoundaryType, KOmegaSpecification, WallVelocityCondition, InterfaceMode
from coredb.models_db import ModelsDB, TurbulenceModel
from openfoam.boundary_conditions.boundary_condition import BoundaryCondition


class Omega(BoundaryCondition):
    DIMENSIONS = '[0 0 -1 0 0 0 0]'

    def __init__(self, region):
        super().__init__(self.boundaryLocation(region.rname), 'omega')

        self._region = region
        self._db = coredb.CoreDB()

        self._initialValue = region.initialOmega

        self._data = None

    def build(self):
        self._data = None

        if ModelsDB.getTurbulenceModel() == TurbulenceModel.K_OMEGA:
            self._data = {
                'dimensions': self.DIMENSIONS,
                'internalField': ('uniform', self._initialValue),
                'boundaryField': self._constructBoundaryField()
            }

        return self

    def _constructBoundaryField(self):
        field = {}

        for bcid, name, type_ in self._region.boundaries:
            xpath = BoundaryDB.getXPath(bcid)

            field[name] = {
                BoundaryType.VELOCITY_INLET.value:      (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.FLOW_RATE_INLET.value:     (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.PRESSURE_INLET.value:      (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.PRESSURE_OUTLET.value:     (lambda: self._constructPressureOutletOmega(xpath)),
                BoundaryType.ABL_INLET.value:           (lambda: self._constructInletOutlet(self._db.getValue(xpath + '/turbulence/k-omega/specificDissipationRate'), self._initialValue)),
                BoundaryType.OPEN_CHANNEL_INLET.value:  (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.OPEN_CHANNEL_OUTLET.value: (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.OUTFLOW.value:             (lambda: self._constructZeroGradient()),
                BoundaryType.FREE_STREAM.value:         (lambda: self._constructFreeStreamOmega(xpath)),
                BoundaryType.FAR_FIELD_RIEMANN.value:   (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUBSONIC_INFLOW.value:     (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUBSONIC_OUTFLOW.value:    (lambda: self._constructZeroGradient()),
                BoundaryType.SUPERSONIC_INFLOW.value:   (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUPERSONIC_OUTFLOW.value:  (lambda: self._constructZeroGradient()),
                BoundaryType.WALL.value:                (lambda: self._constructWallOmega(xpath)),
                BoundaryType.THERMO_COUPLED_WALL.value: (lambda: self._constructNEXTOmegaBlendedWallFunction()),
                BoundaryType.SYMMETRY.value:            (lambda: self._constructSymmetry()),
                BoundaryType.INTERFACE.value:           (lambda: self._constructInterfaceOmega(xpath)),
                BoundaryType.POROUS_JUMP.value:         (lambda: self._constructCyclic()),
                BoundaryType.FAN.value:                 (lambda: self._constructCyclic()),
                BoundaryType.EMPTY.value:               (lambda: self._constructEmpty()),
                BoundaryType.CYCLIC.value:              (lambda: self._constructCyclic()),
                BoundaryType.WEDGE.value:               (lambda: self._constructWedge()),
            }.get(type_)()

        return field

    def _constructInletOutletByModel(self, xpath):
        spec = self._db.getValue(xpath + '/turbulence/k-omega/specification')
        if spec == KOmegaSpecification.K_AND_OMEGA.value:
            return self._constructInletOutlet(
                self._db.getValue(xpath + '/turbulence/k-omega/specificDissipationRate'), self._initialValue)
        elif spec == KOmegaSpecification.INTENSITY_AND_VISCOSITY_RATIO.value:
            return self._constructNEXTViscosityRatioInletOutletTDR(
                self._db.getValue(xpath + '/turbulence/k-omega/turbulentViscosityRatio'), self._initialValue)

    def _constructNEXTOmegaBlendedWallFunction(self):
        return {
            # 'type': 'omegaBlendedWallFunction',  # This type has not ported to OpenFOAM N yet
            'type': 'omegaWallFunction',
            'blending': 'tanh',
            'value': ('uniform', self._initialValue)
        }

    def _constructAtmOmegaWallFunction(self):
        return {
            'type': 'atmOmegaWallFunction',
            'z0': self._db.getValue(BoundaryDB.ABL_INLET_CONDITIONS_XPATH + '/surfaceRoughnessLength'),
            'd': self._db.getValue(BoundaryDB.ABL_INLET_CONDITIONS_XPATH + '/minimumZCoordinate'),
            'value': ('uniform', self._initialValue)
        }

    def _constructPressureOutletOmega(self, xpath):
        if self._db.getValue(xpath + '/pressureOutlet/calculatedBackflow') == 'true':
            return self._constructInletOutletByModel(xpath)
        else:
            return self._constructZeroGradient()

    def _constructFreeStreamOmega(self, xpath):
        spec = self._db.getValue(xpath + '/turbulence/k-omega/specification')
        if spec == KOmegaSpecification.K_AND_OMEGA.value:
            omega = float(self._db.getValue(xpath + '/turbulence/k-omega/specificDissipationRate'))
        elif spec == KOmegaSpecification.INTENSITY_AND_VISCOSITY_RATIO.value:
            _, omega = self._calculateFreeStreamKW(xpath, self._region.rname)
        return self._constructFreestream(omega)

    def _constructWallOmega(self, xpath):
        spec = self._db.getValue(xpath + '/wall/velocity/type')
        if spec == WallVelocityCondition.ATMOSPHERIC_WALL.value:
            return self._constructAtmOmegaWallFunction()
        else:
            return self._constructNEXTOmegaBlendedWallFunction()

    def _constructInterfaceOmega(self, xpath):
        spec = self._db.getValue(xpath + '/interface/mode')
        if spec == InterfaceMode.REGION_INTERFACE.value:
            return self._constructNEXTOmegaBlendedWallFunction()
        else:
            return self._constructCyclicAMI()
