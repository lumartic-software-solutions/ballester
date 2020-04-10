# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields


class VehicleSaleOrder(models.Model):
    _inherit = 'account.invoice'

    transportation_name = fields.Many2one('fleet.vehicle', string="Vehicle",
                                          domain=[('active', '=', True)])
