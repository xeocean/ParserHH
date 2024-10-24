import os
import requests
import sqlite3
import time
import export

from support import config, export

# Задержка перед запросом на сервер
DELAY = 1


def create_db(url: str):
    # Создаем базу данных и таблицу
    with sqlite3.connect(url) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                    SELECT name FROM sqlite_master WHERE type='table' AND name='vacancies';
                """)
        if cursor.fetchone() is None:
            # Если таблицы нет, создаем ее
            cursor.execute("""
                        CREATE TABLE IF NOT EXISTS vacancies (
                            id INTEGER PRIMARY KEY,
                            title VARCHAR(255),
                            company VARCHAR(100),
                            company_id INTEGER,
                            city VARCHAR(50),
                            industries TEXT,
                            salary VARCHAR(50),
                            requirement TEXT,
                            responsibility TEXT,
                            skills TEXT,
                            experience VARCHAR(100),
                            schedule VARCHAR(50),
                            url TEXT
                        )
                    """)
            print("База данных создана и таблица 'vacancies' создана")
        else:
            print("Таблица 'vacancies' уже существует. Будет произведена дозапись")


def delete_db(url: str):
    # Проверяем, существует ли файл базы данных
    if not os.path.exists(url):
        print(f"Ошибка: база данных по пути {url} не найдена.")
        return
    try:
        os.remove(url)
        print(f"База данных {url} успешно удалена.")
    except Exception as e:
        print(f"Ошибка при удалении базы данных: {e}")


def search_skills(vacancy_id: str):
    url = f'https://api.hh.ru/vacancies/{vacancy_id}'

    response = requests.get(url)
    data = response.json()

    # Извлекаем навыки из данных вакансии
    skills = [skill['name'] for skill in data.get('key_skills', [])]
    return ', '.join(skills)


def search_industries(company_id: str):
    url = f'https://api.hh.ru/employers/{company_id}'
    response = requests.get(url)
    data = response.json()

    # Извлекаем отрасли компании
    industries = [industry['name'] for industry in data.get('industries', [])]
    return ', '.join(industries)


def add_vacancy(vacancy_id: str, title: str, company: str, company_id: str, city: str, salary: str, requirement: str,
                responsibility: str, experience: str, schedule: str, url: str, url_db: str):
    with sqlite3.connect(url_db) as conn:
        cursor = conn.cursor()

        # Проверяем, существует ли запись с данным vacancy_id
        cursor.execute("SELECT id FROM vacancies WHERE id = ?", (vacancy_id,))

        # Если запись существует, то возвращает результат
        if cursor.fetchone() is None:

            time.sleep(DELAY)  # Задержка перед запросом на сервер (Подробнее о вакансии)
            skills = search_skills(vacancy_id)

            time.sleep(DELAY)  # Задержка перед запросом на сервер (Подробнее о компании)
            industries = search_industries(company_id)

            cursor.execute("""
                INSERT INTO vacancies (id, title, company, company_id, industries, city, salary, requirement,
                 responsibility, skills, experience, schedule, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vacancy_id, title, company, company_id, industries, city, salary, requirement, responsibility,
                skills, experience, schedule, url))

        conn.commit()


def search_vacancies(config: dict):
    url = "https://api.hh.ru/vacancies"

    if not config:
        print("Ошибка: конфигурация не загружена.")
        return

    for text_search in config['text']:
        for region_value in config['area_id']:
            # Проход по уровням опыта, если они указаны
            experience_levels = config['experience'] if config['experience'] else [None]
            schedule_types = config['schedule'] if config['schedule'] else [None]

            for experience_level in experience_levels:  # Проход по списку уровней опыта
                for schedule_type in schedule_types:  # Проход по списку расписаний

                    page = 0
                    stay = 0

                    while True:
                        try:

                            params = {
                                "text": text_search,
                                "area": region_value,
                                "experience": experience_level if experience_level else None,
                                "schedule": schedule_type if schedule_type else None,
                                "page": page,
                                "per_page": 100,
                            }

                            print(params)

                            response = requests.get(url, params=params)

                            if response.status_code != 200:
                                print(f"Error: {response.status_code}")
                                break

                            data = response.json()
                            total_vacancies = data['found']
                            print(f"Найдено вакансий: {total_vacancies}")

                            if 'items' not in data:
                                print("Нет данных")
                                break

                            for vacancy in data['items']:
                                vacancy_data = {
                                    "vacancy_id": vacancy['id'],
                                    "title": vacancy['name'],
                                    "company": vacancy['employer']['name'],
                                    "company_id": vacancy['employer'].get('id', None),
                                    "city": vacancy.get('area', {}).get('name', None),
                                    "salary": vacancy.get('salary', None),
                                    "requirement": vacancy.get('snippet', {}).get('requirement', None),
                                    "responsibility": vacancy.get('snippet', {}).get('responsibility', None),
                                    "experience": vacancy.get('experience', {}).get('name', None),
                                    "schedule": vacancy.get('schedule', {}).get('name', None),
                                    "url": vacancy['alternate_url'],
                                    "url_db": config["url_db"]
                                }

                                # Обработка зарплаты
                                if vacancy_data["salary"]:
                                    salary_from = vacancy_data["salary"].get('from', None)
                                    # salary_to = vacancy_data["salary"].get('to', None)
                                    vacancy_data["salary"] = salary_from
                                else:
                                    vacancy_data["salary"] = None

                                # Добавление вакансии
                                add_vacancy(**vacancy_data)

                                stay += 1  # Увеличиваем значение stay для текущей страницы
                                remaining = total_vacancies - stay
                                print(f"Добавлена вакансия: {vacancy_data['title']}. Осталось: {remaining}")

                            if page >= data['pages'] - 1:
                                print(f"Поиск завершен! Добавлено {total_vacancies} вакансий")
                                break

                            page += 1

                            time.sleep(DELAY)  # Задержка перед запросом на сервер (Следующая страница)
                        except Exception as e:
                            print(f"Произошла ошибка: {e}. Перезапуск через 10 секунд...")
                            time.sleep(10)
                            continue


def main():
    print("Парсинг hh.ru")
    while True:
        try:
            choice = int(input("Выберите действие (1 - Поиск вакансий, 2 - Удалить БД, 3 - Экспорт в Excel,"
                               " 4 - Экспорт в Json, 5 - Выход): "))
            match choice:
                case 1:
                    choice_config = int(input("Использовать конфигурацию файла? (1 - Да, 2 - Нет): "))
                    if choice_config == 1:
                        config_file = config.load_config()
                        if config_file:
                            create_db(config_file['url_db'])
                            search_vacancies(config_file)
                    elif choice_config == 2:
                        config_file = config.create_config()
                        if config_file:
                            create_db(config_file['url_db'])
                            search_vacancies(config_file)
                case 2:
                    url_db = input("Введите имя базы данных (sqlite.db): ")
                    delete_db(url_db)
                case 3:
                    url_db = input("Введите имя базы данных (sqlite.db): ")
                    if export.export_db_to_excel(url_db):
                        print("Экспорт завершен")
                case 4:
                    url_db = input("Введите имя базы данных (sqlite.db): ")
                    if export.export_db_to_json(url_db):
                        print("Экспорт завершен")
                case 5:
                    print("Завершение работы программы...")
                    break
                case _:
                    print("Неверный выбор. Попробуйте еще раз.")
        except KeyboardInterrupt:
            print("Выход из программы...")
        except ValueError:
            print("Ошибка: введите число от 1 до 5.")


if __name__ == "__main__":
    main()
