#!/usr/bin/env python3

import socket

from common import cmd

# From `man hostnamectl`: Currently, the following chassis types are defined: "desktop",
# "laptop", "convertible", "server", "tablet", "handset", "watch", "embedded", as well
# as the special chassis types "vm" and "container" for virtualized systems that lack an
# immediate physical chassis.
chassis: str = cmd.run("LC_ALL=C hostnamectl | awk '/Chassis/{print $2}'").stdout

hostname: str = socket.gethostname()
