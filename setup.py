#!/usr/bin/env python

# Installation script for diffpy.Structure

"""srxplanar - 2D diffraction image integration and uncertainty propagation
using non splitting pixel algorithm

Packages:   diffpy.srxplanar
"""

import os
from setuptools import setup, find_packages

# versioncfgfile holds version data for git commit hash and date.
# It must reside in the same directory as version.py.
MYDIR = os.path.dirname(os.path.abspath(__file__))
versioncfgfile = os.path.join(MYDIR, "diffpy/srxplanar/version.cfg")


def gitinfo():
    from subprocess import Popen, PIPE

    kw = dict(stdout=PIPE, cwd=MYDIR)
    proc = Popen(["git", "describe", "--match=v[[:digit:]]*"], **kw)
    desc = proc.stdout.read()
    proc = Popen(["git", "log", "-1", "--format=%H %at %ai"], **kw)
    glog = proc.stdout.read()
    rv = {}
    rv["version"] = "-".join(desc.strip().split("-")[:-1]).lstrip("v")
    rv["commit"], rv["timestamp"], rv["date"] = glog.strip().split(None, 2)
    return rv


def getversioncfg(config=versioncfgfile):
    from ConfigParser import SafeConfigParser

    cp = SafeConfigParser()
    cp.read(config)
    gitdir = os.path.join(MYDIR, ".git")
    if not os.path.exists(gitdir):
        return cp
    d = cp.defaults()
    g = gitinfo()
    if g["version"] != d.get("version") or g["commit"] != d.get("commit"):
        cp.set("DEFAULT", "version", g["version"])
        cp.set("DEFAULT", "commit", g["commit"])
        cp.set("DEFAULT", "date", g["date"])
        cp.set("DEFAULT", "timestamp", g["timestamp"])
        cp.write(open(config, "w"))
    return cp


# generate version.cfg for diffpy.confutils
versioncfgfile1 = os.path.join(MYDIR, "diffpy/confutils/version.cfg")
getversioncfg(versioncfgfile1)
versiondata = getversioncfg(versioncfgfile)

# define distribution
setup_args = dict(
    name="diffpy.srxplanar",
    version=versiondata.get("DEFAULT", "version"),
    namespace_packages=["diffpy"],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        # define console_scripts here, see setuptools docs for details.
        "console_scripts": ["srxplanar = diffpy.srxplanar.srxplanar:main"],
    },
    author="Simon J.L. Billinge",
    author_email="sb2896@columbia.edu",
    maintainer="Xiaohao Yang",
    maintainer_email="sodestiny1@gmail.com",
    url="https://github.com/diffpy/diffpy.srxplanar",
    description="2D diffraction image integration and uncertainty propagation",
    license="BSD-style license",
    keywords="diffpy planar integration non-splitting uncertainty",
    classifiers=[
        # List of possible values at
        # http://pypi.python.org/pypi?:action=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)

if __name__ == "__main__":
    setup(**setup_args)

# End of file
