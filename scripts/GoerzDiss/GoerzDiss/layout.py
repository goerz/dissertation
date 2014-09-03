"""
Module containing page geometry and related sizes
"""

textwidth  = 12.5 # cm
figwidth   =  8.5 # cm
textheight = 21.65 # cm

fontsize = 12 # pt
lead = 14.5 # pt

latex_size = {
"tiny"         : 7.33325,
"scriptsize"   : 8.50012,
"footnotesize" : 10.00002,
"small"        : 10.95003,
"normalsize"   : 11.74988,
"large"        : 14.09984,
"Large"        : 15.84985,
"LARGE"        : 19.02350,
"huge"         : 22.82086,
"Huge"         : 22.820
}

cm2inch = 0.39370079 # conversion factor cm to inch
pt2cm   = 0.035277778

# margin at bottom of figure, allowing for x-axis label and tick marks
fig_bottom_margin =  (2 * lead + 1) * pt2cm

# margin at left of figure, allowing for y-axis label and tick marks
fig_left_margin =  4 * lead * pt2cm

# gap between two panels
fig_panel_gap = lead * pt2cm
