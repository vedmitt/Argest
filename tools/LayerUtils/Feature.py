class Feature:

    def __init__(self, fields, values):
        self.content = {}
        i = 0
        for field in fields:
            self.content.setdefault(field, values[i])
            i += 1

    def addNewField(self, name, val):
        self.content.setdefault(name, val)

    def updateValue(self, name, val):
        self.content[name] = val

    def getValue(self, name):
        return self.content.get(name)

    def getAllFields(self):
        return list(self.content.keys())


# fields = ['one', 'two', 'three']
# values = [1, 2, 3]
#
# f = Feature(fields, values)
# print(f.content)
# f.addNewField('four', 4)
# print(f.content)
# print(f.getAllFields())
# f.updateValue('four', 5)
# print(f.content)
# print(f.getValue('four'))