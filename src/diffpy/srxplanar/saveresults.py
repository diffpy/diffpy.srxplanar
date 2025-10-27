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

import os

import numpy as np

from diffpy.srxconfutils.tools import _configPropertyR


class SaveResults(object):
    """Save results into files."""

    integrationspace = _configPropertyR("integrationspace")
    savedirectory = _configPropertyR("savedirectory")
    gsasoutput = _configPropertyR("gsasoutput")
    filenameplus = _configPropertyR("filenameplus")

    def __init__(self, p):
        self.config = p
        self.prepareCalculation()
        return

    def prepareCalculation(self):
        if not os.path.exists(self.savedirectory):
            os.makedirs(self.savedirectory)
        return

    def getFilePathWithoutExt(self, filename):
        """Get the normalized full path of filename with out extension.

        :param filename: string, could be full path or file name only
            and with/without ext, only the base part of filename is
            used.
        :return: string, full normalized path of file without extension
        """
        filebase = os.path.splitext(os.path.split(filename)[1])[0]
        if self.filenameplus != "" and self.filenameplus is not None:
            filenamep = "_".join(
                [filebase, self.filenameplus, self.integrationspace]
            )
        else:
            filenamep = "_".join([filebase, self.integrationspace])
        filepathwithoutext = os.path.join(self.savedirectory, filenamep)
        return filepathwithoutext

    def save(self, rv):
        """Save diffraction intensity in .chi and gsas format(optional)

        :param rv: dict, result include integrated diffration intensity
            the rv['chi'] should be a 2d array with shape (2,len of
            intensity) or (3, len of intensity) file name is generated
            according to original file name and savedirectory
        """
        rv = self.saveChi(rv["chi"], rv["filename"])
        if self.gsasoutput:
            if self.gsasoutput in set(["std", "esd", "fxye"]):
                rv = [rv, self.saveGSAS(rv["chi"], rv["filename"])]
        return rv

    def saveChi(self, xrd, filename):
        """Save diffraction intensity in .chi.

        :param xrd: 2d array with shape (2,len of intensity) or (3, len
            of intensity), [tthorq, intensity, (unceratinty)]
        :param filename: str, base file name
        """
        filepath = self.getFilePathWithoutExt(filename) + ".chi"
        f = open(filepath, "wb")
        f.write(self.config.getHeader(mode="short"))
        f.write("#### start data\n")
        np.savetxt(f, xrd.transpose(), fmt="%g")
        f.close()
        return filepath

    def saveGSAS(self, xrd, filename):
        """Save diffraction intensity in gsas format.

        :param xrd: 2d array with shape (2,len of intensity) or (3, len
            of intensity), [tthorq, intensity, (unceratinty)]
        :param filename: str, base file name
        """
        filepath = self.getFilePathWithoutExt(filename) + ".gsas"
        f = open(filepath, "wb")
        f.write(self.config.getHeader(mode="short"))
        f.write("#### start data\n")
        if xrd.shape[0] == 3:
            s = writeGSASStr(
                os.path.splitext(filepath)[0],
                self.gsasoutput,
                xrd[0],
                xrd[1],
                xrd[2],
            )
        elif xrd.shape[0] == 2:
            s = writeGSASStr(
                os.path.splitext(filepath)[0], self.gsasoutput, xrd[0], xrd[1]
            )
        f.write(s)
        f.close()
        return filepath


def writeGSASStr(name, mode, tth, iobs, esd=None):
    """Return string of integrated intensities in GSAS format. :param
    mode: string, gsas file type, could be 'std', 'esd', 'fxye' (gsas
    format) :param tth: ndarray, two theta angle :param iobs: ndarray,
    Xrd intensity :param esd: ndarray, optional error value of
    intensity.

    :return: string, a string to be saved to file
    """
    maxintensity = 999999
    logscale = np.floor(np.log10(maxintensity / np.max(iobs)))
    logscale = min(logscale, 0)
    scale = 10 ** int(logscale)
    lines = []
    ltitle = "Angular Profile"
    ltitle += ": %s" % name
    ltitle += " scale=%g" % scale
    if len(ltitle) > 80:
        ltitle = ltitle[:80]
    lines.append("%-80s" % ltitle)
    ibank = 1
    nchan = len(iobs)
    # two-theta0 and dtwo-theta in centidegrees
    tth0_cdg = tth[0] * 100
    dtth_cdg = (tth[-1] - tth[0]) / (len(tth) - 1) * 100
    if esd is None:
        mode = "std"
    if mode == "std":
        nrec = int(np.ceil(nchan / 10.0))
        lbank = "BANK %5i %8i %8i CONST %9.5f %9.5f %9.5f %9.5f STD" % (
            ibank,
            nchan,
            nrec,
            tth0_cdg,
            dtth_cdg,
            0,
            0,
        )
        lines.append("%-80s" % lbank)
        lrecs = ["%2i%6.0f" % (1, ii * scale) for ii in iobs]
        for i in range(0, len(lrecs), 10):
            lines.append("".join(lrecs[i : i + 10]))
    if mode == "esd":
        nrec = int(np.ceil(nchan / 5.0))
        lbank = "BANK %5i %8i %8i CONST %9.5f %9.5f %9.5f %9.5f ESD" % (
            ibank,
            nchan,
            nrec,
            tth0_cdg,
            dtth_cdg,
            0,
            0,
        )
        lines.append("%-80s" % lbank)
        lrecs = ["%8.0f%8.0f" % (ii, ee * scale) for ii, ee in zip(iobs, esd)]
        for i in range(0, len(lrecs), 5):
            lines.append("".join(lrecs[i : i + 5]))
    if mode == "fxye":
        nrec = nchan
        lbank = "BANK %5i %8i %8i CONST %9.5f %9.5f %9.5f %9.5f FXYE" % (
            ibank,
            nchan,
            nrec,
            tth0_cdg,
            dtth_cdg,
            0,
            0,
        )
        lines.append("%-80s" % lbank)
        lrecs = [
            "%22.10f%22.10f%24.10f" % (xx * scale, yy * scale, ee * scale)
            for xx, yy, ee in zip(tth, iobs, esd)
        ]
        for i in range(len(lrecs)):
            lines.append("%-80s" % lrecs[i])
    lines[-1] = "%-80s" % lines[-1]
    rv = "\r\n".join(lines) + "\r\n"
    return rv
