from flask import g

from persistence.sqlite import SQLite3Db


def get_db():
    if "db" not in g:
        g.db = SQLite3Db()

    return g.db


def close_db():
    db = g.pop("db", None)

    if db is not None:
        db.close()