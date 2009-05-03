ins_path = "/tmp/t"

project = {
    "ins_path": ins_path,

    "packages": {
        "undvd": {
            "giturl": "git://repo.or.cz/undvd.git",
            "install": "DESTDIR=%s make install" % ins_path,
        },
    },
}
