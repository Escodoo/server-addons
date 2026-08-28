Go to **Settings > Technical > Parameters > System Parameters** and change the
value of these two parameters, created by the module:

| Parameter | Default | What it sets |
| --- | --- | --- |
| `web_theme_color.primary` | `#71639e` | Brand color of the backend |
| `web_theme_color.primary_dark` | `#71639e` | Brand color in Enterprise dark mode |

The value is an hexadecimal color such as `#D01000`. Both the three digit
(`#D10`) and the six digit form are accepted. Any other value is rejected when
you save the parameter, so a typo cannot break the assets.

`web_theme_color.primary_dark` only has an effect on Odoo Enterprise, which is
where dark mode exists. On Community it can be left at the default.

After saving, reload the backend with a hard refresh (Ctrl+F5) so the browser
drops the cached assets. The default values are the standard Odoo colors, so
installing the module alone changes nothing.
