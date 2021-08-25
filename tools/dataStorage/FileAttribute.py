import os
from pathlib import Path


class FileAttribute:
    typex = {'ESRI Shapefile': '.shp', 'delimitedtext': '.txt'}

    def __init__(self, file_path, file_name=None, file_ext=None):
        if os.path.isdir(file_path):
            self.dir_path = file_path
        else:
            self.dir_path = Path(file_path).parent
            self.file_name, self.file_ext = os.path.splitext(os.path.basename(file_path))  # name.shp = name; .shp

    def getFileName(self):
        return self.file_name

    def setFileName(self, new_name):
        self.file_name = new_name

    def getFilePath(self):
        return os.path.join(self.dir_path, self.file_name + self.file_ext)

    def getDirPath(self):
        return self.dir_path

    def getNewFilePath(self, new_fname, file_type):  # file_type or .file_extention
        self.file_name = new_fname
        self.setFileExtendByType(file_type)
        self.file_ext = self.getFileExtension()
        return os.path.join(self.dir_path, self.file_name + self.file_ext)

    def getFileExtension(self):
        return self.file_ext

    def setFileExtendByType(self, type):
        if type in FileAttribute.typex.keys():
            self.file_ext = FileAttribute.typex.get(type)
        elif type in FileAttribute.typex.values():
            self.file_ext = type

    # def setExtraData(self, data):
    #     self.extraData = data
    #
    # def getExtraData(self):
    #     return self.extraData


if __name__ == '__main__':
    fdir = r'/Users/ronya/My_Documents/karelia/karelia_results'
    fpath = r'/Users/ronya/My_Documents/karelia/karelia_results/test_plot_1.shp'

    # fname = os.path.basename(fpath)  # test_plot_1.shp
    # in_fn, in_ex = os.path.splitext(fname)
    # print(in_fn, in_ex)
    #
    # print(os.path.join(fdir, 'test_plot_1' + '.txt'))
    #
    # dirname1 = os.path.basename(fpath)

    # p = Path(fpath)
    # p = Path(fdir)
    # print(p.parent)
