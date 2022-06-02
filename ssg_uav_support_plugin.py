# -*- coding: utf-8 -*-

import os
import sys
import inspect
from qgis.PyQt.QtCore import Qt, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsApplication
from qgis import processing
from .ssg_uav_support_provider import SSG_UAV_Provider

cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]

if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)


class SSG_UAV_support_plugin(object):

    def __init__(self, iface):
        self.iface = iface
        self.menu = self.tr(u'SSG UAV Support')
        self.provider = None
        self.toolbar = self.iface.addToolBar(u'SSG UAV Support')
        self.toolbar.setObjectName(u'SSG_UAV_Support')
        self.actions = []

    def initProcessing(self):
        self.provider = SSG_UAV_Provider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MPMWorkflow', message)

    def add_action(self, icon_path, text, callback, enabled_flag=True, add_to_menu=True, add_to_toolbar=False,
                   status_tip=None, whats_this=None, parent=None):
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:          action.setStatusTip(status_tip)
        if whats_this is not None:          action.setWhatsThis(whats_this)
        if add_to_toolbar and self.toolbar: self.toolbar.addAction(action)
        if add_to_menu and self.menu:       self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        self.initProcessing()
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "load_var.png"),
            self.tr(u'Загрузка данных вариаций'),
            self.do_load_var,
            add_to_toolbar=True,
            whats_this=self.tr(u'Загрузка данных вариаций из файлов формата POS и MiniMag'),
            status_tip=self.tr(u'Загрузка данных вариаций из файлов формата POS и MiniMag'),
            parent=self.iface.mainWindow()
        )
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "load_data.png"),
            self.tr(u'Загрузка данных магнитной съёмки'),
            self.do_load_data,
            add_to_toolbar=True,
            whats_this=self.tr(u'Загрузка данных магнитной съёмки БПЛА'),
            status_tip=self.tr(u'Загрузка данных магнитной съёмки БПЛА'),
            parent=self.iface.mainWindow()
        )
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "calc_var.png"),
            self.tr(u'Учет вариаций'),
            self.do_calc_var,
            add_to_toolbar=True,
            whats_this=self.tr(u'Учет вариаций магнитной съемки'),
            status_tip=self.tr(u'Учет вариаций магнитной съемки'),
            parent=self.iface.mainWindow()
        )
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "shave_data.png"),
            self.tr(u'Обрезка долетов'),
            self.do_shave_data,
            add_to_toolbar=True,
            whats_this=self.tr(u'Обрезка долетов магнитосъемки'),
            status_tip=self.tr(u'Обрезка долетов магнитосъемки'),
            parent=self.iface.mainWindow()
        )
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "num_profile.png"),
            self.tr(u'Нумерация профилей'),
            self.do_num_profiles,
            add_to_toolbar=True,
            whats_this=self.tr(u'Нумерация профилей'),
            status_tip=self.tr(u'Нумерация профилей'),
            parent=self.iface.mainWindow()
        )
        self.add_action(
            os.path.join(os.path.dirname(__file__), "icons", "extract_controls.png"),
            self.tr(u'Выделение контролей'),
            self.do_extracting_controls,
            add_to_toolbar=True,
            whats_this=self.tr(u'Выделение контролей магнитосъемки'),
            status_tip=self.tr(u'Выделение контролей магнитосъемки'),
            parent=self.iface.mainWindow()
        )

    def unload(self):
        if self.provider:
            try:
                QgsApplication.processingRegistry().removeProvider(self.provider)
            except:
                pass
        for action in self.actions:
            self.iface.removePluginMenu(self.menu, action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar

    def do_load_var(self):
        processing.execAlgorithmDialog("ssg_uav:load_variations", {})

    def do_load_data(self):
        processing.execAlgorithmDialog("ssg_uav:load_data", {})

    def do_calc_var(self):
        processing.execAlgorithmDialog("ssg_uav:calc_variations", {})

    def do_shave_data(self):
        processing.execAlgorithmDialog("ssg_uav:shaving_data", {})

    def do_num_profiles(self):
        processing.execAlgorithmDialog("ssg_uav:numerate_profiles", {})

    def do_extracting_controls(self):
        processing.execAlgorithmDialog("ssg_uav:extracting_controls", {})
