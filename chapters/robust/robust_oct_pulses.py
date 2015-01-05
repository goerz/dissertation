#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import get_color, set_axis, new_figure
from QDYN.pulse import Pulse

def create_figure(outfile, pulse_blue_left, pulse_red_left, pulse_blue_right,
    pulse_red_right, guess_left, guess_right):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.3               # Left cv -> plot area
    right_margin    = 3.0               # plot area -> right cv
    top_margin      = 0.2               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 2.0               # height of each panel
    gap             = 0.25              # gap between panels
    spec_pulse_gap  = 1.1               # gap between pulses and spectra
    p2_offset       = p1_offset + h + gap
    p3_offset       = p2_offset + h + spec_pulse_gap
    p4_offset       = p3_offset + h + gap
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p4_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)
    legend_offset = fig_width - right_margin + 0.25 # horizontal offset

    lightblue = get_color('lightblue')
    red = get_color('red')
    orange = get_color('orange')

    # bottom panel: right atom spectrum
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    freq, spec_red_right = pulse_red_right.spectrum(freq_unit='MHz',
                                                    mode='abs')
    spec_red_right *= 1.0 / len(spec_red_right)
    freq, spec_blue_right = pulse_blue_right.spectrum(freq_unit='MHz',
                                                      mode='abs')
    spec_blue_right *= 1.0 / len(spec_red_right)
    # rescale
    scale = 1.393 / np.max(spec_red_right)
    print "scale = ", scale
    spec_red_right *= scale
    spec_blue_right *= scale
    print "max(red)  [right] = ", np.max(spec_red_right)
    print "max(blue) [right] = ", np.max(spec_blue_right)

    ax.axvline(x=-1273.0, ls='--', color='gray')
    ax.axvline(x=1273.0, ls='--', color='gray')
    ax.plot(freq, spec_red_right, color=red, rasterized=True)
    ax.plot(freq, spec_blue_right, color=lightblue, rasterized=True)
    set_axis(ax, 'x', -1500, 1500, 500, minor=5, label='frequency (MHz)')
    set_axis(ax, 'y', 0, 1.05, 0.2,  minor=2, label='spectrum (arb. units)')
    # move y axis label to cover both panels
    ax.yaxis.set_label_coords((left_margin-0.9)/fig_width,
                              (p1_offset + h+0.5*gap) / fig_height,
                              fig.transFigure)
    ax.text(0.25/w, (h-0.2)/h, "d)", transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left')

    # custom legend (with full lines for both colums)
    legend_blue_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=lightblue)
    legend_red_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=red)
    marker_line = matplotlib.pyplot.Line2D((0,1),(0,0), ls='--', color='gray')
    ax.legend((legend_blue_line, legend_red_line, marker_line),
              (r'spec($\Omega_B(t)$)', r'spec($\Omega_R(t)$)', '$\Delta_1$'),
              loc='center left', title="right atom",
              bbox_to_anchor=(legend_offset/fig_width,
                              (p1_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # 2nd panel: left atom spectrum
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    freq, spec_red_left = pulse_red_left.spectrum(freq_unit='MHz',
                                                    mode='abs')
    spec_red_left *= 1.0 / len(spec_red_left)
    freq, spec_blue_left = pulse_blue_left.spectrum(freq_unit='MHz',
                                                      mode='abs')
    spec_blue_left *= 1.0 / len(spec_blue_left)
    # rescale (scaling factor from above)
    spec_red_left *= scale
    spec_blue_left *= scale
    print "max(red)  [left] = ", np.max(spec_red_left)
    print "max(blue) [left] = ", np.max(spec_blue_left)

    ax.axvline(x=-1273.0, ls='--', color='gray')
    ax.axvline(x=1273.0, ls='--', color='gray')
    ax.plot(freq, spec_red_left, color=red, rasterized=True)
    ax.plot(freq, spec_blue_left, color=lightblue, rasterized=True)
    set_axis(ax, 'x', -1500, 1500, 500, minor=5)
    set_axis(ax, 'y', 0, 1.05, 0.2,  minor=2)
    ax.set_xticklabels([])
    ax.text(0.25/w, (h-0.2)/h, "c)", transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left')

    # custom legend (with full lines for both colums)
    legend_blue_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=lightblue)
    legend_red_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=red)
    marker_line = matplotlib.pyplot.Line2D((0,1),(0,0), ls='--', color='gray')
    ax.legend((legend_blue_line, legend_red_line, marker_line),
              (r'spec($\Omega_B(t)$)', r'spec($\Omega_R(t)$)', '$\Delta_1$'),
              loc='center left', title="left atom",
              bbox_to_anchor=(legend_offset/fig_width,
                              (p2_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # 3rd panel: right atom
    pos = [left_margin/fig_width, p3_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(pulse_red_right.tgrid, np.abs(pulse_red_right.amplitude),
            color=red, rasterized=True)
    ax.plot(pulse_blue_right.tgrid, np.abs(pulse_blue_right.amplitude),
            color=lightblue, rasterized=True)
    ax.plot(pulse_red_right.tgrid, guess_right, color=orange)
    set_axis(ax, 'x', 0, 800, 100, minor=4, labelpad=1, label='time (ns)')
    set_axis(ax, 'y', 0,  90, 20,  minor=2, label='amplitude (MHz)')
    # move y axis label to cover both panels
    ax.yaxis.set_label_coords((left_margin-0.9)/fig_width,
                              (p3_offset + h+0.5*gap) / fig_height,
                              fig.transFigure)
    ax.text(0.25/w, (h-0.2)/h, "b)", transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left')

    # custom legend (with full lines for both colums)
    legend_blue_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=lightblue)
    legend_red_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=red)
    guess_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=orange)
    ax.legend((legend_blue_line, legend_red_line, guess_line),
              (r'$\vert\Omega_B(t)\vert$', r'$\vert\Omega_R(t)\vert$', 'guess'),
              loc='center left', title="right atom",
              bbox_to_anchor=(legend_offset/fig_width,
                              (p3_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # top panel: left atom
    pos = [left_margin/fig_width, p4_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'x', 0, 800, 100, minor=4)
    set_axis(ax, 'y', 0, 130, 50,  minor=5)
    ax.set_xticklabels([])
    ax.plot(pulse_red_left.tgrid, np.abs(pulse_red_left.amplitude),
            color=red, rasterized=True)
    ax.plot(pulse_blue_left.tgrid, np.abs(pulse_blue_left.amplitude),
            color=lightblue, rasterized=True)
    ax.plot(pulse_red_left.tgrid, guess_left, color=orange)
    ax.text(0.25/w, (h-0.2)/h, "a)", transform=ax.transAxes,
            verticalalignment='top', horizontalalignment='left')

    # custom legend (with full lines for both colums)
    legend_blue_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=lightblue)
    legend_red_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=red)
    guess_line = matplotlib.pyplot.Line2D((0,1),(0,0), color=orange)
    ax.legend((legend_blue_line, legend_red_line, guess_line),
              (r'$\vert\Omega_B(t)\vert$', r'$\vert\Omega_R(t)\vert$', 'guess'),
              loc='center left', title="left atom",
              bbox_to_anchor=(legend_offset/fig_width,
                              (p4_offset + 0.5*h)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):
    pulse_blue_left  = Pulse(filename=os.path.join(data_folder, 'pulse1.dat'))
    pulse_red_left   = Pulse(filename=os.path.join(data_folder, 'pulse2.dat'))
    pulse_blue_right = Pulse(filename=os.path.join(data_folder, 'pulse3.dat'))
    pulse_red_right  = Pulse(filename=os.path.join(data_folder, 'pulse4.dat'))
    for pulse in [pulse_blue_left, pulse_red_left, pulse_blue_right,
    pulse_red_right]:
        pulse.amplitude *= 100.0
        pulse.ampl_unit = 'MHz'
    guess_left = np.genfromtxt(os.path.join(data_folder, 'pulse1.guess'))
    guess_right = np.genfromtxt(os.path.join(data_folder, 'pulse3.guess'))
    return pulse_blue_left, pulse_red_left, pulse_blue_right, \
           pulse_red_right, guess_left, guess_right


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
