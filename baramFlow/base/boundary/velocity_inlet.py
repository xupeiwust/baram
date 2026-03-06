#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from baramFlow.base.base import Vector, SimpleSheetData
from baramFlow.base.base import SpatialVectorList, TemporalScalarList, TemporalVectorList
from baramFlow.base.boundary.boundary import UserDefinedScalarValue, SpecieValue, BoundaryManager
from baramFlow.base.boundary.temperature import BoundaryTemperature
from baramFlow.coredb import coredb
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.coredb_writer import CoreDBWriter


class VelocitySpecification(Enum):
    COMPONENT = 'component'
    MAGNITUDE = 'magnitudeNormal'


class VelocityProfile(Enum):
    CONSTANT = 'constant'
    SPATIAL_DISTRIBUTION = 'spatialDistribution'
    TEMPORAL_DISTRIBUTION = 'temporalDistribution'


class CoordinateSystem(Enum):
    CARTESIAN = 'cartesian'
    LOCAL_CYLINDRICAL = 'localCylindrical'


@dataclass
class VelocityComponentCartesian:
    profile: VelocityProfile
    constant: Vector = None
    spatialDistribution: SpatialVectorList = None
    temporalDistribution: TemporalVectorList = None


@dataclass
class VelocityMagnitude:
    profile: VelocityProfile
    constant: str = None
    temporalDistribution: TemporalScalarList = None


@dataclass
class LocalCylindricalConstant:
    axialVelocity: str
    radialVelocity: str
    angularSpeed: str


class LocalCylindricalTemporalDistribution(SimpleSheetData):
    columns = ['t', 'u', 'v', 'omega']


@dataclass
class VelocityLocalCylindrical:
    profile: VelocityProfile
    axisOrigin: Vector
    axisDirection: Vector
    constant: LocalCylindricalConstant = None
    temporalDistribution: LocalCylindricalTemporalDistribution = None


@dataclass
class InletVelocity:
    specificationMethod: VelocitySpecification
    coordinateSystem: CoordinateSystem
    component: VelocityComponentCartesian = None
    magnitude: VelocityMagnitude = None
    localCylindrical: VelocityLocalCylindrical = None


@dataclass
class VelocityInletConditions:
    velocity: InletVelocity
    userDefinedScalars: list[UserDefinedScalarValue]
    species: list[SpecieValue]
    temperature: BoundaryTemperature


def updateVelocityInletBoundaryConditions(bcid, conditions: VelocityInletConditions, writer: CoreDBWriter):
    xpath = BoundaryDB.getXPath(bcid) + '/velocityInlet'

    with coredb.CoreDB() as db:
        velocity = conditions.velocity
        db.setValue(xpath + '/velocity/specification', velocity.specificationMethod.value)
        db.setValue(xpath + '/velocity/coordinateSystem', velocity.coordinateSystem.value)

        if velocity.specificationMethod == VelocitySpecification.MAGNITUDE:
            db.setValue(xpath + '/velocity/magnitudeNormal/profile', velocity.magnitude.profile.value)
            if velocity.magnitude.profile == VelocityProfile.CONSTANT:
                db.setValue(xpath + '/velocity/magnitudeNormal/constant', velocity.magnitude.constant)
            elif velocity.magnitude.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if velocity.magnitude.temporalDistribution is not None:
                    db.setValue(xpath + '/velocity/magnitudeNormal/temporalDistribution/piecewiseLinear/t',
                                velocity.magnitude.temporalDistribution.columnDataString(0))
                    db.setValue(xpath + '/velocity/magnitudeNormal/temporalDistribution/piecewiseLinear/v',
                                velocity.magnitude.temporalDistribution.columnDataString(1))
        elif velocity.coordinateSystem == CoordinateSystem.CARTESIAN:
            db.setValue(xpath + '/velocity/component/profile', velocity.component.profile.value)
            if velocity.component.profile == VelocityProfile.CONSTANT:
                db.setValue(xpath + '/velocity/component/constant/x', velocity.component.constant.x)
                db.setValue(xpath + '/velocity/component/constant/y', velocity.component.constant.y)
                db.setValue(xpath + '/velocity/component/constant/z', velocity.component.constant.z)
            elif velocity.component.profile == VelocityProfile.SPATIAL_DISTRIBUTION:
                if velocity.component.spatialDistribution is not None:
                    db.setValue(xpath + '/velocity/component/spatialDistribution/x',
                                velocity.component.spatialDistribution.columnDataString(0))
                    db.setValue(xpath + '/velocity/component/spatialDistribution/y',
                                velocity.component.spatialDistribution.columnDataString(1))
                    db.setValue(xpath + '/velocity/component/spatialDistribution/z',
                                velocity.component.spatialDistribution.columnDataString(2))
                    db.setValue(xpath + '/velocity/component/spatialDistribution/vx',
                                velocity.component.spatialDistribution.columnDataString(3))
                    db.setValue(xpath + '/velocity/component/spatialDistribution/vy',
                                velocity.component.spatialDistribution.columnDataString(4))
                    db.setValue(xpath + '/velocity/component/spatialDistribution/vz',
                                velocity.component.spatialDistribution.columnDataString(5))
            elif velocity.component.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if velocity.component.temporalDistribution is not None:
                    db.setValue(xpath + '/velocity/component/temporalDistribution/piecewiseLinear/t',
                                velocity.component.temporalDistribution.columnDataString(0))
                    db.setValue(xpath + '/velocity/component/temporalDistribution/piecewiseLinear/x',
                                velocity.component.temporalDistribution.columnDataString(1))
                    db.setValue(xpath + '/velocity/component/temporalDistribution/piecewiseLinear/y',
                                velocity.component.temporalDistribution.columnDataString(2))
                    db.setValue(xpath + '/velocity/component/temporalDistribution/piecewiseLinear/z',
                                velocity.component.temporalDistribution.columnDataString(3))
        else:
            db.setValue(xpath + '/velocity/localCylindrical/profile', velocity.localCylindrical.profile.value)
            if velocity.localCylindrical.profile == VelocityProfile.CONSTANT:
                db.setValue(xpath + '/velocity/localCylindrical/constant/axialVelocity',
                            velocity.localCylindrical.constant.axialVelocity)
                db.setValue(xpath + '/velocity/localCylindrical/constant/radialVelocity',
                            velocity.localCylindrical.constant.radialVelocity)
                db.setValue(xpath + '/velocity/localCylindrical/constant/angularSpeed',
                            velocity.localCylindrical.constant.angularSpeed)
            elif velocity.localCylindrical.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if velocity.localCylindrical.temporalDistribution is not None:
                    db.setValue(xpath + '/velocity/localCylindrical/temporalDistribution/t',
                                velocity.localCylindrical.temporalDistribution.columnDataString(0))
                    db.setValue(xpath + '/velocity/localCylindrical/temporalDistribution/u',
                                velocity.localCylindrical.temporalDistribution.columnDataString(1))
                    db.setValue(xpath + '/velocity/localCylindrical/temporalDistribution/v',
                                velocity.localCylindrical.temporalDistribution.columnDataString(2))
                    db.setValue(xpath + '/velocity/localCylindrical/temporalDistribution/omega',
                                velocity.localCylindrical.temporalDistribution.columnDataString(3))

            db.setValue(xpath + '/velocity/localCylindrical/axisOrigin/x', velocity.localCylindrical.axisOrigin.x)
            db.setValue(xpath + '/velocity/localCylindrical/axisOrigin/y', velocity.localCylindrical.axisOrigin.y)
            db.setValue(xpath + '/velocity/localCylindrical/axisOrigin/z', velocity.localCylindrical.axisOrigin.z)
            db.setValue(xpath + '/velocity/localCylindrical/axisDirection/x', velocity.localCylindrical.axisDirection.x)
            db.setValue(xpath + '/velocity/localCylindrical/axisDirection/y', velocity.localCylindrical.axisDirection.y)
            db.setValue(xpath + '/velocity/localCylindrical/axisDirection/z', velocity.localCylindrical.axisDirection.z)

        BoundaryManager.updateTemperature(db, bcid, conditions.temperature)
        BoundaryManager.updateUserDefinedScalars(db, bcid, conditions.userDefinedScalars)
        BoundaryManager.updateSpecies(db, bcid, conditions.species)

        writer.updateInDB(db)

        db.increaseConfigCount()
