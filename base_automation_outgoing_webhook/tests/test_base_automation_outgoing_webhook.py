# Copyright 2021 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestBaseAutomationOutgoingWebhook(TransactionCase):
    at_install = True
    post_install = True

    def test_requests(self):
        """Check that requests package is available"""
        self.env["res.partner"].create({"name": "New Contact"})
