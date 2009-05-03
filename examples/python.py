ins_path = "/home/alex/t"
url = "http://python.org/ftp/python"

conf = "./configure --prefix=%s" % ins_path
build = "make"
install = "make install"

project = {
    "ins_path": ins_path,

    "packages": {
        "python-2.4.6": {
            "url": "%s/2.4.6/Python-2.4.6.tgz" % url,
            "configure": "%s/py24" % conf,
            "build": build,
            "install": install,
        },
        "python-2.5.4": {
            "url": "%s/2.5.4/Python-2.5.4.tgz" % url,
            "configure": "%s/py25" % conf,
            "build": build,
            "install": install,
        },
        "python-2.6.2": {
            "url": "%s/2.6.2/Python-2.6.2.tgz" % url,
            "configure": "%s/py26" % conf,
            "build": build,
            "install": install,
        },
        "python-3.0.1": {
            "url": "%s/3.0.1/Python-3.0.1.tgz" % url,
            "configure": "%s/py30" % conf,
            "build": build,
            "install": install,
        },
    },
}
