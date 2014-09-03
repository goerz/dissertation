"""
Support module for matplotlib plotting
"""
import matplotlib
import numpy as np
from matplotlib.ticker import AutoMinorLocator, FormatStrFormatter
from GoerzDiss.layout import cm2inch, fontsize

colors = {
"white"        : (255, 255, 255),
"black"        : (0, 0, 0),
"red"          : (228, 26, 28),
"blue"         : (55, 126, 184),
"orange"       : (255, 127, 0),
"green"        : (77, 175, 74),
"purple"       : (152, 78, 163),
"brown"        : (166, 86, 40),
"pink"         : (247, 129, 191),
"yellow"       : (210, 210, 21),
"lightred"     : (251, 154, 153),
"lightblue"    : (166, 206, 227),
"lightorange"  : (253, 191, 111),
"lightgreen"   : (178, 223, 138),
"lightpurple"  : (202, 178, 214),
"grey"         : (153, 153, 153),
}

# line styles
ls = {
    "dashed"           : (4,1.5),
    "long-dashed"      : (8,1),
    "double-dashed"    : (3,1,3,2.5),
    "dash-dotted"      : (5,1,1,1),
    "dot-dot-dashed"   : (1,1,1,1,7,1),
    "dash-dash-dotted" : (4,1,4,1,1,1),
    "dotted"           : (1,1),
    "double-dotted"    : (1,1,1,3),
}


def get_color(name, alpha=0.0, format='web'):
    """
    Return RGBA tuple for given color name
    """
    r, g, b = colors[name.lower()]
    if format == 'web':
        return "#%02x%02x%02x" % (r, g, b)
    if format == 'rgb':
        return (r, g, b)
    elif format == 'rgba':
        return (r, g, b, alpha)

def set_axis(ax, which_axis, start, stop, step, range=None, minor=0,
             format=None, label=None, labelpad=None):
    """
    Format the given axis

    ax: instance of matplotlib.axes.Axes
        Axes in which to set the axis
    which_axis: str
        Either 'x', or 'y'
    start: float
        value for first tick on the axis (and start of axis, unless range is
        given
    stop: float
        value for last tick on the axis ( and stop of axis, unless range is
        given)
    step: float
        step between major ticks
    range: tuple
        The minimum and maximum value of the axis. If not given, [start, stop]
    minor:
        Number of subdivisions of the interval between major ticks; e.g.,
        minor=2 will place a single minor tick midway between major ticks.
    format: str
        Format string to use for tick labels. Will be chosen automatically if
        not given
    label: str
        Axis-label
    labelpad: float
        spacing in points between the label and the axis

    If you want to suppress tick labels, you must do so separately, with e.g.
    ax.set_xticklabels([])
    """
    if which_axis == 'x':
        axis = ax.xaxis
    elif which_axis == 'y':
        axis = ax.yaxis
    else:
        raise ValueError('which_axis must be either "x", or "y"')
    axis.set_ticks(np.arange(float(start),
                   float(stop) + float(step)/2.0,
                   float(step)))
    if format is not None:
        majorFormatter = FormatStrFormatter(format)
        axis.set_major_formatter(majorFormatter)
    if minor > 0:
        minorLocator = AutoMinorLocator(minor)
        axis.set_minor_locator(minorLocator)
    if range is None:
        range = [start, stop]
    if which_axis == 'x':
        ax.set_xlim(range)
        if label is not None:
            ax.set_xlabel(label, labelpad=labelpad)
    elif which_axis == 'y':
        ax.set_ylim(range)
        if label is not None:
            ax.set_ylabel(label, labelpad=labelpad)


def new_figure(fig_width, fig_height, size_in_cm=True, **kwargs):
    """
    Return a new matplotlib figure of the specified size (in cm, or in inch, if
    size_in_cm is False)

    The remaining kwargs are passed to the Figure init routine

    You may use the figure as follows:

    >>> import matplotlib
    >>> matplotlib.use('PDF') # backend ('PDF' for pdf, 'Agg' for png)
    >>> fig = new_figure(10, 4)
    >>> pos = [0.05, 0.05, 0.9, 0.9] # left, bottom offset, width, height
    >>> a = fig.add_axes(pos)
    >>> a.plot(linspace(0, 10, 100), linspace(0, 10, 100))
    >>> fig.savefig('out.pdf', format='pdf')

    """
    from matplotlib.pyplot import figure

    # Set up default colors
    color_cycle = ["red", "blue", "orange", "green", "purple",
    "brown", "pink", "yellow", "lightred", "lightblue", "lightorange",
    "lightgreen", "lightpurple"]
    matplotlib.rc('axes',
                  color_cycle=[get_color(cname) for cname in color_cycle])

    backend = matplotlib.get_backend().lower()
    print "Using backend: ", backend
    print "Using maplotlibrc: ", matplotlib.matplotlib_fname()

    if size_in_cm:
        print "Figure height: ", fig_height, " cm"
        print "Figure width : ", fig_width, " cm"
        return figure(figsize=(fig_width*cm2inch, fig_height*cm2inch),
                      **kwargs)
    else:
        print "Figure height: ", fig_height / cm2inch, " cm"
        print "Figure width : ", fig_width / cm2inch , " cm"
        return figure(figsize=(fig_width, fig_height), **kwargs)

