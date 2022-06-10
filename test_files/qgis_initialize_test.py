from old_files.dataStorage.FeaturesList import FeaturesList


f = FeaturesList([], None, [], None)
# from qgis.core import *
#
# # Supply path to qgis install location
# QgsApplication.setPrefixPath('/Applications/QGIS-LTR.app/Contents/MacOS', True)
#
# # Create a reference to the QgsApplication.  Setting the
# # fn2 argument to False disables the GUI.
# qgs = QgsApplication([], False)
#
# # Load providers
# qgs.initQgis()
#
# # Write your code here to load some layers, use processing
# # algorithms, etc.
# data_fn = '/Users/ronya/My_Documents/karelia/karelia_results/the_one_control_lines_2.shp'
# input_lyr = QgsVectorLayer(data_fn, '', 'ogr')
# print(input_lyr.isValid())
#
# # When your script is complete, call exitQgis() to remove the provider and
# # input_lyr registries from memory
# qgs.exitQgis()