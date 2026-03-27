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
from libbaram.pfloat import PFloat


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
    mass: PFloat = PFloat('0')

    centerOfMass: Vector = dataClassField(default_factory=Vector)
    centerOfRotation: Vector = dataClassField(default_factory=Vector)

    orientation: str = ''
    momentOfInertia: str = ''

    translationalConstraintType: TranslationalConstraintType = TranslationalConstraintType.FREE
    rotationalConstraintType: RotationalConstraintType = RotationalConstraintType.FREE

    direction: Vector = dataClassField(default_factory=Vector)
    normal: Vector = dataClassField(default_factory=Vector)
    axis: Vector = dataClassField(default_factory=Vector.zUnit)

    limitAngle: bool = False
    clockwise: PFloat = PFloat('0')
    counterclockwise: PFloat = PFloat('0')

    restraints: list[Restraint] = dataClassField(default_factory=list)
    solver: RigidBodySolver = dataClassField(default_factory=RigidBodySolver)

    accelerationRelaxationFactor: PFloat = PFloat('0.7')
    accelerationDampingFactor: PFloat = PFloat('1.0')

    @classmethod
    def fromElement(cls, e):
        mass = PFloat.fromElement(e.find('mass', namespaces=nsmap))

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
        clockwise = PFloat.fromElement(e.find('clockwise', namespaces=nsmap))
        counterclockwise = PFloat.fromElement(e.find('counterclockwise', namespaces=nsmap))

        restraints = []
        for re_ in e.find('rigidBodyRestraints', namespaces=nsmap).findall('restraint', namespaces=nsmap):
            restraints.append(Restraint.fromElement(re_))
        restraints.sort(key=lambda r: r.order)

        solver = RigidBodySolver.fromElement(e.find('rigidBodySolverType', namespaces=nsmap))

        accelerationRelaxationFactor = PFloat.fromElement(e.find('accelerationRelaxationFactor', namespaces=nsmap))
        accelerationDampingFactor = PFloat.fromElement(e.find('accelerationDampingFactor', namespaces=nsmap))

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
                 self.mass.toElement('mass'),
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
                 self.clockwise.toElement('clockwise'),
                 self.counterclockwise.toElement('counterclockwise'),
                 E('rigidBodyRestraints', *[r.toElement() for r in self.restraints]),
                 self.solver.toElement(),
                 self.accelerationRelaxationFactor.toElement('accelerationRelaxationFactor'),
                 self.accelerationDampingFactor.toElement('accelerationDampingFactor'))


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
