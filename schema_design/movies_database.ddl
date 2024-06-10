CREATE SCHEMA IF NOT EXISTS content;

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT not null,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre(
id uuid PRIMARY KEY,
name VARCHAR(30),
description TEXT,
created timestamp with time zone,
modified timestamp with time zone);

CREATE TABLE IF NOT EXISTS content.genre_film_work(
id uuid PRIMARY KEY,
genre_id uuid NOT NULL REFERENCES content.genre(id),
film_work_id uuid NOT NULL REFERENCES content.film_work(id),
created timestamp with time zone);

CREATE TABLE IF NOT EXISTS content.person(
id uuid PRIMARY KEY,
full_name TEXT NOT NULL,
created timestamp with time zone,
modified timestamp with time zone);

CREATE TABLE IF NOT EXISTS content.person_film_work(
id uuid PRIMARY KEY,
person_id uuid NOT NULL REFERENCES content.person(id),
film_work_id uuid NOT NULL REFERENCES content.film_work(id),
role VARCHAR(20),
created timestamp with time zone);