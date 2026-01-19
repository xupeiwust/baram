#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from pandas import DataFrame

from baramFlow.base.boundary.boundary import TemperatureLayers
from baramFlow.coredb.boundary_db import WallHeatTransferMode


@dataclass
class WallHeatTransfer:
    mode: WallHeatTransferMode
    temperature: str = None
    temperatureDistribution: DataFrame = None
    heatFlux: str = None
    heatTransferCoefficient: str = None
    freeStreamTemperature: str = None
    externalEmissivity: str = None
    wallLayers: TemperatureLayers = None

    def toUpdateListForCoreDB(self, xpath):
        data = [(xpath + '/type', self.mode.value)]
        attributes = []

        if self.mode == WallHeatTransferMode.CONSTANT_TEMPERATURE:
            data.append((xpath + '/temperature', self.temperature))
        elif self.mode == WallHeatTransferMode.CONSTANT_HEAT_FLUX:
            data.append((xpath + '/heatFlux', self.heatFlux))
        elif self.mode == WallHeatTransferMode.CONVECTION:
            data.append((xpath + '/heatTransferCoefficient', self.heatTransferCoefficient))
            data.append((xpath + '/freeStreamTemperature', self.freeStreamTemperature))
            data.append((xpath + '/externalEmissivity', self.externalEmissivity))

            wallLayers, attributes = self.wallLayers.toUpdateListForCoreDB(xpath + '/wallLayers')
            data.extend(wallLayers)

        return data, attributes
