import sqlite3
from pathlib import Path


def delete_duplicate_for_city(url_db: str):
    db_path = Path(url_db)
    if db_path.exists() and db_path.is_file():
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()

                # Удаляем дубликаты по названию вакансии и компании
                cursor.execute("""
                        DELETE FROM vacancies
                        WHERE id NOT IN (
                            SELECT MIN(id)
                            FROM vacancies
                            GROUP BY title, company
                        )
                    """)
                conn.commit()
                print("Дубликаты вакансий по городам успешно удалены.")
        except Exception as e:
            print(f"Ошибка при удалении дубликатов: {e}")
    else:
        print("Файл базы данных не найден или не является файлом")

if __name__ == "__main__":
    url = input("Введите имя базы данных (Например, sqlite.db): ")
    delete_duplicate_for_city(url)
