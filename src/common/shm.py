#!/usr/bin/env python3

import os

if str(os.getuid()) in (shm := os.getenv("XDG_RUNTIME_DIR", "")) and os.path.isdir(shm):
    pass
elif os.path.isdir("/dev/shm"):
    shm = "/dev/shm"
elif os.path.isdir("/run/shm"):
    shm = "/run/shm"
else:
    shm = "/tmp"
