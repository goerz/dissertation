#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script for generating a plot of gate error (data included in file)
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from StringIO import StringIO
from mgplottools.mpl import get_color, set_axis, new_figure, ls, \
                            set_color_cycle


def create_figure(outfile, T_left, pop_loss_left, conc_err_left, T_right,
pop_loss_right, conc_err_right):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.5               # Left cv -> plot area
    right_margin    = 3.5               # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> panel 1
    h               = 3.5               # height of panel
    legend_offset   = 9.4               # Left cv -> legend
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)

    set_color_cycle(['blue', 'blue', 'red', 'red'])

    # panel 1: gate error
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)

    l1, = ax.plot(T_left, pop_loss_left,  marker='*',
            label=r'pop. loss ')
    l2, = ax.plot(T_left, conc_err_left,  marker='o', dashes=ls['dashed'],
            label=r'1-C')
    l3, = ax.plot(T_right, pop_loss_right,  marker='*',
            label=r'pop. loss')
    l4, = ax.plot(T_right, conc_err_right,  marker='o', dashes=ls['dashed'],
            label=r'1-C')

    set_axis(ax, 'x', 40, 155, 20, minor=2, label='pulse duration (ns)')
    set_axis(ax, 'y', 5.0e-6, 1.0e-0, logscale=True,
             label='pop. loss,~~$1-C$')
    top_legend = ax.legend(handles=[l1, l2], loc='upper left',
            title=r'$\omega_c = \SI{6.0}{GHz}$\\$\omega_d = \omega_c-\SI{40}{MHz}$',
            bbox_to_anchor=(legend_offset/fig_width,
                            (bottom_margin+h)/fig_height),
            bbox_transform=fig.transFigure, handlelength=3,
            labelspacing=0.3, borderpad=0.0, borderaxespad=0.0)
    ax.add_artist(top_legend)
    ax.legend(handles=[l3, l4], loc='lower left',
            title=r'$\omega_c = \SI{8.1}{GHz}$\\$\omega_d = \omega_c+\SI{40}{MHz}$',
            bbox_to_anchor=(legend_offset/fig_width,
                            bottom_margin/fig_height),
            bbox_transform=fig.transFigure, handlelength=3,
            labelspacing=0.3, borderpad=0.0, borderaxespad=0.0)

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data():
    data = {}
    data['left'] = """
# T [ns] E_max [MHz]                 pop_loss                      1-C        peak_q        peak_c
     150       153.7   4.9964559022535049E-03   0.0000000000000000E+00        1.5487       10.2221
     140       174.8   2.9461138007140790E-03   0.0000000000000000E+00        1.5593        9.7343
     120       228.4   3.7819210627627609E-03   0.0000000000000000E+00        1.9596       12.8614
     100       303.9   5.5068176063336471E-03   0.0000000000000000E+00        2.2383       14.5059
      90       228.7   1.9567666926425201E-02   8.4526830000000003E-04        2.5977       16.9970
      80       272.6   3.0062105878914450E-02   1.6712669999999999E-03        2.8527       18.8445
      70       300.6   1.5540357511881961E-01   9.3000280000000001E-03        3.2739       43.6869
      60       273.0   6.7845779759214164E-01   4.8570540000000001E-01        2.5084       35.9711
"""
    data['right'] = """
# T [ns] E_max [MHz]                 pop_loss                      1-C        peak_q        peak_c
     150       216.6   1.3408725566342211E-02   0.0000000000000000E+00        1.0560       34.2170
     140       174.0   9.5170526611403350E-03   0.0000000000000000E+00        1.0529       27.9088
     120       249.3   2.4165843224063451E-02   9.0503280000000003E-06        1.0691       52.0290
     100       293.4   2.7663619229554959E-02   5.0797050000000001E-04        1.0747       41.0890
      80       379.9   1.9874284625955418E-02   4.4540550000000002E-04        1.1135       75.2483
      60       434.5   2.4622908148377750E-02   8.7881549999999998E-04        1.1094       78.1755
      50       708.6   3.4145871567271341E-01   4.0401589999999998E-01        1.2273      128.4184
      40       667.4   4.8624556720352291E-01   8.1782889999999997E-01        1.2286      130.5642
"""
    T_left, pop_loss_left, conc_err_left \
    = np.genfromtxt(StringIO(data['left']), usecols=(0, 2, 3),unpack=True)
    T_right, pop_loss_right, conc_err_right \
    = np.genfromtxt(StringIO(data['right']), usecols=(0, 2, 3),unpack=True)
    return T_left, pop_loss_left, conc_err_left, T_right, pop_loss_right, conc_err_right



def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, *read_data())


if __name__ == "__main__":
    sys.exit(main())

