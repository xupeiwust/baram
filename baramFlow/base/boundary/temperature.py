#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from baramFlow.base.base import SpatialScalarList, TemporalScalarList
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.libdb import nsmap


class TemperatureProfile(Enum):
    CONSTANT = 'constant'
    SPATIAL_DISTRIBUTION = 'spatialDistribution'
    TEMPORAL_DISTRIBUTION = 'temporalDistribution'


class TemperatureTemporalDistributionSpecification(Enum):
    PIECEWISE_LINEAR = 'piecewiseLinear'
    POLYNOMIAL = 'polynomial'


@dataclass
class TemperatureTemporalDistribution:
    specification: TemperatureTemporalDistributionSpecification
    POLYNOMIAL = 'polynomial'
    piecewiseLinear: TemporalScalarList = None
    polynomial: str = None  # inputNumberListType in baram.cfd.xsd


@dataclass
class BoundaryTemperature:
    profile: TemperatureProfile
    constant: str = None
    spatialDistribution: SpatialScalarList = None
    temporalDistribution: TemperatureTemporalDistribution = None

    def updateIn(self, db, bcid):
        xpath = BoundaryDB.getXPath(bcid) + '/temperature'
        element = db.getElement(xpath)

        db.setValue(xpath + '/profile', self.profile.value)
        if self.profile == TemperatureProfile.CONSTANT:
            db.setValue(xpath + '/constant', self.constant)
        elif self.profile == TemperatureProfile.SPATIAL_DISTRIBUTION:
            if self.spatialDistribution is not None:
                old = element.find('spatialDistribution', namespaces=nsmap)
                new = self.spatialDistribution.toElement('spatialDistribution')
                element.replace(old, new)
        elif self.profile == TemperatureProfile.TEMPORAL_DISTRIBUTION:
            db.setValue(xpath + '/temporalDistribution/specification',
                        self.temporalDistribution.specification.value)
            if self.temporalDistribution.specification == TemperatureTemporalDistributionSpecification.PIECEWISE_LINEAR:
                if self.temporalDistribution.piecewiseLinear is not None:
                    temporalDistributionElement = element.find('temporalDistribution', namespaces=nsmap)
                    old = temporalDistributionElement.find('piecewiseLinear', namespaces=nsmap)
                    new = self.temporalDistribution.piecewiseLinear.toElement('piecewiseLinear')
                    temporalDistributionElement.replace(old, new)
            elif self.temporalDistribution.specification == TemperatureTemporalDistributionSpecification.POLYNOMIAL:
                if self.temporalDistribution.polynomial is not None:
                    db.setValue(xpath + '/temporalDistribution/polynomial', self.temporalDistribution.polynomial)
