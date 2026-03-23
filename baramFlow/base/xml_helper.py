#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from baramFlow.coredb.libdb import E, nsmap


@dataclass
class Vector:
    x: str = '0'
    y: str = '0'
    z: str = '0'

    @staticmethod
    def fromElement(e):
        return Vector(x=e.find('x', namespaces=nsmap).text,
                      y=e.find('y', namespaces=nsmap).text,
                      z=e.find('z', namespaces=nsmap).text)

    def toElement(self, tag):
        return E(tag,
                    E('x', self.x),
                    E('y', self.y),
                    E('z', self.z))

    def __str__(self):
        return f'({self.x}, {self.y}, {self.z})'
