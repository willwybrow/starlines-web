from dataclasses import dataclass


@dataclass(init=True, repr=True, eq=True, order=True, frozen=True)
class Point:
    x: int
    y: int