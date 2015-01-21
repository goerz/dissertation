IMG = jj.pdf holonomic_entanglement.pdf transmon2013_gate_error_cphase.pdf \
transmon2013_gate_error_cnot.pdf charge_dispersion.pdf                     \
transmon_photo_overlay.pdf CPH_spectra.pdf tm2013_spectra.pdf              \
adiabatic_popdyn.pdf hol_oct_success.pdf hol_oct_120left_popdyn.pdf        \
hol_oct_spectra.pdf
IMG2 =

include ../figures.mk

jj.pdf: jj.tex

holonomic_entanglement.pdf: holonomic_entanglement.py

transmon2013_gate_error_cphase.pdf: transmon2013_gate_error.py matplotlibrc
	@echo "\n** generate figure: transmon2013_gate_error.py -> $@"
	@$(PYTHON) transmon2013_gate_error.py

transmon2013_gate_error_cnot.pdf: transmon2013_gate_error_cphase.pdf
	@echo "\n** generate figure: transmon2013_gate_error.py -> $@"

charge_dispersion.pdf: charge_dispersion.py

transmon_photo_overlay.pdf: transmon_photo_overlay.tex

CPH_spectra.pdf: CPH_spectra.py

tm2013_spectra.pdf: tm2013_spectra.py

adiabatic_popdyn.pdf: adiabatic_popdyn.py

hol_oct_success.pdf: hol_oct_success.py

hol_oct_120left_popdyn.pdf: hol_oct_120left_popdyn.py

hol_oct_spectra.pdf: hol_oct_spectra.py

clean: clean-auto
