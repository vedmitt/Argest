import geopandas as gpd
from PIL import Image
import matplotlib.pyplot as plt

gdf = gpd.read_file('/Users/ronya/Documents/my_modules/num_controls/input/rad_GK30.shp')
print(gdf.shape)
print(gdf.head())
gdf.plot(column='rad')
plt.show()
