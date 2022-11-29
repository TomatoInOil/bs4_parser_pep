# Проект парсинга python.org
## Оглавление
1. [Описание](https://github.com/TomatoInOil/bs4_parser_pep#описание)
2. [Как развернуть проект?](https://github.com/TomatoInOil/bs4_parser_pep#как-развернуть-проект)
3. [Доступные команды](https://github.com/TomatoInOil/bs4_parser_pep#доступные-команды)
    1. [Примеры команд](https://github.com/TomatoInOil/bs4_parser_pep#примеры-команд)
4. [Автор](https://github.com/TomatoInOil/bs4_parser_pep#автор)
## Описание
Парсер включает в себя несколько функций, описанных в разделе "Доступные команды", направленных на сбор информации с официальных поддоменов `*.python.org`.
## Как развернуть проект?
Склонировать репозиторий 
```BASH
git clone https://github.com/TomatoInOil/bs4_parser_pep.git
```
Перейти в корневую папку проекта
```BASH
cd bs4_parser_pep/
```
Создать виртуальное окружение
```BASH
python -m venv venv
```
Активировать виртуальное окружение
```BASH
source venv/Scripts/activate
```
Установить зависимости
```BASH
pip install -r requirements.txt
```
Перейти в папку src
```BASH
cd src/
```
Можно выполнять доступные команды, например
```BASH
python main.py whats-new
```
## Доступные команды
Общая справка
```BASH
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

options:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```
### Примеры команд
Собрать ссылки на статьи о нововведениях в Python, информацию об авторах и редакторах статей, сохраняя результат в CSV-файл.
```BASH
python main.py -o file whats-new
```
Собрать информацию о статусах версий Python, выводя её в терминал в формате PrettyTable.
```BASH
python main.py -o pretty latest-versions
```
Скачать архив с актуальной документацией.
```BASH
python main.py download
```
Посчитать количество PEP в каждом статусе и общее количество PEP и сохранить в CSV-файл, очистив перед этим кеш.
```BASH
python main.py -с -o file pep
```
## Автор
Проект выполнен в рамках учебы в Яндекс.Практикум [Паутовым Даниилом](https://github.com/TomatoInOil) =^..^=______/
