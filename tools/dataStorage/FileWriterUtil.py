import csv
import os


class FileWriterUtil:
    def __init__(self):
        pass

    def writeLinesToFile(self, filepath, lines):
        if len(lines) > 0:
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write(str(line))

    def writeTXTwithHeader(self, fpath, header, data, separator='\t'):
        with open(fpath, 'w') as f:
            w = csv.writer(f, delimiter=separator)
            w.writerow(header)
            for row in data:
                w.writerow(row)
            return 1, '\nФайл с результатом успешно сохранен!'

    def getFilePathsFromDir(self, dir_path, exts):  # 'str', list
        fpaths = []
        with os.scandir(dir_path) as dir:
            for file in dir:
                fpath, ext = os.path.splitext(file)  # /path/to/file , .extention
                if ext in exts:
                    in_fpath = fpath + ext
                    fpaths.append(in_fpath)
        fpaths = sorted(fpaths)  # сортировка по возрастанию
        return fpaths


if __name__ == '__main__':
    filepath = r'/Users/ronya/My_Documents/karelia/20210523_Karelia/Var'
    fpaths = FileWriterUtil().getFilePathsFromDir(filepath, ['.txt'])
    print(fpaths)