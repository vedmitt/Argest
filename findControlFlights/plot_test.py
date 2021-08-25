# import os
# import sys
# import numpy as np
# from matplotlib.figure import Figure
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from PyQt5.QtWidgets import QApplication, QWidget
#
#
# class Canvas(FigureCanvas):
#     def __init__(self, parent):
#         fig, self.ax = plt.subplots(figsize=(5, 4), dpi=200)
#         super().__init__(fig)
#         self.setParent(parent)
#
#         t = np.arange(0.0, 2.0, 0.01)
#         s = 1 + np.sin(2 * np.pi * t)
#
#         self.ax.plot(t, s)
#
#         self.ax.set(xlabel='time (s)', ylabel='voltage (mV)', title='plot title')
#         self.ax.grid()
#
#
# class AppDemo(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.resize(1600, 800)
#         chart = Canvas(self)
#
#
# def runPlot():
#     # # os.environ['DYLD_LIBRARY_PATH'] = '/Applications/QGIS-LTR.app/Contents/MacOS/lib'
#     # # os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/Applications/QGIS-LTR.app/Contents/PlugIns'
#     # app = QApplication(sys.argv)
#     # demo = AppDemo()
#     # demo.show()
#     # sys.exit(app.exec_())
#     # # pass
# #
# runPlot()

# from pylab import figure, axes, pie, title, show
#
# # Make a square figure and axes
# figure(1, figsize=(6, 6))
# ax = axes([0.1, 0.1, 0.8, 0.8])
#
# labels = 'Frogs', 'Hogs', 'Dogs', 'Logs'
# fracs = [15, 30, 45, 10]
#
# explode = (0, 0.05, 0, 0)
# pie(fracs, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True)
# title('Raining Hogs and Dogs', bbox={'facecolor': '0.8', 'pad': 5})
#
# # plt.savefig('foo.png')
# show()  # Actually, don't show, just save to foo.png

# # import the plugins
# from qgis._core import QgsVectorLayer
# from qgis.utils import plugins, iface
#
# # create the VectorLayer object from with iface
# vl = QgsVectorLayer(r'/Users/ronya/My_Documents/Darhan/controls/plots/control_589/control_589_plot_Tk.shp')
#
# # create the instace of the DataPlotly plugin
# my = plugins['DataPlotly']
#
# # initialize and empty dictionary
# dq = {}
#
# # create nested dictionaries for plot and layour properties
# dq['plot_prop'] = {}
# dq['layout_prop'] = {}
#
# # start to fill the dictionary with values you want
#
# # plot type
# dq['plot_type'] = 'scatter'
# # QgsVectorLayer object
# dq["layer"] = vl
# # choose the plot properties
# dq['plot_prop']['x'] = [i["O2"] for i in vl.getFeatures()]
# dq['plot_prop']['y'] = [i["EC"] for i in vl.getFeatures()]
# dq['plot_prop']['marker'] = 'markers'
# dq['plot_prop']['x_name'] = 'O2'
# dq['plot_prop']['y_name'] = 'EC'
#
# # choose the layout properties
# dq['layout_prop']['legend'] = True
# dq['layout_prop']["range_slider"] = {}
# dq['layout_prop']["range_slider"]["visible"] = False
#
# # call the method that opens the dialog
# my.loadPlot(dq)
