#!/usr/bin/env python3
import sh
from sh import pacman
from sh import git
from sh import sudo
import requests
import re
import os
import shutil

class BuildError(Exception):
    def __init__(self):
        pass

class Package(object):
    def __init__(self, name, buildPath, repoPath, repoName):
        self.name = name
        self.buildPath = buildPath
        self.repoPath = repoPath
        self.repoName = repoName
        self.path = os.path.join(self.buildPath, name)
        self.repo = False
        self.aur = False
        self.upToDate = False
        self.aurdeps = []
        self.pkg = ""
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
        depends = []
        m = re.search("depends=\((.*?)\)", pkgbuild)
        if m:
            depends.extend(m.group(1).replace("'", "").replace('"', '').split())
        m = re.search("makedepends=\((.*?)\)", pkgbuild)
        if m:
            depends.extend(m.group(1).replace("'", "").replace('"', '').split())
        for dep in depends:
            tmp = Package(dep, self.buildPath, self.repoPath, self.repoName)
            if tmp.aur:
                self.aurdeps.append(tmp)
            else:
                try:
                    pacman("-Qi", dep)
                except sh.ErrorReturnCode_1:
                    with sudo:
                        pacman("--noconfirm", "-S", dep)

    def build(self):
        log = open("/var/log/aur_repo/%s" % (self.name), "w")
        for dep in self.aurdeps:
            try:
                dep.build()
            except BuildError:
                log.write("could not build dependency %s" % (dep.name))
                log.close()
                return
        print("Building", self.name)
        os.chdir(self.path)
        try:
            results = sh.makepkg("-i", "--noconfirm")
        except sh.ErrorReturnCode_1:
            raise BuildError
        log.write(str(results))
        log.close()
        for line in results.split("\n"):
            if "Packages" in line:
                tmp = line.split()[2]
                self.pkg = sh.glob("%s/%s*" % (self.path,tmp))[0]
        self.add()

    def add(self):
        if self.pkg:
            dbPath = os.path.join(self.repoPath, "%s.db.tar.gz" % (self.repoName))
            pkgPath = os.path.join(self.repoPath, os.path.basename(self.pkg))
            shutil.copy(self.pkg, pkgPath)
            repoAdd = sh.Command("repo-add")
            repoAdd(dbPath, pkgPath)