import pytest
import os
from uuid import uuid4
from base64 import b64decode, b64encode
try:
    from .enigma import Enigma,Password, load_rotor_file, create_enigma
except ImportError:
    from enigma import Enigma,Password, load_rotor_file, create_enigma
from generate_rotors import random_rotor, BASE64

@pytest.fixture(scope='session')
def enigma():
    temp_file = f'TEST.rotors'
    with open(temp_file, 'w') as f:
        f.write(f'{BASE64};')
        for _ in range(28):
            f.write(f'{random_rotor(BASE64)};')
    password = '123456'
    rotors, characters, password = load_rotor_file(temp_file, password)
    enigma = Enigma(characters, rotors, password)
    yield enigma

def test_encrypt(enigma: Enigma):
    data = uuid4()
    data = b64encode(data.bytes).decode('utf-8')
    data_encrypt = enigma.encrypt(str(data))
    data_decrypt = enigma.decrypt(data_encrypt)
    assert data == data_decrypt, f"encryption and decryption failed,"\
        f" data: {data}, data_encrypt: {data_encrypt}, data_decrypt: {data_decrypt}"

def test_create_enigma():
    temp_file = f'TEST-CreateEngima.rotors'
    with open(temp_file, 'w') as f:
        f.write(f'{BASE64};')
        for _ in range(28):
            f.write(f'{random_rotor(BASE64)};')
    password = '123456'
    enigma = create_enigma(temp_file, password)
    assert isinstance(enigma, Enigma)
    os.remove(temp_file)

def test_encrypt_generate(enigma: Enigma):
    data = uuid4()
    data = b64encode(data.bytes).decode('utf-8')
    data_encrypt = "".join(enigma.encrypt_generator(data))
    data_decrypt = "".join(enigma.decrypt_generator(data_encrypt))
    assert data == data_decrypt, f"encryption and decryption (generator) failed,"\
        f" data: {data}, data_encrypt: {data_encrypt}, data_decrypt: {data_decrypt}"

def test_encrypt_generator_chunk(enigma: Enigma):
    data = ''.join([uuid4().hex for _ in range(100)])
    data = b64encode(data.encode('utf-8')).decode('utf-8')
    data_encrypt = "".join(enigma.encrypt_generator_chunk(data, chunk_size=11))
    data_decrypt = "".join(enigma.decrypt_generator_chunk(data_encrypt, chunk_size=17))
    assert data == data_decrypt, f"encryption and decryption (generator) failed,"\
        f" data: {data}, data_encrypt: {data_encrypt}, data_decrypt: {data_decrypt}"

    
