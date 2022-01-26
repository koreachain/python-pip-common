#!/usr/bin/env python3

import base64
import logging
import os
import sys

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from pwinput import pwinput


class Secret:
    """Hide repr() for secrets in debug logs."""

    def __init__(self, msg: str | bytes) -> None:
        self.msg: str | bytes = msg

    def __repr__(self) -> str:
        return 'Secret(msg="***")'

    def reveal(self) -> str | bytes:
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


def vault(ocid: str) -> str:
    """Copyright 2020 Oracle A-Team, Apache License v2.0"""
    with open(ocid) as fd:
        secret_id = fd.read().strip()

    # only load if needed, it may take around 2 seconds in a modern system
    import oci

    # oci outputs protected ocids on debug level, may also print on others
    logging.getLogger("oci").setLevel(logging.ERROR)

    # this will hit the auth service in the region the instance is running
    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()

    # config not needed as region and tenancy are obtained from the Signer
    secret_client = oci.secrets.SecretsClient(config={}, signer=signer)

    def read_secret_value(secret_client, secret_id):
        response = secret_client.get_secret_bundle(secret_id)
        base64_Secret_content = response.data.secret_bundle_content.content
        base64_secret_bytes = base64_Secret_content.encode("ascii")
        base64_message_bytes = base64.b64decode(base64_secret_bytes)
        secret_content = base64_message_bytes.decode("ascii")
        return secret_content

    return read_secret_value(secret_client, secret_id)


if __name__ == "__main__":

    def mlinput() -> str:
        print("Token (empty line to confirm):")
        msg = []
        for line in iter(input, ""):
            msg.append(line.strip())
        return "".join(msg)

    if len(sys.argv) < 2 or sys.argv[1].lstrip("-") in ("h", "help"):
        print(str(__doc__).lstrip())
        sys.exit(0)

    if sys.argv[1] == "new-salt":
        salt = os.urandom(16)
        print(yaml.dump(salt))
        sys.exit(0)

    if sys.argv[1] == "-s":
        salt = base64.urlsafe_b64decode(sys.argv[2])
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
