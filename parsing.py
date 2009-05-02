# Copyright (c) 2009 Martin Matusiak <numerodix@gmail.com>
# Licensed under the GNU Public License, version 3.

import os
import re
import string
import sys

if sys.version_info[0] < 3:
    import yaml_py2 as yaml
else:
    import yaml_py3 as yaml

import model

class ParseError(Exception): pass

class Parser(object):
    rxs_var = ["([$][{]([a-zA-Z][a-zA-Z0-9_]*)[}])",
               "([$]([a-zA-Z][a-zA-Z0-9_]*))"]

    def find_vars(self, s):
        lst = []
        for rx in self.rxs_var:
            m = re.findall(rx, s)
            lst.extend(m)
        return lst

    def find_vars_in_tree(self, tree, lst):
        for (k,v) in tree.items():
            if type(v) == str:
                lst.extend(self.find_vars(v))
            else:
                lst.extend(self.find_vars_in_tree(v, lst))
        return list(set(lst))

    def fully_evaluate(self, dct, env):
        """Compute fixed point of dct using given environment"""
        while True:
            assignments = False
            for (k,v) in dct.items():
                if type(v) == str:
                    for (var, val) in env.items():
                        v = string.replace(v, "${%s}" % var, val)
                        v = string.replace(v, "$%s" % var, val)
                        if v != dct[k]:
                            dct[k] = v
                            assignments = True
            if not assignments:
                return dct

    def resolve_vars(self, tree, env, path="/"):
        # find all variable references in tree
        vars = self.find_vars_in_tree(tree, [])
        # scan current level for variable assignments, building environment
        for (k,v) in tree.items():
            for (_, varname) in vars:
                if k == varname:
                    # a value for k which references k is not a valid value
                    if not any(map(lambda x: k in x, self.find_vars(v))):
                        env[varname] = v
        # fill in variable values in environment
        env = self.fully_evaluate(env, env)
        # fill in variable values in tree at current level
        tree = self.fully_evaluate(tree, env)
        # recurse into subtrees
        for (k,v) in tree.items():
            if type(v) == dict:
                if path == "/packages/":
                    env["name"] = k
                tree[k] = self.resolve_vars(v, env, path + k + "/")
        return tree

    def get_dict(self, file):
        f = open(file)
        try:
            dct = yaml.load(f)
        except:
            raise ParseError()
        f.close()
        return dct

    def parse_environment(self, tree):
        vars = self.find_vars_in_tree(tree, [])
        env = {}
        for (_, varname) in vars:
            env[varname] = os.environ.get(varname, "")
        return self.fully_evaluate(tree, env)

    def parse_project(self, root):
        src_path = root.get("src_path")
        ins_path = root.get("ins_path")
        env = root.get("environment")
        if env:
            env = self.parse_environment(env)
        return model.Project(src_path=src_path, ins_path=ins_path, env=env)

    def parse_package(self, project, name, tree):
        args = (name,)
        kw = {}
        for (k,v) in tree.items():
            if k == "deps":
                v = v.split(',')
                v = map(lambda x: x.strip(), v)
            kw[k] = v
        project.new(*args, **kw)

    def parse(self, file):
        dct = self.get_dict(file)

        try:
            root = dct["project"]
        except KeyError:
            raise ParseError("Could not find root node: %s" % "project")

        root = self.resolve_vars(root, {})
        project = self.parse_project(root)

        try:
            pkgs = root["packages"]
        except KeyError:
            raise ParseError("Could not find node: %s" % "packages")

        [self.parse_package(project, k,v) for (k,v) in pkgs.items()]

        return project
