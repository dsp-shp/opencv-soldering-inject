import os
import sys
from datetime import datetime

class logger(object):
    
    def __init__(self, func) -> None: self.func = func
    
    def __call__(self, *args, **kwargs): return self.init(self.func, *args, **kwargs)

    def init(self, func, *args, **kwargs) -> None:
        """ Инициализация системы логирования поверх выполняемого процесса

        >>> ... func ~ (callable) – выполняемая функция
        >>> return (func ~ callable) – func с набором дополнительных параметров
        """

        import logging
        
        self.JOB_START = datetime.now().replace(microsecond=0)
        self.JOB_ID = ''.join(x for x in str(self.JOB_START) if x.isdigit())
        self.JOB_ID = self.JOB_ID[2:8] + '-' + self.JOB_ID[8:]
        self.LOG_PATH = None
        os.path.abspath('../logs')
        ### Определение параметров логирования
        if kwargs.get('log_to_file', False) == True:
            self.LOG_PATH = os.path.abspath('../logs/{}'.format(self.JOB_START.date()))
            os.makedirs(self.LOG_PATH, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            **(
                {"stream": sys.stdout} if kwargs.get('log_to_file', False) == False else \
                {"filename": os.path.join(self.LOG_PATH, '{}.log'.format(self.JOB_ID))}
            )
        )
        self.LOG_PRE, self.LOG_SEP = '[{}] {{{}}} – ', '-'*80

        ### Реализация метода логирования класса
        self.info = lambda message, *args, status='INFO', divide=False, **kwargs: logging.info(
            ('' if divide == False else self.LOG_SEP + '\n') + \
            self.LOG_PRE.format(str(datetime.now())[:-7], status) + \
            message.format(*args, **kwargs).replace('\n', '\n\t') + \
            ('' if divide == False else '\n' + self.LOG_SEP)
        )
        ### Логирование начала выполнения процесса
        self.info(
            'Выполнение задачи ({}), попытка: {}',
            *(self.JOB_ID, kwargs.get('attempt', 1),),
            status='INFO',
            divide=True,
        )
        try:
            return func(*args, **kwargs, log=self)
        except Exception as e:
            self.info(str(e))
        finally:
            self.info(
                'Задача ({}) выполнена успешно',
                *(self.JOB_ID,),
                status='SUCCESS',
                divide=True
            )
        return

    # ### Реализовано в рамках lambda функции self.init() метода
    # def info(self, message:str, *args, status:str='INFO', divide:bool=False, **kwargs) -> None:
    #     """ Логирование сообщения
    #     """
    #     logging.info(
    #         ('' if divide == False else self.LOG_SEP + '\n') + \
    #         self.LOG_PRE.format(str(datetime.now())[:-7], status) + \
    #         message.format(*args, **kwargs).replace('\n', '\n\t') + \
    #         ('' if divide == False else '\n' + self.LOG_SEP)
    #     )

    def transfer(self, path:str, type:str) -> list:
        """ Бэкапирование изображений в logs/ папку

        >>> ... path ~ (str) - путь к исходному файлу
        >>> ... type ~ (str) – тип изображения:
                    'query' – фрагмент
                    'train' – изображение
        >>> return (str) – путь к бэкапу изображения
        """

        ### В случае, если вывод осуществляется в sys.stdout, пропустить
        if not self.LOG_PATH: return path

        import shutil

        dest = os.path.join(
            self.LOG_PATH,
            '{}_{}.{}'.format(self.JOB_ID, type, path.split('.')[-1])
        )
        shutil.copyfile(path, dest, follow_symlinks=True)
        self.info('Изображение "{}" успешно бэкапировано в \n"{}"', *(path, dest,))
        return dest
