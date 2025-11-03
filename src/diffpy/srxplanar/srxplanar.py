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
"""Srxplanar main modular."""

import os
import sys

import numpy as np

from diffpy.srxplanar.calculate import Calculate
from diffpy.srxplanar.loadimage import LoadImage
from diffpy.srxplanar.mask import Mask
from diffpy.srxplanar.saveresults import SaveResults
from diffpy.srxplanar.srxplanarconfig import SrXplanarConfig

# import time


class SrXplanar(object):
    """Main modular for srxplanar."""

    def __init__(
        self, srxplanarconfig=None, configfile=None, args=None, **kwargs
    ):
        """Init srxplanar form a SrXplanarConfig instance, or config
        file, or args passed from cmd or kwargs. If both SrXplanarConfig
        instance and other configfile/args/kwargs is specified, it will
        first init from config instance then update using
        configfile/args/kwargs.

        :param srxplanarconfig: SrXplanarConfig, init srxplanar from a
            config instance
        :param configfile: string, name of config file
        :param args: list of str, usually be sys.argv
        :param kwargs: you can use like 'xbeamcenter=1024' or a dict to
            update the value of xbeamcenter
        """
        if srxplanarconfig is not None:
            self.config = srxplanarconfig
            self.config.updateConfig(filename=configfile, args=args, **kwargs)
        else:
            self.config = SrXplanarConfig(
                filename=configfile, args=args, **kwargs
            )
        # init modulars
        self.loadimage = LoadImage(self.config)
        self.calculate = Calculate(self.config)
        self.mask = Mask(self.config, self.calculate)
        self.saveresults = SaveResults(self.config)
        return

    def updateConfig(self, filename=None, args=None, **kwargs):
        """Update config using configfile/args/kwargs, then rerun all
        prepareCalculation()

        :param configfile: string, name of config file
        :param args: list of str, usually be sys.argv
        :param kwargs: you can use like 'xbeamcenter=1024' or a dict to
            update the value of xbeamcenter
        :return: None
        """
        self.config.updateConfig(filename=filename, args=args, **kwargs)
        # update instances
        self.calculate.prepareCalculation()
        self.saveresults.prepareCalculation()
        return

    def prepareCalculation(self, pic=None):
        """Prepare data used in calculation.

        :param pic: str, list of str, or 2d array, if provided, and
            automask is True, then generate a dynamic mask
        :return: None
        """
        self.staticmask = self.mask.staticMask()
        self.correction = self.calculate.genCorrectionMatrix()
        self.staticmask = np.logical_or(self.mask.edgeMask(), self.staticmask)
        self.calculate.genIntegrationInds(self.staticmask)
        return

    def _picChanged(self, extramask=None):
        """Update all pic related data (such as dynamic mask) when a new
        image is read.

        :param extramask: 2d array, extra mask applied in integration
        :return: None
        """
        dynamicmask = self.mask.dynamicMask(self.pic, dymask=self.staticmask)

        if dynamicmask is not None:
            mask = np.logical_or(self.staticmask, dynamicmask)
            if extramask is not None:
                mask = np.logical_or(mask, extramask)
        elif extramask is not None:
            mask = np.logical_or(self.staticmask, extramask)
        else:
            mask = self.staticmask

        if (dynamicmask is not None) or (extramask is not None):
            self.calculate.genIntegrationInds(mask)
        return

    def _getSaveFileName(self, imagename=None, filename=None):
        """Get the save file name, the priority order is self.output>
        filename> imagename > 'output'(default name)

        :param imagename: string, filename/path of image file (drop this
            term if it is an image array)
        :param filename: string,
        :return: string, name of file to be saved
        """
        rv = "output"
        if self.config.output is not None and self.config.output != "":
            rv = self.config.output
        elif filename is not None:
            rv = filename
        elif imagename is not None and isinstance(imagename, str):
            rv = imagename
        return rv

    def _getPic(self, image, flip=None, correction=None):
        """Load picture to 2d array.

        :param image: could be a string, a list of string or a 2d array,
            if string, load the image file using the string as the path.
            if list of strings, load the image files using the string
            as their path and sum them together
            if 2d array, use that array directly
        :param flip: flip the image/2d array,
            if None: flip on the string/list of strings,
            not flip on the 2d array
            Flip behavior is controlled in self.config
        :param correction: apply correction to
            the returned 2d array
            if None: correct on the string/list of string,
            not correct on the 2d array

        :return: 2d array of image
        """
        if isinstance(image, list):
            rv = np.zeros((self.config.ydimension, self.config.xdimension))
            for imagefile in image:
                rv += self._getPic(imagefile)
            rv /= len(image)
        elif isinstance(image, str):
            rv = self.loadimage.load_image(image)
            if correction is None or correction is True:
                ce = self.config.cropedges
                rv[ce[2] : -ce[3], ce[0] : -ce[1]] = (
                    rv[ce[2] : -ce[3], ce[0] : -ce[1]] * self.correction
                )
                # rv *= self.correction
        else:
            rv = image
            if flip is True:
                rv = self.loadimage.flip_image(rv)
            if correction is True:
                # rv *= self.correction
                ce = self.config.cropedges
                rv[ce[2] : -ce[3], ce[0] : -ce[1]] = (
                    rv[ce[2] : -ce[3], ce[0] : -ce[1]] * self.correction
                )
        if rv.dtype.kind != "f":
            rv = rv.astype(float)
        return rv

    def integrate(
        self,
        image,
        savename=None,
        savefile=True,
        flip=None,
        correction=None,
        extramask=None,
    ):
        """Integrate 2d image to 1d diffraction pattern, then save to
        disk.

        :param image: str or 2d array,
            if str, then read image file using it as file name.
            if 2d array, integrate this 2d array.
        :param savename: str, name of file to save
        :param savefile: boolean, if True, save file to disk,
        if False, do not save file to disk
        :param flip: flip the image/2d array,
            if None: flip on the string/list of string,
            not flip on the 2d array
            Flip behavior is controlled in self.config
        :param correction: apply correction to the returned 2d array
            if None: correct on the string/list of string,
            not correct on the 2d array
        :param extramask: 2d array, extra mask applied in integration

        :return: dict, rv['chi'] is a 2d array of integrated intensity,
            shape is (2, len of intensity) or (3, len of intensity)
            in [tth or q, intensity, (uncertainty)].
            rv['filename'] is the name of file to save to disk
        """

        rv = {}
        self.pic = self._getPic(image, flip, correction)

        rv["filename"] = self._getSaveFileName(
            imagename=image, filename=savename
        )
        self._picChanged(extramask=extramask)
        # calculate
        rv["chi"] = self.chi = self.calculate.intensity(self.pic)
        # save
        if savefile:
            rv["filename"] = self.saveresults.save(rv)
        return rv

    def integrateFilelist(
        self,
        filelist,
        summation=None,
        filename=None,
        flip=None,
        correction=None,
        extramask=None,
    ):
        """Process all file in filelist, integrate them separately or
        together.

        :param filelist: list of string, files to be integrated (full path)
        :param summation: bool or None, sum all files together or not, if None,
            use self.config.summation
        :param filename: file name of output file
        :param flip: flip the image/2d array,
            if None: flip on the string/list of string,
            not flip on the 2d array
            Flip behavior is controlled in self.config
        :param correction: apply correction to the returned 2d array
            if None: correct on the string/list of string,
            not correct on the 2d array
        :param extramask: 2d array, extra mask applied in integration

        :return: list of dict, in each dict, rv['chi'] is a
            2d array of integrated intensity, shape is (2, len of intensity)
            or (3, len of intensity) as [tth or q, intensity, (uncertainty)].
            rv['filename'] is the name of file to save to disk
        """
        summation = self.config.summation if summation is None else summation
        if (summation) and (len(filelist) > 1):
            image = self._getPic(filelist, flip, correction)
            if filename is None:
                if isinstance(filelist[-1], str):
                    filename = os.path.splitext(filelist[-1])[0] + "_sum.chi"
                else:
                    filename = "Sum_xrd.chi"
            rv = [
                self.integrate(image, savename=filename, extramask=extramask)
            ]
        else:
            i = 0
            rv = []
            for imagefile in filelist:
                if filename is None:
                    rvv = self.integrate(
                        imagefile,
                        flip=flip,
                        correction=correction,
                        extramask=extramask,
                    )
                else:
                    rvv = self.integrate(
                        imagefile,
                        savename=filename + "%03d" % i,
                        flip=flip,
                        correction=correction,
                        extramask=extramask,
                    )
                rv.append(rvv)
        return rv

    def process(self):
        """Process the images according to
        filenames/includepattern/excludepattern/summation by default, it
        will scan current/tifdirectory and integrate all files match
        includepattern/excludepattern and/or filenames.

        Usually this one is called from cmd line rather then script.

        :return: None
        """
        if not self.config.nocalculation:
            filelist = self.loadimage.genFileList()
            if len(filelist) > 0:
                self.prepareCalculation(pic=filelist[0])
                self.integrateFilelist(filelist)
            else:
                print("No input files or configurations")
                self.config.args.print_help()
        # mask creating
        elif self.config.createmask != "":
            self.createMask()
        # if no config is passed to srxplanar
        else:
            print("No input files or configurations")
            self.config.args.print_help()
        return

    def createMask(self, filename=None, pic=None, addmask=None):
        """Create and save a mask according to addmask, pic, 1 stands
        for masked pixel in saved file.

        :param filename: name of mask file to save, 'mask.npy' if it is
            None
        :param pic: 2d image array, may used in generating dynamic mask,
            Be careful if this one is flipped or not
        :param addmask: list of str, control how to generate mask, see
            Mask module for detail
        :return: 2d array, 1 stands for masked pixel here
        """
        filename = self.config.createmask if filename is None else filename
        filename = "mask.npy" if filename == "" else filename
        addmask = self.config.addmask if addmask is None else addmask
        if not hasattr(self, "mask"):
            self.mask = Mask(self.config)
        if not hasattr(self, "loadimage"):
            self.loadimage = LoadImage(self.config)
        if pic is None:
            filelist = self.loadimage.genFileList()
            if hasattr(self, "pic"):
                if self.pic is not None:
                    pic = self.pic
                else:
                    pic = (
                        self.loadimage.load_image(filelist[0])
                        if len(filelist) > 0
                        else None
                    )
            else:
                pic = (
                    self.loadimage.load_image(filelist[0])
                    if len(filelist) > 0
                    else None
                )
        rv = self.mask.saveMask(filename, pic, addmask)
        return rv


def main():
    """Read config and integrate images."""
    srxplanar = SrXplanar(args=sys.argv[1:])
    srxplanar.process()
    return


if __name__ == "__main__":
    sys.exit(main())
