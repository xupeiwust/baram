#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass


from baramFlow.coredb.libdb import E, nsmap
from libbaram.pfloat import PFloat


@dataclass
class Vector:
    x: PFloat = PFloat('0')
    y: PFloat = PFloat('0')
    z: PFloat = PFloat('0')

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

    def toList(self):
        return [float(self.x), float(self.y), float(self.z)]

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'