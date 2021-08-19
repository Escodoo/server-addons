# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import requests
from odoo import api, models


class IrActionsServer(models.Model):

    _inherit = 'ir.actions.server'

    @api.model
    def _get_eval_context(self, action=None):
        eval_context = super(IrActionsServer, self)._get_eval_context(action)

        def make_request(*args, **kwargs):
            return requests.request(*args, **kwargs)

        eval_context["make_request"] = make_request
        return eval_context
