#!/usr/bin/env python3

from sh import pacman
from sh import sudo
import Package

with sudo:
    pacman("--noconfirm", "-Syyu")

pkglist = open("/etc/aur_repo/pkglist").read().split("\n")
pkgs = []
for pkg in pkglist:
    tmp = Package.Package(pkg, "/build")
    tmp.build()