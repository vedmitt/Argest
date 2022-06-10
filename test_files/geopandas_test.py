import os
import pandas as pd
import geopandas as gpd
from PIL import Image
import matplotlib.pyplot as plt

dir_path = '/Users/ronya/Docs/GIS/TESTDATA'

# input_fname = 'input/NorilskGK30_variated_shp.shp'
input_fname = 'output/NorilskGK30_variated_num.shp'

gdf = gpd.read_file(os.path.join(dir_path, input_fname))

gdf = gdf.crs()
gdf = gdf.copy()

f = [0, 1, 1, 2, 3, 4, 2]
print(f.index(2))

# gdf['buffered'] = gdf.buffer(10)

# diss = gdf[['id', 'TIME', 'Profile', 'geometry']].dissolve(by='Profile', as_index=False, aggfunc="first")
# print(type(diss.geometry))
# print(diss.head())
# # schema = {
# #     'geometry': 'Point',
# #     'properties': [
# #         ('id', 'int'),
# #         ('TIME', 'str'),
# #         ('Profile', 'int')
# #     ]
# # }
# diss.to_file(os.path.join(dir_path, 'output/NorilskGK30_dissolved.shp'), index=False, driver="ESRI Shapefile")
#
# g = gpd.GeoDataFrame()