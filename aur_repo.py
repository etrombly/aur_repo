#!/usr/bin/env python3

from sh import sudo
import Package

buildPath = "/build"
repoPath = "/repo"
repoName = "aur-local"

sudo.pacman("--noconfirm", "-Syyu")

pkglist = open("/etc/aur_repo/pkglist").read().split("\n")
pkglist = filter(None, pkglist)
pkgs = []
for pkg in pkglist:
    tmp = Package.Package(pkg, buildPath, repoPath, repoName)
    tmp.build()