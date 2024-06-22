import logging
import os
from dotenv import load_dotenv
import sqlite3
from dataclasses import fields, astuple
from typing import List, Optional

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


class PostgresSaver:
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn
        self.cursor = pg_conn.cursor()

    def save_all_data(self, data: List[dict]) -> None:
        """Функция добавляет данные в postgres."""
        for table in data:
            try:
                table_str = table.get('table')
                schema = table.get('schema')
                data = table.get('data')
                # self._clear_data_table(table_str)
                flag = self._check_table_values(table=table_str)

                if flag:
                    logging.info("Данные уже загружены")
                    print("Данные уже загружены")
                    return

                query = self._creating_query(table=table_str, schema=schema, data=data)
                self.cursor.execute(query)
                self.pg_conn.commit()

            except Exception as e:
                self.pg_conn.rollback()
                logging.error(e)
                return
        logging.info('Данные добавлены в бд.')
        print('Данные добавлены в бд.')

    def _check_table_values(self, table: str) -> Optional[str]:
        """Функция проверяет на наличие данных в таблице postgres."""
        self.cursor.execute(f"SELECT id FROM {table} LIMIT 1")
        value = self.cursor.fetchone()
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
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()
        self.tables = [('genre', GenreSchema),
                       ('person', PersonSchema),
                       ('film_work', FilmWorkSchema),
                       ('genre_film_work', GenreFilmWorkSchema),
                       ('person_film_work', PersonFilmWorkSchema),
                       ]

    def load_movies(self) -> List[dict]:
        """Функция считывает данные из sqlite3."""
        try:
            data = list()
            for table, schema in self.tables:
                self.cursor.execute(f"SELECT * FROM {table}")
                data_table = [schema(*row) for row in self.cursor.fetchall()]
                data.append({'table': table, 'schema': schema, 'data': data_table})
            return data
        except sqlite3.IntegrityError:
            logging.error("Ошибка при загрузке данных из sqlite.")
        except Exception as e:
            logging.error(e)


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
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
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
