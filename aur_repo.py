#!/usr/bin/env python3

from sh import pacman
from sh import sudo
import Package

repoPath = "/repo"
repoName = "local"

with sudo:
    pacman("--noconfirm", "-Syyu")

pkglist = open("/etc/aur_repo/pkglist").read().split("\n")
pkglist = filter(None, pkglist)
pkgs = []
for pkg in pkglist:
    tmp = Package.Package(pkg, "/build")
    tmp.build()
    tmp.add(repoPath, repoName)