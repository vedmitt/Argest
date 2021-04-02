from qgis._core import QgsVectorLayer

vlayer = QgsVectorLayer(r"M:\Sourcetree\input_data\Jarchiha\Jarchiha_all_data.shp", "archiha_all_data", "ogr")
for field in vlayer.fields():
    print(field.name(), field.typeName())

