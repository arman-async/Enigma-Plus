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


class Password:
    def __init__(self, password: str, BaseCharacters: Characters) -> None:
        """
            Example:
            >>> chars = export_base_string_from_file("32.rotors")
            >>> chars = Characters(chars)
            >>> password = Password('123456', chars)

        """
        self.password = password
        self.BaseCharacters = BaseCharacters
        validation = self.validate()
        if not(validation is True):
            raise ValueError(f"Password is not valid: {password}, The {validation} character does not exist in the bit")
        
    def validate(self) -> bool| str:
        if len(self.password) > len(self.BaseCharacters):
            raise ValueError(f"Password length is too long: {len(self.password)} > {len(self.BaseCharacters)}")
        
        for char in self.password:
            if char not in self.BaseCharacters.char:
                return char
        return True
    
    def export_index_chars(self) -> List[int]:
        return [self.BaseCharacters.get_index(char) for char in self.password]
    
    def export_index_chars_formt(self) -> List[List]:
        ""
        len_password = len(self)
        len_base = len(self.BaseCharacters)
        result = [1]*len_base
        result[len_base - len_password: ] = [self.BaseCharacters.get_index(char) for char in self.password]
        return result


    def __str__(self) -> str:
        return self.password
    
    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<length: {len(self.password)} - {self.password}>'
    
    def __len__(self) -> int:
        return len(self.password)
    

class Rotor:
    def __init__(
            self,
            rotor: str,
            characters: Characters,
            offset: int = 0,
            rotate_count: int = 1,
            
    ) -> None:
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
    def __init__(
            self,
            characters:Characters,
            rotors: List[Rotor],
            password: Password,
            reflector:Reflector=None
        ) -> None:
        """
            Exmple:
            >>> from engima import Enigma
            >>> from base64 import b64decode, b64encode
            >>> password = '123456'
            >>> rotors, characters, password = load_rotor_file(file_rotors, password)
            >>> enigma = Enigma(characters, rotors, password)
            >>> data = "<<String>>"
            >>> data = b64encode(data.encode('utf-8')).decode('utf-8')
            >>> data_encrypt = enigma.encrypt(str(data))
            >>> data_decrypt = enigma.decrypt(data_encrypt)
        """
        self.characters: Characters = characters
        self.rotors: List[Rotor] = rotors.copy()
        self.rotors_position_init_status: Tuple = tuple(rotor._position for rotor in self.rotors)
        self.reflector: Reflector = reflector if reflector else Reflector(characters)
        self.password: Password = password
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


def export_base_string_from_file(file_base: Path) -> str:
    with open(file_base, 'r') as f:
        first_line = f.readline()
        return first_line.split(';')[0]


def load_rotor_file(file_rotors: Path, password: Password| str) -> Tuple[List[Rotor], Characters, Password]:
    """
        Example:
        >>> password = '123456'
        >>> rotors, characters, password = load_rotor_file(file_rotors, password)
        >>> Enigma(characters, rotors, password)
        
        @param file_rotors: Path\
              A file containing a string of rotors\
              you can create your own rotor with the script (generate_rotors.py --help).
        
        @param password: Password\
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
    if isinstance(password, str):
        password = Password(password, characters)
    password_list = password.export_index_chars_formt()
    
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
    return (rotors, characters, password)


def create_enigma(file_rotors: Path, password: str) -> Enigma:
    """
        Example:
        >>> password = '123456'
        >>> enigma = create_enigma(file_base, file_rotors, password)
        >>> enigma
        <enigma.enigma.Enigma object at 0x7f5e9e9b9f10>

        @param file_base: Path\
              A file containing a string of characters\
              you can create your own characters with the script (generate_characters.py --help).

        @param password: str\
            - Your password\
            Your password must consist of your base characters (by default BASE64)

    """
    characters = export_base_string_from_file(file_rotors)
    _password = Password(password, Characters(characters))
    rotors, characters, password = load_rotor_file(file_rotors, _password)
    return Enigma(characters, rotors, _password)



if __name__ == "__main__":
    print('for use please "from enigma import Enigma"')
    # print('run with "python -m enigma"')
    print('for test please use "pytest test_enigma.py"')
