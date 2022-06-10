# -*- coding: utf-8 -*-

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load RasterStatClac class from file RasterStatClac.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .ssg_uav_support_plugin import SSG_UAV_support_plugin
    return SSG_UAV_support_plugin(iface)
