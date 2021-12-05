#!/usr/bin/env python3
"""
Usage: enc.py options command [arguments]

Options:
  -s salt
  -c conf

Commands:
  new-salt
  encrypt [message]
  decrypt [message]
"""


import base64
import os
import sys

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pwinput import pwinput


class Secret:
    """Hide repr() for secrets in debug logs."""

    def __init__(self, string: str) -> None:
        self.msg: str = string

    def __repr__(self) -> str:
        return 'Secret(msg="***")'

    def reveal(self) -> str:
        """Return message whenever requested."""
        return self.msg


class Crypto(Fernet):
    """Allow the use of passwords with Fernet."""

    def __init__(self, salt: bytes, password: str) -> None:
        kdf = PBKDF2HMAC(algorithm=SHA256(), length=32, salt=salt, iterations=3200000)
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        super().__init__(key)

    def decrypt(self, *args, **kwargs) -> Secret:
        """Decrypt message and wrap as Secret()."""
        return Secret(super().decrypt(*args, **kwargs).decode())


if __name__ == "__main__":

    def mlinput() -> str:
        msg = [input("Token: ")]
        for line in iter(lambda: input("  ...: "), ""):
            msg.append(line.strip())
        return "".join(msg)

    if len(sys.argv) < 2 or sys.argv[1].lstrip("-") in ("h", "help"):
        print(str(__doc__).lstrip())
        sys.exit(0)

    if sys.argv[1] == "new-salt":
        rand = os.urandom(16)
        salt = base64.urlsafe_b64encode(rand).decode()
        print(salt)
        sys.exit(0)

    if sys.argv[1] == "-s":
        salt = sys.argv[2].encode()
    elif sys.argv[1] == "-c":
        with open(sys.argv[2]) as fd:
            data = yaml.safe_load(fd)
        salt = data["salt"]
    else:
        sys.exit("Missing required option: -s salt|-c conf")

    password = pwinput()
    crypto = Crypto(salt, password)
    del salt, password

    if sys.argv[3] == "encrypt":
        msg = sys.argv[4] if len(sys.argv) > 4 else pwinput(prompt="Message: ")
        token = crypto.encrypt(msg.encode())
        print(yaml.dump(token))
    elif sys.argv[3] == "decrypt":
        b64 = "".join(sys.argv[4].split()) if len(sys.argv) > 4 else mlinput()
        token = base64.urlsafe_b64decode(b64)
        print(crypto.decrypt(token).reveal())
