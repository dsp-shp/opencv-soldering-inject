import unittest
from logger import logger
from detector import detector, PARAMS

class detectorTest(unittest.TestCase):

    def setUp(self):
        class test_logger: info, process = [lambda *args, **kwargs: None] * 2

    def test(self):
        args = {'query_path':'', 'train_path':'', 'params':PARAMS}
        self.assertEqual(
            detector(**input, log=test_logger).values(),
            [],
            'Некорректный результат работы detector(**{})'.format(args)
        )

if __name__ == '__main__':
    unittest.main()

