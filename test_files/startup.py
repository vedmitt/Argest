# from qgis.core import *
#
# # Supply path to qgis install location
# QgsApplication.setPrefixPath("/path/to/qgis/installation", True)
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
#
# # Finally, exitQgis() is called to remove the
# # provider and input_lyr registries from memory
# qgs.exitQgis()
import os

if __name__ == "__main__":
    # uri = " /Users/ronya/My_Documents/GIS_develop/DATA/Norilsk/outputGK30_test.shp|layername='outputGK30_test'"
    uri = " /Users/ronya/My_Documents/GIS_develop/DATA/Norilsk/outputGK30_test.shp"

    # print(uri.find('|'))
    fpath = uri
    out_fn, output_ext = os.path.splitext(fpath)
    print(output_ext)
    print(os.path.basename(out_fn))

    # uri1 = "file:///Users/ronya/My_Documents/GIS_develop/DATA/Norilsk/Var_Veronik_ini1AZ9h2My000Var025_nor.txt?type='csv&maxFields=10000&detectTypes=yes&xField=LON&yField=LAT&crs=EPSG:28406&spatialIndex=no&subsetIndex=no&watchFile=no'"
    # params_dict = {}
    # fpath, params = uri1.split('?')
    # fpath = fpath[7:]
    # print(fpath)
    # comp = params.split('&')
    # for item in comp:
    #     name, val = item.split('=')
    #     params_dict.setdefault(name, str(val))
    # print(params_dict)


