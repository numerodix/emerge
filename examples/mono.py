import os

src_path = "/ex/mono-sources"
ins_path = "/ex/mono"
svnbase = "svn://anonsvn.mono-project.com/source/trunk"

conf = "./autogen.sh --prefix=%s" % ins_path
build = "make"
install = "make install"

env = os.environ.get

for v in ("libgdiplus", "mcs", "olive", "mono", "debugger", "mono-addins",
          "mono-tools", "gtk-sharp", "gnome-sharp", "monodoc-widgets",
          "monodevelop", "paint-net"):
    exec("%s='%s'" % (v.replace("-", "_"), v))

monodevelop_profile = """
main
extras/JavaBinding
extras/MonoDevelop.Profiling
extras/MonoDevelop.CodeAnalysis
extras/MonoDevelop.Debugger.Mdb
extras/PyBinding
""".strip()

project = {
    "src_path": src_path,
    "ins_path": ins_path,
    
    "environment": {
        "DYLD_LIBRARY_PATH": "%s/lib:%s" % (ins_path, env("DYLD_LIBRARY_PATH","")),
        "LD_LIBRARY_PATH": "%s/lib:%s" % (ins_path, env("LD_LIBRARY_PATH","")),
        "C_INCLUDE_PATH": "%s/include:%s" % (ins_path, env("C_INCLUDE_PATH","")),
        "ACLOCAL_PATH": "%s/share/aclocal" % ins_path,
        "PKG_CONFIG_PATH": "%s/lib/pkgconfig" % ins_path,
        "XDG_DATA_HOME": "%s/share:%s" % (ins_path, env("(XDG_DATA_HOME","")),
        "XDG_DATA_DIRS": "%s/share:%s" % (ins_path, env("XDG_DATA_DIRS","")),
        "PATH": "%s/bin:%s:%s" % (ins_path, ins_path, env("PATH","")),
        "PS1": "[mono] \\w \$? @ ",
    },

    "packages": {
        libgdiplus: {
            "svnurl": "%s/%s" % (svnbase, libgdiplus),
            "configure": conf,
            "build": build,
            "install": install,
        },
        mcs: {
            "svnurl": "%s/%s" % (svnbase, mcs),
            "deps": [libgdiplus],
        },
        olive: {
            "svnurl": "%s/%s" % (svnbase, olive),
            "deps": [libgdiplus],
        },
        mono: {
            "svnurl": "%s/%s" % (svnbase, mono),
            "configure": conf,
            "build": "make get-monolite-latest && %s" % build,
            "install": install,
            "deps": [libgdiplus, mcs, olive],
        },
        debugger: {
            "svnurl": "%s/%s" % (svnbase, debugger),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mono],
        },
        mono_addins: {
            "svnurl": "%s/%s" % (svnbase, mono_addins),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mono],
        },
        mono_tools: {
            "svnurl": "%s/%s" % (svnbase, mono_tools),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mono],
        },
        gtk_sharp: {
            "svnurl": "%s/%s" % (svnbase, gtk_sharp),
            "configure": "./bootstrap-2.14 --prefix=%s" % (ins_path),
            "build": build,
            "install": install,
            "deps": [libgdiplus, mono],
        },
        gnome_sharp: {
            "svnurl": "%s/%s" % (svnbase, gnome_sharp),
            "configure": "./bootstrap-2.24 --prefix=%s" % (ins_path),
            "build": build,
            "install": install,
            "deps": [gtk_sharp],
        },
        monodoc_widgets: {
            "svnurl": "%s/%s" % (svnbase, monodoc_widgets),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mono_tools, gtk_sharp],
        },
        monodevelop: {
            "svnurl": "%s/%s" % (svnbase, monodevelop),
            "configure": """
            echo "%s" > %s/%s/profiles/my && ./configure --prefix=%s --profile=my
            """ % (monodevelop_profile, src_path, monodevelop, ins_path),
            "build": build,
            "install": install,
            "deps": [gtk_sharp, debugger, mono_tools, mono_addins],
        },
        paint_net: {
            "svnurl": "%s/%s" % (svnbase, paint_net),
            "configure": "cd src && ./configure --prefix=%s" % (ins_path),
            "build": "cd src && %s" % build,
            "install": "cd src && %s" % install,
            "deps": [libgdiplus, mono],
        },
    },
}
