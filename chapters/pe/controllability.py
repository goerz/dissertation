#!/usr/bin/env python
import os
import sys
import QDYN.local_invariants as LI

# Run with most recent version of Enthought Canopy Python Distribution
# https://www.enthought.com/products/canopy/

import numpy as np

import matplotlib
from matplotlib.pyplot import figure
from mgplottools.mpl import get_color
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from mpl_toolkits.mplot3d import proj3d

from mgplottools.mpl import show_fig, write_pdf, write_png, write_eps

BLUE   = '#377EB8'


def create_figure():
    """
    Return a completed Figure instance
    """
    ### Layout ###

    font = {'family'    : "serif",
            'sans-serif':['Computer Modern Sans serif', 'Helvetica'],
            'serif'     :['Computer Modern Roman', 'Palatino'],
            'monospace' :['Computer Modern Typewriter', 'Courier'],
            'size'      : 8.00}
    matplotlib.rc('text', usetex=True)
    matplotlib.rc('font', **font)
    fig_width       =  12.0 # Total width of figure canvas [cm]
    fig_height      =  8.8  # Total height of figure canvas [cm]
    left_margin1    =  0.0  # Left canvas edge -> plot 1 [cm]
    left_margin2    =  5.9  # Left canvas edge -> plot 2 [cm]
    bottom_margin   =  4.4  # Bottom canvas edge -> top plots [cm]
    w               =  6.3
    h               =  5.0
    dpi             =  600

    cm2inch = 0.39370079 # conversion factor cm to inch
    fig = figure(figsize=(fig_width*cm2inch, fig_height*cm2inch), dpi=dpi)

    # top left
    pos = [left_margin1/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax1 = fig.add_axes(pos, projection='3d')
    plot_weyl_chamber(
        ax1,  'controllability/transmon_non_deg_cloud.dat')

    # top right
    pos = [left_margin2/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax2 = fig.add_axes(pos, projection='3d')
    plot_weyl_chamber(
        ax2, 'controllability/transmon_deg_cloud.dat')

    # bottom left
    pos = [left_margin1/fig_width, 0.0,
           w/fig_width, h/fig_height]
    ax3 = fig.add_axes(pos, projection='3d')
    plot_weyl_chamber(ax3, 'controllability/charge_2pulses_cloud.dat',
                      show_controllability=True)

    # bottom_right
    pos = [left_margin2/fig_width, 0.0,
           w/fig_width, h/fig_height]
    ax4 = fig.add_axes(pos, projection='3d')
    plot_weyl_chamber(
        ax4, 'controllability/charge_1pulse_cloud.dat',
        show_controllability=True)
    ax4.plot([0, 0.5], [0, 0.5] , [0, 0],
             linestyle='--', color='red', linewidth=1.5)

    fig.text(0.0, 1.0, '(a)', va='top', ha='left')
    fig.text(0.5, 1.0, '(b)', va='top', ha='left')
    fig.text(0.0, 0.5, '(c)', va='top', ha='left')
    fig.text(0.5, 0.5, '(d)', va='top', ha='left')

    return fig


def plot_weyl_chamber(ax, points_file, path_files=None, path_colors=None,
    show_controllability=False):
    """
    Given a 3D Axes instance, plot the Weyl chamber in that axis, and the
    points found in points_file
    """
    if path_files is None:
        path_files = []
    if path_colors is None:
        path_colors = []
    assert len(path_files) == len(path_colors), \
    "You muse give a path_color for every path_files"

    ### Style ###

    azim = -55.0 # degrees
    # azimuth angle of zero looks directly onto the c2-c3 plane

    elev = 20.0 # degrees
    # elevation angle of 90 looks onto the c1-c2 plane

    weyl_alpha = 0.0   # transparency of Weyl chamber
    PE_alpha   = 0.0   # transparency of PE polyhedron
    linecolor  = 'black'
    bgcolor    = None  # None -> default
    pointsize  = 1.5

    ax.view_init(elev=elev, azim=azim)
    ax.patch.set_facecolor('None')
    ax.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    ax.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
    # move z-axis to the left
    tmp_planes = ax.zaxis._PLANES
    ax.zaxis._PLANES = (tmp_planes[2], tmp_planes[3],
                        tmp_planes[0], tmp_planes[1],
                        tmp_planes[4], tmp_planes[5])
    ax.zaxis.set_rotate_label(False)
    ax.zaxis.label.set_rotation(90)
    ax.grid(False)
    #ax._axis3don = False # hide axis

    ### Create and plot actual data ###
    t, c1, c2, c3 = np.genfromtxt(points_file, unpack=True)
    s = ax.scatter(c1, c2, c3, c=BLUE, edgecolors='None', s=pointsize)
    # remove the "transparency fog" that matplotlib adds as to indicate
    # depth
    #s.set_edgecolors = s.set_facecolors = lambda *args:None

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
    label_offsets = {
        'A_1' : (-0.10, 0.00 , 0.00),
        'A_2' : (0.01, 0, -0.01),
        'A_3' : (-0.01, 0, 0),
        'O'   : (-0.02,  0.0, 0.02),
        }
    for label in ['O', 'A_1', 'A_2', 'A_3']:
        coords = weyl_points[label]
        coords = np.array(coords) + np.array(label_offsets[label])
        c = linecolor
        ax.text(coords[0], coords[1], coords[2], "$%s$" % label, color=c,
                fontsize='small')
    ax.set_xlabel(r'$c_1/\pi$')
    ax.set_ylabel(r'$c_2/\pi$')
    ax.set_zlabel(r'$c_3/\pi$')
    ax.set_xlim(0,1)
    ax.set_ylim(0,0.5)
    ax.set_zlim(0,0.5)
    ax.tick_params(axis='both', which='major', labelsize=7)
    ax.xaxis._axinfo['ticklabel']['space_factor'] = 0.5
    ax.yaxis._axinfo['ticklabel']['space_factor'] = 0.5
    ax.xaxis._axinfo['label']['space_factor'] = 1.8
    ax.yaxis._axinfo['label']['space_factor'] = 1.8
    [t.set_va('center') for t in ax.get_yticklabels()]
    [t.set_ha('left') for t in ax.get_yticklabels()]
    [t.set_va('center') for t in ax.get_xticklabels()]
    [t.set_ha('right') for t in ax.get_xticklabels()]
    [t.set_va('center') for t in ax.get_zticklabels()]
    [t.set_ha('center') for t in ax.get_zticklabels()]

    def draw_line(origin, end, **kwargs):
        o1, o2, o3 = origin
        c1, c2, c3 = end
        ax.plot([o1, c1], [o2, c2] , [o3, c3], **kwargs)

    if show_controllability:
        control_plane1 = Poly3DCollection(
                         [[O, (0.66667, 0.33333, 0.33333), A2]])
        control_plane1.set_edgecolor('black')
        control_plane1.set_facecolor((0.5, 0.5, 0.5, 0.1))
        control_plane1.set_linewidth(0.0)
        ax.add_collection3d(control_plane1)
        control_plane2 = Poly3DCollection([[A1, (0.3333, 0.3333, 0.3333), A2]])
        control_plane2.set_edgecolor('black')
        control_plane2.set_facecolor((0.5, 0.5, 0.5, 0.1))
        control_plane2.set_linewidth(0.0)
        ax.add_collection3d(control_plane2)
        PR = (0.66667, 0.33333, 0.33333)
        draw_line(O, PR, color='black', linestyle='-', linewidth=1.0)
        draw_line(PR, A2, color='black', linestyle='-', linewidth=1.0)
        draw_line(O, A2, color='black', linestyle='--', linewidth=1.0)
        PL = (0.33333, 0.33333, 0.33333)
        draw_line(A1, PL, color='black', linestyle='-', linewidth=1.0)
        draw_line(PL, A2, color='black', linestyle='--', linewidth=1.0)
        draw_line(A1, A2, color='black', linestyle='-', linewidth=1.0)

    for path_file in path_files:
        color = path_colors.pop(0)
        t, c1, c2, c3 = np.genfromtxt(path_file, unpack=True)
        ax.plot(xs=c1, ys=c2, zs=c3, color=color)

def main(argv=None):
    if argv is None:
        argv = sys.argv

    fig = create_figure()

    if '--show' in argv:
        fig.show()
    else:
        basename = os.path.splitext(__file__)[0]
        pdffile = basename + '.pdf'
        write_pdf(fig, pdffile)


if __name__ == "__main__":
    sys.exit(main())
