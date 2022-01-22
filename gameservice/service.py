from dataclasses import dataclass

from persistence.sqlite import SQLite3Db

@dataclass
class Service:
    repository: SQLite3Db