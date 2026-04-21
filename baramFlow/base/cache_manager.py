#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baramFlow.base.region.region_namager import RegionManager


class CacheManager:
    @staticmethod
    def load():
        RegionManager.load()