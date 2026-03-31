#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from xml.etree.ElementTree import Element

from baramFlow.app import app
from baramFlow.base.boundary.boundary import PatchInteraction
from baramFlow.base.boundary.boundary_data import BoundaryData
from baramFlow.base.boundary.wall import WallHeatTransfer
from baramFlow.base.region.region_namager import RegionsCache
from baramFlow.coredb.boundary_db import BoundaryDB, BoundaryType
from baramFlow.coredb.coredb import CoreDB
from baramFlow.coredb.coredb_writer import CoreDBWriter
from baramFlow.coredb.libdb import ValueException, dbErrorToMessage, nsmap


@dataclass
class CoupledBoundary:
    bcid: str
    coupledBoundary: str
    bctype: BoundaryType = None

    def applyToDB(self, db):
        xpath = BoundaryDB.getXPath(self.bcid)

        db.setValue(xpath + '/coupledBoundary', self.coupledBoundary)
        if self.bctype is not None:
            db.setValue(xpath + '/physicalType', self.bctype.value)


class BoundaryManager:
    @classmethod
    def updateBoundaryCondition(cls, bcid, condition, writer: CoreDBWriter = None):
        boundary = cls.getBoundary(bcid).boundary

        couplingAffected = None
        if BoundaryDB.needsCoupledBoundary(boundary.bctype):
            couplingAffected = cls.updateCouple(boundary, cls.getBoundary(condition.coupledBoundary).boundary)

        try:
            with CoreDB() as db:
                condition.applyToDB(db, bcid)

                if writer is not None:
                    writer.updateInDB(db)

                if couplingAffected is not None:
                    for a in couplingAffected:
                        a.applyToDB(db)

                db.increaseConfigCount()
        except ValueException as e:
            raise ValueError(dbErrorToMessage(e))
        finally:
            RegionsCache.reloadBoundary(bcid)

            if couplingAffected is not None:
                for a in couplingAffected:
                    RegionsCache.reloadBoundary(a.bcid)

    @staticmethod
    def updateCouple(boundary: BoundaryData, partner: BoundaryData):
        if boundary.coupledBoundary == partner.bcid:
            return None

        affected = [CoupledBoundary(bcid=boundary.bcid,
                                    coupledBoundary=partner.bcid),
                    CoupledBoundary(bcid=partner.bcid,
                                    coupledBoundary=boundary.bcid,
                                    bctype=boundary.bctype if boundary.bctype != partner.bctype else None)]

        if boundary.coupledBoundary != '0':
            affected.append(CoupledBoundary(bcid=boundary.coupledBoundary,
                                            coupledBoundary='0'))
        if partner.coupledBoundary != '0':
            affected.append(CoupledBoundary(bcid=partner.coupledBoundary,
                                            coupledBoundary='0'))

        return affected

    @staticmethod
    def patchInteraction(bcid: str):
        return PatchInteraction.fromElement(CoreDB().getElement(BoundaryDB.getXPath(bcid) + '/patchInteraction'))

    @staticmethod
    def updatePatchInteractionInDB(db, bcid, patchInteraction):
        try:
            p = db.getElement(BoundaryDB.getXPath(bcid))

            new: Element = patchInteraction.toElement()

            for i, child in enumerate(p):
                if child.tag == new.tag:
                    p.remove(child)
                    p.insert(i, new)
                    break
            else:
                assert False

            db.increaseConfigCount()
        except ValueException as e:
            raise ValueError(e)

    @staticmethod
    def updateWallHeatTransferInDB(db, bcid, new: WallHeatTransfer):
        boundary = RegionsCache.getBoundary(bcid).boundary
        boundary.wall.heatTransfer.update(new)

        try:
            wall = db.getElement(BoundaryDB.getXPath(bcid) + '/wall')
            wall.replace(wall.find('heatTransfer', namespaces=nsmap), boundary.wall.heatTransfer.toElement())

            db.increaseConfigCount()
        except ValueException as e:
            raise ValueError(e)

    @staticmethod
    def getBoundary(bcid):
        return RegionsCache.getBoundary(bcid)

    @staticmethod
    def getBoundaries():
        return RegionsCache.getBoundaries()

    @staticmethod
    def getBoundariesIn(rname):
        return RegionsCache.getBoundariesIn(rname)

    @staticmethod
    def getZoneAverageDirectionForFan(bcid, bcidOfCouple):
        boundary = RegionsCache.getBoundary(bcid)
        couple = RegionsCache.getBoundary(bcidOfCouple)

        master = boundary if boundary.startFace < couple.startFace else couple
        if master.zoneAverageDirection is None:
            master.zoneAverageDirection = app.meshModel().actorInfo(int(master.bcid)).getZoneAverageDirection()

        return master.zoneAverageDirection
