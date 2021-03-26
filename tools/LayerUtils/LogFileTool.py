class LogFileTool:
    def __init__(self):
        self.filepath = 'M:\Sourcetree\output\log1.txt'

    def writeToLog(self, lines):
        if len(lines) > 0:
            with open(self.filepath, 'w') as f:
                for line in lines:
                    f.write(line)
