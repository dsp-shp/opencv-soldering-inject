# **Реализация CV компонента для НПП "Инжект"**
*«Итоговая реализация программного продукта представляет из себя импортируемую библиотеку, включающую методы детекции, логирования и unit-тестирования, а также механизм вызова методов из .NET окружения»*

Репозиторий включает в себя:
- ```utils/``` – модуль, реализующий основную функциональность компонента
  - ```detector.py``` – реализация детекции объекта
  - ```logger.py``` – система логирования
  - ```tester.py``` – система unit–тестирования
- ```logs/``` – директория для сохранения логов выполнения
  - ```2023-03-01/ 2023-03-02/ 2023-03-03/ ...``` – поддиректории, содержащие результаты тестирования (партиционирование по дате выполнения) 
- ```tests/``` – директория для хранения материалов и результатов тестирования

<br>

### Используемые компоненты
- ```python3``` – *https://docs.python.org/3/faq/general.html*
- ```pip3``` – *https://pypi.org/project/pip/*
- Неоходимые библиотеки: 
  - ```opencv-contib-python``` – *https://pypi.org/project/opencv-contrib-python/*
  - ```matplotlib``` – *https://pypi.org/project/matplotlib/*

<br>

### Интеграция с C# кодом

Прежде чем перейти к процессу интеграции необходимо последовательно установить все необходимые компоненты:
1. установить ```python3```, если не предустановлен в системе;
1. установить пакетный менеджер ```pip```;
1. установить через ```pip``` необходимые библиотеки ~> ```pip3 install opencv-contrib-python matplotlib```;
1. установить ```git```, если не предустановлен в системе;
1. склонировать этот репозиторий в ```site-packages``` *(```pip3 show matplotlib -> Location```)* ~> ```git clone git@github.com:dsp-shp/inject-solder.git```.

Дальнейшая интеграция будет представлять из себя системный вызов ```python3``` с флагом "```-c```" и однострочным скриптом (строкой) для выполнения обнаружения. В последнем необходимо указать передаваемые значения пути к фрагменту и изображению. Пример итогового вызова напрямую из командной оболочки/терминала:
```bash
python3 -c "from inject_solder.utils import detector; detector(query_path='q.png', train_path='t.png')"
```
Результатом такого вызова будет вывод в stdout строкового отображения списка с необходимыми значениями смещения и поворота фрагмента относительно изображения, например:
```
[-0.1, -0.2, 3.4, 4.5, -15.0]
```
Где 0 и 1 элементы – координаты верхнего левого угла фрагмента, 2 и 3 – координаты правого нижнего угла фрагмента, и 4 элемент – его поворот с положительным значением для направления по часовой стрелке.

Итоговая реализация вышеописанного на C#:

```c#
using System;
using System.Diagnostics;
using System.Text.Json;
using System.IO;
using System.Threading.Tasks;

namespace ClassObject
{
    class Program 
    {
        static List<float> get_coordinates(string query_path, string train_path) {
            /* Функция принимает 2 строковых аргумента:
                • query_path – путь к фрагменту,
                • train_path – путь к изображению;
              и возвращает список с float значениями смещения и поворота:
                • смещение по Х левого верхнего угла фрагмента,
                • смещение по Y левого верхнего угла фрагмента,
                • смещение по Х правого нижнего угла фрагмента,
                • смещение по Y правого нижнего угла фрагмента,
                • поворот фрагмента, положителен – по часовой;
              например: [-0.1, -0.2, 3.4, 4.5, -15.0]
            */

            string command = "/usr/bin/python3"; // путь к python3 интерпретатору: python3 -c "import sys; print(sys.executable)"
            string args = "-c \"from inject_solder.utils import detector; detector" + 
              string.Format("(query_path='{0}', train_path='{1}')\"", query_path, train_path); // выполняемый скрипт

            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = command;
            start.Arguments = args;
            start.UseShellExecute = false;
            start.RedirectStandardOutput = true;

            using (Process process = Process.Start(start))
                using (StreamReader reader = process.StandardOutput) // чтение результата из stdout
                    return JsonSerializer.Deserialize<List<float>>(@reader.ReadToEnd()); // десериализация строкового списка
        }

        static void Main(string[] args) {
            // ...
            List<float> coordinates = get_coordinates("q.png", "t.png");
            // ...
            return;
        }
    }
}
```