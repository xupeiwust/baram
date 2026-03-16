#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from uuid import UUID

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.dynamic_mesh.motion_function import MotionFunction


@dataclass
class MotionDefinition:
    uuid: UUID
    name: str
    order: int
    motionFunctions: list[MotionFunction] = dataClassField(default_factory=list)
    cellZones: list[str] = dataClassField(default_factory=list)

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        name = e.find('name', namespaces=nsmap).text
        order = int(e.find('order', namespaces=nsmap).text)

        motionFunctions = []
        for fe in e.find('motionFunctions', namespaces=nsmap).findall('motionFunction', namespaces=nsmap):
            motionFunctions.append(MotionFunction.fromElement(fe))
        motionFunctions.sort(key=lambda f: f.order)

        cellZonesText = e.find('cellZones', namespaces=nsmap).text or ''
        cellZones: list[str] = cellZonesText.split() if cellZonesText.strip() else []

        return MotionDefinition(uuid=uuid, name=name, order=order,
                                motionFunctions=motionFunctions,
                                cellZones=cellZones)

    def toElement(self):
        return E('motionDefinition',
                 E('uuid', str(self.uuid)),
                 E('name', self.name),
                 E('order', str(self.order)),
                 E('motionFunctions', *[f.toElement() for f in self.motionFunctions]),
                 E('cellZones', ' '.join(self.cellZones)))
