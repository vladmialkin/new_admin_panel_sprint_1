import logging
import os
from dotenv import load_dotenv
import sqlite3
from dataclasses import fields, astuple
from typing import List, Optional
from contextlib import contextmanager
import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.rows import dict_row
from schemas import (
    Person as PersonSchema,
    Genre as GenreSchema,
    GenreFilmWork as GenreFilmWorkSchema,
    PersonFilmWork as PersonFilmWorkSchema,
    FilmWork as FilmWorkSchema,
)

load_dotenv()

logging.basicConfig(level=logging.INFO, filename="py_log.log", filemode="w",
                    format="%(asctime)s %(levelname)s %(message)s")

SIZE = 10


@contextmanager
def open_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        logging.info("Creating connection")
        yield conn.cursor()
    finally:
        logging.info("Closing connection")
        conn.commit()
        conn.close()


@contextmanager
def closing(thing):
    try:
        yield thing
    finally:
        thing.close()


class PostgresSaver:
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn

    def save_all_data(self, data: List[dict]) -> None:
        """Функция добавляет данные в postgres."""
        with self.pg_conn.cursor() as cursor:
            for table in data:
                try:
                    table_str = table.get('table')
                    schema = table.get('schema')
                    data = table.get('data')
                    # self._clear_data_table(table_str)
                    flag = self._check_table_values(cursor=cursor, table=table_str)

                    if flag:
                        logging.info("Данные уже загружены")
                        print("Данные уже загружены")
                        return

                    query = self._creating_query(table=table_str, schema=schema, data=data)
                    cursor.execute(query)
                    self.pg_conn.commit()

                except Exception as e:
                    self.pg_conn.rollback()
                    logging.error(e)
                    return
            logging.info('Данные добавлены в бд.')
            print('Данные добавлены в бд.')

    def _check_table_values(self, cursor: psycopg.cursor, table: str) -> Optional[str]:
        """Функция проверяет на наличие данных в таблице postgres."""
        cursor.execute(f"SELECT id FROM {table} LIMIT 1")
        value = cursor.fetchone()
        return value

    def _creating_query(self, table: str, schema, data) -> str:
        """Функция создает запрос для бд postgres."""
        column_names = [field.name for field in fields(schema)]
        column_names_str = ', '.join(column_names)
        col_count = ', '.join(['%s'] * len(column_names))
        bind_values = ','.join(
            self.cursor.mogrify(f"({col_count})", astuple(row)) for row in data)

        query = (f'INSERT INTO {table} ({column_names_str}) VALUES {bind_values} '
                 f'ON CONFLICT (id) DO NOTHING')
        return query

    def _clear_data_table(self, table: str) -> None:
        """Функция удаляет данные из таблицы."""
        self.cursor.execute(f"TRUNCATE {table} CASCADE")
        logging.info(f"Данные удалены из таблицы {table}")


class SQLiteLoader:
    def __init__(self, cursor):
        self.cursor = cursor
        self.tables = [('genre', GenreSchema),
                       ('person', PersonSchema),
                       ('film_work', FilmWorkSchema),
                       ('genre_film_work', GenreFilmWorkSchema),
                       ('person_film_work', PersonFilmWorkSchema),
                       ]

    def load_movies(self) -> List[dict]:
        """Функция считывает данные из sqlite3."""
        with closing(self.cursor) as cursor:
            try:
                data = list()
                for table, schema in self.tables:
                    cursor.execute(f"SELECT * FROM {table}")
                    while True:
                        data_table = [schema(*row) for row in cursor.fetchmany(SIZE)]
                        if data_table:
                            data.append({'table': table, 'schema': schema, 'data': data_table})
                        else:
                            break
                return data
            except sqlite3.IntegrityError:
                logging.error("Ошибка при загрузке данных из sqlite.")
            except Exception as e:
                logging.error(e)


def load_from_sqlite(connection: sqlite3.Cursor, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {
        'dbname': os.environ.get('DB_NAME'),
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('PASSWORD'),
        'host': os.environ.get('HOST'),
        'port': os.environ.get('PORT')
    }
    with open_db(file_name='db.sqlite') as sqlite_cursor, psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_cursor, pg_conn)
