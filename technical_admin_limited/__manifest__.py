# Copyright 2026 - TODAY, Escodoo
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Technical Admin Limited",
    "summary": """
        Access to technical features without
        allowing access to sensitive company data""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Escodoo",
    "website": "https://github.com/Escodoo/server-addons",
    "depends": [
        "base",
        "sale",
        "purchase",
        "account",
        "hr",
        "hr_contract",
    ],
    "data": [
        "security/res_groups.xml",
        "security/ir.model.access.csv",
        "data/record_rules.xml",
    ],
    "installable": True,
}
