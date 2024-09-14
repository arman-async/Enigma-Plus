from typing import *
from array import array
from pathlib import Path
from bidict import bidict
import base64
import sys
import time

class Characters:
    def __init__(self, chars: str) -> None:
        # Speed ​​is important from memory
        self.char = dict({char:index for index, char in enumerate(chars)})
        self.inv = dict({index:char for index, char in enumerate(chars)})

    def get_index(self, char: str) -> int:
        return self.char[char]

    def get_char(self, index: int) -> str:
        return self.inv[index] 

    def export_str(self) -> str:
        return "".join(self.char.keys())

    def export_list(self) -> List[str]:
        return list(self.char.keys())
    
    def export_generator(self) -> Generator[str, None, None]:
        for char in self.char.keys():
            yield char
    
    def __len__(self) -> int:
        return len(self.char)
    
    def __str__(self) -> str:
        return f'{self.char.keys()}'
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<length: {len(self.char)} - {self.char}>'


class Rotor:
    def __init__(
            self,
            rotor: str,
            characters: Characters,
            offset: int = 0,
            rotate_count: int = 1,
            
    ) -> None:
        "Waring: Don't set value(offset) to anything but 0 for now"
        self.rotor = Characters(rotor[offset:] + rotor[:offset])
        self.characters: Characters = characters
        self._position: int = 0
        self._rotate_count: int = rotate_count
        self._rotor_len: int = len(self.rotor)

    
    def rotate(self) -> bool:
        # We perform rotation operations at a very low cost
        old_position = self._position
        self._position = (self._position + self._rotate_count) % self._rotor_len
        return (self._position < old_position)


    def __getitem__(self, input: int) -> str:
        return self.rotor[input]
    
    def input_form_left(self, input: int| str) -> str:
        if isinstance(input, int):
            index = (input + self._position)
        elif isinstance(input, str):
            index = (self.characters.get_index(input) + self._position)
        else:
            raise TypeError(f"input must be int or str, not {type(input)}")
        index = index % self._rotor_len
        return self.rotor.get_char(index)

    def input_form_right(self, input: int| str) -> str:
        if isinstance(input, int):
            index = (input + self._position)
        elif isinstance(input, str):
            index = (self.rotor.get_index(input) + self._position)
        else:
            raise TypeError(f"input must be int or str, not {type(input)}")
        index = index % self._rotor_len
        return self.characters.get_char(index)
    
    def __str__(self) -> str:
        return\
        f"{self.__class__.__name__}< "\
        f"offset: {self.offset} - "\
        f"position: {self._position} - "\
        f"rotate_count: {self._rotate_count} - "\
        f"rotor_len: {self._rotor_len} >"


class Reflector:
    def __init__(self, chars: Characters) -> None:
        self.chars: Characters = chars
    
    def __getitem__(self, input: int | str) -> str:
        if isinstance(input, int):
            index = input
        elif isinstance(input, str):
            index = self.chars.get_index(input)
        else:
            raise TypeError(f"input must be int or str, not {type(input)}")
        return self.chars.get_char(len(self.chars) - index - 1)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<length: {len(self.chars)}>"
    
    def __len__(self) -> int:
        return len(self.chars)


class Enigma:
    def __init__(self, characters:Characters, rotors: List[Rotor], password: str, reflector:Reflector=None) -> None:
        self.characters: Characters = characters
        self.rotors: List[Rotor] = rotors.copy()
        self.rotors_position_init_status: Tuple = tuple(rotor._position for rotor in self.rotors)
        self.reflector: Reflector = reflector if reflector else Reflector(characters)
        self.password: str = password
        self._rotor_count: int = len(self.rotors)

    def __str__(self) -> str:
        return f"{self.__class__.__name__}<rotor_count: {self._rotor_count}>"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __len__(self) -> int:
        return self._rotor_count

    def _rotorize_from_left(self, char: str) -> str:
        char = char
        for rotor in self.rotors:
            char = rotor.input_form_left(char)
        return char
    
    def _rotorize_from_right(self, char: str) -> str:
        char = char
        for rotor in reversed(self.rotors):
            char = rotor.input_form_right(char)
        return char

    def rotors_reset(self) -> None:
        for rotor, position in zip(self.rotors, self.rotors_position_init_status):
            rotor._position = position
    
    def encrypt(self, string: str) -> str:
        """
            encrypt(string) -> string

            Encrypts the given string using the Enigma machine
                and returns the encrypted string

            ### warning: 
                #### Do not use this function to encrypt data larger than 8 kilobytes!
                    #### For large data you can use (self.encrypt_generator) and (self.encrypt_generator_chunk).
        """
        # Warning: This function has been used a lot in this class!
        #   You should never call function (self.rotors_reset()) in this function
        result: array = array('i', [0] * len(string))
        for _, char in enumerate(string):
            rotorize_go = self._rotorize_from_left(char)
            reflect = self.reflector[rotorize_go]
            rotorize_back = self._rotorize_from_right(reflect)
            result[_] = self.characters.get_index(rotorize_back)
        return ''.join(
            self.characters.get_char(index)
            for index in result
        )
    

    def encrypt_generator(self, string: str) -> Generator[str, None, None]:
        for char in string:
            rotorize_go = self._rotorize_from_left(char)
            reflect = self.reflector[rotorize_go]
            rotorize_back = self._rotorize_from_right(reflect)
            yield rotorize_back

    def encrypt_generator_chunk(self, string: str, chunk_size: int=128) -> Generator[str, None, None]:
        for index in range(0, len(string), chunk_size):
            yield self.encrypt(string[index:index+chunk_size])
    
    def decrypt(self, string: str) -> str:
        """
            decrypt(string) -> string

            Dencrypts the given string using the Enigma machine
                and returns the dencrypted string

            ### warning: 
                #### Do not use this function to dencrypt data larger than 8 kilobytes!
                    #### For large data you can use (self.decrypt_generator) and (self.decrypt_generator_chunk).
        """
        self.rotors_reset()
        return self.encrypt(string)
    
    def decrypt_generator(self, string: str) -> Generator[str, None, None]:
        self.rotors_reset()
        return self.encrypt_generator(string)
    
    def decrypt_generator_chunk(self, string: str, chunk_size: int=128) -> Generator[str, None, None]:
        self.rotors_reset()
        return self.encrypt_generator_chunk(string, chunk_size)



def load_rotor_file(file_rotors: Path, password: str) -> Tuple[List[Rotor], Characters, str]:
    """
        Example:
        >>> password = '123456'
        >>> rotors, characters, password = load_rotor_file(file_rotors, password)
        >>> Enigma(characters, rotors, password)
        
        @param file_rotors: Path\
              A file containing a string of rotors\
              you can create your own rotor with the script (generate_rotors.py --help).
        
        @param password: str\
            - Your password\
            Your password must consist of your base characters (by default BASE64)


    """
    rotors_str: List[str] = []
    with open(file_rotors, 'r') as f:
        data: List[str] = "".join(f.readlines()).split(';')
        Base = data[0]
        data: List[str] = data[1:]
        base_len = len(Base)
        for rotor in data:
            rotor_len = len(rotor)
            if rotor_len == 0:
                continue
            elif rotor_len != base_len:
                raise ValueError(f"rotor length is not consistent: {rotor_len} != {base_len}")
            rotors_str.append(rotor)

    characters = Characters(Base)

    password_list = [
        characters.get_index(char)
        for char in password
    ]
    while len(password_list) < len(rotors_str):
        password_list.insert(0, 0)
    
    rotors: List[Rotor] = []
    for rotor_str in rotors_str:
        pass_char_index: int = password_list.pop(0)
        rotor = Rotor(
            rotor_str,
            offset=pass_char_index,
            characters=characters,
            rotate_count=pass_char_index,
        )
        rotors.append(rotor)
    return (rotors, characters)


if __name__ == "__main__":
    # # TEST Devpelopment
    password = "ENIGMa"
    rotors, characters = load_rotor_file(r"32.rotors", password)
    enigma = Enigma(characters, rotors.copy(), password)
    data = "Hello Enigma "
    print(f'data: {data}')

    b64 = base64.b64encode(data.encode('utf-8')).decode('utf-8')
    print(f'- base64: {b64}')

    start_time = time.time()
    data_encrypt = enigma.encrypt(b64)
    print(f'-- encrypt: {data_encrypt}')

    data_decrypt = enigma.decrypt(data_encrypt)
    end_time = time.time()
    print(f'-- decrypt: {data_decrypt}')

    text = base64.b64decode(data_decrypt.encode('utf-8')).decode('utf-8')
    print(f'text: {text}')
    print(f'length: {len(data)}')
    print(f'elapsed time: {end_time - start_time}')

    input('Press Enter to exit...')
