#!/usr/bin/env python
# -*- coding: utf-8 -*-

from baramFlow.base.region.region_namager import RegionsCache


class CacheManager:
    @staticmethod
    def load():
        RegionsCache.load()