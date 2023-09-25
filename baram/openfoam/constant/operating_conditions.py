#!/usr/bin/env python
# -*- coding: utf-8 -*-

from libbaram.openfoam.dictionary.dictionary_file import DictionaryFile

from baram.coredb import coredb
from baram.coredb.general_db import GeneralDB
from baram.openfoam.file_system import FileSystem


class OperatingConditions(DictionaryFile):
    def __init__(self, rname: str):
        super().__init__(FileSystem.caseRoot(), self.constantLocation(rname), 'operatingConditions')

        self._rname = rname

    def build(self):
        if self._data is not None:
            return self

        db = coredb.CoreDB()

        pressure = db.getValue(GeneralDB.OPERATING_CONDITIONS_XPATH + '/pressure')

        self._data = {
            'operatingPressure': ('operatingPressure [1 -1 -2 0 0 0 0]', pressure)
        }

        return self
