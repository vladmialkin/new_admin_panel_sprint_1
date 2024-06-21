import sqlite3
from dataclasses import fields, astuple
import psycopg
from psycopg import ClientCursor, connection as _connection
from psycopg.errors import ForeignKeyViolation
from psycopg.rows import dict_row
from schemas import (
    Person as PersonSchema,
    Genre as GenreSchema,
    GenreFilmWork as GenreFilmWorkSchema,
    PersonFilmWork as PersonFilmWorkSchema,
    FilmWork as FilmWorkSchema,
)


class PostgresSaver:
    def __init__(self, pg_conn):
        self.pg_conn = pg_conn
        self.cursor = pg_conn.cursor()

    def save_all_data(self, data):
        with self.pg_conn:
            for table in data:
                try:
                    self.cursor.execute(f"TRUNCATE {table.get('table')} CASCADE")
                    column_names = [field.name for field in fields(table.get('schema'))]
                    column_names_str = ', '.join(column_names)
                    col_count = ', '.join(['%s'] * len(column_names))
                    bind_values = ','.join(
                        self.cursor.mogrify(f"({col_count})", astuple(row)) for row in table.get('data'))

                    query = (f'INSERT INTO {table.get('table')} ({column_names_str}) VALUES {bind_values} '
                             f'ON CONFLICT (id) DO NOTHING')
                    self.cursor.execute(query)
                    self.pg_conn.commit()
                except Exception as e:
                    self.pg_conn.rollback()
                    print(e)



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

    def load_movies(self) -> list:
        try:
            with self.connection:
                data = list()
                for table, schema in self.tables:
                    self.cursor.execute(f"SELECT * FROM {table}")
                    data_table = [schema(*row) for row in self.cursor.fetchall()]
                    data.append({'table': table, 'schema': schema, 'data': data_table})
                return data

        except sqlite3.IntegrityError:
            print("Ошибка при загрузке данных из sqlite.")


def load_from_sqlite(connection: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    postgres_saver = PostgresSaver(pg_conn)
    sqlite_loader = SQLiteLoader(connection)

    data = sqlite_loader.load_movies()
    postgres_saver.save_all_data(data)


if __name__ == '__main__':
    dsl = {'dbname': 'movies_database', 'user': 'app', 'password': '123qwe', 'host': '127.0.0.1', 'port': 5432}
    with sqlite3.connect('db.sqlite') as sqlite_conn, psycopg.connect(
            **dsl, row_factory=dict_row, cursor_factory=ClientCursor
    ) as pg_conn:
        load_from_sqlite(sqlite_conn, pg_conn)
