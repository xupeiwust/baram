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

    centerOfMassX: str = '0'
    centerOfMassY: str = '0'
    centerOfMassZ: str = '0'

    centerOfRotationX: str = '0'
    centerOfRotationY: str = '0'
    centerOfRotationZ: str = '0'

    orientation: str = ''
    momentOfInertia: str = ''

    translationalConstraintType: TranslationalConstraintType = TranslationalConstraintType.FREE
    rotationalConstraintType: RotationalConstraintType = RotationalConstraintType.FREE

    directionX: str = '0'
    directionY: str = '0'
    directionZ: str = '0'

    normalX: str = '0'
    normalY: str = '0'
    normalZ: str = '0'

    axisX: str = '0'
    axisY: str = '0'
    axisZ: str = '1'

    limitAngle: bool = False
    clockwise: str = '0'
    counterclockwise: str = '0'

    restraints: list[Restraint] = dataClassField(default_factory=list)
    solver: RigidBodySolver = dataClassField(default_factory=RigidBodySolver)

    accelerationRelaxationFactor: str = '0'
    accelerationDampingFactor: str = '0'

    @classmethod
    def fromElement(cls, e):
        mass = e.find('mass', namespaces=nsmap).text

        centerOfMassX = e.find('centerOfMass/x', namespaces=nsmap).text
        centerOfMassY = e.find('centerOfMass/y', namespaces=nsmap).text
        centerOfMassZ = e.find('centerOfMass/z', namespaces=nsmap).text

        centerOfRotationX = e.find('centerOfRotation/x', namespaces=nsmap).text
        centerOfRotationY = e.find('centerOfRotation/y', namespaces=nsmap).text
        centerOfRotationZ = e.find('centerOfRotation/z', namespaces=nsmap).text

        orientation = e.find('orientation', namespaces=nsmap).text or ''
        momentOfInertia = e.find('momentOfInertia', namespaces=nsmap).text or ''

        translationalConstraintType = TranslationalConstraintType(
            e.find('translationalConstraintType', namespaces=nsmap).text)
        rotationalConstraintType = RotationalConstraintType(
            e.find('rotationalConstraintType', namespaces=nsmap).text)

        directionX = e.find('direction/x', namespaces=nsmap).text
        directionY = e.find('direction/y', namespaces=nsmap).text
        directionZ = e.find('direction/z', namespaces=nsmap).text

        normalX = e.find('normal/x', namespaces=nsmap).text
        normalY = e.find('normal/y', namespaces=nsmap).text
        normalZ = e.find('normal/z', namespaces=nsmap).text

        axisX = e.find('axis/x', namespaces=nsmap).text
        axisY = e.find('axis/y', namespaces=nsmap).text
        axisZ = e.find('axis/z', namespaces=nsmap).text

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
            centerOfMassX=centerOfMassX, centerOfMassY=centerOfMassY, centerOfMassZ=centerOfMassZ,
            centerOfRotationX=centerOfRotationX, centerOfRotationY=centerOfRotationY,
            centerOfRotationZ=centerOfRotationZ,
            orientation=orientation,
            momentOfInertia=momentOfInertia,
            translationalConstraintType=translationalConstraintType,
            rotationalConstraintType=rotationalConstraintType,
            directionX=directionX, directionY=directionY, directionZ=directionZ,
            normalX=normalX, normalY=normalY, normalZ=normalZ,
            axisX=axisX, axisY=axisY, axisZ=axisZ,
            limitAngle=limitAngle,
            clockwise=clockwise, counterclockwise=counterclockwise,
            restraints=restraints, solver=solver,
            accelerationRelaxationFactor=accelerationRelaxationFactor,
            accelerationDampingFactor=accelerationDampingFactor)

    def toElement(self):
        return E('rigidBodyMotion',
                 E('mass', self.mass),
                 E('centerOfMass',
                     E('x', self.centerOfMassX),
                     E('y', self.centerOfMassY),
                     E('z', self.centerOfMassZ)),
                 E('centerOfRotation',
                     E('x', self.centerOfRotationX),
                     E('y', self.centerOfRotationY),
                     E('z', self.centerOfRotationZ)),
                 E('orientation', self.orientation),
                 E('momentOfInertia', self.momentOfInertia),
                 E('translationalConstraintType', self.translationalConstraintType.value),
                 E('rotationalConstraintType', self.rotationalConstraintType.value),
                 E('direction',
                     E('x', self.directionX),
                     E('y', self.directionY),
                     E('z', self.directionZ)),
                 E('normal',
                     E('x', self.normalX),
                     E('y', self.normalY),
                     E('z', self.normalZ)),
                 E('axis',
                     E('x', self.axisX),
                     E('y', self.axisY),
                     E('z', self.axisZ)),
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

    normalX: str = '0'
    normalY: str = '0'
    normalZ: str = '0'

    motionFunctions: list[MotionFunction] = dataClassField(default_factory=list)
    rigidBodyMotion: RigidBodyMotion = dataClassField(default_factory=RigidBodyMotion)

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        boundary = e.find('boundary', namespaces=nsmap).text
        pointMotionType = PointMotionType(e.find('pointMotionType', namespaces=nsmap).text)

        normalX = e.find('normal/x', namespaces=nsmap).text
        normalY = e.find('normal/y', namespaces=nsmap).text
        normalZ = e.find('normal/z', namespaces=nsmap).text

        motionFunctions = []
        for fe in e.find('motionFunctions', namespaces=nsmap).findall('motionFunction', namespaces=nsmap):
            motionFunctions.append(MotionFunction.fromElement(fe))
        motionFunctions.sort(key=lambda f: f.order)

        rigidBodyMotion = RigidBodyMotion.fromElement(
            e.find('rigidBodyMotion', namespaces=nsmap))

        return MovingBoundaryEntry(
            uuid=uuid, boundary=boundary, pointMotionType=pointMotionType,
            normalX=normalX, normalY=normalY, normalZ=normalZ,
            motionFunctions=motionFunctions,
            rigidBodyMotion=rigidBodyMotion)

    def toElement(self):
        return E('boundary',
                 E('uuid', str(self.uuid)),
                 E('boundary', self.boundary),
                 E('pointMotionType', self.pointMotionType.value),
                 E('normal',
                     E('x', self.normalX),
                     E('y', self.normalY),
                     E('z', self.normalZ)),
                 E('motionFunctions', *[f.toElement() for f in self.motionFunctions]),
                 self.rigidBodyMotion.toElement())
