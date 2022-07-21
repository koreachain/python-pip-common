#!/usr/bin/env python3

import socket

from common import cmd

# From `man hostnamectl`: Currently, the following chassis types are defined: "desktop",
# "laptop", "convertible", "server", "tablet", "handset", "watch", "embedded", as well
# as the special chassis types "vm" and "container" for virtualized systems that lack an
# immediate physical chassis.
__output: list[str] = cmd.run("LC_ALL=C hostnamectl").stdout.splitlines()
for line in __output:
    if "Chassis" in line:
        chassis = line.split()[-1]
        break
    elif "Virtualization:" in line:
        chassis = "vm"
        break
else:
    chassis = "unknown"

hostname: str = socket.gethostname()
