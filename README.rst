|Icon| |title|_
===============

.. |title| replace:: diffpy.srxplanar
.. _title: https://diffpy.github.io/diffpy.srxplanar

.. |Icon| image:: https://avatars.githubusercontent.com/diffpy
        :target: https://diffpy.github.io/diffpy.srxplanar
        :height: 100px

|PyPI| |Forge| |PythonVersion| |PR|

|CI| |Codecov| |Black| |Tracking|

.. |Black| image:: https://img.shields.io/badge/code_style-black-black
        :target: https://github.com/psf/black

.. |CI| image:: https://github.com/diffpy/diffpy.cmi/actions/workflows/matrix-and-codecov-on-merge-to-main.yml/badge.svg
        :target: https://github.com/diffpy/diffpy.srxplanar/actions/workflows/matrix-and-codecov-on-merge-to-main.yml

.. |Codecov| image:: https://codecov.io/gh/diffpy/diffpy.srxplanar/branch/main/graph/badge.svg
        :target: https://codecov.io/gh/diffpy/diffpy.srxplanar

.. |Forge| image:: https://img.shields.io/conda/vn/conda-forge/diffpy.srxplanar
        :target: https://anaconda.org/conda-forge/diffpy.srxplanar

.. |PR| image:: https://img.shields.io/badge/PR-Welcome-29ab47ff
        :target: https://github.com/diffpy/diffpy.srxplanar/pulls

.. |PyPI| image:: https://img.shields.io/pypi/v/diffpy.srxplanar
        :target: https://pypi.org/project/diffpy.srxplanar/

.. |PythonVersion| image:: https://img.shields.io/pypi/pyversions/diffpy.srxplanar
        :target: https://pypi.org/project/diffpy.srxplanar/

.. |Tracking| image:: https://img.shields.io/badge/issue_tracking-github-blue
        :target: https://github.com/diffpy/diffpy.srxplanar/issues

This is part of xPDFsuite package.

diffpy.srxplanar package provides 2D diffraction image integration using
non splitting pixel algorithm. And it can estimate and propagate statistic
uncertainty of raw counts and integrated intensity.

To learn more about diffpy.srxplanar library, see the examples directory
included in this distribution or the API documentation at

http://diffpy.github.io/diffpy.srxplanar/

For more information about the diffpy.srxplanar library, please consult our `online documentation <https://diffpy.github.io/diffpy.srxplanar>`_.

Citation
--------

If you use this program to do productive scientific research that
leads to publication, we kindly ask that you acknowledge use of the program
by citing the following paper in your publication:

    Xiaohao Yang, Pavol Juhas, Simon J. L. Billinge, On the estimation of
    statistical uncertainties on powder diffraction and small angle
    scattering data from 2-D x-ray detectors, arXiv:1309.3614

Installation
------------

The preferred method is to use `Miniconda Python
<https://docs.conda.io/projects/miniconda/en/latest/miniconda-install.html>`_
and install from the "conda-forge" channel of Conda packages.

To add "conda-forge" to the conda channels, run the following in a terminal. ::

        conda config --add channels conda-forge

We want to install our packages in a suitable conda environment.
The following creates and activates a new environment named ``diffpy.srxplanar_env`` ::

        conda create -n diffpy.srxplanar_env diffpy.srxplanar
        conda activate diffpy.srxplanar_env

To confirm that the installation was successful, type ::

        python -c "import diffpy.srxplanar; print(diffpy.srxplanar.__version__)"

The output should print the latest version displayed on the badges above.

If the above does not work, you can use ``pip`` to download and install the latest release from
`Python Package Index <https://pypi.python.org>`_.
To install using ``pip`` into your ``diffpy.srxplanar_env`` environment, type ::

        pip install diffpy.srxplanar

If you prefer to install from sources, after installing the dependencies, obtain the source archive from
`GitHub <https://github.com/diffpy/diffpy.srxplanar/>`_. Once installed, ``cd`` into your ``diffpy.srxplanar`` directory
and run the following ::

        pip install .

This package also provides command-line utilities. To check the software has been installed correctly, type ::

        srxplanar --version

You can also type the following command to verify the installation. ::

        python -c "import diffpy.srxplanar; print(diffpy.srxplanar.__version__)"


To view the basic usage and available commands, type ::

        srxplanar -h

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
