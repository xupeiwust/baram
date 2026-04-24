#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from enum import Enum

from lxml import etree

from baramFlow.base.base import BatchableNumber
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.libdb import nsmap, E, ns, xmlToBool


class PatchInteractionType(Enum):
    NONE    = 'none'
    REFLECT = 'reflect'
    ESCAPE  = 'escape'
    TRAP    = 'trap'
    RECYCLE = 'recycle'


@dataclass
class CoefficientOfRestitution:
    normal: BatchableNumber = field(default_factory=lambda: BatchableNumber('1'))
    tangential: BatchableNumber = field(default_factory=lambda: BatchableNumber('1'))

    @staticmethod
    def fromElement(e):
        return CoefficientOfRestitution(normal=BatchableNumber.fromElement(e.find('normal', namespaces=nsmap)),
                                        tangential=BatchableNumber.fromElement(e.find('tangential', namespaces=nsmap)))

    def toElement(self):
        return etree.fromstring(f'''
            <coefficientOfRestitution xmlns="{ns}">
                {self.normal.toXML('normal')}
                {self.tangential.toXML('tangential')}
            </coefficientOfRestitution>
        ''')


@dataclass
class RecycleProperties:
    recycleBoundary: str = '0'
    recycleFraction: BatchableNumber = field(default_factory=lambda: BatchableNumber('1'))

    @staticmethod
    def fromElement(e):
        return RecycleProperties(
            recycleBoundary=e.find('recycleBoundary', namespaces=nsmap).text,
            recycleFraction=BatchableNumber.fromElement(e.find('recycleFraction', namespaces=nsmap)))

    def toElement(self):
        return etree.fromstring(f'''
            <recycle xmlns="{ns}">
                <recycleBoundary>{self.recycleBoundary}</recycleBoundary>
                {self.recycleFraction.toXML('recycleFraction')}
            </recycle>
        ''')


@dataclass
class PatchInteraction:
    type: PatchInteractionType = PatchInteractionType.REFLECT
    reflect: CoefficientOfRestitution = field(default_factory=CoefficientOfRestitution)
    recycle: RecycleProperties = field(default_factory=RecycleProperties)

    @staticmethod
    def fromElement(e):
        return PatchInteraction(
            type=PatchInteractionType(e.find('type', namespaces=nsmap).text),
            reflect=CoefficientOfRestitution.fromElement(e.find('reflect/coefficientOfRestitution', namespaces=nsmap)),
            recycle=RecycleProperties.fromElement(e.find('recycle', namespaces=nsmap)))

    def toElement(self):
        return E('patchInteraction',
                    E('type', self.type),
                    E('reflect', self.reflect.toElement()),
                    self.recycle.toElement()
                 )


@dataclass
class UserDefinedScalarValue:
    scalarID: str
    value: str

    def toElement(self):
        return E('scalar',
                    E('scalarID', self.scalarID),
                    E('value', self.value))

    @staticmethod
    def fromElement(element):
        return UserDefinedScalarValue(scalarID=element.find('scalarID', namespaces=nsmap).text,
                                      value=element.find('value', namespaces=nsmap).text)


def updateUserDefinedScalarsInDB(db, bcid, scalars: list[UserDefinedScalarValue]):
    if scalars is None:
        return

    element = db.getElement(BoundaryDB.getXPath(bcid) + '/userDefinedScalars')
    element.clear()

    for s in scalars:
        element.append(s.toElement())


def userDefinedScalarsFromElement(element):
    data = []

    for row in element.findall('userDefinedScalars', namespaces=nsmap):
        data.append(UserDefinedScalarValue.fromElement(row))

    return data


@dataclass
class SpecieValue:
    mid: str
    value: str

    def toElement(self):
        return E('specie',
                    E('value', self.value),
                 mid=self.mid)

    @staticmethod
    def fromElement(element):
        return SpecieValue(mid=element.get('mid'),
                           value=element.find('value', namespaces=nsmap).text)


def updateSpeciesInDB(db, bcid, specieRatios):
    if specieRatios is None:
        return

    element = db.getElement(f'{BoundaryDB.getXPath(bcid)}/species/mixture[mid="{specieRatios.mid}"]')
    for s in specieRatios.ratios:
        element.find(f'specie[mid="{s.mid}"]/value', namespaces=nsmap).text = s.value


def speciesFromElement(element):
    data = []

    for row in element.findall('species', namespaces=nsmap):
        data.append(SpecieValue.fromElement(row))

    return data


@dataclass
class SpecieRatios:
    mid: str
    ratios: list[SpecieValue]


@dataclass
class TemperatureLayer:
    thickness: str
    thermalConductivity : str


@dataclass
class TemperatureLayers:
    disabled: bool                  = True
    layers: list[TemperatureLayer]  = None

    def update(self, new):
        self.disabled = new.disabled

        if new.disabled:
            return

        self.layers = new.layers


    def toElement(self):
        thicknessLayers = ''
        thermalConductivityLayers = ''
        for row in self.layers:
            thicknessLayers += row.thickness + ' '
            thermalConductivityLayers += row.thermalConductivity + ' '

        return E('wallLayers',
                    E('thicknessLayers', thicknessLayers),
                    E('thermalConductivityLayers', thermalConductivityLayers),
                    disabled=self.disabled)

    @staticmethod
    def fromElement(e):
        thicknessLayers = e.find('thicknessLayers', namespaces=nsmap).text.split()
        thermalConductivityLayers = e.find('thermalConductivityLayers', namespaces=nsmap).text.split()

        return TemperatureLayers(disabled=xmlToBool(e.get('disabled')),
                                 layers=[TemperatureLayer(thickness=thicknessLayers[i],
                                                          thermalConductivity=thermalConductivityLayers[i])
                                         for i in range(len(thicknessLayers))])
