#!/usr/bin/env python
# -*- coding: utf-8 -*-


from dataclasses import dataclass
from threading import Lock
from typing import TypedDict

from libbaram.async_signal import AsyncSignal


_mutex = Lock()


class RegionComponents(TypedDict):
    cellZones:  dict[str, str]  # {<czname>: <czid>}
    boundaries: dict[str, str]  # {<bcname>: <bcid>}


class EventBus:
    def __new__(cls, *args, **kwargs):
        with _mutex:
            if not hasattr(cls, '_instance'):
                cls._instance = super(EventBus, cls).__new__(cls, *args, **kwargs)

        return cls._instance

    def __init__(self):
        with _mutex:
            if hasattr(self, '_initialized'):
                return
            else:
                self._initialized = True

        self.onMeshLoading = AsyncSignal(dict[str, RegionComponents], dict[str, RegionComponents])
        self.onProjectOpen = AsyncSignal()
        self.onProjectClose = AsyncSignal()
