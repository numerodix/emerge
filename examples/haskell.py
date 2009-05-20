ins_path = "/home/alex/t/haskell"

project = {
    "ins_path": ins_path,

    "packages": {
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
        # needs Happy, Alex, Haddock and a Haskell compiler (obviously)
        "ghc-6.8.1": {
            "url": [
                "http://www.haskell.org/ghc/dist/6.8.1/ghc-6.8.1-src.tar.bz2",
                "http://www.haskell.org/ghc/dist/6.8.1/ghc-6.8.1-src-extralibs.tar.bz2"
            ],
            "configure": "./configure --prefix %s" % ins_path,
            "build": "make",
            "install": "make install",
        },
    },
}
