#!/usr/bin/env python
import os
import sys
import re
import numpy as np
from glob import glob
from QDYN.pulse import Pulse
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import set_axis, new_figure, get_color

def create_figure(outfile, freq400, spec400, freq1000, spec1000):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.05              # Left cv -> plot area
    right_margin    = 0.25              # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> plot area
    h               = 2.5               # height of each panel
    gap             = 0.2               # gap between panels
    w = (fig_width - (left_margin + right_margin + gap)) /2.0  # width of panel

    w_c = 8.3
    w_1 = 6.5
    w_2 = 6.6

    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)

    scaling = max(np.max(spec400), np.max(spec1000)) / 10.0

    axes = []

    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'y', 0, 10, 2, minor=2, label="spect. (arb. units)")
    ax.plot(freq400, spec400/scaling, color=get_color('blue'))
    ax.text(0.95,0.9, r'$T=\SI{400}{ns}$', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')
    axes.append(ax)

    pos = [(left_margin+w+gap)/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'y', 0, 10, 2, minor=2, ticklabels=False)
    ax.plot(freq1000, spec1000/scaling, color=get_color('blue'))
    ax.text(0.95,0.9, r'$T=\SI{1000}{ns}$', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')
    axes.append(ax)

    for ax in axes:
        ax.axvline(w_c, color='black', lw=0.5, zorder=-10)
        ax.axvline(w_1, color='black', lw=0.5, zorder=-10)
        ax.axvline(w_2, color='black', lw=0.5, zorder=-10)
        set_axis(ax, 'x', 6, 10.9, 0.5, minor=5, label="frequency (MHz)",
                 labelpad=0.0)
        for label in ax.xaxis.get_ticklabels()[::2]:
            label.set_visible(False)


    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):
    """
    Return E (array), entanglement (dict), nc (dict), nq (dict)
    """
    pulse1000 = Pulse(os.path.join(data_folder, 'pulse.CPH0009.dat'))
    pulse400 = Pulse(os.path.join(data_folder, 'pulse.CPH0012.dat'))
    freq1000, spec1000 = pulse1000.spectrum(freq_unit='GHz', mode='abs')
    freq400, spec400 = pulse400.spectrum(freq_unit='GHz', mode='abs')
    return freq400, spec400, freq1000, spec1000


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = 'tm2013_spectra'
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
