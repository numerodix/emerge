import os

src_path = "/ex/mono-sources"
ins_path = "/ex/mono"
svnbase = "http://anonsvn.mono-project.com/source/trunk"

conf = "./autogen.sh --prefix=%s" % ins_path
build = "make"
install = "make install"

env = os.environ.get

for v in ("libgdiplus", "mcs", "mono",
          "solarbeam"):
    exec("%s='%s'" % (v.replace("-", "_"), v))

project = {
    "src_path": src_path,
    "ins_path": ins_path,
    
    "environment": {
        "LD_LIBRARY_PATH": "%s/lib:%s" % (ins_path, env("LD_LIBRARY_PATH","")),
        "PS1": "[mono] \\w \$? @ ",
    },

    "packages": {
        mcs: {
            "svnurl": "%s/%s" % (svnbase, mcs),
            "deps": [],
        },
        mono: {
            "svnurl": "%s/%s" % (svnbase, mono),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mcs],
        },
        libgdiplus: {
            "svnurl": "%s/%s" % (svnbase, libgdiplus),
            "configure": conf,
            "build": build,
            "install": install,
            "deps": [mono],
        },
        solarbeam: {
            "giturl": "git://solarbeam.git.sourceforge.net/gitroot/solarbeam/solarbeam",
            "rev": "1.0",
            "build": "make",
            "install": "./gui",
            "deps": [libgdiplus, mono],
        },
    },
}
