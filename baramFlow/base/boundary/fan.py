#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional

from pandas import DataFrame

from baramFlow.base.file_data_manager import FileDataManager
from baramFlow.coredb.boundary_db import BoundaryDB
from baramFlow.coredb.libdb import boolToXml


@dataclass
class Fan:
    reverseDirection: bool          = False
    fanCurveName: str               = None

    fanCurve: Optional[DataFrame]   = None

    def applyToDB(self, db, bcid):
        if self.fanCurve is not None:
            self.fanCurveName = FileDataManager.putDataFrame(self.fanCurve)

        self.applyCoupleConditionToDB(db, bcid)

    def applyCoupleConditionToDB(self, db, bcid):
        xpath = BoundaryDB.getXPath(bcid)

        db.setValue(xpath + '/fan/reverseDirection', boolToXml(self.reverseDirection))
        if self.fanCurveName:
            db.setValue(xpath + '/fanCurveName', str(self.fanCurveName))
