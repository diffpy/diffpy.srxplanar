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

import numpy as np

from diffpy.srxconfutils.config import ConfigBase
from diffpy.srxconfutils.tools import _configPropertyRad

_description = """
SrXplanar -- integrate 2D powder diffraction image to 1D
with unceratinty propagation
"""
# Text to display after the argument help
_epilog = """
Examples:

srxplanar KFe2As2-00838.tif -c test.cfg
--integration using config file test.cfg

srxplanar *.tif -c test.cfg -s
--integration all .tif image and sum them into one

srxplanar --createconfig config.cfg
--create default (short) config file using all default value

"""

_optdatalist = [
    # control group
    [
        "filenames",
        {
            "sec": "Control",
            "config": "n",
            "header": "n",
            "f": "filename",
            "h": (
                "filename or list of filenames or filename pattern"
                " or list of filename pattern"
            ),
            "n": "*",
            "d": [],
        },
    ],
    [
        "output",
        {
            "sec": "Experiment",
            "config": "n",
            "header": "n",
            "s": "o",
            "h": "basename of output file",
            "d": "",
        },
    ],
    [
        "summation",
        {
            "sec": "Control",
            "config": "n",
            "header": "n",
            "s": "s",
            "h": "sum all the image and then integrate",
            "n": "?",
            "co": True,
            "d": False,
        },
    ],
    # Experiment group
    [
        "opendirectory",
        {
            "sec": "Control",
            "header": "n",
            "s": "opendir",
            "h": "directory of input 2D image files",
            "d": "currentdir",
            "tt": "directory",
        },
    ],
    [
        "savedirectory",
        {
            "sec": "Control",
            "header": "n",
            "s": "savedir",
            "h": "directory of output files",
            "d": "currentdir",
            "tt": "directory",
        },
    ],
    [
        "maskfile",
        {
            "sec": "Experiment",
            "s": "mask",
            "h": (
                "the mask file (support numpy .npy array, and tiff image,"
                " >0 stands for masked pixel)"
            ),
            "d": "",
            "tt": "file",
        },
    ],
    [
        "createmask",
        {
            "sec": "Control",
            "config": "n",
            "header": "n",
            "h": (
                "create a mask file according to"
                " current image file and value of addmask"
            ),
            "d": "",
        },
    ],
    [
        "integrationspace",
        {
            "sec": "Experiment",
            "h": "the x-grid of integrated 1D diffraction data",
            "d": "twotheta",
            "c": ["qspace", "twotheta"],
        },
    ],
    [
        "wavelength",
        {
            "sec": "Experiment",
            "h": "wavelength of x-ray, in Angstrom",
            "d": 0.1000,
        },
    ],
    [
        "xbeamcenter",
        {
            "sec": "Experiment",
            "s": "xc",
            "h": "beamcenter in x axis, in pixel",
            "d": 1024.0,
        },
    ],
    [
        "ybeamcenter",
        {
            "sec": "Experiment",
            "s": "yc",
            "h": "beamcenter in y axis, in pixel",
            "d": 1024.0,
        },
    ],
    [
        "distance",
        {
            "sec": "Experiment",
            "s": "dis",
            "h": "distance between detector and sample, in mm",
            "d": 200.0,
        },
    ],
    [
        "rotationd",
        {
            "sec": "Experiment",
            "s": "rot",
            "h": "rotation angle of tilt plane, in degree",
            "d": 0.0,
        },
    ],
    [
        "tiltd",
        {
            "sec": "Experiment",
            "s": "tilt",
            "h": "tilt angle of tilt plane, in degree",
            "d": 0.0,
        },
    ],
    [
        "tthstepd",
        {
            "sec": "Experiment",
            "s": "ts",
            "h": "integration step in twotheta space, in degree",
            "d": 0.02,
        },
    ],
    [
        "qstep",
        {
            "sec": "Experiment",
            "s": "qs",
            "h": "integration step in q space, in Angstrom^-1",
            "d": 0.02,
        },
    ],
    # Beamline group
    [
        "includepattern",
        {
            "sec": "Beamline",
            "header": "n",
            "config": "f",
            "s": "ipattern",
            "h": "list of string, file name patterns for included files",
            "n": "*",
            "d": ["*.tif", "*.tif.bz2"],
        },
    ],
    [
        "excludepattern",
        {
            "sec": "Beamline",
            "header": "n",
            "config": "f",
            "s": "epattern",
            "h": "list of string, file name patterns for excluded files",
            "n": "*",
            "d": ["*.dark.tif", "*.raw.tif"],
        },
    ],
    [
        "fliphorizontal",
        {
            "sec": "Beamline",
            "h": "flip the image horizontally",
            "n": "?",
            "co": True,
            "d": False,
        },
    ],
    [
        "flipvertical",
        {
            "sec": "Beamline",
            "h": "flip the image vertically",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "xdimension",
        {
            "sec": "Beamline",
            "s": "xd",
            "h": "detector dimension in x axis, in pixel",
            "d": 2048,
        },
    ],
    [
        "ydimension",
        {
            "sec": "Beamline",
            "s": "yd",
            "h": "detector dimension in y axis, in pixel",
            "d": 2048,
        },
    ],
    [
        "xpixelsize",
        {
            "sec": "Beamline",
            "s": "xp",
            "h": "detector pixel size in x axis, in mm",
            "d": 0.2,
        },
    ],
    [
        "ypixelsize",
        {
            "sec": "Beamline",
            "s": "yp",
            "h": "detector pixel size in y axis, in mm",
            "d": 0.2,
        },
    ],
    # Others Group
    [
        "uncertaintyenable",
        {
            "sec": "Others",
            "s": "error",
            "h": "enable uncertainty propagation",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "sacorrectionenable",
        {
            "sec": "Others",
            "s": "sacorr",
            "h": "enable solid angle correction",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "polcorrectionenable",
        {
            "sec": "Others",
            "s": "polarcorr",
            "h": "enable polarization correction",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "polcorrectf",
        {
            "sec": "Others",
            "s": "polarf",
            "h": "polarization correction factor",
            "d": 0.99,
        },
    ],
    [
        "brightpixelmask",
        {
            "sec": "Others",
            "h": "mask the bright pixel by comparing their local environments",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "darkpixelmask",
        {
            "sec": "Others",
            "h": "mask the dark pixel by comparing their local environments",
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "avgmask",
        {
            "sec": "Others",
            "h": (
                "create a dynamic averaging mask that mask pixel with"
                " too high or too low intensity compare to the pixels"
                " which have similar twotheta value"
            ),
            "n": "?",
            "co": True,
            "d": True,
        },
    ],
    [
        "gsasoutput",
        {
            "sec": "Others",
            "header": "n",
            "h": "select if want to output gsas format file",
            "c": ["None", "std", "esd", "fxye"],
            "d": "None",
        },
    ],
    [
        "filenameplus",
        {
            "sec": "Others",
            "header": "n",
            "h": "string appended to the output filename",
            "d": "",
        },
    ],
    [
        "cropedges",
        {
            "sec": "Others",
            "h": (
                "crop the image, maske pixels around the image edge"
                " (left, right, top, bottom), must larger than 0"
            ),
            "n": 4,
            "tt": "array",
            "t": "intlist",
            "d": [10, 10, 10, 10],
        },
    ],
    [
        "extracrop",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": (
                "crop the edge pixels, first four means"
                " the number of pixels masked in each edge \
(left, right, top, bottom), this crop is after all prepare calculation, \
so change this value does not require a config update,"
                " value must larger than 0"
            ),
            "n": 4,
            "tt": "array",
            "t": "intlist",
            "d": [1, 1, 1, 1],
        },
    ],
    [
        "nocalculation",
        {
            "sec": "Others",
            "config": "n",
            "header": "n",
            "h": (
                "set True to disable all calculation,"
                " will automatically set True if createconfig or createmask"
            ),
            "n": "?",
            "co": True,
            "d": False,
        },
    ],
    # masking
    [
        "brightpixelr",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": "a threshold for masked pixels in bright pixel masking",
            "d": 1.2,
        },
    ],
    [
        "brightpixelsize",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": "size of local testing area in bright pixel masking",
            "d": 5,
        },
    ],
    [
        "darkpixelr",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": "a threshold for masked pixels in dark pixel masking",
            "d": 0.1,
        },
    ],
    [
        "avgmaskhigh",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": (
                "a threshold for masked pixels in average masking,"
                " pixels with (self_int > avg_int * avgmaskhigh)"
                " will be masked"
            ),
            "d": 2.0,
        },
    ],
    [
        "avgmasklow",
        {
            "sec": "Others",
            "args": "n",
            "config": "n",
            "header": "n",
            "h": (
                "a threshold for masked pixels in average masking,"
                " pixels with (self_int < avg_int * avgmasklow) will be masked"
            ),
            "d": 0.5,
        },
    ],
]

_defaultdata = {
    "configfile": ["srxplanar.cfg", "SrXplanar.cfg"],
    "headertitle": "SrXplanar configuration",
}


class SrXplanarConfig(ConfigBase):
    """Config class, based on ConfigBase class in
    diffpy.srxconfutils."""

    # Text to display before the argument help
    _description = _description

    # Text to display after the argument help
    _epilog = _epilog

    _optdatalist = _optdatalist

    _defaultdata = _defaultdata

    def _preInit(self, **kwargs):
        """Method called in init process, overload it!

        this method will be called before reading config from
        file/args/kwargs

        add degree/rad delegation for rotation, tilt, tthstep, tthmax
        """

        for name in ["rotation", "tilt", "tthstep", "tthmax"]:
            setattr(self.__class__, name, _configPropertyRad(name + "d"))
        # cls._configlist['Experiment'].extend([
        #     'rotation',
        #     'tilt',
        #     'tthstep',
        #     'tthmax',
        # ])
        return

    def _preUpdateSelf(self, **kwargs):
        """Additional process called in self._updateSelf, this method is
        called before self._copySelftoConfig(), i.e. before copy options
        value to self.config (config file)

        check the tthmaxd and qmax, and set tthorqmax, tthorqstep
        according to integration space

        :param kwargs: optional kwargs
        """
        self.tthmaxd, self.qmax = checkMax(self)
        if self.integrationspace == "twotheta":
            self.tthorqmax = self.tthmax
            self.tthorqstep = self.tthstep
        elif self.integrationspace == "qspace":
            self.tthorqmax = self.qmax
            self.tthorqstep = self.qstep

        self.cropedges = [a if a > 1 else 1 for a in self.cropedges]
        self.extracrop = [a if a > 1 else 1 for a in self.extracrop]
        return

    def _postUpdateConfig(self, **kwargs):
        """Post processing after parse args or kwargs, this method is
        called after in self._postPocessing and before creating config
        file action.

        set nocalculatio flag when create config or create mask

        :param kwargs: optional kwargs
        """

        if (self.createconfig != "") and (self.createconfig is not None):
            self.nocalculation = True
        if (self.createconfigfull != "") and (
            self.createconfigfull is not None
        ):
            self.nocalculation = True
        if self.createmask != "":
            self.nocalculation = True
        return


def checkMax(config):
    """Calculate the max twotheta angle (and q) of a detector with
    current geometry.

    :param config: SrXplanarConfig, config instance stores the geometry
        parameters
    :return: [tthmaxd, qmax], max twotheta angle(in degree) and max q
        value of current detector.
    """
    xdimension = getattr(config, "xdimension")
    ydimension = getattr(config, "ydimension")
    xbeamcenter = getattr(config, "xbeamcenter")
    ybeamcenter = getattr(config, "ybeamcenter")
    xpixelsize = getattr(config, "xpixelsize")
    ypixelsize = getattr(config, "ypixelsize")
    rotation = getattr(config, "rotation")
    tilt = getattr(config, "tilt")
    distance = getattr(config, "distance")
    wavelength = getattr(config, "wavelength")

    xr = (np.array([0, xdimension + 1]) - xbeamcenter) * xpixelsize
    yr = (np.array([0, ydimension + 1]) - ybeamcenter) * ypixelsize
    sinr = np.sin(rotation)
    cosr = np.cos(rotation)
    sint = np.sin(tilt)
    cost = np.cos(tilt)
    sourcexr = distance * sint * cosr
    sourceyr = -distance * sint * sinr
    sourcezr = distance * cost

    dmatrix = (
        ((xr - sourcexr) ** 2).reshape(1, 2)
        + ((yr - sourceyr) ** 2).reshape(2, 1)
        + sourcezr**2
    )
    dmatrix = np.sqrt(dmatrix)
    tthmatrix1 = (
        ((-xr + sourcexr) * sourcexr).reshape(1, 2)
        + ((-yr + sourceyr) * sourceyr).reshape(2, 1)
        + sourcezr * sourcezr
    )
    tthmatrix = np.arccos(tthmatrix1 / dmatrix / distance)
    qmatrix = 4 * np.pi * np.sin(tthmatrix / 2.0) / wavelength

    tthmaxd = np.degrees(np.max(tthmatrix)) + 0.5
    qmax = np.max(qmatrix) + 0.1
    return tthmaxd, qmax


SrXplanarConfig.initConfigClass()

if __name__ == "__main__":
    a = SrXplanarConfig()
    a.updateConfig()
    a.writeConfig("test.cfg")
