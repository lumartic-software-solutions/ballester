# -*- coding: utf-8 -*-
# Odoo, Open Source  Stock Transport Management.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, _

class TransportReport(models.TransientModel):
    _name = 'transport.report.wizard'

    start_date = fields.Date(string="From Date")
    end_date = fields.Date(string="To Date")

    #print report method
    def print_report(self):
        return self.env.ref('stock_transport_management.transport_xlsx').report_action(self)
