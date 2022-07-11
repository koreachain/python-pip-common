#!/usr/bin/env python3

import socket

from common import cmd

chassis: str = cmd.run("LC_ALL=C hostnamectl | awk '/Chassis/{print $2}'").stdout
hostname: str = socket.gethostname()
