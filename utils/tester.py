import unittest
import os
from logger import logger
from detector import detector, PARAMS

### Реализация сисетмы логирования для тестирования
class test_logger: JOB, LOGS, process, info = None, None, lambda path, type: path, \
    lambda *args, **kwargs: None

class detectorTest(unittest.TestCase):

    def _(self, query_path:str, train_path:str, correct:tuple) -> None:
        """ Конструктор detector теста

        >>> ... query_path ~ (str) – наименование фрагмента
        >>> ... train_path ~ (str) – наименование изображения
        >>> ... correct ~ (tuple) – кортеж, содержащий корректные результаты
        >>> return (None)
        """
        
        kwargs = {
            "query_path":os.path.join("../tests/", query_path),
            "train_path":os.path.join("../tests/", train_path), 
            "params":PARAMS
        }
        testing = *[round(x) for x in detector(**kwargs, log=test_logger).values()],
        self.assertEqual(
            testing,
            correct,
            '\nTest details: detector(**{}) = {} (!= {})'.format(kwargs, testing, correct)
        )

    def test_0(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-0_train.png', (131, 129, 435, 377, 0))
    def test_1(self) -> None:
        self._('unit-detector_query.png', 'unit-detector-1_train.png', (141, -39, 456, 194, -3))

class loggerTest(unittest.TestCase):

    def test_retain(self) -> None:
        import os

        part, logs = '2000-01-01', os.path.abspath('../logs/')
        get_part = lambda: len([x for x in os.listdir(logs) if x == part])
        
        os.makedirs(os.path.join(logs, part), exist_ok=True)
        len_before = get_part()
        
        logger(func=lambda: None).retain()
        len_after = get_part()
        self.assertGreaterEqual(
            len_before, 
            len_after
        )



if __name__ == '__main__': unittest.main()

