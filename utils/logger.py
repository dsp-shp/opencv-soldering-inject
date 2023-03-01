import os
import sys

class logger(object):
    
    def __init__(self, func) -> None: self.func = func
    
    def __call__(self, *args, **kwargs): return self.init(self.func, *args, **kwargs)

    def init(self, func, *args, **kwargs):
        """ Инициализация системы логирования поверх выполняемого процесса

        >>> ... func ~ (callable) – выполняемая функция
        >>> return (func ~ callable) – func с набором дополнительных параметров
        """
        import logging
        from datetime import datetime

        print(args, kwargs)

        self.JOB_START = datetime.now()
        self.JOB_ID = ''.join(x for x in str(self.JOB_START)[:19] if x.isdigit())
        self.LOG_PATH = None
        ### Определение параметров логирования
        if kwargs.get('log_to_file', False) == True:
            self.LOG_PATH = '../logs/{}'.format(self.JOB_START.date())
            os.makedirs(self.LOG_PATH, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO, **(
                {"stream": sys.stdout} if kwargs.get('log_to_file', False) == False else \
                {"filename": os.path.join(self.LOG_PATH, '{}.log'.format(self.JOB_ID))}
            )
        )
        ### Реализация метода логирования класса
        self.info = lambda message: logging.info(
            '{}'.format(message)
        )
        ### Логирование начала выполнения процесса
        logging.info('')
        return func(*args, **kwargs, log=self)