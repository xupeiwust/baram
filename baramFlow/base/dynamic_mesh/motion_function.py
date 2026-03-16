#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from baramFlow.coredb.libdb import E, nsmap


class FunctionType(Enum):
    ROTATION              = 'rotation'
    ROTATING_OSCILLATION  = 'rotatingOscillation'
    LINEAR_TRANSLATION    = 'linearTranslation'
    LINEAR_OSCILLATION    = 'linearOscillation'
    MANUAL_POSITION       = 'manualPosition'


@dataclass
class Positions:
    t: str = ''
    surge: str = ''
    sway: str = ''
    heave: str = ''
    roll: str = ''
    pitch: str = ''
    yaw: str = ''

    @classmethod
    def fromElement(cls, e):
        t = e.find('t', namespaces=nsmap).text or ''
        surge = e.find('surge', namespaces=nsmap).text or ''
        sway = e.find('sway', namespaces=nsmap).text or ''
        heave = e.find('heave', namespaces=nsmap).text or ''
        roll = e.find('roll', namespaces=nsmap).text or ''
        pitch = e.find('pitch', namespaces=nsmap).text or ''
        yaw = e.find('yaw', namespaces=nsmap).text or ''

        return Positions(t=t, surge=surge, sway=sway, heave=heave,
                         roll=roll, pitch=pitch, yaw=yaw)

    def toElement(self):
        return E('positions',
                 E('t', self.t),
                 E('surge', self.surge),
                 E('sway', self.sway),
                 E('heave', self.heave),
                 E('roll', self.roll),
                 E('pitch', self.pitch),
                 E('yaw', self.yaw))


@dataclass
class MotionFunction:
    uuid: UUID
    order: int
    functionType: FunctionType

    centerX: str = '0'
    centerY: str = '0'
    centerZ: str = '0'

    axisX: str = '0'
    axisY: str = '0'
    axisZ: str = '1'

    omega: str = '0'

    velocityX: str = '0'
    velocityY: str = '0'
    velocityZ: str = '0'

    angularAmplitudeX: str = '0'
    angularAmplitudeY: str = '0'
    angularAmplitudeZ: str = '0'

    linearAmplitudeX: str = '0'
    linearAmplitudeY: str = '0'
    linearAmplitudeZ: str = '0'

    frequency: str = '0'

    positions: Positions = None

    def __post_init__(self):
        if self.positions is None:
            self.positions = Positions()

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        order = int(e.find('order', namespaces=nsmap).text)
        functionType = FunctionType(e.find('functionType', namespaces=nsmap).text)

        centerX = e.find('center/x', namespaces=nsmap).text
        centerY = e.find('center/y', namespaces=nsmap).text
        centerZ = e.find('center/z', namespaces=nsmap).text

        axisX = e.find('axis/x', namespaces=nsmap).text
        axisY = e.find('axis/y', namespaces=nsmap).text
        axisZ = e.find('axis/z', namespaces=nsmap).text

        omega = e.find('omega', namespaces=nsmap).text

        velocityX = e.find('velocity/x', namespaces=nsmap).text
        velocityY = e.find('velocity/y', namespaces=nsmap).text
        velocityZ = e.find('velocity/z', namespaces=nsmap).text

        angularAmplitudeX = e.find('angularAmplitude/x', namespaces=nsmap).text
        angularAmplitudeY = e.find('angularAmplitude/y', namespaces=nsmap).text
        angularAmplitudeZ = e.find('angularAmplitude/z', namespaces=nsmap).text

        linearAmplitudeX = e.find('linearAmplitude/x', namespaces=nsmap).text
        linearAmplitudeY = e.find('linearAmplitude/y', namespaces=nsmap).text
        linearAmplitudeZ = e.find('linearAmplitude/z', namespaces=nsmap).text

        frequency = e.find('frequency', namespaces=nsmap).text

        positions = Positions.fromElement(e.find('positions', namespaces=nsmap))

        return MotionFunction(uuid=uuid, order=order, functionType=functionType,
                              centerX=centerX, centerY=centerY, centerZ=centerZ,
                              axisX=axisX, axisY=axisY, axisZ=axisZ,
                              omega=omega,
                              velocityX=velocityX, velocityY=velocityY, velocityZ=velocityZ,
                              angularAmplitudeX=angularAmplitudeX,
                              angularAmplitudeY=angularAmplitudeY,
                              angularAmplitudeZ=angularAmplitudeZ,
                              linearAmplitudeX=linearAmplitudeX,
                              linearAmplitudeY=linearAmplitudeY,
                              linearAmplitudeZ=linearAmplitudeZ,
                              frequency=frequency,
                              positions=positions)

    def toElement(self):
        return E('motionFunction',
                 E('uuid', str(self.uuid)),
                 E('order', str(self.order)),
                 E('functionType', self.functionType.value),
                 E('center',
                     E('x', self.centerX),
                     E('y', self.centerY),
                     E('z', self.centerZ)),
                 E('axis',
                     E('x', self.axisX),
                     E('y', self.axisY),
                     E('z', self.axisZ)),
                 E('omega', self.omega),
                 E('velocity',
                     E('x', self.velocityX),
                     E('y', self.velocityY),
                     E('z', self.velocityZ)),
                 E('angularAmplitude',
                     E('x', self.angularAmplitudeX),
                     E('y', self.angularAmplitudeY),
                     E('z', self.angularAmplitudeZ)),
                 E('linearAmplitude',
                     E('x', self.linearAmplitudeX),
                     E('y', self.linearAmplitudeY),
                     E('z', self.linearAmplitudeZ)),
                 E('frequency', self.frequency),
                 self.positions.toElement())
