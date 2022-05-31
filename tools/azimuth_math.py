import math


def calc_all_azimuths(gdf, az_field_name):
    """Подсчет всех азимутов в GeoDataFrame.
        :gdf: GeoDataFrame with coordinates
        :type x1, x2: tuples
        Returns GeoDataFrame with AZIMUTH column"""

    geometry = gdf.geometry

    # gdf[self.ID] = gdf.index
    gdf[az_field_name] = 0
    # gdf[self.AZ_DIFF] = 0

    # подсчет азимутов
    i = 2
    while i < len(gdf):
        if geometry[i - 2] is None or geometry[i - 1] is None or geometry[i] is None:
            pass
        else:
            x0 = (geometry[i - 2].x, geometry[i - 2].y)
            x1 = (geometry[i - 1].x, geometry[i - 1].y)
            x = (geometry[i].x, geometry[i].y)

            a1 = azimuth_calc(x0, x1)
            a2 = azimuth_calc(x1, x)
            # diff = math.fabs(a1 - a2)

            gdf.at[i - 1, az_field_name] = a1
            gdf.at[i, az_field_name] = a2
            # gdf.at[i, self.AZ_DIFF] = diff

        i += 1

    return gdf


def opposite_azimuth(az):
    """Нахождение противоположного направления азимута (на 180 градусов).
            :float az: input azimuth
            Returns opposite azimuth"""

    if 0 <= az < 180:
        return az + 180
    elif 180 <= az < 360:
        return az - 180


def get_targets(gdf):
    """Нахождение целевого азимута (самого популярного) и потивоположного ему.
                :gdf: GeoDataFrame with coordinates
                Returns tuple of target azimuths"""

    azimuths = gdf[gdf.LON != 0].AZIMUTH  # избавимся от нулевых координат

    # # построим гистограмму по азимутам
    # plt.hist(azimuths, bins=20)
    # plt.show()

    # найдем самые популярные азимуты
    az_freq = azimuths.value_counts()
    # self.print(f'\nЧастота азимутов: \n{az_freq}')
    a = az_freq.nlargest(1).index
    a = (*a, opposite_azimuth(*a))
    # self.print(f'\n\nЦелевые азимуты: {a}')
    return a


def specify_bounds(radius, targets):
    """Нахождение интервалов попадания азимута с определенным радиусом.
                    :int radius: радиус точки
                    :tuple targets: target azimuths
                    Returns list of bounds"""

    bounds = [build_bounds((t - radius, t + radius)) for t in targets]
    new_list = [v1 for sub_list in bounds for v1 in sub_list]
    bounds = []
    i = 0
    while i < len(new_list):
        bounds.append((new_list[i], new_list[i + 1]))
        i += 2
    # self.print(f'\n Интервалы азимутов: {bounds}')
    return bounds


def azimuth_calc(x1, x2):
    """AZIMUTH Calculation.
    :x1, x2: coordinates of points
    :type x1, x2: tuples
    Returns AZIMUTH angle in degrees"""

    dX = x2[0] - x1[0]
    dY = x2[1] - x1[1]
    dist = math.sqrt((dX * dX) + (dY * dY))
    dXa = math.fabs(dX)
    if dist != 0:
        beta = math.degrees(math.acos(dXa / dist))
        if dX < 0:
            if dY > 0:
                angle = 270 + beta
            else:
                angle = 270 - beta
        else:
            if dY > 0:
                angle = 90 - beta
            else:
                angle = 90 + beta
        return angle
    else:
        return 0


def check_bounds(azimuth):
    """Проверка вхождения азимута в интервал.
                        :float azimuth: input azimuth
                        Returns azimuth"""

    if azimuth < 0:
        return 360 + azimuth
    elif azimuth > 360:
        return azimuth - 360
    else:
        return azimuth


def build_bounds(bound):
    """Подсчет интервалов.
            :list bound: input bounds
            Returns intervals"""

    b = [check_bounds(bound[0]), check_bounds(bound[1])]
    if b[0] > b[1]:
        return 0, b[1], b[0], 360
    else:
        return b[0], b[1]


def numerate_profiles(gdf, AZIMUTH, FLIGHT_NUM):
    """Нумерация профилей по азимуту.
                Returns gdf with FLIGHT_NUM"""

    buffer = gdf.buffer(10)
    geometry = gdf.geometry

    # gdf['ID'] = gdf.index
    gdf[AZIMUTH] = 0
    # gdf[self.AZ_DIFF] = 0
    gdf[FLIGHT_NUM] = 1

    profile = 1
    i = 2

    while i < len(gdf):
        if geometry[i - 2] is None or geometry[i - 1] is None or geometry[i] is None:
            pass
        else:
            x0 = (geometry[i - 2].x, geometry[i - 2].y)
            x1 = (geometry[i - 1].x, geometry[i - 1].y)
            x = (geometry[i].x, geometry[i].y)

            a1 = azimuth_calc(x0, x1)
            a2 = azimuth_calc(x1, x)
            diff = math.fabs(a1 - a2)

            gdf.at[i - 1, AZIMUTH] = a1
            gdf.at[i, AZIMUTH] = a2
            # gdf.at[i, self.AZ_DIFF] = diff

            if not buffer[i - 1].intersects(buffer[i]) and diff > 5:
                profile += 1
            gdf.at[i, FLIGHT_NUM] = profile

        i += 1

    return gdf
