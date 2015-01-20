#!/usr/bin/env python
import matplotlib
from matplotlib.ticker import FormatStrFormatter
matplotlib.use("PDF")
from matplotlib.pyplot import figure
import os
import sys
import numpy as np
from QDYN.pulse import Pulse
from QDYNTransmonLib.io import collect_pop_plot_data
from mgplottools.mpl import set_axis, new_figure, get_color
import matplotlib.patches as mpatches


def plot_datasets(cavity_data, q1_data, q2_data, pop_data, pulse, outfile):
    """ Create plot for the given data sets.

        Arguments:

        cavity_data   ExcitationDataSet for cavity
        q1_data       ExcitationDataSet for left qubit
        q2_data       ExcitationDataSet for right qubit
        pop_data      PopulationDataSet for logical subspace
        pulse         Pulse data
        outfile       Name of output data file (without extension)
    """
    fig_width       = 8.5     # Total width of canvas [cm]
    pop_plot_height = 2.0     # Height of plot of population dynamics in
                              # the logical subspace (bottom plot) [cm]
    exc_plot_height = 1.5     # Height of plot of mean population numbers
                              # in the qubits and the cavity (top 3 plots) [cm]
    left_margin     =  1.2    # Left canvas edge -> plot area [cm]
    bottom_margin   =  1.0    # Bottom canvas edge -> plot area [cm]
    right_margin    =  0.3    # Right canvas edge -> plot area [cm]
    top_margin      =  0.1    # Top canvas edge -> plot area [cm]


    fig_height = top_margin + 3.0 * exc_plot_height \
                 + pop_plot_height + bottom_margin
    w = fig_width - (left_margin + right_margin)    # width of plots (cm)

    fig = new_figure(fig_width, fig_height)

    ax = [] # instances of matplotlib.axes.Axes

    # Plot population dynamics in logical subspace
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, pop_plot_height/fig_height]
    a = fig.add_axes(pos)
    p00, = a.plot(pop_data.tgrid, pop_data.pop00, color=get_color('red'))
    #p01, = a.plot(pop_data.tgrid, pop_data.pop01, color=get_color('blue'))
    #p10, = a.plot(pop_data.tgrid, pop_data.pop10, color=get_color('orange'))
    #p11, = a.plot(pop_data.tgrid, pop_data.pop11, color=get_color('purple'))
    #tot, = a.plot(pop_data.tgrid,
                  #pop_data.pop00+pop_data.pop10+pop_data.pop01+pop_data.pop11,
                  #color='Grey')
    a.axhline(y=1, ls='--', color='Gray')
    set_axis(a, 'y', 0, 1.0, 0.5, range=(0,1.5), minor=5, label='population',
             label_coords=(-0.85/w, 0.5))
    set_axis(a, 'x', 0, 200, 25, minor=5, label="time (ns)")
    #a.legend([p00, p01, p10, p11], ["00", "01", "10", "11"], ncol=4, loc=9)
    a.legend([p00, ], ["00", ], ncol=1, loc='upper left',
             bbox_to_anchor=(0.1, 1.0), borderpad=0)
    a.text(0.25/w, (pop_plot_height-0.2)/pop_plot_height, "d)",
           transform=a.transAxes, verticalalignment='top',
           horizontalalignment='left')
    # Also plot the pulse
    a2 = a.twinx()
    a2.fill_between(pulse.tgrid,
                    np.abs(pulse.amplitude)/np.max(np.abs(pulse.amplitude)),
                    color='Blue', facecolor='Blue', alpha=0.1)
    blue_patch = mpatches.Patch(color='Blue', alpha=0.1, label='pulse')
    a2.legend(handles=[blue_patch], ncol=1, loc='upper right',
              bbox_to_anchor=(1.0, 1.0), borderpad=0)
    set_axis(a2, 'y', 0, 1.0, 0.5, range=(0,1.5), minor=5, ticklabels=False)

    # patch to use in excitation legend
    gray_patch = mpatches.Patch(color='LightGray')

    # Plot excitation of left qubit
    pos = [left_margin/fig_width, (bottom_margin+pop_plot_height)/fig_height,
           w/fig_width, exc_plot_height/fig_height]
    a = fig.add_axes(pos)
    a.fill_between(q1_data.tgrid, q1_data.sd, color='LightGray',
                   facecolor='LightGray')
    pmq1, = a.plot(q1_data.tgrid, q1_data.mean, color='black')
    set_axis(a, 'x', 0, 200, 25, minor=5, ticklabels=False)
    set_axis(a, 'y', 0, 0.45, 0.2, range=(0, 0.55), minor=4)
    a.legend([pmq1, gray_patch], [r'$\langle i \rangle$', r'$\sigma_i$'],
             ncol=1, loc='upper right', borderpad=0)
    a.text(0.25/w, (exc_plot_height-0.2)/exc_plot_height, "c)",
           transform=a.transAxes, verticalalignment='top',
           horizontalalignment='left')

    # Plot excitation of right qubit
    pos = [left_margin/fig_width,
           (bottom_margin+pop_plot_height+exc_plot_height)/fig_height,
           w/fig_width, exc_plot_height/fig_height]
    a = fig.add_axes(pos)
    a = fig.add_axes(pos)
    a.fill_between(q2_data.tgrid, q2_data.sd, color='LightGray',
                   facecolor='LightGray')
    pmq2, = a.plot(q2_data.tgrid, q2_data.mean, color='black')
    set_axis(a, 'x', 0, 200, 25, minor=5, ticklabels=False)
    set_axis(a, 'y', 0, 0.45, 0.2, range=(0,0.55), minor=4,
             label='qubit and cavity excitations', label_coords=(-0.85/w, 0.5))
    a.legend([pmq2, gray_patch], [r'$\langle j \rangle$', r'$\sigma_j$'],
             ncol=1, loc='upper right', borderpad=0)
    a.text(0.25/w, (exc_plot_height-0.2)/exc_plot_height, "b)",
           transform=a.transAxes, verticalalignment='top',
           horizontalalignment='left')

    # Plot excitation of cavity
    pos = [left_margin/fig_width,
           (bottom_margin+pop_plot_height+2*exc_plot_height)/fig_height,
           w/fig_width, exc_plot_height/fig_height]
    a = fig.add_axes(pos)
    a.fill_between(cavity_data.tgrid, cavity_data.sd, color='LightGray',
                   facecolor='LightGray')
    pmc, = a.plot(cavity_data.tgrid, cavity_data.mean, color='black')
    set_axis(a, 'x', 0, 200, 25, minor=5, ticklabels=False)
    set_axis(a, 'y', 0, 55, 20, minor=4)
    a.legend([pmc, gray_patch], [r'$\langle n \rangle$', r'$\sigma_n$'],
             ncol=1, loc='upper right', borderpad=0)
    a.text(0.25/w, (exc_plot_height-0.2)/exc_plot_height, "a)",
           transform=a.transAxes, verticalalignment='top',
           horizontalalignment='left')

    # write out
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def main(argv=None):
    """ Main Routine """

    rf = 'holonomic_entanglement/params2d40_T200'

    psi_files = [
    'psi00_cavity.dat', 'psi00_q1.dat', 'psi00_q2.dat', 'psi00_phases.dat',
    'psi01_cavity.dat', 'psi01_q1.dat', 'psi01_q2.dat', 'psi01_phases.dat',
    'psi10_cavity.dat', 'psi10_q1.dat', 'psi10_q2.dat', 'psi10_phases.dat',
    'psi11_cavity.dat', 'psi11_q1.dat', 'psi11_q2.dat', 'psi11_phases.dat'
    ]

    data = collect_pop_plot_data(psi_files, rf)

    # Load pulse
    pulse = Pulse(os.path.join(rf, 'pulse.dat'))

    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'

    # Generate Plots
    assert(len(data) == 16), "Unexpected number of data sets"
    # The elements of data correspond to psi_files / rho_files above
    #print "Plotting 00"
    #             cav exc  q1 exc   q2 exc   log pop
    plot_datasets(data[0], data[1], data[2], data[3], pulse,
                  outfile)
    #print "Plotting 01"
    #plot_datasets(data[4], data[5], data[6], data[7], pulse,
    #              os.path.join(rf, 'popdyn01'))
    #print "Plotting 10"
    #plot_datasets(data[8], data[9], data[10], data[11], pulse,
    #              os.path.join(rf, 'popdyn10'))
    #print "Plotting 11"
    #plot_datasets(data[12], data[13], data[14], data[15], pulse,
    #              os.path.join(rf, 'popdyn11'))

    return(0)


if __name__ == "__main__":
    sys.exit(main())

