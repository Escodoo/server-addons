Set the Odoo backend brand color from a system parameter, without writing a
module for each customer.

The navbar, its bottom border and the primary buttons follow the color. Link
and focus colors keep the standard Odoo action teal.

The color is a scss variable, not a runtime style, so changing the parameter
rewrites the theme scss file and rebuilds the web assets. The change is global
for the database: every company and every user sees the same color.

A few spots keep the Odoo purple because the core hardcodes it instead of
reading the variable: the table picker of the html editor and the
`theme-color` meta tag, which colors the browser bar on mobile. Document
layout colors (PDF and email) and the Website theme palette are separate
settings.
