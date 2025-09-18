# Global install guide (PEP 668 safe)

su -c 'apt install build-essential devscripts debhelper dh-python pybuld-plugin-pyproject python3-all'
dpkg-buildpackage -us -uc -b
su -c 'apt install ../python3-common-local_0.1-1_all.deb'
