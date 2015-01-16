#!/usr/bin/env python
import os
import sys
import re
import numpy as np
from glob import glob
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import set_axis, new_figure, set_color_cycle

CHARGEVALS    = [-2.0, -1.0, 0.0, 1.0, 2.0, 3.0] # charge quantum numbers
N_LEVELS = 5

def create_figure(outfile):
    """Create figure of charge dispersion, for different values of EJ/EC"""

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.1               # Left cv -> plot area
    right_margin    = 0.25              # plot area -> right cv
    top_margin      = 0.55              # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> plot area
    h               = 3.5               # height of each panel
    gap             = 0.75              # horizontal gap between panels
    n_panels        = 3

    # width of panels
    w = (fig_width - (left_margin + right_margin) - (n_panels-1)*gap)  \
        / n_panels
    fig_height = bottom_margin + h + top_margin

    fig = new_figure(fig_width, fig_height)
    EC = 1.0

    set_color_cycle()

    # panel 1
    EJ = 0.5
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    plot_charge_dispersion(ax, EJ, EC, title="$E_J/E_C=%.1f$"%EJ)
    set_axis(ax, 'y', 0, 30, 5, minor=4, label="$E/E_C$", range=(-0.5, 30))
    set_axis(ax, 'x', 0, 1, 0.5, minor=2, label="$n_g$",
             ticklabels=["0", "0.5", "1"])

    # panel 2
    EJ = 5.0
    pos = [(left_margin+w+gap)/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    plot_charge_dispersion(ax, EJ, EC, title="$E_J/E_C=%.1f$"%EJ)
    #set_axis(ax, 'y', 0, 7, 1, minor=2, range=(-0.1, 7))
    set_axis(ax, 'y', 0, 30, 5, minor=4, range=(-0.5, 30))
    set_axis(ax, 'x', 0, 1, 0.5, minor=2, label="$n_g$",
             ticklabels=["0", "0.5", "1"])

    # panel 3
    EJ = 50.0
    pos = [(left_margin+2*(w+gap))/fig_width, bottom_margin/fig_height,
            w/fig_width, h/fig_height]
    ax = fig.add_axes(pos)
    plot_charge_dispersion(ax, EJ, EC, title="$E_J/E_C=%.1f$"%EJ)
    #set_axis(ax, 'y', 0, 20, 5, minor=5, range=(-0.5,20))
    set_axis(ax, 'y', 0, 90, 10, minor=2, range=(-2, 95))
    set_axis(ax, 'x', 0, 1, 0.5, minor=2, label="$n_g$",
             ticklabels=["0", "0.5", "1"])

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def plot_charge_dispersion(ax, EJ, EC, chargevals=None, n_levels=None,
    ng_min=0.0, ng_max=1.0, samples=50, title=None):
    """Generate a plot of the charge qubit energy levels on the Axes ax"""
    ngs = np.linspace(ng_min, ng_max, samples)
    if title is not None:
        ax.set_title(title)
    if chargevals is None:
        chargevals = CHARGEVALS
    if n_levels is None:
        n_levels = N_LEVELS
    E = []
    for __ in xrange(n_levels):
        E.append(np.zeros(samples))
    for i, ng in enumerate(ngs):
        H = get_ham(EJ, EC, ng, chargevals)
        evals, evecs = np.linalg.eig(H)
        order = evals.argsort()
        evals = evals[order]
        evecs = evecs[order]
        for n in xrange(n_levels):
            E[n][i] = evals[n] / EC
    offset = E[0][0]
    for n in xrange(n_levels):
        ax.plot(ngs, E[n]-offset)


def get_ham(EJ, EC, ng, chargevals=None):
    """Construct the charge qubit Hamiltonian"""
    if chargevals is None:
        chargevals = CHARGEVALS
    n_levels = len(chargevals)
    H = np.zeros((n_levels,n_levels))
    for i, n in enumerate(chargevals):
        for j in xrange(n_levels):
            if i == j:
                H[i,j] = 4*EC * (n-ng)**2
            elif i == j+1 or i == j-1:
                H[i,j] = -0.5*EJ
    return H


def print_eigensystem(EJ, EC, ng, chargevals=None, n_levels=None):
    if chargevals is None:
        chargevals = CHARGEVALS
    if n_levels is None:
        n_levels = N_LEVELS
    H = get_ham(EJ, EC, ng, chargevals)
    print "****"
    print "Charge Qubit Hamiltonian for EJ=%s, EC=%s" % (EJ, EC)
    print "H = "
    import QDYN
    QDYN.io.print_matrix(H)
    evals, evecs = np.linalg.eig(H)
    order = evals.argsort()
    evals = evals[order]
    evecs = evecs[order]
    for n in xrange(n_levels):
        print ""
        print "eval %d: %f" % (n, evals[n] / EC)
        print "evec %d: %s" % (n, charge_state_str(evecs[n], chargevals))
    print ""


def charge_state_str(charge_state, chargevals):
    fmt = "%.3f \\ket{%d}"
    result = ''
    for i, ampl in enumerate(charge_state):
        if result == '':
            result = fmt % (ampl, chargevals[i])
        else:
            result += " + " + fmt % (ampl, chargevals[i])
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile)
    #print_eigensystem(EJ=20.0, EC=1.0, ng=0.5)

if __name__ == "__main__":
    sys.exit(main())
