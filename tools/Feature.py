class Feature:

    def __init__(self, fields_list, values, geom):
        self.content = {}
        self.geometry = geom
        i = 0
        for field in fields_list:
            self.content.setdefault(field, values[i])
            i += 1

    def addNewVal(self, name, val):
        self.content.setdefault(name, val)

    def setValue(self, name, val):
        if name in self.content.keys():
            self.content[name] = val
        else:
            self.content.setdefault(name, val)

    def getValue(self, name):
        return self.content.get(name)

    def getAllFields(self):
        return list(self.content.keys())

    # def getFieldType(self, field_name):
    #     return self.fields.get(field_name)

    def getAllValues(self):
        return list(self.content.values())

    def getGeometry(self):
        return self.geometry

    def setGeometry(self, geom):
        self.geometry = geom


feat = {'one': 10, 'two': None}
print(feat)
print(bool(feat.get('one')))
print(bool(feat.get('two')))
