class LogFileTool:
    def __init__(self):
        self.filepath = r'/Users/ronya/My_Documents/output/logfile.txt'

    def writeToFile(self, lines):
        if len(lines) > 0:
            with open(self.filepath, 'w') as f:
                for line in lines:
                    f.write('\n' + str(line))

