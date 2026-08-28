# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models

from .web_theme_color import THEME_PARAMS


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def _apply_web_theme_color(self, keys):
        if THEME_PARAMS.intersection(keys):
            self.env["web.theme.color"]._apply_colors()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records._apply_web_theme_color(records.mapped("key"))
        return records

    def write(self, vals):
        res = super().write(vals)
        self._apply_web_theme_color(self.mapped("key"))
        return res

    def unlink(self):
        keys = self.mapped("key")
        res = super().unlink()
        self._apply_web_theme_color(keys)
        return res
