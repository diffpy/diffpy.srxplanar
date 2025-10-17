diffpy.srxplanar
========================================================================

diffpy.srxplanar package provides 2D diffraction image integration using
non splitting pixel algorithm. And it can estimate and propagate statistic
uncertainty of raw counts and integrated intensity. If you are using this
software. If you use this program to do productive scientific research that
leads to publication, we kindly ask that you acknowledge use of the program
by citing the following paper in your publication:

    Xiaohao Yang, Pavol Juhas, Simon J. L. Billinge, On the estimation of
    statistical uncertainties on powder diffraction and small angle
    scattering data from 2-D x-ray detectors, arXiv:1309.3614

To learn more about diffpy.srxplanar library, see the examples directory
included in this distribution or the API documentation at

http://diffpy.github.io/diffpy.srxplanar/

REQUIREMENTS
------------------------------------------------------------------------

The diffpy.srxplanar requires Python 2.6 or 2.7 and the following software:

* `setuptools`  >=0.61(https://pypi.python.org/pypi/setuptools)
* `numpy`       >=1.60(http://www.numpy.org/)
* `scipy`       >=1.10(www.scipy.org/)
* `FabIO`       >=0.80(http://sourceforge.net/projects/fable/files/fabio/)

If your python version < 2.7 (these two packages are included in 2.7 but not in 2.6)

* `ordereddict` https://pypi.python.org/pypi/ordereddict
* `argparse`    https://pypi.python.org/pypi/argparse

On Ubuntu Linux the part of required software can be easily installed using
the system package manager::

    sudo aptitude install \
        python-setuptools python-numpy python-scipy

For Mac OS X machine with the MacPorts package manager one could do::

    sudo port install \
        python27 py27-setuptools py27-numpy py27-scipy

When installing with MacPorts, make sure the MacPorts bin directory is the
first in the system PATH and that python27 is selected as the default
Python version in MacPorts::

    sudo port select --set python python27

For other Linux distributions use their respective package manager; note
the packages may have slightly different names. diffpy.srxplanar should work
on other Unix-like operating systems as well.  Please, search the
web for instructions how to install external dependencies on your particular
system.

For other packages, please go to the webpage list above to download and install.


INSTALLATION
------------------------------------------------------------------------

To install the diffpy.srxplanar package::

    python setup.py install

By default the files are installed in the system directories, which are
usually only writeable by the root.  See the usage info
"./setup.py install --help" for options to install as a normal user under
different location.  Note that installation to non-standard directories may
require adjustments to the PATH and PYTHONPATH environment variables.

DEVELOPMENT
------------------------------------------------------------------------

diffpy.srxplanar is an open-source software developed at the Columbia University
The diffpy.srxplanar sources are hosted at

https://github.com/diffpy/diffpy.srxplanar

Feel free to fork the project and contribute.  To install diffpy.srxplanar
in a development mode, where the sources are directly used by Python
rather than copied to a system directory, use::

    python setup.py develop --user

CONTACTS
------------------------------------------------------------------------

For more information on diffpy.srxplanar please visit the project web-page:

http://www.diffpy.org/

or email Prof. Simon Billinge at sb2896@columbia.edu
