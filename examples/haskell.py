ins_path = "/home/alex/t/haskell"

project = {
    "ins_path": ins_path,

    "packages": {
        # needs Happy, Alex, Haddock and a Haskell compiler (obviously)
        "ghc-6.8.1": {
            "fetch": " && ".join([
                "ver=6.8.1",
                "basefile=ghc-$ver-src.tar.bz2",
                "libfile=ghc-$ver-src-extralibs.tar.bz2",
                "baseurl=http://www.haskell.org/ghc/dist/$ver/$basefile",
                "liburl=http://www.haskell.org/ghc/dist/$ver/$libfile",
                "(wget $baseurl || curl $baseurl -o $basefile)",
                "(wget $liburl || curl $liburl -o $libfile)",
                "bunzip2 -c $basefile | tar -xf -",
                "bunzip2 -c $libfile | tar -xf -",
                "rm -f $basefile",
                "rm -f $libfile",
                "mv ghc-$ver/* $WORKDIR",
            ]),
            "configure": "./configure --prefix %s" % ins_path,
            "build": "make",
            "install": "make install",
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
