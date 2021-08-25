from datetime import datetime
import dateutil.parser


class DataTimeUtil:

    def __init__(self):
        self.epoch = datetime.utcfromtimestamp(0)

    def unix_time_millis(self, dt):
        return (dt - self.epoch).total_seconds() * 1000.0

    def getDate(self, timeStr):
        date = dateutil.parser.parse(timeStr)
        return date

    def getDateByDataformat(self, timeStr, data_format='%d-%m-%YT%H:%M:%S,%f'):
        return datetime.strptime(timeStr, data_format)

    def getDatatimeAsNumber(self, components):  # [month, day, hour, minute, second]
        month = components[0]
        day = components[1]
        hour = components[2]
        minute = components[3]
        second = components[4]

        # res = hour + minute/60 + second/3600  # в часах (без даты)
        # res = month*30 + day + hour*3600 + minute*60 + second  # в секундах (без даты)
        # res = month*30 + day + hour/24 + minute/60 + second/3600  # в днях
        res = month + day/30 + hour/24 + minute/60 + second/3600  # в месяцах
        return res

    def joinDataFromDust(self, features, fields):
        # Объединим столбцы времени
        features.addNewField('TIME', 'String')

        for i in range(features.featureCount()):
            parts = []
            for j in range(len(fields)):
                item = features.getFeatureValue(i, fields[j])

                # if isinstance(item, str):
                # if int(item) < 10:
                #     item = '0' + str(item)
                parts.append(str(item))

            # sec_char = str(fn2).split('.')
            # if int(sec_char[0]) < 10:
            #     sec_char[0] = '0' + sec_char[0]
            # fn2 = sec_char[0] + ',' + str(sec_char[1]) + '00000'

            if len(parts) > 5:
                date = '-'.join(parts[:3])
                time = ':'.join(parts[3:])
                new_val = 'T'.join([date, time])
                # new_val = str(parts[0]) + '-' + str(parts[1]) + '-' + str(parts[2]) + 'T' + str(parts[3]) + ':' + str(parts[4]) + ':' + str(parts[5])
                features.setFeature(i, 'TIME', new_val)

        return features
