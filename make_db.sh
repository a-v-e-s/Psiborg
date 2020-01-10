#!/bin/bash

touch db.sqlite

sqlite3 db.sqlite "BEGIN TRANSACTION;
    CREATE TABLE Tests(
    Number INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, -- test #
    Name TEXT NOT NULL,
    Mood TEXT NOT NULL, -- description of state of mind or other conditions
    Type TEXT NOT NULL, -- test type
    CSV_filepath TEXT NOT NULL
    );
    COMMIT;"