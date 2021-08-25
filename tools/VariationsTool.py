import os
from datetime import datetime
from statistics import median

import numpy as np

from .dataStorage.ExcelFileManager import ExcelFileManager
from .dataStorage.FileWriterUtil import FileWriterUtil
from .dataStorage.NDArrayManager import NDArrayManager
from .dataStorage.VarFileParser import VarFileParser
from .mathUtil.DataTimeUtil import DataTimeUtil
from .mathUtil.InterpolationMathUtil import InterpolationMathUtil

# from dataStorage.ExcelFileManager import ExcelFileManager
# from dataStorage.FileWriterUtil import FileWriterUtil
# from dataStorage.NDArrayManager import NDArrayManager
# from dataStorage.VarFileParser import VarFileParser
# from mathUtil.DataTimeUtil import DataTimeUtil
# from mathUtil.InterpolationMathUtil import InterpolationMathUtil


class VariationsTool:
    def __init__(self):
        self.tmi = 3  # индекс столбца времени магнитки
        self.tvi = 3  # индекс столбца времени вариаций (если столбца два, то первого из них)
        self.Tmi = 0  # индекс столбца физ данных магнитки
        self.Tvi = 0  # индекс столбца физ дфнных вариаций
        # self.mDTformat = '%d.%m.%YT%H:%M:%S,%f'
        # self.vDTformat = '%m-%d-%YT%H:%M:%S,%f'
        self.fexts = ['.txt']

    def getMagnDataFromFpathsAsNDArray(self, fpaths):
        nd = NDArrayManager()
        mkeys, mdata = self.getHeadAndBodyFromTXT(fpaths[0])
        i = 1
        while i < len(fpaths):
            head, body = self.getHeadAndBodyFromTXT(fpaths[i])
            mdata = nd.appendToNDArray(mdata, body, 0)
            i += 1
        return mkeys, mdata

    def getVarDataFromFpathsAsNDArray(self, fpaths):
        nd = NDArrayManager()
        metadata, vkeys, vdata = self.getHeadAndBodyFromVarFile(fpaths[0])
        i = 1
        while i < len(fpaths):
            metadata, head, body = self.getHeadAndBodyFromVarFile(fpaths[i])
            vdata = nd.appendToNDArray(vdata, body, 0)
            i += 1
        return metadata, vkeys, vdata

    def getHeadAndBodyFromTXT(self, fpath):
        nd = NDArrayManager()
        arr = np.genfromtxt(fpath, dtype=str)  # <class 'numpy.ndarray'>
        keys, data = nd.getHeadAndBodyFromNDArray(arr)
        return keys, data

    def getHeadAndBodyFromVarFile(self, var_path):
        return VarFileParser().parse_file(var_path)

    def getTimeAsNumber(self, tmi, mdata, tvi, vdata):
        dt = DataTimeUtil()

        # магнитка извлечение времени и приведение к числу
        mdt_str = [row[tmi] for row in mdata]
        mdt_obj = [dt.getDate(row) for row in mdt_str]
        mcomp = [[a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond] for a in mdt_obj]

        # вариации извлечение времени и приведение к числу
        vdt_str = [row[tvi] + 'T' + row[tvi + 1] for row in vdata]
        vdt_obj = [dt.getDate(row) for row in vdt_str]
        vcomp = [[a.year, a.month, a.day, a.hour, a.minute, a.second, a.microsecond] for a in vdt_obj]

        mcomp, vcomp = self.getRightDayMonth(mcomp, vcomp)

        tms = [dt.unix_time_millis(datetime(row[0], row[1], row[2], row[3], row[4], row[5], row[6])) for row in mcomp]
        tvs = [dt.unix_time_millis(datetime(row[0], row[1], row[2], row[3], row[4], row[5], row[6])) for row in vcomp]

        # print(max(tms), mdt_str[tms.index(max(tms))], mdt_obj[tms.index(max(tms))].month, mdt_obj[tms.index(max(tms))].day)
        # print(max(tvs), vdt_str[tvs.index(max(tvs))], vdt_obj[tvs.index(max(tvs))].month, vdt_obj[tvs.index(max(tvs))].day)
        # return [], []
        return tms, tvs

    def getRightDayMonth(self, mcomp, vcomp):
        nd = NDArrayManager()

        mmonths = nd.getVectorOfData(mcomp, 1)
        vmonths = nd.getVectorOfData(vcomp, 1)
        month = set(vmonths).intersection(set(mmonths))

        mcomp = self.exchangeItemsPositionInData(mcomp, month)
        vcomp = self.exchangeItemsPositionInData(vcomp, month)

        # mdays = nd.getVectorOfData(mcomp, 0)
        # vdays = nd.getVectorOfData(vcomp, 0)
        # mmonths = nd.getVectorOfData(mcomp, 1)
        # vmonths = nd.getVectorOfData(vcomp, 1)
        # print(set(mmonths))
        # print(set(vmonths))
        # print(set(mdays).intersection(set(vdays)))

        return mcomp, vcomp

    def exchangeItemsPositionInData(self, data, month):
        for row in data:
            if row[1] not in month:
                a = row[2]
                row[2] = row[1]
                row[1] = a
        return data

    def getTValuesFromData(self, Tmi, mdata, Tvi, vdata):
        nd = NDArrayManager()
        Tm = nd.getVectorOfData(mdata, Tmi)
        Tv = nd.getVectorOfData(vdata, Tvi)

        Tm = [float(t) for t in Tm]
        Tv = [int(t) / 1000 for t in Tv]
        return Tm, Tv

    def saveDataToExcelWithPlot(self, data, sheetname, outpath):
        x1 = data[0]
        y1 = data[1]
        y2 = data[2]

        xindexes = [2, 1, len(x1) + 2]
        yindexes = [2, 2, len(y2) + 2, 3]
        data = [
            [[1, 1], 'X'],
            [[1, 2], 'Y'],
            [xindexes, x1],
            [yindexes, y2]
        ]
        wb = ExcelFileManager(outpath, True)
        wb.createSheetWithData(sheetname, data)

        # Построим график
        params = {
            'chart_title': 'title',
            'scatterStyle': 'marker',
            'marker_type': 'dot',
            'x_axis.title': 'X',
            'y_axis.title': 'Y',
            'x_val.indexes': xindexes,  # minCol, minRow, maxRow
            'y_val.indexes': yindexes,  # minCol, maxCol, minRow, maxRow
            'chart_place': "D10"
        }
        wb.createScatterChart(params)

    def calcVarAlgorithm(self, tms, tvs, Tv):
        # Скорость выполнения = 0.01017586299985851
        tp = InterpolationMathUtil()
        i = 0
        s = 0
        mi1 = mi2 = 0
        Tmx = []
        while i < len(tms):
            j = s
            while j < len(tvs):
                # print(tms[i], tvs[j])
                if tvs[j] >= tms[i]:
                    mi1 = j - 1
                    mi2 = j
                    s = mi1
                    # print(tvs[mi1], tms[i], tvs[mi2])
                    break
                j += 1
            Tx = tp.interpolatePoint(tms[i], tvs[mi1], Tv[mi1], tvs[mi2], Tv[mi2])
            Tmx.append(Tx)
            i += 1
        return Tmx

    def main_calcVariations(self, var_dpath, magn_dpath, out_fpath):
        fw = FileWriterUtil()
        nd = NDArrayManager()

        # выполним чтение из всех исходных файлов магнитки и вариации
        var_paths = fw.getFilePathsFromDir(var_dpath, self.fexts)
        magn_paths = fw.getFilePathsFromDir(magn_dpath, self.fexts)

        # объединим все файлы в два больших массива
        mkeys, mdata = self.getMagnDataFromFpathsAsNDArray(magn_paths)
        metadata, vkeys, vdata = self.getVarDataFromFpathsAsNDArray(var_paths)

        # рассчитаем время в секундах и запишем значение в отдельный массив
        tms, tvs = self.getTimeAsNumber(self.tmi, mdata, self.tvi, vdata)
        # print(min(tms), max(tvs))

        # выделим массивы значений Т
        Tm, Tv = self.getTValuesFromData(self.Tmi, mdata, self.Tvi, vdata)
        mediana_Tm = median(Tm)  # медиана списка значений поля магнитки
        # print(min(Tm), mediana_Tm, max(Tm))
        # print(min(Tv), max(Tv))

        # Непосредственно алгоритм поиска значений времени и подсчета вариаций
        Tmx = self.calcVarAlgorithm(tms, tvs, Tv)

        # Вычислим разницу между интерполироанным значением T и исходным
        Tmd = [Tm[i] - Tmx[i] for i in range(len(Tm))]

        # Суммируем полученную разницу с медианой поля магнитки
        Tmr = [Tmd[i] + mediana_Tm for i in range(len(Tmd))]

        # запишем данные снова в файл
        new_fnames = ['TimeMilli', 'Field_Var', 'Diff_Var', 'F_Var']
        new_data = [tms, Tmx, Tmd, Tmr]
        mkeys, mdata = nd.appendColumnsWithHeader(mkeys, mdata, new_fnames, new_data)

        # # Сохраним данные в таблицу Excel и построим график
        # self.saveDataToExcelWithPlot([tms, Tm, Tmr], 'sheet1', r'/Users/ronya/My_Documents/Karelia/test_1.xlsx')

        return FileWriterUtil().writeTXTwithHeader(out_fpath, mkeys, mdata)


# if __name__ == '__main__':
#     # vpath = r'/Users/ronya/My_Documents/Karelia/20210523_Karelia/Var'
#     # mpath = r'/Users/ronya/My_Documents/Karelia/20210523_Karelia/Group_1'
#     # opath = r'/Users/ronya/My_Documents/Karelia/test_1.txt'
#
#     vpath = r'/Users/ronya/My_Documents/Elovy_magn/var'
#     mpath = r'/Users/ronya/My_Documents/Elovy_magn/magn'
#     opath = r'/Users/ronya/My_Documents/Elovy_magn/variated_data.txt'
#     VariationsTool().main_calcVariations(vpath, mpath, opath)
