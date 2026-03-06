#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from uuid import UUID

import pandas as pd

from baramFlow.coredb.libdb import nsmap
from baramFlow.base.constants import Function1Type
from baramFlow.coredb.libdb import E


UUID_ZERO = UUID('00000000-0000-0000-0000-000000000000')


class BatchableNumber:
    def __init__(self, text: str, default=None):
        self._text = text
        self._default = default

        assert not self.isParameter() or self._default is not None

    @property
    def text(self):
        return self._text

    def isParameter(self):
        return self._text.startswith('$')

    def parameter(self):
        return self._text[1:] if self.isParameter() else None

    def number(self):
        return self._default

    @staticmethod
    def fromElement(e):
        if parameter := e.get('batchParameter'):
            return BatchableNumber('$' + parameter, e.text)

        return BatchableNumber(e.text)

    def toXML(self, name):
        attr = f' batchParameter="{self.parameter()}"' if self.isParameter() else ''
        return f'<{name}{attr}>{self._default if self.isParameter() else self._text}</{name}>'

    def toElement(self, tag: str):
        if self.isParameter():
            return E(tag, self._default, batchParameter=self.parameter())
        else:
            return E(tag, self._text)


@dataclass
class Vector:
    x: BatchableNumber
    y: BatchableNumber
    z: BatchableNumber

    @staticmethod
    def new(x, y, z):
        return Vector(x=BatchableNumber(x), y=BatchableNumber(y), z=BatchableNumber(z))

    @staticmethod
    def fromElement(e):
        return Vector(x=BatchableNumber.fromElement(e.find('x', namespaces=nsmap)),
                      y=BatchableNumber.fromElement(e.find('y', namespaces=nsmap)),
                      z=BatchableNumber.fromElement(e.find('z', namespaces=nsmap)))

    def toXML(self):
        return f"{self.x.toXML('x')}{self.y.toXML('y')}{self.z.toXML('z')}"

    def toElement(self, tag: str):
        return E(tag,
                 self.x.toElement('x'),
                 self.y.toElement('y'),
                 self.z.toElement('z'))


@dataclass
class Function1ScalarRow:
    t: str
    v: str

    @staticmethod
    def fromElement(e):
        return Function1ScalarRow(t=e.find('t', namespaces=nsmap).text,
                                  v=e.find('v', namespaces=nsmap).text)

    def toXML(self):
        return f'<t>{self.t}</t><v>{self.v}</v>'

    def toElement(self, tag: str):
        return E(tag,
                 E('t', self.t),
                 E('v', self.v))


@dataclass
class Function1VectorRow:
    t: str
    x: str
    y: str
    z: str

    @staticmethod
    def fromElement(e):
        return Function1VectorRow(t=e.find('t', namespaces=nsmap).text,
                                  x=e.find('x', namespaces=nsmap).text,
                                  y=e.find('y', namespaces=nsmap).text,
                                  z=e.find('z', namespaces=nsmap).text)

    def toXML(self):
        return f'<t>{self.t}</t><x>{self.x}</x><y>{self.y}</y><z>{self.z}</z>'

    def toElement(self, tag:str):
        return E(tag,
                 E('t', self.t),
                 E('x', self.x),
                 E('y', self.y),
                 E('z', self.z))


@dataclass
class Function1Scalar:
    type: Function1Type = Function1Type.CONSTANT
    constant: BatchableNumber = field(default_factory=lambda: BatchableNumber('100'))
    table: list[Function1ScalarRow] = field(default_factory=list)

    @staticmethod
    def fromElement(e):
        table = []
        if (element := e.find('table', namespaces=nsmap)) is not None:
            for row in element.findall('row', namespaces=nsmap):
                table.append(Function1ScalarRow.fromElement(row))

        return Function1Scalar(type=Function1Type(e.find('type', namespaces=nsmap).text),
                               constant=BatchableNumber.fromElement(e.find('constant', namespaces=nsmap)),
                               table=table)

    def toXML(self):
        rows = ''
        for row in self.table:
            rows += f'<row>{row.toXML()}</row>'

        return f'''
            <type>{self.type.value}</type>
            <constant>{self.constant.text}</constant>
            <table>{rows}</table>
        '''

    def toElement(self, tag: str):
        tableElement = E('table')
        tableElement.extend([row.toElement('row') for row in self.table])
        return E(tag,
                 self.type.toElement('type'),
                 self.constant.toElement('constant'),
                 tableElement)


@dataclass
class Function1Vector:
    type: Function1Type = Function1Type.CONSTANT
    constant: Vector = field(default_factory=lambda: Vector.new('1', '1', '1'))
    table: list[Function1VectorRow] = field(default_factory=lambda: [])

    @staticmethod
    def fromElement(e):
        table = []
        if (element := e.find('table', namespaces=nsmap)) is not None:
            for row in element.findall('row', namespaces=nsmap):
                table.append(Function1VectorRow.fromElement(row))

        return Function1Vector(type=Function1Type(e.find('type', namespaces=nsmap).text),
                               constant=Vector.fromElement(e.find('constant', namespaces=nsmap)),
                               table=table)

    def toXML(self):
        rows = ''
        for row in self.table:
            rows += f'<row>{row.toXML()}</row>'

        return f'''
            <type>{self.type.value}</type>
            <constant>{self.constant.toXML()}</constant>
            <table>{rows}</table>
        '''

    def toElement(self, tag: str):
        tableElement = E('table')
        tableElement.extend([row.toElement('row') for row in self.table])
        return E(tag,
                 self.type.toElement('type'),
                 self.constant.toElement('constant'),
                 tableElement)


class SimpleSheetData:
    columns = None

    def __init__(self, data: list[list[float]]):
        self._data = data

    def data(self):
        return self._data

    def dataFrame(self):
        return pd.DataFrame(self._data)

    def columnDataString(self, index):
        return ' '.join([str(self._data[row][index]) for row in range(len(self._data))])

    def columnDataElement(self, index):
        return E(self.columns[index],
                 self.columnDataString(index))

    @classmethod
    def fromElement(cls, e):
        data = [e.find(c, namespaces=nsmap).text.split() for c in cls.columns]

        return cls(
            [[float(data[column][row]) for column in range(len(data))] for row in range(len(data[0]))])

    def toElement(self, tag: str):
        return E(tag,
                 *[self.columnDataElement(i) for i in range(len(self.columns))])


class TemporalScalarList(SimpleSheetData):
    columns = ['t', 'v']


class TemporalVectorList(SimpleSheetData):
    columns = ['t', 'x', 'y', 'z']


class SpatialScalarList(SimpleSheetData):
    columns = ['x', 'y', 'z', 'v']


class SpatialVectorList(SimpleSheetData):
    columns = ['x', 'y', 'z', 'vx', 'vy', 'vz']


class TrackedData:
    def __init__(self, init=None):
        self._initData = init
        self._data = init

    def data(self):
        return self._data

    def setData(self, data):
        self._data = data

    def isModified(self):
        return self._initData != self._data

    def isNone(self):
        return self._data is None
