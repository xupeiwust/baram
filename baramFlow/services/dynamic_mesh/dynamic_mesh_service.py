#!/usr/bin/env python
# -*- coding: utf-8 -*-

from threading import Lock

from bidict import bidict

from baramFlow.base.dynamic_mesh.dynamic_mesh import DYNAMIC_MESH_PATH, DynamicMesh, MotionType
from baramFlow.base.dynamic_mesh.moving_boundary import MovingBoundaryEntry, PointMotionType
from baramFlow.base.event_bus import EventBus, RegionComponents
from baramFlow.coredb import coredb

from baramFlow.coredb.boundary_db import BoundaryDB, BoundaryType


_mutex = Lock()


_CONSTRAINT_BOUNDARY_TYPE_MAP = {
    BoundaryType.SYMMETRY: PointMotionType.SYMMETRY,
    BoundaryType.EMPTY:    PointMotionType.EMPTY,
    BoundaryType.WEDGE:    PointMotionType.WEDGE,
    BoundaryType.CYCLIC:   PointMotionType.CYCLIC
}

class DynamicMeshService:
    GRAPHICS_PATH = '/graphics'

    def __new__(cls, *args, **kwargs):
        with _mutex:
            if not hasattr(cls, '_instance'):
                cls._instance = super(DynamicMeshService, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        with _mutex:
            if hasattr(self, '_initialized'):
                return
            else:
                self._initialized = True

        EventBus().onMeshLoading.asyncConnect(self._handleMeshUpdate)
        EventBus().onProjectOpen.asyncConnect(self._handleProjectOpen)
        EventBus().onProjectClose.asyncConnect(self._handleProjectClose)
        EventBus().onBoundaryTypeChange.asyncConnect(self._handleBoundaryTypeChange)

        EventBus().onSaving.connect(self._handleSave)

        self._dynamicMesh = DynamicMesh()

    def getDynamicMesh(self):
        return self._dynamicMesh

    async def load(self):
        db = coredb.CoreDB()
        self._dynamicMesh = DynamicMesh.fromElement(db.getElement(DYNAMIC_MESH_PATH))
        # ToDo: For compatibility. Remove this code block after 20271231
        # Add boundaries to moving boundary list
        # Begin
        if len(self._dynamicMesh.movingBoundaries) == 0:
            rnames = db.getRegions()

            if len(rnames) == 1:  # Dynamic Mesh does not support multi-region
                movingBoundaries: list[MovingBoundaryEntry] = []

                for bcid, bcname, typeStr in db.getBoundaryConditions(rnames[0]):
                    mb = MovingBoundaryEntry(boundary=str(bcid))

                    bctype = BoundaryType(typeStr)
                    if bctype == BoundaryType.SYMMETRY:
                        mb.pointMotionType = PointMotionType.SYMMETRY
                    elif bctype == BoundaryType.EMPTY:
                        mb.pointMotionType = PointMotionType.EMPTY
                    elif bctype == BoundaryType.WEDGE:
                        mb.pointMotionType = PointMotionType.WEDGE
                    elif bctype == BoundaryType.CYCLIC:
                        mb.pointMotionType = PointMotionType.CYCLIC

                    movingBoundaries.append(mb)

                self._dynamicMesh.movingBoundaries = movingBoundaries

        # End

    def saveToCoreDB(self):
        coredb.CoreDB().replaceElement(DYNAMIC_MESH_PATH, self._dynamicMesh.toElement('dynamicMesh'))

    async def _handleProjectOpen(self):
        await self.load()

    async def _handleProjectClose(self):
        self._dynamicMesh = DynamicMesh()

    async def _handleMeshUpdate(self,
                                oldMesh: dict[str, RegionComponents],
                                newMesh: dict[str, RegionComponents]):

        # 1. dynamic mesh does not support multi-region
        # 2. no update if it is the first time to load mesh
        if len(newMesh) > 1 or len(oldMesh) == 0:
            self._dynamicMesh = DynamicMesh()
            return

        oldDefaultRegion = list(oldMesh.values())[0]
        newDefaultRegion = list(newMesh.values())[0]

        oldBoundaries = bidict(oldDefaultRegion['boundaries'])
        newBoundaries = bidict(newDefaultRegion['boundaries'])

        oldCellZones  = bidict(oldDefaultRegion['cellZones'])
        newCellZones  = bidict(newDefaultRegion['cellZones'])

        for md in self._dynamicMesh.motionDefinitions:
            md.processMeshUpdate(oldCellZones, newCellZones)

        newMovingBoundaries: list[MovingBoundaryEntry] = []
        for bcname, bcid in newBoundaries.items():
            if bcname in oldBoundaries:
                mb = next(mb for mb in self._dynamicMesh.movingBoundaries if mb.boundary == oldBoundaries[bcname])
            else:
                mb = MovingBoundaryEntry(boundary=bcid)

            newMovingBoundaries.append(mb)

        for mb in newMovingBoundaries:
            bctype = BoundaryDB.getBoundaryType(mb.boundary)
            if bctype in _CONSTRAINT_BOUNDARY_TYPE_MAP:
                mb.pointMotionType = _CONSTRAINT_BOUNDARY_TYPE_MAP[bctype]

        self._dynamicMesh.movingBoundaries = newMovingBoundaries

        for body in self._dynamicMesh.rigidBodyDynamics.bodies:
            body.processMeshUpdate(oldBoundaries, newBoundaries)

    async def _handleBoundaryTypeChange(self, bcid: str, oldType: BoundaryType, newType: BoundaryType):
        boundaryEntry = next((be for be in self._dynamicMesh.movingBoundaries if be.boundary == bcid), None)
        if boundaryEntry is None:
            raise AssertionError

        if newType in _CONSTRAINT_BOUNDARY_TYPE_MAP:
            boundaryEntry.pointMotionType = _CONSTRAINT_BOUNDARY_TYPE_MAP[newType]

    def _handleSave(self):
        self.saveToCoreDB()


# Auto-instantiate the singleton so that event bus connections are established at import time
_instance = DynamicMeshService()
