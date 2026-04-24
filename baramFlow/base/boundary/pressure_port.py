#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.coredb import _CoreDB
from baramFlow.coredb.libdb import E


@dataclass
class PressureInlet:
    pressure: str

    def applyToDB(self, db: _CoreDB, bcid: str):
        db.setValue(BoundaryDB.getXPath(bcid) + '/pressureInlet/pressure', self.pressure)


@dataclass
class PressureOutlet:
    totalPressure: str
    nonReflective: bool
    calculatedBackflow: bool
    backflowTotalTemperature: str = None

    def toElement(self):
        return E('pressureOutlet',
                    E('totalPressure',              self.totalPressure),
                    E('nonReflective',              self.nonReflective),
                    E('calculatedBackflow',         self.calculatedBackflow),
                    E('backflowTotalTemperature',   self.backflowTotalTemperature))
