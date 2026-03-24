#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum
from uuid import UUID, uuid4

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.xml_helper import Vector


class RestraintType(Enum):
    SIMPLE_DAMPER         = 'simpleDamper'
    TRANSLATIONAL_SPRING  = 'translationalSpring'
    ROTATIONAL_SPRING     = 'rotationalSpring'


@dataclass(kw_only=True)
class Restraint:
    uuid: UUID = dataClassField(default_factory=uuid4)
    order: int
    restraintType: RestraintType

    dampingConstant: str = '0'
    springConstant: str = '0'
    restLength: str = '0'

    axis: Vector = dataClassField(default_factory=lambda: Vector('0', '0', '1'))
    attachmentPoint: Vector = dataClassField(default_factory=Vector)
    anchorPoint: Vector = dataClassField(default_factory=Vector)

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        order = int(e.find('order', namespaces=nsmap).text)
        restraintType = RestraintType(e.find('restraintType', namespaces=nsmap).text)

        dampingConstant = e.find('dampingConstant', namespaces=nsmap).text
        springConstant = e.find('springConstant', namespaces=nsmap).text
        restLength = e.find('restLength', namespaces=nsmap).text

        axis = Vector.fromElement(e.find('axis', namespaces=nsmap))
        attachmentPoint = Vector.fromElement(e.find('attachmentPoint', namespaces=nsmap))
        anchorPoint = Vector.fromElement(e.find('anchorPoint', namespaces=nsmap))

        return Restraint(uuid=uuid, order=order, restraintType=restraintType,
                         dampingConstant=dampingConstant,
                         springConstant=springConstant,
                         restLength=restLength,
                         axis=axis,
                         attachmentPoint=attachmentPoint,
                         anchorPoint=anchorPoint)

    def toElement(self):
        return E('restraint',
                 E('uuid', str(self.uuid)),
                 E('order', str(self.order)),
                 E('restraintType', self.restraintType.value),
                 E('dampingConstant', self.dampingConstant),
                 E('springConstant', self.springConstant),
                 E('restLength', self.restLength),
                 self.axis.toElement('axis'),
                 self.attachmentPoint.toElement('attachmentPoint'),
                 self.anchorPoint.toElement('anchorPoint'))
