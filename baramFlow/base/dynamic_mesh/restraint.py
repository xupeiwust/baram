#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from baramFlow.coredb.libdb import E, nsmap


class RestraintType(Enum):
    SIMPLE_DAMPER         = 'simpleDamper'
    TRANSLATIONAL_SPRING  = 'translationalSpring'
    ROTATIONAL_SPRING     = 'rotationalSpring'


@dataclass
class Restraint:
    uuid: UUID
    order: int
    restraintType: RestraintType

    dampingConstant: str = '0'
    springConstant: str = '0'
    restLength: str = '0'

    axisX: str = '0'
    axisY: str = '0'
    axisZ: str = '1'

    attachmentPointX: str = '0'
    attachmentPointY: str = '0'
    attachmentPointZ: str = '0'

    anchorPointX: str = '0'
    anchorPointY: str = '0'
    anchorPointZ: str = '0'

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        order = int(e.find('order', namespaces=nsmap).text)
        restraintType = RestraintType(e.find('restraintType', namespaces=nsmap).text)

        dampingConstant = e.find('dampingConstant', namespaces=nsmap).text
        springConstant = e.find('springConstant', namespaces=nsmap).text
        restLength = e.find('restLength', namespaces=nsmap).text

        axisX = e.find('axis/x', namespaces=nsmap).text
        axisY = e.find('axis/y', namespaces=nsmap).text
        axisZ = e.find('axis/z', namespaces=nsmap).text

        attachmentPointX = e.find('attachmentPoint/x', namespaces=nsmap).text
        attachmentPointY = e.find('attachmentPoint/y', namespaces=nsmap).text
        attachmentPointZ = e.find('attachmentPoint/z', namespaces=nsmap).text

        anchorPointX = e.find('anchorPoint/x', namespaces=nsmap).text
        anchorPointY = e.find('anchorPoint/y', namespaces=nsmap).text
        anchorPointZ = e.find('anchorPoint/z', namespaces=nsmap).text

        return Restraint(uuid=uuid, order=order, restraintType=restraintType,
                         dampingConstant=dampingConstant,
                         springConstant=springConstant,
                         restLength=restLength,
                         axisX=axisX, axisY=axisY, axisZ=axisZ,
                         attachmentPointX=attachmentPointX,
                         attachmentPointY=attachmentPointY,
                         attachmentPointZ=attachmentPointZ,
                         anchorPointX=anchorPointX,
                         anchorPointY=anchorPointY,
                         anchorPointZ=anchorPointZ)

    def toElement(self):
        return E('restraint',
                 E('uuid', str(self.uuid)),
                 E('order', str(self.order)),
                 E('restraintType', self.restraintType.value),
                 E('dampingConstant', self.dampingConstant),
                 E('springConstant', self.springConstant),
                 E('restLength', self.restLength),
                 E('axis',
                     E('x', self.axisX),
                     E('y', self.axisY),
                     E('z', self.axisZ)),
                 E('attachmentPoint',
                     E('x', self.attachmentPointX),
                     E('y', self.attachmentPointY),
                     E('z', self.attachmentPointZ)),
                 E('anchorPoint',
                     E('x', self.anchorPointX),
                     E('y', self.anchorPointY),
                     E('z', self.anchorPointZ)))
