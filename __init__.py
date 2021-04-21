# -*- coding: utf-8 -*-
"""
/***************************************************************************
 bpla_plugin_flights
                                 A QGIS plugin
 Description
                             -------------------
        copyright            : (C) 2021 by Ronya14
        email                : ronya14@mail.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""

from .bpla_plugin_flights import bpla_plugin_flights
from PyQt5.QtCore import *


def name():
    return "BPLA Plugin Flights"


def description():
    return "this plugin removes irregular points."


def version():
    return "v1.0.0-beta"


def qgisMinimumVersion():
    return "3.0"


def qgisMaximumVersion():
    return "3.18"


def authorName():
    return "Veronika Dmitrieva"


def icon():
    return "icons/icon.png"


def classFactory(iface):
    return bpla_plugin_flights(iface)
