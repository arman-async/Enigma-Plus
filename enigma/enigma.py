from typing import *
from pathlib import Path

BASE64 = "0123456789+/ABCDEFGHIJKLMNOPQRSTUVWXYZ=abcdefghijklmnopqrstuvwxyz"

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


class Reflector:
    def __init__(self, reflector: List[str]) -> None:
        self.reflector: List[str] = reflector
    
    def __getitem__(self, input: int | str) -> str:
        if isinstance(input, int):
            index = input
        elif isinstance(input, str):
            try:
                index = self.reflector.index(input)
            except ValueError:
                raise ValueError(f"{input} not in reflector")
        else:
            raise TypeError(f"input must be int or str, not {type(input)}")
        
        return self.reflector[len(self.reflector) - index - 1]
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}<length: {len(self.reflector)}>"
    
    def __len__(self) -> int:
        return len(self.reflector)


class Enigma:
    def __init__(self, rotors: List[Rotor], password: str, reflector:Reflector=None) -> None:
        self.rotors: List[Rotor] = rotors
        self.reflector: Reflector = reflector if reflector else Reflector(BASE64)
        self.password: str = password
        self._rotor_count: int = len(self.rotors)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<rotor_count: {self._rotor_count}>"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self) -> int:
        return self._rotor_count

    def encrypt(self, string: str) -> str:
        pass


def load_rotor_file(file_rotors: Path, password: str, Base:List[str]) -> List[Rotor]:

    rotors_str: List[str] = []
    with open(file_rotors, 'r') as f:
        data: List[str] = "".join(f.readlines()).split(';')
        last_len = len(data[0])
        for rotor in data:
            if len(rotor) == 0:
                continue
            elif len(rotor) != last_len:
                raise ValueError(f"rotor length is not consistent: {len(rotor)} != {last_len}")
            last_len = len(rotor)
            rotors_str.append(rotor)

    password_list = [
        Base.index(char)
        for char in password
    ]
    while len(password_list) < len(rotors_str):
        password_list.insert(0,1)
    
    return [
        Rotor(rotor_str, rotate_count=password_list.pop(0))
        for rotor_str in rotors_str
    ]


if __name__ == "__main__":
    # TEST Devpelopment
    rotors = load_rotor_file("new.rotors", "ENIGMA", BASE64)
    for rotor in rotors:
        print(rotor)