#!/usr/bin/env python
import matplotlib
matplotlib.use("PDF")
import os
import sys
from QDYNTransmonLib.popdyn import PopPlot
from mgplottools.mpl import set_axis, new_figure, get_color


def create_figure(outfile, runfolder):
    """ Create plot for the data in the given runfolder

        Arguments:

        outfile    Name of output data file
        runfolder  Folder from which to read data
    """

    fig_width      = 11.0    # Total width of canvas [cm]
    h_pop          = 2.0     # Height of plot of population dynamics in
                             # the logical subspace (bottom plot) [cm]
    h_exc          = 1.5     # Height of plot of mean population numbers
                             # in the qubits and the cavity (top 3 plots) [cm]
    left_margin    =  1.2    # Left canvas edge -> plot area [cm]
    bottom_margin  =  1.0    # Bottom canvas edge -> plot area [cm]
    right_margin   =  2.8    # Right canvas edge -> plot area [cm]
    top_margin     =  0.1    # Top canvas edge -> plot area [cm]
    legend_gap     =  0.3    # Right canvas edge -> legend [cm]
    pop_top_buffer =  0.66   # extra space in pop plot [cm]
    exc_top_buffer =  0.0    # extra space in exc plot [cm]
    hilbert_space = True
    dpi           = 300
    gap           = 0.0 # Not used
    xaxis_minor   = 5
    title         = ''

    fig_height = top_margin + 3.0 * h_exc + h_pop + bottom_margin
    panel_width = fig_width - (left_margin + right_margin)

    fig = new_figure(fig_width, fig_height)

    plot = PopPlot(runfolder, hilbert_space, dpi, left_margin,
                   right_margin, bottom_margin, top_margin, panel_width,
                   gap, legend_gap, h_pop, h_exc, xaxis_minor,
                   pop_top_buffer, exc_top_buffer, title)
    plot.styles['00']['color'] = get_color('red')
    plot.panel_label = {}
    plot.legend_title = {'cavity': 'cavity', 'q1': 'left qubit',
                         'q2': 'right qubit', 'pop': 'log. subspace'}
    plot.plot(basis_states=('00', ), pops=('00', ), fig=fig,
              in_panel_legend=False)

    set_axis(plot.ax['00']['pop'],    'x', 0, 200, 25, minor=5)
    set_axis(plot.ax['00']['q1'],     'x', 0, 200, 25, minor=5)
    set_axis(plot.ax['00']['q2'],     'x', 0, 200, 25, minor=5)
    set_axis(plot.ax['00']['cavity'], 'x', 0, 200, 25, minor=4)
    set_axis(plot.ax['00']['pop'],   'y', 0, 1.0, 0.5, range=(0,1.5),  minor=5)
    set_axis(plot.ax['00']['q1'],    'y', 0, 0.7, 0.2, range=(0,0.85), minor=4)
    set_axis(plot.ax['00']['q2'],    'y', 0, 0.7, 0.2, range=(0,0.85), minor=4)
    set_axis(plot.ax['00']['cavity'],'y', 0, 58,  20,                  minor=4)

    # panel labels
    for (panel, height, label) in [
    ('cavity', h_exc, 'a)'),
    ('q2',     h_exc, 'b)'),
    ('q1',     h_exc, 'c)'),
    ('pop',    h_pop, 'd)')]:
        ax = plot.ax['00'][panel]
        ax.text(0.25/panel_width, (height-0.2)/height, label,
            transform=ax.transAxes, verticalalignment='top',
            horizontalalignment='left')

    # write out
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def main(argv=None):
    """ Main Routine """

    rf = 'holonomic_entanglement/params2d40_T200'

    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, rf)

    return(0)


if __name__ == "__main__":
    sys.exit(main())

