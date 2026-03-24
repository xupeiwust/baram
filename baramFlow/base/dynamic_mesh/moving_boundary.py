#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum
from uuid import UUID, uuid4

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.dynamic_mesh.motion_function import MotionFunction
from baramFlow.base.dynamic_mesh.rigid_body_solver import RigidBodySolver
from baramFlow.base.dynamic_mesh.restraint import (
    Restraint,
)
from baramFlow.base.xml_helper import Vector


class PointMotionType(Enum):
    FIXED             = 'fixed'
    SLIP              = 'slip'
    NORMAL            = 'normal'
    PRESCRIBED_MOTION = 'prescribedMotion'
    RIGID_BODY_MOTION = 'rigidBodyMotion'
    CYCLIC            = 'cyclic'
    CYCLIC_AMI        = 'cyclicAMI'
    SYMMETRY          = 'symmetry'
    EMPTY             = 'empty'
    WEDGE             = 'wedge'


class TranslationalConstraintType(Enum):
    FREE  = 'free'
    PLANE = 'plane'
    LINE  = 'line'
    FIXED = 'fixed'


class RotationalConstraintType(Enum):
    FREE  = 'free'
    AXIS  = 'axis'
    FIXED = 'fixed'


@dataclass
class RigidBodyMotion:
    mass: str = '0'

    centerOfMass: Vector = dataClassField(default_factory=Vector)
    centerOfRotation: Vector = dataClassField(default_factory=Vector)

    orientation: str = ''
    momentOfInertia: str = ''

    translationalConstraintType: TranslationalConstraintType = TranslationalConstraintType.FREE
    rotationalConstraintType: RotationalConstraintType = RotationalConstraintType.FREE

    direction: Vector = dataClassField(default_factory=Vector)
    normal: Vector = dataClassField(default_factory=Vector)
    axis: Vector = dataClassField(default_factory=lambda: Vector('0', '0', '1'))

    limitAngle: bool = False
    clockwise: str = '0'
    counterclockwise: str = '0'

    restraints: list[Restraint] = dataClassField(default_factory=list)
    solver: RigidBodySolver = dataClassField(default_factory=RigidBodySolver)

    accelerationRelaxationFactor: str = '0.7'
    accelerationDampingFactor: str = '1.0'

    @classmethod
    def fromElement(cls, e):
        mass = e.find('mass', namespaces=nsmap).text

        centerOfMass = Vector.fromElement(e.find('centerOfMass', namespaces=nsmap))
        centerOfRotation = Vector.fromElement(e.find('centerOfRotation', namespaces=nsmap))

        orientation = e.find('orientation', namespaces=nsmap).text or ''
        momentOfInertia = e.find('momentOfInertia', namespaces=nsmap).text or ''

        translationalConstraintType = TranslationalConstraintType(
            e.find('translationalConstraintType', namespaces=nsmap).text)
        rotationalConstraintType = RotationalConstraintType(
            e.find('rotationalConstraintType', namespaces=nsmap).text)

        direction = Vector.fromElement(e.find('direction', namespaces=nsmap))
        normal = Vector.fromElement(e.find('normal', namespaces=nsmap))
        axis = Vector.fromElement(e.find('axis', namespaces=nsmap))

        limitAngle = e.find('limitAngle', namespaces=nsmap).text == 'true'
        clockwise = e.find('clockwise', namespaces=nsmap).text
        counterclockwise = e.find('counterclockwise', namespaces=nsmap).text

        restraints = []
        for re_ in e.find('rigidBodyRestraints', namespaces=nsmap).findall('restraint', namespaces=nsmap):
            restraints.append(Restraint.fromElement(re_))
        restraints.sort(key=lambda r: r.order)

        solver = RigidBodySolver.fromElement(e.find('rigidBodySolverType', namespaces=nsmap))

        accelerationRelaxationFactor = e.find('accelerationRelaxationFactor', namespaces=nsmap).text
        accelerationDampingFactor = e.find('accelerationDampingFactor', namespaces=nsmap).text

        return RigidBodyMotion(
            mass=mass,
            centerOfMass=centerOfMass,
            centerOfRotation=centerOfRotation,
            orientation=orientation,
            momentOfInertia=momentOfInertia,
            translationalConstraintType=translationalConstraintType,
            rotationalConstraintType=rotationalConstraintType,
            direction=direction,
            normal=normal,
            axis=axis,
            limitAngle=limitAngle,
            clockwise=clockwise, counterclockwise=counterclockwise,
            restraints=restraints, solver=solver,
            accelerationRelaxationFactor=accelerationRelaxationFactor,
            accelerationDampingFactor=accelerationDampingFactor)

    def toElement(self):
        return E('rigidBodyMotion',
                 E('mass', self.mass),
                 self.centerOfMass.toElement('centerOfMass'),
                 self.centerOfRotation.toElement('centerOfRotation'),
                 E('orientation', self.orientation),
                 E('momentOfInertia', self.momentOfInertia),
                 E('translationalConstraintType', self.translationalConstraintType.value),
                 E('rotationalConstraintType', self.rotationalConstraintType.value),
                 self.direction.toElement('direction'),
                 self.normal.toElement('normal'),
                 self.axis.toElement('axis'),
                 E('limitAngle', self.limitAngle),
                 E('clockwise', self.clockwise),
                 E('counterclockwise', self.counterclockwise),
                 E('rigidBodyRestraints', *[r.toElement() for r in self.restraints]),
                 self.solver.toElement(),
                 E('accelerationRelaxationFactor', self.accelerationRelaxationFactor),
                 E('accelerationDampingFactor', self.accelerationDampingFactor))


@dataclass(kw_only=True)
class MovingBoundaryEntry:
    uuid: UUID = dataClassField(default_factory=uuid4)
    boundary: str = '0'
    pointMotionType: PointMotionType = PointMotionType.FIXED

    normal: Vector = dataClassField(default_factory=Vector)

    motionFunctions: list[MotionFunction] = dataClassField(default_factory=list)
    rigidBodyMotion: RigidBodyMotion = dataClassField(default_factory=RigidBodyMotion)

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        boundary = e.find('boundary', namespaces=nsmap).text
        pointMotionType = PointMotionType(e.find('pointMotionType', namespaces=nsmap).text)

        normal = Vector.fromElement(e.find('normal', namespaces=nsmap))

        motionFunctions = []
        for fe in e.find('motionFunctions', namespaces=nsmap).findall('motionFunction', namespaces=nsmap):
            motionFunctions.append(MotionFunction.fromElement(fe))
        motionFunctions.sort(key=lambda f: f.order)

        rigidBodyMotion = RigidBodyMotion.fromElement(
            e.find('rigidBodyMotion', namespaces=nsmap))

        return MovingBoundaryEntry(
            uuid=uuid, boundary=boundary, pointMotionType=pointMotionType,
            normal=normal,
            motionFunctions=motionFunctions,
            rigidBodyMotion=rigidBodyMotion)

    def toElement(self):
        return E('boundary',
                 E('uuid', str(self.uuid)),
                 E('boundary', self.boundary),
                 E('pointMotionType', self.pointMotionType.value),
                 self.normal.toElement('normal'),
                 E('motionFunctions', *[f.toElement() for f in self.motionFunctions]),
                 self.rigidBodyMotion.toElement())
