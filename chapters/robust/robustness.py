#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import get_color, set_axis, new_figure, ls, \
                            set_color_cycle

def create_figure(outfile, sig_time, rob_jz_time, rob_stirap_time,
    rob_mixed_time, sig_ampl, rob_jz_ampl, rob_stirap_ampl, rob_mixed_ampl,
    sig_det, rob_jz_det, rob_stirap_det, rob_mixed_det):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 2.25              # Left cv -> plot area
    right_margin    = 2.25              # plot area -> right cv
    top_margin      = 0.2               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 2.0               # height of each panel
    gap             = 1.0               # gap between panels
    p2_offset       = p1_offset + h + gap
    p3_offset       = p2_offset + h + gap
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p3_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    set_color_cycle()

    # bottom panel: time
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(sig_time, rob_jz_time)
    ax.plot(sig_time, rob_stirap_time, dashes=ls['dash-dotted'])
    ax.plot(sig_time, rob_mixed_time, dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 1.6, 0.5, minor=5, label=r'$\sigma_{\text{time}}$ (ns)')
    set_axis(ax, 'y', 0.995, 1.0,  0.001, minor=2)

    # center panel: amplitude
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(sig_ampl, rob_jz_ampl,
            label="simult. pulses")
    ax.plot(sig_ampl, rob_stirap_ampl, dashes=ls['dash-dotted'],
            label="STIRAP")
    ax.plot(sig_ampl, rob_mixed_ampl, dashes=ls['dashed'],
            label="mixed STIRAP/simult.")
    set_axis(ax, 'x', 0, 3, 1, minor=5, labelpad=-1, label=r'$\sigma_{\Omega}$ (\%)')
    set_axis(ax, 'y', 0.8, 1.0, 0.04, minor=2, label='average gate fidelity')
    ax.legend(loc='lower right', borderaxespad=0)

    # top panel: detuning
    pos = [left_margin/fig_width, p3_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(sig_det, rob_jz_det)
    ax.plot(sig_det, rob_stirap_det, dashes=ls['dash-dotted'])
    ax.plot(sig_det, rob_mixed_det, dashes=ls['dashed'])
    set_axis(ax, 'x', 0, 150, 50, minor=5, labelpad=-1, label=r'$\sigma_{\text{Ryd}}$ (kHz)')
    set_axis(ax, 'y', 0.9, 1.0, 0.02, minor=2)

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):

    sig_time, rob_jz_time, rob_stirap_time, rob_mixed_time \
    = np.genfromtxt(os.path.join(data_folder, 'robust_time.dat'), unpack=True)

    sig_ampl, rob_jz_ampl, rob_stirap_ampl, rob_mixed_ampl \
    = np.genfromtxt(os.path.join(data_folder, 'robust_ampl.dat'), unpack=True)

    sig_det, rob_jz_det, rob_stirap_det, rob_mixed_det \
    = np.genfromtxt(os.path.join(data_folder, 'robust_det.dat'), unpack=True)

    return sig_time, rob_jz_time, rob_stirap_time, rob_mixed_time, sig_ampl, \
    rob_jz_ampl, rob_stirap_ampl, rob_mixed_ampl, sig_det, rob_jz_det, \
    rob_stirap_det, rob_mixed_det


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
