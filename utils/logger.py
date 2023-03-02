from os import path as os, makedirs
from sys import stdout
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
        
        self.JOB, self.LOGS = datetime.now().strftime('%y%m%d-%H%M%S'), None
        
        ### Определение параметров логирования
        if kwargs.get('logfile', True) == True:
            self.LOGS = os.abspath('../logs/' + str(datetime.now().date()))
            makedirs(self.LOGS, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            **(
                {"stream": stdout} if kwargs.get('logfile', True) == False else \
                {"filename": os.join(self.LOGS, '{}.log'.format(self.JOB))}
            )
        )
        ### Реализация метода логирования класса
        self.info = lambda message, *args, prefix=True, status='INFO', divide=False, **kwargs: \
            logging.info(
                ('' if divide == False else '-'*80 + '\n') + \
                ('' if prefix == False else '[{}] {{{}}} – '.format(str(datetime.now())[:-7], status)) + \
                (message.format(*args, **kwargs).replace('\n', '\n\t')) + \
                ('' if divide == False else '\n' + '-'*80)
            )
        ### Логирование начала выполнения процесса
        self.info(
            'Выполнение задачи ({}), попытка: {}',
            self.JOB,
            kwargs.get('attempt', 1),
            status='INFO',
            divide=True,
        )

        try:
            status, message = 'SUCCESS', 'выполнена успешно'
            return func(*args, **kwargs, log=self)
        except Exception as e:
            status, message = 'FAILED', 'прервана ошибкой'
            self.info(str(e), status='ERROR')
        finally:
            self.info('Задача ({}) {}', self.JOB, message, status=status, divide=True)
        
        pass

    # ### Реализовано в рамках lambda функции self.init() метода
    # def info(self, message:str, *args, status:str='INFO', divide:bool=False, **kwargs) -> None:
    #     """ Логирование сообщения
    #     """
    #     logging.info(
    #         ('' if divide == False else self.SEPR + '\n') + \
    #         self.PREF.format(str(datetime.now())[:-7], status) + \
    #         message.format(*args, **kwargs).replace('\n', '\n\t') + \
    #         ('' if divide == False else '\n' + self.SEPR)
    #     )

    def transfer(self, path:str, type:str) -> list:
        """ Бэкапирование изображений в logs/ папку

        >>> ... path ~ (str) - путь к исходному файлу
        >>> ... type ~ (str) – тип изображения:
                    = 'query' – фрагмент
                    = 'train' – изображение
        >>> return (str) – путь к бэкапу изображения
        """
        import shutil
        
        if not self.LOGS: return path ### пропустить если вывод осуществляется в stdout

        dest = os.join(self.LOGS, '{}_{}.{}'.format(self.JOB, type, path.split('.')[-1]))
        shutil.copyfile(path, dest, follow_symlinks=True)
        self.info('\tИзображение "{}" успешно бэкапировано в "{}"', path, dest, prefix=False)
        
        return dest