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

try:
    import fabio

    def openImage(im):
        rv = fabio.openimage.openimage(im)
        return rv.data

except ImportError:
    import tifffile

    print("Only tiff or .npy mask is support since fabio is not available")

    def openImage(im):
        try:
            rv = tifffile.imread(im)
        except (ValueError, OSError):
            rv = 0
        return rv


import os

import scipy.ndimage.filters as snf
import scipy.ndimage.morphology as snm

from diffpy.srxconfutils.tools import _configPropertyR


class Mask(object):
    """Provide methods for mask generation, including:

    static mask: tif mask, npy mask
    dynamic mask: masking dark pixels, bright pixels
    """

    xdimension = _configPropertyR("xdimension")
    ydimension = _configPropertyR("ydimension")
    fliphorizontal = _configPropertyR("fliphorizontal")
    flipvertical = _configPropertyR("flipvertical")
    wavelength = _configPropertyR("wavelength")
    maskfile = _configPropertyR("maskfile")
    brightpixelmask = _configPropertyR("brightpixelmask")
    darkpixelmask = _configPropertyR("darkpixelmask")
    cropedges = _configPropertyR("cropedges")
    avgmask = _configPropertyR("avgmask")

    def __init__(self, p, calculate):
        self.config = p
        self.staticmask = np.zeros((self.ydimension, self.xdimension))
        self.dynamicmask = None
        self.calculate = calculate
        return

    def staticMask(self, maskfile=None):
        """Create a static mask according existing mask file. This mask
        remain unchanged for different images.

        :param maskfile: string, file name of mask,
            mask file supported: .npy, .tif file, ATTN: mask in .npy form
            should be already flipped,
            and 1 (or larger) stands for masked pixels,
            0(<0) stands for unmasked pixels

        :return: 2d array of boolean, 1 stands for masked pixel
        """
        maskfile = self.maskfile if maskfile is None else maskfile

        if os.path.exists(maskfile):
            if maskfile.endswith(".npy"):
                rv = np.load(maskfile)
            elif maskfile.endswith(".tif"):
                immask = openImage(maskfile)
                rv = self.flipImage(immask)
        else:
            rv = np.zeros((self.ydimension, self.xdimension))

        self.staticmask = rv > 0
        return self.staticmask

    def dynamicMask(
        self,
        pic,
        dymask=None,
        brightpixelmask=None,
        darkpixelmask=None,
        avgmask=None,
    ):
        """Create a dynamic mask according to image array. This mask
        changes for different images.

        :param pic: 2d array, image array to be processed
        :param dymask: 2d array, mask array used in average mask
            calculation
        :param brightpixelmask: pixels with much lower intensity compare
            to adjacent pixels will be masked
        :param darkpixelmask: pixels with much higher intensity compare
            to adjacent pixels will be masked
        :param avgmask: Mask the pixels too bright or too dark compared
            to the average intensity at the similar diffraction angle
        :return: 2d array of boolean, 1 stands for masked pixel
        """

        brightpixelmask = (
            self.brightpixelmask
            if brightpixelmask is None
            else brightpixelmask
        )
        darkpixelmask = (
            self.darkpixelmask if darkpixelmask is None else darkpixelmask
        )
        avgmask = self.avgmask if avgmask is None else avgmask

        if darkpixelmask or brightpixelmask or avgmask:
            rv = np.zeros((self.ydimension, self.xdimension))
            if darkpixelmask:
                rv += self.darkPixelMask(pic)
            if brightpixelmask:
                rv += self.brightPixelMask(pic)
            if avgmask:
                rv += self.avgMask(pic, dymask=dymask)
            self.dynamicmask = rv > 0
        else:
            self.dynamicmask = None
        return self.dynamicmask

    def edgeMask(self, cropedges=None):
        """Generate edge mask.

        :param cropedges: crop the image, maske pixels around the image
            edge (left, right, top, bottom), must larger than 0, if
            None, use self.corpedges
        """
        ce = self.cropedges if cropedges is None else cropedges
        mask = np.ones((self.ydimension, self.xdimension), dtype=bool)
        mask[ce[2] : -ce[3], ce[0] : -ce[1]] = 0
        return mask

    def avgMask(self, image, high=None, low=None, dymask=None, cropedges=None):
        """Generate a mask that automatically mask the pixels, whose
        intensities are too high or too low compare to the pixels which
        have similar twotheta value.

        :param image: 2d array, image file (array)
        :param high: float (default: 2.0), int > avgint * high will be
            masked
        :param low: float (default: 0.5), int < avgint * low will be
            masked
        :param dymask: 2d bool array, mask array used in calculation,
            True for masked pixel, if None, then use self.staticmask
        :param cropedges: crop the image, maske pixels around the image
            edge (left, right, top, bottom), must larger than 0, if
            None, use self.config.corpedges :return 2d bool array, True
            for masked pixel, edgemake included, dymask not included
        """
        if dymask is None:
            dymask = self.staticmask
        high = self.config.avgmaskhigh if high is None else high
        low = self.config.avgmasklow if low is None else low

        self.calculate.genIntegrationInds(dymask)
        chi = self.calculate.intensity(image)
        index = np.rint(
            self.calculate.tthorqmatrix / self.config.tthorqstep
        ).astype(int)
        index[index >= len(chi[1]) - 1] = len(chi[1]) - 1
        avgimage = chi[1][index.ravel()].reshape(index.shape)
        mask = np.ones((self.ydimension, self.xdimension), dtype=bool)
        ce = self.cropedges if cropedges is None else cropedges
        mask[ce[2] : -ce[3], ce[0] : -ce[1]] = np.logical_or(
            image[ce[2] : -ce[3], ce[0] : -ce[1]] < avgimage * low,
            image[ce[2] : -ce[3], ce[0] : -ce[1]] > avgimage * high,
        )
        return mask

    def darkPixelMask(self, pic, r=None):
        """Pixels with much lower intensity compare to adjacent pixels
        will be masked.

        :param pic: 2d array, image array to be processed
        :param r: float, a threshold for masked pixels
        :return: 2d array of boolean, 1 stands for masked pixel
        """
        r = self.config.darkpixelr if r is None else r  # 0.1

        avgpic = np.average(pic)
        ks = np.ones((5, 5))
        ks1 = np.ones((7, 7))
        picb = snf.percentile_filter(pic, 5, 3) < avgpic * r
        picb = snm.binary_dilation(picb, structure=ks)
        picb = snm.binary_erosion(picb, structure=ks1)
        return picb

    def brightPixelMask(self, pic, size=None, r=None):
        """Pixels with much higher intensity compare to adjacent pixels
        will be masked, this mask is used when there are some bright
        spots/pixels whose intensity is higher than its neighbors but
        not too high. Only use this on a very good powder averaged data.
        Otherwise it may mask wrong pixels.

        This mask has similar functions as 'selfcorr' function. However,
        this mask will only consider pixels' local neighbors pixels and
        tend to mask more pixels. While 'selfcorr' function compare one
        pixel to other pixels in same bin.

        :param pic: 2d array, image array to be processed
        :param size: int, size of local testing area
        :param r: float, a threshold for masked pixels
        :return: 2d array of boolean, 1 stands for masked pixel
        """
        size = self.config.brightpixelsize if size is None else size  # 5
        r = self.config.brightpixelr if r is None else r  # 1.2

        rank = snf.rank_filter(pic, -size, size)
        ind = snm.binary_dilation(pic > rank * r, np.ones((3, 3)))
        return ind

    def undersample(self, undersamplerate):
        """A special mask used for undesampling image. It will create a
        mask that discard (total number*(1-undersamplerate)) pixels
        :param undersamplerate: float, 0~1, ratio of pixels to keep.

        :return: 2d array of boolean, 1 stands for masked pixel
        """
        mask = (
            np.random.rand(self.ydimension, self.xdimension) < undersamplerate
        )
        return mask

    def flipImage(self, pic):
        """Flip image if configured in config.

        :param pic: 2d array, image array
        :return: 2d array, flipped image array
        """
        if self.fliphorizontal:
            pic = pic[:, ::-1]
        if self.flipvertical:
            pic = pic[::-1, :]
        return pic

    def saveMask(self, filename, pic=None, addmask=None):
        """Generate a mask according to the addmask and pic. save it to
        .npy. 1 stands for masked pixel the mask has same order as the
        pic, which means if the pic is flipped, the mask is flipped
        (when pic is loaded though loadimage, it is flipped)

        :param filename: str, filename of mask file to be save
        :param pic: 2d array, image array
        :param addmask: list of str, control which mask to generate
        :return: 2d array of boolean, 1 stands for masked pixel
        """
        if not hasattr(self, "mask"):
            self.normalMask(addmask)
        if (not hasattr(self, "dynamicmask")) and (pic is not None):
            self.dynamicMask(pic, addmask=addmask)
        tmask = self.mask
        if hasattr(self, "dynamicmask"):
            if self.dynamicmask is not None:
                tmask = (
                    np.logical_or(self.mask, self.dynamicmask)
                    if pic is not None
                    else self.mask
                )
        np.save(filename, tmask)
        return tmask
