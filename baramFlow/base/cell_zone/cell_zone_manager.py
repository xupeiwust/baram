#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baramFlow.services.region.region_service import RegionService


class CellZoneManager:
    @staticmethod
    def getCellZone(czid: str):
        return RegionService.getCellZone(czid)

    @staticmethod
    def getCellZones():
        return RegionService.getCellZones()
