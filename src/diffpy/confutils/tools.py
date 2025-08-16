#!/usr/bin/env python
##############################################################################
#
# diffpy.confutils  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2013 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

import numpy as np
import re
import time
import zlib
import hashlib

def _configPropertyRad(nm):
    '''
    helper function of options delegation, rad to degree
    '''
    rv = property(fget=lambda self: np.radians(getattr(self, nm)),
                  fset=lambda self, val: setattr(self, nm, np.degrees(val)),
                  fdel=lambda self: delattr(self, nm))
    return rv

def _configPropertyR(name):
    '''
    Create a property that forwards self.name to self.config.name.
    
    read only
    '''
    rv = property(fget=lambda self: getattr(self.config, name),
            doc='attribute forwarded to self.config, read-only')
    return rv

def _configPropertyRW(name):
    '''
    Create a property that forwards self.name to self.config.name.
    
    read and write
    '''
    rv = property(fget=lambda self: getattr(self.config, nm),
                  fset=lambda self, value: setattr(self.config, nm, value),
                  fdel=lambda self: delattr(self, nm),
                  doc='attribute forwarded to self.config, read/write')
    return rv

def str2bool(v):
    '''
    turn string to bool
    '''
    return v.lower() in ("yes", "true", "t", "1")

def opt2Str(opttype, optvalue):
    '''
    turn the value of one option to string, according to the option type
    list of values are truned into "value1, value2, value3..."
    
    :param opttype: string, type of opitons, for example 'str' or 'intlist'
    :param optvalue: value of the option
    
    :return: string, usually stored in ConfigBase.config
    '''

    if opttype.endswith('list'):
        rv = ', '.join(map(str, optvalue))
    else:
        rv = str(optvalue)
    return rv

def StrConv(opttype):
    '''
    get the type (a converter function) according to the opttype
    
    the function doesn't take list
    
    :param opttype: string, a type of options, could be 'str', 'int',
        'float', or 'bool'
        
    :return: type (converter function) 
    
    '''
    if opttype.startswith('str'):
        conv = str
    elif opttype.startswith('int'):
        conv = int
    elif opttype.startswith('float'):
        conv = float
    elif opttype.startswith('bool'):
        conv = str2bool
    else:
        conv = None
    return conv

def str2Opt(opttype, optvalue):
    '''
    convert the string to value of one option, according to the option type
    
    :param opttype: string, type of opitons, for example 'str' or 'intlist'
    :param optvalue: string, value of the option
    
    :return: value of the option, usually stored in ConfigBase.config
    '''
    # base converter
    conv = StrConv(opttype)
    if opttype.endswith('list'):
        temp = re.split('\s*,\s*', optvalue)
        rv = map(conv, temp) if len(temp) > 0 else []
    else:
        rv = conv(optvalue)
    return rv

class FakeConfigFile(object):
    '''
    A fake configfile object used in reading config from header of data
    or a real config file. 
    '''
    def __init__(self, configfile, endline='###'):
        self.configfile = configfile
        self.fp = open(configfile)
        self.endline = endline
        self.ended = False
        self.name = configfile
        return

    def readline(self):
        '''
        readline function
        '''
        line = self.fp.readline()
        if line.startswith(self.endline) or self.ended:
            rv = ''
            self.ended = True
        else:
            rv = line
        return rv

    def close(self):
        '''
        close the file
        '''
        self.fp.close()
        return

def checkCRC32(filename):
    '''
    calculate the crc32 value of file
    
    :param filename: path to the file
    
    :return: crc32 value of file
    '''
    try:
        fd = open(filename, 'rb')
    except:
        return 'Read error'
    eachLine = fd.readline()
    prev = 0
    while eachLine:
        prev = zlib.crc32(eachLine, prev)
        eachLine = fd.readline()
    fd.close()
    return prev

def checkMD5(filename, blocksize=65536):
    '''
    calculate the MD5 value of file
    
    :param filename: path to the file
    
    :return: md5 value of file
    '''
    try:
        fd = open(filename, 'rb')
    except:
        return 'Read error'
    buf = fd.read(blocksize)
    md5 = hashlib.md5()
    while len(buf) > 0:
        md5.update(buf)
        buf = fd.read(blocksize)
    fd.close()
    return md5.hexdigest()

def checkFileVal(filename):
    '''
    check file integrity using crc32 and md5. It will read file twice then
    compare the crc32 and md5. If two results doesn't match, it will wait until 
    the file is completed written to disk.
    
    :param filename: path to the file
    '''
    valflag = False
    lastcrc = checkCRC32(filename)
    while not valflag:
        currcrc = checkCRC32(filename)
        if currcrc == lastcrc:
            lastmd5 = checkMD5(filename)
            time.sleep(0.01)
            currmd5 = checkMD5(filename)
            if lastmd5 == currmd5:
                valflag = True
        else:
            time.sleep(0.5)
            lastcrc = checkCRC32(filename)
    return
