#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script for generating a plot of gate error (data included in file)
"""
import os
import sys
import numpy as np
import matplotlib
matplotlib.use('PDF')
from StringIO import StringIO
from mgplottools.mpl import get_color, set_axis, new_figure, ls, \
                            set_color_cycle


def create_figure(outfile, T, E_max, pop_loss, peak_qubit, peak_cavity,
    err_avg_0, err_avg_100, err_avg_25):

    # Layout
    fig_width       = 12.5              # Total canvas (cv) width
    left_margin     = 1.5               # Left cv -> plot area
    right_margin    = 0.4               # plot area -> right cv
    top_margin      = 0.3               # top cv -> plot area
    bottom_margin   = 1.0               # bottom cv -> panel 1
    h_error         = 2.80              # height of each panel 1
    h_peak_c        = 1.25              # height of each panel 2
    h_peak_q        = 1.25              # height of each panel 3
    h_peak_E        = 1.60              # height of each panel 4
    h = h_error + h_peak_c + h_peak_q + h_peak_E # height of total plot area
    w = fig_width - (left_margin + right_margin)  # width of panel
    fig_height = bottom_margin + h + top_margin
    fig = new_figure(fig_width, fig_height)

    set_color_cycle(['blue', 'red', 'orange'])

    # panel 1: gate error
    pos = [left_margin/fig_width, bottom_margin/fig_height,
            w/fig_width, (h_error)/fig_height]
    ax = fig.add_axes(pos)
    ax.plot(T, err_avg_0,   marker='o',
            label=r'$1-F_{\text{avg}}$, no dissipation ')
    ax.plot(T, err_avg_25,  marker='o',
            label=r'$1-F_{\text{avg}}$, $\tau = \SI{25}{\micro\second}$')
    ax.plot(T, err_avg_100, marker='o',
            label=r'$1-F_{\text{avg}}$, $\tau = \SI{100}{\micro\second}$')
    ax.plot(T, pop_loss, color=get_color('black'), label=r'pop. loss',
            marker='*', ls='--')
    set_axis(ax, 'x', 100, 1000, 100, minor=2, range=(75, 1025),
             label='pulse duration (ns)')
    set_axis(ax, 'y', 5.0e-4, 1.0e-0, label='gate error', logscale=True,
             drop_ticklabels=(-2,), label_coords=(-1.0/w,0.5))
    ax.legend(loc=9, ncol=2, bbox_to_anchor=(0.55,0.99), frameon=False,
              prop={'size':8})
    ax.text(0.97,0.9, r'(d)', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')


    # panel 2: peak_cavity
    pos = [left_margin/fig_width, (bottom_margin+h_error)/fig_height,
           w/fig_width, h_peak_c/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'x', 100, 1000, 100, minor=2, range=(75, 1025),
             ticklabels=False)
    peak_c_max = int(max(peak_cavity)*1.3)
    peak_c_major = 5
    if peak_c_max > 20:
        peak_c_major = 10
    set_axis(ax, 'y', 0, peak_c_max, peak_c_major, minor=5,
             label=r'$\langle n \rangle_{\max}$',
             drop_ticklabels=(-1,), label_coords=(-1.0/w,0.5))
    ax.plot(T, peak_cavity, marker='o')
    ax.text(0.97,0.9, r'peak cavity population (c)', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')

    # panel 3: peak_qubit
    pos = [left_margin/fig_width,
           (bottom_margin+h_error+h_peak_c)/fig_height,
           w/fig_width, h_peak_q/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'x', 100, 1000, 100, minor=2, range=(75, 1025),
             ticklabels=False)
    set_axis(ax, 'y', 0, 3.25, 1, minor=2, label=r'$\langle i \rangle_{\max}$',
             drop_ticklabels=(-1,), label_coords=(-1.0/w,0.5))
    ax.plot(T, peak_qubit, marker='o')
    ax.text(0.97,0.9, r'peak qubit population (b)', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')

    # panel 4: peak_pulse amplitude
    pos = [left_margin/fig_width,
           (bottom_margin+h_error+h_peak_c+h_peak_q)/fig_height,
           w/fig_width, h_peak_E/fig_height]
    ax = fig.add_axes(pos)
    set_axis(ax, 'x', 100, 1000, 100, minor=2, range=(75, 1025),
             ticklabels=False)
    set_axis(ax, 'y', 0, 1600, 500, minor=5,
             label=r'$\epsilon_{0}$ (MHz)',
             label_coords=(-1.0/w,0.5))
    ax.plot(T, E_max, marker='o')
    ax.text(0.97,0.9, r'peak pulse amplitude (a)', transform=ax.transAxes,
           horizontalalignment='right', verticalalignment='top')


    # output
    fig.savefig(outfile, format=os.path.splitext(outfile)[1][1:])


def read_data(gate):
    #uk006169@katamon:~/jobs/DissertationTM> cat transmon2013_cphase.dat
    data = {}
    data['CPHASE'] = """
# T [ns] E_max [MHz]                 pop_loss    peak qubit   peak_cavity         1-F_avg(no_diss)   1-F_avg(tau=100micros)    1-F_avg(tau=25micros)
     100      1436.6   7.9805631317856118E-02        1.1744        7.3342   2.8625775910490842E-01   2.8781693601806418E-01   2.9247230359156129E-01
     200      1177.1   2.7089049199828801E-03        2.0116       11.6775   2.7637640092690319E-03   9.9031983717954297E-03   3.1001157091772761E-02
     250       987.3   2.2072854070904761E-03        1.4504       11.7758   2.2389699247071788E-03   8.5763986485041244E-03   2.7326725629151841E-02
#     300       846.7   1.6789961906125361E-02        1.0448       11.7100   2.0586740322626640E-02   2.8413890460260220E-02   5.1473431348428078E-02
# T=300 is outlier: pulse was complex when it should be real -> discard
     400       490.0   9.9447729773305404E-04        1.9717        5.7139   9.9888962386684987E-04   6.4325305178105641E-03   2.2516643077624909E-02
     500       585.9   7.6298879400100716E-03        1.7707       10.0698   7.7305403511620518E-03   1.5275989771788789E-02   3.7481213055643670E-02
     600       550.6   9.7633599027213691E-04        2.0004        4.6567   9.9504849618770042E-04   7.7246971293474243E-03   2.7527990823043580E-02
     700       269.8   2.2841639976982631E-03        1.7414        4.0625   2.3039495447242380E-03   8.5840778585709598E-03   2.7119349368115438E-02
     800       225.1   1.4601331116479430E-03        1.0110        4.0472   1.4726207446995601E-03   8.7539440609741836E-03   3.0188273069494339E-02
     900       346.6   3.7753648150939960E-03        1.6683        7.3124   3.8030142690033131E-03   1.8005026268796520E-02   5.8958380320235482E-02
    1000       176.6   6.8654144226409919E-04        1.0132        3.4877   6.9717037075456290E-04   1.0985217359672511E-02   4.1045586236366782E-02
"""
    data['CNOT'] = """
# T [ns] E_max [MHz]                 pop_loss    peak qubit   peak_cavity         1-F_avg(no_diss)   1-F_avg(tau=100micros)    1-F_avg(tau=25micros)
     100      1101.0   9.2121534170207853E-02        1.6945        7.8345   3.0089369295104118E-01   3.0262608595354462E-01   3.0779604927180648E-01
     200      1082.2   4.3515152435913307E-02        1.8680       26.7518   5.0510782650375903E-02   5.8524348740774390E-02   8.2136978746138789E-02
#    250      1091.7   3.9074667095453366E-03        2.0158       17.8839   4.1639909666575381E-03   1.0489540439466699E-02   2.9209782254739910E-02
# T=250 is outlier: pulse was complex when it should be real -> discard
     300       661.2   1.4304038743124799E-02        1.2475       20.0054   1.5218756650273280E-02   2.5099194653358081E-02   5.4115039073117210E-02
     500       548.7   1.1122135888285149E-03        2.0031        5.0610   1.1557990112959220E-03   6.7827003468948774E-03   2.3422912765435840E-02
    1000       124.3   1.4698286566885430E-03        1.1707        2.9240   1.4960446463501140E-03   1.3148485944880490E-02   4.7226337831756997E-02
"""
    return np.genfromtxt(StringIO(data[gate]), unpack=True)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    basename = os.path.splitext(__file__)[0]
    outfile = basename + '_cphase.pdf'
    create_figure(outfile, *read_data('CPHASE'))
    outfile = basename + '_cnot.pdf'
    create_figure(outfile, *read_data('CNOT'))


if __name__ == "__main__":
    sys.exit(main())

