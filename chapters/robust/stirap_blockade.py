#!/usr/bin/env python
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import get_color, set_axis, new_figure, ls

def create_figure(outfile, ampl, final_1r_1200, final_rr_1200, max_1r_1200,
    max_rr_1200, blockeff_1200, final_1r_4200, final_rr_4200, max_1r_4200,
    max_rr_4200, blockeff_4200):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.5               # Left cv -> plot area
    right_margin    = 3.0               # plot area -> right cv
    top_margin      = 0.2               # top cv -> plot area
    p1_offset       = 1.0               # bottom cv -> panel 1
    h               = 2.0               # height of each panel
    gap             = 0.5               # gap between panels
    p2_offset       = p1_offset + h + gap
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = p2_offset + h + top_margin
    fig = new_figure(fig_width, fig_height)

    blue = get_color('blue')
    orange = get_color('orange')
    red = get_color('red')
    green = get_color('green')

    # bottom panel: right atom
    pos = [left_margin/fig_width, p1_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(ampl, final_1r_4200, color=blue, dashes=ls['dashed'],
            label="max $P_{1r}$")
    ax.plot(ampl, final_rr_4200, color=orange, dashes=ls['dash-dotted'],
            label="max $P_{rr}$")
    ax.plot(ampl, max_1r_4200, color=red, dashes=ls['long-dashed'],
            label="final $P_{1r}$")
    ax.plot(ampl, max_rr_4200, color=green, dashes=ls['dash-dash-dotted'],
            label="final $P_{rr}$")
    ax.plot(ampl, blockeff_4200, color='black',
            label="blockade eff.")
    set_axis(ax, 'x', 0, 500, 100, minor=4, label='peak amplitude (MHz)')
    set_axis(ax, 'y', 0, 1,  0.2, minor=2, label='population', range=(0,1.05))
    # move y axis label to cover both panels
    ax.yaxis.set_label_coords((left_margin-0.8)/fig_width,
                              0.5*(fig_height+p1_offset)/fig_height,
                              fig.transFigure)
    ax.legend(loc='center right',
              bbox_to_anchor=(1.0, 0.5*(fig_height+p1_offset)/fig_height),
              bbox_transform=fig.transFigure, borderpad=0.0, borderaxespad=0.0)
    ax.text(0.75, 0.6, '$T =$ 4200~ns', transform=ax.transAxes, verticalalignment='center')

    # top panel: left atom
    pos = [left_margin/fig_width, p2_offset/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(ampl, final_1r_1200, color=blue, dashes=ls['dashed'],
            label="max $P_{1r}$")
    ax.plot(ampl, final_rr_1200, color=orange, dashes=ls['dash-dotted'],
            label="max $P_{rr}$")
    ax.plot(ampl, max_1r_1200, color=red, dashes=ls['long-dashed'],
            label="final $P_{1r}$")
    ax.plot(ampl, max_rr_1200, color=green, dashes=ls['dash-dash-dotted'],
            label="final $P_{rr}$")
    ax.plot(ampl, blockeff_1200, color='black',
            label="blockade eff.")
    set_axis(ax, 'x', 0, 500, 100, minor=4)
    set_axis(ax, 'y', 0, 1, 0.2,  minor=2, range=(0,1.05))
    ax.set_xticklabels([])
    ax.text(0.03, 0.6, '$T =$ 1200~ns', transform=ax.transAxes, verticalalignment='center')

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):

    ampl, final_1r_1200, final_rr_1200, \
    max_1r_1200, max_rr_1200, blockeff_1200  \
    = np.genfromtxt(os.path.join(data_folder, '1200.dat'), unpack=True)

    ampl, final_1r_4200, final_rr_4200, \
    max_1r_4200, max_rr_4200, blockeff_4200 \
    = np.genfromtxt(os.path.join(data_folder, '4200.dat'), unpack=True)

    return ampl, final_1r_1200, final_rr_1200, max_1r_1200, max_rr_1200,    \
           blockeff_1200, final_1r_4200, final_rr_4200, max_1r_4200,  \
           max_rr_4200, blockeff_4200


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
