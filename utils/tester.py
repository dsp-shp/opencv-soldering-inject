import os
import unittest
import sys
try: from .detector import detector, PARAMS; from .logger import logger, HOME ### поддержка python3 -c "tester(...)"
except: from detector import detector, PARAMS; from logger import logger, HOME ### поддержка python3 tester.py ...

### Реализация системы логирования для тестирования
class logger_: JOB, LOGS, process, info = None, None, lambda path, type: path, \
    lambda *args, **kwargs: None

### Unit-тестирование детекции
class unit_detector(unittest.TestCase):

    def _(self, query_path:str, train_path:str, correct:tuple) -> None:
        """ Конструктор detector теста

        >>> ... query_path ~ (str) – наименование фрагмента
        >>> ... train_path ~ (str) – наименование изображения
        >>> ... correct ~ (tuple) – кортеж, содержащий корректные результаты
        >>> return (None)
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

### Unit-тестирование методов логирования
class unit_logger(unittest.TestCase):

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
    

### Auto-тестирование детекции
class auto_detector:

    def __call__(
            self,
            path:str=os.path.join(HOME, 'logs'),
            file:str='tester.auto_detector.tsv'
        ) -> None:

        from multiprocessing import cpu_count
        from concurrent.futures import ProcessPoolExecutor
        try: import pandas as pd
        except: pass

        data = []
        with ProcessPoolExecutor(cpu_count() - 1) as executor:
            for i in executor.map(self.compute, self.generate()): data += i
        
        pd.DataFrame(data).to_csv(path_or_buf=os.path.join(path, file), sep='\t', index=False)

    def generate(
            self,
            lights:range=(0, 1,),
            scales:range=range(25, 51, 5),
            angles:range=range(0, 46, 15),
            attempts:range=range(1, 4, 1)
    ) -> tuple:
        """ Генерация набора параметров для р

        >>> ... lights ~ (range) – 
        >>> ... lights ~ (range) – 
        >>> ... lights ~ (range) – 
        >>> ... lights ~ (range) – 
        >>> yield (tuple) – 
        """

        for light in lights:
            files = (*filter(lambda x: '{}.scans.'.format(light) in x, 
                os.listdir(os.path.join(HOME, 'tests', 'autos'))
            ),)
            for file in files[:1]:
                for scale in scales:
                    for angle in angles:
                        for attempt in attempts:
                            yield (light, files, file, scale, angle, attempt,)

    def compute(
            self,
            params:tuple,
            alt_path:str=None,
        ) -> list:
        """ Рассчет ожидаемых и получение определяемых значений смещения и поворота

        >>> ... params ~ (tuple) – кортеж, содержащий параметры детекции
        >>> return (list) - данные об одной итерации тестирования
        """

        import math
        from random import randrange, choice
        try: from PIL import Image
        except: pass

        light, files, file, scale, angle, attempt = params

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

        query_img = query_img.crop((obj_cords[1][0], obj_cords[0][1], obj_cords[3][0], obj_cords[2][1]))
        ### Подготовка изображения
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
        try:
            det_kwargs = {"query_path":None, "train_path":None, "params":PARAMS, "log":logger_}
            det_cords = (*detector(**det_kwargs, query_img=query_img, train_img=train_img).values(),)
        except Exception as e:
            det_cords = None
        finally:
            det_extra = (*det_cords[-1].values(),) if det_cords[-1] else (None,)*4
            det_cords = det_cords[:-1] if det_cords else None
            return [{
                ### параметры изображения,
                "img_name": file, 
                "img_size": train_img.size,
                "img_rot_size": train_img.size, 
                "img_contains": True if not alt_path else False,
                "img_is_highlighted": bool(light),
                ### ... фрагмента,
                "obj_scale": scale,
                "obj_size": obj_size,
                "obj_cords": obj_cords, 
                "obj_angle": -angle,
                "obj_attem": attempt, 
                "pre_cords": pre_cords, 
                ### результаты детекции
                "det_angle": det_cords[-1] if det_cords else None,
                "det_cords": det_cords[:-1] if det_cords else None,
                ### экстра
                "det_query_keys": det_extra[0],
                "det_train_keys": det_extra[1],
                "det_matches": det_extra[2],
                "det_good_matches": det_extra[3], 
            }] + (self.compute(params, alt_path=path) if not alt_path else [])


if __name__ == '__main__': unittest.main()

