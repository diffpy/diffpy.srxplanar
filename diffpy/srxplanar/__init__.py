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

from .._version import get_versions
__version__ = get_versions()['version']
del get_versions

# some convenience imports
from diffpy.srxplanar.srxplanar import SrXplanar
from diffpy.srxplanar.srxplanarconfig import SrXplanarConfig

# unit tests


# End of file
