#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from dataclasses import dataclass
from dataclasses import field as dataClassField


from baramFlow.coredb.libdb import E, nsmap
from libbaram.pfloat import PFloat


@dataclass
class Vector:
    x: PFloat
    y: PFloat
    z: PFloat

    @staticmethod
    def zero():
        return Vector(PFloat('0'), PFloat('0'), PFloat('0'))

    @staticmethod
    def xUnit():
        return Vector(PFloat('1'), PFloat('0'), PFloat('0'))

    @staticmethod
    def yUnit():
        return Vector(PFloat('0'), PFloat('1'), PFloat('0'))

    @staticmethod
    def zUnit():
        return Vector(PFloat('0'), PFloat('0'), PFloat('1'))

    @staticmethod
    def fromElement(e):
        return Vector(x=PFloat.fromElement(e.find('x', namespaces=nsmap)),
                      y=PFloat.fromElement(e.find('y', namespaces=nsmap)),
                      z=PFloat.fromElement(e.find('z', namespaces=nsmap)))

    def toElement(self, tag):
        return E(tag,
                    self.x.toElement('x'),
                    self.y.toElement('y'),
                    self.z.toElement('z'))

    def toFloatList(self):
        return [float(self.x), float(self.y), float(self.z)]

    def isXAligned(self):
        return float(self.y) == 0 and float(self.z) == 0

    def isYAligned(self):
        return float(self.x) == 0 and float(self.z) == 0

    def isZAligned(self):
        return float(self.x) == 0 and float(self.y) == 0

    def magnitude(self):
        return math.sqrt(float(self.x) ** 2 + float(self.y) ** 2 + float(self.z) ** 2)

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'