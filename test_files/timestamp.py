from datetime import datetime
from dateutil import parser

if __name__ == '__main__':
    # magn_format = "%d-%m-%YT%H:%M:%S,%f"
    time_str = '05-03-2021T07:50:05,00'

    # dt = datetime.strptime(time_str, magn_format)
    dt = parser.parse(time_str)
    print(dt)
    print(dt.day, dt.month, dt.year)
