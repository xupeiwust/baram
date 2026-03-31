#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4

from pandas import DataFrame

from libbaram.natural_name_uuid import uuidToNnstr

from baramFlow.coredb.project import Project


class FileDataManager:
    _dataFrames: dict[str, DataFrame] = {}

    @classmethod
    def putDataFrame(cls, data: DataFrame):
        id_ = uuid4()
        name = uuidToNnstr(id_)
        Project.instance().fileDB().putDataFrame(name, data)
        cls._dataFrames[name] = data

        return id_