import os
import sys
from logger import logger
from json import loads


@logger
def detector(
    query_img_path:str,
    train_img_path:str,
    params:dict={
        ### Дефолтные значения
        "MIN_MATCH_COUNT":10,
        "FLANN_INDEX_PARAMS":{"algorithm":1, "trees":5},
        "FLANN_SEARCH_PARAMS":{"checks":50}
    },
    log_to_file:bool=False,
    log:object=None,
    attempt:int=1,
    **kwargs
) -> None:
    """ Определение объекта на изображении

    >>> ... query_img_path ~ (str) - путь к фрагменту
    >>> ... train_img_path ~ (str) - путь к изображению
    >>> ... params ~ (dict) - набор корректирующих параметров
    >>> ... log_to_file ~ (bool) - способ логирования процесса выполнения:
                = True - в файл директории logs/
                = False - в sys.stdout
    >>> ... log ~ (object) – объект, реализующий логирование
    >>> ... attempt ~ (int) - номер попытки
    >>> return (None) – функция логирует результат в sys.stdout
    """

    import cv2 as cv
    import numpy as np
    from math import acos, sqrt, pi
    from matplotlib import pyplot as plt

    min_match_count, flann_index_params, flann_search_params = params
    log.info('Параметры детекции:\n"{}"', params)

    query_img = cv.imread(log.transfer(query_img_path, 'query'), cv.IMREAD_GRAYSCALE) ### объект
    train_img = cv.imread(log.transfer(train_img_path, 'train'), cv.IMREAD_GRAYSCALE) ### изображение
    log.info('Изображения прочитаны')
    
    sys.exit()

    sift = cv.SIFT_create() ### инициализация детектора
    ### Поиск ключевых точек и дескрипторов
    query_key, query_des = sift.detectAndCompute(query_img, None)
    train_key, train_des = sift.detectAndCompute(train_img, None)
    ### Мэтчинг
    flann = cv.FlannBasedMatcher(flann_index_params, flann_search_params)
    matches = flann.knnMatch(query_des, train_des, k=2)

    ### Определение подходящих мэтчей по проверке Lowe
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

    if len(good_matches) < min_match_count: raise Exception(
        "Недостаточно совпадений найдено - {}/{}".format(len(good_matches), min_match_count)
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
    ### Вывод итогового результата
    print([shifted_x, shifted_y, angle,])

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
    ### Проверка на наличие необходимого/достаточного количества параметров
    if len(sys.argv[1:]) not in (2, 3,): raise Exception(
        'Некорректное количество входных параметров: {}.\n'.format(sys.argv[1:]) + \
        'Обязательно наличие пути к образцу, пути к изображению.'
    )
    ### Проверка на корректность указаных путей
    for path in sys.argv[1:3]:
        if not os.path.exists(path): raise Exception(
        'Некорректный путь к файлу: {}.'.format(path)
    )
    ### Проверка на корректность дампа словаря
    if len(sys.argv[1:]) == 3:
        try: params = loads(sys.argv[3])
        except Exception as exc: raise Exception(
            'Некорректно задан конфигурационный словарь: {}.\n{}'.format(sys.argv[3], exc)
        )
    ### Если detect.py вызван корректно
    detector(
        query_img_path=sys.argv[1], 
        train_img_path=sys.argv[2], 
        ### Нет необходимости в коррекции параметров при первоначальном вызове
        # **({"params": loads(argv[3].replace('\'', '"'))} if len(argv[1:]) == 3 else {})
        log_to_file=True
    )