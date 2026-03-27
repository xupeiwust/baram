#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum

from baramFlow.base.base import SimpleSheetData
from baramFlow.base.base import SpatialVectorList, TemporalScalarList, TemporalVectorList
from baramFlow.base.boundary.boundary import BoundaryBase
from baramFlow.base.boundary.temperature import BoundaryTemperature
from baramFlow.base.xml_helper import Vector
from baramFlow.coredb.boundary_db import BoundaryDB


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
    constant: Vector = dataClassField(default_factory=Vector.xUnit)
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

    def updateIn(self, db, bcid):
        xpath = BoundaryDB.getXPath(bcid) + '/velocityInlet/velocity'

        db.setValue(xpath + '/specification', self.specificationMethod.value)
        db.setValue(xpath + '/coordinateSystem', self.coordinateSystem.value)

        if self.specificationMethod == VelocitySpecification.MAGNITUDE:
            db.setValue(xpath + '/magnitudeNormal/profile', self.magnitude.profile.value)
            if self.magnitude.profile == VelocityProfile.CONSTANT:
                db.setValue(xpath + '/magnitudeNormal/constant', self.magnitude.constant)
            elif self.magnitude.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if self.magnitude.temporalDistribution is not None:
                    db.replaceElement(xpath + '/magnitudeNormal/temporalDistribution/piecewiseLinear',
                                      self.magnitude.temporalDistribution.toElement('piecewiseLinear'))
        elif self.coordinateSystem == CoordinateSystem.CARTESIAN:
            db.setValue(xpath + '/component/profile', self.component.profile.value)
            if self.component.profile == VelocityProfile.CONSTANT:
                db.replaceElement(xpath + '/component/constant', self.component.constant.toElement('constant'))
            elif self.component.profile == VelocityProfile.SPATIAL_DISTRIBUTION:
                if self.component.spatialDistribution is not None:
                    db.replaceElement(xpath + '/component/spatialDistribution',
                                      self.component.spatialDistribution.toElement('spatialDistribution'))
            elif self.component.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if self.component.temporalDistribution is not None:
                    db.replaceElement(xpath + '/component/temporalDistribution/piecewiseLinear',
                                      self.component.temporalDistribution.toElement('piecewiseLinear'))
        else:
            db.setValue(xpath + '/localCylindrical/profile', self.localCylindrical.profile.value)
            if self.localCylindrical.profile == VelocityProfile.CONSTANT:
                db.setValue(xpath + '/localCylindrical/constant/axialVelocity',
                            self.localCylindrical.constant.axialVelocity)
                db.setValue(xpath + '/localCylindrical/constant/radialVelocity',
                            self.localCylindrical.constant.radialVelocity)
                db.setValue(xpath + '/localCylindrical/constant/angularSpeed',
                            self.localCylindrical.constant.angularSpeed)
            elif self.localCylindrical.profile == VelocityProfile.TEMPORAL_DISTRIBUTION:
                if self.localCylindrical.temporalDistribution is not None:
                    db.replaceElement(xpath + '/localCylindrical/temporalDistribution',
                                      self.localCylindrical.temporalDistribution.toElement('temporalDistribution'))

            db.replaceElement(xpath + '/localCylindrical/axisOrigin',
                              self.localCylindrical.axisOrigin.toElement('axisOrigin'))
            db.replaceElement(xpath + '/localCylindrical/axisDirection',
                              self.localCylindrical.axisDirection.toElement('axisDirection'))


@dataclass
class VelocityInletCondition(BoundaryBase):
    velocity: InletVelocity = None
    temperature: BoundaryTemperature = None

    def _updateTypeConditionIn(self, db):
        self.velocity.updateIn(db, self.bcid)

        if self.temperature is not None:
            self.temperature.updateIn(db, self.bcid)
