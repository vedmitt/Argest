import os
from qgis.core import edit
from qgis.utils import iface

from PyQt5.QtCore import QVariant
from qgis._core import QgsProject, QgsVectorLayer

from .dataStorage.FileManager import FileManager


class ControlsExtractTool:
    def __init__(self, guiUtil, isToBeParsed, lyrName, outDir):
        self.guiUtil = guiUtil
        self.layerName = lyrName
        self.layer = QgsProject.instance().mapLayersByName(lyrName)[0]
        self.isToBeParsed = isToBeParsed

        self.fnames = ['Buffered',
                       'Dissolved',
                       'intersection',
                       'Joins',
                       'Controls',
                       'Control_pairs_1',
                       'Control_pairs'
                       ]
        self.outDir = outDir
        self.bufferFn = os.path.join(outDir, self.fnames[0] + '.shp')
        self.dissoveFn = os.path.join(outDir, self.fnames[1] + '.shp')
        self.intersectFn = os.path.join(outDir, self.fnames[2] + '.shp')
        self.joinFn = os.path.join(outDir, self.fnames[3] + '.shp')
        self.controlFn = os.path.join(outDir, self.fnames[4] + '.shp')
        self.resultFn1 = os.path.join(outDir, self.fnames[5] + '.shp')
        self.resultFn = os.path.join(outDir, self.fnames[6] + '.shp')

    def makeBuffer(self):
        FileManager().makeBufferOperation(self.layer, self.bufferFn)
        iface.addVectorLayer(self.bufferFn, '', 'ogr')

    def makeDissolved(self):
        lg = FileManager()
        lg.makeDissolveOperation(self.bufferFn, self.dissoveFn)
        lg.createFieldByExpression(self.dissoveFn, 'area', QVariant.Double, '$area')
        iface.addVectorLayer(self.dissoveFn, '', 'ogr')

    def makeIntersection(self):
        lg = FileManager()
        vlayer = lg.createVirtualLayerByQuery("?query=SELECT st_intersection(a.geometry, b.geometry) as geometry, a.FLIGHT_NUM as flight1, b.FLIGHT_NUM as flight2, a.GLOBAL_NUM as glob1, b.GLOBAL_NUM as glob2, a.TIME as time1, b.TIME as time2 \
                            FROM Dissolved a JOIN Dissolved b ON ( \
                                (a.global_num < b.global_num)and \
                                (a.geometry is NOT NULL)and \
                                (b.geometry is NOT NULL)and \
                                (st_intersects(a.geometry, b.geometry)) \
                            )  \
                            ", "intersection")

        lg.createLayerByWriter(vlayer.fields(), vlayer.getFeatures(), vlayer.sourceCrs(), self.intersectFn)
        lg.createFieldByExpression(self.intersectFn, 'area', QVariant.Double, '$area')
        iface.addVectorLayer(self.intersectFn, '', 'ogr')

    def makeJoin(self):
        lg = FileManager()
        csv = QgsVectorLayer(self.dissoveFn, 'Dissolved', 'ogr')
        shp = QgsVectorLayer(self.intersectFn, 'intersection', 'ogr')
        shpField = 'flight1'  # intersection
        csvField = 'FLIGHT_NUM'  # dissolved
        lg.makeJoinOperation(csv, shp, csvField, shpField, self.joinFn)

        # после объединения полей, остается много ненужных
        joinLyr = QgsVectorLayer(self.joinFn, 'Joins', 'ogr')
        disFields = csv.fields().names()
        interFields = shp.fields().names()
        joinFields = joinLyr.fields().names()

        # поэтому сначала удалим пустые поля в конце
        start = len(interFields) - len(disFields) + 1
        i = start
        indexesToRemove = []
        namesToRename = []
        while i < len(joinFields):
            if i >= start + len(disFields) - 1:
                indexesToRemove.append(i)
                namesToRename.append(joinFields[i])
            i += 1
        # print(joinFields[len(interFields):])
        namesToRename.remove(csvField)
        # self.guiUtil.setOutputStyle([0, '\n' + str(namesToRename)])
        lg.removeFields(joinLyr, indexesToRemove)

        # а затем переименуем оставшиеся
        joinLyr = QgsVectorLayer(self.joinFn, 'Joins', 'ogr')
        joinFields = joinLyr.fields().names()
        i = start
        j = 0
        with edit(joinLyr):
            while i < len(joinFields):
                if i >= start:
                    # self.guiUtil.setOutputStyle([0, str(joinFields[i])])
                    idx = joinLyr.fields().indexFromName(joinFields[i])
                    joinLyr.renameAttribute(idx, namesToRename[j])
                    j += 1
                i += 1

        # Вычислим разность площадей
        lg.createFieldByExpression(self.joinFn, 'area_diff', QVariant.Double, '"area" / "area_2"')
        iface.addVectorLayer(self.joinFn, '', 'ogr')

    def makeControlScheme(self):
        lg = FileManager()
        joinLyr = QgsVectorLayer(self.joinFn, 'Joins', 'ogr')
        expression = "if ( area_diff > 0.5, if ( time1 > time2, flight1, flight2), '')"
        fields, feats = lg.selectByExpression(joinLyr, expression)
        lg.createLayerByWriter(fields, feats, joinLyr.sourceCrs(), self.controlFn)
        lg.createFieldByExpression(self.controlFn, 'FLIGHT_NUM', QVariant.Int, expression)
        iface.addVectorLayer(self.controlFn, '', 'ogr')

    def makeControlPairs(self):
        lg = FileManager()
        layer_1 = self.layer
        layer_2 = QgsVectorLayer(self.controlFn, 'Controls', 'ogr')

        # сделаем intersection и выделим пары рядовых и контрольных профилей
        lyr = QgsVectorLayer(self.dissoveFn, 'Dissolved', 'ogr')
        in_fields = lyr.fields().names()
        in_fields.remove('area')

        lg.intersectionOperation(layer_1, layer_2, self.resultFn1, in_fields, ['FLIGHT_NUM'])

        # Приведем тип Multipoint в Point
        lg.multipartToSingleparts(self.resultFn1, self.resultFn)

        iface.addVectorLayer(self.resultFn, '', 'ogr')
        self.guiUtil.setOutputStyle([1, '\nКонтрольные профиля успешно найдены!'])

    def makeParseControlPairs(self):
        lg = FileManager()
        resLyr = QgsVectorLayer(self.resultFn, 'Control_pairs', 'ogr')
        controlField = "FLIGHT_N_1"
        fields, feats = lg.selectByExpression(resLyr, controlField)

        controlNums = []
        for f in feats:
            controlNums.append(f[controlField])
        feats = set(controlNums)
        controlNums = list(feats)
        # self.guiUtil.setOutputStyle([0, '\n' + str(controlNums)])
        self.outDir = os.path.join(self.outDir, 'controls')
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)

        for num in controlNums:
            fname = 'control_' + str(num) + '.shp'
            fpath = os.path.join(self.outDir, fname)
            expression = '"FLIGHT_N_1" = ' + str(num)  # найти контрольные профиля
            fields, feats = lg.selectByExpression(resLyr, expression)

            # найти рядовые профиля
            ordinary_nums = []
            for f in feats:
                if f['FLIGHT_NUM'] != num:
                    ordinary_nums.append(f['FLIGHT_NUM'])

            found_nums = list(set(ordinary_nums))
            if len(found_nums) > 1:
                most_common = max(ordinary_nums, key=ordinary_nums.count)  # рядовой профиль
            else:
                most_common = found_nums[0]

            self.guiUtil.setOutputStyle([0, '\nРядовой №' + str(most_common) + ', контрольный №' + str(num)])
            # найти контрольные профиля и рядовые профиля
            expression = '"FLIGHT_N_1" = ' + str(num) + ' and ("FLIGHT_NUM" = ' + str(
                num) + ' or "FLIGHT_NUM" = ' + str(most_common) + ')'
            fields, feats = lg.selectByExpression(resLyr, expression)
            lg.createLayerByWriter(fields, feats, resLyr.sourceCrs(), fpath, 'point')
            iface.addVectorLayer(fpath, '', 'ogr')

        self.guiUtil.setOutputStyle([1, '\nКонтрольные профиля успешно разделены!'])

    def deleteFilesFromLegend(self):
        lg = FileManager()
        i = 0
        while i < len(self.fnames) - 1:
            lg.removeLyrFromLegend(self.fnames[i])
            lg.removeShapeFile(self.outDir, self.fnames[i])
            i += 1

    def main_controlFlightsExtract(self):
        """
        Алгоритм выделения контролей
        """
        self.makeBuffer()  # Построим буфер вокруг каждой точки
        self.makeDissolved()  # Сделаем Dissolved
        self.makeIntersection()  # Сделаем Intersection
        self.makeJoin()  # Объединим файлы с помощью join
        self.makeControlScheme()  # Выделим и сохраним точки по запросу

        # После того как контрольные профиля были найдены, вернемся к исходному слою и выделим точки
        self.makeControlPairs()

        # удалим вспомогательные слои из легенды и файлы из папки
        self.deleteFilesFromLegend()

        # Когда все пары профилей рядовых и контрольных вместе, разделим их на отдельные пары
        if self.isToBeParsed:
            self.makeParseControlPairs()
