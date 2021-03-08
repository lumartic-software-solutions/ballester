# -*- coding: utf-8 -*-
# Odoo, Open Source Ballester Product.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta



class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    origin_number = fields.Char('Origin NUmber')
    date_delivery = fields.Datetime('Delivery Date')
    client_ref = fields.Char('Customer Reference')