# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import re

from odoo import api, models
from odoo.exceptions import ValidationError

PARAM_PRIMARY = "web_theme_color.primary"
PARAM_PRIMARY_DARK = "web_theme_color.primary_dark"

DEFAULT_PRIMARY = "#71639e"
DEFAULT_PRIMARY_DARK = "#71639e"

COLOR_PATTERN = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")

# (parameter, default, asset to rewrite, bundle it belongs to)
THEME_ASSETS = (
    (
        PARAM_PRIMARY,
        DEFAULT_PRIMARY,
        "/web_theme_color/static/src/scss/primary_variables.scss",
        "web._assets_primary_variables",
    ),
    (
        PARAM_PRIMARY_DARK,
        DEFAULT_PRIMARY_DARK,
        "/web_theme_color/static/src/scss/primary_variables.dark.scss",
        "web.dark_mode_variables",
    ),
)

THEME_PARAMS = frozenset(asset[0] for asset in THEME_ASSETS)

SCSS_TEMPLATE = """\
// Generated from the system parameter %(param)s.
// Change that parameter instead of editing this file.
$o-community-color: %(color)s !default;
$o-enterprise-color: %(color)s !default;
$o-brand-odoo: %(color)s !default;
$o-brand-primary: %(color)s !default;
"""


class WebThemeColor(models.AbstractModel):
    _name = "web.theme.color"
    _description = "Backend Theme Color"

    @api.model
    def _check_color(self, param, color):
        if not COLOR_PATTERN.match(color or ""):
            raise ValidationError(
                self.env._(
                    "%(color)s is not a valid color for %(param)s.\n\n"
                    "Use an hexadecimal value such as #D01000.",
                    color=color or "",
                    param=param,
                )
            )
        return color

    @api.model
    def _apply_colors(self):
        """Rewrite the theme scss files from the system parameters.

        The colors are scss variables, so they are only picked up when the
        bundle is compiled. Saving the asset replaces the file and invalidates
        the bundle; on the default color the customization is removed instead,
        so no attachment is left behind.
        """
        assets = self.env["web_editor.assets"].sudo()
        params = self.env["ir.config_parameter"].sudo()
        for param, default, url, bundle in THEME_ASSETS:
            color = params.get_param(param) or default
            self._check_color(param, color)
            if color.lower() == default.lower():
                assets.reset_asset(url, bundle)
                continue
            content = SCSS_TEMPLATE % {"color": color, "param": param}
            assets.save_asset(url, bundle, content, "scss")
