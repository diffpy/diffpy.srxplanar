#!/usr/bin/env python
##############################################################################
#
# diffpy.confutils  by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2012 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Xiaohao Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Package for organizing program configurations. It can read/write
configurations file, parse arguments from command lines, and also parse
arguments passed from method/function calling inside python.

Note: for python 2.6, argparse and orderedDict is required, install them with
easy_install
"""


import argparse
import os
from collections import OrderedDict
from configparser import ConfigParser

from diffpy.confutils.tools import FakeConfigFile, StrConv, opt2Str, str2Opt


class ConfigBase(object):
    """_optdatalist_default, _optdatalist are metadata used to
    initialize the options, see below for examples.

    options presents in --help (in cmd), config file,
    headers have same order as in these list,
    so arrange them in right order here.

    optional args to control if the options presents in args, config file or
    file header

    'args' - default is 'a'
        if 'a', this option will be available in self.args
        if 'n', this option will not be available in self.args
    'config' - default is 'a'
        if 'f', this option will present in self.config and be written to
        config file only in full mode
        if 'a', this option will present in self.config and be written to
        config file both in full and short mode
        if 'n', this option will not present in self.config
    'header' - default is 'a'
        if 'f', this option will be written to header only in full mode
        if 'a', this option will be written to header both in full and short
        mode
        if 'n', this option will not be written to header

    so in short mode, all options with 'a' will be written, in full mode,
    all options with 'a' or 'f' will be written
    """

    # Text to display before the argument help
    _description = """Description of configurations
    """
    # Text to display after the argument help
    _epilog = """
    """

    """
    optdata contains these keys:
    these args will be passed to argparse, see the documents of argparse for
    detail information

    'f': full, (positional)
    's': short
    'h': help
    't': type
    'a': action
    'n': nargs
    'd': default
    'c': choices
    'r': required
    'de': dest
    'co': const
    """
    _optdatanamedict = {
        "h": "help",
        "t": "type",
        "a": "action",
        "n": "nargs",
        "d": "default",
        "c": "choices",
        "r": "required",
        "de": "dest",
        "co": "const",
    }

    # examples, overload it
    _optdatalist_default = [
        [
            "configfile",
            {
                "sec": "Control",
                "config": "f",
                "header": "n",
                "s": "c",
                "h": "name of input config file",
                "d": "",
            },
        ],
        [
            "createconfig",
            {
                "sec": "Control",
                "config": "n",
                "header": "n",
                "h": (
                    "create a config file according to default"
                    "or current values"
                ),
                "d": "",
            },
        ],
        [
            "createconfigfull",
            {
                "sec": "Control",
                "config": "n",
                "header": "n",
                "h": "create a full configurable config file",
                "d": "",
            },
        ],
    ]
    # examples, overload it
    _optdatalist = [
        [
            "tifdirectory",
            {
                "sec": "Experiment",
                "header": "n",
                "s": "tifdir",
                "h": "directory of raw tif files",
                "d": "currentdir",
            },
        ],
        [
            "integrationspace",
            {
                "sec": "Experiment",
                "h": "integration space, could be twotheta or qspace",
                "d": "twotheta",
                "c": ["twotheta", "qspace"],
            },
        ],
        [
            "wavelength",
            {
                "sec": "Experiment",
                "h": "wavelength of x-ray, in A",
                "d": 0.1000,
            },
        ],
        [
            "rotationd",
            {
                "sec": "Experiment",
                "s": "rot",
                "h": "rotation angle of tilt plane, in degree",
                "d": 0.0,
            },
        ],
        [
            "includepattern",
            {
                "sec": "Beamline",
                "s": "ipattern",
                "h": "file name pattern for included files",
                "n": "*",
                "d": ["*.tif"],
            },
        ],
        [
            "excludepattern",
            {
                "sec": "Beamline",
                "s": "epattern",
                "h": "file name pattern for excluded files",
                "n": "*",
                "d": ["*.dark.tif", "*.raw.tif"],
            },
        ],
        [
            "fliphorizontal",
            {
                "sec": "Beamline",
                "h": "flip the image horizontally",
                "n": "?",
                "co": True,
                "d": False,
            },
        ],
        [
            "regulartmatrixenable",
            {
                "sec": "Others",
                "h": "normalize tmatrix in splitting method",
                "n": "?",
                "co": True,
                "d": False,
            },
        ],
        [
            "maskedges",
            {
                "sec": "Others",
                "config": "f",
                "header": "f",
                "h": (
                    "mask the edge pixels, first four means"
                    " the number of pixels masked in each edge \n"
                    " (left, right, top, bottom),"
                    " the last one is the radius of a region"
                    " masked around the corner"
                ),
                "n": 5,
                "d": [1, 1, 1, 1, 50],
            },
        ],
    ]

    # some default data
    # configfile: default config file name
    # headertitle: default title of header
    _defaultdata = {
        "configfile": ["config.cfg"],
        "headertitle": "Configuration information",
    }

    def __init__(self, filename=None, args=None, **kwargs):
        """Init the class and update the values of options if specified
        in filename/args/kwargs.

        it will:
            1. call self._preInit method
            2. find the config file if specified in filename/args/kwargs
                if failed, try to find default config file
            3. update the options value using filename/args/kwargs
                file > args > kwargs

        :param filename: str, file name of the config file
        :param args: list of str, args passed from cmd
        :param kwargs: dict, optional kwargs

        :return: None
        """
        # call self._preInit
        self._preInit(**kwargs)

        # update config, first detect if a default config should be load
        filename = self._findDefaultConfigFile(filename, args, **kwargs)
        self.updateConfig(filename, args, **kwargs)
        return

    # example, overload it
    def _preInit(self, **kwargs):
        """Method called in init process, overload it!

        this method will be called before reading config from
        file/args/kwargs
        """
        # for name in ['rotation']:
        #    setattr(self.__class__, name, _configPropertyRad(name+'d'))
        # self._configlist['Experiment'].extend(['rotation'])
        return

    ###########################################################################

    def _findConfigFile(self, filename=None, args=None, **kwargs):
        """Find config file, if any config is specified in
        filename/args/kwargs then return the filename of config.

        :param filename: str, file name of config file
        :param filename: list of str, args passed from cmd
        :param kwargs: optional kwargs
        :return: name of config file if found, otherwise None
        """
        rv = None
        if filename is not None:
            rv = filename
        if args is not None:
            if ("--configfile" in args) or ("-c" in args):
                obj = self.args.parse_args(args)
                rv = obj.configfile
        if kwargs.has_key("configfile"):
            rv = kwargs["configfile"]
        return rv

    def _findDefaultConfigFile(self, filename=None, args=None, **kwargs):
        """Find default config file, if any config is specified in
        filename/args/kwargs or in self._defaultdata['configfile'], then
        return the filename of config.

        kwargs > args > filename > default

        param filename: str, file name of config file
        param filename: list of str, args passed from cmd
        param kwargs: optional kwargs

        return: name of config file if found, otherwise None
        """
        rv = self._findConfigFile(filename, args, **kwargs)
        if rv is None:
            for dconf in self._defaultdata["configfile"]:
                if (os.path.exists(dconf)) and (rv is None):
                    rv = dconf
        return rv

    ###########################################################################

    def _updateSelf(self, optnames=None, **kwargs):
        """Update the options value, then copy the values in the
        self.'options' to self.config.

        1. call self._preUpdateSelf
        2. apply options' value from *self.option* to self.config
        3. call self._postUpdateSelf

        :param optnames: str or list of str, name of options whose value has
        been changed, if None, update all options
        """
        # so some check right here
        self._preUpdateSelf(**kwargs)
        # copy value to self.config
        self._copySelftoConfig(optnames)
        # so some check right here
        self._postUpdateSelf(**kwargs)
        return

    # example, overload it
    def _preUpdateSelf(self, **kwargs):
        """Additional process called in self._updateSelf, this method is
        called before self._copySelftoConfig(), i.e. before copy options
        value to self.config (config file)"""
        return

    def _postUpdateSelf(self, **kwargs):
        """Additional process called in self._updateSelf, this method is
        called after self._copySelftoConfig(), i.e. before copy options
        value to self.config (config file)"""
        return

    ###########################################################################

    def _getTypeStr(self, optname):
        """Return the type of option.

        :param optname: str, name of option
        :return: string, type of the option
        """
        opttype = self._getTypeStrC(optname)
        return opttype

    @classmethod
    def _getTypeStrC(cls, optname):
        """Class method, return the type of option first try to get type
        information from metadata, if failed, try to get type from
        default value.

        :param optname: str, name of option
        :return: string, type of the option
        """
        optdata = cls._optdata[optname]
        if "t" in optdata:
            opttype = optdata["t"]
        else:
            value = optdata["d"]
            if isinstance(value, str):
                opttype = "str"
            elif isinstance(value, bool):
                opttype = "bool"
            elif isinstance(value, float):
                opttype = "float"
            elif isinstance(value, int):
                opttype = "int"
            elif isinstance(value, list):
                if len(value) == 0:
                    opttype = "strlist"
                elif isinstance(value[0], str):
                    opttype = "strlist"
                elif isinstance(value[0], bool):
                    opttype = "boollist"
                elif isinstance(value[0], float):
                    opttype = "floatlist"
                elif isinstance(value[0], int):
                    opttype = "intlist"

        return opttype

    ###########################################################################

    def _detectAddSections(self):
        """Detect sections present in self._optdata and add them to
        self.config also add it to self._configlist."""
        self._detectAddSectionsC(self)
        return

    @classmethod
    def _detectAddSectionsC(cls):
        """Class method, detect sections present in self._optdata and
        add them to self.config also add it to self._configlist."""
        # seclist = [self._optdata[key]['sec'] for key in self._optdata.keys()]
        seclist = [cls._optdata[opt[0]]["sec"] for opt in cls._optdatalist]
        secdict = OrderedDict.fromkeys(seclist)
        # for sec in set(seclist):
        for sec in secdict.keys():
            cls.config.add_section(sec)
            cls._configlist[sec] = []
        return

    def _addOpt(self, optname):
        """Add options to self.config and self.args and self.*option*,
        this will read metadata from self._optdatalist.

        :param optname: string, name of option
        """
        self._addOptC(self, optname)
        return

    @classmethod
    def _addOptC(cls, optname):
        """Class method, add options to self.config and self.args and
        self.*option*, this will read metadata in self._optdatalist.

        :param optname: string, name of option
        """
        optdata = cls._optdata[optname]
        opttype = cls._getTypeStrC(optname)

        # replace currentdir in default to os.getcwd()
        if optdata["d"] == "currentdir":
            optdata["d"] = os.getcwd()

        # add to cls.'optname'
        cls._addOptSelfC(optname, optdata)

        # add to cls.config
        secname = optdata["sec"] if "sec" in optdata else "Others"
        cls._configlist[secname].append(optname)
        if optdata.get("config", "a") != "n":
            strvalue = (
                ", ".join(map(str, optdata["d"]))
                if isinstance(optdata["d"], list)
                else str(optdata["d"])
            )
            cls.config.set(secname, optname, strvalue)
        # add to cls.args
        if optdata.get("args", "a") != "n":
            # transform optdata to a dict that can pass to add_argument method
            pargs = dict()
            for key in optdata.keys():
                if key in cls._optdatanamedict:
                    pargs[cls._optdatanamedict[key]] = optdata[key]
            pargs["default"] = argparse.SUPPRESS
            pargs["type"] = StrConv(opttype)
            # add args
            if "f" in optdata:
                cls.args.add_argument(optname, **pargs)
            elif "s" in optdata:
                cls.args.add_argument(
                    "--" + optname, "-" + optdata["s"], **pargs
                )
            else:
                cls.args.add_argument("--" + optname, **pargs)
        return

    @classmethod
    def _addOptSelfC(cls, optname, optdata):
        """Class method, assign options value to *self.option*, using
        metadata.

        :param optname: string, name of the option
        :param optdata: dict, metadata of the options, get it from
            self._optdatalist
        """
        setattr(cls, optname, optdata["d"])
        return

    def _copyConfigtoSelf(self, optnames=None):
        """Copy the options' value from self.config to self.*option*

        :param optnames: str or list of str, names of options whose
            value copied from self.config to self.*option*'. Set None to
            update all
        """
        if optnames is not None:
            optnames = optnames if isinstance(optnames, list) else [optnames]
        else:
            optnames = []
            for secname in self.config.sections():
                optnames += self.config.options(secname)

        for optname in optnames:
            if self._optdata.has_key(optname):
                secname = self._optdata[optname]["sec"]
                opttype = self._getTypeStr(optname)
                optvalue = self.config.get(secname, optname)
                setattr(self, optname, str2Opt(opttype, optvalue))
        return

    def _copySelftoConfig(self, optnames=None):
        """Copy the value from self.*option* to self.config.

        :param optname: str or list of str, names of options whose value
            copied from self.*option* to self.config. Set None to update
            all
        """
        if optnames is not None:
            optnames = optnames if isinstance(optnames, list) else [optnames]
        else:
            optnames = []
            for secname in self.config.sections():
                optnames += self.config.options(secname)

        for optname in optnames:
            if self._optdata.has_key(optname):
                secname = self._optdata[optname]["sec"]
                opttype = self._getTypeStr(optname)
                optvalue = getattr(self, optname)
                self.config.set(secname, optname, opt2Str(opttype, optvalue))
        return

    ###########################################################################

    def parseArgs(self, pargs):
        """Parse args and update the value in self.*option*, this will
        call the self.args() to parse args,

        :param pargs: list of string, arguments to parse, usually coming
            from sys.argv
        """
        obj = self.args.parse_args(pargs)
        changedargs = obj.__dict__.keys()
        for optname in changedargs:
            if self._optdata.has_key(optname):
                setattr(self, optname, getattr(obj, optname))
        # update self
        if len(changedargs) > 0:
            self._updateSelf(changedargs)
        return obj

    def parseKwargs(self, **kwargs):
        """Update self.*option* values according to the kwargs.

        :param kwargs: dict, keywords=value
        """
        if kwargs != {}:
            changedargs = []
            for optname, optvalue in kwargs.iteritems():
                if self._optdata.has_key(optname):
                    setattr(self, optname, optvalue)
                    changedargs.append(optname)
            # update self
            self._updateSelf(changedargs)
        return

    def parseConfigFile(self, filename):
        """Read a config file and update the self.*option*

        :param filename: str, file name of config file (include path)
        """
        if filename is not None:
            filename = os.path.abspath(filename)
            if os.path.exists(filename):
                self.configfile = filename
                self._copySelftoConfig()
                fileobj = FakeConfigFile(filename)
                # self.config.read(filename)
                self.config.readfp(fileobj)
                self._copyConfigtoSelf()
                self._updateSelf()
        return

    def updateConfig(self, filename=None, args=None, **kwargs):
        """Update config according to a config file, args (from
        ``sys.argv``), or ``**kwargs``.

        Steps:
          1. call ``self._preUpdateConfig()``
          2. process file/args/kwargs passed to this method
          3. read a config file if specified in ``args`` or ``kwargs``
          4. call ``self._postUpdateConfig()``
          5. write config file if specified in ``args``/``kwargs``

        :param filename: str, file name of the config file
        :param args: list of str, args passed from cmd
        :param kwargs: dict, optional keyword arguments
        :return: True if anything updated, False if nothing updated
        """

        # call self._preUpdateConfig
        self._preUpdateConfig(**kwargs)

        filename = self._findConfigFile(filename, args, **kwargs)
        if filename is not None:
            rv = self.parseConfigFile(filename)
        if args is not None:
            rv = self.parseArgs(args)
        if kwargs != {}:
            rv = self.parseKwargs(**kwargs)

        if (
            (filename is None)
            and ((args is None) or (args == []))
            and (kwargs == {})
        ):
            rv = self._updateSelf()

        # call self._callbackUpdateConfig
        self._postUpdateConfig(**kwargs)

        # write config file
        self._createConfigFile()
        return rv

    def _preUpdateConfig(self, **kwargs):
        """Method called before parsing args or kwargs or config file,
        in self.updateConfig."""
        return

    def _postUpdateConfig(self, **kwargs):
        """Method called after parsing args or kwargs or config file, in
        self.updateConfig."""
        return

    ###########################################################################
    def _createConfigFile(self):
        """Write output config file if specified in configuration the
        filename is specified by self.createconfig."""
        if (self.createconfig != "") and (self.createconfig is not None):
            self.writeConfig(self.createconfig, "short")
            self.createconfig = ""
        if (self.createconfigfull != "") and (
            self.createconfigfull is not None
        ):
            self.writeConfig(self.createconfigfull, "full")
            self.createconfigfull = ""
        return

    def writeConfig(self, filename, mode="short", changeconfigfile=True):
        """Write config to file. the file is compatible with python
        package ConfigParser.

        :param filename: string, name of file
        :param mode: string, 'short' or 'full' ('s' or 'f'). in short
            mode, all options with 'a' will be written, in full mode,
            all options with 'a' or 'f' will be written
        """
        if changeconfigfile:
            self.configfile = os.path.abspath(filename)
        self._updateSelf()
        # func decide if write the option to config according to mode
        # options not present in self._optdata will not be written to config
        if mode.startswith("s"):
            mcond = (
                lambda optname: self._optdata.get(
                    optname, {"config": "n"}
                ).get("config", "a")
                == "a"
            )
        else:
            mcond = (
                lambda optname: self._optdata.get(
                    optname, {"config": "n"}
                ).get("config", "a")
                != "n"
            )

        lines = []
        for section in self.config._sections:
            tlines = []
            for key, value in self.config._sections[section].items():
                if (key != "__name__") and mcond(key):
                    tlines.append(
                        "%s = %s" % (key, str(value).replace("\n", "\n\t"))
                    )
            if len(tlines) > 0:
                lines.append("[%s]" % section)
                lines.extend(tlines)
                lines.append("")
        rv = "\n".join(lines) + "\n"
        fp = open(filename, "w")
        fp.write(rv)
        fp.close()
        return

    def getHeader(self, title=None, mode="full"):
        """Get a header of configurations values,

        :param title: str, title of header, if None, try to get it from
            self.defaultvalue
        :param mode: string, 'short' or 'full' ('s' or 'f'). in short
            mode, all options with 'a' will be written, in full mode,
            all options with 'a' or 'f' will be written
        :return: string, lines with line break that can be directly
            written to a text file
        """

        lines = []
        title = "# %s #" % (
            self._defaultdata["headertitle"] if title is None else title
        )
        lines.append(title)
        # func decide if write the option to header according to mode
        # options not present in self._optdata will not be written to header
        if mode.startswith("s"):
            mcond = (
                lambda optname: self._optdata.get(
                    optname, {"header": "n"}
                ).get("header", "a")
                == "a"
            )
        else:
            mcond = (
                lambda optname: self._optdata.get(
                    optname, {"header": "n"}
                ).get("header", "a")
                != "n"
            )

        for secname in self._configlist.keys():
            tlines = []
            for optname in self._configlist[secname]:
                if mcond(optname):
                    value = getattr(self, optname)
                    ttype = self._getTypeStr(optname)
                    strvalue = (
                        ", ".join(map(str, value))
                        if ttype.endswith("list")
                        else str(value)
                    )
                    tlines.append("%s = %s" % (optname, strvalue))
            if len(tlines) > 0:
                lines.append("[%s]" % secname)
                lines.extend(tlines)
                lines.append("")
        rv = "\n".join(lines) + "\n"
        return rv

    def resetDefault(self, optnames=None):
        """Reset all values to their default value.

        :param optnames: list of str, name of options to reset, None for
            all options
        """
        if optnames is None:
            optnames = self._optdata.keys()
        for optname in optnames:
            if self._optdata.has_key(optname):
                setattr(self, optname, self._optdata[optname]["d"])
        self._updateSelf()
        return

    ###########################################################################
    # IMPORTANT call this method if you want to add options
    # as class attributes!!!

    @classmethod
    def initConfigClass(cls):
        """Init config class and add options to class.

        IMPORTANT: call this method after you define
        the metadata of your config class to add options as class attributes!!!
        """
        cls._preInitConfigClass()

        cls.config = ConfigParser(dict_type=OrderedDict)
        cls.args = argparse.ArgumentParser(
            description=cls._description,
            epilog=cls._epilog,
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        cls._configlist = OrderedDict({})

        cls._optdatalist = cls._optdatalist_default + cls._optdatalist
        cls._optdata = dict(cls._optdatalist)
        cls._detectAddSectionsC()
        for opt in cls._optdatalist:
            key = opt[0]
            cls._addOptC(key)

        cls._postInitConfigClass()
        return

    @classmethod
    def _postInitConfigClass(cls):
        """Additional processes called after initConfigClass.

        overload it
        """
        pass

    @classmethod
    def _preInitConfigClass(cls):
        """Additional processes called before initConfigClass.

        overload it
        """
        pass


# VERY IMPORTANT!!!
# add options to class
# initConfigClass(ConfigBase)
# ConfigBase.initConfigClass()

if __name__ == "__main__":

    test = ConfigBase()
    test.updateConfig()
