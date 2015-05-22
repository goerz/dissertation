#!/usr/bin/env python
import os
import sys
import numpy as np
from QDYN.pulse import Pulse
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import set_axis, new_figure, get_color

def create_figure(outfile, freq_left, spec_left, freq_right, spec_right):

    # Layout
    fig_width       = 11.0              # Total canvas (cv) width
    left_margin     = 1.2               # Left cv -> plot area
    right_margin    = 2.8               # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> plot area
    h               = 2.5               # height of each panel
    vgap            = 1.0               # horizontal gap between panels
    w = fig_width - (left_margin + right_margin)  # width of panel

    det_c  =   40.0
    det_w1 =  890.0
    det_w2 = 1290.0

    fig_height = bottom_margin + h + top_margin  + h + 1
    fig = new_figure(fig_width, fig_height)

    scaling = max(np.max(spec_left), np.max(spec_right))
    scaling /= 40.0

    axes = []

    # top panel
    pos = [left_margin/fig_width, (bottom_margin+h+vgap)/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'y', 0, 10, 2, minor=2, label="spect. (arb. units)")
    ax.plot(freq_left, spec_left/scaling, color=get_color('blue'),
            rasterized=True)
    ax.text(0.05,0.8,
            r'$\omega_c = \SI{6.0}{GHz}$\\$\omega_d = \omega_c-\SI{40}{MHz}$',
            transform=ax.transAxes,
            horizontalalignment='left', verticalalignment='top')
    ax.axvline(det_c,  color='black', ls='--', lw=1.0)
    ax.axvline(det_w1, color='black', ls='--', lw=1.0)
    ax.axvline(det_w2, color='black', ls='--', lw=1.0)
    axes.append(ax)
    print "peak of left spectrum is ", np.max(spec_left/scaling)


    # bottom panel
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'y', 0, 10, 2, minor=2, label="spect. (arb. units)")
    ax.plot(freq_right, spec_right/scaling, color=get_color('blue'),
            rasterized=True)
    ax.text(0.95,0.8,
            r'$\omega_c = \SI{8.1}{GHz}$\\$\omega_d = \omega_c+\SI{40}{MHz}$',
            transform=ax.transAxes,
            horizontalalignment='right', verticalalignment='top')
    ax.axvline(-det_c,  color='black', ls='--', lw=1.0)
    ax.axvline(-det_w1, color='black', ls='--', lw=1.0)
    ax.axvline(-det_w2, color='black', ls='--', lw=1.0)
    axes.append(ax)
    print "peak of right spectrum is ", np.max(spec_right/scaling)

    for ax in axes:
        set_axis(ax, 'x', -1500, 1500, 500, minor=5,
                label="frequency relative to $\omega_d$ (MHz)",
                 labelpad=1.0)


    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(folder_left, folder_right):

    pulse_left = Pulse(os.path.join(folder_left, 'pulse.dat'))
    freq_left, spec_left = pulse_left.spectrum(freq_unit='MHz', mode='abs')

    pulse_right = Pulse(os.path.join(folder_right, 'pulse.dat'))
    freq_right, spec_right = pulse_right.spectrum(freq_unit='MHz', mode='abs')

    return freq_left, spec_left, freq_right, spec_right


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, *read_data('HOL00302','HOL02302'))

if __name__ == "__main__":
    sys.exit(main())
