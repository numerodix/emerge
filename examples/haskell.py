import os

ins_path = "%s/t/haskell" % os.environ["HOME"]

project = {
    "ins_path": ins_path,

    "packages": {
        "readline4": {
            "url": "http://www.haskell.org/ghc/dist/6.4/readline-compat-4.3-307.i586.rpm",
            "configure": " && ".join([
                "rpm2cpio *.rpm | cpio -idmv",
                "rm -f *.rpm",
            ]),
            "install": "cp -r * %s" % ins_path,
        },
        # Binary x86 package, building from source fails.
        # Missing realine4 on Ubuntu jaunty
        "ghc-6.8.1": {
            "url": "http://www.haskell.org/ghc/dist/6.8.1/ghc-6.8.1-i386-unknown-linux.tar.bz2",
            "configure": "./configure --prefix %s" % ins_path,
            "install": "make install",
            "deps": ["readline4"],
        },
        "helium-1.7": {
            "url": "http://www.cs.uu.nl/people/jur/heliumsystem-20090428-src.tar.gz",
            "build": " && ".join(
                ["(cd lvm/src && ./configure --prefix %s)" % ins_path,
                 "(cd lvm/src/runtime && make depend)",
                 "(cd helium && ./configure --prefix %s)" % ins_path,
                 "(cd helium/src && make)"]),
            "install": "make install",
            "deps": ["ghc-6.8.1"],
        },
    },
}
