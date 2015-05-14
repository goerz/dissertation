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
    h_pop          = 2.5     # Height of plot of population dynamics in
                             # the logical subspace (bottom plot) [cm]
    h_exc          = 1.7     # Height of plot of mean population numbers
                             # in the qubits and the cavity (top 3 plots) [cm]
    left_margin    =  1.2    # Left canvas edge -> plot area [cm]
    bottom_margin  =  1.0    # Bottom canvas edge -> plot area [cm]
    right_margin   =  2.0    # Right canvas edge -> plot area [cm]
    top_margin     =  0.5    # Top canvas edge -> plot area [cm]
    legend_gap     =  0.3    # Right canvas edge -> legend [cm]
    pop_top_buffer =  0.66   # extra space in pop plot [cm]
    exc_top_buffer =  0.0    # extra space in exc plot [cm]
    hilbert_space = False
    cavity        = False
    dpi           = 300
    gap           = 0.0 # Not used
    xaxis_minor   = 5
    title         = ''

    fig_height = top_margin + 2.0 * h_exc + h_pop + bottom_margin
    panel_width = fig_width - (left_margin + right_margin)

    fig = new_figure(fig_width, fig_height)
    fig.text(0, 1, '(b)', va='top', ha='left')

    plot = PopPlot(runfolder, hilbert_space, cavity, dpi, left_margin,
                   right_margin, bottom_margin, top_margin, panel_width,
                   gap, legend_gap, h_pop, h_exc, xaxis_minor,
                   pop_top_buffer, exc_top_buffer, title)
    plot.styles['00']['color'] = get_color('red')
    plot.styles['01']['color'] = get_color('blue')
    plot.styles['10']['color'] = get_color('orange')
    plot.styles['11']['color'] = get_color('purple')
    plot.plot(basis_states=('11', ), pops=('00', '01', '10', '11', 'tot' ),
              fig=fig, in_panel_legend=True)

    set_axis(plot.ax['11']['pop'],    'x', 0, 400, 50, minor=5)
    set_axis(plot.ax['11']['q1'],     'x', 0, 400, 50, minor=5)
    set_axis(plot.ax['11']['q2'],     'x', 0, 400, 50, minor=5)
    set_axis(plot.ax['11']['pop'],   'y', 0, 1.0, 0.5, range=(0,1.3),  minor=5)
    set_axis(plot.ax['11']['q1'],    'y', 0, 1.9, 0.5, minor=5)
    set_axis(plot.ax['11']['q2'],    'y', 0, 1.9, 0.5, minor=5)

    # write out
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def main(argv=None):
    """ Main Routine """

    rf = './t3r20101'

    basename = os.path.splitext(__file__)[0]
    outfile = basename + '.pdf'
    create_figure(outfile, rf)

    return(0)


if __name__ == "__main__":
    sys.exit(main())

