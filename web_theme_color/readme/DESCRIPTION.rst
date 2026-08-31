Set the Odoo backend brand color from a system parameter, without writing a
module for each customer.

The navbar, its bottom border, the primary buttons, the form focus states and
the links follow the color. In 16.0 there is no separate ``$o-action``
variable, so everything derived from the brand color moves with it.

The color is a scss variable, not a runtime style, so changing the parameter
rewrites the theme scss file and rebuilds the web assets. The change is global
for the database: every company and every user sees the same color.

This 16.0 version only themes the light backend. Dark mode is an Enterprise
feature, and on 16.0 the ``web.dark_mode_variables`` bundle cannot be resolved
on Community at all: its own ``before`` directive targets
``base/static/src/scss/onboarding.variables.scss``, a file that bundle does not
carry, so writing into it raises. The 18.0 version of this module does handle
dark mode.

A few spots keep the Odoo purple because the core hardcodes it instead of
reading the variable: the table picker of the html editor and the
``theme-color`` meta tag, which colors the browser bar on mobile. Document
layout colors (PDF and email) and the Website theme palette are separate
settings.
