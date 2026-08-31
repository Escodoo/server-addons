# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Web Theme Color",
    "summary": """
        Set the backend brand color from a system parameter""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/server-addons",
    "depends": [
        "web",
        "web_editor",
    ],
    "data": [
        "data/ir_config_parameter.xml",
    ],
    "assets": {
        "web._assets_primary_variables": [
            (
                "prepend",
                "web_theme_color/static/src/scss/primary_variables.scss",
            ),
        ],
    },
    "installable": True,
}
