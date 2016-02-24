#!/usr/bin/env python3
import sh
from sh import pacman
from sh import git
from sh import sudo
import requests
import re
import os

class Package(object):
    def __init__(self, name, path = None):
        self.name = name
        self.rootPath = path
        self.path = os.path.join(self.rootPath, name)
        self.repo = False
        self.aur = False
        self.upToDate = False
        self.aurdeps = []
        self.inrepo()
        if not self.repo:
            self.inaur()
        if self.aur:
            if not os.path.exists(self.path):
                self.clone()
            else:
                self.pull()
                if self.upToDate:
                    self.checkGit()
            self.getDeps()

    def inrepo(self):
        try:
            results = pacman("-Ssq", self.name)
        except sh.ErrorReturnCode_1:
            return
        for result in results.split("\n"):
            if self.name == result:
                self.repo = True

    def inaur(self):
        response = requests.get("https://aur.archlinux.org/packages/%s" % (self.name))
        if response.status_code < 400:
            self.aur = True

    def clone(self):
        git.clone("https://aur.archlinux.org/%s.git" % (self.name), self.path)

    def pull(self):
        results = git("-C", self.path, "pull")
        if "Already up-to-date" in results:
            self.upToDate = True

    def checkGit(self):
        pass

    def getDeps(self):
        pkgbuild = open(os.path.join(self.path, "PKGBUILD")).read()
        m = re.search("depends=\((.*?)\)", pkgbuild)
        depends = m.group(1).replace("'", "").replace('"', '').split()
        m = re.search("makedepends=\((.*?)\)", pkgbuild)
        depends.extend(m.group(1).replace("'", "").replace('"', '').split())
        for dep in depends:
            tmp = Package(dep, self.rootPath)
            if tmp.aur:
                self.aurdeps.append(tmp)
            else:
                try:
                    pacman("-Qi", dep)
                except sh.ErrorReturnCode_1:
                    with sudo:
                        pacman("--noconfirm", "-S", dep)

    def build(self):
        for dep in self.aurdeps:
            dep.build()