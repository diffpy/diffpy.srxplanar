#!/usr/bin/env python

# Installation script for diffpy.Structure

"""srxplanar - 2D diffraction image integration and uncertainty propagation
using non splitting pixel algorithm

Packages:   diffpy.srxplanar
"""

import os
from setuptools import setup, find_packages

# define distribution
setup_args = dict(
        name="diffpy.srxplanar",
        namespace_packages=['diffpy'],
        packages=find_packages(),
        include_package_data=True,
        zip_safe=False,
        entry_points={
            # define console_scripts here, see setuptools docs for details.
            'console_scripts' : ['srxplanar = diffpy.srxplanar.srxplanar:main'
                                 ],
                        },

        author='Simon J.L. Billinge',
        author_email='sb2896@columbia.edu',
        maintainer='Xiaohao Yang',
        maintainer_email='sodestiny1@gmail.com',
        url='https://github.com/diffpy/diffpy.srxplanar',
        description="2D diffraction image integration and uncertainty propagation",
        license='BSD-style license',
        keywords="diffpy planar integration non-splitting uncertainty",
        classifiers=[
            # List of possible values at
            # http://pypi.python.org/pypi?:action=list_classifiers
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Science/Research',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Operating System :: Unix',
            'Programming Language :: Python :: 2.6',
            'Programming Language :: Python :: 2.7',
            'Topic :: Scientific/Engineering :: Chemistry',
            'Topic :: Scientific/Engineering :: Physics',
        ],
)

if __name__ == '__main__':
    setup(**setup_args)

# End of file
