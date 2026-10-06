# Copyright 2026 - TODAY, Wesley Oliveira <wesley.oliveira@escodoo.com.br>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase, tagged

from odoo.addons.web_theme_color.models.web_theme_color import (
    DEFAULT_PRIMARY,
    PARAM_PRIMARY,
    THEME_ASSETS,
)

CUSTOM_COLOR = "#d01000"


@tagged("post_install", "-at_install")
class TestWebThemeColor(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.params = cls.env["ir.config_parameter"].sudo()
        cls.assets = cls.env["web_editor.assets"].sudo()
        cls.primary_url, cls.primary_bundle = next(
            (url, bundle)
            for param, _default, url, bundle in THEME_ASSETS
            if param == PARAM_PRIMARY
        )

    def setUp(self):
        super().setUp()
        # The database may already carry a customized color, so start every
        # test from the default one.
        for param, default, _url, _bundle in THEME_ASSETS:
            parameter = self.params.search([("key", "=", param)])
            if parameter:
                parameter.write({"value": default})
            else:
                self.params.create({"key": param, "value": default})

    def _custom_attachment(self, url, bundle):
        custom_url = self.assets._make_custom_asset_url(url, bundle)
        return self.assets._get_custom_attachment(custom_url)

    def _primary_attachment(self):
        return self._custom_attachment(self.primary_url, self.primary_bundle)

    def _set_primary(self, color):
        self.params.set_param(PARAM_PRIMARY, color)

    def test_default_keeps_the_assets_untouched(self):
        """The default color leaves no scss override behind."""
        for _param, _default, url, bundle in THEME_ASSETS:
            self.assertFalse(self._custom_attachment(url, bundle))

    def test_custom_color_saves_the_asset(self):
        """A color other than the default writes the scss override."""
        self._set_primary(CUSTOM_COLOR)
        attachment = self._primary_attachment()
        self.assertTrue(attachment)
        content = base64.b64decode(attachment.datas).decode("utf-8")
        self.assertIn(CUSTOM_COLOR, content)
        self.assertIn("$o-brand-primary", content)

    def test_short_form_color_is_accepted(self):
        """The three digit form is a valid color."""
        self._set_primary("#d10")
        content = base64.b64decode(self._primary_attachment().datas).decode("utf-8")
        self.assertIn("#d10", content)

    def test_default_color_resets_the_asset(self):
        """Going back to the default removes the override instead of writing it."""
        self._set_primary(CUSTOM_COLOR)
        self.assertTrue(self._primary_attachment())
        self._set_primary(DEFAULT_PRIMARY)
        self.assertFalse(self._primary_attachment())

    def test_invalid_color_is_rejected(self):
        """A value that is not a hexadecimal color cannot be saved."""
        with self.assertRaises(ValidationError):
            self._set_primary("red")

    def test_renaming_the_key_resets_the_asset(self):
        """A parameter renamed away from a theme key stops applying its color."""
        self._set_primary(CUSTOM_COLOR)
        self.assertTrue(self._primary_attachment())
        parameter = self.params.search([("key", "=", PARAM_PRIMARY)])
        parameter.key = "web_theme_color.primary_renamed"
        self.assertFalse(self._primary_attachment())

    def test_unlinking_the_parameter_resets_the_asset(self):
        """Deleting the parameter falls back to the default color."""
        self._set_primary(CUSTOM_COLOR)
        self.assertTrue(self._primary_attachment())
        self.params.search([("key", "=", PARAM_PRIMARY)]).unlink()
        self.assertFalse(self._primary_attachment())

    def test_unrelated_parameter_leaves_the_assets_alone(self):
        """Other system parameters do not touch the theme assets."""
        self.params.set_param("web_theme_color_unrelated.param", "whatever")
        self.assertFalse(self._primary_attachment())
