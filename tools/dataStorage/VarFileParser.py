class VarFileParser:
    def __init__(self):
        pass

    def parse_line(self, line):
        if len(line.split(';')) > 1:
            res = [name.strip() for name in line.split(';')[1].split(':')]

            if len(res) == 1:
                res = [name.strip() for name in res[0].split(' ')]
                filter_object = filter(lambda x: x != "", res)
                res = list(filter_object)

        else:
            res = [name.strip() for name in line.split(' ')]

        return res

    def parse_file(self, filepath):  # varitions files parser
        metadata = {}
        fields = []
        records = []

        with open(filepath) as f:
            content = f.read().splitlines()

        i = 1
        while i < len(content):
            res = self.parse_line(content[i])

            if len(res) == 2:
                metadata.setdefault(res[0], res[1])
            elif len(res) > 2:
                records.append(res)

            i += 1

        for field in records.pop(0):
            fields.append(field)

        return metadata, fields, records


if __name__ == '__main__':
    filepath = '/Users/ronya/My_Documents/karelia/20210517_Magn_Data_All/Var/05030748.txt'
    p = VarFileParser()
    mdata, fields, records = p.parse_file(filepath)
    print(mdata)
    print(fields)
    print(records)
