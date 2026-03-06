#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from baramFlow.base.base import SpatialScalarList, TemporalScalarList


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
