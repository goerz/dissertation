#!/usr/bin/env python
import os
import sys
import re
import numpy as np
from glob import glob
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import set_axis, new_figure # pip install mgplottools

def create_figure(outfile, E, entanglement, nc, nq):
    """
    E is a an array of pulse amplitudes

    entanglement is dictionary with with following structure:

        entanglement[<paramset>][<detuning>] = <array of values, over E>

    e.g. `entanglement[1][-40]` would contains the data from the file
    `entanglement_params1d-40_T200.dat`

    nc and nq contain the number of cavity and qubit levels used in the
    propagation in order to reach convergence, also as a dictionary

        nc[<paramset>][<detuning>] = <value>
        nq[<paramset>][<detuning>] = <value>

    There will be on panel per parameter set and one curve per detuning
    """

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    legend_offset   = fig_width-3.9     # Left cv -> legend
    left_margin     = 1.0               # Left cv -> plot area
    right_margin    = 4.1               # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> plot area
    p1_offset       = 0.8               # bottom cv -> panel 1
    h               = 2.0               # height of each panel
    gap             = 0.0               # gap between panels
    w = fig_width - (left_margin + right_margin)  # width of panel
    n_panels = len(entanglement.keys())

    fig_height = bottom_margin + n_panels*h + (n_panels-1)*gap + top_margin
    fig = new_figure(fig_width, fig_height)

    param_sets = entanglement.keys()
    param_sets.sort()
    bottom_set = param_sets[-1]
    for i_panel, param_set in enumerate(param_sets):
        # each param_set is one panel; we start from the top
        p_offset = bottom_margin + (n_panels-i_panel-1)*(h+gap)
        pos = [left_margin/fig_width, p_offset/fig_height,
               w/fig_width, h/fig_height]
        ax = fig.add_axes(pos)
        detunings = entanglement[param_set].keys()
        detunings.sort()
        for detuning in detunings:
            label = "$d = %d$~MHz (%d/%d)" \
                    % (detuning, nc[param_set][detuning],
                       nq[param_set][detuning])
            n_points = len(entanglement[param_set][detuning])
            ax.plot(E[:n_points], entanglement[param_set][detuning],
                    label=label)
        if param_set == bottom_set:
            set_axis(ax, 'x', E[0], E[-1], 50, minor=5,
                     label=r'peak pulse amplitude $E_0$ (MHz)')
        else:
            set_axis(ax, 'x', E[0], E[-1], 50, minor=5, ticklabels=False)
        set_axis(ax, 'y', 0, 1, 0.5, minor=5)
        if i_panel == 0: # top panel
            ax.set_yticklabels(['0', '0.5', '1.0'])
        else:
            ax.set_yticklabels(['0', '0.5', ''])
        ax.legend(loc='center left', title="parameter set %d" % param_set,
                  bbox_to_anchor=(legend_offset/fig_width,
                                 (p_offset + 0.5*h)/fig_height),
                  bbox_transform=fig.transFigure,
                  labelspacing=0.1, fontsize="small",
                  borderpad=0.0, borderaxespad=0.0)
        panels_total_height = n_panels*h + (n_panels-1)*gap
    fig.text(0, (bottom_margin + 0.5*panels_total_height)/fig_height,
             'entanglement (concurrence) after $T=\SI{200}{ns}$',
             rotation='vertical', ha='left', va='center')

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def arg_first_extr(a):
    """
    Given an array a, return the index of the first local maximum in a
    """
    i_last = len(a)-1
    for i, val in enumerate(a):
        if i == 0:
            continue
        if i == i_last:
            return i
        if a[i-1] < val > a[i+1]:
            return i
        if a[i-1] > val < a[i+1]:
            return i

def read_data(data_folder):
    """
    Return E (array), entanglement (dict), nc (dict), nq (dict)
    """
    entanglement = {}
    nc = {}
    nq = {}
    filename_rx = re.compile(
    'entanglement_params(?P<param_set>\d+)d(?P<det>[\d-]+)_T200.dat')
    datfiles = glob(os.path.join(data_folder, 'entanglement_*_T200.dat'))
    for filename in datfiles:
        match = filename_rx.match(os.path.split(filename)[-1])
        E, c_values = np.genfromtxt(filename, usecols=(0,1), unpack=True)
        n_q_vals, n_c_vals = np.genfromtxt(filename, usecols=(2,3),
                                           dtype=np.int, unpack=True)
        i_extr = arg_first_extr(c_values)
        n_q_extr = n_q_vals[i_extr]
        n_c_extr = n_c_vals[i_extr]
        if match:
            param_set = int(match.group('param_set'))
            detuning  = int(match.group('det'))
            if not entanglement.has_key(param_set):
                entanglement[param_set] = {}
                nc[param_set] = {}
                nq[param_set] = {}
            entanglement[param_set][detuning] = c_values
            nc[param_set][detuning] = n_c_extr
            nq[param_set][detuning] = n_q_extr
        else:
            raise ValueError("filename %s did not match the expected pattern"
                             % filename)
    return E, entanglement, nc, nq


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, *read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
