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
"""Definition of __version__, __date__, __gitsha__."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("diffpy.srxplanar")
except PackageNotFoundError:
    __version__ = "unknown"


# End of file
