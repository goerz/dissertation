#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from StringIO import StringIO
from mgplottools.mpl import get_color, set_axis, new_figure, ls

def create_figure(outfile, pulse_duration, pop_0i, pop_rr, gate_error):

    # Layout
    fig_width       = 8.5               # Total canvas (cv) width
    left_margin     = 0.9               # Left cv -> plot area
    right_margin    = 0.35              # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> panel 1
    h               = 2.5               # height of each panel
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)

    # Panel
    pos = [left_margin/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(pulse_duration, pop_0i, dashes=ls['dashed'],
            label='max pop in $\Ket{0i}$')
    ax.plot(pulse_duration, pop_rr, dashes=ls['long-dashed'],
            label='max pop in $\Ket{rr}$')
    ax.plot(pulse_duration, gate_error, color='black',
            label='gate error')
    set_axis(ax, 'x', 0, 700, 100, minor=4, range=(10, 700),
             label='central pulse duration (ns)')
    ax.set_yscale('log')
    ax.set_ylim(1.0e-3, 1.0e0)
    ax.legend()

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(datfile):
    data = """
# pulse dur [ns]  max pop 0i        max pop rr      gate error
  10              0.0837            0.8827          0.54675839
  20              0.0506            0.7553          0.42540254
  30              0.0363            0.5689          0.31267201
  40              0.0283            0.3972          0.23354138
  50              0.0232            0.2699          0.17602662
  75              0.016             0.1153          0.08980501
  100             0.0122            0.0694          0.05393173
  150             0.0083            0.0343          0.0249168
  200             0.0063            0.02            0.01393326
  250             0.005             0.0128          0.00952858
  300             0.0042            0.009           0.00662097
  350             0.0036            0.0066          0.00482424
  400             0.0032            0.0051          0.00366514
  450             0.0029            0.004           0.00298152
  500             0.0025515683      0.0032745798    0.00240066
  550             0.0023239946      0.0027134376    0.00195581
  600             0.0021279147      0.0022725114    0.00175541
  650             0.0019674974      0.0019544359    0.00135133
  700             0.0018390561      0.0016939797    0.00085459
"""
    return np.genfromtxt(StringIO(data), unpack=True)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
