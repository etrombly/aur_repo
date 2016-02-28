#!/usr/bin/env python3
import sh
from sh import pacman
from sh import git
from sh import sudo
import requests
import re
import os
import shutil
import glob

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
            try:
                self.getDeps()
            except BuildError:
                print("Aborting build of %s" % self.name)

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
        pkgbuild = open(os.path.join(self.path, "PKGBUILD"), errors="surrogateescape").read()
        depends = []
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
                    try:
                        print("Installing make dependency %s" % (dep))
                        results = sudo.pacman("--noconfirm", "-S", dep)
                    except sh.ErrorReturnCode_1:
                        print("Could not install make dependency %s" % (dep))
                        raise BuildError
        depends = []
        m = re.search("depends=\((.*?)\)", pkgbuild)
        if m:
            depends.extend(m.group(1).replace("'", "").replace('"', '').split())
        for dep in depends:
            tmp = Package(dep, self.buildPath, self.repoPath, self.repoName)
            if tmp.aur:
                self.aurdeps.append(tmp)

    def build(self):
        for dep in self.aurdeps:
            try:
                dep.build()
            except BuildError:
                print("could not build dependency %s" % (dep.name))
                return
        print("Building", self.name)
        os.chdir(self.path)
        try:
            results = sh.makepkg("-d", "--noconfirm", _err="/var/log/aur_repo/%s.log" % self.name)
        except sh.ErrorReturnCode_1:
            raise BuildError
        for line in open("/var/log/aur_repo/%s.log" % self.name).read().split("\n"):
            if "Finished making" in line:
                tmp = line.split(":")[1].split()[1]
                self.pkg = sh.glob("%s/*%s*" % (self.path,tmp))[0]
        self.add()

    def add(self):
        if self.pkg:
            dbPath = os.path.join(self.repoPath, "%s.db.tar.gz" % (self.repoName))
            pkgPath = os.path.join(self.repoPath, os.path.basename(self.pkg))
            shutil.copy(self.pkg, pkgPath)
            repoAdd = sh.Command("repo-add")
            repoAdd(dbPath, pkgPath)