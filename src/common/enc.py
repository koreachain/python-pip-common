#!/usr/bin/env python3
"""
Usage:
  enc.py new-salt
  enc.py (-s <salt> | -c <conf>) (encrypt | multi-encrypt)
  enc.py (-s <salt> | -c <conf>) decrypt [<message>]

Options:
  -h, --help
  -s, --salt <salt:str>
  -c, --conf <conf:str>

Commands:
  new-salt                   Generate a new salt.
  encrypt                    Encrypt a message.
  multi-encrypt              Encrypt multiple messages.
  decrypt [<message:str>]    Decrypt a message.
"""

import base64
import logging
import os
import sys
from typing import Union

import yaml
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from getch import getch

from common import arg

Message = Union[str, bytes, list[str], list[bytes]]


class Secret:
    """Hide repr() for secrets in debug logs."""

    def __init__(self, msg: Message) -> None:
        self.msg: Message = msg

    def __repr__(self) -> str:
        return 'Secret(msg="***")'

    def reveal(self) -> Message:
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


def prompt_for_secret(prompt: str = "Secret: ") -> str:
    """Securely prompt the user for a secret."""

    print(prompt, end="", flush=True, file=sys.stderr)
    buf = b""
    while True:
        ch = getch().encode()
        if ch in {b"\n", b"\r", b"\r\n"}:
            print("", file=sys.stderr)
            break
        elif ch == b"\x03":  # Ctrl+C
            return ""  # or raise KeyboardInterrupt
        elif ch in {b"\x08", b"\x7f"}:  # Backspace
            buf = buf[:-1]
            print(
                f'\r{(len(prompt)+len(buf)+1)*" "}\r{prompt}{"*" * len(buf)}',
                end="",
                flush=True,
                file=sys.stderr,
            )
        else:
            buf += ch
            print("*", end="", flush=True, file=sys.stderr)

    return buf.decode()


def vault(ocid: str) -> str:
    """Copyright 2020 Oracle A-Team, Apache License v2.0"""

    try:
        import oci
    except ImportError:
        sys.exit("Missing required module: oci>=2.52.1.")

    with open(ocid) as fd:
        secret_id = fd.read().strip()

    # only load if needed, it may take around 2 seconds in a modern system
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


def _mlinput() -> str:
    print("Token (empty line to confirm):", file=sys.stderr)
    msg = []
    for line in iter(input, ""):
        msg.append(line.strip())
    return "".join(msg)


def main():
    if args.new_salt:
        salt = os.urandom(16)
        print(yaml.dump(salt))
        sys.exit(0)

    if args.salt:
        salt = base64.urlsafe_b64decode(args.salt)
    elif args.conf:
        with open(args.conf) as fd:
            data = yaml.safe_load(fd)
        salt = data["salt"]
    else:
        sys.exit("Missing required option: -s|--salt or -c|--conf")

    if sys.stdin.isatty():
        password = prompt_for_secret(prompt="Password: ")
    else:
        if not args.decrypt or not args.message:
            sys.exit("Error: stdin must be a TTY unless decrypting a given message.")
        password = sys.stdin.read().strip()
    crypto = Crypto(salt, password)
    del salt, password

    if args.encrypt:
        message = prompt_for_secret(prompt="Message: ")
        token = crypto.encrypt(message.encode())
        print(yaml.dump(token))
    elif args.multi_encrypt:
        print("Prompt for multiple messages. Press Ctrl+C to stop.", file=sys.stderr)
        x = 1
        while True:
            message = prompt_for_secret(prompt=f"[{x}] Message: ")
            token = crypto.encrypt(message.encode())
            print(yaml.dump(token))
            x += 1
    elif args.decrypt:
        b64 = "".join(args.message.split()) if args.message else _mlinput()
        token = base64.urlsafe_b64decode(b64)
        print(crypto.decrypt(token).reveal())


if __name__ == "__main__":
    args = arg.parse(__doc__)

    main()
