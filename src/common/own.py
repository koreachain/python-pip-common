#!/usr/bin/env python3

import os
import socket

from common import cmd

# From `man hostnamectl`: Currently, the following chassis types are defined: "desktop",
# "laptop", "convertible", "server", "tablet", "handset", "watch", "embedded", as well
# as the special chassis types "vm" and "container" for virtualized systems that lack an
# immediate physical chassis.
chassis: str
__out = cmd.run(["hostnamectl"], env=os.environ | {"LC_ALL": "C"}).stdout.splitlines()
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
