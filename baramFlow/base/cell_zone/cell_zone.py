#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dataclasses import dataclass

from lxml import etree

from resources import resource

from baramFlow.coredb.libdb import nsmap


CELL_ZONE_ELEMENT_PATH = 'configurations/cell_zone.xml'


@dataclass
class CellZoneData:
    czid: str   = None
    name: str   = None
    rname: str  = None

    def toElement(self):
        with open(resource.file(CELL_ZONE_ELEMENT_PATH), 'rb') as file:
            xml = file.read()

        element = etree.fromstring(xml)
        element.set('czid', self.czid)
        element.find('name', namespaces=nsmap).text = self.name

        return element

    @staticmethod
    def fromElement(e):
        return CellZoneData(
            czid=e.get('czid'),
            name=e.find('name', namespaces=nsmap).text)
