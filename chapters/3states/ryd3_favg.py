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
                            set_color_cycle, new_ls_cycle


def create_figure(outfile, data_nodiss, data_bad, data_diss):
    """
    Each "data" variable contains an arrays of 4 tupels:
        [(iter, F_avg_full), (iter, F_avg_3st),
         (iter, F_avg_2st), (iter, F_avg_2st_w)]
    """

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.5               # Left cv -> plot area
    right_margin    = 4.0               # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> panel 1
    h               = 2.3               # height of panel
    gap             = 0.65              # vertical gap between panels
    n_panels = 3
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = bottom_margin + n_panels*h + (n_panels-1)*gap + top_margin
    fig = new_figure(fig_width, fig_height)

    set_color_cycle(['black', 'red', 'green', 'orange'])

    panels = []
    line_labels = ['full basis', '3 states', '2 states', '2 states (weight)']
    panel_label = [r'no dissipation,\par $T=\SI{50}{ns}$',
                   r'no dissipation,\par bad guess',
                   r'$\tau = \SI{25}{ns}$, \par $T = \SI{75}{ns}$']
    for i_panel, data in enumerate([data_nodiss, data_bad, data_diss]):

        bottom_offset = bottom_margin + (n_panels-i_panel-1)*(h+gap)
        pos = [left_margin/fig_width,
               bottom_offset/fig_height,
               w/fig_width, h/fig_height]
        print "Adding new panel at %s" % str(pos)
        ax = fig.add_axes(pos)
        ls_cycle = new_ls_cycle(['solid', 'dashed', 'dotted', 'solid'])
        for i_line, (iter, favg) in enumerate(data):
            ax.plot(iter, favg, dashes=next(ls_cycle),
                    label=line_labels[i_line])
        ax.legend(loc='center right',
                title=panel_label[i_panel],
                bbox_to_anchor=(1.0,
                                (bottom_offset+0.5*h)/fig_height),
                bbox_transform=fig.transFigure,
                labelspacing=0.3, borderpad=0.0, borderaxespad=0.0)
        panels.append(ax)

    set_axis(panels[0], 'x', 0, 80, 10, minor=2, label='')
    set_axis(panels[0], 'y', 1.0e-5, 1.0e-0, logscale=True,
             label=r'$1-F_{\text{avg}}$')
    set_axis(panels[1], 'x', 0, 1500, 500, minor=5, label='')
    set_axis(panels[1], 'y', 1.0e-3, 1.5, logscale=True,
             label=r'$1-F_{\text{avg}}$')
    set_axis(panels[2], 'x', 0, 1000, 200, minor=2, label='OCT iteration')
    set_axis(panels[2], 'y', 4.0e-3, 0.2, logscale=True,
             label=r'$1-F_{\text{avg}}$')

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(datfolder):
    data = []
    sets = [
        ('no_diss/fbR0004_f_avg.dat',
         'no_diss/s2R0004_f_avg.dat',
         'no_diss/s5R0004_f_avg.dat',
         'no_diss/s5R0402_f_avg.dat'),
        ('no_diss_bad_guess/fbR0002_f_avg.dat',
         'no_diss_bad_guess/s2R0200_f_avg.dat',
         'no_diss_bad_guess/s5R0200_f_avg.dat',
         'no_diss_bad_guess/s5R0202_f_avg.dat'),
        ('diss/fbR0003_f_avg.dat',
         'diss/s2R0003_f_avg.dat',
         'diss/s5R0003_f_avg.dat',
         'diss/s5R0302_f_avg.dat')
    ]
    for set in sets:
        data.append([])
        for file in set:
            filename = os.path.join(datfolder, file)
            iter, favg = np.genfromtxt(filename, usecols=(0,1), unpack=True)
            data[-1].append( (iter, favg) )
    return tuple(data)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, *read_data('rydberg'))


if __name__ == "__main__":
    sys.exit(main())

