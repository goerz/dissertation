#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script for generating a plot of gate error (data included in file)
"""

import matplotlib
matplotlib.use("PDF") # backend selection (must be done before other imports)
#matplotlib.use('Agg') # for PNG output
import numpy as np
from matplotlib.pyplot import figure
import os
import sys

# Main Data:

T = [100, 200, 250, 300, 400, 500, 600, 700, 800, 900, 1000]

E_no_diss = [ 2.86e-1, 2.76e-3, 2.23e-3, 2.06e-2, 9.99e-4, 7.73e-3, 9.95e-4,
              2.30e-3, 1.47e-3, 3.80e-3, 6.97e-4]

E_100 = [ 2.87e-1, 4.43e-3, 4.14e-3, 2.29e-2, 3.32e-3, 1.06e-2, 4.00e-3,
         5.54e-3, 5.63e-3, 9.48e-3, 6.37e-3]

E_25 = [ 2.89e-1, 9.44e-3, 9.83e-3, 2.96e-2, 1.02e-2, 1.91e-2, 1.29e-2,
          1.52e-2, 1.80e-2, 2.63e-2, 2.32e-2]

Delta_U = [7.98e-2, 3.09e-3, 2.21e-3, 1.67e-2, 9.94e-4, 7.63e-3, 9.76e-4,
           2.28e-3, 1.46e-3, 3.78e-3, 6.87e-4]

# Inset data:

Pulse_E0 = [ 1300, 1200, 1000, 800, 500, 560, 530, 250, 220, 340, 170 ]

Pop_bad = [9.38e-4, 4.12e-4, 3.00e-4, 9.09e-4, 1.15e-5, 1.41e-3, 4.18e-8,
           4.14e-7, 6.43e-8, 6.92e-6, 1.17e-8]

N_c = [26, 32, 39, 51, 21, 56, 19, 26, 21, 25, 16]
N_q = [ 5, 6, 5, 5, 5, 5, 5, 5, 4, 5, 4]


def plot_gate_error(outfile):
    font = {'family'    : "serif",
            'sans-serif':['Computer Modern Sans serif', 'Helvetica'],
            'serif'     :['Computer Modern Roman', 'Palatino'],
            'monospace' :['Computer Modern Typewriter', 'Courier'],
            'size'      :  9.00}
    matplotlib.rc('text', usetex=True)
    matplotlib.rc('font', **font)
    fig_width       =  17.0       # Total width of canvas [cm]
    fig_height      =  12.0       # Total height of canvas [cm]
    left_margin     =  1.0        # Left canvas edge -> plot area [cm]
    bottom_margin   =  1.0        # Bottom canvas edge -> plot area [cm]
    right_margin    =  0.5        # Right canvas edge -> plot area [cm]
    top_margin      =  0.3        # Top canvas edge -> plot area [cm]
    format          = 'pdf'       # Output format
    gui             = False       # Do not use GUI
    dpi             = 600         # Resolution (PNG)

    # Process data & plot
    h = (fig_height - (top_margin + bottom_margin)) # height of  plot (cm)
    w = fig_width - (left_margin + right_margin)    # width of plots (cm)
    cm2inch = 0.39370079 # conversion factor cm to inch
    fig = figure(figsize=(fig_width*cm2inch, fig_height*cm2inch), dpi=dpi)
    ax = [] # instances of matplotlib.axes.Axes
    print "Figure height: ", fig_height, " cm"
    print "Figure width : ", fig_width, " cm"
    print "Plot height: ", h, " cm"
    print "Plot width : ", w, " cm"
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    a = fig.add_axes(pos)
    a.plot(T, E_no_diss, color="Black", marker='o', label=r'gate error, no dissipation ')
    a.plot(T, E_25, color="Red", marker='o', label=r'gate error, $\tau = 25 \mu$s')
    a.plot(T, E_100, color="Blue", marker='o', label=r'gate error, $\tau = 100 \mu$s')
    a.plot(T, Delta_U, color="Gray", label=r'$\Delta_U$')
    a.set_yscale('log')
    a.set_xlabel("gate duration [ns]")
    a.set_ylim(3e-4, 1)
    a.legend(loc=8, ncol=2, frameon=False, prop={'size':9})
    ax.append(a)

    # inlet: Pop_bad (left bottom)
    #                 left, bottom, width, height
    a = fig.add_axes([ 0.18,   0.65,   0.35, 0.15])
    a.plot(T, Pop_bad, marker='x')
    a.set_yscale('log')
    a.text(0.9,0.9, r'$\int P_{b} \, dt / T$', transform=a.transAxes,
           horizontalalignment='right', verticalalignment='top')
    ax.append(a)

    # inlet: E_0 (left top)
    #                 left, bottom, width, height
    a = fig.add_axes([ 0.18,   0.8,   0.35, 0.15])
    a.plot(T, Pulse_E0, marker='x')
    a.set_ylim(0, 1300)
    a.set_yticks([250, 500, 750, 1000, 1250])
    a.set_xticklabels([])
    a.text(0.9,0.9, r'$E_0$ [GHz] (opt. pulse)', transform=a.transAxes,
           horizontalalignment='right', verticalalignment='top')
    ax.append(a)


    # inlet: N_c (right bottom)
    #                 left, bottom, width, height
    a = fig.add_axes([ 0.59,   0.65,   0.35, 0.15])
    a.set_yticks(range(20,60,10))
    a.plot(T, N_c, marker='x')
    a.text(0.9,0.9, r'$N_c$', transform=a.transAxes,
           horizontalalignment='right', verticalalignment='top')
    ax.append(a)


    # inlet: N_q (right top)
    #                 left, bottom, width, height
    a = fig.add_axes([ 0.59,   0.8,   0.35, 0.15])
    a.plot(T, N_q, marker='x')
    a.set_xticklabels([])
    a.set_ylim(3.5,6.5)
    a.set_yticks([4,5,6])
    a.text(0.9,0.9, r'$N_q$', transform=a.transAxes,
           horizontalalignment='right', verticalalignment='top')
    ax.append(a)

    for a in ax:
        a.set_xlim(100, 1000)

    if gui:
        fig.show()
    fig.savefig(outfile, format=format, dpi=dpi)


def main(argv=None):
    """ Main Routine """

    backend = matplotlib.get_backend().lower()
    print "Using backend: ", backend

    # Generate Plot
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    plot_gate_error(outfile)


if __name__ == "__main__":
    sys.exit(main())

