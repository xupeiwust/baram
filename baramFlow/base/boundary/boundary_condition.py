#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from baramFlow.base.boundary.ABL_inlet import AtmosphericBoundaryLayer
from baramFlow.base.boundary.boundary import UserDefinedScalarValue, SpecieValue, updateUserDefinedScalarsInDB
from baramFlow.base.boundary.boundary import updateSpeciesInDB
from baramFlow.base.boundary.fan import Fan
from baramFlow.base.boundary.temperature import BoundaryTemperature
from baramFlow.base.boundary.velocity_inlet import VelocityInlet
from baramFlow.coredb.boundary_db import BoundaryDB


@dataclass
class VelocityInletCondition:
    velocityInet: VelocityInlet = None
    temperature: BoundaryTemperature = None

    userDefinedScalars: list[UserDefinedScalarValue] = None
    species: list[SpecieValue] = None

    def applyToDB(self, db, bcid):
        self.velocityInet.applyToDB(db, bcid)

        if self.temperature is not None:
            self.temperature.applyToDB(db, bcid)

        updateUserDefinedScalarsInDB(db, bcid, self.userDefinedScalars)
        updateSpeciesInDB(db, bcid, self.species)


@dataclass
class FanCondition:
    fan: Fan    = None
    coupledBoundary: str = None

    def applyToDB(self, db, bcid):
        self.fan.applyToDB(db, bcid)
        self.fan.applyCoupleConditionToDB(db, self.coupledBoundary)

        db.setValue(BoundaryDB.getXPath(bcid) + '/coupledBoundary', self.coupledBoundary)


@dataclass
class ABLInletCondition:
    abl: AtmosphericBoundaryLayer = None

    userDefinedScalars: list[UserDefinedScalarValue] = None
    species: list[SpecieValue] = None

    def applyToDB(self, db, bcid):
        self.abl.applyToDB(db)

        updateUserDefinedScalarsInDB(db, bcid, self.userDefinedScalars)
        updateSpeciesInDB(db, bcid, self.species)
