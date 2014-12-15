#!/usr/bin/env python

import sys
import os
import numpy as np
from math import sqrt
from mgplottools.mpl import new_figure, write_figure, get_color
from QDYN.bloch import Bloch, bloch_coordinates

def create_figure(outfile):

    # Layout
    fig_width       = 8.0               # Total canvas (cv) width
    left_margin     = 0.0               # Left cv -> plot area
    right_margin    = 0.0               # plot area -> right cv
    top_margin      = 0.0               # top cv -> plot area
    bottom_margin   = 0.0               # bottom cv -> panel 1
    w               = fig_width - left_margin - right_margin
    h               = w
    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)

    pos = [left_margin/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos, projection='3d')

    b = Bloch()
    b.wireframe=False
    pnt = bloch_coordinates(np.array((3,1+1j))/sqrt(11.0))
    b.add_precession(pnt, [1,0,0])
    b.add_precession(pnt, [0,-1,0])
    b.add_precession(pnt, [0,0,1])
    b.add_points(pnt)
    b.add_vectors(pnt)
    b.sphere_alpha=0.3
    b.set_label_convention("xyz01")
    b.precession_color = [get_color('orange'), get_color('blue'),
                          get_color('red')]
    b.vector_color = ['black']
    b.precession_width = [2.0]
    b.xyz_axes = 2
    b.view = [-68, 16]
    b.render(fig, ax)

    # output
    write_figure(fig, outfile)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile)

if __name__ == "__main__":
    sys.exit(main())
