#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from baramFlow.coredb.libdb import nsmap


@dataclass
class Vector:
    x: str
    y: str
    z: str

    @staticmethod
    def fromElement(e):
        return Vector(x=e.find('x', namespaces=nsmap).text,
                      y=e.find('y', namespaces=nsmap).text,
                      z=e.find('z', namespaces=nsmap).text)
