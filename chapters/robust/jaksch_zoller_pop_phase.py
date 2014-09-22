#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import get_color, set_axis, new_figure, ls
from QDYN.pulse import Pulse

def create_figure(outfile, tgrid, pop_10, pop_1i, pop_1r, pop_01, pop_i1,
    pop_r1, pop_00, pop_i0, pop_r0, phase_10, phase_1r, phase_01, phase_r1,
    phase_00, phase_r0 ):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.10              # Left cv -> plot area
    right_margin    = 0.30              # plot area -> right cv
    top_margin      = 0.5               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 1.8               # height of each panel
    vgap            = 0.5               # vertical gap between panels
    hgap            = 1.2               # horizontal
    p2_offset       = p1_offset + h + vgap
    p3_offset       = p2_offset + h + vgap
    w = (fig_width - (left_margin+right_margin+hgap) ) / 2.0  # width of panel
    fig_height = p3_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    orange = get_color('orange')
    blue   = get_color('blue')
    red    = get_color('red')

    # bottom left
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_00, label='$00$', color=blue)
    ax.plot(tgrid, pop_i0, label='$i0$', color=red,
            dashes=ls['long-dashed'])
    ax.plot(tgrid, pop_r0, label='$r0$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4, label='time (ns)')
    set_axis(ax, 'y', 0, 1,  0.2, minor=2)
    ax.legend(loc='center right')

    # center left
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_01, label='$01$', color=blue)
    ax.plot(tgrid, pop_i1, label='$i1$', color=red,
            dashes=ls['long-dashed'])
    ax.plot(tgrid, pop_r1, label='$r1$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', 0, 1,  0.2, minor=2)
    ax.set_xticklabels([])
    ax.legend(loc='center right')

    # top left
    pos = [left_margin/fig_width, p3_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, pop_10, label='$10$', color=blue)
    ax.plot(tgrid, pop_1i, label='$1i$', color=red,
            dashes=ls['long-dashed'])
    ax.plot(tgrid, pop_1r, label='$1r$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', 0, 1,  0.2, minor=2)
    ax.set_xticklabels([])
    ax.legend(loc='center right')
    ax.set_title("Population")

    # bottom right
    pos = [(left_margin+w+hgap)/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, phase_00, label=r'$00$', color=blue)
    ax.plot(tgrid, phase_r0, label=r'$r0$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4, label='time (ns)')
    set_axis(ax, 'y', -1, 1,  0.5, minor=2)
    ax.legend(ncol=2, loc='upper center')

    # center right
    pos = [(left_margin+w+hgap)/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, phase_01, label=r'$01$', color=blue)
    ax.plot(tgrid, phase_r1, label=r'$r1$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', -1, 1,  0.5, minor=2)
    ax.set_xticklabels([])
    ax.legend(ncol=2, loc='upper center')

    # top right
    pos = [(left_margin+w+hgap)/fig_width, p3_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(tgrid, phase_00, label=r'$10$', color=blue)
    ax.plot(tgrid, phase_r0, label=r'$1r$', color=orange,
            dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', -1, 1,  0.5, minor=2)
    ax.set_xticklabels([])
    ax.legend(ncol=2, loc='upper center')
    ax.set_title("phase ($\pi$)")

    # panel labels
    fig.text(0, (p3_offset+h)/fig_height,
             "a)")
    fig.text(0, (p2_offset+h)/fig_height,
             "b)")
    fig.text(0, (p1_offset+h)/fig_height,
             "c)")
    fig.text((left_margin+w+0.2)/fig_width, (p3_offset+h)/fig_height,
             "d)")
    fig.text((left_margin+w+0.2)/fig_width, (p2_offset+h)/fig_height,
             "e)")
    fig.text((left_margin+w+0.2)/fig_width, (p1_offset+h)/fig_height,
             "f)")

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):
    tgrid, pop_10, pop_1i, pop_1r, pop_01, pop_i1, pop_r1, pop_00, pop_i0, \
    pop_r0 = np.genfromtxt(os.path.join(data_folder, 'pop.dat'), unpack=True)
    tgrid, phase_10, phase_1r, phase_01, phase_r1, phase_00, phase_r0 \
    = np.genfromtxt(os.path.join(data_folder, 'phase.dat'), unpack=True)
    return tgrid, pop_10, pop_1i, pop_1r, pop_01, pop_i1, pop_r1, pop_00,     \
           pop_i0, pop_r0, phase_10, phase_1r, phase_01, phase_r1, phase_00,  \
           phase_r0


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
