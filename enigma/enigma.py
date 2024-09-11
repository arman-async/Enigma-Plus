from typing import *
import time

class Rotor:
    def __init__(self, rotor: List[str], offset: int = 0, rotate_count: int = 1) -> None:
        self.rotor: List[str] = rotor
        self.offset: int = offset
        self._position: int = offset
        self._rotate_count: int = rotate_count
        self._rotor_len: int = len(self.rotor)
    
    def rotate(self) -> None:
        if self._position == (self._rotor_len - 1):
            self._position = 0
        else:
            self._position = (self._position + self._rotate_count) % len(self.rotor)

    def __getitem__(self, index: int) -> str:
        return self.rotor[(self._position + index) % len(self.rotor)]

    def __str__(self) -> str:
        return\
        f"{self.__class__.__name__}< "\
        f"offset: {self.offset} - "\
        f"position: {self._position} - "\
        f"rotate_count: {self._rotate_count} - "\
        f"rotor_len: {self._rotor_len} >"
    