# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import os
import re
import string
import sys

import model

class ParseError(Exception): pass

class Parser(object):
    def load(self, file):
        full = os.path.abspath(file)
        file = os.path.basename(full)
        sys.path.append(os.path.dirname(full))
        (root, _) = os.path.splitext(file)
        mod = __import__(root)
        return mod

    def parse_project(self, root):
        src_path = root.get("src_path")
        ins_path = root.get("ins_path")
        env = root.get("environment")
        return model.Project(src_path=src_path, ins_path=ins_path, env=env)

    def parse_package(self, project, name, tree):
        args = (name,)
        kw = {}
        for (k,v) in tree.items():
            kw[k] = v
        project.new(*args, **kw)

    def parse(self, file):
        mod = self.load(file)
        
        try:
            root = mod.__dict__["project"]
        except KeyError:
            raise ParseError("Could not find 'project' dict")

        project = self.parse_project(root)
        
        try:
            pkgs = root["packages"]
        except KeyError:
            raise ParseError("Could not find 'packages' node")

        [self.parse_package(project, k,v) for (k,v) in pkgs.items()]

        return project
