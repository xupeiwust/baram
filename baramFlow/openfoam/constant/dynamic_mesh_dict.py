#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from uuid import UUID

from baramFlow.base.dynamic_mesh.dynamic_mesh import MotionType
from baramFlow.base.dynamic_mesh.motion_function import MotionFunctionType
from baramFlow.base.dynamic_mesh.moving_boundary import PointMotionType
from baramFlow.base.dynamic_mesh.restraint import RestraintType
from baramFlow.base.dynamic_mesh.rigid_body_dynamics import Joint, JointType
from baramFlow.base.dynamic_mesh.rigid_body_solver import RigidBodyDynamicsSolverType
from baramFlow.base.xml_helper import Vector
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.services.dynamic_mesh.dynamic_mesh_service import DynamicMeshService
from libbaram.natural_name_uuid import uuidToNnstr
from libbaram.openfoam.dictionary.dictionary_file import DictionaryFile

from baramFlow.coredb.cell_zone_db import ZoneType, CellZoneDB
from baramFlow.coredb.coredb_reader import CoreDBReader
from baramFlow.openfoam.file_system import FileSystem


_motionFunctionNames = {
    MotionFunctionType.ROTATION: 'rotatingMotion',
    MotionFunctionType.ROTATING_OSCILLATION: 'oscillatingRotatingMotion',
    MotionFunctionType.LINEAR_TRANSLATION: 'linearMotion',
    MotionFunctionType.LINEAR_OSCILLATION: 'oscillatingLinearMotion',
    MotionFunctionType.MANUAL_POSITION: 'tabulated6DoFMotion'
}




class DynamicMeshDict(DictionaryFile):
    def __init__(self, rname: str):
        super().__init__(FileSystem.caseRoot(), self.constantLocation(rname), 'dynamicMeshDict')

        self._rname = rname

        self._dynamicMesh = DynamicMeshService().getDynamicMesh()

    def build(self):
        if self._data is not None:
            return self

        if self._dynamicMesh.motionType == MotionType.MOVING_CELL_ZONE:
            self._buildMovingCellZone()
        elif self._dynamicMesh.motionType == MotionType.MOVING_BOUNDARY:
            self._buildMovingBoundary()
        elif self._dynamicMesh.motionType == MotionType.RIGID_BODY_DYNAMICS:
            self._buildRigidBodyDynamics()

        # db = CoreDBReader()

        # zones = db.getCellZonesByType(self._rname, ZoneType.SLIDING_MESH.value)
        # if zones:
        #     self._data = {
        #         'dynamicFvMesh': 'dynamicMotionSolverListFvMesh',
        #         'motionSolverLibs': ['"libfvMotionSolvers.so"'],
        #         'motionSolver': 'fvMotionSolvers',
        #         'solvers': {}
        #     }

        #     for czid in zones:
        #         xpath = CellZoneDB.getXPath(czid)
        #         name = db.getValue(xpath + '/name')

        #         self._data['solvers'][f'sliding_{name}'] = {
        #             'solver': 'solidBody',
        #             'solidBodyMotionFunction': 'rotatingMotion',
        #             'cellZone': name,
        #             'rotatingMotionCoeffs': {
        #                 'origin': db.getVector(xpath + '/slidingMesh/rotationAxisOrigin'),
        #                 'axis': db.getVector(xpath + '/slidingMesh/rotationAxisDirection'),
        #                 'omega': float(db.getValue(xpath + '/slidingMesh/rotatingSpeed')) * 2 * 3.141592 / 60
        #             }
        #         }

        return self

    def _buildMovingCellZone(self):
        self._data = {
            'dynamicFvMesh': 'dynamicMotionSolverListFvMesh',
            'motionSolverLibs': ['fvMotionSolvers'],
            'solvers': {}
        }

        for motionDefinition in self._dynamicMesh.motionDefinitions:
            mdData = {
                'motionSolver': 'solidBody',
                'solidBodyCoeffs': {
                    'solidBodyMotionFunction': 'multiMotion',
                    'multiMotionCoeffs': {}
                }
            }
            if motionDefinition.cellZones:
                mdData['cellZone'] = '(' + '|'.join(motionDefinition.cellZones) + ')'

            for mFunction in motionDefinition.motionFunctions:
                mfData: dict = {
                    'solidBodyMotionFunction': _motionFunctionNames[mFunction.functionType]
                }

                if mFunction.functionType == MotionFunctionType.ROTATION:
                    mfData['origin'] = mFunction.origin.toFloatList()
                    mfData['axis'] = mFunction.axis.toFloatList()
                    mfData['omega'] = float(mFunction.rpm) * 2 * math.pi / 60.0
                elif mFunction.functionType == MotionFunctionType.ROTATING_OSCILLATION:
                    mfData['origin'] = mFunction.origin.toFloatList()
                    mfData['amplitude'] = mFunction.angularAmplitude.toFloatList()
                    mfData['omega'] = float(mFunction.rpm) * 2 * math.pi / 60.0
                elif mFunction.functionType == MotionFunctionType.LINEAR_TRANSLATION:
                    mfData['velocity'] = mFunction.velocity.toFloatList()
                elif mFunction.functionType == MotionFunctionType.LINEAR_OSCILLATION:
                    mfData['amplitude'] = mFunction.linearAmplitude.toFloatList()
                    mfData['omega'] = float(mFunction.frequency) * 2 * math.pi
                elif mFunction.functionType == MotionFunctionType.MANUAL_POSITION:
                    mfData['CofG'] = mFunction.origin.toFloatList()
                    # ToDo: save data to file and add the name into the dictionary

                mdData['multiMotionCoeffs'][uuidToNnstr(mFunction.uuid)] = mfData

            self._data['solvers'][uuidToNnstr(motionDefinition.uuid)]

    def _buildMovingBoundary(self):
        movingBoundaries = [BoundaryDB.getBoundaryName(mb.boundary) for mb in self._dynamicMesh.movingBoundaries
                            if mb.pointMotionType in (PointMotionType.PRESCRIBED_MOTION, PointMotionType.RIGID_BODY_MOTION)]

        self._data = {
            'dynamicFvMesh': 'dynamicMotionSolverFvMesh',
            'motionSolverLibs': ['fvMotionSolvers'],
            'motionSolver': 'displacementLaplacian',
            'displacementLaplacianCoeffs': {
                'diffusivity': ('inverseDistance', [movingBoundaries])
            }
        }


    def _buildRigidBodyDynamics(self):
        rbd = self._dynamicMesh.rigidBodyDynamics

        if rbd.solver.solverType == RigidBodyDynamicsSolverType.NEWMARK:
            solver = {
                'type': 'Newmakr',
                'gamma': float(rbd.solver.velocityIntegrationCoefficient),
                'beta': float(rbd.solver.positionIntegrationCoefficient)
            }
        elif rbd.solver.solverType == RigidBodyDynamicsSolverType.CRANK_NICOLSON:
            solver = {
                'type': 'CrankNicolson',
                'aoc': float(rbd.solver.offCenteringAccelerationCoefficient),
                'beta': float(rbd.solver.offCenteringVelocityCoefficient)
            }
        elif rbd.solver.solverType == RigidBodyDynamicsSolverType.SYMPLECTIC:
            solver = {
                'type': 'symplectic',
            }
        else:
            raise AssertionError

        bodies = {}
        for body in rbd.bodies:
            bDict = {
                'type': 'ridigBody',
                'parent': 'root' if body.parent == UUID(int=0) else uuidToNnstr(body.parent),
                'mass': float(body.mass),
                'centreOfMass': body.centerOfMass.toFloatList(),
                'inertia': [float(i) for i in body.momentOfInertia],
                'transform': ([float(i) for i in body.orientation], body.centerOfRotation.toFloatList()),
                'patches': [BoundaryDB.getBoundaryName(bcid) for bcid in body.boundaries],
                'innerDistance': float(body.deformationOffset),
                'outerDistance': float(body.deformationDistance)
            }

            jDict = self._compactJointDict([self._jointDict(j) for j in body.joints])
            if len(jDict) == 1:
                bDict['joint'] = jDict[0]
            elif len(jDict) > 1:
                bDict['joint'] = {
                    'type': 'composite',
                    'joints': jDict
                }

            bodies[uuidToNnstr(body.uuid)] = bDict

        restraints = {}
        for r in rbd.restraints:
            if r.restraintType == RestraintType.SIMPLE_DAMPER:
                restraints[uuidToNnstr(r.uuid)] = {
                    'type': 'linearDamper',
                    'coeff': float(r.dampingConstant)
                }
            elif r.restraintType == RestraintType.TRANSLATIONAL_SPRING:
                restraints[uuidToNnstr(r.uuid)] = {
                    'type': 'linearSpring',
                    'refAttachmentPt': r.attachmentPoint.toFloatList(),
                    'anchor': r.anchorPoint.toFloatList(),
                    'restLength': float(r.restLength),
                    'stiffness': float(r.springConstant),
                    'damping': float(r.dampingConstant)
                }
            elif r.restraintType == RestraintType.ROTATIONAL_SPRING:
                restraints[uuidToNnstr(r.uuid)] = {
                    'type': 'linearAxialAngularSpring',
                    'axis': r.axis.toFloatList(),
                    'stiffness': float(r.springConstant),
                    'damping': float(r.dampingConstant)
                }

        self._data = {
            'dynamicFvMesh': 'dynamicMotionSolverFvMesh',
            'motionSolverLibs': ['rigidBodyMeshMotion'],
            'motionSolver': 'rigidBodyMotion',
            'rigidBodyMotionCoeffs': {
                'solver': solver,
                'accelerationRelaxation': float(rbd.accelerationRelaxationFactor),
                'accelerationDamping': float(rbd.accelerationDampingFactor),
                'bodies': bodies,
            },
            'restraints': restraints
        }

    def _jointDict(self, joint: Joint) -> dict:
        if joint.jointType == JointType.SPHERICAL:
            return {'type': 'Rs' }

        elif joint.jointType == JointType.PRISMATIC:
            if joint.direction.isXAligned():
                return {'type': 'Px' }
            elif joint.direction.isYAligned():
                return {'type': 'Py' }
            elif joint.direction.isZAligned():
                return {'type': 'Pz' }
            else:
                return {'type': 'Pa',
                        'axis': joint.direction.toFloatList() }

        elif joint.jointType == JointType.REVOLUTE:
            if joint.axis.isXAligned():
                return {'type': 'Rx' }
            elif joint.axis.isYAligned():
                return {'type': 'Ry' }
            elif joint.axis.isZAligned():
                return {'type': 'Rz' }
            else:
                return {'type': 'Ra',
                        'axis': joint.axis.toFloatList() }

        else:
            raise AssertionError

    def _compactJointDict(self, joints):
        result = []
        i = 0
        while i < len(joints):
            if i + 2 < len(joints):
                types = [joints[i + k]['type'] for k in range(3)]
                if set(types) == {'Px', 'Py', 'Pz'}:
                    result.append({'type': 'Pxyz'})
                    i += 3
                    continue
                elif all(t in ('Rx', 'Ry', 'Rz') for t in types) and len(set(types)) == 3:
                    axes = ''.join(t[1] for t in types)
                    result.append({'type': f'R{axes}'})
                    i += 3
                    continue
            result.append(joints[i])
            i += 1
        return result



