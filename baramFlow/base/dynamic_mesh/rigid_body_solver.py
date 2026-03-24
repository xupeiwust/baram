#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import Enum

from baramFlow.coredb.libdb import E, nsmap


class SolverType(Enum):
    NEWMARK         = 'newmark'
    CRANK_NICOLSON  = 'crankNicolson'
    SYMPLECTIC      = 'symplectic'


@dataclass
class RigidBodySolver:
    solverType: SolverType = SolverType.NEWMARK
    velocityIntegrationCoefficient: str = '0.7'
    positionIntegrationCoefficient: str = '1.0'
    offCenteringAccelerationCoefficient: str = '0.5'
    offCenteringVelocityCoefficient: str = '0.5'

    @classmethod
    def fromElement(cls, e):
        solverType = SolverType(e.find('solverType', namespaces=nsmap).text)
        velocityIntegrationCoefficient = e.find('velocityIntegrationCoefficient', namespaces=nsmap).text
        positionIntegrationCoefficient = e.find('positionIntegrationCoefficient', namespaces=nsmap).text
        offCenteringAccelerationCoefficient = e.find('offCenteringAccelerationCoefficient', namespaces=nsmap).text
        offCenteringVelocityCoefficient = e.find('offCenteringVelocityCoefficient', namespaces=nsmap).text

        return RigidBodySolver(
            solverType=solverType,
            velocityIntegrationCoefficient=velocityIntegrationCoefficient,
            positionIntegrationCoefficient=positionIntegrationCoefficient,
            offCenteringAccelerationCoefficient=offCenteringAccelerationCoefficient,
            offCenteringVelocityCoefficient=offCenteringVelocityCoefficient)

    def toElement(self):
        return E('rigidBodySolverType',
                 E('solverType', self.solverType.value),
                 E('velocityIntegrationCoefficient', self.velocityIntegrationCoefficient),
                 E('positionIntegrationCoefficient', self.positionIntegrationCoefficient),
                 E('offCenteringAccelerationCoefficient', self.offCenteringAccelerationCoefficient),
                 E('offCenteringVelocityCoefficient', self.offCenteringVelocityCoefficient))
