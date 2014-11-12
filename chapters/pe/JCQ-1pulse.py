#!/usr/bin/env python
import os
import sys
import numpy as np
from StringIO import StringIO
from mgplottools.mpl import set_axis, new_figure, ls, \
                            write_figure, get_color

def create_figure(outfile, EC, Aerr, Perr, Qerr, PEerr):

    # Layout
    fig_width       = 8.5               # Total canvas (cv) width
    left_margin     = 1.35              # Left cv -> plot area
    right_margin    = 0.15              # plot area -> right cv
    top_margin      = 0.05              # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> panel 1
    h               = 3.5               # height of each panel
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)


    # Panel
    pos = [left_margin/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(EC, Aerr, dashes=ls['dashed'], color=get_color('green'),
            label='$A_2$', marker='s')
    ax.plot(EC, Perr, dashes=ls['dash-dotted'], color=get_color('blue'),
            label='$P$', marker='v')
    ax.plot(EC, Qerr, dashes=ls['dotted'], color=get_color('orange'),
            label='$Q$', marker='^')
    ax.plot(EC, PEerr, dashes=ls['solid'], color=get_color('black'),
            label='PE', marker='o')
    set_axis(ax, 'x', 0, 100, 10, minor=2, range=(0, 102),
             label='charging energy $E_C$ (GHz)')
    ax.set_yscale('log')
    ax.set_ylim(1.0e-5, 3.0e-1)
    ax.set_ylabel(r'opt. error $\epsilon_{\text{lec}}$, $\epsilon_{\text{PE}}$')
    ax.legend(ncol=2, loc='center right', bbox_to_anchor=(1.0, 0.65))

    # output
    write_figure(fig, outfile)


def read_data():
    data = """
#  E_C [GHz]            1-F_lec[AGATE]            1-F_lec[PGATE]            1-F_lec[QGATE]                    1-F_pe
       5.000    1.3697590846438690E-01    1.7817915046180444E-01    1.0471388824096783E-01    1.9164264381444696E-02
      10.000    3.0136061788389235E-02    1.4127637566976059E-01    6.4176281093328291E-02    1.1513574896959700E-03
      15.000    1.1607772161618457E-02    7.0460335411720587E-03    9.1125272921921407E-04    4.9974076380043808E-04
      20.000    5.2024362382019351E-03    1.8529931483246220E-02    4.5574474756371330E-04    2.2301209642217046E-04
      30.000    2.9893902690392160E-03    6.6806632070107730E-02    3.6874522558760781E-04    1.8043635162867666E-04
      40.000    1.6193052557158527E-03    7.4087734659324278E-02    3.0425970585079565E-04    9.4028404419965739E-05
     100.000    2.4832388620066315E-04    6.2562613339925854E-02    2.5856055799122757E-04    1.3953955978363020E-05
"""
    return np.genfromtxt(StringIO(data), unpack=True)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, *read_data())

if __name__ == "__main__":
    sys.exit(main())
