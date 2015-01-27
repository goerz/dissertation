#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import get_color, set_axis, new_figure, ls, \
                            set_color_cycle

def create_figure(outfile, tgrid, pop_10, pop_1i, pop_1r, pop_01, \
    pop_i1, pop_r1, pop_00, pop_int, pop_r0, pop_0r, pop_rr):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.3               # Left cv -> plot area
    right_margin    = 3.0               # plot area -> right cv
    top_margin      = 0.2               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 1.9               # height of each panel
    gap             = 0.25              # gap between panels
    p2_offset       = p1_offset + h + gap
    p3_offset       = p2_offset + h + gap
    legend_offset = fig_width - right_margin + 0.6  # horizontal offset
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p3_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    set_color_cycle(['blue', 'green', 'red', 'orange', 'purple'])

    # bottom panel: 00
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_00,  label='00')
    ax.plot(tgrid, pop_int, label='int', dashes=ls['dashed'])
    ax.plot(tgrid, pop_r0,  label='r0',  dashes=ls['long-dashed'])
    ax.plot(tgrid, pop_0r,  label='0r',  dashes=ls['dash-dotted'])
    ax.plot(tgrid, pop_rr,  label='rr',  dashes=ls['dash-dash-dotted'])
    set_axis(ax, 'x', 0, 800, 100, minor=4, label='time (ns)')
    set_axis(ax, 'y', 0, 1.05,  0.2, minor=2)
    ax.legend(loc='center left',
              bbox_to_anchor=(legend_offset/fig_width,
                              (p1_offset + 0.5*h - 0.1)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # center panel: 01
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_01,  label='01')
    ax.plot(tgrid, pop_i1 , label='i1',  dashes=ls['dashed'])
    ax.plot(tgrid, pop_r1,  label='r1',  dashes=ls['long-dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', 0, 1.05,  0.2, minor=2, label='population')
    ax.set_xticklabels([])
    ax.legend(loc='center left',
              bbox_to_anchor=(legend_offset/fig_width,
                              (p2_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # top panel: detuning
    pos = [left_margin/fig_width, p3_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_10,  label='10')
    ax.plot(tgrid, pop_1i , label='1i',  dashes=ls['dashed'])
    ax.plot(tgrid, pop_1r,  label='1r',  dashes=ls['long-dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', 0, 1.05,  0.2, minor=2)
    ax.set_xticklabels([])
    ax.legend(loc='center left',
              bbox_to_anchor=(legend_offset/fig_width,
                              (p3_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):

    tgrid, pop_10, pop_1i, pop_1r \
    = np.genfromtxt(os.path.join(data_folder, 'psi10_pops.dat'),
                    usecols=(0,5,7,8), unpack=True)

    tgrid, pop_01, pop_i1, pop_r1 \
    = np.genfromtxt(os.path.join(data_folder, 'psi01_pops.dat'),
                    usecols=(0,2,10,14), unpack=True)

    tgrid, pop_00, pop_0i, pop_i0, pop_ii, pop_ir, \
    pop_ri, pop_r0, pop_0r, pop_rr \
    = np.genfromtxt(os.path.join(data_folder, 'psi00_pops.dat'),
                    usecols=(0,1,3,9,11,12,15,13,4,16), unpack=True)
    pop_int = pop_0i + pop_i0 + pop_ii + pop_ir + pop_ri

    return tgrid, pop_10, pop_1i, pop_1r, pop_01, pop_i1, pop_r1, pop_00, \
    pop_int, pop_r0, pop_0r, pop_rr


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
