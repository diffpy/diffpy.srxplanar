|Icon| |title|_
===============

.. |title| replace:: diffpy.srxplanar
.. _title: https://diffpy.github.io/diffpy.srxplanar

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.srxplanar
        :height: 100px

|PythonVersion| |PR|

|Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.srxplanar/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.srxplanar

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff
        :target: https://github.com/diffpy/diffpy.srxplanar/pulls

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.srxplanar
        :target: https://pypi.org/project/diffpy.srxplanar/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.srxplanar
        :target: https://pypi.org/project/diffpy.srxplanar/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.srxplanar/issues

Distance Printer, calculate the inter atomic distances. Part of xPDFsuite

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

For more information about the diffpy.srxplanar library, please consult our `online documentation <https://diffpy.github.io/diffpy.srxplanar>`_.

Citation
--------

If you use diffpy.srxplanar in a scientific publication, we would like you to cite this package as

        diffpy.srxplanar Package, https://github.com/diffpy/diffpy.srxplanar

Installation
------------

The preferred method is to be installed with `xpdfsuite` package or the wheel file.

This package also provides command-line utilities. To check the software has been installed correctly, type ::

        diffpy.srxplanar --version

You can also type the following command to verify the installation. ::

        python -c "import diffpy.srxplanar; print(diffpy.srxplanar.__version__)"


To view the basic usage and available commands, type ::

        diffpy.srxplanar -h

Getting Started
---------------

You may consult our `online documentation <https://diffpy.github.io/diffpy.srxplanar>`_ for tutorials and API references.

Support and Contribute
----------------------

If you see a bug or want to request a feature, please `report it as an issue <https://github.com/diffpy/diffpy.srxplanar/issues>`_ and/or `submit a fix as a PR <https://github.com/diffpy/diffpy.srxplanar/pulls>`_.

Feel free to fork the project. To install diffpy.srxplanar
in a development mode, with its sources being directly used by Python
rather than copied to a package directory, use the following in the root
directory ::

        pip install -e .

To ensure code quality and to prevent accidental commits into the default branch, please set up the use of our pre-commit
hooks.

1. Install pre-commit in your working environment by running ``conda install pre-commit``.

2. Initialize pre-commit (one time only) ``pre-commit install``.

Thereafter your code will be linted by black and isort and checked against flake8 before you can commit.
If it fails by black or isort, just rerun and it should pass (black and isort will modify the files so should
pass after they are modified). If the flake8 test fails please see the error messages and fix them manually before
trying to commit again.

Improvements and fixes are always appreciated.

Before contributing, please read our `Code of Conduct <https://github.com/diffpy/diffpy.srxplanar/blob/main/CODE-OF-CONDUCT.rst>`_.

Contact
-------

For more information on diffpy.srxplanar please visit the project `web-page <https://diffpy.github.io/>`_ or email Simon Billinge at sb2896@columbia.edu.

Acknowledgements
----------------

``diffpy.srxplanar`` is built and maintained with `scikit-package <https://scikit-package.github.io/scikit-package/>`_.
