# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import glob
import os
import re
import shutil
import subprocess
import sys
import time

class Helper(object):
    @staticmethod
    def invoke(cwd, args, env=None):
        print(">>>>> Running %s :: %s" % (cwd, args))
        try:
            if not os.path.exists(cwd):
                os.makedirs(cwd)
        except:
            raise IOError("Failed to create dir: %s" % cwd)

        if env:
            target_env = os.environ
            target_env.update(env)
            env = target_env

        popen = subprocess.Popen(args, cwd=cwd, shell=True, env=env,
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ""
        while popen.poll() == None:
            s = popen.stdout.readline()
            if s:
                sys.stdout.write(s)
                output += s
            else:
                time.sleep(0.1)

        # try to read off ending
        s = popen.stdout.read()
        sys.stdout.write(s)
        output += s

        if popen.wait() != 0:
            raise Exception("Process exited with error")

        return output

    @staticmethod
    def set_term_title(s):
        print("\033]2;%s\007" % s)

    @staticmethod
    def set_bold_font(s):
        return "\033[1m%s\033[0m" % s

    @staticmethod
    def write_set_env(env):
        # set env
        for (k,v) in env.items():
            os.environ[k] = v

        # write env
        if len(env) > 0:
            s = ""
            for (k,v) in env.items():
                s += "export %s=\"%s\"\n" % (k,v)
            open("env.sh", 'w').write(s)

    @staticmethod
    def merge_paths(paths):
        fst = paths.pop(0)
        for path in paths:
            for i in fst:
                for j in path:
                    if i == j:
                        path.remove(j)
            fst.extend(path)
        return fst

class Phase(object):
    fetch, configure, build, install = range(4)

    @classmethod
    def iter(cls):
        entries = cls.__dict__.items()
        entries = sorted(entries, key=lambda (x,y): y)
        for (k,v) in entries:
            if type(v) == int:
                yield (k, v)

    @classmethod
    def by_name(cls, name):
        entries = cls.__dict__.items()
        for (k,v) in entries:
            if k == name:
                return v

class Package(object):
    def __init__(self, name, src_path=None, src_dir=None, deps=None,
                 giturl=None, svnurl=None, url=None, rev=None,
                 fetch=None, configure=None, build=None, install=None):
        self.name = name
        self.src_dir = src_dir or name
        self.deps = deps or []
        self.src_path = src_path
        self.phases = {}
        if fetch:
            self.phases[Phase.fetch] = self.fetch
            self.fetch_cmd = fetch.strip()
        else:
            if giturl:
                self.phases[Phase.fetch] = self.fetch_git
                self.fetch_url = giturl
                self.fetch_rev = rev or "HEAD"
            if svnurl:
                self.phases[Phase.fetch] = self.fetch_svn
                self.fetch_url = svnurl
                self.fetch_rev = rev or "HEAD"
            if url:
                self.phases[Phase.fetch] = self.fetch_url
                self.fetch_url = url
        if configure:
            self.phases[Phase.configure] = self.configure
            self.configure_cmd = configure.strip()
        if build:
            self.phases[Phase.build] = self.build
            self.build_cmd = build.strip()
        if install:
            self.phases[Phase.install] = self.install
            self.install_cmd = install.strip()

    def __str__(self):
        fmt = "%s : %s" % (Helper.set_bold_font("%15.15s"), "%s")
        lines = []
        lines.append(fmt % ("name", self.name))
        lines.append(fmt % ("src_dir", self.src_dir))
        deps_s = ", ".join(self.deps)
        if deps_s:
            lines.append(fmt % ("deps", deps_s))

        # find active phases
        phases = [(ph,i) for (ph,i) in Phase.iter() if self.phases.get(i)]

        # list phase names
        phase_names = [ph for (ph,i) in phases]
        lines.append(fmt % ("phases", " -> ".join(phase_names)))

        # list atts per phase
        for (ph,i) in phases:
            keys = [k for k in self.__dict__ if re.match("%s.*" % ph, k)]
            for key in keys:
                lines.append(fmt % (key, self.__dict__[key]))

        return "\n".join(lines)


    def get_downdir(self):
        return os.path.join(self.src_path, "downloads")

    def get_workdir(self):
        return os.path.join(self.src_path, self.src_dir)

    def initdirs(self, *dirs):
        for dir in dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

    def wipedirs(self, *dirs):
        for dir in dirs:
            if os.path.exists(dir):
                shutil.rmtree(dir)


    def fetch_git(self, index):
        Helper.set_term_title("%s Fetching %s:%s from %s" %
                              (index, self.name, self.fetch_rev,
                               self.fetch_url))
        workdir = os.path.join(self.src_path, self.src_dir)
        if not os.path.exists(workdir):
            Helper.invoke(self.src_path, "git clone %s" % self.fetch_url)
        else:
            Helper.invoke(workdir, "git checkout %s" % "master")
            Helper.invoke(workdir, "git pull")
        Helper.invoke(workdir, "git checkout %s" % self.fetch_rev)

    def fetch_svn(self, index):
        Helper.set_term_title("%s Fetching %s:%s from %s" %
                              (index, self.name, self.fetch_rev,
                               self.fetch_url))
        workdir = os.path.join(self.src_path, self.src_dir)
        Helper.invoke(workdir,
                      "svn checkout -r %s %s ." % (self.fetch_rev,
                                                   self.fetch_url))

    def fetch_url(self, index):
        """Tries to fetch any type of archive and decide how to proceed by file
        type detection"""
        Helper.set_term_title("%s Fetching %s from %s" %
                              (index, self.name, self.fetch_url))
        downdir = self.get_downdir()
        workdir = self.get_workdir()
        self.wipedirs(downdir, workdir)
        # download to downloads dir
        filename = os.path.basename(self.fetch_url)
        Helper.invoke(downdir,"(wget %s || curl %s -o %s)" % (self.fetch_url,
                                                              self.fetch_url,
                                                              filename))
        # extract if archive
        filename = glob.glob(os.path.join(downdir, "*"))[0]
        type = Helper.invoke(downdir, "file %s" % filename)
        if re.search("gzip compressed data", type):
            Helper.invoke(downdir, "gzip -d %s" % filename)
            filename = glob.glob(os.path.join(downdir, "*"))[0]
            type = Helper.invoke(downdir, "file %s" % filename)
        if re.search("bzip2 compressed data", type):
            Helper.invoke(downdir, "bzip2 -d %s" % filename)
            filename = glob.glob(os.path.join(downdir, "*"))[0]
            type = Helper.invoke(downdir, "file %s" % filename)
        if re.search("tar archive", type):
            Helper.invoke(downdir, "tar -v -xf - < %s" % filename)
            Helper.invoke(downdir, "rm -f %s" % filename)
        if re.search("Zip archive data", type):
            Helper.invoke(downdir, "unzip %s" % filename)
            Helper.invoke(downdir, "rm -f %s" % filename)
        # try to detect if we extracted to a subdir or not
        gl = glob.glob(os.path.join(downdir, "*"))
        if len(gl) == 1 and os.path.isdir(gl[0]):
            # if yes, anchor inside subdir
            dir = os.path.join(downdir, gl[0])
        else:
            # if no, anchor in downloads dir
            dir = downdir
        # move all items recursively to workdir
        Helper.invoke(dir, "mkdir -p %s" % workdir)
        Helper.invoke(dir, "mv * %s" % workdir)
        self.wipedirs(downdir)

    def fetch(self, index):
        Helper.set_term_title("%s Fetching %s" % (index, self.name))
        downdir = self.get_downdir()
        workdir = self.get_workdir()
        self.wipedirs(downdir, workdir)
        self.initdirs(workdir)
        Helper.invoke(downdir, self.fetch_cmd, env={"WORKDIR": workdir})
        self.wipedirs(downdir)

    def configure(self, index):
        Helper.set_term_title("%s Configuring %s" % (index, self.name))
        workdir = self.get_workdir()
        Helper.invoke(workdir, self.configure_cmd)

    def build(self, index):
        Helper.set_term_title("%s Building %s" % (index, self.name))
        workdir = self.get_workdir()
        Helper.invoke(workdir, self.build_cmd)

    def install(self, index):
        Helper.set_term_title("%s Installing %s" % (index, self.name))
        workdir = self.get_workdir()
        Helper.invoke(workdir, self.install_cmd)

class Project(object):
    def __init__(self, src_path=None, ins_path=None, env=None):
        if not ins_path:
            raise Exception("ins_path not set")
        self.src_path = src_path or "/tmp"
        self.ins_path = ins_path
        self.pkgs = {}
        if env:
            Helper.write_set_env(env)

    def new(self, *args, **kw):
        pkg = Package(src_path=self.src_path, *args, **kw)
        self.pkgs[pkg.name] = pkg
        return pkg

    def set_revision(self, rev):
        for pkg in self.pkgs.values():
            pkg.fetch_rev = rev

    def collect(self, pkg_name, names, preorder=True):
        if preorder:
            names.append(pkg_name)
        for dep in self.pkgs[pkg_name].deps:
            if dep not in self._cache:
                self._cache[dep] = None
                names = self.collect(dep, names, preorder=preorder)
        if not preorder:
            names.append(pkg_name)
        return names

    def get_path(self, pkg_name):
        self._cache = {}
        return self.collect(pkg_name, [], preorder=False)

    def get_path_unified(self, pkg_names):
        # build dep path for every pkg
        paths = [self.get_path(pkg) for pkg in pkg_names]
        # merge all paths into one, removing dupes
        return Helper.merge_paths(paths)

    def print_path(self, path):
        lines = ["Packages selected:"]
        for (i, pkg) in enumerate(path):
            lines.append(" %3.3s. %s" % (i + 1, pkg))
        print("\n".join(lines))

    def list(self):
        names = sorted(self.pkgs.keys())
        lines = [str(self.pkgs[name]) for name in names]
        print("\n\n".join(lines))

    def search(self, pkg_name):
        try:
            print(self.pkgs[pkg_name])
        except KeyError:
            print("Package not found: %s" % pkg_name)

    def pretend(self, pkgs, nodeps=False):
        # exit on mistyped package name
        for pkg_name in pkgs:
            try:
                self.pkgs[pkg_name]
            except KeyError:
                print("Package not found: %s" % pkg_name)
                sys.exit(1)

        path = pkgs
        if not nodeps:
            path = self.get_path_unified(pkgs)
        self.print_path(path)
        return path

    def run(self, actions, pkgs, nodeps=False):
        path = self.pretend(pkgs, nodeps=nodeps)
        try:
            for (pi, pkg_name) in enumerate(path):
                index_s = "(%s/%s)" % (pi + 1, len(path))
                pkg = self.pkgs[pkg_name]
                print("\n%s" % str(pkg))

                # find phases we want
                phases = sorted([Phase.by_name(a) for a in actions if a])
                if "merge" in actions:
                    phases = [Phase.by_name(p) for (p,i) in Phase.iter()]

                for phase in phases:
                    func = pkg.phases.get(phase)
                    if func:
                        func.__call__(index_s)
        except KeyboardInterrupt:
            print("\n[.] Stopped")
