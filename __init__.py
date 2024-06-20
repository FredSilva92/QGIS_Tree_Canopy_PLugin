# -*- coding: utf-8 -*-
"""
/***************************************************************************
 copasarvores
                                 A QGIS plugin
 teste
                             -------------------
        begin                : 2017-06-16
        copyright            : (C) 2017 by Pedro Silva
        email                : up201007485@fc.up.pt
        git sha              : $Format:%H$
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
    """Load copasarvores class from file copasarvores.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .copas_arvores import copasarvores
    return copasarvores(iface)
