#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum
from uuid import UUID

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.dynamic_mesh.rigid_body_solver import RigidBodySolver
from baramFlow.base.dynamic_mesh.restraint import Restraint


class JointType(Enum):
    PRISMATIC  = 'prismatic'
    REVOLUTE   = 'revolute'
    SPHERICAL  = 'spherical'


@dataclass
class Joint:
    jointType: JointType

    directionX: str = '0'
    directionY: str = '0'
    directionZ: str = '0'

    axisX: str = '0'
    axisY: str = '0'
    axisZ: str = '1'

    @classmethod
    def fromElement(cls, e):
        jointType = JointType(e.find('jointType', namespaces=nsmap).text)

        directionX = e.find('direction/x', namespaces=nsmap).text
        directionY = e.find('direction/y', namespaces=nsmap).text
        directionZ = e.find('direction/z', namespaces=nsmap).text

        axisX = e.find('axis/x', namespaces=nsmap).text
        axisY = e.find('axis/y', namespaces=nsmap).text
        axisZ = e.find('axis/z', namespaces=nsmap).text

        return Joint(jointType=jointType,
                     directionX=directionX, directionY=directionY, directionZ=directionZ,
                     axisX=axisX, axisY=axisY, axisZ=axisZ)

    def toElement(self):
        return E('joint',
                 E('jointType', self.jointType.value),
                 E('direction',
                     E('x', self.directionX),
                     E('y', self.directionY),
                     E('z', self.directionZ)),
                 E('axis',
                     E('x', self.axisX),
                     E('y', self.axisY),
                     E('z', self.axisZ)))


@dataclass
class Body:
    uuid: UUID
    name: str
    parent: UUID

    mass: str = '0'

    centerOfMassX: str = '0'
    centerOfMassY: str = '0'
    centerOfMassZ: str = '0'

    centerOfRotationX: str = '0'
    centerOfRotationY: str = '0'
    centerOfRotationZ: str = '0'

    orientation: str = ''
    momentOfInertia: str = ''

    boundaries: list[str] = dataClassField(default_factory=list)
    joints: list[Joint] = dataClassField(default_factory=list)

    deformationOffset: str = '0'
    deformationDistance: str = '0'

    @classmethod
    def fromElement(cls, e):
        uuid = UUID(e.find('uuid', namespaces=nsmap).text)
        name = e.find('name', namespaces=nsmap).text
        parent = UUID(e.find('parent', namespaces=nsmap).text)

        mass = e.find('mass', namespaces=nsmap).text

        centerOfMassX = e.find('centerOfMass/x', namespaces=nsmap).text
        centerOfMassY = e.find('centerOfMass/y', namespaces=nsmap).text
        centerOfMassZ = e.find('centerOfMass/z', namespaces=nsmap).text

        centerOfRotationX = e.find('centerOfRotation/x', namespaces=nsmap).text
        centerOfRotationY = e.find('centerOfRotation/y', namespaces=nsmap).text
        centerOfRotationZ = e.find('centerOfRotation/z', namespaces=nsmap).text

        orientation = e.find('orientation', namespaces=nsmap).text or ''
        momentOfInertia = e.find('momentOfInertia', namespaces=nsmap).text or ''

        boundariesText = e.find('boundaries', namespaces=nsmap).text or ''
        boundaries: list[str] = boundariesText.split() if boundariesText.strip() else []

        joints = []
        jointsElement = e.find('joints', namespaces=nsmap)
        for je in jointsElement.findall('joint', namespaces=nsmap):
            joints.append(Joint.fromElement(je))

        deformationOffset = e.find('deformationOffset', namespaces=nsmap).text
        deformationDistance = e.find('deformationDistance', namespaces=nsmap).text

        return Body(uuid=uuid, name=name, parent=parent,
                    mass=mass,
                    centerOfMassX=centerOfMassX, centerOfMassY=centerOfMassY,
                    centerOfMassZ=centerOfMassZ,
                    centerOfRotationX=centerOfRotationX, centerOfRotationY=centerOfRotationY,
                    centerOfRotationZ=centerOfRotationZ,
                    orientation=orientation,
                    momentOfInertia=momentOfInertia,
                    boundaries=boundaries,
                    joints=joints,
                    deformationOffset=deformationOffset,
                    deformationDistance=deformationDistance)

    def toElement(self):
        jointsElement = E('joints')
        for j in self.joints:
            jointsElement.append(j.toElement())

        return E('body',
                 E('uuid', str(self.uuid)),
                 E('name', self.name),
                 E('parent', str(self.parent)),
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
                 E('boundaries', ' '.join(self.boundaries)),
                 jointsElement,
                 E('deformationOffset', self.deformationOffset),
                 E('deformationDistance', self.deformationDistance))


@dataclass
class RigidBodyDynamics:
    solver: RigidBodySolver = dataClassField(default_factory=RigidBodySolver)
    accelerationRelaxationFactor: str = '0'
    accelerationDampingFactor: str = '0'
    bodies: list[Body] = dataClassField(default_factory=list)
    restraints: list[Restraint] = dataClassField(default_factory=list)

    @classmethod
    def fromElement(cls, e):
        solver = RigidBodySolver.fromElement(e.find('rigidBodySolverType', namespaces=nsmap))
        accelerationRelaxationFactor = e.find('accelerationRelaxationFactor', namespaces=nsmap).text
        accelerationDampingFactor = e.find('accelerationDampingFactor', namespaces=nsmap).text

        bodies = []
        bodiesElement = e.find('bodies', namespaces=nsmap)
        for be in bodiesElement.findall('body', namespaces=nsmap):
            bodies.append(Body.fromElement(be))

        restraints = []
        for re_ in e.find('rigidBodyRestraints', namespaces=nsmap).findall('restraint', namespaces=nsmap):
            restraints.append(Restraint.fromElement(re_))
        restraints.sort(key=lambda r: r.order)

        return RigidBodyDynamics(
            solver=solver,
            accelerationRelaxationFactor=accelerationRelaxationFactor,
            accelerationDampingFactor=accelerationDampingFactor,
            bodies=bodies,
            restraints=restraints)

    def toElement(self):
        bodiesElement = E('bodies')
        for b in self.bodies:
            bodiesElement.append(b.toElement())

        return E('rigidBodyDynamics',
                 self.solver.toElement(),
                 E('accelerationRelaxationFactor', self.accelerationRelaxationFactor),
                 E('accelerationDampingFactor', self.accelerationDampingFactor),
                 bodiesElement,
                 E('rigidBodyRestraints', *[r.toElement() for r in self.restraints]))
