import cv2 as cv
from os import path as os
from sys import argv
from logger import logger
from json import loads

### Дефолтные значения
PARAMS={
    "MIN_MATCHES":10,
    "FLN_INDEX":{"algorithm":1, "trees":5},
    "FLN_SEARCH":{"checks":50},
    "HOMOGRAPHY":{"method":cv.RANSAC, "ransacReprojThreshold":5.0}
}

@logger
def detector(
    query_path:str,
    train_path:str,
    params:dict=PARAMS,
    logfile:bool=True,
    log:object=None,
    attempt:int=1,
    **kwargs
) -> None:
    """ Определение объекта на изображении

    >>> ... query_path ~ (str) - путь к фрагменту
    >>> ... train_path ~ (str) - путь к изображению
    >>> ... params ~ (dict) - набор корректирующих параметров
    >>> ... logfile ~ (bool) - способ логирования процесса выполнения:
                = True - в файл директории logs/
                = False - в sys.stdout
    >>> ... log ~ (object) – объект, реализующий логирование
    >>> ... attempt ~ (int) - номер попытки выполнения
    >>> return (None) – функция логирует результат в sys.stdout
    """

    import numpy as np
    from math import acos, sqrt, pi
    from matplotlib import pyplot as plt

    global PARAMS

    MIN_MATCHES, FLN_INDEX, FLN_SEARCH, HOMOGRAPHY = {**PARAMS, **params}.values()
    log.info('Параметры детекции:\n"{}"', params)

    log.info('Обработка изображений:')
    query_img = cv.imread(log.transfer(query_path, 'query'), cv.IMREAD_GRAYSCALE) ### фрагмент
    train_img = cv.imread(log.transfer(train_path, 'train'), cv.IMREAD_GRAYSCALE) ### изображение
    log.info('Изображения прочитаны')
    
    detector = cv.SIFT_create() ### инициализация детектора
    log.info('Детектор инициализирован: {}', detector.__class__)
    ### Поиск ключевых точек и дескрипторов
    query_key, query_des = detector.detectAndCompute(query_img, None)
    train_key, train_des = detector.detectAndCompute(train_img, None)
    log.info('Ключевые точки определены: query ({}), train ({})', len(query_key), len(train_key))
    ### Мэтчинг
    matcher = cv.FlannBasedMatcher(FLN_INDEX, FLN_SEARCH)
    log.info('Мэтчер инициализирован: {}', matcher.__class__)
    matches = matcher.knnMatch(query_des, train_des, k=2)
    ### Определение подходящих мэтчей по проверке Lowe
    good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]
    log.info('Результаты мэтчинга: до очистки ({}), после очистки ({})', len(matches), len(good_matches))

    if len(good_matches) < MIN_MATCHES: raise Exception(
        'Недостаточно совпадений найдено - {}/{}'.format(len(good_matches), MIN_MATCHES)
    )

    ### Гомография
    M, mask = cv.findHomography(
        srcPoints=np.float32([query_key[m.queryIdx].pt for m in good_matches]).reshape(-1,1,2),
        dstPoints=np.float32([train_key[m.trainIdx].pt for m in good_matches]).reshape(-1,1,2),
        **HOMOGRAPHY
    )
    matches_mask = mask.ravel().tolist()
    log.info('Поиск гомографии:\n{}', M)

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
    log.info('Определение координат исходного фрагмента:\n"{}"', [[*x[0]] for x in train_pts])

    ### Определение смещения и поворота
    shifted_x = train_pts[-1][0][0] - train_pts[0][0][0]
    shifted_y = train_pts[-1][0][1] - train_pts[0][0][1]
    radius = sqrt(shifted_x**2 + shifted_y**2)
    angle = round(acos(shifted_x / radius) * 180 / pi, 1) * (1 if shifted_y >= 0 else -1)
    shifts = {
        'x1': round(train_pts[0][0][0], 3),
        'y1': round(train_pts[0][0][1], 3), 
        'x2': round(train_pts[2][0][0], 3), 
        'y2': round(train_pts[2][0][1], 3), 
        'r': angle
    }
    log.info('Определение параметров смещения (положительно при повороте по часовой):\n"{}"', shifts,)

    ### Вывод итогового результата
    print([*shifts.values()])
    log.info('Вывод результата в STDOUT: "{}"', *([*shifts.values()],))

    ### Отрисовка результата
    final_img = cv.drawMatches(
        img1=query_img, 
        keypoints1=query_key, 
        img2=train_img, 
        keypoints2=train_key,
        matches1to2=good_matches,
        outImg=None,
        matchesMask=matches_mask,
        **{ ### параметры отрисовки
            "matchColor":(0,255,0),
            "singlePointColor":None,
            "flags":2
        }
    )
    plt.imshow(final_img, 'gray'), plt.axis('off')
    reslt_path = None if not log.LOGS else os.join(log.LOGS, log.JOB+'_reslt.png')
    log.info('Отрисовка результата' + ('' if not reslt_path else ':\n"{}"'.format(reslt_path)))
    plt.show() if not log.LOGS else plt.savefig(reslt_path, bbox_inches='tight')

    pass


if __name__ == '__main__':
    ### Проверка на наличие необходимого/достаточного количества параметров
    if len(argv[1:]) not in (2, 3,): raise Exception(
        'Некорректное количество входных параметров: {}.\n'.format(argv[1:]) + \
        'Обязательно наличие пути к образцу, пути к изображению.'
    )
    ### Проверка на корректность указаных путей
    for arg in argv[1:3]:
        if not os.exists(arg): raise Exception(
        'Некорректный путь к файлу: {}.'.format(arg)
    )
    ### Проверка на корректность дампа словаря
    if len(argv[1:]) == 3:
        try: params = loads(argv[3])
        except Exception as exc: raise Exception(
            'Некорректно задан конфигурационный словарь: {}.\n{}'.format(argv[3], exc)
        )
    ### Если detect.py вызван корректно
    detector(
        query_path=argv[1], 
        train_path=argv[2], 
        ### Нет необходимости в коррекции параметров при первоначальном вызове
        # **({"params": loads(argv[3].replace('\'', '"'))} if len(argv[1:]) == 3 else {})
        logfile=True
    )