#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from uuid import UUID

from pandas import DataFrame

from baramFlow.base.base import UUID_ZERO
from baramFlow.base.boundary.boundary import TemperatureLayers
from baramFlow.base.file_data_manager import FileDataManager
from baramFlow.coredb.boundary_db import WallHeatTransferMode
from baramFlow.coredb.libdb import E, nsmap


@dataclass
class WallHeatTransfer:
    mode: WallHeatTransferMode          = WallHeatTransferMode.ADIABATIC
    temperature: str                    = '300'
    heatFlux: str                       = '1000'
    temperatureDistributionName: UUID   = UUID_ZERO
    heatTransferCoefficient: str        = '100'
    freeStreamTemperature: str          = '300'
    externalEmissivity: str             = '0'
    wallLayers: TemperatureLayers       = field(default_factory=TemperatureLayers)

    temperatureDistribution: DataFrame  = None

    def update(self, new):
        self.mode = new.mode

        if new.mode == WallHeatTransferMode.CONSTANT_TEMPERATURE:
            self.temperature = new.temperature
        elif new.mode == WallHeatTransferMode.TEMPERATURE_DISTRIBUTION:
            if new.temperatureDistribution is not None:
                self.temperatureDistributionName = FileDataManager.putDataFrame(new.temperatureDistribution)
            self.temperatureDistribution = new.temperatureDistribution
        elif new.mode == WallHeatTransferMode.CONSTANT_HEAT_FLUX:
            self.heatFlux = new.heatFlux
        elif new.mode == WallHeatTransferMode.CONVECTION:
            self.heatTransferCoefficient = new.heatTransferCoefficient
            self.freeStreamTemperature = new.freeStreamTemperature
            self.externalEmissivity = new.externalEmissivity
            self.wallLayers.update(new.wallLayers)

    def toElement(self):
        return E('heatTransfer',
                    E('type', self.mode),
                    E('temperature', self.temperature),
                    E('heatFlux', self.heatFlux),
                    E('temperatureDistributionName', self.temperatureDistributionName),
                    E('heatTransferCoefficient', self.heatTransferCoefficient),
                    E('freeStreamTemperature', self.freeStreamTemperature),
                    E('externalEmissivity', self.externalEmissivity),
                    self.wallLayers.toElement())

    @staticmethod
    def fromElement(e):
        return WallHeatTransfer(mode=WallHeatTransferMode(e.find('type', namespaces=nsmap).text),
                                temperature=e.find('temperature', namespaces=nsmap).text,
                                heatFlux=e.find('heatFlux', namespaces=nsmap).text,
                                temperatureDistributionName=UUID(e.find('temperatureDistributionName', namespaces=nsmap).text),
                                heatTransferCoefficient=e.find('heatTransferCoefficient', namespaces=nsmap).text,
                                freeStreamTemperature=e.find('freeStreamTemperature', namespaces=nsmap).text,
                                externalEmissivity=e.find('externalEmissivity', namespaces=nsmap).text,
                                wallLayers=TemperatureLayers.fromElement(e.find('wallLayers', namespaces=nsmap)))


@dataclass
class Wall:
    heatTransfer: WallHeatTransfer = field(default_factory=WallHeatTransfer)

    @staticmethod
    def fromElement(e):
        return Wall(heatTransfer=WallHeatTransfer.fromElement(e.find('heatTransfer', namespaces=nsmap)))
