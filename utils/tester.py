import os
import sys
import typing
import unittest
try: from .detector import detector, PARAMS; from .logger import logger, HOME ### поддержка python3 -c "tester(...)"
except: from detector import detector, PARAMS; from logger import logger, HOME ### поддержка python3 tester.py ...

### Реализация системы логирования для тестирования
class logger_: JOB, LOGS, process, info = None, None, lambda path, type: path, \
    lambda *args, **kwargs: None

class unit_detector(unittest.TestCase):
    """ Unit-тестирование детекции

    ...

    """

    def _(self, query_path: str, train_path: str, correct: tuple) -> None:
        """ Конструктор detector теста

        Параметры:
            query_path ~ (str) – наименование фрагмента
            train_path ~ (str) – наименование изображения
            correct ~ (tuple) – кортеж, содержащий корректные результаты

        """
        
        kwargs = {
            "query_path":os.path.join(HOME, 'tests/units', query_path),
            "train_path":os.path.join(HOME, 'tests/units', train_path), 
            "params":PARAMS,
            "log":logger_
        }
        testing = *[round(x) for x in (*detector(**kwargs).values(),)[:-1]],
        self.assertEqual(
            testing,
            correct,
            '\nTest details: detector(**{}) = {} (!= {})'.format(kwargs, testing, correct)
        )

    def test_0(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-0_train.png', (131, 129, 435, 377, 0))
    def test_1(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-1_train.png', (141, -39, 456, 194, -3))
    def test_2(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-2_train.png', (895, 639, 591, 392, 180))
    def test_3(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-3_train.png', (885, 804, 569, 572, 177))

class unit_logger(unittest.TestCase):
    """ Unit-тестирование методов логирования

    ...

    """

    def test_retain(self) -> None: ### проверка logger.retain(...)
        
        part, logs = '2000-01-01', os.path.join(HOME, 'logs/')
        get_part = lambda: len([x for x in os.listdir(logs) if x == part])
        ### Создание более неактульных партиций >>> TODO: создавать рандомное количество партиций
        os.makedirs(os.path.join(logs, part), exist_ok=True); len_before = get_part()
        ### Вызов retain(...)
        logger(func=lambda: None).retain(); len_after = get_part()
        
        self.assertGreaterEqual(len_before, len_after)

    def test_transfer(self) -> None: ### проверка logger.transfer(...)

        test_logger = logger(func=lambda: None); test_logger()
        ### Бэкапирование изображений
        query_path = test_logger.transfer(
            path=os.path.join(HOME, 'tests/units', 'unit-detector_query.png'), 
            type='query'
        )
        train_path = test_logger.transfer(
            path=os.path.join(HOME, 'tests/units', 'unit-detector-0_train.png'), 
            type='train'
        )
        ### Проверка и удаление бэкапов
        query, train = os.path.exists(query_path), os.path.exists(train_path)
        for path in (query_path, train_path, ): os.remove(path)

        self.assertEqual(query and train, True)

    def test_init(self) -> None: pass ### TODO: проверка logger.init(...)

    def test_info(self) -> None: pass ### TODO: проверка logger.info(...)
    
class auto_detector:
    """ Auto-тестирование детекции

    ...

    """

    def __call__(self, path:str=os.path.join(HOME, 'logs', 'tester.auto_detector.tsv'), **kwargs) -> None:

        from multiprocessing import cpu_count
        from concurrent.futures import ProcessPoolExecutor
        try: import pandas as pd
        except: pass
        from datetime import datetime

        data, counter = [], 0

        print(datetime.now().replace(microsecond=0))
        
        with ProcessPoolExecutor(cpu_count() - 1) as executor:
            for i in executor.map(self.compute, self.generate(**kwargs)): 
                data += i; counter += 1
                if counter % 5000 == 0: print(counter, datetime.now().replace(microsecond=0))
        
        pd.DataFrame(data).to_csv(path_or_buf=path, sep='\t', index=False)

    def generate(
            self,
            types:tuple=tuple(tuple(
                x for x in os.listdir(os.path.join(HOME, 'tests', 'autos')) if y + '.scans.' in x
            ) for y in ('0', '1',)),
            scales:range=range(25, 51, 5),
            angles:range=range(0, 16),
            attempts:range=range(1, 6)
    ) -> tuple:
        """ Генерация детализации для отчетности

        Параметры:
            types (tuple): тип данных (набор файлов с, без подсветки)
            scales (range): масштаб фрагмента (отн. изображения)
            angles (range): угол поворота фрагмента
            attempts (range): номер итерации тестирования

        Возвращает:
            typing.Generator[tuple]: значения атрибутов детализации

        """

        for files in types:
            for file in files:
                for scale in scales:
                    for angle in angles:
                        for attempt in attempts:
                            yield (files, file, scale, angle, attempt,)

    def compute(self, params:tuple, alt_path:str=None) -> list:
        """ Рассчет ожидаемых и получение определяемых значений смещения и поворота

        Параметры:
            params (tuple): кортеж, содержащий параметры детекции
            alt_path (str): путь к альтернативному фрагменту: проверка на ложно-положительное обнаружение

        Возвращает:
            list: данные об одной итерации тестирования

        """

        import math
        from random import randrange, choice
        try: from PIL import Image
        except: pass

        files, file, scale, angle, attempt = params

        ### Определение возможных координат в исходных данных
        poses = [tuple(int(y) for y in x.split('.')[-2][1:-1].split(',')) for x in files]
        pos_x, pos_y = sorted([*set([x[0] for x in poses])]), sorted([*set([y[1] for y in poses])])

        img_path = os.path.join(HOME, 'tests', 'autos', file) 
        query_img, train_img = Image.open(img_path if not alt_path else alt_path), Image.open(img_path)
        
        if not alt_path:
            ### Поиск отличного от выбранного (img) изображения для выборки инородного фрагмента
            file_cords = file.split('.')[-2][1:-1].split(',')
            path = img_path.replace(','.join(file_cords), ','.join(
                [str(x[(int(file_cords[i]) + len(x) // 2) % (len(x) - 1)]) for i, x in enumerate((pos_x, pos_y,))]
            ))
            if not os.path.exists(path):
                path = img_path.replace(file, choice((*{*files}.difference({file}),)))

        obj_size = tuple(int(x * scale / 100.0) for x in train_img.size)
        img_margins = tuple(train_img.size[x] - obj_size[x] for x in (0, 1,))

        ### Подготовка фрагмента
        obj_x = randrange(0, img_margins[0])
        obj_y = randrange(0, img_margins[1] - 80) if obj_x <= 115 \
            else randrange(0, img_margins[1])
        obj_cords = (
            (obj_x, obj_y), 
            (obj_x, obj_y + obj_size[1]), 
            (obj_x + obj_size[0], obj_y + obj_size[1]), 
            (obj_x + obj_size[0], obj_y)
        )

        ### Подготовка изображений
        query_img = query_img.crop((obj_cords[1][0], obj_cords[0][1], obj_cords[3][0], obj_cords[2][1]))
        train_img = train_img.rotate(angle, Image.NEAREST, expand=1)
        
        ### Ожидаемый результат
        angle_rad, obj_x1, obj_y1 = angle * math.pi / 180, obj_x + obj_size[0], obj_y + obj_size[1]
        pre_cords = tuple(round(x, 3) for x in (
            obj_x * math.cos(angle_rad) + obj_y * math.sin(angle_rad),  ### левый верхний угол
            train_img.size[1] - (obj_x * math.sin(angle_rad) + (train_img.size[1] - obj_y) * math.cos(angle_rad)),
            obj_x1 * math.cos(angle_rad) + obj_y1 * math.sin(angle_rad), ### правый нижний угол
            train_img.size[1] - (obj_x1 * math.sin(angle_rad) + (train_img.size[1] - obj_y1) * math.cos(angle_rad)),
        ))

        ### Получаемый результат
        det_error, detected, det_angle, det_cords = None, {}, None, None
        try:
            detected = detector(
                query_path=None,
                train_path=None,
                params=PARAMS,
                log=logger_,
                query_img=query_img, 
                train_img=train_img
            )
        except Exception as e:
            det_error = str(e)
        finally:
            det_angle = detected.get('r', None)
            det_cords = (*detected.values(),)[:4] if all(tuple(x in detected for x in ('x1', 'y1', 'x2', 'y2',))) == True else None
            det_extra = {'det_{}'.format(x): y for x, y in detected.get('extra', {}).items()}
            return [{
                ### Параметры изображения
                "img_name": file, 
                "img_size": train_img.size,
                "img_rot_size": train_img.size, 
                "img_contains": True if not alt_path else False,
                "img_is_highlighted": bool(int(file.split('.')[0])),
                ### Параметры фрагмента
                "obj_scale": scale,
                "obj_size": obj_size,
                "obj_cords": obj_cords, 
                "obj_angle": -angle, ### корректировка направления
                "obj_attem": attempt, 
                "pre_cords": pre_cords, 
                ### Результаты детекции
                "det_error": det_error,
                "det_angle": det_angle,
                "det_cords": det_cords,
                **det_extra
            }] + (self.compute(params, alt_path=path) if not alt_path else [])


if __name__ == '__main__': unittest.main()
