#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum
from uuid import UUID, uuid4

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.xml_helper import Vector
from libbaram.pfloat import PFloat


class MotionFunctionType(Enum):
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


@dataclass(kw_only=True)
class MotionFunction:
    uuid: UUID = dataClassField(default_factory=uuid4)
    order: int
    functionType: MotionFunctionType

    origin: Vector = dataClassField(default_factory=Vector.zero)
    axis: Vector = dataClassField(default_factory=Vector.zUnit)
    rpm: PFloat = dataClassField(default_factory=lambda: PFloat('0'))

    velocity: Vector = dataClassField(default_factory=Vector.zero)
    angularAmplitude: Vector = dataClassField(default_factory=Vector.zero)
    linearAmplitude: Vector = dataClassField(default_factory=Vector.zero)

    frequency: PFloat = dataClassField(default_factory=lambda: PFloat('0'))

    positions: Positions = None

    def __post_init__(self):
        if self.positions is None:
            self.positions = Positions()

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        order = int(e.find('order', namespaces=nsmap).text)
        functionType = MotionFunctionType(e.find('functionType', namespaces=nsmap).text)

        origin = Vector.fromElement(e.find('origin', namespaces=nsmap))
        axis = Vector.fromElement(e.find('axis', namespaces=nsmap))
        rpm = PFloat.fromElement(e.find('rpm', namespaces=nsmap))

        velocity = Vector.fromElement(e.find('velocity', namespaces=nsmap))
        angularAmplitude = Vector.fromElement(e.find('angularAmplitude', namespaces=nsmap))
        linearAmplitude = Vector.fromElement(e.find('linearAmplitude', namespaces=nsmap))

        frequency = PFloat.fromElement(e.find('frequency', namespaces=nsmap))

        positions = Positions.fromElement(e.find('positions', namespaces=nsmap))

        return MotionFunction(uuid=uuid, order=order, functionType=functionType,
                              origin=origin,
                              axis=axis,
                              rpm=rpm,
                              velocity=velocity,
                              angularAmplitude=angularAmplitude,
                              linearAmplitude=linearAmplitude,
                              frequency=frequency,
                              positions=positions)

    def toElement(self):
        return E('motionFunction',
                 E('uuid', str(self.uuid)),
                 E('order', str(self.order)),
                 E('functionType', self.functionType.value),
                 self.origin.toElement('origin'),
                 self.axis.toElement('axis'),
                 self.rpm.toElement('rpm'),
                 self.velocity.toElement('velocity'),
                 self.angularAmplitude.toElement('angularAmplitude'),
                 self.linearAmplitude.toElement('linearAmplitude'),
                 self.frequency.toElement('frequency'),
                 self.positions.toElement())
