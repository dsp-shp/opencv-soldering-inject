import os
import shutil
import sys
from datetime import datetime, timedelta

HOME = os.path.join(sys.path[-1], 'inject_solder/') ### путь к корню модуля

class logger(object):

    def __init__(self, func) -> None: 
        self.func = func; self.retain()

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs) if kwargs.get('log', None) \
            else self.init(self.func, *args, **kwargs)

    def init(self, func, *args, logs:str=os.path.join(HOME, 'logs/'), attempt:int=1, **kwargs) -> None:
        """ Инициализация системы логирования поверх выполняемого процесса

        >>> ... func ~ (callable) – выполняемая функция
        >>> return (func ~ callable) – func с набором дополнительных параметров
        """

        import logging
        
        self.JOB, self.LOGS = datetime.now().strftime('%y%m%d-%H%M%S'), None
        
        ### Определение параметров логирования
        if kwargs.get('logfile', True) == True:
            self.LOGS = os.path.join(logs, str(datetime.now().date()))
            os.makedirs(self.LOGS, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(message)s',
            **(
                {"stream": sys.stdout} if kwargs.get('logfile', True) == False else \
                {"filename": os.path.join(self.LOGS, '{}.log'.format(self.JOB))}
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
        ### Реализация метода обработки изображений
        self.process = self.transfer if self.LOGS else lambda path, type: path

        ### Логирование начала выполнения процесса
        self.info(
            'Выполнение задачи ({}), попытка: {}',
            self.JOB,
            attempt,
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
            if status == 'FAILED' and attempt < 4:
                self.init(func, *args, attempt=attempt+1, **kwargs)
        
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

    def transfer(self, path:str, type:str) -> str:
        """ Бэкапирование изображений в logs/ директорию
        (вызывается только в случае логирования выполнения в файл)
        
        >>> ... path ~ (str) - путь к исходному файлу
        >>> ... type ~ (str) – тип изображения:
                    = 'query' – фрагмент
                    = 'train' – изображение
        >>> return (str) – путь к бэкапу изображения
        """
        
        dest = os.path.join(self.LOGS, '{}_{}.{}'.format(self.JOB, type, path.split('.')[-1]))
        shutil.copyfile(path, dest, follow_symlinks=True)
        self.info('\tИзображение "{}" успешно бэкапировано в "{}"', path, dest, prefix=False)
        
        return dest
    
    def retain(self, days:int=3) -> None:
        """ Удаление неактуальных дневных партиций в logs/ директории

        >>> ... days ~ (int) – глубина сохранения партиций
        >>> return (None)
        """
        
        logs = os.path.join(HOME, 'logs/')
        for x in os.listdir(logs):
            path = os.path.join(logs, x)
            if os.path.isdir(path) and x < str(datetime.now().date() - timedelta(days=days)):
                shutil.rmtree(path)