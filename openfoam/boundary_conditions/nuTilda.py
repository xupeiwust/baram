#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CoolProp.CoolProp import PropsSI

from coredb import coredb
from coredb.cell_zone_db import RegionDB
from coredb.material_db import MaterialDB, Phase
from coredb.boundary_db import BoundaryDB, BoundaryType, SpalartAllmarasSpecification, InterfaceMode
from coredb.models_db import ModelsDB, TurbulenceModel
from openfoam.boundary_conditions.boundary_condition import BoundaryCondition


class NuTilda(BoundaryCondition):
    DIMENSIONS = '[0 2 -1 0 0 0 0]'

    def __init__(self, rname: str):
        super().__init__(self.boundaryLocation(rname), 'nuTilda')

        self._rname = rname
        self._db = coredb.CoreDB()

        p = float(self._db.getValue('.//initialization/initialValues/pressure'))\
            + float(self._db.getValue('.//operatingConditions/pressure'))  # Pressure
        t = float(self._db.getValue('.//initialization/initialValues/temperature'))  # Temperature
        b = float(self._db.getValue('.//initialization/initialValues/turbulentViscosity'))  # Turbulent Viscosity

        mid = RegionDB.getMaterial(rname)
        assert MaterialDB.getPhase(mid) in [Phase.LIQUID, Phase.GAS]
        cpName = MaterialDB.getCoolPropName(mid)

        rho = PropsSI('D', 'T', float(t), 'P', float(p), cpName)  # Density
        mu  = PropsSI('V', 'T', float(t), 'P', float(p), cpName)  # Viscosity

        nu = mu / rho  # Kinetic Viscosity
        nut = b * nu

        self._initialValue = nut  # nut can be used for the INITIAL value of nuTilda

        self._data = None

    def build(self):
        self._data = None

        if ModelsDB.getTurbulenceModel() == TurbulenceModel.SPALART_ALLMARAS:
            self._data = {
                'dimensions': self.DIMENSIONS,
                'internalField': ('uniform', self._initialValue),
                'boundaryField': self._constructBoundaryField()
            }

        return self

    def _constructBoundaryField(self):
        field = {}

        boundaries = self._db.getBoundaryConditions(self._rname)
        for bcid, name, type_ in boundaries:
            xpath = BoundaryDB.getXPath(bcid)

            field[name] = {
                BoundaryType.VELOCITY_INLET.value:      (lambda: self._constructFixedValueByModel(xpath)),
                BoundaryType.FLOW_RATE_INLET.value:     (lambda: self._constructFixedValueByModel(xpath)),
                BoundaryType.PRESSURE_INLET.value:      (lambda: self._constructFixedValueByModel(xpath)),
                BoundaryType.PRESSURE_OUTLET.value:     (lambda: self._constructPressureOutletNuTilda(xpath)),
                BoundaryType.ABL_INLET.value:           (lambda: None),
                BoundaryType.OPEN_CHANNEL_INLET.value:  (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.OPEN_CHANNEL_OUTLET.value: (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.OUTFLOW.value:             (lambda: self._constructZeroGradient()),
                BoundaryType.FREE_STREAM.value:         (lambda: self._constructFreestream(xpath + '/freeStream')),
                BoundaryType.FAR_FIELD_RIEMANN.value:   (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUBSONIC_INFLOW.value:     (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUBSONIC_OUTFLOW.value:    (lambda: self._constructZeroGradient()),
                BoundaryType.SUPERSONIC_INFLOW.value:   (lambda: self._constructInletOutletByModel(xpath)),
                BoundaryType.SUPERSONIC_OUTFLOW.value:  (lambda: self._constructZeroGradient()),
                BoundaryType.WALL.value:                (lambda: self._constructZeroGradient()),
                BoundaryType.THERMO_COUPLED_WALL.value: (lambda: self._constructZeroGradient()),
                BoundaryType.SYMMETRY.value:            (lambda: self._constructSymmetry()),
                BoundaryType.INTERFACE.value:           (lambda: self._constructInterfaceNuTilda(xpath)),
                BoundaryType.POROUS_JUMP.value:         (lambda: self._constructCyclic()),
                BoundaryType.FAN.value:                 (lambda: self._constructCyclic()),
                BoundaryType.EMPTY.value:               (lambda: self._constructEmpty()),
                BoundaryType.CYCLIC.value:              (lambda: self._constructCyclic()),
                BoundaryType.WEDGE.value:               (lambda: self._constructWedge()),
            }.get(type_)()

        return field

    def _constructFixedValueByModel(self, xpath):
        spec = self._db.getValue(xpath + '/turbulence/spalartAllmaras/specification')
        if spec == SpalartAllmarasSpecification.MODIFIED_TURBULENT_VISCOSITY.value:
            return self._constructFixedValue(
                self._db.getValue(xpath + '/turbulence/spalartAllmaras/modifiedTurbulentViscosity'))
        elif spec == SpalartAllmarasSpecification.TURBULENT_VISCOSITY_RATIO.value:
            # ToDo: Setting according to boundary field spec
            return {
                'type': ''
            }

    def _constructInletOutletByModel(self, xpath):
        spec = self._db.getValue(xpath + '/turbulence/spalartAllmaras/specification')
        if spec == SpalartAllmarasSpecification.MODIFIED_TURBULENT_VISCOSITY.value:
            return self._constructInletOutlet(
                self._db.getValue(xpath + '/turbulence/spalartAllmaras/modifiedTurbulentViscosity'), self._initialValue)
        elif spec == SpalartAllmarasSpecification.TURBULENT_VISCOSITY_RATIO.value:
            # ToDo: Setting according to boundary field spec
            return {
                'type': ''
            }

    def _constructPressureOutletNuTilda(self, xpath):
        if self._db.getValue(xpath + '/pressureOutlet/calculatedBackflow') == 'true':
            return self._constructInletOutletByModel(xpath)
        else:
            return self._constructZeroGradient()

    def _constructInterfaceNuTilda(self, xpath):
        spec = self._db.getValue(xpath + '/interface/mode')
        if spec == InterfaceMode.REGION_INTERFACE.value:
            return self._constructZeroGradient()
        else:
            return self._constructCyclicAMI()
