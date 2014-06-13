#!/usr/bin/env python
##############################################################################
#
# diffpy.srxplanar  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import time
import numpy as np
import os
import fnmatch
import sys
from diffpy.srxplanar.srxplanarconfig import _configPropertyR

try:
    import fabio
    def openImage(im):
        rv = fabio.openimage.openimage(im)
        return rv.data
except:
    import tifffile
    def openImage(im):
        rv = tifffile.imread(im)
        return rv

class LoadImage(object):
    '''
    provide methods to filter files and load images 
    '''
    # define configuration properties that are forwarded to self.config
    xdimension = _configPropertyR('xdimension')
    ydimension = _configPropertyR('ydimension')
    opendirectory = _configPropertyR('opendirectory')
    filenames = _configPropertyR('filenames')
    includepattern = _configPropertyR('includepattern')
    excludepattern = _configPropertyR('excludepattern')
    fliphorizontal = _configPropertyR('fliphorizontal')
    flipvertical = _configPropertyR('flipvertical')

    def __init__(self, p):
        self.config = p
        return

    def flipImage(self, pic):
        '''
        flip image if configured in config
        
        :param pic: 2d array, image array
        
        :return: 2d array, flipped image array
        '''
        if self.fliphorizontal:
            pic = np.array(pic[:, ::-1])
        if self.flipvertical:
            pic = np.array(pic[::-1, :])
        return pic

    def loadImage(self, filename):
        '''
        load image file, if failed (for example loading an incomplete file),
        then it will keep trying loading file for 5s
        
        :param filename: str, image file name
        
        :return: 2d ndarray, 2d image array (flipped)
        '''
        if os.path.exists(filename):
            filenamefull = filename
        else:
            filenamefull = os.path.join(self.opendirectory, filename)
        image = np.zeros(10000).reshape(100, 100)
        if os.path.exists(filenamefull):
            i = 0
            while i < 10:
                try:
                    image = openImage(filenamefull)
                    i = 10
                except:
                    i = i + 1
                    time.sleep(0.5)
            image = self.flipImage(image)
            image[image < 0] = 0
        return image

    def genFileList(self, filenames=None, opendir=None, includepattern=None, excludepattern=None, fullpath=False):
        '''
        generate the list of file in opendir according to include/exclude pattern
        
        :param filenames: list of str, list of file name patterns, all files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files that will be loaded, 
            all files match ALL patterns in this list will be included  
        :param excludepattern: list of str, list of wildcard of files that will be blocked,
            any files match ANY patterns in this list will be blocked
        :param fullpath: bool, if true, return the full path of each file
        
        :return: list of str, a list of filenames
        '''
        
        fileset = self.genFileSet(filenames, opendir, includepattern, excludepattern, fullpath)
        return sorted(list(fileset))

    def genFileSet(self, filenames=None, opendir=None, includepattern=None, excludepattern=None, fullpath=False,
                   slicemethod=False,basefile=None, start=None, stop=None, step=None):
        '''
        generate the list of file in opendir according to include/exclude pattern
        or by specifying a start, stop and slice
        
        :param filenames: list of str, list of file name patterns, all files match ANY pattern in this list will be included
        :param opendir: str, the directory to get files
        :param includepattern: list of str, list of wildcard of files that will be loaded, 
            all files match ALL patterns in this list will be included  
        :param excludepattern: list of str, list of wildcard of files that will be blocked,
            any files match ANY patterns in this list will be blocked
        :param fullpath: bool, if true, return the full path of each file
        :param slicemethod: bool, if true use slice method
            The slicemethod is designed to have similar outcomes to Fit2d's 'File Series' methods.
            This produces a set of files which are, within the start stop bounds, and an integer
            mulitple of step from one another.  The structure could be improved by using a start
            and stop file and parse the start and stop file numbers from there.  Additionally,
            this assumes that the defining number is at the end of the file.  Finally, this only
            handles integer numbers, no more complex numbering schemes.
        
        :return: set of str, a list of filenames
        '''
        filenames = self.filenames if filenames == None else filenames
        opendir = self.opendirectory if opendir == None else opendir
        includepattern = self.includepattern if includepattern == None else includepattern
        excludepattern = self.excludepattern if excludepattern == None else excludepattern
        # filter the filenames according to include and exclude pattern
        filelist = os.listdir(opendir)
        fileset = set()
        for includep in includepattern:
            fileset |= set(fnmatch.filter(filelist, includep))
        for excludep in excludepattern:
            fileset -= set(fnmatch.filter(filelist, excludep))
        # filter by slicemethod
        if slicemethod:
            i=start
            fileset2=set()
            while i<=stop:
                for filename in fileset:
                    shortfile, fileExtension = os.path.splitext(filename)
                    if shortfile.endswith(str(i)):
                        filelist.append(filename)
                        i+=step
            fileset = set(filelist)
        else:
            # filter the filenames according to filenames
            if len(filenames) > 0:
                fileset1 = set()
                for filename in filenames:
                    fileset1 |= set(fnmatch.filter(fileset, filename))
                fileset = fileset1
            if fullpath:
                filelist = map(lambda x: os.path.abspath(os.path.join(opendir, x)), fileset)
                fileset = set(filelist)
        return fileset
