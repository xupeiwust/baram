#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from dataclasses import field as dataClassField
from enum import Enum
from uuid import UUID, uuid4

from bidict import bidict

from baramFlow.coredb.libdb import E, nsmap
from baramFlow.base.dynamic_mesh.rigid_body_solver import RigidBodySolver
from baramFlow.base.dynamic_mesh.restraint import Restraint
from baramFlow.base.xml_helper import Vector


class JointType(Enum):
    PRISMATIC  = 'prismatic'
    REVOLUTE   = 'revolute'
    SPHERICAL  = 'spherical'


@dataclass
class Joint:
    jointType: JointType

    direction: Vector = dataClassField(default_factory=Vector)
    axis: Vector = dataClassField(default_factory=lambda: Vector('0', '0', '1'))

    @classmethod
    def fromElement(cls, e):
        jointType = JointType(e.find('jointType', namespaces=nsmap).text)
        direction = Vector.fromElement(e.find('direction', namespaces=nsmap))
        axis = Vector.fromElement(e.find('axis', namespaces=nsmap))

        return Joint(jointType=jointType, direction=direction, axis=axis)

    def toElement(self):
        return E('joint',
                 E('jointType', self.jointType.value),
                 self.direction.toElement('direction'),
                 self.axis.toElement('axis'))


@dataclass(kw_only=True)
class Body:
    uuid: UUID = dataClassField(default_factory=uuid4)
    name: str
    parent: UUID

    mass: str = '0'

    centerOfMass: Vector = dataClassField(default_factory=Vector)
    centerOfRotation: Vector = dataClassField(default_factory=Vector)

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

        centerOfMass = Vector.fromElement(e.find('centerOfMass', namespaces=nsmap))
        centerOfRotation = Vector.fromElement(e.find('centerOfRotation', namespaces=nsmap))

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
                    centerOfMass=centerOfMass,
                    centerOfRotation=centerOfRotation,
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
                 self.centerOfMass.toElement('centerOfMass'),
                 self.centerOfRotation.toElement('centerOfRotation'),
                 E('orientation', self.orientation),
                 E('momentOfInertia', self.momentOfInertia),
                 E('boundaries', ' '.join(self.boundaries)),
                 jointsElement,
                 E('deformationOffset', self.deformationOffset),
                 E('deformationDistance', self.deformationDistance))

    def processMeshUpdate(self, oldBoundaries: bidict[str, str], newBoundaries: bidict[str, str]):
        boundaries: list[str] = []
        for boundary in self.boundaries:
            name = oldBoundaries.inverse[boundary]
            if name in newBoundaries:
                boundaries.append(newBoundaries[name])

        self.boundaries = boundaries


@dataclass
class RigidBodyDynamics:
    solver: RigidBodySolver = dataClassField(default_factory=RigidBodySolver)
    accelerationRelaxationFactor: str = '0.7'
    accelerationDampingFactor: str = '1.0'
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
