#!/usr/bin/env python
############################################################################
#    Copyright (C) 2013 by Michael Goerz                                   #
#    http://michaelgoerz.net
#                                                                          #
#    This program is free software; you can redistribute it and/or modify  #
#    it under the terms of the GNU General Public License as published by  #
#    the Free Software Foundation; either version 3 of the License, or     #
#    (at your option) any later version.                                   #
#                                                                          #
#    This program is distributed in the hope that it will be useful,       #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         #
#    GNU General Public License for more details.                          #
#                                                                          #
#    You should have received a copy of the GNU General Public License     #
#    along with this program; if not, write to the                         #
#    Free Software Foundation, Inc.,                                       #
#    59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             #
############################################################################

""" This module provides a thin parser around XMGrace agr files

    It provides the central AgrFile class, which simply stores all the lines
    of an agr file, but in a small tree-like structure that make it easier to
    access the different parts of the file. See the documentation of the
    AgrFile class for more information about the layout of an agr file.
    AgrFile provides methods for editing the different parts of the agr file
    and making common modifications (such as exchanging the data for a plot).

    The module fulfills two purposes:

    1) Assisting in simple scripts that generate xmgrace plots based on an
       existing template (e.g. by replacing the plot data).

    2) Allowing to *interactively* explore an agr file in ipython, to edit its
       various parts, and to make common modifications to the file. To enter
       interactive mode, simply run this module as a script (you may give the
       name of an agr file as a parameter to load that file).

    The module's purpose is *not* to create an agr file from scratch. For this,
    use the pygrace module (http://pygrace.github.io).

    Example interactive usage:

        # load ipython with agr object instantiated
        % ./xmgrace_parser.py plot.agr

        >>> agr.print_summary()
        Canvas size: 29.70 x 20.99 cm
        There are 3 drawing objects in the plot
        There are 5 regions in the plot
        There are 3 graphs in the plot
        Graph 0 [size 18.27 x 7.35 cm at (6.17, 11.54) cm]
            Set G0S0 (xy): 2000 data points
                comment: points_1_1.dat
                legend : f1(x)
            Set G0S1 (xy): 2000 data points
                comment: points_1_2.dat
                legend : f2(x)
        Graph 1 [size 6.05 x 7.35 cm at (6.17, 2.10) cm]
            Set G1S0 (xy): 2000 data points
                comment: points_2_1.dat
                legend : g1(x)
            Set G1S1 (xy): 1901 data points
                comment: points_2_2.dat
                legend : g2(x)
        Graph 2 [size 9.51 x 7.35 cm at (14.94, 2.099028.2) cm]
            Set G2S0 (xy): 2000 data points
                comment: points_3_1.dat

        # open EDITOR with header lines, to allow modifications
        >>> agr.edit_header()

        # read data of dataset G0S0 into numpy arrays
        >>> x, y = agr.get_data(0,0)

        # overwrite data of dataset G0S1
        >>> agr.set_data(0, 1, x, y, comment='new data')

        # overwrite data of dataset G0S0
        >>> agr.set_data(0, 0, filename='new.dat', columns=(0,1), legend='new')

        # change color of G0S0
        >>> g0s0 = agr.get_set(0,0)
        >>> g0s0.update_properties(line_color=2, symbol_color=2)

        # or, using the dictionary interface (less efficient if multiple
        # properties are set)
        >>> g0s0['line_color'] = 2
        >>> g0s0['symbol_color'] = 2

        # switch G0S0 and G0S1
        >>> agr.reorder_sets(0, (1,0))

        # Move down G0 by 1 cm
        >>> agr.set_graph_view(0, x_min=6.14, y_min=10.54,
        ... width=18.27, height=7.35)

        # What font size should I set if the text should be 10pt in the output
        # PDF?
        >>> agr.fontsize(10)
        0.5379011902408587

        # If you prefer to work in inches, you can set the default unit:
        >>> DEFAULT_UNIT = 'inch'

        # You can do some rudimentary conversion between TeX and XmGrace
        # strings (and back with grace2tex):
        >>> tex2grace(r'|\\epsilon_1(t)|')
        |\\xe\\f{}\\s1\\N(t)|

        # write out
        >>> agr.write()

    The above examples are just a small subset of what is possible; please
    explore the module using ipython's interactive capabilities (tab
    completion!)
"""

import re
import logging
from StringIO import StringIO
import sys, tempfile, os
from subprocess import call
import numpy as np
from datetime import datetime
import shutil
from optparse import OptionParser


#logging.basicConfig(filename='debug.log',level=logging.DEBUG)

EDITOR = os.environ.get('EDITOR','vim')
XMGRACE = None # if None, select xmgrace executable from PATH
DEFAULT_UNIT = 'cm'

# TODO: add methods/dictionary interface to other objects
# TODO: test with all agr files I can come across
# TODO: Implement AgrFontDict and AgrPalette structures
# TODO: make pip installable (with script hook)

############################### Main Class ####################################

class AgrFile():
    """ Structured array of lines in an agr file

        An agr file as written by the xmgrace program has the following
        structure:
        1. the project "header" lines, which declare the page layout, fonts,
           colors, default linewidths, etc, ending with the file timestamp.
        2. an array of "drawing objects" (e.g. string annotation). For each
           drawing object, there are several lines specifying the properties of
           that object
        3. an array of regions, again with several lines per region specifying
           its properties
        4. an array of graphs. Each graph has the following structure:
           4a. several lines of graph properties
           4b. an array of "sets", each with a several lines describing the
               properties of that set
        5. an array of datasets. Each dataset contains a small header giving
           the dataset label and type, followed by the raw ascii data contained
           in the dataset. The datasets are in the same order as the
           graphs/sets and are connected by their label: the dataset G0S0 is
           associated with the first set in the first graph. Note that the
           'sets' (4b) describe only the visual appearance of a plot, whereas
           the corresponding dataset contains the actual data.

        See also the section "3.1 General concepts" in the xmgrace user manual

        The attributes of an AgrFile object mirror the above structure
        directly:
        header_lines   : array of strings containing the project header
                         description
        drawing_objects: array of AgrDrawingObject objects, which in turn store
                         the array of strings describing the drawing object in
                         their 'lines' attribute
        regions        : array of AgrRegion objects, which in turn store the
                         array of strings  describing the region in their
                         'lines' attribute
        graphs         : array of AgrGraph objects. Each AgrGraph object stores
                         the graph properties in its 'lines' attribute and also
                         contains the attribute 'sets', which is an array of
                         AgrSet set objects. Each AgrSet object then stores the
                         lines describing the properties of the set in their
                         'lines' attribute
        datasets       : array of AgrDataSet objects, which in turn store the
                         array of strings describing the data in their 'lines'
                         attribute

       Furthermore AgrFile objects have the 'filename' attribute, which keeps
       track of the name of the file from which it was created.

       The string representation of an AgrFile object is the concatenated lines
       that are stored in it, i.e. printing an AgrFile object after it was
       created would print the entire content of the file it was created from.
       The strings in the object can also be accessed as an iterator (`for line
       in agr`)
    """

    _rx_header_start  = re.compile(r'# Grace project file')
    _rx_header_stop   = re.compile(r'@timestamp def')
    _rx_region_start  = re.compile(r'@r(\d+) (on|off)')
    _rx_object_start  = re.compile(r'@with (\w+)')
    _rx_graph_start   = re.compile(r'@g(\d+) (on|off)')
    _rx_dataset_start = re.compile(r'@target G(\d+).S(\d+)')
    _rx_set_label     = re.compile(r'G(\d+)S(\d+)', re.I)
    _rx_page_size     = re.compile(r'@page\s+size\s+(\d+),\s*(\d+)')
    _rx_font_size = re.compile(r""" # any line defining a font size
    (^@ \s* default \s+ char \s+ size \s+)
    (?P<val>.*)
    """, re.X)

    def __init__(self, agr_file, repair=False):
        """ Instantiate a new AgrFile from the given filename

            If 'repair' is given as True, try to fix datasets being in the
            wrong order. You should always check the result of such a repair
            attempt
        """
        self.header_lines    = []  # Array of strings
        self.drawing_objects = []  # Array of AgrDrawingObject objects
        self.regions         = []  # Array of AgrRegion objects
        self.graphs          = []  # Array of AgrGraph objects
        self.datasets        = []  # Array of AgrDataSet objects
        self.filename = agr_file
        self.font_factor     = 1.0 # Scaling of font sizes, relative to "Times"
        self.xmgrace = XMGRACE
        if XMGRACE is None:
            self.xmgrace = which('xmgrace')
        if self.xmgrace is None:
            print >> sys.stdout, "WARNING: xmgrace not availabe"

        self.parse(agr_file, repair)

    def clear(self):
        """ Clear all lines """
        self.header_lines    = []
        self.drawing_objects = []
        self.regions         = []
        self.graphs          = []
        self.datasets        = []

    def __str__(self):
        """ Return the entire agr file as a string """
        lines = []
        lines.extend(self.header_lines)
        lines.extend(map(str, self.drawing_objects))
        lines.extend(map(str, self.regions))
        lines.extend(map(str, self.graphs))
        lines.extend(map(str, self.datasets))
        return ''.join(lines)

    def __iter__(self):
        """ Return iterator for all the lines in the agr file"""
        return StringIO(str(self))

    def _set_timestamp(self):
        """ Update the timestamp to the current time """
        timestamp = datetime.now().strftime("%a %B %d %H:%M:%S %Y")
        for i, line in enumerate(self.header_lines):
            if line.startswith('@timestamp def'):
                self.header_lines[i] = "@timestamp def \"%s\"\n" % timestamp
                return

    def get_size(self, unit='DEFAULT_UNIT'):
        """ Return the canvas/page size as a tuple (width, height) in the given
            unit. Unit may be 'cm', 'mm', 'in', or 'pt'.
        """
        if unit == 'DEFAULT_UNIT': unit = DEFAULT_UNIT
        for i, line in enumerate(self.header_lines):
            match = self._rx_page_size.match(line)
            if match:
                width  = _conv_abs_coord(int(match.group(1)), 'pt', unit)
                height = _conv_abs_coord(int(match.group(2)), 'pt', unit)
                return (width, height)

    def get_graph_view(self, g, unit='DEFAULT_UNIT'):
        """ Return the tuple (x_min, y_min, x_max, y_max) that define the
            position of the graph with index g on the canvas, in the given unit
        """
        if unit == 'DEFAULT_UNIT': unit = DEFAULT_UNIT
        x_min, y_min, x_max, y_max = [float(f) for f in re.split(r'\s*,\s*',
                                     self.graphs[g]['view'])]
        x_min = self.conv_coord(x_min, from_unit='viewport', to_unit=unit)
        y_min = self.conv_coord(y_min, from_unit='viewport', to_unit=unit)
        x_max = self.conv_coord(x_max, from_unit='viewport', to_unit=unit)
        y_max = self.conv_coord(y_max, from_unit='viewport', to_unit=unit)
        return (x_min, y_min, x_max, y_max)

    def print_graph_view(self, g, unit='DEFAULT_UNIT'):
        """ Print the position of the graph with index g on the canvas, in the
            given unit
        """
        if unit == 'DEFAULT_UNIT': unit = DEFAULT_UNIT
        x_min, y_min, x_max, y_max = self.get_graph_view(g, unit)
        print "x_min : %f %s" % (x_min, unit)
        print "y_min : %f %s" % (y_min, unit)
        print "x_max : %f %s" % (x_max, unit)
        print "y_max : %f %s" % (y_max, unit)
        width = x_max - x_min
        height = y_max - y_min
        print "width : %f %s" % (width, unit)
        print "height: %f %s" % (height, unit)

    def set_graph_view(self, g, x_min=None, y_min=None, x_max=None, y_max=None,
    width=None, height=None, unit='DEFAULT_UNIT', move_legend=True,
    silent=False):
        """ Position the graph with index g on the canvas. The horizontal
            position is specified by x_min and x_max, or by x_min or x_max and
            width. The vertical position is specified by y_min and y_max, or by
            y_min or y_max and height. The values must be in the specified
            unit, which can be 'cm', 'mm', 'in', 'pt', or 'viewport'
            ('v', 'vp'). All values are relative to the bottom left corner of
            the canvas.

            If move_legend is true, the legend will be moved with the same
            offset as the lower left corner of the graph.

            The new position of the graph, as well as the offset of the legend,
            is any, will be printed to the screen unless silent is True
        """
        if unit == 'DEFAULT_UNIT': unit = DEFAULT_UNIT
        defined = lambda val: not val is None
        # get current properties of the graph
        old_view_str, old_legend_loctype, old_legend_pos \
        = self.graphs[g].get_properties(['view', 'legend_loctype', 'legend'])
        old_x_min, old_y_min, old_x_max, old_y_max \
        = [float(f) for f in re.split(r'\s*,\s*', old_view_str)]
        # get x_min and x_max, if not given
        if not ((defined(x_min)) and (defined(x_max))):
            if (defined(x_min) and defined(width)):
                x_max = x_min + width
            elif (defined(x_max) and defined(width)) :
                x_min = x_max - width
            else:
                raise ValueError("You must either give x_min and x_max; or "
                "x_min or x_max and width")
        # get y_min and y_max, if not given
        if not ((defined(y_min)) and (defined(y_max))):
            if (defined(y_min) and defined(height)):
                y_max = y_min + height
            elif (defined(y_max) and defined(height)):
                y_min = y_max - height
            else:
                raise ValueError("You must either give y_min and y_max; or "
                "y_min or y_max and height")
        # Convert to viewpoint coordinates
        x_min = self.conv_coord(x_min, from_unit=unit, to_unit='viewport')
        y_min = self.conv_coord(y_min, from_unit=unit, to_unit='viewport')
        x_max = self.conv_coord(x_max, from_unit=unit, to_unit='viewport')
        y_max = self.conv_coord(y_max, from_unit=unit, to_unit='viewport')
        # Set view
        self.graphs[g]['view'] = ", ".join(
        ["%f" % v for v in (x_min, y_min, x_max, y_max)])
        # Print info
        if not silent:
            x_min_u = self.conv_coord(x_min, 'viewport', DEFAULT_UNIT)
            x_max_u = self.conv_coord(x_max, 'viewport', DEFAULT_UNIT)
            y_min_u = self.conv_coord(y_min, 'viewport', DEFAULT_UNIT)
            y_max_u = self.conv_coord(y_max, 'viewport', DEFAULT_UNIT)
            old_x_min_u = self.conv_coord(old_x_min, 'viewport', DEFAULT_UNIT)
            old_x_max_u = self.conv_coord(old_x_max, 'viewport', DEFAULT_UNIT)
            old_y_min_u = self.conv_coord(old_y_min, 'viewport', DEFAULT_UNIT)
            old_y_max_u = self.conv_coord(old_y_max, 'viewport', DEFAULT_UNIT)
            print 'Moved graph to new viewpoint'
            print "x_min : %.2f -> %.2f %s" \
                  % (old_x_min_u, x_min_u, DEFAULT_UNIT)
            print "y_min : %.2f -> %.2f %s" \
                  % (old_y_min_u, y_min_u, DEFAULT_UNIT)
            print "x_max : %.2f -> %.2f %s" \
                  % (old_x_max_u, x_max_u, DEFAULT_UNIT)
            print "y_max : %.2f -> %.2f %s" \
                  % (old_y_max_u, y_max_u, DEFAULT_UNIT)
            width  = x_max - x_min
            height = y_max - y_min
            old_width  = old_x_max - old_x_min
            old_height = old_y_max - old_y_min
            print "width : %.2f -> %.2f %s" \
                  % (old_width, width, DEFAULT_UNIT)
            print "height: %.2f -> %.2f %s" \
                  % (old_height, height, DEFAULT_UNIT)
        # Move legend (if activated)
        if move_legend and old_legend_loctype.strip() == 'view':
            x_offset = x_min - old_x_min
            y_offset = y_min - old_y_min
            old_legend_x, old_legend_y \
            = [float(f) for f in re.split(r'\s*,\s*', old_legend_pos)]
            legend_x = old_legend_x + x_offset
            legend_y = old_legend_y + y_offset
            self.graphs[g]['legend'] = "%f, %f" % (legend_x, legend_y)
            if not silent:
                print "Moved legend by offset %f, %f (%s)" \
                % (self.conv_coord(x_offset, 'viewport', DEFAULT_UNIT),
                   self.conv_coord(y_offset, 'viewport', DEFAULT_UNIT),
                   DEFAULT_UNIT)

    def conv_coord(self, val, from_unit=DEFAULT_UNIT, to_unit='viewport'):
        """ Convert between absolute and relative (viewport) coordiantes
            Both `from_unit` and `to_unit` can be 'cm', 'mm', 'in', 'pt', or
            'viewport'
        """
        if from_unit == to_unit: return val
        if from_unit.startswith('v'): # "viewport" or any abbreviation
            device_size = min(self.get_size(unit=to_unit))
            return val * device_size
        else:
            if to_unit.startswith('v'): # "viewport" or any abbreviation
                device_size = min(self.get_size(unit='pt'))
                return _conv_abs_coord(val, from_unit, 'pt') / device_size
            else:
                return _conv_abs_coord(val, from_unit, to_unit)

    def set_size(self, width, height, unit='DEFAULT_UNIT'):
        """ Set the canvas/page size from the given tuple in the specified
            unit. Unit may be 'cm', 'mm', 'in', or 'pt'.

            Note that the page size is the only thing stored in the agr file.
            All other device properties (such as DPI) are in the
            ~/.grace/gracerc.user config file or a set via command line
            options. Changes to the device properties in the GUI are lost when
            xmgrace exits.
        """
        if unit == 'DEFAULT_UNIT': unit = DEFAULT_UNIT
        if unit == 'cm':
            width  *= 28.346457
            height *= 28.346457
        if unit == 'mm':
            width  *= 2.8346457
            height *= 2.8346457
        elif unit.startswith('in'):
            width  *= 72.0
            height *= 72.0
        for i, line in enumerate(self.header_lines):
            if self._rx_page_size.match(line):
                self.header_lines[i] = "@page size %d, %d\n" \
                                        % (int(width), int(height))
                return

    def fontsize(self, size, from_unit="pt", to_unit=None):
        """ Make a rough conversion between absolute and relative font sizes

            The font sizes in xmgrace are relative to the viewport coordinates,
            i.e. if the canvas size is changed, the xmgrace font sizes have to
            be adjusted to result in the same absolute font size.

            Absolute font sizes are in postscript points (unit 'pt' or 'pp'),
            relative font sizes are in 'agr' or 'grace' units, where 'agr'
            denotes the units used internally in the Grace project file, and
            'grace' denotes the unit used in the graphical user interface. The
            two differ by a factor of 100 (1 agr unit = 100 grace units)

            The number reported is a heuristic value for the "Times" font and
            normal canvas sizes. For other fonts, you may have to set
            self.font_factor; which scales the conversion from absolute to
            relative coordinates.

            The easiest way to verify the actual resulting font sizes in an PDF
            hardcopy of a plot is to use the Python pdfminer package and run
            e.g.

                pdf2txt.py -t xml out.pdf
        """
        # The "device size" defines "1" for viewpoint coordinates: it is either
        # the width or the height of the canvas, whichever is smaller.
        device_size = min(self.get_size(unit='pt'))
        if from_unit == to_unit:
            return size
        if from_unit in ['pt', 'pp']:
            if to_unit is None:
                to_unit = 'agr'
            agr_size  = self.font_factor * size / (device_size * 0.031245)
            if to_unit == 'agr':
                return agr_size
            elif to_unit == 'grace':
                return agr_size * 100
            else:
                logging.error("Unknown to_unit: %s" % to_unit)
                return None
        elif from_unit in ['agr', 'grace']:
            if to_unit is None:
                to_unit = 'pt'
            agr_size  = size
            if from_unit == 'grace':
                agr_size = float(agr_size) / 100.0
            return agr_size * device_size * 0.031245 / self.font_factor
        else:
            logging.error("Unknown from_unit: %s" % from_unit)
            return None

    def print_summary(self):
        """ Print a description of how many graphs / data sets are in the agr
            file
        """
        canvas_width, canvas_height = self.get_size()
        print "Canvas size: %.2f x %.2f %s" \
        % (canvas_width, canvas_height, DEFAULT_UNIT)
        self.check_consistency()
        n_drawing_objects = len(self.drawing_objects)
        if n_drawing_objects == 1:
            print "There is %d drawing object in the plot" % n_drawing_objects
        else:
            print "There are %d drawing objects in the plot" \
            % n_drawing_objects
        n_regions = len(self.regions)
        if n_regions == 1:
            print "There is %d region in the plot" % n_regions
        else:
            print "There are %d regions in the plot" % n_regions
        n_graphs = len(self.graphs)
        if n_graphs == 1:
            print "There is %d graph in the plot" % n_graphs
        else:
            print "There are %d graphs in the plot" % n_graphs
        for i, graph in enumerate(self.graphs):
            x_min, y_min, x_max, y_max = self.get_graph_view(i)
            width = x_max - x_min
            height = y_max - y_min
            n_sets = len(graph.sets)
            if n_sets == 1:
                print "Graph %d [size %.2f x %.2f %s at (%.2f, %f.2) %s]" \
                % (i, width, height, DEFAULT_UNIT, x_min, y_min, DEFAULT_UNIT)
            else:
                print "Graph %d [size %.2f x %.2f %s at (%.2f, %.2f) %s]" \
                % (i, width, height, DEFAULT_UNIT, x_min, y_min, DEFAULT_UNIT)
            for j, set in enumerate(graph.sets):
                print "    Set G%dS%d (%s): %d data points" \
                % (i, j, set._get_type(), self.get_dataset(i,j).get_n_rows())
                comment = set._get_comment()
                if comment is not None and comment != "":
                    print "        comment: %s" % comment
                legend = set._get_legend()
                if legend is not None and legend != "":
                    print "        legend : %s" % legend

    def get_set(self, g, s):
        """ Return the AgrSet instance that matches the given graph and set
            number, raise IndexError if no such set exists.
        """
        return self.graphs[g].sets[s]

    def get_set_by_label(self, label):
        """ Return the AgrSet instance that matches the given label, where
            `label` is a string such as 'G0S1' (non-case-sensitive). Raise a
            ValueError if the label is not in the proper format.
        """
        match = self._rx_set_label.match(label)
        if match:
            g = int(match.group(1))
            s = int(match.group(2))
            return self.get_set(g, s)
        else:
            raise ValueError

    def get_labels(self):
        """ Return a list of set labels of the form 'G0S0' for all available
            sets
        """
        labels = []
        for g, graph in enumerate(self.graphs):
            for s in xrange(len(graph.sets)):
                label = "G%dS%d" % (g, s)
                labels.append(label)
        return labels

    def get_dataset(self, g, s):
        """ Return the AgrDataSet instance that matches the given graph and set
            number, or None if no such dataset can be found
        """
        for dataset in self.datasets:
            if (dataset.get_g_s() == (g, s)):
                return dataset
        return None

    def get_dataset_by_label(self, label):
        """ Return the AgrDataSet instance that matches the given label, where
            `label` is a string such as 'G0S1' (non-case-sensitive). Raise a
            ValueError if the label is not in the proper format.
        """
        match = self._rx_set_label.match(label)
        if match:
            g = int(match.group(1))
            s = int(match.group(2))
            return self.get_dataset(g, s)
        else:
            raise ValueError

    def check_consistency(self):
        """ Check that for each set there is a matching dataset (with matching
            type) and vice versa, and that the datasets are in consecutive
            order.

            Throw a AgrInconsistencyError if the check fails
        """
        expected_datasets = []
        expected_types = []
        for g, graph in enumerate(self.graphs):
            for s, set in enumerate(graph.sets):
                expected_datasets.append((g, s))
                expected_types.append(set._get_type())
        expected_datasets.reverse() # so that we can pop
        expected_types.reverse()
        try:
            for dataset in self.datasets:
                expected_g_s = expected_datasets.pop()
                expected_type = expected_types.pop()
                if dataset.get_g_s() != expected_g_s:
                    raise AgrInconsistencyError("datasets are in the wrong "
                    "order")
                if dataset.get_type() != expected_type:
                    raise AgrInconsistencyError("datasets have the wrong type")
        except IndexError:
            raise AgrInconsistencyError("There are extra datasets")
        if len(expected_datasets) != 0:
            raise AgrInconsistencyError("There are missing datasets")

    def reorder_sets(self, g, new_order):
        """ Rearrange the sets within the graph `g` to the order given in
            the tuple `new_order`. E.g. if graph 0 has 3 sets, you could use
            `new_order = (1,0,2)` to switch the first two sets. Visually, this
            results only in the order of the plots in the graph legend.

            The datasets will be rearranged appropriately to reflect the new
            order.
        """
        logging.debug("rearranging datasets for graph %d", g)
        # check new_order: new_order must be a permutation of indices
        if not ( (min(new_order) == 0) and (max(new_order) == len(new_order)-1)
                and len(new_order) == len(self.graphs[g].sets)):
            raise ValueError("new_order must be a permutation of indices of "
            "self.graphs[g].sets")

        # determine offset of in self.datasets where datasets belonging to the
        # graph g start
        offset = 0
        for gg, graph in enumerate(self.graphs):
            if gg < g:
                offset += len(graph.sets)
            else:
                break
        logging.debug("datasets offset %d", offset)

        # build new_order array for datasets
        dataset_new_order = []
        j = 0
        for i in xrange(len(self.datasets)):
            dataset_new_order.append(i)
            if i >= offset:
                if j < len(new_order):
                    dataset_new_order[-1] = new_order[j] + offset
                    j += 1
        logging.debug("datasets new order %s", str(dataset_new_order))

        # reorder sets in graph
        self.graphs[g].sets = [self.graphs[g].sets[i] for i in new_order]
        self._re_number()

        # reorder actual datasets
        self.datasets = [self.datasets[i] for i in dataset_new_order]

        self._re_number()

    def move_set(self, g_old, s, g_new):
        """ Move the set `s` from graph number `g_old` to graph number `g_new`.
            Raise IndexError if any non-existing graphs/sets are given. The set
            will be appended as a new set to the `g_new` graph.

            The datasets will be rearranged appropriately to reflect the move.
        """

        # move the set properties
        graph_set = self.graphs[g_old].sets[s]
        self.graphs[g_new].sets.append(graph_set)
        del(self.graphs[g_old].sets[s])

        # find the actual dataset ...
        dataset = None
        i_dataset = -1
        for i, ds in enumerate(self.datasets):
            if ds.get_g_s() == (g_old, s):
                dataset = ds
                i_dataset = i
                break
        # ... and move it
        del self.datasets[i_dataset]
        insert_pos = 0
        for i, ds in enumerate(self.datasets):
            g = ds.get_g_s()[0]
            if g == g_new:
                insert_pos = i + 1
            if g > g_new:
                break
        if insert_pos < len(self.datasets):
            self.datasets.insert(insert_pos, dataset)
        else:
            self.datasets.append(dataset)

        self._re_number()

    def kill_set(self, g, s):
        """ Remove the specifed set from the specified graph, along with the
            corresponding dataset
        """
        del self.graphs[g].sets[s]
        dataset_to_delete = 0
        for i, dataset in enumerate(self.datasets):
            if (dataset.get_g_s() == (g, s)):
                dataset_to_delete = i
                break
        del self.datasets[dataset_to_delete]
        self._re_number()

    def kill_graph(self, g):
        """ Remove the specified graph, along with all corresponding datasets
        """
        del self.graphs[g]
        new_datasets = []
        for i, dataset in enumerate(self.datasets):
            if (dataset.get_g_s()[0] != g):
                new_datasets.append(dataset)
        self.datasets = new_datasets
        self._re_number()

    def _re_number(self):
        """ Fix the numbering of all graphs and sets, and datasets.
            This routine should be called after reordering any sets. Of course,
            everything must be in the intended order before calling it.
            Specifically, the datasets must have been reordered along with the
            sets.
        """
        new_dataset_indices = []
        for g, graph in enumerate(self.graphs):
            graph._force_index(g)
            for s, graph_set in enumerate(graph.sets):
                graph_set._force_index(s)
                new_dataset_indices.append((g,s))
        for i, dataset in enumerate(self.datasets):
            dataset._force_index(*new_dataset_indices[i])

    def _linelog(self, line_nr, attr, sub_attr=None):
        """ Note in the debug log that line has been added to the array
            self.{attr}, or self.{attr}.{sub_attr}
        """
        if sub_attr is None:
            logging.debug("line %d -> %s[%d]", line_nr, attr,
                          len(self.__dict__[attr])-1)
        else:
            logging.debug("line %d -> %s[%d].%s[%d]", line_nr, attr,
                          len(self.__dict__[attr])-1, sub_attr,
                          len(self.__dict__[attr][-1].__dict__[sub_attr])-1)

    def get_data(self, g, s):
        """ Return a numpy array for each data column in the set `s` in
            graph `g`
        """
        return self.get_dataset(g,s).get_data()

    def set_data(self, g, s, *numpy_arrays, **kwargs):
        """ Overwrite the dataset described by set `s` in graph `g`.

            You may give one numpy array per column as a positional argument,
            or load data from file using the keyword arguments `filename` and
            `columns`, where `columns` is a tuple of integers indicating which
            columns from the file should be used.

            The routine handles the following keyword arguments:
            filename: name of file from which to read the data
            columns : columns in filename from which to read the data
            fmt     : format string for the dataset (cf AgrDataSet `set_data`
                      routine). If not given, defaults to '%10g'.

            All other keyword arguments are passed to the update_properties
            method of the set `s` in graph `g`. One example for a possible
            usage would be to supply a new legend and/or comment.
            If the filename keyword argument is present, put its value
            (along with informations about columns if available) in the set
            comment, unless a comment is set explicitly with a comment keyword
            argument.
        """

        # extract format
        fmt = '%10g'
        if 'fmt' in kwargs:
            fmt = kwargs['fmt']
            del kwargs['fmt']

        # create a new comment if loading from file
        if not 'comment' in kwargs:
            if 'filename' in kwargs:
                comment = kwargs['filename']
                if 'columns' in kwargs:
                    comment += ", columns %s" % str(kwargs['columns'])
                kwargs['comment'] = comment

        # collect data
        if len(numpy_arrays) > 0:
            data = numpy_arrays
            if ('filename' in kwargs) or ('columns' in kwargs):
                raise TypeError("You must not give the 'filename' or "
                "'columns' keywords if you give numpy arrays as positional "
                "arguments")
        else: # load data from file
            if 'filename' in kwargs:
                filename = kwargs['filename']
                del kwargs['filename']
                if 'columns' in kwargs:
                    columns = kwargs['columns']
                    del kwargs['columns']
                    data = np.genfromtxt(filename, usecols=columns,
                                         unpack=True)
                else:
                    data = np.genfromtxt(filename, unpack=True)
            else:
                raise TypeError("You must give the 'filename' keyword "
                "if you do not give numpy arrays as positional "
                "arguments")

        # update set properties
        self.graphs[g].sets[s].update_properties(**kwargs)

        # update dataset
        if 'type' in kwargs:
            self.get_dataset(g,s).set_type(kwargs['type'], check_columns=False)
        self.get_dataset(g,s).set_data(*data, fmt=fmt)

    def view(self):
        """ Write out the current data to a temporary file, and view it in
            xmgrace for interactive manipulation. Any changes saved from
            xmgrace will replace the current data.
        """
        assert self.xmgrace is not None, "xmgrace executable not found"
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(str(self))
            tmpfile.flush()
            call([self.xmgrace, tmpfile.name])
        filename = self.filename
        self.parse(tmpfile.name)
        self.filename = filename
        os.unlink(tmpfile.name)

    def hardcopy(self, filename, device=None, dpi=300, write_batch=None,
    **kwargs):
        """ Create a hardcopy for the current plot.

            Arguments:
            filename    : Name of file to which to write the hardcopy
            device      : Output device. Available devices are printed by
                          `xmgrace -version`. If no device is given, it is
                          determined from the extension of `filename`
            dpi         : Output resolution
            write_batch : If given, name of batchfile that is to be written.
                          Using the batchfile with xmgrace directly will then
                          allow to produce a hardcopy directly

            In addition to the above arguments, device-specific settings can be
            given as keyword arguments, see Section 7.3 "Device-specific
            settings" in the Grace User Manual. Settings that do not take
            arguments should be passed True (e.g. grayscale=True).
        """
        assert self.xmgrace is not None, "xmgrace executable not found"
        extension = os.path.splitext(filename)[1][1:]
        if device is None:
            select_device = {
             'ps': 'PostScript', 'eps':'EPS', 'pdf':'PDF', 'jpg':'JPEG',
             'png':'PNG'
            }
            try:
                device = select_device[extension]
            except KeyError:
                logging.error("Could not determine output device")
                return
        with tempfile.NamedTemporaryFile(suffix=".cmd", delete=False) \
        as batchfile:
            if write_batch is not None:
                command = [self.xmgrace, '-hardcopy', '-nosafe',
                           '-hdevice', device, '-printfile', filename,
                           '-batch', write_batch, self.filename]
                batchfile.write("# %s\n" % " ".join(command))
            batchfile.write("DEVICE \"%s\" DPI %d\n" % (device, dpi))
            batchfile.write("DEVICE \"%s\" FONT ANTIALIASING on\n" % device)
            batchfile.write("PAGE SIZE %d, %d\n" % self.get_size(unit='pt'))
            for key in kwargs:
                if isinstance(kwargs[key], bool):
                    batchfile.write("DEVICE \"%s\" OP \"%s\"\n"
                                    % (device, key))
                else:
                    batchfile.write("DEVICE \"%s\" OP \"%s:%s\"\n"
                                    % (device, key, kwargs[key]))
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(str(self))
            tmpfile.flush()
            command = [self.xmgrace, '-hardcopy', '-nosafe',
                       '-hdevice', device, '-printfile', filename,
                       '-batch', batchfile.name, tmpfile.name]
            print " ".join(command)
            call(command)
            print "Written hardcopy to %s" % filename
        if write_batch is not None:
            shutil.copy(batchfile.name, write_batch)
        os.unlink(batchfile.name)
        os.unlink(tmpfile.name)

    def edit_header(self):
        """ Load header_lines in EDITOR for editing"""
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.header_lines))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.header_lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                self.header_lines.append(line)
        os.unlink(tmpfile.name)

    def edit_drawing_object(self, index):
        """ Load drawing object with the given index in EDITOR for editing """
        self.drawing_objects[index].edit_lines()

    def edit_drawing_objects(self):
        """ Load all drawing object in EDITOR for editing """
        lines_to_edit = map(str, self.drawing_objects)
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(lines_to_edit))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        edited_lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                edited_lines.append(line)
        os.unlink(tmpfile.name)
        # write out everything to a temporary agr file, replacing the drawing
        # objects with the edited_lines, then read in the file again
        filename = self.filename
        lines = []
        lines.extend(self.header_lines)
        lines.extend(edited_lines)
        lines.extend(map(str, self.regions))
        lines.extend(map(str, self.graphs))
        lines.extend(map(str, self.datasets))
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(lines))
        self.parse(tmpfile.name)
        self.filename = filename
        os.unlink(tmpfile.name)

    def edit_region(self, index):
        """ Load region with the given index in EDITOR for editing """
        self.regions[index].edit_lines()

    def edit_graph(self, g, with_sets=True):
        """ Load properties for graph g in EDITOR for editing. If with_sets is
            True, also include the properties of all sets belonging to the
            graph.
        """
        if with_sets:
            lines_to_edit = self.graphs[g].lines
            lines_to_edit.extend(map(str, self.graphs[g].sets))
            with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
            as tmpfile:
                tmpfile.write(''.join(lines_to_edit))
                tmpfile.flush()
                call([EDITOR, tmpfile.name])
            edited_lines = []
            with open(tmpfile.name) as fh:
                for line in fh:
                    edited_lines.append(line)
            os.unlink(tmpfile.name)
            # write out everything to a temporary agr file, replacing the graph
            # with the edited_lines, then read in the file again
            filename = self.filename
            lines = []
            lines.extend(self.header_lines)
            lines.extend(map(str, self.drawing_objects))
            lines.extend(map(str, self.regions))
            for i, graph in enumerate(self.graphs):
                if i == g:
                    lines.extend(edited_lines)
                else:
                    lines.append(str(graph))
            lines.extend(map(str, self.datasets))
            with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
            as tmpfile:
                tmpfile.write(''.join(lines))
            self.parse(tmpfile.name)
            self.filename = filename
            os.unlink(tmpfile.name)
        else:
            self.graphs[g].edit_lines()

    def edit_set(self, g, s):
        """ Load properties for set s in graph g in EDITOR for editing """
        self.graphs[g].edit_set(s)

    def edit_dataset(self, g, s):
        """ Load data for dataset s of graph g in EDITOR for editing
            (i.e. dataset G{g}S{s} for the agr file)
        """
        for dataset in self.datasets:
            if dataset.get_g_s() == (g, s):
                dataset.edit_data()
                break

    def parse(self, agr_file, repair=False):
        """ Load the given agr_file. This completely overwrites any previous
            data.

            If repair is given as True, try to renumber datasets if necessary.
        """
        self.clear()
        logging.debug("* Parsing %s", agr_file)
        self.filename = agr_file
        state = "opened"
        line_nr = 0
        with open(agr_file, 'r') as fh:
            for line in fh:
                line_nr += 1
                if line == "":
                    continue # just skip blank lines
                if (state == "opened"):
                    self.header_lines.append(line)
                    self._linelog(line_nr, 'header_lines')
                    if self._rx_header_start.match(line):
                        state = "in_header"
                elif (state == "in_header"):
                    self.header_lines.append(line)
                    self._linelog(line_nr, 'header_lines')
                    if self._rx_header_stop.match(line):
                        state = "in_drawing_objects"
                elif (state == "in_drawing_objects"):
                    # the drawing_options may be ended by the start of a region
                    if self._rx_region_start.match(line):
                        state = "in_regions"
                        self.regions.append(AgrRegion())
                        self.regions[-1].lines.append(line)
                        self._linelog(line_nr, 'regions', 'lines')
                    # ... or by the start of a graph
                    elif self._rx_graph_start.match(line):
                        state = "in_graphs"
                        logging.debug("line %i -> new graph %d",
                                      line_nr, len(self.graphs))
                        self.graphs.append(AgrGraph(line))
                    else: # a proper drawing_objects line
                        if self._rx_object_start.match(line):
                            self.drawing_objects.append(AgrDrawingObject())
                        self.drawing_objects[-1].lines.append(line)
                        self._linelog(line_nr, 'drawing_objects', 'lines')
                elif (state == "in_regions"):
                    # the regions may be ended by the start of a graph
                    if self._rx_graph_start.match(line):
                        state = "in_graphs"
                        logging.debug("line %i -> new graph %d", line_nr,
                                      len(self.graphs))
                        self.graphs.append(AgrGraph(line))
                    else: # a proper region line
                        if self._rx_region_start.match(line):
                            self.regions.append(AgrRegion())
                        self.regions[-1].lines.append(line)
                        self._linelog(line_nr, 'regions', 'lines')
                elif (state == "in_graphs"):
                    # the graphs may be ended by the start of a dataset
                    if self._rx_dataset_start.match(line):
                        state = "in_datasets"
                        self.datasets.append(AgrDataSet())
                        self.datasets[-1].lines.append(line)
                        self._linelog(line_nr, 'datasets', 'lines')
                    elif self._rx_graph_start.match(line):
                        logging.debug("line %i -> new graph %d", line_nr,
                                      len(self.graphs))
                        self.graphs.append(AgrGraph(line))
                    else: # a proper graph line
                        self._linelog(line_nr, 'graphs')
                        try:
                            self.graphs[-1]._parse_line(line)
                        except AgrParserError:
                            logging.error("Could not parse line %d of %s",
                                          line_nr, agr_file)
                            raise
                elif (state == "in_datasets"):
                    if self._rx_dataset_start.match(line):
                        self.datasets.append(AgrDataSet())
                    self.datasets[-1].lines.append(line)
                    self._linelog(line_nr, 'datasets', 'lines')
                else:
                    msg = "Could not parse line %d of %s" % (line_nr, agr_file)
                    logging.error(msg)
                    raise AgrParserError(msg)
        logging.debug("Done Parsing %s", agr_file)
        if state == 'opened':
            raise AgrParserError("The file is missing the "
            "'Grace project file' header.")
        if repair:
            self.datasets.sort(key = lambda dataset: str(dataset.get_g_s()))
            self._re_number()
        self.check_consistency()

    def write(self, agr_file=None, overwrite=False, consistency_check=True):
        """ Write out the current data to the given `agr_file`, or to the
            original agr file (`filename` attribute), if no `agr_file`
            parameter is given. The timestamp in the file will be updated.

            If the file already exists, you will be asked if you want to
            overwrite it, unless `overwrite` is given as True.

            If you want to write the file without doing a consistency check,
            pass `consistency_check` as False
        """
        if consistency_check:
            self.check_consistency()
        self._set_timestamp()
        out_file = None
        if agr_file is not None:
            out_file = agr_file
        else:
            if self.filename is not None:
                out_file = self.filename

        if not overwrite:
            if os.path.exists(out_file):
                msg = "%s exists. Do you want to overwrite? yes/[no]: " \
                      % out_file
                answer = raw_input(msg)
                if answer == "yes":
                    overwrite = True
            else:
                overwrite = True

        if out_file is None:
            raise ValueError("No output file given")

        if overwrite:
            with open(out_file, 'w') as fh:
                fh.write(str(self))
            print "Written to %s" % out_file
        else:
            print "Nothing written"

    def scale_font(self, factor):
        """ Scale all font sizes by the given factor """
        for i, line in enumerate(self.header_lines):
            match = self._rx_font_size.match(line)
            if match:
                value = float(match.group("val"))
                value *= factor
                line = "%s%f" % (match.group(1), value)
                self.header_lines[i] = line + "\n"
        for drawing_object in self.drawing_objects:
            drawing_object.scale_font(factor)
        for graph in self.graphs:
            graph.scale_font(factor)

    def set_fontsize(self, size, unit='pt'):
        """ Set the font size of all strings. The value of size in in the given
            unit ('pt', 'agr', or 'grace', as understood by the fontsize method
        """
        value = self.fontsize(size, unit)
        for i, line in enumerate(self.header_lines):
            match = self._rx_font_size.match(line)
            if match:
                line = "%s%f" % (match.group(1), value)
                self.header_lines[i] = line + "\n"
        for drawing_object in self.drawing_objects:
            drawing_object.set_fontsize(value)
        for graph in self.graphs:
            graph.set_fontsize(value)

    def merge(self, agr_file, merge_drawing_objects=False):
        """ Load the graphs and associated data from the given agr_file into
            the current canvas. The current header remains unaffected.

            If merge_drawing_objects is True, also that drawing objects from
            the given agr_file will be imported.
        """
        if (isinstance(agr_file, str)):
            other = AgrFile(agr_file)
        elif (isinstance(agr_file, AgrFile)):
            other = agr_file
        else:
            raise ValueError("agr_file must be either string or AgrFile "
                             "instance")
        self.graphs   += other.graphs
        self.datasets += other.datasets
        if merge_drawing_objects:
            self.drawing_objects += other.drawing_objects
        self._re_number()

################## Auxiliary classes (substructures) ##########################


class AgrDrawingObject():
    """ Array of lines from the agr file representing a single "Drawing Object",
        e.g. a string label (stored in the lines attribute)
    """

    _rx_font_size  = re.compile(r'(^@\s+string\s+char\s+size\s+)(?P<val>.*)$')

    def __init__(self):
        """ Create a new instance, without any lines """
        self.lines = []

    def __str__(self):
        """ Return the multi-line string (partial agr file) for the drawing
            object
        """
        return ''.join(self.lines)

    def edit_lines(self):
        """ Load lines in EDITOR for editing"""
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.lines))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                self.lines.append(line)
        os.unlink(tmpfile.name)

    def scale_font(self, factor):
        """ Scale all font sizes by the given factor """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                value = float(match.group("val"))
                value *= factor
                line = "%s%f" % (match.group(1), value)
                self.lines[i] = line + "\n"

    def set_fontsize(self, size):
        """ Set the font size of all strings. The value of size in in 'agr'
            units.
        """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                line = "%s%f" % (match.group(1), size)
                self.lines[i] = line + "\n"


class AgrRegion():
    """ Array of lines from the agr file representing a single xmgrace region
        (stored in the lines attribute)
    """

    def __init__(self):
        """ Create a new instance, without any lines """
        self.lines = []

    def __str__(self):
        """ Return the multi-line string (partial agr file) for the region
        """
        return ''.join(self.lines)

    def edit_lines(self):
        """ Load lines in EDITOR for editing"""
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.lines))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                self.lines.append(line)
        os.unlink(tmpfile.name)


class AgrGraph():
    """ Structured array of lines from the agr file describing a single graph.

        The lines describing the graph are split in the graph properties,
        and an array of sets appearing in the graph.

        attributes:
        lines : array of lines describing the graph properties
        sets  : array of AgrSet objects, which in turn store the lines
                describing each set that is part of the graph

        The class provides a minimum dictionary interface to the properties.
        They keys for all available properties are given by the `keys` method.
        Note that when getting/setting multiple properties at the same time, it
        is more efficient to use the `get_properties` and `update_properties`
        methods.
    """

    # regexes for parsing
    _rx_set_start      = re.compile(r'@\s*s(\d+) hidden')
    # regexes for property lines
    _rx_fixed_point_format  = re.compile(r""" # 'fixedpoint format' regex
    ^ # regex matches e.g. '@g0 fixedpoint format general general'
    (?P<pre> @(g\d+)?\s+)               # '@g0 '
    (?P<kwd> fixedpoint\s+format)       # 'fixedpoint format'
    (?P<sep> \s+)                       # ' '
    (?P<val> [a-zA-Z]+(\s+[a-zA-Z]+)+)  # 'false'
    $""", re.X)
    _rx_on_off_line  = re.compile(r""" # 'on/off' regex
    ^ # regex matches '@    legend on' or '@    legend off'
    (?P<pre> @(g\d+)?\s+) # '@    '
    (?P<kwd> [\w\s]+\w    # 'legend on'
    (?P<sep> \s+)         # ' '
    (?P<val> (on|off)))   # 'on'
    $""", re.X)
    _rx_lit_line  = re.compile(r""" # 'literal' regex
    ^ # regex matches e.g.'@g0 stacked false' or '@    xaxes scale Normal'
    (?P<pre> @(g\d+)?\s+)  # '@g0 '
    (?P<kwd> [\w\s]+\w)    # 'stacked'
    (?P<sep> \s+)          # ' '
    (?P<val> [a-zA-Z]+)    # 'false'
    $""", re.X)
    _rx_str_line  = re.compile(r""" # 'string' regex
    ^ # regex matches e.g. '@    xaxis  ticklabel formula ""'
    (?P<pre> @(g\d+)?\s+)  # '@    '
    (?P<kwd> [\w\s]+\w)    # 'xaxis  ticklabel formula'
    (?P<sep> \s+)          # ''
    (?P<val> ".*")         # '""'
    $""", re.X)
    _rx_pnt_line  = re.compile(r""" # 'point' regex (2 or more values)
    ^ # regex matches e.g. '@    xaxis  ticklabel offset 0.000000 , 0.000000'
      # or '@    view 0.129412, 0.550000, 1.164706, 0.900000'
    (?P<pre> @(g\d+)?\s+)                    # '@    '
    (?P<kwd> [\w\s]+\w)                      # 'xaxis  ticklabel offset'
    (?P<sep> \s+)                            # ' '
    (?P<val> (\s*[\d.+-]+\s*,)+\s*[\d.+-]+)  # '0.000000 , 0.000000'
    $""", re.X)
    _rx_num_line  = re.compile(r""" # 'numeral' regex
    ^ # regex matches e.g. '@g0 bar hgap 0.000000'
    (?P<pre> @(g\d+)?\s+)  # '@g0 '
    (?P<kwd> [\w\s]+\w)    # 'bar hgap'
    (?P<sep> \s+)          # ' '
    (?P<val> [\d.+-]+)     # '0.000000'
    $""", re.X)
    _rx_font_size = re.compile(r""" # any line defining a font size
    (^@\s+
     ( (sub)?title \s+ size |
       (x|y)axis \s+ (tick)?label \s+ char \s+ size |
       legend \s+ char \s+ size
     ) \s+
    )
    (?P<val>.*)
    """, re.X)

    def __init__(self, first_line):
        """ Create a new instance, based on the given `first_line` """
        self.lines = [] # Array of strings (only graph properties, no sets!)
        self.sets  = [] # Array of AgrSet objects
        self._state = "in_properties"
        self.lines.append(first_line)
        self._linelog('lines')

    def __str__(self):
        """ Return the multi-line string (partial agr file) for the entire
            graph, including the properties of all its data sets
        """
        lines = []
        lines.extend(self.lines)
        lines.extend(map(str, self.sets))
        return ''.join(lines)

    def _linelog(self, attr, sub_attr=None):
        """ Note in the debug log that line has been added to the array
            self.{attr}, or self.{attr}.{sub_attr}
        """
        if sub_attr is None:
            logging.debug("  line -> %s[%d]", attr, len(self.__dict__[attr])-1)
        else:
            logging.debug("  line -> %s[%d].%s[%d]", attr,
                          len(self.__dict__[attr])-1, sub_attr,
                          len(self.__dict__[attr][-1].__dict__[sub_attr])-1)

    def edit_lines(self):
        """ Load lines in EDITOR for editing (remember that the lines to not
            include any of the sets; just the general graph properties)
        """
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.lines))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                self.lines.append(line)
        os.unlink(tmpfile.name)

    def edit_set(self, s):
        """ Load set properties for set s in EDITOR for editing """
        self.sets[s].edit_lines()

    def _force_index(self, g):
        """ Change the graph index number in self.lines to `g`
        """
        rx_graph_line = re.compile(r'@g(\d+) (.*)')
        rx_with_line  = re.compile(r'@with g(\d+)')
        for i, line in enumerate(self.lines):
            match = rx_graph_line.match(line)
            if match:
                self.lines[i] = "@g%d %s\n" % (g, match.group(2))
            else:
                match = rx_with_line.match(line)
                if match:
                    self.lines[i] = "@with g%d\n" % g
                    # after the 'with' line, there's nothing else to replace
                    break

    def _parse_line(self, line):
        """ Parse a graph line, append to `lines` attribute to delegate to
            AgrSet object (`sets` array)
        """
        if self._state == "in_properties":
            if self._rx_set_start.match(line):
                self.sets.append(AgrSet())
                self.sets[-1].lines.append(line)
                self._linelog('sets', 'lines')
                self._state = "in_sets"
            else:
                self.lines.append(line)
                self._linelog('lines')
        elif self._state == "in_sets":
            if self._rx_set_start.match(line):
                self.sets.append(AgrSet())
            self.sets[-1].lines.append(line)
            self._linelog('sets', 'lines')
        else:
            raise AgrParserError("Could not parse graph line")

    def __getitem__(self, key):
        """ Look up a property """
        return self.get_properties([key])[0]

    def __setitem__(self, key, value):
        """ Set a property """
        self.update_properties(**{key: value})

    def __iter__(self):
        """ Iterator (not implemented) """
        raise NotImplementedError

    def __delitem__(self, key):
        """ Dictionary deletion (not implemented) """
        raise NotImplementedError


    def get_properties(self, properties):
        """ Given list of graph property names, return an list of their values
            (as strings)
        """
        regexes = [self._rx_fixed_point_format, self._rx_on_off_line,
                   self._rx_lit_line, self._rx_str_line, self._rx_pnt_line,
                   self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            return _get_properties_in_lines(self.lines, regexes, properties)
        except TypeError:
            raise
        except KeyError:
            raise

    def update_properties(self, **kwargs):
        """ Replace graph properties according to the given keyword arguments.

            E.g. we can change '@    title color 1' -> '@    title color 2'
            by calling `update_properties(title_color=2)`. In general, the
            allowed keys are those returned by the keys method.

            If keyword arguments are supplied that don't have a matching
            property in the set, a TypeError is raised.
        """
        logging.debug("* Update Set properties")
        regexes = [self._rx_fixed_point_format, self._rx_on_off_line,
                   self._rx_lit_line, self._rx_str_line, self._rx_pnt_line,
                   self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            _update_properties_in_lines(self.lines, regexes, **kwargs)
        except TypeError:
            raise

    def keys(self):
        """ Return the array of available graph properties """
        regexes = [self._rx_fixed_point_format, self._rx_on_off_line,
                   self._rx_lit_line, self._rx_str_line, self._rx_pnt_line,
                   self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            return _keys_in_lines(self.lines, regexes)
        except TypeError:
            raise

    def scale_font(self, factor):
        """ Scale all font sizes by the given factor """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                value = float(match.group("val"))
                value *= factor
                line = "%s%f" % (match.group(1), value)
                self.lines[i] = line + "\n"
        for set in self.sets:
            set.scale_font(factor)

    def set_fontsize(self, size):
        """ Set the font size of all strings. The value of size in in 'agr'
            units.
        """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                line = "%s%f" % (match.group(1), size)
                self.lines[i] = line + "\n"
        for set in self.sets:
            set.set_fontsize(size)


class AgrSet():
    """ Array of lines from the agr file representing the properties (i.e. not
        the actual data) of a dataset in a graph (stored in the lines
        attribute)

        The class provides a minimum dictionary interface to the properties.
        They keys for all available properties are given by the `keys` method.
        Note that when getting/setting multiple properties at the same time, it
        is more efficient to use the `get_properties` and `update_properties`
        methods.
    """

    # regexes for getters of specific property lines
    _rx_type      = re.compile(r'@\s*s\d+\s+type\s+(\w+)$')
    _rx_comment   = re.compile(r'@\s*s\d+\s+comment\s+"(.*)"$')
    _rx_legend    = re.compile(r'@\s*s\d+\s+legend\s+"(.*)"$')
    # regexes for general property lines
    _rx_on_off_line  = re.compile(r""" # 'on/off' regex
    ^ # regex matches e.g. '@    s0 errorbar on'
    (?P<pre> @\s*s\d+\s+)  # '@    s0 '
    (?P<kwd> [\w\s]+\w    # 'errorbar on'
    (?P<sep> \s+)         # ' '
    (?P<val> (on|off)))   # 'on'
    $""", re.X)
    _rx_lit_line  = re.compile(r""" # 'literal' regex
    ^ # regex matches e.g.'@    s0 errorbar place both'
    (?P<pre> @\s*s\d+\s+)  # '@    s0 '
    (?P<kwd> [\w\s]+\w)    # 'errorbar place
    (?P<sep> \s+)          # ' '
    (?P<val> [a-z]+)       # 'both'
    $""", re.X)
    _rx_str_line  = re.compile(r""" # 'string' regex
    ^ # regex matches e.g. '@    s0 avalue prepend ""'
    (?P<pre> @\s*s\d+\s+)  # '@    s0 '
    (?P<kwd> [\w\s]+\w)    # 'avalue prepend'
    (?P<sep> \s+)          # ' '
    (?P<val> ".*")         # '""'
    $""", re.X)
    _rx_pnt_line  = re.compile(r""" # 'point' regex (2 or more values)
    ^ # regex matches e.g. 's0 avalue offset 0.000000 , 0.000000'
    (?P<pre> @\s*s\d+\s+)                    # '@    s0 '
    (?P<kwd> [\w\s]+\w)                      # 'avalue offset'
    (?P<sep> \s+)                            # ' '
    (?P<val> (\s*[\d.+-]+\s*,)+\s*[\d.+-]+)  # '0.000000 , 0.000000'
    $""", re.X)
    _rx_num_line  = re.compile(r""" # 'numeral' regex
    ^ # regex matches e.g. '@    s0 symbol size 0.250000'
    (?P<pre> @\s*s\d+\s+)  # '@    s0 '
    (?P<kwd> [\w\s]+\w)    # 'symbol size'
    (?P<sep> \s+)          # ' '
    (?P<val> [\d.+-]+)     # '0.250000'
    $""", re.X)
    _rx_font_size = re.compile(r""" # any line defining a font size
    (^@\s+
     s\d+ \s+ avalue \s+ char \s+ size
     \s+
    )
    (?P<val>.*)
    """, re.X)

    def __init__(self):
        """ Create a new instance, without any lines """
        self.lines = []

    def edit_lines(self):
        """ Load lines in EDITOR for editing """
        with tempfile.NamedTemporaryFile(suffix=".agr", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.lines))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.lines = []
        with open(tmpfile.name) as fh:
            for line in fh:
                self.lines.append(line)
        os.unlink(tmpfile.name)

    def _force_index(self, s):
        """ Change the set index number in self.lines to `s`
        """
        rx_set_line = re.compile(r'(@\s*s)(\d+) (.*)')
        for i, line in enumerate(self.lines):
            match = rx_set_line.match(line)
            if match:
                self.lines[i] = "%s%d %s\n" \
                % (match.group(1), s, match.group(3))
            else:
                logging.error("Unexpected format for AgrSet lines")

    def _get_type(self):
        """ Return the type (xy, xydx, ...), for the set"""
        for line in self.lines:
            match = self._rx_type.match(line)
            if match:
                return match.group(1)

    def _get_comment(self):
        """ Return the current comment string for the set """
        for line in self.lines:
            match = self._rx_comment.match(line)
            if match:
                return match.group(1)
        return None

    def _get_legend(self):
        """ Return the current legend string for the set """
        for line in self.lines:
            match = self._rx_legend.match(line)
            if match:
                return match.group(1)
        return None

    def update_properties(self, **kwargs):
        """ Replace set properties according to the given keywords.

            E.g. we can change '@    s0 symbol 1' -> '@    s0 symbol 2'
            by calling `update_properties(symbol=2)`. Spaces in property names
            are converted to underscores (consecutive spaces are contracted),
            so the line '@    s0 avalue char size 1.150000' could be modified
            by the call `update_properties(avalue_char_size=2.0)`.

            If keyword arguments are supplied that don't have a matching
            property in the set, a TypeError is raised.
        """
        logging.debug("* Update Set properties")
        regexes = [self._rx_on_off_line, self._rx_lit_line, self._rx_str_line,
                   self._rx_pnt_line, self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            _update_properties_in_lines(self.lines, regexes, **kwargs)
        except TypeError:
            raise

    def __getitem__(self, key):
        """ Look up a property """
        return self.get_properties([key])[0]

    def __setitem__(self, key, value):
        """ Set a property """
        self.update_properties(**{key: value})

    def __iter__(self):
        """ Iterator (not implemented) """
        raise NotImplementedError

    def __delitem__(self, key):
        """ Dictionary deletion (not implemented) """
        raise NotImplementedError

    def get_properties(self, properties):
        """ Given list of set property names, return an list of their values
            (as strings). Recognized property names are those returned by the
            keys method
        """
        regexes = [self._rx_on_off_line, self._rx_lit_line, self._rx_str_line,
                   self._rx_pnt_line, self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            return _get_properties_in_lines(self.lines, regexes, properties)
        except TypeError:
            raise
        except KeyError:
            raise

    def keys(self):
        """ Return the array of available set properties """
        regexes = [self._rx_on_off_line, self._rx_lit_line, self._rx_str_line,
                   self._rx_pnt_line, self._rx_num_line]
        for i, rx in enumerate(regexes):
            logging.debug("Regex %d: %s", i, rx.pattern.split("\n")[0])
        try:
            return _keys_in_lines(self.lines, regexes)
        except TypeError:
            raise

    def __str__(self):
        """ Return the multi-line string (partial agr file) for the set
        """
        return ''.join(self.lines)

    def scale_font(self, factor):
        """ Scale all font sizes by the given factor """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                value = float(match.group("val"))
                value *= factor
                line = "%s%f" % (match.group(1), value)
                self.lines[i] = line + "\n"

    def set_fontsize(self, size):
        """ Set the font size of all strings. The value of size in in 'agr'
            units.
        """
        for i, line in enumerate(self.lines):
            match = self._rx_font_size.match(line)
            if match:
                line = "%s%f" % (match.group(1), size)
                self.lines[i] = line + "\n"


class AgrDataSet():
    """ Array of lines from the agr file representing the actual data of a
        dataset (stored in the lines attribute)
    """

    _rx_graph_set_number = re.compile(r'@target G(\d+).S(\d+)')
    _rx_type             = re.compile(r'@type (\w+)')
    _set_types = {
        # set type    n: number of columns
        'xy':         2, # An X-Y scatter and/or line plot, plus (optionally)
                         # an annotated value
        'xydx':       3, # Same as XY, but with error bars (either one- or
                         # two-sided) along X axis
        'xydy':       3, # Same as XYDX, but error bars are along Y axis
        'xydxdx':     4, # Same as XYDX, but left and right error bars are
                         # defined separately
        'xydydy':     4, # Same as XYDXDX, but error bars are along Y axis
        'xydxdy':     4, # Same as XY, but with X and Y error bars (either
                         # one- or two-sided)
        'xydxdxdydy': 6, # Same as XYDXDY, but left/right and upper/lower
                         # error bars are defined separately
        'bar':        2, # Same as XY, but vertical bars are used instead of
                         # symbols
        'bardy':      3, # Same as BAR, but with error bars (either one- or
                         # two-sided) along Y axis
        'bardydy':    4, # Same as BARDY, but lower and upper error bars are
                         # defined separately
        'xyhilo':     5, # Hi/Low/Open/Close plot
        'xyz':        3, # Same as XY; makes no sense unless the annotated
                         # value is Z
        'xyr':        3, # X, Y, Radius. Only allowed in Fixed graphs
        'xysize':     3, # Same as XY, but symbol size is variable
        'xycolor':    3, # X, Y, color index (of the symbol fill)
        'xycolpat':   4, # X, Y, color index, pattern index (currently used
                         # for Pie charts only)
        'xyvmap':     4, # Vector map
        'xyboxplot':  6  # Box plot (X, median, upper/lower limit, upper/lower
                         # whisker)
    }

    def __init__(self):
        """ Create a new instance, without any lines """
        self.lines = []

    def __str__(self):
        """ Return the multi-line string (partial agr file) for the data stored
            in the object
        """
        return ''.join(self.lines)

    def get_g_s(self):
        """ Return a tuple (g, s) where g is the graph index and s is the set
            index for which the DataSet contains data
        """
        match = self._rx_graph_set_number.match(self.lines[0])
        if match:
            g = int(match.group(1))
            s = int(match.group(2))
            return (g, s)

    def _force_index(self, g, s):
        """ Change the graph index number in self.lines to `g` and the set
            index number to `s`, i.e. set the first line to
            '@target G{g}.S{s}'.
        """
        self.lines[0] = "@target G%d.S%d\n" % (g,s)

    def edit_data(self):
        """ Load data lines in EDITOR for editing"""
        with tempfile.NamedTemporaryFile(suffix=".tmp", delete=False) \
        as tmpfile:
            tmpfile.write(''.join(self.lines[2:-1]))
            tmpfile.flush()
            call([EDITOR, tmpfile.name])
        self.lines = self.lines[0:2]
        with open(tmpfile.name) as fh:
            for line in fh:
                self.lines.append(line)
        self.lines.append("&\n")
        os.unlink(tmpfile.name)

    def get_n_rows(self):
        """ Return the number of data points (rows) in the data set """
        return len(self.lines) - 3

    def get_n_columns(self):
        """ Return the number of columns in the data set (based on the declared
            type)
        """
        match = self._rx_type.match(self.lines[1])
        if match:
            type = match.group(1)
            try:
                return self._set_types[type]
            except KeyError:
                raise AgrInconsistencyError("Unknown dataset type %s" % type)
        else:
            raise AgrInconsistencyError("No dataset type")

    def get_data(self):
        """ Return a numpy array for each column of data """
        return np.genfromtxt(StringIO(str(self)), skip_header=2,
                             skip_footer=1, unpack=True)

    def get_type(self):
        """ Return the type (xy, xydx, ...), for the data set"""
        match = self._rx_type.match(self.lines[1])
        if match:
            type = match.group(1)
            return type
        else:
            raise AgrInconsistencyError("No dataset type")

    def set_type(self, type, check_columns=True):
        """ Set the type (xy, xydx, ...) for the data set """
        if type in self._set_types.keys():
            self.lines[1] = "@type %s\n" % type
        else:
            raise ValueError("Unknown dataset type %s" % type)
        if check_columns:
            n_columns = len(self.lines[2].split())
            if self._set_types[type] != n_columns:
                raise(AgrInconsistencyError(
                "%s type implies %d columns, but %d columns are present"
                % (type, self._set_types[type], n_columns)))

    def set_data(self, *numpy_arrays, **kwargs):
        """ Set the data from the data set from the given numpy arrays

            You may give 'fmt' as a keyword argument, to indicate how the data
            should  be formatted. The value for 'fmt' may be a single format
            (%10.5f), a sequence of formats, or a multi-format string, e.g.
            'Iteration %d - %10.5f' (cf. numpy savetxt documentation).
            If not given, the default format '%10g' is used.
        """
        if len(numpy_arrays) != self.get_n_columns():
            raise ValueError("number of passed arrays must match existing "
            "number of columns")
        write_buffer = StringIO()
        write_buffer.write(self.lines[0])
        write_buffer.write(self.lines[1])
        if 'fmt' in kwargs:
            np.savetxt(write_buffer, zip(*numpy_arrays), fmt=kwargs['fmt'])
        else:
            np.savetxt(write_buffer, zip(*numpy_arrays), fmt='%10g')
        write_buffer.write(self.lines[-1])
        read_buffer = StringIO(write_buffer.getvalue())
        write_buffer.close()
        self.lines = []
        for line in read_buffer:
            self.lines.append(line)
        read_buffer.close()


############################ Utility Routines #################################


def _update_properties_in_lines(lines, regexes, **kwargs):
    """ Parse each line in `lines` as a string describing a key-value-pair,
        and update its value according to the the given keyword arguments

        Arguments:
        lines:    Array of strings, each of the form "{pre}{kwd}{sep}{val}",
                  that is a line-prefix, a keyword/property (which my include
                  spaces), a separator, and a value
        regexes:  Array of regular expressions that describe the possible
                  structures of the lines. Each regular expression must contain
                  the named groups 'pre', 'kwd', 'sep', and 'val', which are
                  used to cut up the line into its constituents

        After the above positional arguments, an arbitrary number of keyword
        arguments can be given that give new values the the corresponding
        property. If the keyword derived from {key} (as explained in
        _keys_in_line) the value in that line is updated according to the given
        keyword argument.
    """
    logging.debug("_update_properties_in_lines: kwargs: %s", str(kwargs))
    # check regexes: must contain the necessary groups
    for regex in regexes:
        for group in ['pre', 'kwd', 'sep', 'val']:
            if not group in regex.groupindex.keys():
                raise ValueError("regex \n%s\n' "% regex.pattern
                +"does not define groups 'pre', 'kwd', 'sep', 'val'")
    kwd_count = {} # dictionary for counting keyword uses
    for i, line in enumerate(lines):
        matched = False
        logging.debug("line %d: %s", i, line[:-1])
        for ir, regex in enumerate(regexes):
            match = regex.match(line)
            if match:
                matched = True
                line_keyword = match.group('kwd')        # with spaces
                keyword = line_keyword.replace(" ", "_") # without spaces
                while "__" in keyword:
                    keyword = keyword.replace('__', '_')
                if keyword.endswith('_on'):
                    keyword = keyword[:-3] + "_on_off"
                elif keyword.endswith('_off'):
                    keyword = keyword[:-4] + "_on_off"
                if keyword in kwd_count:
                    kwd_count[keyword] += 1
                    keyword = "%s_%d" % (keyword, kwd_count[keyword])
                else:
                    kwd_count[keyword] = 1
                logging.debug("regex %d matched line %d (keyword %s)", ir, i,
                              keyword)
                if keyword in kwargs:
                    logging.debug("keyword %s in kwargs", keyword)
                    pre = match.group('pre')
                    sep = match.group('sep')
                    old_val = match.group('val')
                    val = str(kwargs[keyword])
                    if old_val.startswith('"'): # strings must be quoted
                        # first, ensure value is unquoted
                        if val.startswith('"'):
                            val = val[1:]
                        if val.endswith('"'):
                            val = val[:-1]
                        # then, quote it
                        val = "\"%s\"" % val
                    logging.debug("Setting %s for %s", val, line_keyword)
                    lines[i] = "%s%s%s%s\n" % (pre, line_keyword, sep, val)
                    del kwargs[keyword]
            if matched:
                break # go to next line
        if not matched:
            logging.debug("No regex matched line %d", i)
    if len(kwargs.keys()) > 0:
        raise TypeError("Unexpected keyword arguments: %s" % kwargs.keys())


def _get_properties_in_lines(lines, regexes, properties):
    """ Parse each line in `lines` as a string describing a key-value-pair,
        search for the given properties, and return an array of their
        respective values (as strings)

        Arguments:
        lines:       Array of strings, each of the form "{pre}{kwd}{sep}{val}",
                     that is a line-prefix, a keyword/property (which my
                     include spaces), a separator, and a value
        regexes:     Array of regular expressions that describe the possible
                     structures of the lines. Each regular expression must
                     contain the named groups 'pre', 'kwd', 'sep', and 'val',
                     which are used to cut up the line into its constituents
        properties:  Array of property names to get value for

        Keys are derived from {kwd} according to the rules specified in
        _keys_in_lines
    """
    logging.debug("_get_properties_in_lines: properties: %s", str(properties))
    result_dict = {}
    result = []
    # check regexes: must contain the necessary groups
    for regex in regexes:
        for group in ['pre', 'kwd', 'sep', 'val']:
            if not group in regex.groupindex.keys():
                raise ValueError("regex \n%s\n' "% regex.pattern
                +"does not define groups 'pre', 'kwd', 'sep', 'val'")
    kwd_count = {} # dictionary for counting keyword uses
    for i, line in enumerate(lines):
        matched = False
        logging.debug("line %d: %s", i, line[:-1])
        for ir, regex in enumerate(regexes):
            match = regex.match(line)
            if match:
                matched = True
                line_keyword = match.group('kwd')        # with spaces
                keyword = line_keyword.replace(" ", "_") # without spaces
                while "__" in keyword:
                    keyword = keyword.replace('__', '_')
                if keyword.endswith('_on'):
                    keyword = keyword[:-3] + "_on_off"
                elif keyword.endswith('_off'):
                    keyword = keyword[:-4] + "_on_off"
                if keyword in kwd_count:
                    kwd_count[keyword] += 1
                    keyword = "%s_%d" % (keyword, kwd_count[keyword])
                else:
                    kwd_count[keyword] = 1
                logging.debug("regex %d matched line %d (keyword %s)", ir, i,
                              keyword)
                if keyword in properties:
                    logging.debug("keyword %s in properties", keyword)
                    val = match.group('val')
                    if val.startswith('"'):
                        val = val[1:]
                    if val.endswith('"'):
                        val = val[:-1]
                    result_dict[keyword] = val
            if matched:
                break # go to next line
        if not matched:
            logging.debug("No regex matched line %d", i)
    for property in properties:
        try:
            result.append(result_dict[property])
        except KeyError:
            raise KeyError("No property '%s' found" % property)
    return result


def _keys_in_lines(lines, regexes):
    """ Parse each line in `lines` as a string describing a key-value-pair,
        and return a list of all keys.

        Arguments:
        lines:       Array of strings, each of the form "{pre}{kwd}{sep}{val}",
                     that is a line-prefix, a property key (which may
                     include spaces), a separator, and a value
        regexes:     Array of regular expressions that describe the possible
                     structures of the lines. Each regular expression must
                     contain the named groups 'pre', 'kwd', 'sep', and 'val',
                     which are used to cut up the line into its constituents

        They keys are obtained from the match of {kwd} according to the
        following rules:
        * Spaces are contracted and replaced by underscores.
        * keys that end in either '_on' or '_off' are modified to end in
          '_on_off'
        * If a key appears multiple time, occurences in subsequent lines are
        * mapped to '*_2', '*_3' etc; that is, a counter is appended.
    """
    logging.debug("_keys_in_lines")
    result = []
    # check regexes: must contain the necessary groups
    for regex in regexes:
        for group in ['pre', 'kwd', 'sep', 'val']:
            if not group in regex.groupindex.keys():
                raise ValueError("regex \n%s\n' "% regex.pattern
                +"does not define groups 'pre', 'kwd', 'sep', 'val'")
    kwd_count = {} # dictionary for counting keyword uses
    for i, line in enumerate(lines):
        matched = False
        logging.debug("line %d: %s", i, line[:-1])
        for ir, regex in enumerate(regexes):
            match = regex.match(line)
            if match:
                matched = True
                line_keyword = match.group('kwd')        # with spaces
                keyword = line_keyword.replace(" ", "_") # without spaces
                while "__" in keyword:
                    keyword = keyword.replace('__', '_')
                if keyword.endswith('_on'):
                    keyword = keyword[:-3] + "_on_off"
                elif keyword.endswith('_off'):
                    keyword = keyword[:-4] + "_on_off"
                if keyword in kwd_count:
                    kwd_count[keyword] += 1
                    keyword = "%s_%d" % (keyword, kwd_count[keyword])
                else:
                    kwd_count[keyword] = 1
                logging.debug("regex %d matched line %d (keyword %s)", ir, i,
                              keyword)
                result.append(keyword)
            if matched:
                break # go to next line
        if not matched:
            logging.debug("No regex matched line %d", i)
    return result


def _conv_abs_coord(val, from_unit, to_unit):
    """ Convert between two absolute coordinate units ('cm', 'mm', 'in', 'pt')
    """
    if from_unit != 'pt':
        if from_unit == 'cm':
            val /= 0.035277778
        elif from_unit == 'mm':
            val /= 0.35277778
        elif from_unit.startswith('in'):
            val /= 0.013888889
        else:
            raise ValueError("Unknown unit %s" % from_unit)
    if to_unit != 'pt':
        if to_unit == 'cm':
            val *= 0.035277778
        elif to_unit == 'mm':
            val *= 0.35277778
        elif to_unit.startswith('in'):
            val *= 0.013888889
        else:
            raise ValueError("Unknown unit %s" % to_unit)
    return val


def which(name):
    """ Search PATH for executable files with the given name. Return first
        found path (equivalent to linux `which` command), or None if it cannot
        be found.
    """
    # adapted from a routine that is part of the Twisted framework
    # (http://twistedmatrix.com)
    flags = os.X_OK # On Windows, only flag that has any meaning is os.F_OK.
    exts = filter(None, os.environ.get('PATHEXT', '').split(os.pathsep))
    path = os.environ.get('PATH', None)
    if path is None:
        return None
    for p in os.environ.get('PATH', '').split(os.pathsep):
        p = os.path.join(p, name)
        if os.access(p, flags):
            return p
        for e in exts:
            pext = p + e
            if os.access(pext, flags):
                return pext
    return None


############################ String Conversion ################################


def tex2grace(string, print_string=True):
    """ Convert the given string from TeX to XmGrace syntax. Only greek
        letters, and non-nested subscripts and superscripts are supported.

        If print_string is True, print the resulting string, otherwise return
        it.
    """
    mappings = [
        (r'\\alpha',     r'\\xa\\f{}'),
        (r'\\beta',      r'\\xa\\f{}'),
        (r'\\gamma',     r'\\xg\\f{}'),
        (r'\\delta',     r'\\xd\\f{}'),
        (r'\\epsilon',   r'\\xe\\f{}'),
        (r'\\eps',       r'\\xe\\f{}'),
        (r'\\zeta',      r'\\xz\\f{}'),
        (r'\\eta',       r'\\xh\\f{}'),
        (r'\\theta',     r'\\xq\\f{}'),
        (r'\\gamma',     r'\\xg\\f{}'),
        (r'\\kappa',     r'\\xk\\f{}'),
        (r'\\lambda',    r'\\xl\\f{}'),
        (r'\\mu',        r'\\xm\\f{}'),
        (r'\\nu',        r'\\xn\\f{}'),
        (r'\\xi',        r'\\xx\\f{}'),
        (r'\\pi',        r'\\xp\\f{}'),
        (r'\\rho',       r'\\xr\\f{}'),
        (r'\\sigma',     r'\\xs\\f{}'),
        (r'\\tau',       r'\\xt\\f{}'),
        (r'\\upsilon',   r'\\xu\\f{}'),
        (r'\\phi',       r'\\xj\\f{}'),
        (r'\\chi',       r'\\xc\\f{}'),
        (r'\\psi',       r'\\xy\\f{}'),
        (r'\\omega',     r'\\xw\\f{}'),
        (r'\\Gamma',     r'\\xG\\f{}'),
        (r'\\Delta',     r'\\xD\\f{}'),
        (r'\\Theta',     r'\\xT\\f{}'),
        (r'\\Lambda',    r'\\xL\\f{}'),
        (r'\\Xi',        r'\\xX\\f{}'),
        (r'\\Pi',        r'\\xP\\f{}'),
        (r'\\Sigma',     r'\\xS\\f{}'),
        (r'\\Upsilon',   r'\\xU\\f{}'),
        (r'\\Phi',       r'\\xF\\f{}'),
        (r'\\Psi',       r'\\xY\\f{}'),
        (r'\\Omega',     r'\\xW\\f{}'),
        (r'\\cdot',      r'\\#{b7}'),
        (r'\\pm',        r'\\#{b1}'),
        (r'\\times',     r'\\#{d7}'),
        (r'\^\{(.+?)\}', r'\\S\1\\N'),
        (r'_\{(.+?)\}',  r'\\s\1\\N'),
        (r'\^(.)',       r'\\S\1\\N'),
        (r'_(.)',        r'\\s\1\\N'),
    ]
    for mapping in mappings:
        string = re.sub(mapping[0], mapping[1], string)
    if print_string:
        print string
    else:
        return string


def grace2tex(string, print_string=True):
    """ Inverse of tex2grace """
    mappings = [
        ( r'\\f\{Symbol\}', r'\\x'),
        ( r'\\xa\\f\{\}',   r'\\alpha'),
        ( r'\\xa\\f\{\}',   r'\\beta'),
        ( r'\\xg\\f\{\}',   r'\\gamma'),
        ( r'\\xd\\f\{\}',   r'\\delta'),
        ( r'\\xe\\f\{\}',   r'\\epsilon'),
        ( r'\\xz\\f\{\}',   r'\\zeta'),
        ( r'\\xh\\f\{\}',   r'\\eta'),
        ( r'\\xq\\f\{\}',   r'\\theta'),
        ( r'\\xg\\f\{\}',   r'\\gamma'),
        ( r'\\xk\\f\{\}',   r'\\kappa'),
        ( r'\\xl\\f\{\}',   r'\\lambda'),
        ( r'\\xm\\f\{\}',   r'\\mu'),
        ( r'\\xn\\f\{\}',   r'\\nu'),
        ( r'\\xx\\f\{\}',   r'\\xi'),
        ( r'\\xp\\f\{\}',   r'\\pi'),
        ( r'\\xr\\f\{\}',   r'\\rho'),
        ( r'\\xs\\f\{\}',   r'\\sigma'),
        ( r'\\xt\\f\{\}',   r'\\tau'),
        ( r'\\xu\\f\{\}',   r'\\upsilon'),
        ( r'\\xj\\f\{\}',   r'\\phi'),
        ( r'\\xc\\f\{\}',   r'\\chi'),
        ( r'\\xy\\f\{\}',   r'\\psi'),
        ( r'\\xw\\f\{\}',   r'\\omega'),
        ( r'\\xG\\f\{\}',   r'\\Gamma'),
        ( r'\\xD\\f\{\}',   r'\\Delta'),
        ( r'\\xT\\f\{\}',   r'\\Theta'),
        ( r'\\xL\\f\{\}',   r'\\Lambda'),
        ( r'\\xX\\f\{\}',   r'\\Xi'),
        ( r'\\xP\\f\{\}',   r'\\Pi'),
        ( r'\\xS\\f\{\}',   r'\\Sigma'),
        ( r'\\xU\\f\{\}',   r'\\Upsilon'),
        ( r'\\xF\\f\{\}',   r'\\Phi'),
        ( r'\\xY\\f\{\}',   r'\\Psi'),
        ( r'\\xW\\f\{\}',   r'\\Omega'),
        (r'\\#{b7}',        r'\\cdot'),
        (r'\\#{b1}',        r'\\pm'),
        (r'\\#{d7}',        r'\\times'),
        ( r'\\S(.+?)\\N',   r'^{\1}'),
        ( r'\\s(.+?)\\N',   r'_{\1}'),
        ( r'\\S(.+?)\\N',   r'^\1'),
        ( r'\\s(.+?)\\N',   r'_\1'),
    ]
    for mapping in mappings:
        string = re.sub(mapping[0], mapping[1], string)
    if print_string:
        print string
    else:
        return string


############################### Exceptions ####################################


class AgrParserError(Exception):
    """ Exception thrown when the parser encounters an error """
    pass


class AgrInconsistencyError(Exception):
    """ Exception thrown when the agr data is found to be in an inconsistent or
        illegal state
    """
    pass


####################### Main Program (start ipython) ##########################

def main(argv=None):
    if argv is None:
        argv = sys.argv
    arg_parser = OptionParser(
    usage = "usage: %prog [options] [AGR_FILE]",
    description = "Work with an XMGrace AGR file interactively.")
    arg_parser.add_option(
        '--repair', action='store_true', dest='repair',
        help="Attempt to repair the given agr file")
    arg_parser.add_option(
        '--hardcopy', action='store', dest='hardcopy',
        help="Write out a hardcopy to the given file and exit immediately")
    options, args = arg_parser.parse_args(argv)
    try:
        from IPython import embed
        from IPython.core.page import page
        loaded_file = False
        if (len(args) > 1):
            filename = args[-1]
            if os.path.isfile(filename):
                agr = AgrFile(filename, repair=options.repair)
                loaded_file = True
            else:
                logging.error("File '%s' not found", filename)
        if loaded_file:
            banner = """
*************** Starting ipython with xmgrace_parser preloaded **************

The variable `agr` has been loaded as

    agr = AgrFile('{0}')

and is ready for interactive use. Type `page(__doc__)` to show the module
documentation including example usage.

******************************************************************************
""".format(filename)
        else:
            banner = """
*************** Starting ipython with xmgrace_parser preloaded **************

You can now directly create an AgrFile object like this:

    >>> agr = AgrFile('plot.agr')

and work with it interactively. Type `page(__doc__)` to show the module
documentation including example usage.

******************************************************************************
"""
        banner2 = """
?         -> Introduction and overview of IPython's features.
%quickref -> Quick reference.
help      -> Python's own help system.
object?   -> Details about 'object', use 'object??' for extra details.
%pylab    -> load numpy and matplotlib
"""
        exit_msg="Exiting interactive xmgrace_parser"
        if options.hardcopy:
            if loaded_file:
                agr.hardcopy(options.hardcopy)
            else:
                arg_parser.error("The --hardcopy option is only valid if an "
                                 "AGR_FILE is also given")
        else:
            embed(banner1=banner, banner2=banner2, exit_msg=exit_msg)
    except ImportError:
        logging.error("IPython is not available. Can't run interactively")
        return 1

if __name__ == "__main__":
    sys.exit(main())
