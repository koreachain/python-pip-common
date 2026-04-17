#!/usr/bin/env python3

import os
import sys
from typing import Union

import yaml
from box import Box

from common import enc


def cfg(filename="./config.yml", token: Union[str, None] = None):
    with open(filename) as fd:
        conf: dict = yaml.safe_load(fd)

    secrets = None
    if (salt := conf.get("salt")) and (raw_secrets := conf.get("secrets")):
        token = token or os.environ.get("TOKEN") or enc.prompt_for_secret()
        crypto = enc.Crypto(salt, token)
        secrets = {
            k: (crypto.decrypt(v) if isinstance(v, bytes) else v) for k, v in raw_secrets.items()
        }
        del token, conf["salt"], conf["secrets"]

    return Box(conf, frozen_box=True), Box(secrets or {}, frozen_box=True)


def main():
    print(cfg(sys.argv[1]))


if __name__ == "__main__":
    main()
