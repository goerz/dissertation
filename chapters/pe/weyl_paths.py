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

PURPLE = '#984EA3'
BLUE   = '#377EB8'
RED    = '#E41A1C'


def weyl_path(datfile):
    """
    Extract the Weyl chamber coordinates c1, c2, c3 as numpy arrays over
    iteration number the local_invariants_oct_iter.dat file written during
    optimization.
    """
    c1, c2, c3 = np.genfromtxt(datfile, usecols=(8,9,10), unpack=True)
    return zip(c1, c2, c3)


def PE_dist(c1, c2, c3):
    """
    Return distance of (c1, c3, c3) to PE polyhedron, zero if inside
    """
    if (c1 + c2 <= 0.5):
        F = np.cos(np.pi*(c1 + c2 - 0.5) / 4.0)**2
    elif (c2 + c3 >= 0.5):
        F = np.cos(np.pi*(c2 + c3 - 0.5) / 4.0)**2
    elif (c1 - c2 >= 0.5):
        F = np.cos(np.pi*(c1 - c2 - 0.5) / 4.0)**2
    else:
        F = 1.0
    return 1.0-F


def dist(p1, p2):
    """
    Return Eucledian distance between points p1, p2 in the Weyl chamber
    """
    c1, c2, c3 = p1
    s1, s2, s3 = p2
    d1 = (c1 - s1)**2
    d2 = (c2 - s2)**2
    d3 = (c3 - s3)**2
    return np.sqrt(d1 + d2 + d3)


def filter_path(path):
    """
    Given an array of Weyl chamber points, return a filtered array:
    * drop points that are extremely close to the previous point
    * stop as soon as the points enter the PE polyhedron
    """
    LIMIT = 0.005
    result = []
    for point in path:
        if len(result) == 0:
            result.append(point)
        elif dist(point, result[-1]) > LIMIT:
            result.append(point)
        if PE_dist(*point) == 0.0:
            return result
    return result


def end_point(path):
    """
    Given an array of Weyl chamber points, return either the last element of
    the array or the first element that is inside the PE polyhedron
    """
    for point in path:
        if PE_dist(*point) == 0.0:
            return point
    return path[-1]


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
    PE_alpha   = 0.1   # transparency of PE polyhedron
    linecolor  = 'black'
    bgcolor    = None  # None -> default
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
    weyl_points = {'A_1' : A1, 'A_2' : A2, 'A_3' : A3, 'O' : O, 'L' : L,
                   'M' : M, 'N' : N, 'P' : P, 'Q': Q}
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
    #ax.scatter(*zip(*weyl_points.values()), edgecolors='None', s=1.0)
    label_offsets = {
        'A_1' : (-0.1, 0.0, 0.0),
        'A_2' : (0, 0, 0),
        'A_3' : (0, 0, 0),
        'O'   : (0, -0.03, 0.01),
        'L'   : (-0.05, 0, 0.01),
        'M'   : (0.05, -0.01, 0),
        'N'   : (-0.055, 0, 0.008),
        'P'   : (-0.05, 0, 0.008),
        'Q'   : (0, 0.01, 0.01)}
    for label, coords in weyl_points.items():
        coords = np.array(coords) + np.array(label_offsets[label])
        c = linecolor
        if label == 'Q':
            c = 'DarkSlateGray'
        ax.text(coords[0], coords[1], coords[2], "$%s$" % label, color=c,
                fontsize='small')
    ax.set_xlabel('$c_1/\\pi$')
    ax.set_ylabel('$c_2/\\pi$')
    ax.set_zlabel('$c_3/\\pi$')
    ax.set_xlim(0,1)
    ax.set_ylim(0,0.5)
    ax.set_zlim(0,0.5)
    if bgcolor is not None:
        ax.w_xaxis.set_pane_color(bgcolor)
        ax.w_yaxis.set_pane_color(bgcolor)
        ax.w_zaxis.set_pane_color(bgcolor)

    ### Create and plot actual data ###

    weyl_paths = {
        25 : weyl_path("weyl_paths/25.dat"),
        40 : weyl_path("weyl_paths/40.dat"),
        50 : weyl_path("weyl_paths/50.dat"),
        75 : weyl_path("weyl_paths/75.dat"),
        100 : weyl_path("weyl_paths/100.dat"),
        200 : weyl_path("weyl_paths/200.dat"),
        300 : weyl_path("weyl_paths/300.dat"),
        400 : weyl_path("weyl_paths/400.dat"),
    }

    path_50 = filter_path(weyl_paths[50])
    s = ax.scatter(*zip(*path_50), c=BLUE, edgecolors='None', s=pointsize)
    # remove the "transparency fog" that matplotlib adds as to indicate depth
    #s.set_edgecolors = s.set_facecolors = lambda *args:None

    path_400 = filter_path(weyl_paths[400])
    s = ax.scatter(*zip(*path_400), c=PURPLE, edgecolors='None', s=pointsize)
    # remove the "transparency fog" that matplotlib adds as to indicate depth
    #s.set_edgecolors = s.set_facecolors = lambda *args:None

    end_points = []
    for label in weyl_paths.keys():
        end_points.append(end_point(weyl_paths[label]))
        c1, c2, c3 = end_points[-1]
        label_origin = {
             25 : (0, 0.01, 0.3),
             40 : (0, 0.11,  0.3),
             75 : (0, 0.21, 0.3),
             50 : (0, 0.31,  0.3),
            400 : (0.55, 0.5, 0.3),
            200 : (0.85, 0.5, 0.3),
            300 : (0.7, 0.5, 0.3),
            100 : (0.85, 0.5, 0.02),
        }
        o1, o2, o3 = label_origin[label]
        ax.plot([o1, c1], [o2, c2] , [o3, c3], # label line
                color='black', linestyle='-', linewidth=0.2)
        ax.text(o1-0.025, o2, o3, label, color=linecolor, fontsize='small')
        if label == 50: # label for starting point
            o1, o2, o3 = (0.9, 0.15, 0.0)
            c1, c2, c3 = weyl_paths[label][0] # starting point
            ax.plot([o1, c1], [o2, c2] , [o3, c3], # label line
                    color='black', linestyle='-', linewidth=0.2)
            ax.text(o1, o2, o3, "50$^*$", color=linecolor, fontsize='small')
        if label == 400: # label for starting point
            o1, o2, o3 = (0.81, 0.05, 0.01)
            c1, c2, c3 = weyl_paths[label][0] # starting point
            ax.plot([o1, c1], [o2, c2] , [o3, c3], # label line
                    color='black', linestyle='-', linewidth=0.2)
            ax.text(o1, o2, o3, "400$^*$", color=linecolor,
                    horizontalalignment='right', fontsize='small')
    s = ax.scatter(*zip(*end_points), c=RED, edgecolors='None', s=pointsize)
    # remove the "transparency fog" that matplotlib adds as to indicate depth
    #s.set_edgecolors = s.set_facecolors = lambda *args:None
    ax.tick_params(direction='out', pad=20)


    ### Write out ###

    format = os.path.splitext(outfile)[-1][1:]
    fig.savefig(outfile, format=format, dpi=dpi)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    #plot_weyl_chamber(outfile='weyl_paths.png')
    #os.system("convert weyl_paths.png weyl_paths.eps")

    plot_weyl_chamber(outfile='weyl_paths.pdf')

if __name__ == "__main__":
    sys.exit(main())
