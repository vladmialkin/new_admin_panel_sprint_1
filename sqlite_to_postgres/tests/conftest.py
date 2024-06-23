import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

import psycopg
import pytest
from psycopg import ClientCursor
from psycopg.rows import dict_row

from dotenv import load_dotenv

load_dotenv()


@contextmanager
def open_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        yield conn.cursor()
    finally:
        conn.commit()
        conn.close()


@contextmanager
def closing(thing):
    try:
        yield thing
    finally:
        thing.close()


dsl = {
    'dbname': os.environ.get('DB_NAME'),
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('PASSWORD'),
    'host': os.environ.get('HOST'),
    'port': os.environ.get('PORT')
}


@pytest.fixture
def sqlite_cursor():
    with open_db(file_name='db.sqlite') as sqlite_conn:
        with closing(sqlite_conn) as sqlite_cursor:
            yield sqlite_cursor


@pytest.fixture
def postgres_cursor():
    with psycopg.connect(**dsl, row_factory=dict_row, cursor_factory=ClientCursor) as pg_conn:
        with pg_conn.cursor() as postgres_cursor:
            yield postgres_cursor
