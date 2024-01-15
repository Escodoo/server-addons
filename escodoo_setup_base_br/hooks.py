# Copyright (C) 2024 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

# import logging
# from odoo import api, SUPERUSER_ID


# def pre_init_hook(cr):
#     """Check if 'escodoo_setup_base' is installed and install it if not."""
#     env = api.Environment(cr, SUPERUSER_ID, {})

#     logger = logging.getLogger(__name__)
#     logger.info("EXECUTANDO PRE INIT HOOK")

#     # Verifica se o módulo 'escodoo_setup_base' está instalado
#     base_module = env['ir.module.module'].search([('name', '=', 'escodoo_setup_base')])
#     if not base_module or base_module.state != 'installed':
#         # Instala o módulo 'escodoo_setup_base'
#         logger.info("------- Instalando módulo escodoo_setup_base -------")
#         base_module.button_immediate_install()
