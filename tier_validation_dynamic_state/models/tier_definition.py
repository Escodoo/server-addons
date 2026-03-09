# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class TierDefinition(models.Model):
    _inherit = "tier.definition"

    state_from = fields.Many2one(
        comodel_name="ir.model.fields.selection",
        ondelete="cascade",
    )
    state_to = fields.Many2one(
        comodel_name="ir.model.fields.selection",
        ondelete="cascade",
    )
