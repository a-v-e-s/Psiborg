#!/bin/bash

touch db.sqlite

sqlite3 db.sqlite "BEGIN TRANSACTION;
    CREATE TABLE Tests(
    Number INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL,
    Mood TEXT NOT NULL,
    Type TEXT NOT NULL,
    CSV_filepath TEXT NOT NULL
    );
    COMMIT;"