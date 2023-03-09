import os
import unittest
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
            "params":PARAMS
        }
        testing = *[round(x) for x in detector(**kwargs, log=logger_).values()],
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
def auto_detector(scales=range(25, 51, 5), angles=range(0, 46, 15)):
    import pandas as pd
    from PIL import Image

    def get_cords() -> list:
        """ Рассчет ожидаемых и получение определяемых значений смещения и поворота
        
        >>> return (list) - данные об одной итерации тестирования
        """
        import math
        from random import randrange

        kwargs = {"query_path":None, "train_path":None, "params":PARAMS, "log":logger_}

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
        query_img = img.crop((obj_cords[1][0], obj_cords[0][1], obj_cords[3][0], obj_cords[2][1]))
        ### Подготовка изображения
        train_img = img.rotate(angle, Image.NEAREST, expand=1)
        
        ### Ожидаемый результат
        angle_rad, obj_x1, obj_y1 = angle * math.pi / 180, obj_x + obj_size[0], obj_y + obj_size[1]
        pre_cords = tuple(round(x, 3) for x in (
            obj_x * math.cos(angle_rad) + obj_y * math.sin(angle_rad), 
            train_img.size[1] - (obj_x * math.sin(angle_rad) + (img.size[1] - obj_y) * math.cos(angle_rad)),
            obj_x1 * math.cos(angle_rad) + obj_y1 * math.sin(angle_rad), 
            train_img.size[1] - (obj_x1 * math.sin(angle_rad) + (img.size[1] - obj_y1) * math.cos(angle_rad)),
        ))
        ### Получаемый результат
        try: det_cords = (*detector(**kwargs, query_img=query_img, train_img=train_img).values(),)
        except Exception as e: det_cords = None
        finally: return [
            file, img.size, train_img.size, img_light, ### параметры изображения,
            scale, obj_size, obj_cords, angle, pre_cords, ### ... фрагмента,
            *((det_cords[-1], det_cords[:-1],) if det_cords else (None, None,)) ### результаты детекции
        ]

    data = []
    files = [x for x in os.listdir(os.path.join(HOME, 'tests', 'autos')) if '.scans.' in x]
    
    for file in files[:5]:
        img_light = False if file.startswith('std.') else True
        img = Image.open(os.path.join(HOME, 'tests', 'autos', file))
        for scale in scales:
            obj_size = tuple(int(x * scale / 100.0) for x in img.size)
            img_margins = tuple(img.size[x] - obj_size[x] for x in (0, 1,))
            for angle in angles: data.append(get_cords())
    
    ### Сохранить результат
    pd.DataFrame(
        data=data, columns=[
            'img_name', 'img_size', 'img_rot_size', 'img_is_highlighted', ### параметры изображения,
            'obj_scale', 'obj_size', 'obj_cords', 'obj_angle', 'pre_cords', ### ... фрагмента,
            'det_angle', 'det_cords' ### результаты детекции
        ]
    ).to_csv(path_or_buf=os.path.join(HOME, 'logs', 'tester.auto_detector.tsv'), sep='\t', index=False)


if __name__ == '__main__': unittest.main()

