#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from baramFlow.coredb.libdb import E, nsmap
from libbaram.pfloat import PFloat


class SolverType(Enum):
    NEWMARK         = 'newmark'
    CRANK_NICOLSON  = 'crankNicolson'
    SYMPLECTIC      = 'symplectic'


@dataclass
class RigidBodySolver:
    solverType: SolverType = SolverType.NEWMARK
    velocityIntegrationCoefficient: PFloat = PFloat('0.7')
    positionIntegrationCoefficient: PFloat = PFloat('1.0')
    offCenteringAccelerationCoefficient: PFloat = PFloat('0.5')
    offCenteringVelocityCoefficient: PFloat = PFloat('0.5')

    @classmethod
    def fromElement(cls, e):
        solverType = SolverType(e.find('solverType', namespaces=nsmap).text)
        velocityIntegrationCoefficient = PFloat.fromElement(e.find('velocityIntegrationCoefficient', namespaces=nsmap))
        positionIntegrationCoefficient = PFloat.fromElement(e.find('positionIntegrationCoefficient', namespaces=nsmap))
        offCenteringAccelerationCoefficient = PFloat.fromElement(e.find('offCenteringAccelerationCoefficient', namespaces=nsmap))
        offCenteringVelocityCoefficient = PFloat.fromElement(e.find('offCenteringVelocityCoefficient', namespaces=nsmap))

        return RigidBodySolver(
            solverType=solverType,
            velocityIntegrationCoefficient=velocityIntegrationCoefficient,
            positionIntegrationCoefficient=positionIntegrationCoefficient,
            offCenteringAccelerationCoefficient=offCenteringAccelerationCoefficient,
            offCenteringVelocityCoefficient=offCenteringVelocityCoefficient)

    def toElement(self):
        return E('rigidBodySolverType',
                 E('solverType', self.solverType.value),
                 self.velocityIntegrationCoefficient.toElement('velocityIntegrationCoefficient'),
                 self.positionIntegrationCoefficient.toElement('positionIntegrationCoefficient'),
                 self.offCenteringAccelerationCoefficient.toElement('offCenteringAccelerationCoefficient'),
                 self.offCenteringVelocityCoefficient.toElement('offCenteringVelocityCoefficient'))
