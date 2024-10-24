import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


# Подключаемся к базе данных и загружаем данные
def load_vacancies(url_db):
    db_path = Path(url_db)
    if db_path.exists() and db_path.is_file():
        try:
            conn = sqlite3.connect(db_path)
            query = "SELECT * FROM vacancies"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Ошибка: {e}")
            return None
    else:
        print("Файл базы данных не найден или не является файлом")
        return None


# Функция для анализа статистики по вакансиям
def analyze_statistics(vacancies_df):
    total_vacancies = len(vacancies_df)
    print(f"Общее количество вакансий: {total_vacancies}")

    # Количество вакансий по регионам
    vacancies_by_city = vacancies_df['city'].value_counts()
    print("\nКоличество вакансий по регионам:")
    print(vacancies_by_city)

    # Количество вакансий по компаниям
    vacancies_by_company = vacancies_df['company'].value_counts()
    print("\nКоличество вакансий по компаниям:")
    print(vacancies_by_company.head(10))  # Топ-10 компаний
    return vacancies_by_city, vacancies_by_company


# Функция для анализа зарплат
def analyze_salaries(vacancies_df):
    vacancies_df['salary'] = vacancies_df['salary'].str.replace(' - ', ' ').str.split(' ').str[0].replace('',
                                                                                                          None).astype(
        float)
    average_salary = vacancies_df['salary'].mean()
    print(f"\nСредняя зарплата: {average_salary:.2f}")

    # Распределение зарплат
    salary_distribution = vacancies_df['salary'].describe()
    print("\nРаспределение зарплат:")
    print(salary_distribution)
    return vacancies_df['salary']


# Функция для анализа навыков
def analyze_skills(vacancies_df):
    skills_series = vacancies_df['skills'].str.split(', ').explode()
    top_skills = skills_series.value_counts().head(10)
    print("\nТоп-10 наиболее распространенных навыков:")
    print(top_skills)
    return top_skills


# Функция для анализа уровней опыта
def analyze_experience(vacancies_df):
    experience_counts = vacancies_df['experience'].value_counts()
    print("\nКоличество вакансий по уровням опыта:")
    print(experience_counts)
    return experience_counts


# Функция для анализа зарплат по уровням опыта
def analyze_salaries_by_experience(vacancies_df):
    vacancies_df['salary'] = vacancies_df['salary'].fillna('').astype(str)

    # Предварительная обработка столбца зарплат
    vacancies_df['salary'] = (
        vacancies_df['salary']
        .str.replace(' - ', ' ')
        .str.split(' ')
        .str[0]
        .replace('', None)
        .astype(float)
    )

    vacancies_df = vacancies_df.dropna(subset=['salary'])

    salary_by_experience = vacancies_df.groupby('experience')['salary'].mean()
    print("\nСредняя зарплата по уровням опыта:")
    print(salary_by_experience)
    return salary_by_experience


# Функция для анализа распределения вакансий по зарплатам
def analyze_salary_distribution(vacancies_df):
    salary_bins = [0, 30000, 60000, 90000, 120000, float('inf')]
    salary_labels = ['0-30k', '30k-60k', '60k-90k', '90k-120k', '120k+']
    vacancies_df['salary_category'] = pd.cut(vacancies_df['salary'], bins=salary_bins, labels=salary_labels)

    salary_distribution = vacancies_df['salary_category'].value_counts()
    print("\nРаспределение вакансий по зарплатным категориям:")
    print(salary_distribution)
    return salary_distribution


# Функция для визуализации данных
def visualize_data(vacancies_by_city, salary_series):
    # Визуализация количества вакансий по регионам
    plt.figure(figsize=(10, 6))
    vacancies_by_city.head(10).plot(kind='bar')
    plt.title('Количество вакансий по регионам')
    plt.xlabel('Регион')
    plt.ylabel('Количество вакансий')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Визуализация распределения зарплат
    plt.figure(figsize=(10, 6))
    salary_series.plot(kind='hist', bins=30)
    plt.title('Распределение зарплат')
    plt.xlabel('Зарплата')
    plt.ylabel('Количество вакансий')
    plt.tight_layout()
    plt.show()


def main(db_url: str):
    vacancies_df = load_vacancies(db_url)

    if vacancies_df is not None and not vacancies_df.empty:
        # Анализ данных
        vacancies_by_city, _ = analyze_statistics(vacancies_df)
        salary_series = analyze_salaries(vacancies_df)
        analyze_skills(vacancies_df)
        analyze_experience(vacancies_df)
        analyze_salaries_by_experience(vacancies_df)
        analyze_salary_distribution(vacancies_df)

        # Визуализация данных
        visualize_data(vacancies_by_city, salary_series)


if __name__ == "__main__":
    url = input("Введите имя базы данных (Например, sqlite.db): ")
    main(url)
