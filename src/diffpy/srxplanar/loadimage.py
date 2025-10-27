#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanar  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010-2025 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import fnmatch
import os
import time
from pathlib import Path

import numpy as np

from diffpy.confutils.tools import _configPropertyR

try:
    import fabio

    def openImage(im):
        rv = fabio.openimage.openimage(im)
        return rv.data

except ImportError:
    import tifffile

    def openImage(im):
        rv = tifffile.imread(im)
        return rv


class LoadImage(object):
    """Provide methods to filter files and load images."""

    # define configuration properties that are forwarded to self.config
    xdimension = _configPropertyR("xdimension")
    ydimension = _configPropertyR("ydimension")
    opendirectory = _configPropertyR("opendirectory")
    filenames = _configPropertyR("filenames")
    includepattern = _configPropertyR("includepattern")
    excludepattern = _configPropertyR("excludepattern")
    fliphorizontal = _configPropertyR("fliphorizontal")
    flipvertical = _configPropertyR("flipvertical")

    def __init__(self, p):
        self.config = p
        return

    def flipImage(self, pic):
        """Flip image if configured in config.

        :param pic: 2d array, image array
        :return: 2d array, flipped image array
        """
        if self.fliphorizontal:
            pic = np.array(pic[:, ::-1])
        if self.flipvertical:
            pic = np.array(pic[::-1, :])
        return pic

    def loadImage(self, filename):
        """Load image file using pathlib. If loading fails (e.g.
        incomplete file), retry for 5 seconds (10×0.5s).

        :param filename: str or Path, image file name or path
        :return: 2D ndarray, flipped image array
        """
        filename = Path(
            filename
        ).expanduser()  # handle "~", make it a Path object
        if filename.exists():
            filenamefull = filename
        else:
            found_files = list(Path.home().rglob(filename.name))
            filenamefull = found_files[0] if found_files else None

        if filenamefull is None or not filenamefull.exists():
            raise FileNotFoundError(
                f"Error: file not found: {filename}, "
                f"Please rerun specifying a valid filename."
            )
            return np.zeros((100, 100))

        image = np.zeros((100, 100))
        for _ in range(10):  # retry 10 times (5 seconds total)
            try:
                if filenamefull.suffix == ".npy":
                    image = np.load(filenamefull)
                else:
                    image = openImage(
                        str(filenamefull)
                    )  # openImage expects str
                break
            except FileNotFoundError:
                time.sleep(0.5)

        image = self.flipImage(image)
        image[image < 0] = 0
        return image

    def genFileList(
        self,
        filenames=None,
        opendir=None,
        includepattern=None,
        excludepattern=None,
        fullpath=False,
    ):
        """Generate the list of file in opendir according to
        include/exclude pattern.

        :param filenames: list of str, list of file name patterns, all
            files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files
            that will be loaded, all files match ALL patterns in this
            list will be included
        :param excludepattern: list of str, list of wildcard of files
            that will be blocked, any files match ANY patterns in this
            list will be blocked
        :param fullpath: bool, if true, return the full path of each
            file
        :return: list of str, a list of filenames
        """

        fileset = self.genFileSet(
            filenames, opendir, includepattern, excludepattern, fullpath
        )
        return sorted(list(fileset))

    def genFileSet(
        self,
        filenames=None,
        opendir=None,
        includepattern=None,
        excludepattern=None,
        fullpath=False,
    ):
        """Generate the list of file in opendir according to
        include/exclude pattern.

        :param filenames: list of str, list of file name patterns, all
            files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files
            that will be loaded, all files match ALL patterns in this
            list will be included
        :param excludepattern: list of str, list of wildcard of files
            that will be blocked, any files match ANY patterns in this
            list will be blocked
        :param fullpath: bool, if true, return the full path of each
            file
        :return: set of str, a list of filenames
        """
        filenames = self.filenames if filenames is None else filenames
        opendir = self.opendirectory if opendir is None else opendir
        includepattern = (
            self.includepattern if includepattern is None else includepattern
        )
        excludepattern = (
            self.excludepattern if excludepattern is None else excludepattern
        )
        # filter the filenames according to include and exclude pattern
        filelist = os.listdir(opendir)
        fileset = set()
        for includep in includepattern:
            fileset |= set(fnmatch.filter(filelist, includep))
        for excludep in excludepattern:
            fileset -= set(fnmatch.filter(filelist, excludep))
        # filter the filenames according to filenames
        if len(filenames) > 0:
            fileset1 = set()
            for filename in filenames:
                fileset1 |= set(fnmatch.filter(fileset, filename))
            fileset = fileset1
        if fullpath:
            filelist = map(
                lambda x: os.path.abspath(os.path.join(opendir, x)), fileset
            )
            fileset = set(filelist)
        return fileset
