import datetime
import re
import uuid

import pytest


@pytest.mark.parametrize('table', ['genre', 'person', 'film_work', 'person_film_work', 'genre_film_work'])
def test_check_tables(table, sqlite_cursor, postgres_cursor):
    sqlite_cursor.execute(f"SELECT id FROM {table} limit 1")
    sqlite_data = sqlite_cursor.fetchone()
    postgres_cursor.execute(f"SELECT id FROM {table} limit 1")
    postgres_data = postgres_cursor.fetchone()
    assert sqlite_data is not None and postgres_data is not None


@pytest.mark.parametrize('table', ['genre', 'person', 'film_work', 'person_film_work', 'genre_film_work'])
def test_check_count_person_film_work(table, sqlite_cursor, postgres_cursor):
    sqlite_cursor.execute(f"SELECT COUNT(*) FROM person_film_work")
    sqlite_count = sqlite_cursor.fetchone()[0]
    postgres_cursor.execute(f"SELECT COUNT(*) FROM person_film_work")
    postgres_count = postgres_cursor.fetchone().get('count')
    assert sqlite_count == postgres_count


@pytest.mark.parametrize('table', ['genre', 'person', 'film_work', 'person_film_work', 'genre_film_work'])
def test_check_data_person_film_work(table, sqlite_cursor, postgres_cursor):
    flag = True
    sqlite_cursor.execute(f"SELECT * FROM {table}")
    sqlite_data = sqlite_cursor.fetchall()
    postgres_cursor.execute(f"SELECT * FROM {table}")
    postgres_data = postgres_cursor.fetchall()

    pattern = r'^\d{4}-\d{2}-\d{2}'
    postgres_list = []
    sqlite_list = []
    for sqlite_row in sqlite_data:
        sqlite_row_list = []
        for sqlite_val in sqlite_row:
            if sqlite_val is not None:
                if not isinstance(sqlite_val, (int, float)):
                    if re.match(pattern, sqlite_val):
                        sqlite_val = sqlite_val[:10]
            sqlite_row_list.append(sqlite_val)
        sqlite_list.append(tuple(sqlite_row_list))

    for postgres_row in postgres_data:
        postgres_row_list = []
        for postgres_val in postgres_row.values():
            if isinstance(postgres_val, uuid.UUID):
                postgres_val = str(postgres_val)
            if isinstance(postgres_val, datetime.datetime):
                postgres_val = postgres_val.strftime('%Y-%m-%d')
            postgres_row_list.append(postgres_val)
        postgres_list.append(tuple(postgres_row_list))
    assert sqlite_list == postgres_list
