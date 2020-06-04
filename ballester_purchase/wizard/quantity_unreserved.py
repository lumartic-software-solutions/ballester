# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class BarcodeWizard(models.TransientModel):
    _name = 'quantity.unreserved'
    _description = 'Unreserved Quantity'

    def action_unreserved(self):
        self.env.cr.execute('update stock_quant set reserved_quantity=0.0')


