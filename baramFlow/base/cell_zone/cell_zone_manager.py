#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baramFlow.base.region.region_namager import RegionManager


class CellZoneManager:
    @staticmethod
    def getCellZone(czid: str):
        return RegionManager.getCellZone(czid)

    @staticmethod
    def getCellZones():
        return RegionManager.getCellZones()
