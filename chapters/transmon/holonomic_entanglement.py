#!/usr/bin/env python
import os
import sys
import numpy as np
from glob import glob
import matplotlib
matplotlib.use('PDF')
from mgplottools.mpl import set_axis, new_figure, get_color, set_color_cycle, ls

def create_figure(outfile, data):
    """
    data is a dict
    run_folder => {
        'E' => array of amplitudes
        'concurrence' => array of concurrences for each value in E,
        'pop_loss' => array of population loss from log subsp (E)
        'nq_vals' => array of number of qubit levels included in prop (E),
        'nc_vals' => array of number of qubit levels included in prop (E)
    }
    """

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    legend_offset   = fig_width-3.9     # Left cv -> legend
    left_margin     = 1.1               # Left cv -> plot area
    right_margin    = 4.1               # plot area -> right cv
    top_margin      = 0.4               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> plot area
    h               = 2.0               # height of each panel
    gap             = 0.0               # gap between panels
    w = fig_width - (left_margin + right_margin)  # width of panel

    n_panels = 2
    panels_total_height = n_panels*h + (n_panels-1)*gap

    fig_height = bottom_margin + n_panels*h + (n_panels-1)*gap + top_margin
    fig = new_figure(fig_width, fig_height)

    E = data[data.keys()[0]]['E'] # pulse amplitude, for all axes

    axes = [] # panels
    # create axes from top to bottom
    for i in xrange(n_panels):
        p_offset = bottom_margin + (n_panels-i-1)*(h+gap)
        pos = [left_margin/fig_width, p_offset/fig_height,
               w/fig_width, h/fig_height]
        ax = fig.add_axes(pos)
        if i == n_panels-1:
            set_axis(ax, 'x', E[0], E[-1], 50, minor=5,
                     label=r'peak pulse amplitude $\epsilon_0$ (MHz)')
        else:
            set_axis(ax, 'x', E[0], E[-1], 50, minor=5, ticklabels=False)
        set_axis(ax, 'y', 0, 1, 0.5, minor=5)
        if i == 0: # top panel
            ax.set_yticklabels(['0', '0.5', '1.0'])
        else:
            ax.set_yticklabels(['0', '0.5', ''])
        axes.append(ax)

    titles = [# title for each panel (top to bottom)
        r'$\omega_c = \SI{6.0}{GHz} < \omega_1, \omega_2$',
        r'$\omega_c = \SI{8.1}{GHz} > \omega_1, \omega_2$',
    ]

    # do the plotting
    for (file, label, color) in (
        ('params1d-60_T200', r'$\omega_d = \omega_c - 60$~MHz', 'blue'),
        ('params1d-40_T200', r'$\omega_d = \omega_c - 40$~MHz', 'orange'),
        ('params1d40_T200',  r'$\omega_d = \omega_c + 40$~MHz', 'red'),
        ('params1d60_T200',  r'$\omega_d = \omega_c + 60$~MHz', 'green')
     ):
        try:
            axes[0].plot(data[file]['E'], data[file]['concurrence'],
                        label=label, color=get_color(color))
        except KeyError:
            pass
    for (file, label, color) in (
        ('params2d-60_T200', r'$\omega_d = \omega_c - 60$~MHz', 'blue'),
        ('params2d-40_T200', r'$\omega_d = \omega_c - 40$~MHz', 'orange'),
        ('params2d40_T200',  r'$\omega_d = \omega_c + 40$~MHz', 'red'),
        ('params2d60_T200',  r'$\omega_d = \omega_c + 60$~MHz', 'green')
     ):
        try:
            axes[1].plot(data[file]['E'], data[file]['concurrence'],
                        label=label, color=get_color(color))
        except KeyError:
            pass

    # label points
    marker_x = (125, 250)
    marker_y = (0.9984, 0.9857)
    marker_text = ("1", "2")
    axes[0].scatter(marker_x,  marker_y, c='black', clip_on=False,
                    edgecolors='none', zorder=10)
    for i, txt in enumerate(marker_text):
            axes[0].annotate(txt, (marker_x[i],marker_y[i]),
                             xytext=(2, 3), textcoords='offset points')
    marker_x = (425,)
    marker_y = (0.9968, )
    marker_text = ("3",)
    axes[1].scatter(marker_x,  marker_y, c='black', clip_on=False,
                    edgecolors='none', zorder=10)
    for i, txt in enumerate(marker_text):
            axes[1].annotate(txt, (marker_x[i],marker_y[i]),
                             xytext=(2, 3), textcoords='offset points')


    # legend
    for i, ax in enumerate(axes):
        p_offset = bottom_margin + (n_panels-i-1)*(h+gap)
        ax.legend(loc='center left', title=titles[i],
                  bbox_to_anchor=(legend_offset/fig_width,
                                 (p_offset + 0.5*h)/fig_height),
                  bbox_transform=fig.transFigure,
                  labelspacing=0.1, fontsize="small",
                  borderpad=0.0, borderaxespad=0.0)

    # y axis label
    fig.text(0, (bottom_margin + 0.5*panels_total_height)/fig_height,
             'concurrence after $T=\SI{200}{ns}$',
             rotation='vertical', ha='left', va='center')

    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(data_folder):
    """
    Return dictionary

    run_folder => {
        'E' => array of amplitudes
        'concurrence' => array of concurrences for each value in E,
        'pop_loss' => array of population loss from log subsp (E)
        'nq_vals' => array of number of qubit levels included in prop (E),
        'nc_vals' => array of number of qubit levels included in prop (E)
    }
    """
    result = {}
    subdirs = [os.path.join(data_folder,o) for o in os.listdir(data_folder)
               if os.path.isdir(os.path.join(data_folder,o))]
    for folder in subdirs:
        foldername = os.path.split(folder)[-1]
        datfile = glob(os.path.join(folder, 'entanglement*.dat'))[0]
        try:
            E, concurrence, pop_loss = np.genfromtxt(datfile, usecols=(0,1,2),
                                                    unpack=True)
            nq_vals, nc_vals = np.genfromtxt(datfile, usecols=(3,4),
                                            dtype=np.int, unpack=True)

            result[foldername] = {
                'E':  E,
                'concurrence':  concurrence,
                'pop_loss':  pop_loss,
                'nq_vals':  nq_vals,
                'nc_vals':  nc_vals
            }
        except ValueError:
            # skip if the data file is empty (run has not finished yet)
            pass
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    data_folder = basename
    create_figure(outfile, read_data(data_folder))

if __name__ == "__main__":
    sys.exit(main())
