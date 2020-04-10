# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models,fields,api

class Survey(models.Model):
    _inherit = 'survey.user_input'

    sale_order_id = fields.Many2one('sale.order','Sale Order')
    