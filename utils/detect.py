""" 

"""

import os
from json import dumps, loads
from datetime import datetime
from sys import argv

### Глобальные параметры
MIN_MATCH_COUNT = 10
FLANN_INDEX_PARAMS = {"algorithm":1, "trees":5}
FLANN_SEARCH_PARAMS = {"checks":50}

def decorate_logging(func):
    ###
    def _(*args, **kwargs):
        """ Инициализация системы логирования
        """
        import logging
        
        
        now = datetime.now()
        JOB = str(now.date()), ''.join(x for x in str(now)[:19] if x.isdigit())
        
        ### Параметры логирования
        path = './logs/{}'.format(now.date())
        os.makedirs(path, exist_ok=True)
        logging.basicConfig(filename=os.path.join(path, '{}.log'.format(JOB)), level=logging.DEBUG)
        
        return func(*args, **kwargs)

    return _

@decorate_logging
def detect(
    query_img_path:str,
    train_img_path:str,
    params:dict={
        "MIN_MATCH_COUNT":MIN_MATCH_COUNT,
        "FLANN_INDEX_PARAMS": FLANN_INDEX_PARAMS,
        "FLANN_SEARCH_PARAMS": FLANN_SEARCH_PARAMS
    }
) -> None:
    """ Определение объекта на изображении

    >>> ... query_img_path ~ (str) - путь к объекту
    >>> ... train_img_path ~ (str) - путь к изображению
    >>> ... params ~ (dict) - набор корректирующих параметров
    >>> return (None)
    """

    import cv2 as cv
    import numpy as np
    from math import acos, sqrt, pi
    from matplotlib import pyplot as plt

    MIN_MATCH_COUNT = params.get('MIN_MATCH_COUNT', None)
    FLANN_INDEX_PARAMS = params.get('FLANN_INDEX_PARAMS', None)
    FLANN_SEARCH_PARAMS = params.get('FLANN_SEARCH_PARAMS', None)

    query_img = cv.imread(query_img_path, cv.IMREAD_GRAYSCALE) ### объект
    train_img = cv.imread(train_img_path, cv.IMREAD_GRAYSCALE) ### изображение

    sift = cv.SIFT_create() ### инициализация детектора
    ### Поиск ключевых точек и дескрипторов
    query_key, query_des = sift.detectAndCompute(query_img, None)
    train_key, train_des = sift.detectAndCompute(train_img, None)
    ### Мэтчинг
    flann = cv.FlannBasedMatcher(FLANN_INDEX_PARAMS, FLANN_SEARCH_PARAMS)
    matches = flann.knnMatch(query_des, train_des, k=2)

    ### Определение подходящих мэтчей по проверке Lowe
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

    if len(good_matches) < MIN_MATCH_COUNT: raise Exception( ### обработка исключений
        "Недостаточно совпадений найдено - {}/{}".format(len(good_matches), MIN_MATCH_COUNT)
    )

    ### Гомография
    M, mask = cv.findHomography(
        srcPoints=np.float32([query_key[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2),
        dstPoints=np.float32([train_key[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2),
        method=cv.RANSAC,
        ransacReprojThreshold=5.0
    )
    matches_mask = mask.ravel().tolist()

    ### Определение крайних точек объекта
    h, w = query_img.shape
    query_pts=np.float32([[0,0], [0,h-1], [w-1,h-1], [w-1,0]]).reshape(-1,1,2)
    train_pts = cv.perspectiveTransform(src=query_pts, m=M)
    train_img = cv.polylines( ### выделение объекта на изображении
        img=train_img, 
        pts=[np.int32(train_pts)], 
        isClosed=True, 
        color=255, 
        thickness=5, 
        lineType=cv.LINE_AA
    )

    ### Определение смещения и поворота
    shifted_x = train_pts[-1][0][0] - train_pts[0][0][0]
    shifted_y = train_pts[-1][0][1] - train_pts[0][0][1]
    radius = sqrt(shifted_x**2 + shifted_y**2)

    angle = round(acos(shifted_x / radius) * 180 / pi, 1)
    if round(shifted_y, 1) != 0: angle = angle if shifted_y > 0 else -angle

    # message = ("" + \
    #     "Координаты объекта: {coords}\n" + \
    #     "Смещение на {x_shift} по X и на {y_shift} по Y\n" + \
    #     "Поворот относительно верхней левой точки на {angle}º{clockwise}"
    # ).format(
    #     coords=[(*x[0],) for x in train_pts],
    #     x_shift=round(train_pts[0][0][0], 3),
    #     y_shift=round(train_pts[0][0][1], 3),
    #     angle=angle,
    #     clockwise='' if clockwise is None else \
    #         ' {} часовой'.format('по' if clockwise == True else 'против')
    # )

    # print(message)

    # ### Отрисовка результата
    # final_img = cv.drawMatches(
    #     img1=query_img, 
    #     keypoints1=query_key, 
    #     img2=train_img, 
    #     keypoints2=train_key, 
    #     matches1to2=good_matches,
    #     outImg=None,
    #     matchesMask=matches_mask,
    #     **{ ### параметры отрисовки
    #         "matchColor":(0,255,0),
    #         "singlePointColor":None,
    #         "flags":2
    #     }
    # )
    # plt.imshow(final_img, 'gray'), plt.show()    


if __name__ == '__main__': 
    ### Проверка на наличие необходимого количества параметров
    if len(argv[1:]) < 2: raise Exception(
        'Недостаточное количество входных параметров: {}.\n'.format(argv[1:]) + \
        'Обязательно наличие пути к образцу, пути к изображению.'
    )
    ### Проверка на корректность указаных параметров
    for path in argv[1:3]:
        if not os.path.exists(path): raise Exception(
        'Некорректный путь к файлу: {}.'.format(path)
    )
    ### Если detect.py вызван корректно
    detect(
        query_img_path=argv[1], 
        train_img_path=argv[2], 
        ### Нет необходимости в коррекции параметров при первоначальном вызове
        # **({"params": loads(argv[3].replace('\'', '"'))} if len(argv[1:]) == 3 else {})
    )