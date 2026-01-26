from odoo import api, exceptions, models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    def _check_technical_admin_limited(self):
        if self.env.user.has_group(
            "technical_admin_limited.group_technical_admin_limited"
        ):
            raise exceptions.AccessError(
                self.env._(
                    "You are not allowed to access System Parameters.\n\n"
                    "This action is restricted for Technical "
                    "Administrators (Limited)."
                )
            )

    @api.model
    def web_search_read(
        self, domain, specification, offset=0, limit=None, order=None, count_limit=None
    ):
        self._check_technical_admin_limited()
        return super().web_search_read(
            domain,
            specification,
            offset=offset,
            limit=limit,
            order=order,
            count_limit=count_limit,
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
