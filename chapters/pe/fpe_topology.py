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

FPE_MIN = 10.0
FPE_MAX = -10.0


def create_figure():
    """
    Return a completed Figure instance
    """
    global FPE_MIN, FPE_MAX

    ### Layout ###

    font = {'family'    : "serif",
            'sans-serif':['Computer Modern Sans serif', 'Helvetica'],
            'serif'     :['Computer Modern Roman', 'Palatino'],
            'monospace' :['Computer Modern Typewriter', 'Courier'],
            'size'      : 8.00}
    matplotlib.rc('text', usetex=True)
    matplotlib.rc('font', **font)
    fig_width       =  12.0 # Total width of figure canvas [cm]
    fig_height      =  4.4  # Total height of figure canvas [cm]
    left_margin1    =  0.0  # Left canvas edge -> plot 1 [cm]
    left_margin2    =  5.9  # Left canvas edge -> plot 2 [cm]
    bottom_margin   =  0.0  # Bottom canvas edge -> top plots [cm]
    w               =  6.3
    h               =  5.0
    dpi             =  600
    colorbar_width  =  0.3
    colorbar_left   =  4.65
    colorbar_bottom =  1.65
    colorbar_height =  2.6

    cm2inch = 0.39370079 # conversion factor cm to inch
    fig = figure(figsize=(fig_width*cm2inch, fig_height*cm2inch), dpi=dpi)

    FPE_MIN = 10.0
    FPE_MAX = -10.0

    # left
    pos = [left_margin1/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax1 = fig.add_axes(pos, projection='3d')
    s1 = plot_weyl_chamber(ax1,  inside=False)
    ax_colorbar1 = fig.add_axes([(left_margin1 + colorbar_left)/fig_width,
                                 colorbar_bottom/fig_height,
                                 colorbar_width/fig_width,
                                 colorbar_height/fig_height])
    cbar = fig.colorbar(s1, cax=ax_colorbar1,
                        ticks=[-1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5] )
    cbar.solids.set_rasterized(True)
    cbar.outline.set_linewidth(0)
    cbar.ax.tick_params(labelsize=7)

    print "== Outside =="
    print "Minimum value: ", FPE_MIN
    print "Maximum value: ", FPE_MAX
    print ""

    FPE_MIN = 10.0
    FPE_MAX = -10.0

    # right
    pos = [left_margin2/fig_width, bottom_margin/fig_height,
           w/fig_width, h/fig_height]
    ax2 = fig.add_axes(pos, projection='3d')
    s2 = plot_weyl_chamber(ax2,  inside=True, show_c3_label=False)
    ax_colorbar2 = fig.add_axes([(left_margin2 + colorbar_left)/fig_width,
                                 colorbar_bottom/fig_height,
                                 colorbar_width/fig_width,
                                 colorbar_height/fig_height])
    cbar = fig.colorbar(s2, cax=ax_colorbar2,
                        ticks=[-0.050, -0.025, 0.0, 0.025, 0.05])
    cbar.solids.set_rasterized(True)
    cbar.outline.set_linewidth(0)
    cbar.ax.tick_params(labelsize=7)

    print "== INSIDE =="
    print "Minimum value: ", FPE_MIN
    print "Maximum value: ", FPE_MAX
    print ""

    return fig


def fpe(c1, c2, c3):
    """
    Return value of perfect entanglers functional for Weyl chamber coordinates
    c1, c2, c3
    """
    global FPE_MIN, FPE_MAX
    g1, g2, g3 = LI.g1g2g3_from_c1c2c3(c1, c2, c3)
    f = LI.FPE(g1, g2, g3)
    if f < FPE_MIN:
        FPE_MIN = f
    if f > FPE_MAX:
        FPE_MAX = f
    return f


def fpe_topology(inside, n=25):
    """
    Return four arrays, c1, c2, c3, f
    """

    c1s = []
    c2s = []
    c3s = []
    fs  = []

    c1_candidates = np.linspace(0, 1.0, n)
    c2_candidates = np.linspace(0, 0.5, n)
    c3_candidates = np.linspace(0, 0.5, n)

    for c1 in c1_candidates:
        for c2 in c2_candidates:
            for c3 in c3_candidates:
                if LI.point_in_weyl_chamber(c1, c2, c3):
                    if ((inside and LI.point_in_PE(c1, c2, c3))
                    or  (not inside and not LI.point_in_PE(c1, c2, c3))):
                        f = fpe(c1, c2, c3)
                        c1s.append(c1)
                        c2s.append(c2)
                        c3s.append(c3)
                        fs.append(f)
    return np.array(c1s), np.array(c2s), np.array(c3s), np.array(fs)


def plot_weyl_chamber(ax, inside, show_c3_label=True):
    """
    Given a 3D Axes instance, plot the Weyl chamber in that axis, and the
    points found in points_file
    """
    ### Style ###

    azim = -55.0 # degrees
    #azim = 60.0 # degrees
    # azimuth angle of zero looks directly onto the c2-c3 plane

    elev = 20.0 # degrees
    # elevation angle of 90 looks onto the c1-c2 plane

    weyl_alpha = 0.0   # transparency of Weyl chamber
    PE_alpha   = 0.0   # transparency of PE polyhedron
    linecolor  = 'black'
    bgcolor    = None  # None -> default
    pointsize  = 5.0
    linewidth  = 0.5

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

    def draw_line(origin, end, **kwargs):
        o1, o2, o3 = origin
        c1, c2, c3 = end
        ax.plot([o1, c1], [o2, c2] , [o3, c3], **kwargs)
        #draw_line(O, PR, color='black', linestyle='-', lw=linewidth)

    # background lines
    #   Weyl chamber
    draw_line(O, A2, color='black', linestyle='--', lw=linewidth, zorder=-1)
    #   PE
    draw_line(P, Q, color='black',  linestyle='--', lw=linewidth, zorder=-1)
    draw_line(P, A2, color='black', linestyle='--', lw=linewidth, zorder=-1)
    if not inside:
        draw_line(M, L, color='black', linestyle='--', lw=linewidth, zorder=-1)

    ### Create and plot actual data ###
    c1, c2, c3, f = fpe_topology(inside)
    s = ax.scatter3D(c1, c2, c3, c=f, edgecolors='None', s=pointsize,
                     cmap='RdYlBu_r', rasterized=False, zorder=1000)
    # remove the "transparency fog" that matplotlib adds as to indicate
    # depth
    s.set_edgecolors = s.set_facecolors = lambda *args:None

    # foreground lines
    #   Weyl chamber
    draw_line(O, A1, color='black', linestyle='-', lw=linewidth)
    draw_line(A1, A2, color='black', linestyle='-', lw=linewidth)
    draw_line(A2, A3, color='black', linestyle='-', lw=linewidth)
    draw_line(A3, A1, color='black', linestyle='-', lw=linewidth)
    draw_line(A3, O, color='black', linestyle='-', lw=linewidth)
    #   PE
    draw_line(L, N, color='black', linestyle='-', lw=linewidth)
    draw_line(L, P, color='black', linestyle='-', lw=linewidth)
    draw_line(N, P, color='black', linestyle='-', lw=linewidth)
    draw_line(N, A2, color='black', linestyle='-', lw=linewidth)
    draw_line(N, M, color='black', linestyle='-', lw=linewidth)
    if inside:
        draw_line(M, L, color='black', linestyle='--', lw=linewidth)
    else:
        draw_line(Q, L, color='black', linestyle='--',lw=linewidth)

        #'A_1' : (-0.10, 0.00 , 0.00),
    label_offsets = {
        'A_1' : (-0.03, 0.04 , 0.00),
        'A_2' : (0.01, 0, -0.01),
        'A_3' : (-0.01, 0, 0),
        'O'   : (-0.025,  0.0, 0.02),
        'L'   : (-0.075, 0, 0.01),
        'M'   : (0.05, -0.01, 0),
        'N'   : (-0.075, 0, 0.009),
        'P'   : (-0.05, 0, 0.008),
        'Q'   : (0, 0.01, 0.03),
        }
    for label in ['O', 'A_1', 'A_2', 'A_3', 'M', 'N', 'P', 'L', 'Q']:
        if inside and label == 'Q':
            continue
        coords = weyl_points[label]
        coords = np.array(coords) + np.array(label_offsets[label])
        c = linecolor
        ax.text(coords[0], coords[1], coords[2], "$%s$" % label, color=c,
                fontsize='small')
    ax.set_xlabel(r'$c_1/\pi$')
    ax.set_ylabel(r'$c_2/\pi$')
    if show_c3_label:
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
    return s



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
        #write_png(fig, pdffile, dpi=600)


if __name__ == "__main__":
    sys.exit(main())
