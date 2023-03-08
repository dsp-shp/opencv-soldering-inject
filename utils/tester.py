import os
import unittest
from detector import detector, PARAMS
from logger import logger, HOME

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
class auto_detector:

    def __init__(self): pass
    
    ### (highlighted, standard)
    ### angle: (0 - 45)
    ### image size: (% of image zone)


### Зоны:
### (0 <= x <= 165) & (0 <= y <= 85)
### (0 <= x <= 430) & (0 <= y <= 40)
### (0 <= x <= 115) & (520 <= y <= 597)

if __name__ == '__main__': unittest.main()

