# Enigma Plus
### An attempt to modernize the Enigma cryptosystem

- You can make the device with your favorite characters
  - (Base 64 characters are used by default)
- You can easily make as many rotors as you want
  - `$ python generate_rotors.py --help`
- Your password has a lot to do with encryption
    - The rotors will change with your password
    - Your password determines the rotation size of each rotor


### User
```
from enigma.enigma import Enigma, load_rotor_file
password = '123456'
rotors, characters, password = load_rotor_file(file_rotors, password)
enigma = Enigma(characters, rotors, password)
data = "<<String>>"
data = b64encode(data.encode('utf-8')).decode('utf-8')
data_encrypt = enigma.encrypt(str(data))
data_decrypt = enigma.decrypt(data_encrypt) 
```



This document will be completed soon...
