#!/usr/bin/env python
##############################################################################
#
# diffpy.confutils  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSENOTICE.txt for license information.
#
##############################################################################

"""Convenience module for executing all unit tests with

python -m diffpy.confutils.tests.run
"""


if __name__ == '__main__':
    import sys
    from diffpy.confutils.tests import test
    # produce zero exit code for a successful test
    sys.exit(not test().wasSuccessful())

# End of file