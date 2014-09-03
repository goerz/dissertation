#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from GoerzDiss.plotting import get_color, set_axis, new_figure
from GoerzDiss import layout
from QDYN.pulse import Pulse

def create_figure(outfile, pulse_blue_left, pulse_red_left, pulse_blue_right,
    pulse_red_right):

    # Layout
    fig_width       = layout.figwidth   # Total canvas (cv) width
    left_margin     = 1.3               # Left cv -> plot area
    right_margin    = 0.35              # plot area -> right cv
    top_margin      = 0.2               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 2.0               # height of each panel
    gap             = 0.5               # gap between panels
    p2_offset       = p1_offset + h + gap
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p2_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    lightblue = get_color('lightblue')
    red = get_color('red')

    # bottom panel: right atom
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(pulse_blue_right.tgrid, np.abs(pulse_blue_right.amplitude),
            color=lightblue)
    line, = ax.plot(pulse_red_right.tgrid, np.abs(pulse_red_right.amplitude),
                    color=red)
    #line.set_dashes([8,8])
    set_axis(ax, 'x', 0, 4500, 1000, minor=4,
             label='time (ns)')
    set_axis(ax, 'y', 0, 300,  50, minor=2, label='amplitude (MHz)')
    # move y axis label to cover both panels
    ax.yaxis.set_label_coords((left_margin-0.9)/fig_width,
                              0.5*(fig_height+p1_offset)/fig_height,
                              fig.transFigure)
    ax.text(0.5, 0.75, 'right atom', horizontalalignment='center',
            transform=ax.transAxes)

    # top panel: left atom
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'x', 0, 4500, 1000, minor=4)
    set_axis(ax, 'y', 0, 1050, 200,  minor=2)
    ax.set_xticklabels([])
    ax.plot(pulse_blue_left.tgrid, np.abs(pulse_blue_left.amplitude),
            color=lightblue)
    line, = ax.plot(pulse_red_left.tgrid, np.abs(pulse_red_left.amplitude), color=red)
    #line.set_dashes([8,8])
    ax.text(0.5, 0.7, 'left atom',  horizontalalignment='center',
            transform=ax.transAxes)

    # custom legend (with full lines for both colums)
    legend_blue_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=lightblue)
    legend_red_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=red)
    ax.legend((legend_blue_line, legend_red_line),
              ('$\Omega_B(t)$', '$\Omega_R(t)$'),
              loc='center', bbox_to_anchor=(0.5, 0.3))

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):
    pulse_blue_left  = Pulse(filename=os.path.join(data_folder, 'stirap_pulse1.dat'))
    pulse_red_left   = Pulse(filename=os.path.join(data_folder, 'stirap_pulse2.dat'))
    pulse_blue_right = Pulse(filename=os.path.join(data_folder, 'stirap_pulse3.dat'))
    pulse_red_right  = Pulse(filename=os.path.join(data_folder, 'stirap_pulse4.dat'))
    return pulse_blue_left, pulse_red_left, pulse_blue_right, pulse_red_right


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = 'schemes_pulses'
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
