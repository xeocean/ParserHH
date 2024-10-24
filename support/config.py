import json
import os
from pathlib import Path


def create_config():
    url_db = input("Введите имя базы данных для сохранения результатов (например, sqlite_db): ")
    text = input("Введите ключевые слова для поиска через запятую: ").split(',')
    area_id = input("Введите регионы поиска через запятую (113 - Вся Россия): ").split(',')

    # Все возможные уровни опыта
    experience_options = ['noExperience', 'between1And3', 'between3And6', 'moreThan6', None]
    experience = input("Введите уровни опыта через запятую (например, 'noExperience,between1And3') "
                       "или оставьте пустым: ").split(',')
    experience = [exp for exp in experience if exp in experience_options]

    # Все возможные типы расписания
    schedule_options = ['fullDay', 'partTime', 'remote', 'flexible', None]
    schedule = input("Введите уровни расписания через запятую (например, 'fullDay,partTime,remote') "
                     "или оставьте пустым: ").split(',')
    schedule = [sched for sched in schedule if sched in schedule_options]

    if text and area_id and url_db:
        config_data = {
            "url_db": f'{url_db}.db',
            "text": text if text else [],
            "experience": experience if experience else [],
            "schedule": schedule if schedule else [],
            "area_id": area_id if area_id else [],
        }

        config_dir = Path("config")
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)

        name_config = input("Введите имя файла конфигурации (например, config): ")
        config_path = os.path.join(config_dir, f"{name_config}.json")

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=4)
            print(f"Конфигурация сохранена в {name_config}.json")

        return config_data

    else:
        return


def load_config():
    config_dir = Path("config")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    name_config = input("Введите имя файла конфигурации (например, config): ")

    try:
        config_path = os.path.join(config_dir, f"{name_config}.json")
        with open(config_path, "r") as f:
            config_data = json.load(f)
            print(f"Конфигурация загружена из {name_config}")
            print(config_data)
            return config_data
    except FileNotFoundError:
        print(f"Ошибка: файл конфигурации {name_config}.json не найден.")
        return None
