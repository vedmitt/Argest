class LogFileTool:
    def __init__(self):
        self.filepath = 'M:\Sourcetree\output\log1.txt'

    def writeToFile(self, lines, filepath):
        if len(lines) > 0:
            with open(filepath, 'w') as f:
                for line in lines:
                    f.write('\n' + str(line))

    def readFromFile(self, filepath, separator):
        pass
