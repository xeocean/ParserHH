# ParserHH

## Описание

#### main.py

Программа для парсинга вакансий с сайта hh.ru, обработкой и сохранением данных в базе данных SQLite, а также
экспортом в Excel и JSON форматы. Реализовано интерактивное меню для удобства взаимодействия пользователя с программой.
Также предоставляется возможность загружать настройки из файла или создавать их вручную.

#### scan.py | filter.py

Добавлены несколько скриптов для удаления дубликатов и анализа данных. scan.py позволяет сканировать базу данных на
наличие дубликатов и удалять их; filter.py предоставляет функции для анализа и фильтрации данных,
полученных из базы данных.

#### Структура проекта:
- config - содержит файлы конфигурации для настройки параметров парсинга и работы программы.
- export - содержит файлы экспорта данных из базы данных в различные форматы, такие как Excel и JSON.
- support - содержит вспомогательные функции, используемые в других модулях программы.
- main.py - основной файл программы, запускающий парсинг и предоставляющий интерактивное меню для пользователя.
- scan.py - модуль (скрипт) для сканирования базы данных на наличие дубликатов и управления ими.
- filter.py - модуль (скрипт) для анализа и фильтрации данных, позволяющий пользователю получать информацию по заданным критериям.

## Quick Start
1. Клонируйте репозиторий: `git clone https://github.com/xeocean/ParserHH.git`
2. Создайте виртуальное окружение: `python -m venv venv`  
   - Для Linux/macOS: `source venv/bin/activate`
   - Для Windows: `venv\Scripts\activate`
3. Установите зависимости: `pip install -r requirements.txt `
4. Запустите приложение: `python main.py`

