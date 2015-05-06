#!/usr/bin/env python
import os
import sys

# Run with most recent version of Enthought Canopy Python Distribution
# https://www.enthought.com/products/canopy/

import numpy as np

import matplotlib
#matplotlib.use("PDF") # backend selection (must be done before other imports)
matplotlib.use("Agg") # backend selection (must be done before other imports)
from matplotlib.pyplot import figure
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d


def plot_weyl_chamber(outfile):

    import matplotlib.pyplot as plt

    ### Layout ###

    font = {'family'    : "serif",
            'sans-serif':['Computer Modern Sans serif', 'Helvetica'],
            'serif'     :['Computer Modern Roman', 'Palatino'],
            'monospace' :['Computer Modern Typewriter', 'Courier'],
            'size'      : 8.00}
    matplotlib.rc('text', usetex=True)
    matplotlib.rc('font', **font)
    fig_width       =  8.5 # Total width of figure canvas [cm]
    fig_height      =  6.0 # Total height of figure canvas [cm]
    left_margin     =  0.0 # Left canvas edge -> plots [cm]
    bottom_margin   =  0.0 # Bottom canvas edge -> plots [cm]
    right_margin    =  0.3 # Right canvas edge -> plots [cm]
    top_margin      =  0.0 # Top canvas edge -> plots
    dpi             =  600 # DPI for PNG outfile

    ### Style ###

    azim = -50.0 # degrees
    # azimuth angle of zero looks directly onto the c2-c3 plane

    elev = 20.0 # degrees
    # elevation angle of 90 looks onto the c1-c2 plane

    weyl_alpha = 0.0   # transparency of Weyl chamber
    PE_alpha   = 0.3   # transparency of PE polyhedron
    linecolor  = 'black'
    pointsize  = 5

    ### Canvas ###

    w = fig_width - (left_margin + right_margin)  # width of plot (cm)
    h = fig_height - (bottom_margin + top_margin) # height of plot (cm)
    cm2inch = 0.39370079 # conversion factor cm to inch
    fig = figure(figsize=(fig_width*cm2inch, fig_height*cm2inch), dpi=dpi)

    pos = [left_margin/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax = fig.add_axes(pos, projection='3d')
    ax.view_init(elev=elev, azim=azim)

    ### Plot Weyl Chamber / PE polyhedron ###

    A1 = (1, 0, 0)
    A2 = (0.5, 0.5, 0)
    A3 = (0.5, 0.5, 0.5)
    O  = (0, 0, 0)
    L  = (0.5, 0, 0)
    M  = (0.75, 0.25, 0)
    N  = (0.75, 0.25, 0.25)
    P  = (0.25, 0.25, 0.25)
    Q  = (0.25, 0.25, 0)
    B  = (0.5, 0.25, 0)
    weyl_points = {'A_1' : A1, 'A_2' : A2, 'A_3' : A3, 'O' : O, 'L' : L,
                   'M' : M, 'N' : N, 'P' : P, 'Q': Q, 'B': B}
    weyl_faces = []
    #weyl_faces.append((True, [[A1, A2, O]]))
    weyl_faces.append((True, [[A2, O, A3]]))
    weyl_faces.append((False, [[A1, A2, A3]]))
    weyl_faces.append((False, [[A1, O, A3]]))
    for hidden, face in weyl_faces:
        pol = Poly3DCollection(face)
        pol.set_facecolor((1, 1, 1, weyl_alpha))
        pol.set_edgecolor(linecolor)
        pol.set_linewidth(0.5)
        if hidden:
            pol.set_linestyle('--')
        ax.add_collection3d(pol)
    PE_faces = []
    #PE_faces.append((True,  [[L, M, A2, Q]]))
    PE_faces.append((True,  [[A2, P, Q]]))
    #PE_faces.append((True,  [[N, P, A2]]))
    PE_faces.append((True,  [[L, P, Q]]))
    PE_faces.append((True, [[L, M, N]]))
    PE_faces.append((False, [[M, A2, N]]))
    PE_faces.append((False, [[N, L, P]]))
    for hidden, face in PE_faces:
        pol = Poly3DCollection(face)
        pol.set_facecolor((0.5, 0.5, 0.5, PE_alpha))
        pol.set_edgecolor(linecolor)
        pol.set_linewidth(0.5)
        if hidden:
            pol.set_linestyle('--')
        ax.add_collection3d(pol)
    ax.scatter(*zip(*weyl_points.values()), edgecolors='None', s=pointsize,
               color='black')
    label_offsets = {
        'A_1' : (-0.1, 0.0, 0.0),
        'A_2' : (0, 0, 0),
        'A_3' : (0, 0, 0),
        'O'   : (0, -0.03, 0.01),
        'L'   : (-0.05, 0, 0.01),
        'M'   : (0.05, -0.01, 0),
        'N'   : (-0.055, 0, 0.008),
        'P'   : (-0.05, 0, 0.008),
        'B'   : (-0.05, 0, 0.008),
        'Q'   : (0, 0.01, 0.01)}
    for label, coords in weyl_points.items():
        coords = np.array(coords) + np.array(label_offsets[label])
        c = linecolor
        if label == 'Q' or label == 'B':
            c = 'DarkSlateGray'
        ax.text(coords[0], coords[1], coords[2], "$%s$" % label, color=c,
                fontsize='small')
    ax.set_xlabel('$c_1/\\pi$')
    ax.set_ylabel('$c_2/\\pi$')
    ax.set_zlabel('$c_3/\\pi$')
    ax.set_xlim(0,1)
    ax.set_ylim(0,0.5)
    ax.set_zlim(0,0.5)
    ax.patch.set_facecolor('None')
    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.grid(False)

    ax.tick_params(direction='out', pad=20)


    ### Write out ###

    format = os.path.splitext(outfile)[-1][1:]
    fig.savefig(outfile, format=format, dpi=dpi)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    plot_weyl_chamber(outfile)

if __name__ == "__main__":
    sys.exit(main())
