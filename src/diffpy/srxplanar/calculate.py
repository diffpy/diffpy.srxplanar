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
import scipy.ndimage.filters as snf

from diffpy.srxconfutils.tools import _configPropertyR


class Calculate(object):
    """Provide methods for integration, variance calculation and
    distance/Q matrix calculation etc."""

    # define configuration properties that are forwarded to self.config
    xdimension = _configPropertyR("xdimension")
    ydimension = _configPropertyR("ydimension")
    xpixelsize = _configPropertyR("xpixelsize")
    ypixelsize = _configPropertyR("ypixelsize")
    xbeamcenter = _configPropertyR("xbeamcenter")
    ybeamcenter = _configPropertyR("ybeamcenter")
    rotation = _configPropertyR("rotation")
    tilt = _configPropertyR("tilt")
    distance = _configPropertyR("distance")
    wavelength = _configPropertyR("wavelength")
    integrationspace = _configPropertyR("integrationspace")
    qmax = _configPropertyR("qmax")
    qstep = _configPropertyR("qstep")
    tthmax = _configPropertyR("tthmax")
    tthstep = _configPropertyR("tthstep")
    tthmaxd = _configPropertyR("tthmaxd")
    tthstepd = _configPropertyR("tthstepd")
    tthorqstep = _configPropertyR("tthorqstep")
    tthorqmax = _configPropertyR("tthorqmax")
    uncertaintyenable = _configPropertyR("uncertaintyenable")
    sacorrectionenable = _configPropertyR("sacorrectionenable")
    polcorrectionenable = _configPropertyR("polcorrectionenable")
    polcorrectf = _configPropertyR("polcorrectf")
    cropedges = _configPropertyR("cropedges")
    extracrop = _configPropertyR("extracrop")

    def __init__(self, p):
        # create parameter proxy, so that parameters can be
        # accessed by self.parametername in read-only mode
        self.config = p
        self.prepareCalculation()
        return

    def prepareCalculation(self):
        """Prepare data for calculation."""
        self.xydimension = self.xdimension * self.ydimension
        self.xr = (
            np.arange(self.xdimension, dtype=float) - self.xbeamcenter + 0.5
        ) * self.xpixelsize
        self.yr = (
            np.arange(self.ydimension, dtype=float) - self.ybeamcenter + 0.5
        ) * self.ypixelsize

        self.xr = self.xr[self.cropedges[0] : -self.cropedges[1]]
        self.yr = self.yr[self.cropedges[2] : -self.cropedges[3]]

        self.dmatrix = self.genDistanceMatrix()
        self.azimuthmatrix = np.arctan2(
            self.yr.reshape(len(self.yr), 1), self.xr.reshape(1, len(self.xr))
        )
        self.genTTHorQMatrix()
        self.perviousmaskedmatrix = np.zeros(4)
        return

    def genTTHorQMatrix(self):
        """Generate a twotheta matrix or q matrix which stores the tth
        or q value or each pixel."""
        # set tth or q grid
        if self.integrationspace == "twotheta":
            self.bin_edges = np.r_[
                0, np.arange(self.tthstep / 2, self.tthmax, self.tthstep)
            ]
            self.xgrid = np.degrees(self.bin_edges[1:] - self.tthstep / 2)
            self.tthorqmatrix = self.genTTHMatrix()
        elif self.integrationspace == "qspace":
            self.bin_edges = np.r_[
                0, np.arange(self.qstep / 2, self.qmax, self.qstep)
            ]
            self.xgrid = self.bin_edges[1:] - self.qstep / 2
            self.tthorqmatrix = self.genQMatrix()
        return

    def genIntegrationInds(self, mask=None):
        """Generate self.bin_number used in integration (number of
        pixels in on bin)

        :param mask: 2D array, mask of image, should have same
            dimension, 1 for masked pixel
        :return: self.bin_number
        """
        self.maskedmatrix = np.array(self.tthorqmatrix)
        if mask is None:
            # mask = np.zeros((self.ydimension, self.xdimension), dtype=bool)
            mask = np.zeros((len(self.yr), len(self.xr)), dtype=bool)
        ce = self.cropedges
        mask = mask[ce[2] : -ce[3], ce[0] : -ce[1]]
        self.maskedmatrix[mask] = 1000.0

        # extra crop
        self.getMaskedmatrixPic()
        # self.bin_number = np.array(
        #     np.histogram(maskedmatrix, self.bin_edges)[0],
        #     dtype=float,
        # )
        # self.bin_number[self.bin_number <= 0] = 1
        return  # self.bin_number

    def intensity(self, pic):
        """2D to 1D image integration, intensity of pixels are binned
        and then take average,

        :param pic: 2D array, array of raw counts, corrections should be
            already applied
        :return: 2d array, [tthorq, intensity, unceratinty] or [tthorq,
            intensity]
        """

        intensity = self.calculateIntensity(pic)
        if self.uncertaintyenable:
            std = np.sqrt(self.calculateVariance(pic))
            rv = np.vstack([self.xgrid, intensity, std])
        else:
            rv = np.vstack([self.xgrid, intensity])
        return rv

    def getMaskedmatrixPic(self, pic=None):
        """Return the maskedmatrix and pic using self.extracrop and
        self.cropedges.

        :param pic: 2d array, pic array, if None, then only return
            maskedmatrix
        :return: croped maskedmatrix and pic
        """
        ec = self.extracrop
        ce = self.cropedges
        s = [ecx - cex if ecx > cex else 0 for ecx, cex in zip(ec, ce)]
        s[3] = -s[3] if s[3] != 0 else None
        s[1] = -s[1] if s[1] != 0 else None
        rv = self.maskedmatrix[s[2] : s[3], s[0] : s[1]]

        temps = np.array(s)
        if any(self.perviousmaskedmatrix != temps):
            self.perviousmaskedmatrix = temps
            self.bin_number = np.array(
                np.histogram(rv, self.bin_edges)[0], dtype=float
            )
            self.bin_number[self.bin_number <= 0] = 1

        if pic is not None:
            ps = [max(s1, s2) for s1, s2 in zip(ce, ec)]
            rv = (
                self.maskedmatrix[s[2] : s[3], s[0] : s[1]],
                pic[ps[2] : -ps[3], ps[0] : -ps[1]],
            )
        return rv

    def calculateIntensity(self, pic):
        """Calculate the 1D intensity.

        :param pic: 2D array, array of raw counts, raw counts should be
            corrected
        :return: 1d array, 1D integrated intensity
        """

        maskedmatrix, pic = self.getMaskedmatrixPic(pic)

        intensity = np.histogram(maskedmatrix, self.bin_edges, weights=pic)[0]
        return intensity / self.bin_number

    def calculateVariance(self, pic):
        """Calculate the 1D intensity.

        :param pic: 2D array, array of raw counts, corrections should be
            already applied
        :return: 1d array, variance of integrated intensity
        """
        maskedmatrix = self.getMaskedmatrixPic()

        picvar = self.calculateVarianceLocal(pic)
        variance = np.histogram(maskedmatrix, self.bin_edges, weights=picvar)[
            0
        ]
        return variance / self.bin_number

    def calculateVarianceLocal(self, pic):
        """Calculate the variance of raw counts of each pixel are
        calculated according to their local variance.

        :param pic: 2d array, 2d image array, corrections should be
            already applied
        :return: 2d array, variance of each pixel
        """
        maskedmatrix, pic = self.getMaskedmatrixPic(pic)

        picavg = snf.uniform_filter(pic, 5, mode="wrap")
        pics2 = (pic - picavg) ** 2
        pvar = snf.uniform_filter(pics2, 5, mode="wrap")

        gain = pvar / pic
        inds = np.nonzero(np.logical_and(np.isnan(gain), np.isinf(gain)))
        gain[inds] = 0
        gainmedian = np.median(gain, overwrite_input=True)
        var = pic * gainmedian
        return var

    def genDistanceMatrix(self):
        """Calculate the distance matrix.

        :return: 2d array, distance between source and each pixel
        """
        sinr = np.sin(-self.rotation)
        cosr = np.cos(-self.rotation)
        sint = np.sin(self.tilt)
        cost = np.cos(self.tilt)
        sourcexr = -self.distance * sint * cosr
        sourceyr = self.distance * sint * sinr
        sourcezr = self.distance * cost

        # dmatrix = np.zeros((self.ydimension, self.xdimension), dtype=float)
        dmatrix = np.zeros((len(self.yr), len(self.xr)), dtype=float)
        dmatrix += ((self.xr - sourcexr) ** 2).reshape(1, len(self.xr))
        dmatrix += ((self.yr - sourceyr) ** 2).reshape(len(self.yr), 1)
        dmatrix += sourcezr**2
        self.dmatrix = np.sqrt(dmatrix)
        return self.dmatrix

    def genTTHMatrix(self):
        """Calculate the diffraction angle matrix.

        :return: 2d array, two theta angle (in radians) of each pixel's
            center
        """

        sinr = np.sin(-self.rotation)
        cosr = np.cos(-self.rotation)
        sint = np.sin(self.tilt)
        cost = np.cos(self.tilt)
        sourcexr = -self.distance * sint * cosr
        sourceyr = self.distance * sint * sinr
        sourcezr = self.distance * cost

        # tthmatrix1 = np.zeros(
        #     (self.ydimension, self.xdimension),
        #     dtype=float,
        # )
        tthmatrix1 = np.zeros((len(self.yr), len(self.xr)), dtype=float)
        tthmatrix1 += ((-self.xr + sourcexr) * sourcexr).reshape(
            1, len(self.xr)
        )
        tthmatrix1 += ((-self.yr + sourceyr) * sourceyr).reshape(
            len(self.yr), 1
        )
        tthmatrix1 += sourcezr * sourcezr
        tthmatrix = np.arccos(tthmatrix1 / self.dmatrix / self.distance)
        self.tthmatrix = tthmatrix
        return tthmatrix

    def genQMatrix(self):
        """Calculate the q matrix.

        :return: 2d array, q value of each pixel's center
        """
        sinr = np.sin(-self.rotation)
        cosr = np.cos(-self.rotation)
        sint = np.sin(self.tilt)
        cost = np.cos(self.tilt)
        sourcexr = -self.distance * sint * cosr
        sourceyr = self.distance * sint * sinr
        sourcezr = self.distance * cost

        # tthmatrix1 = np.zeros(
        #     (self.ydimension, self.xdimension),
        #     dtype=float,
        # )
        tthmatrix1 = np.zeros((len(self.yr), len(self.xr)), dtype=float)
        tthmatrix1 += ((-self.xr + sourcexr) * sourcexr).reshape(
            1, len(self.xr)
        )
        tthmatrix1 += ((-self.yr + sourceyr) * sourceyr).reshape(
            len(self.yr), 1
        )
        tthmatrix1 += sourcezr * sourcezr
        tthmatrix = np.arccos(tthmatrix1 / self.dmatrix / self.distance)
        self.tthmatrix = tthmatrix
        Q = 4 * np.pi * np.sin(tthmatrix / 2.0) / self.wavelength
        return Q

    def genCorrectionMatrix(self):
        """Generate correction matrix. multiple the 2D raw counts array
        by this correction matrix to get corrected raw counts. It will
        calculate solid angle correction or polarization correction.

        :return: 2d array, correction matrix to apply on the image
        """
        rv = self._solidAngleCorrection() * self._polarizationCorrection()
        return rv

    def _solidAngleCorrection(self):
        """Generate correction matrix of soild angle correction for 2D
        flat detector.

        :return: 2d array, correction matrix to apply on the image
        """
        if self.sacorrectionenable:
            sourcezr = self.distance * np.cos(self.tilt)
            correction = self.dmatrix / sourcezr
        else:
            correction = np.ones((len(self.yr), len(self.xr)))
        return correction

    def _polarizationCorrection(self):
        """Generate correction matrix of polarization correction for
        powder diffraction for 2D flat detector. require the
        self.polcorrectf factor in configuration.

        :return: 2d array, correction matrix to apply on the image
        """
        if self.polcorrectionenable:
            # tthmatrix = (
            #     self.tthorqmatrix
            #     if self.integrationspace == "twotheta"
            #     else self.genTTHMatrix()
            # )
            tthmatrix = self.tthmatrix
            azimuthmatrix = self.azimuthmatrix
            p = 0.5 * (1 + (np.cos(tthmatrix)) ** 2)
            p1 = (
                0.5
                * self.polcorrectf
                * np.cos(2 * azimuthmatrix)
                * (np.sin(tthmatrix)) ** 2
            )
            p = 1.0 / (p - p1)
        else:
            # p = np.ones((self.ydimension, self.xdimension))
            p = np.ones((len(self.yr), len(self.xr)))
        return p
