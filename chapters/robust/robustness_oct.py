#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from GoerzDiss.plotting import get_color, set_axis, new_figure, ls
from GoerzDiss import layout

def create_figure(outfile, sig_mixed_ampl, rob_mixed_ampl, rob_800oct_ampl,
    rob_800oct2_ampl, rob_100oct_ampl, sig_mixed_det, rob_mixed_det,
    rob_800oct_det, rob_800oct2_det, rob_100oct_det):

    # Layout
    fig_width       = layout.figwidth   # Total canvas (cv) width
    left_margin     = 1.4               # Left cv -> plot area
    right_margin    = 0.3               # plot area -> right cv
    top_margin      = 0.01              # top cv -> plot area
    p1_offset       = 0.8               # bottom cv -> panel 1
    h               = 2.1               # height of each panel
    gap             = 1.0               # gap between panels
    p2_offset       = p1_offset + h + gap
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p2_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    # bottom panel: amplitude
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(sig_mixed_ampl, rob_mixed_ampl)
            #label="mixed stirap/simult.")
    ax.plot(sig_mixed_ampl, rob_800oct_ampl,  dashes=ls['dash-dotted'])
            #label="OCT (800ns)")
    ax.plot(sig_mixed_ampl, rob_800oct2_ampl, dashes=ls['dotted'],
            label="OCT (800ns), optimized further")
    ax.plot(sig_mixed_ampl, rob_100oct_ampl,  dashes=ls['dashed'],
            label="OCT (100ns)")
    set_axis(ax, 'x', 0, 3, 1, minor=5, labelpad=-1,
             label=r'$\sigma_{\Omega}$ (ns)')
    ax.set_yscale('log')
    ax.set_ylim(1.0e-6, 5.0e0)
    ax.set_ylabel('average gate fidelity')
    # move y axis label to cover both panels
    ax.yaxis.set_label_coords((left_margin-1.0)/fig_width,
                              0.5*(fig_height+p1_offset)/fig_height,
                              fig.transFigure)
    ax.legend(loc='upper left', borderaxespad=0.0,
              fontsize='small', labelspacing=0.1)

    # top panel: detuning
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(sig_mixed_det, rob_mixed_det,
            label="mixed stirap/simult.")
    ax.plot(sig_mixed_det, rob_800oct_det,  dashes=ls['dash-dotted'],
            label="OCT (800ns)")
    ax.plot(sig_mixed_det, rob_800oct2_det, dashes=ls['dotted'])
            #label="OCT (800ns), optimized further")
    ax.plot(sig_mixed_det, rob_100oct_det,  dashes=ls['dashed'])
            #label="OCT (100ns)")
    set_axis(ax, 'x', 0, 150, 50, minor=5, labelpad=-1,
             label=r'$\sigma_{\text{Ryd}}$ (kHz)')
    ax.set_yscale('log')
    ax.set_ylim(1.0e-6, 5.0e0)
    ax.legend(loc='upper left', borderaxespad=0.0,
              fontsize='small', labelspacing=0.1)

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):

    sig_mixed_ampl, rob_mixed_ampl, rob_800oct_ampl, \
    rob_800oct2_ampl, rob_100oct_ampl \
    = np.genfromtxt(os.path.join(data_folder, 'robust_oct_ampl.dat'),
                    unpack=True)

    sig_mixed_det, rob_mixed_det, rob_800oct_det, \
    rob_800oct2_det, rob_100oct_det \
    = np.genfromtxt(os.path.join(data_folder, 'robust_oct_det.dat'),
                    unpack=True)

    return sig_mixed_ampl, rob_mixed_ampl, rob_800oct_ampl, rob_800oct2_ampl, \
           rob_100oct_ampl, sig_mixed_det, rob_mixed_det, rob_800oct_det,     \
           rob_800oct2_det, rob_100oct_det


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
