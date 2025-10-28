from functools import partial

import numpy as np
from scipy.optimize import leastsq, minimize

try:
    from matplotlib import rcParams

    rcParams["backend"] = "QtAgg"
    import matplotlib.pyplot as plt

    mplenabled = True
except ImportError:
    mplenabled = False


def halfcut(
    p, srx, image, xycenter, qind=[50, 500], show=False, mode="x", output=0
):
    """Cut the image into two half, integrate them and compare the
    results, if the calibration information is correct, two half should
    give same results.

    :param p: calibration parameters
    :param srx: SrXplanar object, object to do the integration
    :param image: str or 2d array, image to be calibrated
    :param xycenter: [int, int], cut position
    :param qind: [int, int], range of q to calculate the difference
    :param show: bool, True to plot the cut
    :param mode: str, mode of calibration, could be x, y, tilt,
        rotation, all, xy
    :param output: int, 0 to return one number (sum of square of
        difference), 1 to return the difference array
    :return: sum of square of difference or difference array
    """
    if mode == "x":
        srx.updateConfig(xbeamcenter=p)
    elif mode == "y":
        srx.updateConfig(ybeamcenter=p)
    elif mode == "tilt":
        srx.updateConfig(tiltd=p)
    elif mode == "rotation":
        srx.updateConfig(rotationd=p)
    elif mode == "all":
        srx.updateConfig(
            xbeamcenter=p[0], ybeamcenter=p[1], rotationd=p[2], tiltd=p[3]
        )
    elif mode == "xy":
        srx.updateConfig(xbeamcenter=p[0], ybeamcenter=p[1])
    elif mode == "show":
        pass

    srx.prepareCalculation()
    kwargs = {
        "savename": None,
        "savefile": False,
        "flip": False,
        "correction": False,
    }
    if mode != "y":
        srx.config.extracrop = [1, srx.config.xdimension - xycenter[0], 1, 1]
        res1 = srx.integrate(image, **kwargs)
        chi1 = res1["chi"][1][qind[0] : qind[1]]

        srx.config.extracrop = [xycenter[0], 1, 1, 1]
        res2 = srx.integrate(image, **kwargs)
        chi2 = res2["chi"][1][qind[0] : qind[1]]

    if mode != "x":
        srx.config.extracrop = [1, 1, 1, srx.config.ydimension - xycenter[1]]
        res3 = srx.integrate(image, **kwargs)
        chi3 = res3["chi"][1][qind[0] : qind[1]]

        srx.config.extracrop = [1, 1, xycenter[1], 1]
        res4 = srx.integrate(image, **kwargs)
        chi4 = res4["chi"][1][qind[0] : qind[1]]

    if mode == "x":
        rv = chi1 - chi2
        rv = rv / (chi1 + chi2).mean()
    elif mode == "y":
        rv = chi3 - chi4
        rv = rv / (chi3 + chi4).mean()
    else:
        r1 = chi1 - chi2
        r2 = chi3 - chi4
        rv = np.concatenate(
            [r1 / (chi1 + chi2).mean(), r2 / (chi3 + chi4).mean()]
        )

    rv0 = np.sum(rv**2)
    print(p)
    print(rv0)
    if output == 0:
        rv = rv0

    if show and mplenabled:
        print(p)
        print(rv)
        plotRes(mode, res1, res2, res3, res4)
    return rv


def plotRes(mode, res1, res2, res3, res4):
    """Plot results."""
    plt.ion()
    plt.figure(1)
    plt.clf()
    if mode != "y":
        plt.plot(res1["chi"][0], res1["chi"][1], label="left")
        plt.plot(res2["chi"][0], res2["chi"][1], label="right")
    if mode != "x":
        plt.plot(res3["chi"][0], res3["chi"][1], label="up")
        plt.plot(res4["chi"][0], res4["chi"][1], label="down")
    plt.legend()
    plt.show()
    return


def minimize1(func, bounds):
    """1d minimizer.

    :param func: callable function f(x), 1d function
    :param bounds: (float, float), the initial bounds
    :return: float, the value of x
    """
    diffb = np.abs(bounds[1] - bounds[0])
    if diffb > 6:
        trylist = np.linspace(
            bounds[0], bounds[1], 3 * int(bounds[1] - bounds[0]) + 1, True
        )
    else:
        trylist = np.linspace(bounds[0], bounds[1], 21, True)
    vlow = np.inf
    rv = trylist[0]
    for v in trylist:
        temp = func(v)
        if temp < vlow:
            rv = v
            vlow = temp
    if diffb > 6:
        trylist = np.linspace(rv - 0.5, rv + 0.5, 21, True)
    else:
        trylist = np.linspace(rv - diffb / 12.0, rv + diffb / 12.0, 21, True)

    for v in trylist:
        temp = func(v)
        if temp < vlow:
            rv = v
            vlow = temp
    return rv


def selfCalibrateX(
    srx,
    image,
    xycenter=None,
    mode="all",
    output=0,
    showresults=False,
    qrange=[None, None],
    **kwargs,
):
    """Do the self calibration using mode X.

    the initial value is read from the current value of srx object, and
    the refined results will be writrn into the srx object

    :param srx: SrXplanar object, object to do the integration
    :param image: str or 2d array, image to be calibrated
    :param xycenter: [int, int], cut position, if None, determine it
        using current beam center
    :param mode: str, mode of calibration, could be x, y, xy, tilt,
        rotation, all
    :param output: int, 0 to use fmin optimizer, 1 to use leastsq
        optimizer
    :param showresults: bool, plot the halfcut result
    :param qrange: q range used in calculating difference
    :return: list, refined parameter
    """
    bak = {}
    for opt in [
        "uncertaintyenable",
        "integrationspace",
        "qmax",
        "qstep",
        "cropedges",
        "extracrop",
        "brightpixelmask",
        "darkpixelmask",
        "avgmask",
    ]:
        bak[opt] = getattr(srx.config, opt)

    xycenter = [int(srx.config.xbeamcenter), int(srx.config.ybeamcenter)]

    qmax = srx.config.qmax
    # qstep = qmax / 2000
    qstep = qmax / srx.config.xdimension

    srx.updateConfig(
        uncertaintyenable=False,
        integrationspace="qspace",
        # qmax=qmax,
        qstep=qstep,
        brightpixelmask=False,
        darkpixelmask=False,
        avgmask=False,
    )
    # qind = [50, 1000]
    qind = [None, None]
    qind[0] = (
        int(qrange[0] / qstep)
        if qrange[0] is not None
        else srx.config.xdimension / 20
    )
    qind[0] = 0 if qind[0] < 0 else qind[0]
    qind[1] = (
        int(qrange[1] / qstep)
        if qrange[1] is not None
        else srx.config.xdimension / 2
    )
    qind[1] = (
        srx.config.xdimension - 5
        if qind[1] > srx.config.xdimension - 5
        else qind[1]
    )

    srx.prepareCalculation()
    srxconfig = srx.config
    image = np.array(srx._getPic(image))

    func = partial(
        halfcut,
        srx=srx,
        image=image,
        qind=qind,
        mode=mode,
        output=output,
        xycenter=xycenter,
        show=False,
    )

    xywidth = 6 if not kwargs.has_key("xywidth") else kwargs["xywidth"]
    if mode == "x":
        p0 = [srxconfig.xbeamcenter]
        bounds = (p0[0] - xywidth, p0[0] + xywidth)
    elif mode == "y":
        p0 = [srxconfig.ybeamcenter]
        bounds = (p0[0] - xywidth, p0[0] + xywidth)
    elif mode == "tilt":
        p0 = [srxconfig.tiltd]
        bounds = (p0[0] - 5, p0[0] + 5)
    elif mode == "rotation":
        p0 = [srxconfig.rotationd]
        bounds = (0, 360)
    elif mode == "all":
        p0 = [
            srxconfig.xbeamcenter,
            srxconfig.ybeamcenter,
            srxconfig.rotationd,
            srxconfig.tiltd,
        ]
        bounds = [
            [p0[0] - xywidth, p0[0] + xywidth],
            [p0[1] - xywidth, p0[1] + xywidth],
            [0, 360],
            [srxconfig.tiltd - 10, srxconfig.tiltd + 10],
        ]
    elif mode == "xy":
        p0 = [srxconfig.xbeamcenter, srxconfig.ybeamcenter]
        bounds = [
            [p0[0] - xywidth, p0[0] + xywidth],
            [p0[1] - xywidth, p0[1] + xywidth],
        ]

    if output == 0:
        if mode in ["x", "y", "tilt", "rotation"]:
            rv = minimize1(func, bounds)
            p = [rv]
        else:
            rv = minimize(
                func,
                p0,
                method="Powell",
                bounds=bounds,
                options={"xtol": 0.001, "ftol": 0.001},
            )
            p = rv.x
    else:
        rv = leastsq(func, p0, epsfcn=0.001)
        p = rv[0]

    print(p)
    if mode == "x":
        srx.updateConfig(xbeamcenter=p[0], **bak)
    elif mode == "y":
        srx.updateConfig(ybeamcenter=p[0], **bak)
    elif mode == "tilt":
        srx.updateConfig(tiltd=p[0], **bak)
    elif mode == "rotation":
        srx.updateConfig(rotation=p[0], **bak)
    elif mode == "xy":
        srx.updateConfig(xbeamcenter=p[0], ybeamcenter=p[1], **bak)
    elif mode == "all":
        srx.updateConfig(
            xbeamcenter=p[0],
            ybeamcenter=p[1],
            rotationd=p[2],
            tiltd=p[3],
            **bak,
        )

    if showresults:
        halfcut(
            [],
            srx=srx,
            image=image,
            xycenter=xycenter,
            qind=qind,
            show=True,
            mode="show",
            output=output,
        )
    return p


def selfCalibrate(
    srx,
    image,
    mode="xy",
    cropedges="auto",
    showresults=False,
    qrange=[None, None],
    **kwargs,
):
    """Do the self calibration.

    the initial value is read from the current value of srx object, and the
    refined results will be writrn into the srx object

    :param srx: SrXplanar object, object to do the integration
    :param image: str or 2d array, image to be calibrated
    :param mode: str or list of str:
        all: refine all parameters at once
        xy: refine x and y
        list of str: eg. ['x', 'y', 'xy'] -> refine x, then y, then xy
    :param cropedges: list of int or str
        if list of int, it will be passed to srx instance and used as cropedges
        if 'auto', the cropedges of srx instance will be set automatically ,
        if 'x'('y'), then a slice along x(y) axis will be used
        if 'box', then a box around the center will be used
        if 'all', then use all pixels
    :param showresults: bool, plot the halfcut result
    :param qrange: q range used in calculating difference

    :return: list, refined parameter
    """

    # lineCalibrate(srx, image)

    p = []
    if isinstance(mode, str):
        xc = srx.config.xbeamcenter
        yc = srx.config.ybeamcenter
        xd = srx.config.xdimension
        yd = srx.config.ydimension

        if not isinstance(cropedges, (list, tuple)):
            if cropedges == "y" or (cropedges == "auto" and mode == "y"):
                ce = [int(xc - 50), int(xd - xc - 50), yd / 100, yd / 100]
            elif cropedges == "x" or (cropedges == "auto" and mode == "x"):
                ce = [xd / 100, xd / 100, int(yc - 50), int(yd - yc - 50)]
            elif cropedges == "box" or (
                cropedges == "auto" and (mode not in ["x", "y"])
            ):
                ce = [
                    int(xc - xd / 6),
                    int(xd - xc - xd / 6),
                    int(yc - yd / 6),
                    int(yd - yc - yd / 6),
                ]
            else:
                ce = [10, 10, 10, 10]

            cebak = srx.config.cropedges
            srx.updateConfig(cropedges=ce)
            p = selfCalibrateX(
                srx,
                image,
                mode=mode,
                showresults=showresults,
                qrange=qrange,
                **kwargs,
            )
            srx.updateConfig(cropedges=cebak)

    elif isinstance(mode, (list, tuple)):
        for m in mode:
            p = selfCalibrate(srx, image, m, cropedges, qrange=qrange)
    return p
