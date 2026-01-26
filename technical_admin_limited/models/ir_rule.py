from odoo import api, exceptions, models


class IrRule(models.Model):
    _inherit = "ir.rule"

    def _check_technical_admin_limited(self):
        if self.env.user.has_group(
            "technical_admin_limited.group_technical_admin_limited"
        ):
            raise exceptions.AccessError(
                self.env._(
                    "You are not allowed to modify rules.\n\n"
                    "This action is restricted for Technical "
                    "Administrators (Limited)."
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._check_technical_admin_limited()
        return super().create(vals_list)

    def write(self, vals):
        self._check_technical_admin_limited()
        return super().write(vals)

    def unlink(self):
        self._check_technical_admin_limited()
        return super().unlink()
