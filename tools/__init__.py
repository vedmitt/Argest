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


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load bpla_plugin_flights class from file bpla_plugin_flights.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .numit_plugin import numit_plugin
    return numit_plugin(iface)
