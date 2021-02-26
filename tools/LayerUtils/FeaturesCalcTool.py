import math


class FeaturesCalcTool:
    def __init__(self):
        pass

    # def removeZeroPointsFromMemory(self, textEdit):
    #     # далее работаем с временным слоем
    #     if templayer is not None:
    #         setTextStyle('green', 'bold')
    #         textEdit.append('Временный слой успешно создан!')
    #         setTextStyle('black', 'normal')
    #         textEdit.append('Количество точек во временном слое: ' + str(templayer.GetFeatureCount()))
    #         # -------- удаляем нулевые точки ---------------
    #         if checkBox.isChecked:
    #             textEdit.append('\nНачинаем удаление нулевых точек...')
    #             try:
    #                 for i in range(templayer.GetFeatureCount()):
    #                     feat = templayer.GetNextFeature()
    #                     if feat is not None:
    #                         geom = feat.geometry()
    #                         if geom.GetX() == 0.0 and geom.GetY() == 0.0:
    #                             templayer.DeleteFeature(feat.GetFID())
    #                             outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #                             # textEdit.append(str(feat.GetField("TIME")))
    #                 templayer.ResetReading()
    #                 setTextStyle('green', 'bold')
    #                 textEdit.append('Нулевые точки успешно удалены!')
    #                 setTextStyle('black', 'normal')
    #                 textEdit.append(
    #                     'Количество точек после удаления нулевых: ' + str(templayer.GetFeatureCount()))
    #             except Exception as err:
    #                 setTextStyle('red', 'bold')
    #                 textEdit.append('\nНе удалось удалить нулевые точки! ' + str(err))
    #
    #         outDS.SyncToDisk()
    #
    #
    # def azimutCalc(self, x1, x2):
    #     dX = x2[0] - x1[0]
    #     dY = x2[1] - x1[1]
    #     dist = math.sqrt((dX * dX) + (dY * dY))
    #     dXa = math.fabs(dX)
    #     if dist != 0:
    #         beta = math.degrees(math.acos(dXa / dist))
    #         if (dX > 0):
    #             if (dY < 0):
    #                 angle = 270 + beta
    #             else:
    #                 angle = 270 - beta
    #         else:
    #             if (dY < 0):
    #                 angle = 90 - beta
    #             else:
    #                 angle = 90 + beta
    #         return angle
    #     else:
    #         return 0
    #
    # def distanceCalc(self, x1, x2):
    #     dX = x2[0] - x1[0]
    #     dY = x2[1] - x1[1]
    #     dist = math.sqrt((dX * dX) + (dY * dY))
    #     return dist
    #
    # def mainAzimutCalc(self):
    #     # ------ основная часть плагина -------------------------
    #     global azimut_2
    #     textEdit.append('\nНачинаем удаление избыточных точек...')
    #     try:
    #         feat_list = []
    #         for i in range(templayer.GetFeatureCount()):
    #             feat = templayer.GetNextFeature()
    #             feat_list.append(feat)
    #         templayer.ResetReading()
    #
    #         # отсортируем список по времени
    #         feat_list = sorted(feat_list, key=lambda feature: feature.GetField("TIME"), reverse=False)
    #
    #         accuracy = 10
    #         flightList = []
    #         parts_list = []
    #         min_dist = 6.966525707833812e-08
    #         bad_paths = []
    #         i = 0
    #         az_temp = []
    #         avg_az_list = []
    #         while i + 2 < len(feat_list):
    #             azimut_1 = azimutCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
    #                                        [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])
    #             azimut_2 = azimutCalc([feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()],
    #                                        [feat_list[i + 2].geometry().GetX(), feat_list[i + 2].geometry().GetY()])
    #
    #             dist = distanceCalc([feat_list[i].geometry().GetX(), feat_list[i].geometry().GetY()],
    #                                      [feat_list[i + 1].geometry().GetX(), feat_list[i + 1].geometry().GetY()])
    #
    #             if math.fabs(azimut_1 - azimut_2) < accuracy:
    #                 if dist < min_dist:
    #                     bad_paths.append(feat_list[i].GetFID())
    #                 else:
    #                     parts_list.append(feat_list[i])
    #                     az_temp.append(azimut_1)
    #             else:
    #                 if parts_list is not None:
    #                     flightList.append(parts_list)
    #                     az_sum = 0
    #                     for item in az_temp:
    #                         az_sum = az_sum + item
    #                     avg_az_list.append(az_sum / len(az_temp))
    #                 parts_list = [feat_list[i]]
    #                 az_temp = [azimut_1]
    #             i += 1
    #
    #         if parts_list is not None:
    #             parts_list.append(feat_list[i])
    #             parts_list.append(feat_list[i + 1])
    #             avg_az_list.append(azimut_2)
    #             flightList.append(parts_list)
    #
    #         # удаляем аномальные пути в начале полетов
    #         for item in bad_paths:
    #             templayer.DeleteFeature(item)
    #             outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #
    #         textEdit.append('Количество частей полетов: ' + str(len(flightList)))
    #         # textEdit.append('Количество усредненных азимутов: ' + str(len(avg_az_list)))
    #         longest_path = max(len(elem) for elem in flightList)
    #         textEdit.append('Самый длинный полет: ' + str(longest_path))
    #         # shortest_path = min(len(elem) for elem in flightList)
    #         # textEdit.append('Самый короткий полет: ' + str(shortest_path))
    #
    #         i_longest = 0
    #         for path in flightList:
    #             if len(path) == longest_path:
    #                 i_longest = flightList.index(path)
    #                 break
    #
    #         target_az = avg_az_list[i_longest]
    #         textEdit.append('Целевой азимут: ' + str(target_az))
    #         for i in range(len(avg_az_list)):
    #             if math.fabs(avg_az_list[i] - target_az) < accuracy or math.fabs((avg_az_list[i]+180) - target_az) < accuracy:
    #                 if len(flightList[i]) < 20:
    #                     for feat in flightList[i]:
    #                         templayer.DeleteFeature(feat.GetFID())
    #                         outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #             else:
    #                 for feat in flightList[i]:
    #                     templayer.DeleteFeature(feat.GetFID())
    #                     outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #
    #         # for i in range(len(avg_az_list)):
    #         #     textEdit.append(str(avg_az_list[i]))
    #
    #         # while i + 2 < len(avg_az_list):
    #         #     if math.fabs(avg_az_list[i] - avg_az_list[i+1]) < 90 \
    #         #             or math.fabs(avg_az_list[i+1] - avg_az_list[i+2]) < 90:
    #         #         if len(flightList[i]) > len(flightList[i+1]) and len(flightList[i+2]) > len(flightList[i+1]):
    #         #             for feat in flightList[i+1]:
    #         #                 templayer.DeleteFeature(feat.GetFID())
    #         #                 outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #         #     else:
    #         #         for feat in flightList[i]:
    #         #             templayer.DeleteFeature(feat.GetFID())
    #         #             outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #
    #         # for path in flightList:
    #         #     if len(path) < longest_path / 2:
    #         #         for feat in path:
    #         #             templayer.DeleteFeature(feat.GetFID())
    #         #             outDS.ExecuteSQL('REPACK ' + templayer.GetName())
    #
    #         setTextStyle('green', 'bold')
    #         textEdit.append('Избыточные точки успешно удалены!')
    #         setTextStyle('black', 'normal')
    #         textEdit.append('\nКоличество точек в полученном слое: ' + str(templayer.GetFeatureCount()))
    #
    #     except Exception as err:
    #         setTextStyle('red', 'bold')
    #         textEdit.append('\nНе удалось удалить избыточные точки! ' + str(err))
    #
    #     outDS.SyncToDisk()