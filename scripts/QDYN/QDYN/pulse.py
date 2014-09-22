"""
Working with (real-valued) pulses
"""
import numpy as np
from numpy.fft import fftfreq, fft, ifft
import matplotlib
from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
from scipy import signal
import scipy.fftpack
import re
import sys
from QDYN.units import NumericConverter
convert = NumericConverter()


class Pulse(object):
    """
    Class describing Pulse

    Attributes
    ----------

    tgrid : ndarray(float64)
        time points at which the pulse values are defined
    amplitude : ndarray(float64), ndarray(complex128)
        array of real or complex pulse values
    mode : str
        How to write the pulse values to file. Can be `complex`, `real`, or
        `abs`. There will be three columns in the file for `mode='complex'`,
        and two columns for `mode='real'` or `mode='abs'`
    time_unit : str
        Unit of values in `tgrid`
    ampl_unit : str
        Unit of values in `amplitude`
    freq_unit : str
        Unit to use for frequency when calculating the spectrum
    dt : scalar
        Time step (in `time_unit`)
    preamble  : array
        Array of lines that are written before the header when writing the
        pulse to file. Each line should start with '# '
    postamble : array
        Array of lines that are written after all data lines. Each line
        should start with '# '
    """

    def __init__(self, filename=None, tgrid=None, amplitude=None,
                 time_unit='au', ampl_unit='au', freq_unit=None,
                 mode='complex'):
        """
        Initialize a pulse

        Arguments
        ---------
        filename : None, str
            Name of file from which to read pulse. If given, `tgrid`,
            `amplitude`, `time_unit`, `ampl_unit`, `mode` should be None
        tgrid : None, ndarray(float64)
            Time grid values
        amplitude : None, ndarray(float64), ndarray(complex128)
            Amplitude values
        time_unit : str
            Unit of values in `tgrid`. Will be ignored when reading from file.
        ampl_unit : str
            Unit of values in `amplitude`. Will be ignored when reading from
            file.
        freq_unit : str
            Unit of frequencies when calculating spectrum. If not given, an
            appropriate unit based on `time_unit` will be chosen
        mode : str
            Value the `mode` attribute (indicating format of file when pulse is
            written out

        Examples
        --------
        >>> p = Pulse('pulse.dat')

        >>> import numpy as np
        >>> p = Pulse(tgrid=np.linspace(0, 800, 1000),
        ...           amplitude=np.zeros(1000),
        ...           time_unit='ns', ampl_unit='MHz')
        """
        if filename is None:
            assert (tgrid is not None), \
            "Either filename or tgrid must be present"
            tgrid = np.array(tgrid, dtype=np.float64)
            if amplitude is None:
                amplitude = np.zeros(len(tgrid))
            if mode == 'complex':
                amplitude = np.array(amplitude, dtype=np.complex128)
            else:
                amplitude = np.array(amplitude, dtype=np.float64)
        else:
            assert tgrid is None and amplitude is None, \
            "Either filename or tgrid and amplitude must be present"
        self.tgrid = tgrid
        self.amplitude = amplitude
        self.mode = mode
        self.time_unit = time_unit
        self.ampl_unit = ampl_unit
        self.freq_unit = 'au'

        self.preamble = []
        self.postamble = []
        if filename is not None:
            self.read(filename)

        freq_units = { # map time_unit to most suitable freq_unit
            'ns' : 'GHz',
            'ps' : 'cminv',
            'fs' : 'eV',
            'microsec' : 'MHz',
        }
        try:
            self.freq_unit = freq_units[self.time_unit]
        except KeyError:
            self.freq_unit = 'au'
        if freq_unit is not None:
            self.freq_unit = freq_unit

        self._check()

    def _check(self):
        """
        Check self-consistency of pulse
        """
        assert self.tgrid is not None, "Pulse is not initialized"
        assert self.amplitude is not None, "Pulse is not initialized"
        assert type(self.tgrid) == np.ndarray, "tgrid must be numpy array"
        assert type(self.amplitude) == np.ndarray, \
        "amplitude must be numpy array"
        assert self.tgrid.dtype.type is np.float64, \
        "tgrid must be double precision"
        assert self.amplitude.dtype.type in [np.float64, np.complex128], \
        "amplitude must be double precision"
        assert len(self.tgrid) == len(self.amplitude), \
        "length of tgrid and amplitudes do not match"
        assert self.mode in ['complex', 'abs', 'real'], \
        "Illegal value for mode: %s" % self.mode
        assert self.ampl_unit in convert.au_convfactors.keys(), \
        "Unknown ampl_unit %s" % self.ampl_unit
        assert self.time_unit in convert.au_convfactors.keys(), \
        "Unknown time_unit %s" % self.time_unit
        assert self.freq_unit in convert.au_convfactors.keys(), \
        "Unknown freq_unit %s" % self.freq_unit
        if self.mode == 'real':
            if np.max(np.abs(self.amplitude.imag)) > 0.0:
                print >> sys.stderr, \
                "mode is 'real', but pulse has non-zero imaginary part"


    def read(self, filename):
        """
        Read a pulse from file, in the format generated by the QDYN
        `write_pulse` routine.

        Notes
        -----

        The `write` method allows to restore *exactly* the original pulse file
        """
        header_rx = {
            'complex': re.compile(r'''
                ^\#\s*t(ime)? \s* \[\s*(?P<time_unit>\w+)\s*\]\s*
                Re\((ampl|E)\) \s* \[\s*(?P<ampl_unit>\w+)\s*\]\s*
                Im\((ampl|E)\) \s* \[(\w+)\]\s*$''', re.X|re.I),
            'real': re.compile(r'''
                ^\#\s*t(ime)? \s* \[\s*(?P<time_unit>\w+)\s*\]\s*
                Re\((ampl|E)\) \s* \[\s*(?P<ampl_unit>\w+)\s*\]\s*$''',
                re.X|re.I),
            'abs': re.compile(r'''
                ^\#\s*t(ime)? \s* \[\s*(?P<time_unit>\w+)\s*\]\s*
                (Abs\()?(ampl|E)(\))? \s* \[\s*(?P<ampl_unit>\w+)\s*\]\s*$''',
                re.X|re.I),
        }

        try:
            t, x, y = np.genfromtxt(filename, unpack=True, dtype=np.float64)
        except ValueError:
            t, x = np.genfromtxt(filename, unpack=True, dtype=np.float64)
            y = None
        with open(filename) as in_fh:
            in_preamble = True
            for line in in_fh:
                if line.startswith('#'):
                    if in_preamble:
                        self.preamble.append(line.strip())
                    else:
                        self.postamble.append(line.strip())
                else:
                    if in_preamble:
                        in_preamble = False
            # the last line of the preamble *must* be the header line. We will
            # process it and remove it from self.preamble
            try:
                header_line = self.preamble.pop()
                found_mode = False
                for mode, pattern in header_rx.items():
                    match = pattern.match(header_line)
                    if match:
                        self.mode = mode
                        self.time_unit = match.group('time_unit')
                        self.ampl_unit = match.group('ampl_unit')
                        found_mode = True
                        break
                if not found_mode:
                    print "\nWARNING: Non-standard header in pulse file"
                    print "Check that pulse was read with correct units\n"
                    if y is None:
                        self.mode = 'abs'
                    else:
                        self.mode = 'complex'
                    free_pattern = re.compile(r'''
                    ^\# .* \[\s*(?P<time_unit>\w+)\s*\]
                        .* \[\s*(?P<ampl_unit>\w+)\s*\]''', re.X)
                    match = free_pattern.search(header_line)
                    if match:
                        self.time_unit = match.group('time_unit')
                        self.ampl_unit = match.group('ampl_unit')
                        print "Set time_unit = ", self.time_unit
                        print "Set ampl_unit = ", self.ampl_unit
                    else:
                        print "\nWARNING: Could not identify units."
                        print "Setting to atomic units\n"
                        self.time_unit = 'au'
                        self.ampl_unit = 'au'
            except IndexError:
                raise IOError("Pulse file does not contain a preamble")
        self.tgrid = t
        if self.mode == 'abs':
            self.amplitude = x
        elif self.mode == 'real':
            self.amplitude = x
        elif self.mode == 'complex':
            self.amplitude = x + 1j * y
        else:
            raise ValueError("mode must be 'abs', 'real', or 'complex'")
        self._check()

    def dt(self):
        """
        Return time step
        """
        return self.tgrid[1] - self.tgrid[0]

    def t0(self):
        """
        Return time at which the pulse begins, which is dt/2 before the first
        point in the pulse
        """
        result = self.tgrid[0] - 0.5 * self.dt()
        if abs(result) < 1.0e-15*self.tgrid[-1]:
            result = 0.0
        return result

    def w_max(self, freq_unit=None):
        """
        Return the maximum frequency that can be represented with the current
        sampling rate
        """
        if freq_unit is None:
            freq_unit = self.freq_unit
        n = len(self.tgrid)
        dt = convert.to_au(self.dt(), self.time_unit)
        if n % 2 == 1:
            # odd
            w_max = ((n - 1) * np.pi) / (n * dt)
        else:
            # even
            w_max = np.pi / dt
        return convert.from_au(w_max, freq_unit)

    def dw(self, freq_unit=None):
        """
        Return the step width in the spectrum (i.e. the spectral resolution)
        based on the current pulse duration
        """
        n = len(self.tgrid)
        w_max = self.w_max(freq_unit)
        if n % 2 == 1:
            # odd
            return  2.0 * w_max / float(n-1)
        else:
            # even
            return 2.0 * w_max / float(n)

    def T(self):
        """
        Return the time at which the pulse ends, which is dt/2 after the last
        point in the pulse
        """
        result = self.tgrid[-1] + 0.5 * self.dt()
        if abs(round(result) - result) < (1.0e-15 * result):
            result = round(result)
        return result

    def config_tgrid(self):
        """
        Return a multiline string describing a time grid in a QDYN config file
        that is appropriate to the pulse
        """
        unit = self.time_unit
        nt = len(self.tgrid) + 1
        result = ['tgrid: n = 1',]
        result.append(' 1: t_start = %g_%s, t_stop = %g_%s, nt = %d'
                      % (self.t0(), unit, self.T(), unit, nt))
        return "\n".join(result)

    def convert(self, time_unit=None, ampl_unit=None, freq_unit=None):
        """
        Convert the pulse data to different units
        """
        if not time_unit is None:
            c = convert.to_au(1, self.time_unit) \
                * convert.from_au(1, time_unit)
            self.tgrid *= c
            self.time_unit = time_unit
        if not ampl_unit is None:
            c = convert.to_au(1, self.ampl_unit) \
                * convert.from_au(1, ampl_unit)
            self.amplitude *= c
            self.ampl_unit = ampl_unit
        if not freq_unit is None:
            self.freq_unit = freq_unit
        self._check()

    def get_timegrid_point(self, t, move="left"):
        """
        Return the next point to the left (or right) of the given `t` which is
        on the pulse time grid
        """
        t_start = self.tgrid[0]
        t_stop = self.tgrid[-1]
        dt = self.dt()
        if t < t_start:
            return t_start
        if t > t_stop:
            return t_stop
        if move == "left":
            n = np.floor((t - t_start) / dt)
        else:
            n = np.ceil((t - t_start) / dt)
        return t_start + n * dt

    def fluence(self):
        """
        Calculate and return the fluence (integrated pulse energy) for the
        pulse

        .. math:: \\int_{-\\infty}^{\\infty} \\vert|E(t)\\vert^2 dt
        """
        return np.sum(self.amplitude**2) * self.dt()

    def oct_iter(self):
        """
        Attempt to extract the OCT iteration number from the pulse preamble and
        return it. On failure, return 0.
        """
        iter_rx = re.compile(r'OCT iter[\s:]*(\d+)', re.I)
        for line in self.preamble:
            iter_match = iter_rx.search(line)
            if iter_match:
                return int(iter_match.group(1))

    def spectrum(self, freq_unit=None, mode='complex', sort=False):
        """
        Calculate the spectrum of the pulse

        Parameters
        ----------

        freq_unit : str, optional
            Desired unit of the `freq` output array. Can Hz (GHz, Mhz, etc) to
            obtain frequencies, or any energy unit, using the correspondence
            `f = E/h`. If not given, defaults to the `freq_unit` attribtue
        mode : str, optional
            Wanted mode for `spectrum` output array.
            Possible values are 'complex', 'abs', 'real', 'imag'
        sort : bool, optional
            Sort the output `freq` array (and the output `spectrum` array) so
            that frequecies are ordered from `-w_max .. 0 .. w_max`, instead of
            the direct output from the FFT. This is good for plotting, but does
            not allow to do an inverse Fourier transform afterwards

        Returns
        -------

        freq : ndarray(float64)
            Frequency values associated with the amplitude values in
            `spectrum`, i.e. the x-axis of the spectrogram. The values are in
            the unit `freq_unit`
        spectrum : ndarray(float64), ndarray(complex128)
            Real (`mode in ['abs', 'real', 'imag']`) or complex
            (`mode='complex'`) amplitude of each frequency component

        Notes
        -----

            If `sort=False` and `mode='complex'`, the original pulse
            values can be obtained by simply calling `np.fft.ifft`

            The spectrum is not normalized (Scipy follows the convention of
            doing the normalization on the backward transform). You might want
            to normalized by 1/n for plotting.
        """
        if freq_unit is None:
            freq_unit = self.freq_unit
        s = fft(self.amplitude) # spectrum amplitude
        n = len(self.amplitude)
        dt = self.dt()
        dt = convert.to_au(dt, self.time_unit)
        f = fftfreq(n, d=dt/(2.0*np.pi)) # spectrum frequencies
        c = convert.from_au(1, freq_unit)
        f *= c # convert to desired unit
        modifier = {
            'abs'    : lambda s: np.abs(s),
            'real'   : lambda s: np.real(s),
            'imag'   : lambda s: np.imag(s),
            'complex': lambda s: s
        }
        if sort:
            order = np.argsort(f)
            f = f[order]
            s = s[order]
        return f, modifier[mode](s)

    def derivative(self):
        """
        Calculate the derivative of the current pulse and return it as a new
        pulse. Note that derivative is in units of `ampl_unit`/`time_unit`.
        """
        self._unshift()
        T = self.tgrid[-1] - self.tgrid[0]
        deriv = scipy.fftpack.diff(self.amplitude) * (2.0*np.pi / T)
        deriv_pulse = Pulse(tgrid=self.tgrid, amplitude=deriv,
                            time_unit=self.time_unit, ampl_unit=self.ampl_unit)
        self._shift()
        deriv_pulse._shift()
        return deriv_pulse

    def write(self, filename, mode=None):
        """
        Write a pulse to file, in the same format as the QDYN `write_pulse`
        routine

        Parameters
        ----------

        filename : str
            Name of file to which to write the pulse
        mode : str, optional
           Mode in which to write files. Possible values are 'abs', 'real', or
           'complex'. The former two result in a two-column file, the latter in
           a three-column file. If not given, the value of the `mode` attribute
           is used.
        """
        if mode is None:
            mode = self.mode
        self._check()
        preamble = self.preamble
        if not hasattr(preamble, '__getitem__'):
            preamble = [str(preamble), ]
        postamble = self.postamble
        if not hasattr(postamble, '__getitem__'):
            postamble = [str(postamble), ]
        with open(filename, 'w') as out_fh:
            # preamble
            for line in preamble:
                line = str(line).strip()
                if line.startswith('#'):
                    print >> out_fh, line
                else:
                    print >> out_fh, '# ', line
            # header and data
            time_header     = "time [%s]" % self.time_unit
            ampl_re_header  = "Re(ampl) [%s]" % self.ampl_unit
            ampl_im_header  = "Im(ampl) [%s]" % self.ampl_unit
            ampl_abs_header = "Abs(ampl) [%s]" % self.ampl_unit
            if mode == 'abs':
                print >> out_fh, "# %23s%25s" % (time_header, ampl_abs_header)
                for i, t in enumerate(self.tgrid):
                    print >> out_fh, "%25.17E%25.17E" \
                                     % (t, abs(self.amplitude[i]))
            elif mode == 'real':
                print >> out_fh, "# %23s%25s" % (time_header, ampl_re_header)
                for i, t in enumerate(self.tgrid):
                    print >> out_fh, "%25.17E%25.17E" \
                                     % (t, self.amplitude.real[i])
            elif mode == 'complex':
                print >> out_fh, "# %23s%25s%25s" \
                                % (time_header, ampl_re_header, ampl_im_header)
                for i, t in enumerate(self.tgrid):
                    print >> out_fh, "%25.17E%25.17E%25.17E" \
                                     % (t, self.amplitude.real[i],
                                        self.amplitude.imag[i])
            else:
                raise ValueError("mode must be 'abs', 'real', or 'complex'")
            # postamble
            for line in self.postamble:
                line = str(line).strip()
                if line.startswith('#'):
                    print >> out_fh, line
                else:
                    print >> out_fh, '# ', line

    def _unshift(self):
        """
        Move the pulse onto the unshifted time grid. This increases the number
        of points by one
        """
        dt = self.dt()
        tgrid_new = np.linspace(self.t0(), self.T(), len(self.tgrid)+1)
        pulse_new = np.zeros(len(self.amplitude)+1,
                             dtype=self.amplitude.dtype.type)
        pulse_new[0] = self.amplitude[0]
        for i in xrange(1, len(pulse_new)-1):
            pulse_new[i] = 0.5 * (self.amplitude[i-1] + self.amplitude[i])
        pulse_new[-1] = self.amplitude[-1]
        self.tgrid     = tgrid_new
        self.amplitude = pulse_new
        self._check()

    def _shift(self):
        """
        Inverse of _unshift
        """
        dt = self.dt()
        tgrid_new = np.linspace(self.tgrid[0]  + dt/2.0,
                                self.tgrid[-1] - dt/2.0, len(self.tgrid)-1)
        pulse_new = np.zeros(len(self.amplitude)-1,
                             dtype=self.amplitude.dtype.type)
        pulse_new[0] = self.amplitude[0]
        for i in xrange(1, len(pulse_new)-1):
            pulse_new[i] = 2.0 * self.amplitude[i] - pulse_new[i-1]
        pulse_new[-1] = self.amplitude[-1]
        self.tgrid     = tgrid_new
        self.amplitude = pulse_new
        self._check()

    def resample(self, upsample=None, downsample=None, num=None, window=None):
        """
        Resample the pulse, either by giving an upsample ratio, a downsample
        ration, or a number of sampling points

        Parameters
        ----------

        upsample : int, optional
           Factor by which to increase the number of samples. Afterwards, those
           points extending beyond the original end point of the pulse are
           discarded.
        downsample : int, optional
            For `downsample=n` keep only every n'th point of the original
            pulse. This may cause the resampled pulse to end earlier than the
            original pulse
        num : int, optional
            Resample with `num` sampling points. This may case the end point of
            the resampled pulse to change
        window : array_like, callable, string, float, or tuple, optional
            Specifies the window applied to the signal in the Fourier
            domain.  See `sympy.signal.resample`

        Notes
        -----

        Exactly one of `upsample`, `downsample`, or `num` must be given.

        Upsampling will maintain the pulse start and end point (as returned by
        the `T()` and `t0()` methods), up to some rounding errors.
        Downsampling, or using an arbitrary number will change the end point of
        the pulse in general.
        """
        self._unshift()
        dt = self.dt()
        nt = len(self.tgrid)

        if sum([(x is not None) for x in [upsample, downsample, num]]) != 1:
            raise ValueError(
            "Exactly one of upsample, downsample, or num must be given")
        if num is None:
            if upsample is not None:
                upsample = int(upsample)
                num = nt * upsample
            elif downsample is not None:
                downsample = int(downsample)
                assert downsample > 0, "downsample must be > 0"
                num = nt / downsample
            else:
                num =  nt
        else:
            num = num + 1 # to account for shifting

        a, t = signal.resample(self.amplitude, num, self.tgrid, window=window)

        if upsample is not None:
            # discard last (upsample-1) elements
            self.amplitude = a[:-(upsample-1)]
            self.tgrid = t[:-(upsample-1)]
        else:
            self.amplitude = a
            self.tgrid = t

        self._shift()

    def show(self, show_pulse=True, show_spectrum=True, zoom=True,
             freq_unit=None, title="", mark_freqs=None):
        """
        Show a plot of the pulse and its spectrum

        Parameters
        ----------

        show_pulse : bool
            Include a plot of the pulse amplitude? If the pulse has a vanishing
            imaginary part, the plot will show the real part of the amplitude,
            otherwise, there will be one plot for the absolute value of the
            amplitude and one showing the complex phase in units of pi
        show_spectrum : bool
            Include a plot of the spectrum?
        zoom : bool
            If `True`, only show the part of the spectrum that has
            amplitude of at least 0.1% of the maximum peak in the spectrum.
            For real pulses, only the positive part of the spectrum is shown
        freq_unit : str
            Unit in which to show the frequency axis in the spectrum. If not
            given, use the `freq_unit` attribute
        title: str
            An optional title to show at the top of the figure
        mark_freqs : None, array of floats
            Array of frequencies to mark in spectrum as vertical dashed lines
        """
        if freq_unit is None:
            freq_unit = self.freq_unit
        self._check()
        # determine whether pulse is complex or real by looking at all the
        # imaginary parts. We do *not* want to use the 'mode' attribute, which
        # only indicates how the file is to be written out
        if np.max(np.abs(self.amplitude.imag)) > 0.0:
            pulse_is_complex = True
        else:
            pulse_is_complex = False

        if show_pulse and show_spectrum:
            if pulse_is_complex:
                # show abs(pulse), phase(pulse), abs(spectrum)
                gs = GridSpec(3, 1, height_ratios=[2, 1, 2])
            else:
                # show real(pulse), abs(spectrum)
                gs = GridSpec(2, 1, height_ratios=[1, 1])
        else:
            if show_pulse:
                if pulse_is_complex:
                    # show abs(pulse), phase(pulse)
                    gs = GridSpec(2, 1, height_ratios=[2, 1])
                else:
                    # show real(pulse)
                    gs = GridSpec(1, 1)
            else:
                gs = GridSpec(1, 1)

        if show_pulse:
            # plot pulse amplitude
            ax1 = plt.subplot(gs[0])
            if pulse_is_complex:
                ax1.plot(self.tgrid, np.abs(self.amplitude))
                ax1.set_ylabel("abs(pulse) (%s)" % self.ampl_unit)
            else:
                ax1.axhline(y=0.0, ls='-', color='black')
                ax1.plot(self.tgrid, self.amplitude.real)
                ax1.set_ylabel("pulse) (%s)" % self.ampl_unit)
            ax1.set_xlabel("time (%s)" % self.time_unit)
            if pulse_is_complex:
                # plot pulse phase
                ax2 = plt.subplot(gs[1])
                ax2.axhline(y=0.0, ls='-', color='black')
                ax2.plot(self.tgrid, np.angle(self.amplitude) / np.pi)
                ax2.set_ylabel("phase (pi)")
                ax2.set_xlabel("time (%s)" % self.time_unit)

        if show_spectrum:

            freq, spectrum = self.spectrum(mode='abs', sort=True,
                                           freq_unit=freq_unit)
            # normalizing the spectrum makes it independent of the number of
            # sampling points. That is, the spectrum of a signal that is simply
            # resampled will be the same as that of the original signal. Scipy
            # follows the convention of doing the normalization in the inverse
            # transform
            spectrum *= 1.0 / len(spectrum)

            if zoom:
                # figure out the range of the spectrum
                max_amp = np.amax(spectrum)
                if pulse_is_complex:
                    # we center the spectrum around zero, and extend
                    # symmetrically in both directions as far as there is
                    # significant amplitude
                    wmin = np.max(freq)
                    wmax = np.min(freq)
                    for i, w in enumerate(freq):
                        if spectrum[i] > 0.001*max_amp:
                            if w > wmax:
                                wmax = w
                            if w < wmin:
                                wmin = w
                    wmax = max(abs(wmin), abs(wmax))
                    wmin = -wmax
                else:
                    # we show only the positive part of the spectrum (under the
                    # assumption that the spectrum is symmetric) and zoom in
                    # only on the region that was significant amplitude
                    wmin = 0.0
                    wmax = 0.0
                    for i, w in enumerate(freq):
                        if spectrum[i] > 0.001*max_amp:
                            if wmin == 0 and w > 0:
                                wmin = w
                            wmax = w
                buffer = (wmax - wmin) * 0.1

            # plot spectrum
            ax3 = plt.subplot(gs[-1])
            if zoom:
                ax3.set_xlim((wmin-buffer), (wmax+buffer))
            ax3.set_xlabel("frequency (%s)" % freq_unit)
            ax3.set_ylabel("abs(spec) (arb. un.)")
            ax3.plot(freq, spectrum)
            if mark_freqs is not None:
                for freq in mark_freqs:
                    ax3.axvline(x=float(freq), ls='--', color='black')

        plt.subplots_adjust(hspace=0.3)
        plt.suptitle(title)
        plt.show()

    def show_pulse(self):
        """
        Show a plot of the pulse amplitude; alias for
        `show(show_spectrum=False)`
        """
        self.show(show_spectrum=False)

    def show_spectrum(self, zoom=True, freq_unit=None):
        """
        Show a plot of the pulse spectrum; alias for
        `show(show_pulse=False, zoom=zoom, freq_unit=freq_unit)`
        """
        self.show(show_pulse=False, zoom=zoom, freq_unit=freq_unit)


def tgrid_from_config(config, pulse_grid=True):
    """
    Extract the time grid from the given config file

    Paramters
    ---------

    config : str
        Path to config file
    pulse_grid : bool, optional
        If True (default), return the time grid for pulse values, which is
        shifted by dt/2 with respect to the time grid for the states.
        If False, return the time grid for the states, directly as it is
        defined in the config file


    Returns
    -------

    tgrid : ndarray(float64)
        Time grid values
    timeunit : str
        Unit of values in `tgrid`
    """
    with open(config) as in_fh:
        in_tgrid = False
        params = {
            't_start': None,
            't_stop': None,
            'dt': None,
            'nt': None,
        }
        rxs = {
            't_start': re.compile(r't_start\s*=\s*([\d.de]+)(_\w+)?', re.I),
            't_stop': re.compile(r't_stop\s*=\s*([\d.de]+)(_\w+)?', re.I),
            'dt': re.compile(r'dt\s*=\s*([\d.de]+)(_\w+)?', re.I),
            'nt': re.compile(r'nt\s*=\s*(\d+)'),
        }
        timeunit = 'au'
        for line in in_fh:
            line = line.strip()
            if line.startswith('tgrid'):
                in_tgrid = True
            elif re.match(r'^\w+:', line):
                in_tgrid = False
            if in_tgrid:
                for param, rx in rxs.items():
                    m = rx.search(line)
                    if m:
                        if len(m.groups()) == 2: # value and unit in match
                            value = float(m.group(1))
                            unit = m.group(2)
                            if unit is not None:
                                timeunit = unit[1:]
                                value = convert.to_au(value, timeunit)
                            params[param] = value
                        else:
                            value = int(m.group(1))
                            params[param] = value
        t_start = params['t_start']
        t_stop = params['t_stop']
        dt = params['dt']
        nt = params['nt']
        if t_start is None:
            assert ((t_stop is not None) and (dt is not None)
            and (nt is not None)), "tgrid not fully specified in config"
            t_start = t_stop - (nt-1) * dt
        if t_stop is None:
            assert ((t_start is not None) and (dt is not None)
            and (nt is not None)), "tgrid not fully specified in config"
            t_stop = t_start + (nt-1)*dt
        if nt is None:
            assert ((t_start is not None) and (dt is not None)
            and (t_stop is not None)), "tgrid not fully specified in config"
            nt = int( (t_stop - t_start)/ dt ) + 1
        if dt is None:
            assert ((t_start is not None) and (nt is not None)
            and (t_stop is not None)), "tgrid not fully specified in config"
            dt = (t_stop - t_start) / float(nt - 1)
        t_start = convert.from_au(t_start, timeunit)
        t_stop = convert.from_au(t_stop, timeunit)
        dt = convert.from_au(dt, timeunit)
        if pulse_grid:
            # convert to pulse parameters
            t_start += 0.5*dt
            t_stop  -= 0.5*dt
            nt      -= 1
        tgrid = np.linspace(t_start, t_stop, nt)
        return tgrid, timeunit


###############################################################################
# Shape functions
###############################################################################


def carrier(t, time_unit, freq, freq_unit, weights=None, complex=False):
    """
    Create the "carrier" of the pulse as a weighted superposition of cosines at
    different frequencies.

    Parameters
    ----------
    t : scalar, ndarray(float64)
        Time value or time grid
    time_unit : str
        Unit of `t`
    freq : scalar, ndarray(float64)
        Carrier frequency or frequencies
    freq_unit : str
        Unit of `freq`
    weights : array-like, optional
        If `freq` is an array, weights for the different frequencies. If not
        given, all weights are 1
    complex : bool
        If `True`, oscillate in the complex plane

    Returns
    -------

    signal : scalar, ndarray(complex128)
        Depending on whether `complex` is `True` or `False`,
        .. math::
            s(t) = \\sum_j  w_j * \\cos(\\omega_j * t) \\
            s(t) = \\sum_j  w_j * \\exp(i*\\omega_j * t)

        with :math:`\\omega_i = 2 * \\pi * f_i`, and frequency `f_i` where
        `f_i` is the i'th value in `freq`

        `signal` is a scalar if `t` is a scalar, and and array if `t` is an
        array

    Notes
    -----

    `freq_unit` can be Hz (GHz, MHz, etc), describing the frequency directly,
    or any energy unit, in which case the energy value E (given through the
    freq parameter) is converted to an actual frequency as

     .. math:: f = E / (\\hbar * 2 * pi)
    """
    if hasattr(t, '__getitem__'):
        signal = np.zeros(len(t), dtype=np.complex128)
        assert type(t) == np.ndarray, "t must be numpy array"
        assert t.dtype.type is np.float64, "t must be double precision real"
    else:
        signal = 0.0
    c = convert.to_au(1, time_unit) * convert.to_au(1, freq_unit)
    if hasattr(freq, '__getitem__'):
        if weights is None:
            weights = np.ones(len(freq))
        norm = float(sum(weights))
        for (w, weight) in zip(freq, weights):
            if complex:
                signal += (weight/norm) * np.exp(1j*c*w*t) # element-wise
            else:
                signal += (weight/norm) * np.cos(c*w*t) # element-wise
    else:
        if complex:
            signal += np.exp(1j*c*freq*t) # element-wise
        else:
            signal += np.cos(c*freq*t) # element-wise
    return signal


def gaussian(t, E0, t0, sigma):
    """
    Return a Gaussian shape

    Parameters
    ----------

    t : scalar, ndarray

    Returns
    -------

    gaussian : scalar, ndarray
        Gaussian shape of same type as `t`

    """
    return E0 * np.exp(-(t-t0)**2/(2*sigma**2))


@np.vectorize
def box(t, t_start, t_stop):
    """
    Return a box-shape (Theta-function) that is zero before `t_start` and after
    `t_stop` and one elsewehere

    Parameters
    ----------

    t : scalar, ndarray
        Time point or time grid
    t_start : scalar
        First value of `t` for which the box has value 1
    t_stop : scalar
        Last value of `t` for which the box has value 1

    Returns
    -------

    box_shape : ndarray(float64)
        If `t` is an array, `box_shape` is an array of the same size as `t`
        If `t` is scalar, `box_shape` is an array of size 1 (which for all
        intents and purposes can be used like a float)
    """
    if t < t_start:
        return 0.0
    if t > t_stop:
        return 0.0
    return 1.0


def blackman(t, t_start, t_stop, a=0.16):
    """
    Return a Blackman function between `t_start` and `t_stop`,
    see http://en.wikipedia.org/wiki/Window_function#Blackman_windows

    A Blackman shape looks nearly identical to a Gaussian with a 6-sigma
    interval between start and stop  Unlike the Gaussian,
    however, it will go exactly to zero at the edges. Thus, Blackman pulses
    are often preferable to Gaussians.

    Parameters
    ----------
    t : scalar, ndarray
        Time point or time grid
    t_start : scalar
        Starting point of Blackman shape
    t_stop : scalar
        End point of Blackman shape

    Returns
    -------

    blackman_shape: scalar, ndarray(float64)
        If `t` is a scalar, `blackman_shape` is the scalar value of the
        Blackman shape at `t`.
        If `t` is an array, `blackman_shape` is an array of same size as `t`,
        containing the values for the Blackman shape (zero before `t_start` and
        after `t_stop`)

    See Also
    --------
    numpy.blackman
    """
    T = t_stop - t_start
    return 0.5 * (1.0 - a - np.cos(2.0*np.pi * (t-t_start)/T)
                  + a*np.cos(4.0*np.pi * (t-t_start)/T)) \
           * box(t, t_start, t_stop)


@np.vectorize
def flattop(t, t_start, t_stop, t_rise, t_fall=None):
    """
    Return flattop shape, starting at `t_start` with a sine-squared ramp that
    goes to 1 within `t_rise`, and ramps down to 0 again within `t_fall` from
    `t_stop`

    Parameters
    ----------
    t : scalar, ndarray
        Time  point or time grid
    t_start : scalar
        Start of flattop window
    t_stop : scalar
        Stop of flattop window
    t_rise : scalar
        Duration of ramp-up, starting at `t_start`
    t_fall : scalar, optional
        Duration of ramp-down, ending at `t_stop`. If not given,
        `t_fall=t_rise`.

    Returns
    -------

    flattop_shape : ndarray(float64)
        If `t` is an array, `flattop_shape` is an array of the same size as `t`
        If `t` is scalar, `flattop_ox_shape` is an array of size 1 (which for
        all intents and purposes can be used like a float)
    """
    if (t >= t_start) and (t <= t_stop):
        f = 1.0
        if t_fall is None:
            t_fall = t_rise
        if (t <= t_start + t_rise):
            f = np.sin(np.pi * (t-t_start) / (2.0*t_rise))**2
        elif (t >= t_stop - t_fall):
            f = np.sin(np.pi * (t-t_stop) / (2.0*t_fall))**2
        return f
    else:
        return 0.0

