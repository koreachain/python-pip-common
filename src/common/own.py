#!/usr/bin/env python3

import logging
import os
import socket

import fastlogging
import requests

from common import cmd

if "root" in fastlogging.domains:
    log = fastlogging.domains["root"]
else:
    log = logging.getLogger(__name__)

# From `man hostnamectl`: Currently, the following chassis types are defined: "desktop",
# "laptop", "convertible", "server", "tablet", "handset", "watch", "embedded", as well
# as the special chassis types "vm" and "container" for virtualized systems that lack an
# immediate physical chassis.
chassis: str
__out = cmd.run(["hostnamectl"], env={**os.environ, "LC_ALL": "C"}).stdout.splitlines()
for line in __out:
    if "Chassis" in line:
        chassis = line.split()[1]
        break
    elif "Virtualization:" in line:
        chassis = "vm"
        break
else:
    chassis = "unknown"

hostname: str = socket.gethostname()

ip: str
country: str


def _ip() -> str:
    global ip
    try:
        reply = requests.get("https://checkip.amazonaws.com", timeout=5)
    except Exception as e:
        log.warning(f"{type(e).__name__}: {e}, fallback to Cloudflare")
        reply = requests.get("https://icanhazip.com", timeout=15)

    ip = reply.text.strip()

    return ip


def _country() -> str:
    global country
    reply = requests.get("https://api.iplocation.net", params={"ip": __getattr__("ip")})
    country = reply.json()["country_code2"]

    return country


def __getattr__(name: str):
    if name == "ip":
        return _ip()
    elif name == "country":
        return _country()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
